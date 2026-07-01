# WHAT DOES THIS FILE DO: Defines the web search tool using Tavily Search API.

# ================== IMPORTS ==================
from langchain_core.tools import tool
from langchain_community.tools.tavily_search import TavilySearchResults

from app.core.config import settings
from app.core.exceptions import ToolExecutionException
from app.core.logging import get_logger
# ================== IMPORTS ==================


# =========== VARIABLES : Web search tools and loggers ===========
logger = get_logger(__name__)
tavily = TavilySearchResults(max_results=5, tavily_api_key=settings.TAVILY_API_KEY)
# =========== VARIABLES : Web search tools and loggers ===========


# =========== FUNCTION ===========
# ROLE: Executes web searches using Tavily search engine.
@tool
async def web_search(query: str) -> str:
    """ Search the web using the Tavily search engine to retrieve real-time, current, or technical information.
    Use this tool when the query requires facts, news, documentation, or data that may not be present in the model's static training weights.
    
    Args:
        query: The search query string containing keywords relevant to the research topic.
        
    Returns:
        A numbered list string of search results, where each result displays the page title, reference URL, and content snippet.
    """
    
    # FLOW-1: Log invocation and execute search query using Tavily async handler
    logger.info("web_search_called", query=query)  # USE: Tracing search call query parameter
    
    try:
        results = await tavily.ainvoke(query)  # USE: Trigger async Tavily search request
        logger.info("web_search_completed", results_count=len(results))  # USE: Log success search metadata
        formatted_results = []
        
        # FLOW-2: Process search results and build a numbered text summary
        for i, res in enumerate(results, 1):
            title = res.get("title", "No Title")  # USE: Extract document title
            url = res.get("url", "No URL")      # USE: Extract link URL reference
            content = res.get("content", "")    # USE: Extract text snippet content
            formatted_results.append(f"{i}. Title: {title}\n   URL: {url}\n   Content: {content}\n")
            
        # FLOW-3: Return the combined string representation of results
        return "\n".join(formatted_results)
        
    except Exception as e:
        raise ToolExecutionException(f"Web search failed: {str(e)}")  # USE: Custom tool error translation
# =========== FUNCTION ===========