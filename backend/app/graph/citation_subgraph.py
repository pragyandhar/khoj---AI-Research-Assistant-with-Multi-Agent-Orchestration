# Task-1: CitationState(TypedDict) banao with fields: citations: list[dict], verified_citations: list[dict], failed_citations: list[dict]
# Task-2: async def verify_citation_node(state: CitationState) -> dict banao — har citation ke liye URL accessible hai check karo (httpx.AsyncClient se HEAD request), accessible hai toh verified_citations mein add karo, nahi hai toh failed_citations mein
# Task-3: async def score_citations_node(state: CitationState) -> dict banao — verified citations ko relevance score ke basis pe sort karo, top 5 rakho
# Task-4: build_citation_subgraph() function banao — StateGraph(CitationState) banao, dono nodes add karo, verify → score edge lagao, compile karo
# Task-5: Main graph mein citation subgraph ko node ki tarah add karo: workflow.add_node("citation_check", build_citation_subgraph()) — LangGraph automatically subgraph ko invoke karta hai jab yeh node aata hai
# Task-6: Edge update karo: summary → citation_check → output