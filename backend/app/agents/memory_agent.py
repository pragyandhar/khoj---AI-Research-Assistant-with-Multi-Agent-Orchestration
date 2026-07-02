# WHAT DOES THIS FILE DO: Defines the MemoryMixin to track windowed request conversation history for LLM agents.

# ================== IMPORTS ==================
from langchain_classic.memory import ConversationBufferWindowMemory
# ================== IMPORTS ==================


# =========== CLASS ===========
# ROLE: Mixin class providing short-term conversation memory capabilities to agents.
class MemoryMixin:
    """ Mixin providing windowed conversation memory tracking. """


    # =========== FUNCTION ===========
    # ROLE: Initialize memory tracker storage with fixed window size of 10.
    def __init__(self):
        """ Setup memory buffer with 10-turns limit. """
        
        # FLOW-1: Initialize ConversationBufferWindowMemory object
        self.memory = ConversationBufferWindowMemory(
            k=10,
            return_messages=True,
            memory_key="chat_history"
        )                                       # USE: Store memory instance
    # =========== FUNCTION ===========


    # =========== FUNCTION ===========
    # ROLE: Fetch the list of historical messages from memory context.
    def get_memory_context(self) -> list:
        """ Returns the list of messages stored in the window buffer. """
        
        # FLOW-1: Retrieve message history list
        return self.memory.chat_memory.messages  # USE: Get messages list
    # =========== FUNCTION ===========


    # =========== FUNCTION ===========
    # ROLE: Append new message interaction to window memory.
    def save_to_memory(self, human_msg: str, ai_msg: str) -> None:
        """ Saves human query and corresponding AI response to context memory. """
        
        # FLOW-1: Call save_context on memory buffer object
        self.memory.save_context(
            {"input": human_msg},
            {"output": ai_msg}
        )                                       # USE: Store turn context
    # =========== FUNCTION ===========


    # =========== FUNCTION ===========
    # ROLE: Flush all stored history from memory.
    def clear_memory(self) -> None:
        """ Clear context variables and resets the window buffer. """
        
        # FLOW-1: Reset memory buffer
        self.memory.clear()                     # USE: Call clear method
    # =========== FUNCTION ===========
# =========== CLASS ===========