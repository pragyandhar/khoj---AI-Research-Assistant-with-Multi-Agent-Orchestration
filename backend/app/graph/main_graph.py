# WHAT DOES THIS FILE DO: Constructs and compiles the core LangGraph workflow orchestrating the multi-agent execution pipeline.

# ================== IMPORTS ==================
from langgraph.graph import StateGraph, END

from app.graph.state import GraphState
from app.graph.nodes.router_node import router_node
from app.graph.nodes.research_node import research_node
from app.graph.nodes.summary_node import summary_node
from app.graph.nodes.output_node import output_node
# ================== IMPORTS ==================


# =========== FUNCTION ===========
# ROLE: Compiles and builds the core StateGraph workflow.
def build_graph():
    """ Setup nodes, linear edges, entry/finish points, and compile the graph. """
    
    # FLOW-1: Instantiate StateGraph with our custom GraphState TypedDict
    workflow = StateGraph(GraphState)           # USE: Define LangGraph state machine schema
    
    # FLOW-2: Register execution nodes
    workflow.add_node("router", router_node)    # USE: Register routing stage
    workflow.add_node("research", research_node)  # USE: Register search stage
    workflow.add_node("summary", summary_node)  # USE: Register summary parser stage
    workflow.add_node("output", output_node)    # USE: Register final output stage
    
    # FLOW-3: Configure linear routing path edges
    workflow.set_entry_point("router")          # USE: Set graph execution entry node
    workflow.add_edge("router", "research")     # USE: Step 1 edge
    workflow.add_edge("research", "summary")    # USE: Step 2 edge
    workflow.add_edge("summary", "output")      # USE: Step 3 edge
    workflow.set_finish_point("output")         # USE: Terminate graph at output stage
    
    # FLOW-4: Compile graph and return it
    compiled = workflow.compile()
    
    return compiled
# =========== FUNCTION ===========


# =========== VARIABLES : Singleton compiled graph instance ===========
graph = build_graph()                           # USE: Singleton graph object for orchestration
# =========== VARIABLES : Singleton compiled graph instance ===========