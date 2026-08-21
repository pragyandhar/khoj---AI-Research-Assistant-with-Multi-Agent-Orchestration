# WHAT DOES THIS FILE DO: Defines the technology research specialist agent prioritizing documentation and technical sources.

# ================== IMPORTS ==================
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

from app.agents.base_agent import BaseAgent
from app.core.exceptions import LLMException
from app.tools.web_search import web_search
# ================== IMPORTS ==================


# =========== CLASS ===========
# ROLE: Technology specialist agent prioritizing official docs, repositories, and technical blogs.
class TechnologyResearchAgent(BaseAgent):
    """ Research agent specialized in technology and software domains. """

    SYSTEM_PROMPT = (
        "You are a technology research specialist. Prioritize official documentation, "
        "GitHub repositories, technical blogs, and recent releases. Focus on practical "
        "implementation details and current industry standards."
    )  # USE: Fixed specialist system prompt


    # =========== FUNCTION ===========
    # ROLE: Initialize the technology specialist agent with web search tooling.
    def __init__(self):
        """ Initialize agent with web search tool bound via BaseAgent. """

        # FLOW-1: Call base agent class constructor supplying search tools list
        super().__init__(tools=[web_search])  # USE: Instantiate parent base agent
    # =========== FUNCTION ===========


    # =========== FUNCTION ===========
    # ROLE: Conduct technology-focused research on a topic by querying search tools.
    async def run(self, query: str, topic: str) -> str:
        """ Run the research react agent using the technology specialist prompt. """

        # FLOW-1: Inject topic context into the fixed specialist system prompt
        system_prompt = f"{self.SYSTEM_PROMPT}\n\nCurrent research topic: {topic}."  # USE: Topic-aware specialist prompt

        # FLOW-2: Prep messages payload with system prompt and query
        input_messages = [SystemMessage(content=system_prompt), HumanMessage(content=query)]  # USE: Message list for react agent

        # FLOW-3: Execute target langchain reactive agent graph and parse response messages
        try:
            response = await self.agent.ainvoke(
                {"messages": input_messages},
                config={"recursion_limit": 10}
            )                                   # USE: Run react agent execution graph

            messages = response.get("messages", [])  # USE: Fetch list of graph output messages

            # FLOW-4: Traverse messages backward to extract final AIMessage content
            for msg in reversed(messages):
                if isinstance(msg, AIMessage):  # USE: Check if message type is AIMessage
                    return msg.content

            raise LLMException("No valid AI response found in agent execution trajectory")

        except Exception as e:
            # FLOW-5: Log failed execution and translate to LLMException
            self.logger.error("research_agent_failed", agent_type="technology", query=query, topic=topic, error=str(e))  # USE: Log agent execution failure details
            raise LLMException(f"Technology research execution failed: {str(e)}")  # USE: Wrapper exception
    # =========== FUNCTION ===========
# =========== CLASS ===========
