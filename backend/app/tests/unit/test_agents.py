# WHAT DOES THIS FILE DO: Unit tests for checking LLM Router, Research, and Summary agents behaviors.

# ================== IMPORTS ==================
from unittest.mock import patch, MagicMock, AsyncMock

import pytest

from app.agents.research_agent import ResearchAgent
from app.agents.router_agent import RouterAgent, RouteDecision
from app.agents.summary_agent import SummaryAgent
from app.models.report import StructuredReport
# ================== IMPORTS ==================


# =========== FUNCTION ===========
# ROLE: Test that RouterAgent correctly classifies tech queries.
@pytest.mark.asyncio
async def test_router_agent_classifies_technology(mock_openai):
    """ Verifies tech queries are routed to technology category. """
    
    # FLOW-1: Setup structured output mock to return RouteDecision technology
    mock_instance = mock_openai.return_value    # USE: Get mock OpenAI client
    mock_structured_llm = mock_instance.with_structured_output.return_value  # USE: Get structured LLM reference
    mock_structured_llm.ainvoke = AsyncMock(return_value=RouteDecision(topic="technology"))  # USE: Set mocked response
    
    # FLOW-2: Instantiate router agent and run query
    agent = RouterAgent()                       # USE: Instantiate RouterAgent
    result = await agent.run("explain kubernetes")  # USE: Run router query
    
    # FLOW-3: Assert output is technology
    assert result == "technology"
# =========== FUNCTION ===========


# =========== FUNCTION ===========
# ROLE: Test that RouterAgent falls back to general category on LLM error.
@pytest.mark.asyncio
async def test_router_agent_fallback_on_error(mock_openai):
    """ Verifies general category fallback on LLM exceptions. """
    
    # FLOW-1: Mock structured LLM to raise exception
    mock_instance = mock_openai.return_value    # USE: Get mock OpenAI client
    mock_structured_llm = mock_instance.with_structured_output.return_value  # USE: Get structured LLM reference
    mock_structured_llm.ainvoke = AsyncMock(side_effect=Exception("LLM error connection timeout"))  # USE: Trigger error
    
    # FLOW-2: Instantiate router agent and run query
    agent = RouterAgent()                       # USE: Instantiate RouterAgent
    result = await agent.run("explain kubernetes")  # USE: Run router query
    
    # FLOW-3: Assert fallback to general category
    assert result == "general"
# =========== FUNCTION ===========


# =========== FUNCTION ===========
# ROLE: Test that ResearchAgent binds and triggers the web search tool.
@pytest.mark.asyncio
async def test_research_agent_calls_web_search(mock_openai):
    """ Verifies web search tool bindings and execution triggering. """
    
    # FLOW-1: Instantiate research agent and assert tool binding presence
    agent = ResearchAgent()                     # USE: Instantiate ResearchAgent
    assert len(agent.tools) == 1                # USE: Verify exactly one tool is bound
    assert agent.tools[0].name == "web_search"  # USE: Verify bound tool is web_search
    
    # FLOW-2: Mock LLM client graph execution trigger
    from langchain_core.messages import AIMessage
    mock_instance = mock_openai.return_value    # USE: Get mock OpenAI client
    mock_instance.ainvoke = AsyncMock(return_value={"messages": [AIMessage(content="Mocked findings.")]})  # USE: Mock standard client invoke
    
    # FLOW-3: Mock and patch react agent graph ainvoke call and run agent
    with patch.object(agent.agent, "ainvoke", AsyncMock(return_value={"messages": [AIMessage(content="Mocked findings.")]})) as mock_ainvoke:
        await agent.run("quantum computing", "technology")  # USE: Trigger research agent run
        mock_ainvoke.assert_called_once()       # USE: Verify react agent graph was invoked
# =========== FUNCTION ===========


# =========== FUNCTION ===========
# ROLE: Test that SummaryAgent returns a StructuredReport Pydantic object.
@pytest.mark.asyncio
async def test_summary_agent_returns_structured_report(mock_openai):
    """ Verifies summary agent parses raw findings to StructuredReport. """
    
    # FLOW-1: Mock structured output response with StructuredReport instance
    mock_instance = mock_openai.return_value    # USE: Get mock OpenAI client
    mock_structured_llm = mock_instance.with_structured_output.return_value  # USE: Get structured LLM reference
    
    from app.models.report import ReportSection
    dummy_report = StructuredReport(
        title="Test Report",
        summary="Test summary",
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
    )                                           # USE: Instantiate mock report
    mock_structured_llm.ainvoke = AsyncMock(return_value=dummy_report)  # USE: Bind invoke response
    
    # FLOW-2: Instantiate summary agent and run summarization
    agent = SummaryAgent()                      # USE: Instantiate SummaryAgent
    result = await agent.run("raw research findings", "original query", "technology")  # USE: Run summarizer agent
    
    # FLOW-3: Assert result matches mock report fields
    assert isinstance(result, StructuredReport)  # USE: Assert return type
    assert result.title == "Test Report"        # USE: Assert correct schema mapping
# =========== FUNCTION ===========