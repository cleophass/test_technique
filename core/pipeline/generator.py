from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from core.pipeline.prompts.generator import SYSTEM_PROMPT
from core.config import GENERATOR_MODEL_NAME
from typing import List
from langchain_core.messages import AIMessage
from langchain.tools import ToolRuntime
from langgraph.checkpoint.memory import InMemorySaver


  

class QAAgent:
    def __init__(self, model_name=GENERATOR_MODEL_NAME, 
                 system_prompt=SYSTEM_PROMPT, 
                 temperature=0.7, 
                 checkpointer: ToolRuntime = InMemorySaver() # type: ignore
                 ): 
        self.model_name = model_name
        self.system_prompt = system_prompt
        self.temperature = temperature
        self.checkpointer = checkpointer
        self.agent = self._initialize_agent()
        self.config = {"configurable": {"thread_id": "1"}}

    
    def _initialize_agent(self):
        model = init_chat_model(
            model=self.model_name,
            temperature=self.temperature,
            timeout=10,
            max_tokens=500
        )
        return create_agent(
            model=model,
            system_prompt=self.system_prompt,
            checkpointer=self.checkpointer, # type: ignore
        )
    
    def answer(self, question:str, chunks:List[str]):
        context = "\n\n".join(chunks)
        prompt = {
            "messages": [
                {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"}
            ]
        }
        # we need a step to extract the answer from the response
        
        response = self.agent.invoke(prompt, config=self.config)  # type: ignore
        answer = self.get_answer(response)
        return answer

    def get_answer(self, response) -> str:
        # Let's browse the response in inverse order and find the first AIMessage
        for message in reversed(response["messages"]):
            return message.content
        return "There was an error generating the answer. Check in generator.py"