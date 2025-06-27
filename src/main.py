"""
InstaFacade - CLI Entry Point
AI-powered image authenticity analyzer with Instagram integration (CLI Mode)
"""

import asyncio
import sys
import os

# Add src to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from instafacade import InstaFacadeAgent
from instafacade.utils import check_requirements


async def main():
    """Main function to run the InstaFacade Agent in CLI mode"""
    print("🚀 InstaFacade CLI Agent with Instagram DM MCP")
    print("=" * 50)
    
    # Check requirements
    if not check_requirements():
        print("❌ Requirements check failed. Please fix the issues above.")
        return
    
    try:
        # Create and run the agent in interactive CLI mode
        agent = InstaFacadeAgent()
        await agent.run_interactive_session()
        
    except FileNotFoundError as e:
        print(f"❌ Setup Error: {str(e)}")
        print("\n💡 Setup Instructions:")
        print("1. Clone the Instagram DM MCP repository:")
        print("   git clone https://github.com/trypeggy/instagram_dm_mcp.git")
        print("\n2. Install dependencies:")
        print("   pip install -r requirements.txt")
        print("\n3. Set up your .env file with Instagram credentials")
        
    except KeyboardInterrupt:
        print("\n👋 InstaFacade CLI session ended by user")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        print("\n💡 Try running with debug mode for more details")


if __name__ == "__main__":
    asyncio.run(main()) 