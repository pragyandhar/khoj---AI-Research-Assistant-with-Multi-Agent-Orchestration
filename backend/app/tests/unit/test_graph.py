# WHAT DOES THIS FILE DO: Unit and integration tests for LangGraph nodes, routing pauses, state updates, and citation validation checks.

# ================== IMPORTS ==================
from unittest.mock import AsyncMock, MagicMock, patch
import pytest

from langgraph.checkpoint.memory import MemorySaver

from app.graph.state import GraphState
from app.graph.nodes.router_node import router_node
from app.graph.nodes.research_node import research_node
from app.graph.main_graph import build_graph
from app.graph.citation_subgraph import build_citation_subgraph, CitationState
from app.agents.router_agent import RouteDecision
from app.agents.citation_agent import CitationVerification
from app.models.report import StructuredReport
# ================== IMPORTS ==================


# =========== FUNCTION ===========
# ROLE: Verifies that router_node processes query and returns topic update.
@pytest.mark.asyncio
async def test_router_node_updates_topic(mock_openai):
    """ Verifies that router_node processes query and returns topic update. """
    
    # FLOW-1: Set up mock OpenAI structured output RouteDecision value
    mock_instance = mock_openai.return_value
    mock_structured_llm = mock_instance.with_structured_output.return_value
    mock_structured_llm.ainvoke = AsyncMock(return_value=RouteDecision(topic="technology"))
    
    # FLOW-2: Create a GraphState with query
    state = GraphState(
        query="explain quantum computing",
        topic="",
        research_output="",
        final_report=None,
        session_id="test-session",
        status="pending",
        error=None,
        messages=[],
        human_approved=False,
        graph_checkpoint_id=None,
        created_at="",
        citations=[],
        verified_citations=[],
        failed_citations=[]
    )
    
    # FLOW-3: Invoke router_node
    result = await router_node(state)
    
    # FLOW-4: Assert result topic matches mocked decision — router now also selects the
    # specialist agent and pauses for approval before research runs (Phase 4)
    assert result.get("topic") == "technology"
    assert result.get("selected_agent") == "technology"
    assert result.get("status") == "awaiting_approval"
# =========== FUNCTION ===========


# =========== FUNCTION ===========
# ROLE: Verifies that research_node updates the state with research output.
@pytest.mark.asyncio
async def test_research_node_updates_output():
    """ Verifies that research_node updates the state with research output. """
    
    # FLOW-1: Create a GraphState with query and topic
    state = GraphState(
        query="explain quantum computing",
        topic="technology",
        research_output="",
        final_report=None,
        session_id="test-session",
        status="pending",
        error=None,
        messages=[],
        human_approved=False,
        graph_checkpoint_id=None,
        created_at="",
        citations=[],
        verified_citations=[],
        failed_citations=[]
    )
    
    # FLOW-2: Mock ResearchAgent instance and run result
    with patch("app.graph.nodes.research_node.ResearchAgent") as MockResearchAgent:
        mock_agent_instance = MockResearchAgent.return_value
        mock_agent_instance.run = AsyncMock(return_value="Mocked research details and findings.")
        
        # FLOW-3: Execute research_node
        result = await research_node(state)
        
        # FLOW-4: Verify results output is populated
        assert result.get("research_output") == "Mocked research details and findings."
        assert result.get("status") == "summarizing"
# =========== FUNCTION ===========


# =========== FUNCTION ===========
# ROLE: Verifies the graph compiles and interrupts execution before human approval.
@pytest.mark.asyncio
async def test_graph_pauses_at_human_approval(mock_openai):
    """ Verifies the graph compiles and interrupts execution before human approval. """
    
    # FLOW-1: Build graph with MemorySaver checkpointer
    checkpointer = MemorySaver()
    graph = build_graph(checkpointer=checkpointer)
    
    # FLOW-2: Setup mock OpenAI agent outcomes to bypass routing and research exceptions
    mock_instance = mock_openai.return_value
    mock_structured_llm = mock_instance.with_structured_output.return_value
    mock_structured_llm.ainvoke = AsyncMock(return_value=RouteDecision(topic="technology"))
    
    from langchain_core.messages import AIMessage
    mock_instance.ainvoke = AsyncMock(return_value={"messages": [AIMessage(content="Mocked research findings.")]})
    
    # FLOW-3: Setup thread configuration and initial state input
    config = {"configurable": {"thread_id": "test-thread-1"}}
    initial_state = {
        "query": "explain quantum computing",
        "topic": "",
        "research_output": "",
        "final_report": None,
        "session_id": "test-session-1",
        "status": "pending",
        "error": None,
        "messages": [],
        "human_approved": False,
        "graph_checkpoint_id": None,
        "created_at": "",
        "citations": [],
        "verified_citations": [],
        "failed_citations": []
    }
    
    # FLOW-4: Run async invoke to trigger graph execution
    await graph.ainvoke(initial_state, config=config)
    
    # FLOW-5: Get current thread state and assert it paused at human_approval node
    state_info = await graph.aget_state(config)
    assert state_info.next == ("human_approval",)
# =========== FUNCTION ===========


# =========== FUNCTION ===========
# ROLE: Verifies the graph resumes execution after human approval state update.
@pytest.mark.asyncio
async def test_graph_resumes_after_approval(mock_openai):
    """ Verifies the graph resumes execution after human approval state update. """
    
    # FLOW-1: Build graph and setup mock responses
    checkpointer = MemorySaver()
    graph = build_graph(checkpointer=checkpointer)
    
    mock_instance = mock_openai.return_value
    mock_structured_llm = mock_instance.with_structured_output.return_value
    mock_structured_llm.ainvoke = AsyncMock(return_value=RouteDecision(topic="technology"))
    
    from langchain_core.messages import AIMessage
    mock_instance.ainvoke = AsyncMock(return_value={"messages": [AIMessage(content="Mocked research findings.")]})
    
    from app.models.report import ReportSection
    dummy_report = StructuredReport(
        title="Test Report",
        summary="Test summary of research findings.",
        sections=[
            ReportSection(
                heading="Introduction",
                content="This is the content for the introduction section of the test report containing more than fifty characters to pass validation checks.",
                citations=[]
            )
        ],
        topic="technology",
        confidence_score=0.95,
        total_sources=0
    )
    mock_structured_llm.ainvoke = AsyncMock(return_value=dummy_report)
    
    # FLOW-2: Setup config and run initial execution to pause before human approval
    config = {"configurable": {"thread_id": "test-thread-2"}}
    initial_state = {
        "query": "explain quantum computing",
        "topic": "",
        "research_output": "",
        "final_report": None,
        "session_id": "test-session-2",
        "status": "pending",
        "error": None,
        "messages": [],
        "human_approved": False,
        "graph_checkpoint_id": None,
        "created_at": "",
        "citations": [],
        "verified_citations": [],
        "failed_citations": []
    }
    
    await graph.ainvoke(initial_state, config=config)
    
    # FLOW-3: Assert state is paused
    state_info = await graph.aget_state(config)
    assert state_info.next == ("human_approval",)
    
    # FLOW-4: Update state setting human_approved flag to True
    await graph.aupdate_state(config, {"human_approved": True}, as_node="human_approval")
    
    # FLOW-5: Mock verification of HTTP requests inside citation check node to return True
    with patch("httpx.AsyncClient.head") as mock_head, patch("httpx.AsyncClient.get") as mock_get:
        mock_head.return_value = MagicMock(status_code=200)
        mock_get.return_value = MagicMock(status_code=200)
        
        # FLOW-6: Resume execution by invoking graph with None input
        final_state = await graph.ainvoke(None, config=config)
        
        # FLOW-7: Assert status is completed and final_report is set
        assert final_state.get("status") == "completed"
        assert final_state.get("final_report") is not None
# =========== FUNCTION ===========


# =========== FUNCTION ===========
# ROLE: Verifies that citation subgraph separates accessible and failing URLs.
@pytest.mark.asyncio
async def test_citation_subgraph_filters_failed_urls():
    """ Verifies that citation subgraph separates accessible and failing URLs. """
    
    # FLOW-1: Setup test CitationState input
    state = CitationState(
        query="What is quantum computing?",
        citations=[
            {"title": "Valid Source", "url": "https://example.com/ok", "relevance_score": 0.8},
            {"title": "Invalid Source", "url": "https://example.com/fail", "relevance_score": 0.5}
        ],
        verified_citations=[],
        failed_citations=[]
    )

    # FLOW-2: Mock httpx AsyncClient to succeed for /ok and fail for /fail
    async def mock_head_or_get(url, *args, **kwargs):
        if "/ok" in str(url):
            return MagicMock(status_code=200)
        raise Exception("Connection Refused")

    # FLOW-3: Stub the citation agent's relevance check so the URL-accessible citation
    # also passes relevance scoring, isolating this test to URL accessibility filtering
    async def fake_run(self, claim: str, citation: dict) -> CitationVerification:
        return CitationVerification(relevance_score=0.9, justification="Relevant.", is_valid=True)

    with patch("httpx.AsyncClient.head", side_effect=mock_head_or_get), \
         patch("httpx.AsyncClient.get", side_effect=mock_head_or_get), \
         patch("app.graph.citation_subgraph.CitationAgent.run", new=fake_run):

        # FLOW-4: Build and execute citation subgraph
        subgraph = build_citation_subgraph()
        result = await subgraph.ainvoke(state)

        # FLOW-5: Assert citations are partitioned correctly
        verified = result.get("verified_citations", [])
        failed = result.get("failed_citations", [])

        assert len(verified) == 1
        assert verified[0]["url"] == "https://example.com/ok"
        assert len(failed) == 1
        assert failed[0]["url"] == "https://example.com/fail"
# =========== FUNCTION ===========