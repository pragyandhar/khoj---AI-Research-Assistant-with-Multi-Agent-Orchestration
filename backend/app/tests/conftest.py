# WHAT DOES THIS FILE DO: Configures pytest options and defines shared test fixtures for database, HTTP clients, and model mockers.

# ================== IMPORTS ==================
from unittest.mock import patch, MagicMock, AsyncMock
import os
import sys

# Setup session-scoped mock for ChatOpenAI before any application imports occur to prevent real API connections
patch_openai = patch("langchain_openai.ChatOpenAI")
mock_openai_class = patch_openai.start()

from fastapi import FastAPI
import httpx
from httpx import ASGITransport
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

# Setup dummy env variables before local imports to pass Pydantic validation
os.environ["OPENAI_API_KEY"] = "test-openai"
os.environ["TAVILY_API_KEY"] = "test-tavily"
os.environ["LANGSMITH_API_KEY"] = "test-langsmith"
os.environ["LANGSMITH_PROJECT"] = "test-project"
os.environ["DATABASE_URL"] = "postgresql+asyncpg://user:pass@localhost/db"
os.environ["REDIS_URL"] = "redis://localhost:6379/0"
os.environ["API_SECRET_KEY"] = "test-secret-key"

# Mock setup_checkpointer and build_graph to prevent connection/execution errors during tests
from unittest.mock import AsyncMock, MagicMock
import sys

async def mock_astream_events(*args, **kwargs):
    yield {
        "event": "on_chain_end",
        "name": "router",
        "data": {"output": {"topic": "technology", "status": "researching"}}
    }
    yield {
        "event": "on_chain_end",
        "name": "research",
        "data": {"output": {"status": "awaiting_approval"}}
    }
    yield {
        "event": "on_chain_end",
        "name": "human_approval",
        "data": {"output": {"status": "summarizing"}}
    }
    yield {
        "event": "on_chain_end",
        "name": "summary",
        "data": {
            "output": {
                "final_report": {
                    "title": "Test Report",
                    "summary": "Summary",
                    "sections": [
                        {
                            "heading": "Introduction",
                            "content": "This is the content for the introduction section of the test report containing more than fifty characters to pass validation checks.",
                            "citations": []
                        }
                    ],
                    "topic": "technology",
                    "confidence_score": 0.9,
                    "total_sources": 0
                }
            }
        }
    }
    yield {
        "event": "on_chain_end",
        "name": "citation_check",
        "data": {"output": {"verified_citations": [], "failed_citations": []}}
    }

mock_state_info = MagicMock()
mock_state_info.next = []
mock_state_info.values = {
    "query": "explain artificial intelligence in detail",
    "topic": "technology"
}


async def mock_astream(*args, **kwargs):
    """ Synthetic resumed-graph stream used by /approve endpoint tests. """
    yield {"human_approval": {"status": "researching", "human_approved": True}}
    yield {"research": {"research_output": "Mocked research findings.", "status": "summarizing"}}
    yield {
        "summary": {
            "final_report": {
                "title": "Test Report",
                "summary": "Summary",
                "sections": [
                    {
                        "heading": "Introduction",
                        "content": "This is the content for the introduction section of the test report containing more than fifty characters to pass validation checks.",
                        "citations": []
                    }
                ],
                "topic": "technology",
                "confidence_score": 0.9,
                "total_sources": 0
            },
            "citations": [],
            "status": "citing"
        }
    }
    yield {"citation_check": {"verified_citations": [], "failed_citations": []}}


mock_graph = MagicMock()
mock_graph.astream_events = mock_astream_events
mock_graph.astream = mock_astream
mock_graph.aget_state = AsyncMock(return_value=mock_state_info)
mock_graph.aupdate_state = AsyncMock()

# Patch setup_checkpointer and build_graph before any imports of app
from unittest.mock import patch

patch_checkpointer = patch("app.graph.checkpointer.setup_checkpointer", new=AsyncMock(return_value=MagicMock()))
patch_graph = patch("app.graph.main_graph.build_graph", new=MagicMock(return_value=mock_graph))

patch_checkpointer.start()
patch_graph.start()

from app.core.dependencies import get_db_session
from app.db.base import Base
from app.main import app
from app.models.report import StructuredReport, ReportSection

# Manually register mocks on app.state to guarantee availability during tests
app.state.checkpointer = MagicMock()
app.state.graph = mock_graph

# Stop the patches now that app.state.graph/checkpointer are pinned to the mocks above.
# ASGITransport never triggers FastAPI's lifespan during tests, so these patches only
# ever existed to protect that import-time app construction — leaving them active would
# make app.graph.main_graph.build_graph / app.graph.checkpointer.setup_checkpointer
# resolve to mocks for every test, including ones (like test_graph.py) that import and
# call the real functions directly to build a genuine graph with a MemorySaver.
patch_checkpointer.stop()
patch_graph.stop()
# ================== IMPORTS ==================


# =========== VARIABLES : Test API key constants ===========
TEST_API_KEY = "test-secret-key"            # USE: Fixed secret key used for validating test requests
# =========== VARIABLES : Test API key constants ===========


# =========== FUNCTION ===========
# ROLE: Configure pytest options for the test session.
def pytest_configure(config):
    """ Sets the default asyncio mode option to auto. """
    
    # FLOW-1: Set asyncio mode to auto in pytest config options
    config.option.asyncio_mode = "auto"         # USE: Configure pytest-asyncio to run tests in auto mode
# =========== FUNCTION ===========


# =========== FUNCTION ===========
# ROLE: Fixture to ensure API key environment variable is populated.
@pytest.fixture(autouse=True)
def setup_api_key():
    """ Sets target secret key in environment variables during tests execution. """
    
    # FLOW-1: Write test key to os.environ dictionary
    os.environ["API_SECRET_KEY"] = TEST_API_KEY  # USE: Mock API key environment variable
    
    yield
# =========== FUNCTION ===========


# =========== FUNCTION ===========
# ROLE: Yields an async HTTP client for FastAPI integration testing.
@pytest.fixture
async def app_client():
    """ Async context client generator for routing integration tests. """
    
    # FLOW-1: Open httpx AsyncClient session and yield it using ASGITransport
    async with httpx.AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:  # USE: Context manager for HTTP client
        yield client
# =========== FUNCTION ===========


# =========== FUNCTION ===========
# ROLE: Mocks ChatOpenAI client response for structured outputs and react agent actions.
@pytest.fixture
def mock_openai():
    """ Setup mock object for ChatOpenAI agent and parser models. """
    
    # FLOW-1: Reset and configure the global mocked OpenAI class instance
    mock_openai_class.reset_mock()
    mock_instance = mock_openai_class.return_value  # USE: Retrieve target mock instance
    
    # FLOW-2: Mock with_structured_output behavior
    mock_structured_llm = MagicMock()       # USE: MagicMock for structured LLM response
    mock_instance.with_structured_output.return_value = mock_structured_llm  # USE: Bind structured mock
    
    # FLOW-3: Build dummy StructuredReport schema object
    dummy_report = StructuredReport(
        title="Test Research Report",
        summary="This is a test summary of research findings.",
        sections=[
            ReportSection(
                heading="Introduction",
                content="This is the content for the introduction section of the test report.",
                citations=[]
            )
        ],
        topic="general",
        confidence_score=0.9,
        total_sources=0
    )                                           # USE: Pydantic mock report payload
    mock_structured_llm.ainvoke = AsyncMock(return_value=dummy_report)  # USE: Bind report response to structured invoke
    
    # FLOW-4: Mock plain ainvoke for create_react_agent message list response
    from langchain_core.messages import AIMessage
    mock_instance.ainvoke = AsyncMock(
        return_value={"messages": [AIMessage(content="Mocked research findings content.")]}
    )                                           # USE: Bind mock message response

    # FLOW-5: Stub create_react_agent itself, so BaseAgent subclasses (Research/Science/
    # Technology agents) get a working .agent.ainvoke() without needing to mock LangGraph's
    # internal ReAct tool-calling loop (model.bind_tools(tools).ainvoke(...) is a separate,
    # unconfigured mock chain that plain mock_instance.ainvoke above does not reach).
    with patch("app.agents.base_agent.create_react_agent") as mock_create_react_agent:
        mock_react_agent = MagicMock()
        mock_react_agent.ainvoke = AsyncMock(
            return_value={"messages": [AIMessage(content="Mocked research findings content.")]}
        )                                       # USE: Stand-in compiled react agent with a working ainvoke
        mock_create_react_agent.return_value = mock_react_agent

        yield mock_openai_class
# =========== FUNCTION ===========


# =========== FUNCTION ===========
# ROLE: Setup SQLite in-memory database session fixture overriding production DB connections.
@pytest.fixture
async def test_db():
    """ Setup in-memory test database and override dependencies. """
    
    # FLOW-1: Initialize SQLite in-memory engine and build metadata schemas
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)  # USE: SQLite test async connection
    
    async with engine.begin() as conn:          # USE: Acquire connection transaction
        await conn.run_sync(Base.metadata.create_all)  # USE: DDL schema generation call
        
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)  # USE: Create test session factory
    
    # FLOW-2: Yield active test session and register dependency overrides
    async with session_factory() as session:    # USE: Open connection session context
    
    
        # =========== FUNCTION ===========
        # ROLE: Nested generator dependency overriding production database connection.
        async def override_get_db_session():
            """ Yields active in-memory session. """
            yield session
        # =========== FUNCTION ===========
        
        app.dependency_overrides[get_db_session] = override_get_db_session  # USE: Inject dependency override
        yield session
        
    # FLOW-3: Cleanup dependencies and drop all generated schemas
    app.dependency_overrides.clear()            # USE: Reset application overrides list
    
    async with engine.begin() as conn:          # USE: Open connection context
        await conn.run_sync(Base.metadata.drop_all)  # USE: Drop DDL schemas
# =========== FUNCTION ===========