# WHAT DOES THIS FILE DO: Defines the SummaryAgent for summarizing raw text data into StructuredReport schemas.

# ================== IMPORTS ==================
from app.agents.base_agent import BaseAgent
from app.core.exceptions import LLMException
from app.models.report import StructuredReport
from app.tools.structured_parser import parse_to_structured_report
# ================== IMPORTS ==================


# =========== CLASS ===========
# ROLE: Summary agent that converts unstructured research findings into a structured report.
class SummaryAgent(BaseAgent):
    """ Agent class responsible for summarizing research output into JSON schemas. """


    # =========== FUNCTION ===========
    # ROLE: Initialize SummaryAgent with no search tools.
    def __init__(self):
        """ Setup summarizer agent with parent initialization. """
        
        # FLOW-1: Call parent class base agent setup without tools
        super().__init__(tools=[])              # USE: parent base agent constructor
    # =========== FUNCTION ===========


    # =========== FUNCTION ===========
    # ROLE: Summarize raw research findings into a StructuredReport object.
    async def run(self, research_output: str, original_query: str, topic: str) -> StructuredReport:
        """ Parses unstructured research text into a StructuredReport. """
        
        # FLOW-1: Trigger structured parser on findings text and query context
        try:
            report = await parse_to_structured_report(research_output, original_query)  # USE: Call parser utility
            
            return report
            
        except Exception as e:
            # FLOW-2: Log error and raise custom LLMException on failure
            self.logger.error("summary_agent_failed", query=original_query, topic=topic, error=str(e))  # USE: Tracing summary failure
            raise LLMException("Summary generation failed")  # USE: Wrapper exception raising
    # =========== FUNCTION ===========
# =========== CLASS ===========