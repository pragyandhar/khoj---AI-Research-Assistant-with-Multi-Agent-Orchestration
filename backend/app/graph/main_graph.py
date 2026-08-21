# WHAT DOES THIS FILE DO: Constructs and compiles the core LangGraph workflow orchestrating the multi-agent execution pipeline.

# ================== IMPORTS ==================
from langgraph.graph import StateGraph, END

from app.graph.state import GraphState
from app.graph.nodes.router_node import router_node, route_after_approval
from app.graph.nodes.research_node import research_node
from app.graph.nodes.human_approval_node import human_approval_node
from app.graph.nodes.summary_node import summary_node
from app.graph.nodes.output_node import output_node
from app.graph.citation_subgraph import build_citation_subgraph
# ================== IMPORTS ==================


# =========== FUNCTION ===========
# ROLE: Compiles and builds the core StateGraph workflow with persistent checkpointer and store.
def build_graph(checkpointer=None, store=None):
    """ Setup nodes, linear edges, entry/finish points, and compile the graph. """
    
    # FLOW-1: Instantiate StateGraph with our custom GraphState TypedDict
    workflow = StateGraph(GraphState)           # USE: Define LangGraph state machine schema
    
    # FLOW-2: Register execution nodes including human approval step and citation subgraph
    workflow.add_node("router", router_node)    # USE: Register routing stage
    workflow.add_node("research", research_node)  # USE: Register search stage
    workflow.add_node("human_approval", human_approval_node)  # USE: Register human approval gate stage
    workflow.add_node("summary", summary_node)  # USE: Register summary parser stage
    workflow.add_node("citation_check", build_citation_subgraph())  # USE: Register citation subgraph check stage
    workflow.add_node("output", output_node)    # USE: Register final output stage
    
    # FLOW-3: Configure routing path edges — approval gate now sits before research fires
    workflow.set_entry_point("router")          # USE: Set graph execution entry node
    workflow.add_edge("router", "human_approval")  # USE: Route straight to approval gate before any web search
    workflow.add_conditional_edges(
        "human_approval",
        route_after_approval,                   # USE: Picks next node based on state["selected_agent"]
        {
            "science_research": "research",     # USE: All three routes converge on the same research node
            "tech_research": "research",         # USE: research_node itself picks the specialist agent to run
            "general_research": "research",
        }
    )                                           # USE: Conditional edge for dynamic post-approval agent routing
    workflow.add_edge("research", "summary")    # USE: Route to summary stage
    workflow.add_edge("summary", "citation_check")  # USE: Route to citation check subgraph
    workflow.add_edge("citation_check", "output")  # USE: Route to output stage
    workflow.set_finish_point("output")         # USE: Terminate graph at output stage
    
    # FLOW-4: Compile graph with checkpointer, long-term memory store, and interrupt configs
    compiled = workflow.compile(
        checkpointer=checkpointer,
        store=store,                             # USE: Long-term memory store, available to nodes via LangGraph's store injection
        interrupt_before=["human_approval"]
    )                                           # USE: Compile state machine
    
    return compiled
# =========== FUNCTION ===========