# I will use an specific structured output agent to ensure the question is valid if not i will return the justifcation of the llm
from core.types import RewriterAgentResponse
from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from core.pipeline.prompts.rewriter import SYSTEM_PROMPT
from core.config import REWRITER_MODEL_NAME

class RewriterAgent:
    def __init__(self, model_name=REWRITER_MODEL_NAME, system_prompt=SYSTEM_PROMPT, temperature=0.5): # Increased temperature for more diverse rewrites
        self.model_name = model_name
        self.system_prompt = system_prompt
        self.temperature = temperature
        self.agent = self._initialize_agent()
    
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
            response_format=RewriterAgentResponse
        )
    
    def rewrite_question(self, question: str) -> RewriterAgentResponse:
        prompt = {
            "messages": [{"role": "user", "content": f"{question}"}]
        }
        response = self.agent.invoke(prompt) # type: ignore
        
        # verify that structured_response is inside 
        if isinstance(response, dict) and 'structured_response' in response:
            response = response['structured_response']
            return response
        else:
            print("Invalid response structure from rewriter agent:", response)
            return RewriterAgentResponse(**{"neededRewrite": False, "rewritten_question": "Invalid response structure"})