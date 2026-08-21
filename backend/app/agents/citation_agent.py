# WHAT DOES THIS FILE DO: Defines the LLM-powered citation agent verifying source relevance against a research claim.

# ================== IMPORTS ==================
from pydantic import BaseModel, Field

from app.agents.base_agent import BaseAgent
from app.core.exceptions import LLMException
# ================== IMPORTS ==================


# =========== CLASS ===========
# ROLE: Structured output model representing a citation's relevance verdict.
class CitationVerification(BaseModel):
    """ Structured verdict on whether a source supports a given claim. """

    relevance_score: float = Field(..., ge=0.0, le=1.0)  # USE: How well the source supports the claim, 0 to 1
    justification: str                          # USE: Brief explanation of the verdict
    is_valid: bool                              # USE: Whether the source is considered a valid citation
# =========== CLASS ===========


# =========== CLASS ===========
# ROLE: Citation specialist agent judging source relevance using LLM reasoning.
class CitationAgent(BaseAgent):
    """ Agent verifying whether a source actually supports a research claim. """

    SYSTEM_PROMPT = (
        "You are a citation verification specialist. Given a research claim and a "
        "source, determine if the source actually supports the claim. Return a "
        "relevance score from 0.0 to 1.0 and a brief justification."
    )  # USE: Fixed specialist system prompt


    # =========== FUNCTION ===========
    # ROLE: Initialize the citation agent with structured output binding, no tools.
    def __init__(self):
        """ Initialize agent without tools — verification relies on LLM judgment only. """

        # FLOW-1: Call base agent class constructor with an empty tools list
        super().__init__(tools=[])              # USE: Instantiate parent base agent

        # FLOW-2: Bind structured output format for citation verification
        self.structured_llm = self.llm.with_structured_output(CitationVerification)  # USE: Bound structured model
    # =========== FUNCTION ===========


    # =========== FUNCTION ===========
    # ROLE: Verify whether a citation source supports the given research claim.
    async def run(self, claim: str, citation: dict) -> CitationVerification:
        """ Judge citation relevance against a claim and return a structured verdict. """

        # FLOW-1: Build the verification prompt referencing the claim and source metadata
        messages = [
            ("system", self.SYSTEM_PROMPT),
            ("human", (
                f"Claim: {claim}\n\n"
                f"Source title: {citation.get('title', '')}\n"
                f"Source URL: {citation.get('url', '')}"
            )),
        ]                                       # USE: Structured verification prompt

        # FLOW-2: Invoke structured LLM and translate failures to LLMException
        try:
            verification = await self.structured_llm.ainvoke(messages)  # USE: Get relevance verdict from LLM

            return verification

        except Exception as e:
            self.logger.error("citation_agent_failed", claim=claim, url=citation.get("url", ""), error=str(e))  # USE: Log verification failure
            raise LLMException(f"Citation verification failed: {str(e)}")  # USE: Wrapper exception
    # =========== FUNCTION ===========
# =========== CLASS ===========
