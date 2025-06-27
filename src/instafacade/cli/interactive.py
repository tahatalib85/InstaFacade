"""
Interactive session handler for InstaFacade
"""

import asyncio
from typing import Dict, Any, List, Optional
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langgraph.prebuilt import create_react_agent


class InteractiveSession:
    """Handles interactive chat sessions with the InstaFacade agent"""
    
    def __init__(self, agent, mcp_session, tools: List, conversation_history: List, thread_id: str):
        self.agent = agent
        self.mcp_session = mcp_session
        self.tools = tools
        self.conversation_history = conversation_history
        self.thread_id = thread_id
    
    async def run(self):
        """Run the interactive session"""
        self._print_welcome_message()
        
        # Initialize conversation with system message
        system_message = SystemMessage(content="""You are InstaFacade, an AI assistant that combines image authenticity analysis with Instagram messaging capabilities. 

You have access to:
- Image authenticity analysis using reverse image search
- Instagram DM sending and receiving
- Story and post checking for fake content
- Snarky message generation for calling out fake content

Remember previous conversations and maintain context throughout the session. Be helpful, witty, and thorough in your responses.""")
        
        self.conversation_history.append(system_message)
        
        while True:
            try:
                user_input = input("\n🤖 > ").strip()
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("👋 Goodbye!")
                    break
                
                if not user_input:
                    continue
                
                print(f"\n🔄 Processing: {user_input}")
                
                # Add user message to conversation history
                user_message = HumanMessage(content=user_input)
                self.conversation_history.append(user_message)
                
                # Process the user input with the agent
                print("🤖 Sending to LangChain agent with conversation history...")
                config = {"configurable": {"thread_id": self.thread_id}}
                
                response = await self.agent.ainvoke(
                    {"messages": self.conversation_history}, 
                    config=config
                )
                
                # Extract and display the response
                self._process_response(response)
                
            except KeyboardInterrupt:
                print("\n👋 Session interrupted. Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error processing request: {str(e)}")
    
    def _print_welcome_message(self):
        """Print the welcome message and instructions"""
        print("\n✅ Agent successfully initialized!")
        print("=" * 60)
        print("Available capabilities:")
        print("  🔍 Image authenticity analysis (InstaFacade)")
        print("  📱 Instagram direct messaging")
        print("  👤 Instagram user information lookup")
        print("  📸 Instagram stories and posts analysis")
        print("  📩 Send photos/videos via Instagram DM")
        print("  🔎 Search Instagram users and threads")
        
        print("\n💡 Example commands:")
        print("  • 'Analyze this image for authenticity: test.jpg'")
        print("  • 'Send a message to @username saying hello'")
        print("  • 'Get user info for @username'")
        print("  • 'Send photo test.jpg to @username with message'")
        print("  • 'Analyze image test.jpg and if fake, message @username about it'")
        print("  • 'Check @username latest story for authenticity'")
        print("  • 'Check @username latest post for authenticity'")
        print("  • 'Search for users named john'")
        print("  • 'Get recent posts from @username'")
        print("  • 'Show my conversation history' (memory management)")
        print("  • 'Clear conversation history' (memory management)")
        
        print("\nType your request or 'quit' to exit.")
        print("💾 Conversation history is maintained across messages!")
        print("=" * 60)
    
    def _process_response(self, response: Dict[str, Any]):
        """Process and display the agent response"""
        print(f"🤖 Agent response type: {type(response)}")
        print(f"🤖 Agent response keys: {response.keys() if isinstance(response, dict) else 'Not a dict'}")
        
        # Extract and display the response
        if isinstance(response, dict) and "messages" in response:
            messages = response["messages"]
            print(f"🤖 Number of messages: {len(messages)}")
            
            # Get the last AI message
            ai_messages = [msg for msg in messages if isinstance(msg, AIMessage)]
            if ai_messages:
                last_ai_message = ai_messages[-1]
                # Add AI response to conversation history
                self.conversation_history.append(last_ai_message)
                print(f"\n✨ Response: {last_ai_message.content}")
                print(f"💾 Conversation history now has {len(self.conversation_history)} messages")
            else:
                # Fallback: display all messages
                for i, msg in enumerate(messages):
                    print(f"🤖 Message {i}: Type={type(msg)}, Content preview={str(msg)[:100]}...")
                
                if messages:
                    last_message = messages[-1]
                    if hasattr(last_message, 'content'):
                        print(f"\n✨ Response: {last_message.content}")
                        # Add to history if it's not already there
                        if not isinstance(last_message, (HumanMessage, AIMessage, SystemMessage)):
                            ai_response = AIMessage(content=str(last_message.content))
                            self.conversation_history.append(ai_response)
                    else:
                        print(f"\n✨ Response: {last_message}")
                        ai_response = AIMessage(content=str(last_message))
                        self.conversation_history.append(ai_response)
        else:
            print(f"\n✨ Response: {response}")
            # Add response to conversation history
            ai_response = AIMessage(content=str(response))
            self.conversation_history.append(ai_response) 