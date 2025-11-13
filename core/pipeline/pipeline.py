from core.pipeline.guardrails import GuardAgent
from core.pipeline.rewriter import RewriterAgent
from core.pipeline.hyde import HyDEAgent
from core.pipeline.reranker import Reranker
from core.pipeline.generator import QAAgent
from core.types import GuardAgentResponse, ElasticsearchAnswer
from core.vector_store.retriever import Retriever
from typing import Dict
from core.utils import Utils    


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
    
    def process_query(self, question: str) -> Dict:

        # first step are the guardrails
        try:
            print("Checking guardrails...")
            guard_response = self.guard_agent.validate_question(question)
            if guard_response.isSafe:
                print("Question passed guardrails.")
            else:
                print(f"Question failed guardrails: {guard_response.reasons}")
                return {
                    "error": "Question did not pass guardrails",
                    "reasons": guard_response.reasons
                }
        except Exception as e:
            print(f"Error during guardrail validation: {e}")
            return {
                "error": "Guardrail validation failed",
                "details": str(e)
            }
        
        #second step is the rewriting of the question if needed
        try:
            print("Rewriting question if needed...")
            rewritten_question = self.rewriter_agent.rewrite_question(question)
        except Exception as e:
            print(f"Error during question rewriting: {e}")
            return {
                "error": "Question rewriting failed",
                "details": str(e)
            }
        print(f"Rewritten question successfully")
        
        # third step is the HyDE generation
        try:
            print("Generating HyDE...")
            hyde_response = self.hyde_agent.generate_hyde(rewritten_question.rewritten_question)
            
        except Exception as e:
            print(f"Error during HyDE generation: {e}")
            return {
                "error": "HyDE generation failed",
                "details": str(e)
            }
        print(f"HyDE generated successfully")
        
        # Then we should have two parrallel steps the retrieval, I will do it sequentially to simplify
        # retrieval for rewritten question
        try:
            print("Retrieving documents for rewritten question...")
            rewritten_docs = self.retriever.retrieve_documents(rewritten_question.rewritten_question, top_k=5)
            print(f"Retrieved {len(rewritten_docs.hits)} documents for rewritten question.")

        except Exception as e:
            print(f"Error during document retrieval: {e}")
            return {
                "error": "Document retrieval failed",
                "details": str(e)
            }
        
        # retrieval for hyde question
        try:
            print("Retrieving documents for HyDE question...")
            hyde_docs = self.retriever.retrieve_documents(hyde_response.hypothetical_answer, top_k=5)
            print(f"Retrieved {len(hyde_docs.hits)} documents for HyDE question.")
        except Exception as e:
            print(f"Error during document retrieval for HyDE: {e}")
            return {
                "error": "Document retrieval for HyDE failed",
                "details": str(e)
            }
        
        # before reranking we need to merge the two sets of documents
        merged_docs = self.utils.merge_two_ElasticsearchAnswer_lists(rewritten_docs, hyde_docs)
            
            
        try:
            print("Reranking documents...")
            reranked_docs = self.reranker.rerank(question, merged_docs, top_n=3) 
            # extract all content as a single list  of string 
            reranked_contents = [doc.source.get('content', '') for doc in reranked_docs.hits]
            print(f"Reranked to {len(reranked_docs.hits)} documents.")
        except Exception as e:
            print(f"Error during document reranking: {e}")
            return {
                "error": "Document reranking failed",
                "details": str(e)
            }
        
        # finally the generation
        try:
            print("Generating final answer...")
            final_answer = self.qa_agent.answer(question, reranked_contents)
            print("Final answer generated.")
            return {
                "answer": final_answer,
                "source_documents": [
                     reranked_docs
                ]
            }
        except Exception as e:
            print(f"Error during answer generation: {e}")
            return {
                "error": "Answer generation failed",
                "details": str(e)
            }   