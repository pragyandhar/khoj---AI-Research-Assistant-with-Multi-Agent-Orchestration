# WHAT DOES THIS FILE DO: Defines Pydantic schema models for research report generation and output serialization.

# ================== IMPORTS ==================
from datetime import datetime
from pydantic import BaseModel, Field
# ================== IMPORTS ==================


# =========== CLASS ===========
# ROLE: Model representing a citation source with relevance score metadata.
class Citation(BaseModel):
    """ Citation structure containing source metadata and score. """

    # FLOW-1: Set up citation attributes with range checks on relevance
    title: str                                  # USE: Title of cited document or website
    url: str                                    # USE: Target link URL to the source
    relevance_score: float = Field(..., ge=0.0, le=1.0)  # USE: Score between 0 and 1 representing relevance
# =========== CLASS ===========


# =========== CLASS ===========
# ROLE: Model representing a section in a structured report.
class ReportSection(BaseModel):
    """ Section of report containing markdown text and its relevant citations. """

    # FLOW-1: Set up section fields with minimum content size requirement
    heading: str                                # USE: The section header/title
    content: str = Field(..., min_length=50)    # USE: Markdown textual content of the section
    citations: list[Citation] = []              # USE: List of supporting citation objects
# =========== CLASS ===========


# =========== CLASS ===========
# ROLE: Main structure representing a complete research output report.
class StructuredReport(BaseModel):
    """ Structure for representing a fully formatted research report. """

    # FLOW-1: Define report fields, section lists, scores, and timestamp
    title: str                                  # USE: Overall report title
    summary: str = Field(..., max_length=300)   # USE: Short high level summary of findings
    sections: list[ReportSection] = Field(..., min_length=1)  # USE: List containing at least one report section
    topic: str                                  # USE: Categorized research topic name
    confidence_score: float = Field(..., ge=0.0, le=1.0)  # USE: Confidence assessment score between 0 and 1
    total_sources: int = Field(..., ge=0)       # USE: Total number of sources cited
    generated_at: datetime = Field(default_factory=datetime.utcnow)  # USE: Timestamp when report was generated
# =========== CLASS ===========