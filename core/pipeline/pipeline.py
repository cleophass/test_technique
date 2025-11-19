from core.pipeline.guardrails import GuardAgent
from core.pipeline.rewriter import RewriterAgent
from core.pipeline.hyde import HyDEAgent
from core.pipeline.reranker import Reranker
from core.pipeline.generator import QAAgent
from core.types import GuardAgentResponse, ElasticsearchAnswer, RAGResponse, ElasticsearchAnswerItem
from core.vector_store.retriever import Retriever
from typing import Dict, List, Optional, Callable
from core.utils import Utils    
from core.vector_store.logger import ActivityLogger


class RAGPipeline:
    def __init__(
        self,
    ):
        self.guard_agent = GuardAgent()
        self.rewriter_agent = RewriterAgent()
        self.hyde_agent = HyDEAgent()
        self.retriever = Retriever()
        self.reranker = Reranker()
        self.qa_agent = QAAgent()
        self.utils = Utils()
        self.activity_logger = ActivityLogger("rag_pipeline")
        

    
    def process_query(self, question: str, status_callback: Optional[Callable[[str], None]] = None
) -> RAGResponse:
        def update_status(message: str): #this will be used in front to display the state
            """Helper to update status if callback is provided"""
            if status_callback:
                status_callback(message)
            print(f"RAGPPELINE: {message}")  

        # first step are the guardrails
        try:
            update_status("Checking guardrails...")
            
            guard_response = self.guard_agent.validate_question(question)
            if guard_response.isSafe:
                update_status("Question passed guardrails.")
                
            else:
                update_status(f"Question failed guardrails: {guard_response.reasons}")
                return self.utils.construct_RAGResponse(
                    answer="",
                    error="Question did not pass guardrails",
                    details=guard_response.reasons
                )
        except Exception as e:
            self.activity_logger.log_interaction(f"Error during guardrail validation: {e}", "error")
            return self.utils.construct_RAGResponse(
                answer="",
                error="Guardrail validation failed",
                details=str(e)
            )
        
        #second step is the rewriting of the question if needed
        try:
            update_status("Rewriting question if needed...")
            
            rewritten_question = self.rewriter_agent.rewrite_question(question)
        except Exception as e:
            self.activity_logger.log_interaction(f"Error during question rewriting: {e}", "error")
            return self.utils.construct_RAGResponse(
                answer="",
                error="Question rewriting failed",
                details=str(e)
            )
        update_status("Rewritten question successfully")
        
        
        # third step is the HyDE generation
        try:
            
            update_status("Generating HyDE...")
            hyde_response = self.hyde_agent.generate_hyde(rewritten_question.rewritten_question)
            
        except Exception as e:
            self.activity_logger.log_interaction(f"Error during HyDE generation: {e}", "error")
            return self.utils.construct_RAGResponse(
                answer="",
                error="HyDE generation failed",
                details=str(e)
            )
        update_status(f"HyDE generated successfully")
        
        
        # Then we should have two parrallel steps the retrieval, I will do it sequentially to simplify
        # retrieval for rewritten question
        try:
            
            update_status("Retrieving documents for rewritten question...")
            rewritten_docs = self.retriever.retrieve_documents(rewritten_question.rewritten_question, top_k=4)
            update_status(f"Retrieved {len(rewritten_docs.hits)} documents for rewritten question.")

        except Exception as e:
            self.activity_logger.log_interaction(f"Error during document retrieval: {e}", "error")
            update_status(f"Error during document retrieval: {e}")
            return self.utils.construct_RAGResponse(
                answer="",
                error="Document retrieval for rewritten question failed",
                details=str(e)
            )
        
        # retrieval for hyde question
        try:
            update_status("Retrieving documents for HyDE question...")
            hyde_docs = self.retriever.retrieve_documents(hyde_response.hypothetical_answer, top_k=4)
            update_status(f"Retrieved {len(hyde_docs.hits)} documents for HyDE question.")
        except Exception as e:
            self.activity_logger.log_interaction(f"Error during document retrieval for HyDE: {e}", "error")
            return self.utils.construct_RAGResponse(
                answer="",
                error="Document retrieval for HyDE failed",
                details=str(e)
            )
            
            
        # before reranking we need to merge the two sets of documents
        merged_docs = self.utils.merge_two_ElasticsearchAnswer_lists(rewritten_docs, hyde_docs)
            
            
        try:
            update_status("Reranking documents...")
            
            reranked_docs = self.reranker.rerank(question, merged_docs, top_n=2) 
            # extract all content as a single list  of string 
            reranked_contents = [doc.source.get('content', '') for doc in reranked_docs.hits]
            update_status(f"Reranked to {len(reranked_docs.hits)} documents.")
        except Exception as e:
            self.activity_logger.log_interaction(f"Error during document reranking: {e}", "error")
            return self.utils.construct_RAGResponse(
                answer="",
                error="Document reranking failed",
                details=str(e)
            )
           
        
        
        # finally the generation
        try:
            update_status("Generating final answer...")
            
            final_answer = self.qa_agent.answer(question, reranked_contents)
            update_status("Final answer generated.")
            
            final_response = self.utils.construct_RAGResponse(
                answer=final_answer,
                source_documents=reranked_docs
            )
            
            return final_response
        except Exception as e:
            self.activity_logger.log_interaction(f"Error during answer generation: {e}", "error")
            return self.utils.construct_RAGResponse(
                answer="",
                error="Answer generation failed",
                details=str(e)
            )
            
    