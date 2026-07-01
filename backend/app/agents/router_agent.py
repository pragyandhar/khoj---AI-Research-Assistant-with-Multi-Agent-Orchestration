# WHAT DOES THIS FILE DO: Defines the RouterAgent for classifying incoming research queries.

# ================== IMPORTS ==================
from typing import Literal

from langchain_openai import ChatOpenAI
from pydantic import BaseModel

from app.agents.base_agent import BaseAgent
from app.core.config import settings
# ================== IMPORTS ==================


# =========== CLASS ===========
# ROLE: Pydantic model for extracting topic classification decisions from LLM.
class RouteDecision(BaseModel):
    """ Structured output model representing topic routing selection. """

    topic: Literal["science", "technology", "general"]  # USE: Target categorization label
# =========== CLASS ===========


# =========== CLASS ===========
# ROLE: Router agent to classify user queries into distinct research domains.
class RouterAgent(BaseAgent):
    """ Agent that determines topic classification using structured output. """


    # =========== FUNCTION ===========
    # ROLE: Initialize RouterAgent and override LLM settings for classification.
    def __init__(self):
        """ Setup router LLM and bind structured classification model. """
        
        # FLOW-1: Call parent class base agent setup
        super().__init__(tools=[])              # USE: BaseAgent constructor initialization
        
        # FLOW-2: Override LLM client configuration for lower temperature
        self.llm = ChatOpenAI(
            model="gpt-4o",                     # USE: OpenAI LLM version identifier
            api_key=settings.OPENAI_API_KEY,    # USE: OpenAI authentication key
            temperature=0.1,                    # USE: Lower temperature for high deterministic results
        )                                       # USE: Rebind LLM instance
        
        # FLOW-3: Bind structured output format to the LLM client instance
        self.structured_llm = self.llm.with_structured_output(RouteDecision)  # USE: Bound structured model
    # =========== FUNCTION ===========


    # =========== FUNCTION ===========
    # ROLE: Route research query to topic categories science, technology, or general.
    async def run(self, query: str) -> str:
        """ Classify incoming user query into target thematic category. """
        
        # FLOW-1: Set up classification messages instructions
        messages = [
            ("system", "You are an expert query router. Classify the user query into exactly one of three categories: 'science' (academic research, physics, chemistry, biology, medical), 'technology' (software, coding, hardware, engineering, tech news), or 'general' (history, politics, pop culture, standard facts, others)."),
            ("human", f"Route this query: {query}")
        ]                                       # USE: Structured routing prompt
        
        # FLOW-2: Invoke structured LLM and catch exceptions with fallback
        try:
            decision = await self.structured_llm.ainvoke(messages)  # USE: Get classification output from LLM
            
            return decision.topic
            
        except Exception as e:
            # FLOW-3: Log exception error and default to general category
            self.logger.error("router_agent_failed", error=str(e))  # USE: Log routing failures
            
            return "general"
    # =========== FUNCTION ===========
# =========== CLASS ===========