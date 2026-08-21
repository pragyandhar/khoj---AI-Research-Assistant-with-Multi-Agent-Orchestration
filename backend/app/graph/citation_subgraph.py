# WHAT DOES THIS FILE DO: Defines the citation check subgraph to verify source connectivity and filter top relevance citations.

# ================== IMPORTS ==================
from typing import TypedDict
import asyncio

import httpx
from langgraph.graph import StateGraph

from app.agents.citation_agent import CitationAgent
from app.core.exceptions import LLMException
# ================== IMPORTS ==================


# =========== CLASS ===========
# ROLE: State schema tracking citations check execution.
class CitationState(TypedDict):
    """ TypedDict schema tracking citations verification progress. """

    query: str
    citations: list[dict]
    verified_citations: list[dict]
    failed_citations: list[dict]
# =========== CLASS ===========


# =========== FUNCTION ===========
# ROLE: Checks availability of a single URL.
async def _verify_single_url(client: httpx.AsyncClient, url: str, citation: dict) -> tuple[dict, bool]:
    """ Sends HEAD/GET requests to test connectivity. """
    
    try:
        response = await client.head(url)
        if response.status_code < 400:
            return citation, True
            
    except Exception:
        pass
        
    try:
        response = await client.get(url)
        if response.status_code < 400:
            return citation, True
            
    except Exception:
        pass
        
    return citation, False
# =========== FUNCTION ===========


# =========== FUNCTION ===========
# ROLE: Verifies the accessibility of each citation URL using HTTP check.
async def verify_citation_node(state: CitationState) -> dict:
    """ Checks every citation URL for connectivity and groups them. """
    
    citations = state.get("citations") or []
    verified = []
    failed = []
    
    async with httpx.AsyncClient(timeout=5.0, follow_redirects=True) as client:
        # Check URLs in parallel using asyncio.gather
        tasks = []
        for citation in citations:
            url = citation.get("url", "")
            if url:
                tasks.append(_verify_single_url(client, url, citation))
            else:
                failed.append(citation)
                
        if tasks:
            results = await asyncio.gather(*tasks)
            for citation, is_valid in results:
                if is_valid:
                    verified.append(citation)
                else:
                    failed.append(citation)
                    
    return {"verified_citations": verified, "failed_citations": failed}
# =========== FUNCTION ===========


# =========== FUNCTION ===========
# ROLE: Checks a single citation's relevance against the research claim via the citation agent.
async def _verify_single_relevance(citation_agent: CitationAgent, claim: str, citation: dict) -> dict | None:
    """ Returns the citation with an LLM-assessed relevance_score, or None if it fails/is irrelevant. """

    try:
        verification = await citation_agent.run(claim=claim, citation=citation)
    except LLMException:
        return None

    if not verification.is_valid or verification.relevance_score < 0.5:
        return None

    scored_citation = dict(citation)            # USE: Avoid mutating the original citation dict
    scored_citation["relevance_score"] = verification.relevance_score  # USE: Overwrite with LLM-verified score

    return scored_citation
# =========== FUNCTION ===========


# =========== FUNCTION ===========
# ROLE: Verifies relevance of URL-accessible citations and limits the result to the top 5.
async def score_citations_node(state: CitationState) -> dict:
    """ Drops citations that don't actually support the claim, then sorts and truncates to top 5. """

    verified = state.get("verified_citations") or []
    claim = state.get("query", "")

    citation_agent = CitationAgent()            # USE: Shared agent instance for this batch of citations

    # Verify relevance for every URL-accessible citation in parallel
    relevance_checked = await asyncio.gather(
        *[_verify_single_relevance(citation_agent, claim, citation) for citation in verified]
    )                                           # USE: Parallel LLM relevance checks
    relevant_citations = [citation for citation in relevance_checked if citation is not None]  # USE: Drop failed/irrelevant citations

    # Sort by relevance_score in descending order
    sorted_citations = sorted(
        relevant_citations,
        key=lambda c: float(c.get("relevance_score", 0.0)),
        reverse=True
    )                                           # USE: Sort citations descending

    top_5 = sorted_citations[:5]                # USE: Keep top 5 elements

    return {"verified_citations": top_5}
# =========== FUNCTION ===========


# =========== FUNCTION ===========
# ROLE: Compiles and builds the citation check StateGraph subgraph.
def build_citation_subgraph():
    """ Setup nodes, edges, entry/finish points, and compile the subgraph. """
    
    workflow = StateGraph(CitationState)        # USE: Define StateGraph for citation state schema
    
    # Register verification and scoring nodes
    workflow.add_node("verify", verify_citation_node)  # USE: Register verify node
    workflow.add_node("score", score_citations_node)  # USE: Register score node
    
    # Configure edges routing
    workflow.set_entry_point("verify")          # USE: Start at verify node
    workflow.add_edge("verify", "score")        # USE: Route verify to score node
    workflow.set_finish_point("score")          # USE: End at score node
    
    compiled = workflow.compile()
    
    return compiled
# =========== FUNCTION ===========