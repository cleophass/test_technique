# this title will be used in the sidebar to named the conversation

# I will use an specific structured output agent to ensure the question is valid if not i will return the justifcation of the llm
from core.types import TitleAgentResponse
from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from core.pipeline.prompts.title import SYSTEM_PROMPT
from core.config import TITLE_MODEL_NAME

class TitleAgent:
    def __init__(self, model_name=TITLE_MODEL_NAME, system_prompt=SYSTEM_PROMPT, temperature=0.7):
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
            response_format=TitleAgentResponse
        )
    
    def create_title(self, question: str) -> TitleAgentResponse:
        prompt = {
            "messages": [{"role": "user", "content": f"{question}"}]
        }
        response = self.agent.invoke(prompt) # type: ignore
        
        # verify that structured_response is inside 
        if isinstance(response, dict) and 'structured_response' in response:
            response = response['structured_response']
            return response
        else:
            print("Invalid response structure from title agent:", response)
            return TitleAgentResponse(**{"Titre": "Invalid response structure"})