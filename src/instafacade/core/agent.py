"""
Main InstaFacade Agent - Orchestrates all components for image analysis and Instagram integration
"""

import asyncio
import os
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path
from dotenv import load_dotenv

# LangChain imports
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

# Import components
from .analyzer import InstaFacadeAnalyzer
from ..tools import ImageAnalysisTools, StoryAnalysisTools, PostAnalysisTools, MessageTools, MemoryTools
from ..cli.interactive import InteractiveSession
from ..utils.helpers import check_requirements, get_instagram_mcp_path, get_python_executable

# Load environment variables
load_dotenv()

# Set up logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class InstaFacadeAgent:
    """
    Main LangChain agent that combines InstaFacade image analysis with Instagram DM capabilities
    """
    
    def __init__(self):
        """Initialize the agent with OpenAI model and components"""
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        
        # Initialize the language model
        self.llm = ChatOpenAI(
            model="gpt-4o",
            api_key=self.openai_api_key,
            temperature=0
        )
        
        # Initialize InstaFacade analyzer
        try:
            self.facade_analyzer = InstaFacadeAnalyzer()
            logger.info("✅ InstaFacade analyzer initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize InstaFacade analyzer: {e}")
            self.facade_analyzer = None
        
        # Get Instagram MCP server path
        self.instagram_mcp_path = get_instagram_mcp_path()
        
        # Initialize memory for conversation history
        self.memory = MemorySaver()
        self.conversation_history = []
        self.thread_id = "instafacade_session"
        
        # Initialize tool components
        self._initialize_tool_components()
    
    def _initialize_tool_components(self):
        """Initialize all tool components"""
        self.message_tools = MessageTools()
        self.image_tools = ImageAnalysisTools(self.facade_analyzer)
        self.story_tools = StoryAnalysisTools(self.facade_analyzer, self.llm, self.message_tools)
        self.post_tools = PostAnalysisTools(self.facade_analyzer, self.llm, self.message_tools)
        self.memory_tools = MemoryTools(self.conversation_history, self.thread_id)
    
    def _collect_instafacade_tools(self) -> List:
        """Collect all InstaFacade tools"""
        all_tools = []
        
        if self.facade_analyzer:
            all_tools.extend(self.image_tools.get_tools())
            all_tools.extend(self.story_tools.get_tools())
            all_tools.extend(self.post_tools.get_tools())
            all_tools.extend(self.message_tools.get_tools())
            all_tools.extend(self.memory_tools.get_tools())
            logger.info("🎯 Added InstaFacade tools: image analysis, story/post checking, messaging, memory")
        
        return all_tools
    
    async def run_interactive_session(self):
        """Run an interactive session with the agent"""
        print("\n🎯 InstaFacade Agent with Instagram DM MCP")
        print("=" * 60)
        
        try:
            # Import MCP components here to avoid circular imports
            from mcp import ClientSession, StdioServerParameters
            from mcp.client.stdio import stdio_client
            from langchain_mcp_adapters.tools import load_mcp_tools
            
            # Create MCP server parameters with correct Python path and session support
            python_executable = get_python_executable()
            session_file_path = os.path.join(os.getcwd(), "session.json")
            
            server_params = StdioServerParameters(
                command=python_executable,
                args=[
                    self.instagram_mcp_path,
                    "--session-file", session_file_path
                ]
            )
            
            # Validate credentials
            self._validate_instagram_credentials()
            
            # Log the MCP server command for debugging
            logger.info(f"🔧 Starting MCP server with command: {python_executable} {' '.join(server_params.args)}")
            print(f"🔧 Using Python: {python_executable}")
            print(f"🔧 Session file: {session_file_path}")
            
            # Keep the MCP connection alive throughout the session
            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    # Initialize MCP connection
                    print("📡 Initializing Instagram DM MCP...")
                    await asyncio.wait_for(session.initialize(), timeout=60.0)
                    print("✅ MCP session initialized successfully!")
                    
                    # Load MCP tools
                    print("🔧 Loading Instagram DM tools...")
                    mcp_tools = await load_mcp_tools(session)
                    logger.info(f"🔧 Loaded {len(mcp_tools)} MCP tools: {[tool.name for tool in mcp_tools]}")
                    
                    # Use MCP tools directly without debug wrapper
                    wrapped_mcp_tools = mcp_tools
                    
                    # Collect all tools
                    instafacade_tools = self._collect_instafacade_tools()
                    all_tools = instafacade_tools + wrapped_mcp_tools
                    
                    logger.info(f"🛠️  Total tools available: {len(all_tools)}")
                    
                    # Print tool information
                    self._print_tool_info(all_tools)
                    
                    # Create the React agent with memory
                    agent = create_react_agent(
                        model=self.llm, 
                        tools=all_tools,
                        checkpointer=self.memory
                    )
                    
                    print("🎉 Successfully connected to Instagram DM MCP!")
                    
                    # Run interactive session
                    interactive_session = InteractiveSession(
                        agent=agent,
                        mcp_session=session,
                        tools=all_tools,
                        conversation_history=self.conversation_history,
                        thread_id=self.thread_id
                    )
                    
                    await interactive_session.run()
                    
        except Exception as e:
            print(f"\n🚨 Failed to start interactive session: {str(e)}")
            self._print_troubleshooting_tips()
            logger.error(f"Failed to start interactive session: {str(e)}")
    
    def _validate_instagram_credentials(self):
        """Validate Instagram credentials"""
        instagram_username = os.getenv('INSTAGRAM_USERNAME')
        instagram_password = os.getenv('INSTAGRAM_PASSWORD')
        
        print(f"📋 Using Instagram credentials:")
        print(f"   Username: {instagram_username if instagram_username else '❌ NOT SET'}")
        print(f"   Password: {'✅ SET' if instagram_password else '❌ NOT SET'}")
        
        if not instagram_username or not instagram_password:
            raise Exception("Instagram credentials not found in environment variables!")
        
        print("📱 Instagram will send a 2FA request to your phone - please approve it QUICKLY!")
        print("⚡ The server may crash if you take too long, so be ready!")
        print("⏳ Starting connection process...")
    

    
    def _print_tool_info(self, all_tools: List):
        """Print detailed tool information"""
        print(f"🔧 DETAILED TOOL LIST:")
        for i, tool in enumerate(all_tools):
            print(f"   {i+1}. {tool.name}: {tool.description[:100]}...")
    
    def _print_troubleshooting_tips(self):
        """Print troubleshooting tips"""
        print("\n💡 Troubleshooting tips:")
        print("1. Make sure your Instagram credentials are correct in .env")
        print("2. Approve Instagram 2FA requests quickly on your phone")
        print("3. Check if Instagram DM MCP server is properly installed")
        print("4. Try running the script again")
    


    async def analyze_and_notify(self, image_path: str, username: str, custom_message: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze an image and optionally notify a user via Instagram DM if deception is detected.
        
        Args:
            image_path: Path to the image to analyze
            username: Instagram username to notify
            custom_message: Custom message to send (optional)
            
        Returns:
            Dictionary with analysis and notification results
        """
        try:
            # This would need to be implemented with the full MCP connection
            # For now, return a placeholder
            return {"success": False, "error": "This method needs full MCP implementation"}
            
        except Exception as e:
            return {"success": False, "error": str(e)} 