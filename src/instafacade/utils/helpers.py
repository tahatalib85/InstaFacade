"""
Helper utilities for InstaFacade
"""

import os
import logging

logger = logging.getLogger(__name__)


def check_requirements() -> dict:
    """Check if all required environment variables and dependencies are available"""
    required_vars = {
        'OPENAI_API_KEY': 'OpenAI API key for GPT-4o',
        'IMGBB_API_KEY': 'ImgBB API key for image uploads', 
        'SERPAPI_KEY': 'SerpAPI key for reverse image search',
        'INSTAGRAM_USERNAME': 'Instagram username for MCP server',
        'INSTAGRAM_PASSWORD': 'Instagram password for MCP server'
    }
    
    missing_vars = []
    for var, description in required_vars.items():
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   • {var}: {required_vars[var]}")
        print(f"\nPlease add these to your .env file:")
        for var in missing_vars:
            print(f"{var}=your_{var.lower()}_value")
        
        return {
            "success": False,
            "missing": missing_vars
        }
    
    return {
        "success": True,
        "missing": []
    }


def get_instagram_mcp_path() -> str:
    """Get the path to the Instagram DM MCP server"""
    possible_paths = [
        "./instagram_dm_mcp/src/mcp_server.py",
        "../instagram_dm_mcp/src/mcp_server.py",
        os.getenv('INSTAGRAM_MCP_PATH', './instagram_dm_mcp/src/mcp_server.py')
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            logger.info(f"✅ Found Instagram MCP server at: {path}")
            return os.path.abspath(path)
    
    raise FileNotFoundError(
        f"Instagram DM MCP server not found. Tried paths: {possible_paths}\n"
        f"Please ensure the Instagram DM MCP repository is cloned and accessible."
    )


def get_python_executable() -> str:
    """Get the current Python executable path"""
    import sys
    python_path = sys.executable
    logger.info(f"✅ Using Python executable: {python_path}")
    return python_path 