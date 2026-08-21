# WHAT DOES THIS FILE DO: Tests multi-agent routing, citation relevance scoring, and approval-time query modification.

# ================== IMPORTS ==================
from unittest.mock import AsyncMock, patch
import pytest

from app.graph.nodes.router_node import router_node
from app.graph.citation_subgraph import CitationState, score_citations_node
from app.agents.router_agent import RouteDecision
from app.agents.citation_agent import CitationVerification
from app.main import app
# ================== IMPORTS ==================


# =========== FUNCTION ===========
# ROLE: Verifies a science-topic query is routed to the science specialist agent.
@pytest.mark.asyncio
async def test_router_selects_science_agent(mock_openai):
    """ Verifies router_node selects the science specialist for a science query. """

    # FLOW-1: Mock the router's structured output to classify as science
    mock_structured_llm = mock_openai.return_value.with_structured_output.return_value
    mock_structured_llm.ainvoke = AsyncMock(return_value=RouteDecision(topic="science"))

    # FLOW-2: Run router_node and verify the selected specialist agent
    result = await router_node({"query": "explain CRISPR gene editing"})

    assert result["selected_agent"] == "science"
    assert result["topic"] == "science"
# =========== FUNCTION ===========


# =========== FUNCTION ===========
# ROLE: Verifies a technology-topic query is routed to the technology specialist agent.
@pytest.mark.asyncio
async def test_router_selects_technology_agent(mock_openai):
    """ Verifies router_node selects the technology specialist for a tech query. """

    # FLOW-1: Mock the router's structured output to classify as technology
    mock_structured_llm = mock_openai.return_value.with_structured_output.return_value
    mock_structured_llm.ainvoke = AsyncMock(return_value=RouteDecision(topic="technology"))

    # FLOW-2: Run router_node and verify the selected specialist agent
    result = await router_node({"query": "how does Kubernetes work"})

    assert result["selected_agent"] == "technology"
    assert result["topic"] == "technology"
# =========== FUNCTION ===========


# =========== FUNCTION ===========
# ROLE: Verifies routing falls back to the general agent when classification fails.
@pytest.mark.asyncio
async def test_router_fallback_to_general(mock_openai):
    """ Verifies router_node falls back to 'general' when the router LLM call fails. """

    # FLOW-1: Force the router's structured output call to raise
    mock_structured_llm = mock_openai.return_value.with_structured_output.return_value
    mock_structured_llm.ainvoke = AsyncMock(side_effect=Exception("LLM unavailable"))

    # FLOW-2: Run router_node and verify the general fallback agent is selected
    result = await router_node({"query": "some ambiguous query"})

    assert result["selected_agent"] == "general"
    assert result["topic"] == "general"
# =========== FUNCTION ===========


# =========== FUNCTION ===========
# ROLE: Verifies the citation subgraph drops low-relevance citations via the citation agent.
@pytest.mark.asyncio
async def test_citation_agent_scores_relevance():
    """ Verifies score_citations_node drops citations the citation agent scores as irrelevant. """

    # FLOW-1: Build citation agent responses keyed by citation URL, avoiding reliance on
    # asyncio.gather's execution order across the parallel relevance checks
    async def fake_run(self, claim: str, citation: dict) -> CitationVerification:
        if citation["url"].endswith("/relevant"):
            return CitationVerification(relevance_score=0.9, justification="Directly supports the claim.", is_valid=True)
        return CitationVerification(relevance_score=0.2, justification="Unrelated to the claim.", is_valid=False)

    state = CitationState(
        query="What is quantum computing?",
        citations=[],
        verified_citations=[
            {"title": "Relevant Source", "url": "https://example.com/relevant", "relevance_score": 0.5},
            {"title": "Irrelevant Source", "url": "https://example.com/irrelevant", "relevance_score": 0.5},
        ],
        failed_citations=[]
    )

    # FLOW-2: Run score_citations_node with the citation agent's LLM call patched out
    with patch("app.graph.citation_subgraph.CitationAgent.run", new=fake_run):
        result = await score_citations_node(state)

    # FLOW-3: Only the high-relevance citation should survive
    verified = result["verified_citations"]
    assert len(verified) == 1
    assert verified[0]["url"] == "https://example.com/relevant"
    assert verified[0]["relevance_score"] == 0.9
# =========== FUNCTION ===========


# =========== FUNCTION ===========
# ROLE: Verifies a modified_query submitted at approval time is passed into the graph state update.
@pytest.mark.asyncio
async def test_query_modification_on_approval(app_client, test_db):
    """ Verifies POST /approve forwards modified_query into the graph state update. """

    # FLOW-1: Reset the shared mocked graph's aupdate_state call history for a clean assertion
    app.state.graph.aupdate_state.reset_mock()

    headers = {"Authorization": "Bearer test-secret-key"}  # USE: Mock API key header dict
    payload = {"modified_query": "explain CRISPR gene editing instead"}  # USE: Approval body with a query edit

    # FLOW-2: Call the approve endpoint with a modified_query
    response = await app_client.post(
        "/api/v1/research/sessions/test-session-id/approve",
        json=payload,
        headers=headers
    )

    assert response.status_code == 200

    # FLOW-3: Verify the state update passed to aupdate_state carried the modified query
    _, state_update = app.state.graph.aupdate_state.call_args.args
    assert state_update["human_approved"] is True
    assert state_update["modified_query"] == "explain CRISPR gene editing instead"
# =========== FUNCTION ===========
