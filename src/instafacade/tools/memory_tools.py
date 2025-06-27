"""
Memory management tools for InstaFacade
"""

from typing import Dict, Any, List
from langchain.tools import tool
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage


class MemoryTools:
    """Tools for managing conversation memory"""
    
    def __init__(self, conversation_history: List, thread_id: str):
        self.conversation_history = conversation_history
        self.thread_id = thread_id
    
    def get_tools(self):
        """Get all memory management tools"""
        return [
            self.manage_conversation_memory
        ]
    
    @property
    def manage_conversation_memory(self):
        """Create tool to manage conversation memory"""
        conversation_history = self.conversation_history
        thread_id = self.thread_id
        
        @tool
        def manage_conversation_memory(action: str = "status") -> Dict[str, Any]:
            """
            Manage conversation memory and history.
            
            Args:
                action: Action to perform - "status", "clear", "summary"
                
            Returns:
                Dictionary with memory management results
            """
            print(f"💾 TOOL CALLED: manage_conversation_memory with action: {action}")
            
            if action == "status":
                return {
                    "action": "status",
                    "message_count": len(conversation_history),
                    "thread_id": thread_id,
                    "memory_enabled": True,
                    "last_messages": [
                        {
                            "type": type(msg).__name__,
                            "content_preview": str(msg.content)[:100] + "..." if len(str(msg.content)) > 100 else str(msg.content)
                        }
                        for msg in conversation_history[-3:]  # Show last 3 messages
                    ]
                }
            
            elif action == "clear":
                old_count = len(conversation_history)
                # Keep only the system message
                system_messages = [msg for msg in conversation_history if isinstance(msg, SystemMessage)]
                conversation_history.clear()
                conversation_history.extend(system_messages)
                return {
                    "action": "clear",
                    "message": f"Conversation history cleared! Removed {old_count - len(system_messages)} messages.",
                    "remaining_messages": len(conversation_history)
                }
            
            elif action == "summary":
                message_types = {}
                for msg in conversation_history:
                    msg_type = type(msg).__name__
                    message_types[msg_type] = message_types.get(msg_type, 0) + 1
                
                return {
                    "action": "summary",
                    "total_messages": len(conversation_history),
                    "message_types": message_types,
                    "thread_id": thread_id,
                    "memory_enabled": True
                }
            
            else:
                return {"error": f"Unknown action: {action}. Use 'status', 'clear', or 'summary'"}
        
        return manage_conversation_memory 