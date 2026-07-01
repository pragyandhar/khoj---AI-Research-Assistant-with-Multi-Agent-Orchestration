# WHAT DOES THIS FILE DO: Utilizes ChatOpenAI to parse raw text data into structured report schemas.

# ================== IMPORTS ==================
from langchain_openai import ChatOpenAI

from app.core.config import settings
from app.core.exceptions import LLMException
from app.core.logging import get_logger
from app.models.report import StructuredReport
# ================== IMPORTS ==================


# =========== VARIABLES : Structured parser loggers ===========
logger = get_logger(__name__)
# =========== VARIABLES : Structured parser loggers ===========


# =========== FUNCTION ===========
# ROLE: Configures and returns ChatOpenAI model with structured output mapping.
def get_structured_llm():
    """ Instantiate OpenAI model bound to StructuredReport schema structure. """
    
    # FLOW-1: Setup ChatOpenAI client and bind StructuredReport output schema
    llm = ChatOpenAI(
        model="gpt-4o",                         # USE: OpenAI LLM model identifier version
        api_key=settings.OPENAI_API_KEY,        # USE: Authenticate with OpenAI api key
        temperature=0.2,                        # USE: Set lower temperature for structural correctness
    )                                           # USE: ChatOpenAI model initializer
    
    return llm.with_structured_output(StructuredReport)  # USE: Returns structured model interface
# =========== FUNCTION ===========


# =========== FUNCTION ===========
# ROLE: Parses raw research string to StructuredReport schema using OpenAI LLM.
async def parse_to_structured_report(raw_content: str, query: str) -> StructuredReport:
    """ Calls the structured LLM instance to convert raw text into report schema. """
    
    # FLOW-1: Set up system instructions and human search context messages
    system_msg = (
        "You are an expert research analyst. Your task is to transform raw research content into a polished, structured JSON report.\n"
        "Analyze the provided raw research data thoroughly. Synthesize the findings into a clear title, a brief high-level summary (maximum 300 characters), "
        "and detailed thematic sections (minimum 1 section). For each section, write content of at least 50 characters and attach relevant citations with relevance scores (0.0 to 1.0) "
        "based strictly on the raw data. Assign a confidence score (0.0 to 1.0) reflecting the completeness and accuracy of the raw data.\n"
        "Maintain strict factual integrity and do not hallucinate or invent any information."
    )     
    
    messages = [
        ("system", system_msg),
        ("human", f"Original Query: {query}\n\nRaw Research Content:\n{raw_content}")
    ]
    
    # FLOW-2: Get structured model instance and execute request
    try:
        structured_llm = get_structured_llm()   # USE: Fetch the bound model interface
        result = await structured_llm.ainvoke(messages)  # USE: Run async LLM inference call
        
        return result
        
    except Exception as e:
        # FLOW-3: Log failure and raise custom LLMException
        logger.error("structured_output_failed", error=str(e))  # USE: Error tracer log
        raise LLMException("Failed to generate structured report")  # USE: Custom LLM error wrapper
# =========== FUNCTION ===========