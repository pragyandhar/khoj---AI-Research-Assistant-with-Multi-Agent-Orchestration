# WHAT DOES THIS FILE DO: Defines the ResearchAgent for executing web search and gathering topic details.

# ================== IMPORTS ==================
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

from app.agents.base_agent import BaseAgent, build_research_message
from app.agents.memory_agent import MemoryMixin
from app.core.exceptions import LLMException
from app.tools.web_search import web_search
# ================== IMPORTS ==================


# =========== CLASS ===========
# ROLE: Research agent executing search tools to query the web and gather facts.
class ResearchAgent(BaseAgent, MemoryMixin):
    """ Agent class implementing comprehensive web-search research capabilities. """


    # =========== FUNCTION ===========
    # ROLE: Initialize ResearchAgent with web search capabilities and memory.
    def __init__(self):
        """ Initialize the agent with web search tool bound and memory mixin. """
        
        # FLOW-1: Call base agent class constructor supplying search tools list
        BaseAgent.__init__(self, tools=[web_search])  # USE: Instantiate parent base agent
        
        # FLOW-2: Initialize memory mixin class constructor
        MemoryMixin.__init__(self)              # USE: Instantiate parent memory mixin
    # =========== FUNCTION ===========


    # =========== FUNCTION ===========
    # ROLE: Conduct research on a topic by querying the search tools.
    async def run(self, query: str, topic: str, retrieved_context: str = "", memory_context: str = "") -> str:
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
        )                                       # USE: Rich research directives formatting

        # FLOW-2: Get previous message history list from memory
        memory_messages = self.get_memory_context()  # USE: Retrieve history messages list

        # FLOW-3: Prep messages payload with system prompt, history, and RAG/memory-context-aware query
        human_content = build_research_message(query, retrieved_context, memory_context)  # USE: Inject past research and user preferences ahead of the query
        input_messages = [SystemMessage(content=system_prompt)] + memory_messages + [HumanMessage(content=human_content)]  # USE: Concat message array
        
        # FLOW-4: Execute target langchain reactive agent graph and parse response messages
        try:
            response = await self.agent.ainvoke(
                {"messages": input_messages},
                config={"recursion_limit": 10}
            )                                   # USE: Run react agent execution graph
            
            messages = response.get("messages", [])  # USE: Fetch list of graph output messages
            
            # FLOW-5: Traverse messages backward to extract final AIMessage content and save context
            for msg in reversed(messages):
                if isinstance(msg, AIMessage):  # USE: Check if message type is AIMessage
                    self.save_to_memory(query, msg.content)  # USE: Save conversation turn to memory buffer
                    
                    return msg.content
                    
            raise LLMException("No valid AI response found in agent execution trajectory")
            
        except Exception as e:
            # FLOW-6: Log failed execution and translate to LLMException
            self.logger.error("research_agent_failed", query=query, topic=topic, error=str(e))  # USE: Log agent execution failure details
            raise LLMException(f"Research execution failed: {str(e)}")  # USE: Wrapper exception
    # =========== FUNCTION ===========
# =========== CLASS ===========