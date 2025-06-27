#!/usr/bin/env python3
"""
Setup script to create the initial Instagram session
Run this once before using the InstaFacade agent
"""

import os
import subprocess
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def main():
    print("🚀 Instagram Session Setup")
    print("=" * 40)
    
    # Get credentials
    username = os.getenv('INSTAGRAM_USERNAME')
    password = os.getenv('INSTAGRAM_PASSWORD')
    
    if not username or not password:
        print("❌ Error: Instagram credentials not found!")
        print("Please add INSTAGRAM_USERNAME and INSTAGRAM_PASSWORD to your .env file")
        return False
    
    print(f"📱 Setting up session for: {username}")
    print("⚠️  You may need to approve a 2FA request on your phone")
    
    # Path to MCP server
    mcp_server_path = Path("instagram_dm_mcp/src/mcp_server.py")
    if not mcp_server_path.exists():
        print(f"❌ Error: MCP server not found at {mcp_server_path}")
        return False
    
    # Run the MCP server to create session
    cmd = [
        sys.executable,
        str(mcp_server_path),
        "--username", username,
        "--password", password,
        "--session-file", "session.json"
    ]
    
    print("🔄 Starting Instagram login process...")
    print("   (This will exit after creating the session)")
    
    try:
        # Run for a short time to create session, then stop
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # Wait a bit for login to complete
        import time
        time.sleep(10)
        
        # Kill the process
        process.terminate()
        
        # Check if session file was created
        if Path("session.json").exists():
            print("✅ Session created successfully!")
            print("🎉 You can now run the InstaFacade agent")
            return True
        else:
            print("❌ Session file not created. Please check the output above for errors.")
            return False
            
    except Exception as e:
        print(f"❌ Error during setup: {e}")
        return False

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1) 