# this title will be used in the sidebar to named the conversation

# I will use an specific structured output agent to ensure the question is valid if not i will return the justifcation of the llm
from core.types import TitleAgentResponse
from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from core.pipeline.prompts.title import SYSTEM_PROMPT
from core.config import TITLE_MODEL_NAME
from core.vector_store.logger import ActivityLogger

class TitleAgent:
    def __init__(self, model_name=TITLE_MODEL_NAME, system_prompt=SYSTEM_PROMPT, temperature=0.7):
        self.model_name = model_name
        self.system_prompt = system_prompt
        self.temperature = temperature
        self.agent = self._initialize_agent()
        self.activity_logger = ActivityLogger("title_agent")
        
    
    def _initialize_agent(self):
        try:
            model = init_chat_model(
                model=self.model_name,
                temperature=self.temperature,
                timeout=10,
                max_tokens=500
            )
            return create_agent(
                model=model,
                system_prompt=self.system_prompt,
                response_format=TitleAgentResponse,
                name="Title Agent",
            )
        except Exception as e:
            self.activity_logger.log_interaction(f"Error initializing Title Agent: {e}", "error")
            raise e
    
    def create_title(self, question: str) -> TitleAgentResponse:
        try:
            prompt = {
                "messages": [{"role": "user", "content": f"{question}"}]
            }
            response = self.agent.invoke(prompt) # type: ignore
            
            # verify that structured_response is inside 
            if isinstance(response, dict) and 'structured_response' in response:
                response = response['structured_response']
                return response
            else:
                self.activity_logger.log_interaction(f"Invalid response structure from title agent: {response}", "error")
                return TitleAgentResponse(**{"Titre": "Invalid response structure"})
        except Exception as e:
            self.activity_logger.log_interaction(f"Error creating title: {e}", "error")
            raise e