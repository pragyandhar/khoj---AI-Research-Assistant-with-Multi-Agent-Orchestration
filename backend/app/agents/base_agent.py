# WHAT DOES THIS FILE DO: Defines the abstract base class for all AI research assistant agents.

# ================== IMPORTS ==================
from abc import ABC, abstractmethod

from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

from app.core.config import settings
from app.core.logging import get_logger
# ================== IMPORTS ==================


# =========== CLASS ===========
# ROLE: Abstract base class for all research sub-agents.
class BaseAgent(ABC):
    """ Base class that sets up LLM, React agent executors, and logging. """


    # =========== FUNCTION ===========
    # ROLE: Initialize LLM client, bind tool executors, and prepare logger instance.
    def __init__(self, tools: list = []):
        """ Initialize parent agent class with OpenAI client and logger. """
        
        # FLOW-1: Set up loggers and OpenAI Chat Client
        self.logger = get_logger(self.__class__.__name__)  # USE: Setup logger specific to agent class name
        self.llm = ChatOpenAI(
            model="gpt-4o",                     # USE: Default OpenAI model used across agents
            api_key=settings.OPENAI_API_KEY,    # USE: OpenAI api authentication key
            temperature=0.7,                    # USE: Creativity level temperature setting
        )                                       # USE: Initialize ChatOpenAI client
        
        # FLOW-2: Setup react agent graph executor using the tools list
        self.tools = tools                      # USE: Store tools list reference
        self.agent = create_react_agent(self.llm, tools)  # USE: Langgraph react agent initialization
    # =========== FUNCTION ===========


    # =========== FUNCTION ===========
    # ROLE: Interface execution method to run agent workflow.
    @abstractmethod
    async def run(self, **kwargs) -> str:
        """ Abstract execute method to implement custom agent logic. """
        pass
    # =========== FUNCTION ===========
# =========== CLASS ===========