# WHAT DOES THIS FILE DO: Defines the ResearchAgent for executing web search and gathering topic details.

# ================== IMPORTS ==================
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

from app.agents.base_agent import BaseAgent
from app.core.exceptions import LLMException
from app.tools.web_search import web_search
# ================== IMPORTS ==================


# =========== CLASS ===========
# ROLE: Research agent executing search tools to query the web and gather facts.
class ResearchAgent(BaseAgent):
    """ Agent class implementing comprehensive web-search research capabilities. """


    # =========== FUNCTION ===========
    # ROLE: Initialize ResearchAgent with web search capabilities.
    def __init__(self):
        """ Initialize the agent with web search tool bound. """
        
        # FLOW-1: Call base agent class constructor supplying search tools list
        super().__init__(tools=[web_search])    # USE: Instantiate parent with search tools
    # =========== FUNCTION ===========


    # =========== FUNCTION ===========
    # ROLE: Conduct research on a topic by querying the search tools.
    async def run(self, query: str, topic: str) -> str:
        """ Run the research react agent on the provided query. """
        
        # FLOW-1: Setup dynamic, detailed system prompt instruction
        system_prompt = (
            f"You are an elite, highly detailed research specialist in the field of {topic}.\n"
            "Your objective is to conduct a thorough, comprehensive investigation on the user's query.\n"
            "Guidelines:\n"
            "1. Leverage the web search tool effectively. Design precise keyword search queries to gather relevant, high-quality, and current information.\n"
            "2. Keep strict track of source metadata, including page titles and exact URLs. Always cite your sources when presenting facts.\n"
            "3. Synthesize information from multiple search results. Organize the retrieved facts logically, note any contradictions, and provide rich technical context.\n"
            "4. Do not hallucinate. Do not make up search results, URLs, or facts. Every claim you make must be directly backed by the search output."
        )
        
        # FLOW-2: Execute target langchain reactive agent graph and parse response messages
        try:
            response = await self.agent.ainvoke(
                {"messages": [SystemMessage(content=system_prompt), HumanMessage(content=query)]},
                config={"recursion_limit": 10}
            )
            
            messages = response.get("messages", [])  # USE: Fetch list of graph output messages
            
            # FLOW-3: Traverse messages backward to extract final AIMessage content
            for msg in reversed(messages):
                if isinstance(msg, AIMessage):  # USE: Check if message type is AIMessage
                    return msg.content
                    
            raise LLMException("No valid AI response found in agent execution trajectory")
            
        except Exception as e:
            # FLOW-4: Log failed execution and translate to LLMException
            self.logger.error("research_agent_failed", query=query, topic=topic, error=str(e))  # USE: Log agent execution failure details
            raise LLMException(f"Research execution failed: {str(e)}")  # USE: Wrapper exception
    # =========== FUNCTION ===========
# =========== CLASS ===========