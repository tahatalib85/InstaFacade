"""
Story analysis tools for InstaFacade
"""

from typing import Dict, Any, Optional
from langchain.tools import tool
from langchain_openai import ChatOpenAI
from ..core.analyzer import InstaFacadeAnalyzer
from .message_tools import MessageTools


class StoryAnalysisTools:
    """Tools for Instagram story authenticity analysis"""
    
    def __init__(self, facade_analyzer: Optional[InstaFacadeAnalyzer] = None, llm: Optional[ChatOpenAI] = None, message_tools: Optional[MessageTools] = None):
        self.facade_analyzer = facade_analyzer
        self.llm = llm
        self.message_tools = message_tools
    
    def get_tools(self):
        """Get all story analysis tools"""
        return [
            # Temporarily disabled for web interface to avoid conflicts with MCP tools
            # self.check_latest_authentic_story,
            self.analyze_story_authenticity,
            # self.regenerate_snarky_message, # This is a secondary action, not a primary tool
        ]
    
    @property
    def check_latest_authentic_story(self):
        """Create the check latest authentic story tool with proper closure"""
        facade_analyzer = self.facade_analyzer
        
        @tool
        def check_latest_authentic_story(username: str) -> Dict[str, Any]:
            """
            Starts the authenticity analysis for a user's latest Instagram story.
            This is the primary tool for story analysis. It initiates a multi-step process
            to fetch the story and perform a reverse image search analysis.
            Its job is to return the facts about the story's authenticity.
            """
            print(f"🕵️ TOOL CALLED: check_latest_authentic_story for user: {username}")
            
            if not facade_analyzer:
                print("❌ InstaFacade analyzer not available")
                return {"error": "InstaFacade analyzer not available"}
            
            try:
                print(f"📱 Step 1: Getting latest stories from @{username}...")
                
                return {
                    "step": "get_stories",
                    "instruction": f"Please call the get_user_stories tool with username '{username}' to get their latest stories, then pass the media_url of the first story to analyze_story_authenticity",
                    "username": username
                }
                
            except Exception as e:
                print(f"❌ Story check failed: {e}")
                return {"error": f"Story check failed: {str(e)}"}
        
        return check_latest_authentic_story
    
    @property
    def analyze_story_authenticity(self):
        """Create tool to analyze story authenticity and generate snarky messages"""
        facade_analyzer = self.facade_analyzer
        llm = self.llm
        
        @tool
        def analyze_story_authenticity(story_media_url: str, username: str, generate_snarky_message: bool = True) -> Dict[str, Any]:
            """
            Analyze a story image for authenticity and generate snarky message if fake.
            
            Args:
                story_media_url: URL of the story image to analyze
                username: Username of the person who posted the story
                generate_snarky_message: Whether to generate a snarky message if fake
                
            Returns:
                Dictionary with analysis results and optional snarky message
            """
            print(f"🔍 TOOL CALLED: analyze_story_authenticity for {username}'s story: {story_media_url}")
            
            if not facade_analyzer:
                return {"error": "InstaFacade analyzer not available"}
            
            try:
                print(f"🔎 Analyzing story image for authenticity...")
                analysis_results = facade_analyzer.analyze_image(story_media_url)
                
                result = {
                    "username": username,
                    "story_url": story_media_url,
                    "analysis": analysis_results,
                    "is_fake": analysis_results.get("deception_detected", False)
                }
                
                if analysis_results.get("deception_detected", False):
                    print(f"🚨 FAKE STORY DETECTED!")
                    
                    source = analysis_results.get('matching_source', 'Unknown source')
                    title = analysis_results.get('matching_title', 'N/A')
                    
                    if generate_snarky_message:
                        print(f"😈 Generating snarky message...")
                        
                        try:
                            if self.message_tools:
                                evidence_details = {
                                    "source": source,
                                    "title": title,
                                    "url": analysis_results.get('matching_image_url', story_media_url),
                                    "confidence": analysis_results.get('confidence', 0.9)
                                }
                                snarky_message = self.message_tools.generate_savage_message(
                                    username=username,
                                    content_type="story",
                                    is_fake=True,
                                    evidence_details=evidence_details,
                                    style="savage"
                                )
                            else:
                                # Fallback if message_tools is not available
                                snarky_message = f"Hey @{username}, nice 'original' content! 🤔 Just wondering how your personal photo ended up on {source} before you posted it... 📸✨"

                            result.update({
                                "snarky_message": snarky_message,
                                "proof_source": source,
                                "proof_title": title,
                                "message_ready": True
                            })
                            
                            print(f"✅ Snarky message generated: {snarky_message}")
                            
                        except Exception as e:
                            print(f"❌ Failed to generate snarky message: {e}")
                            result["snarky_message"] = f"Hey @{username}, nice 'original' content! 🤔 Just wondering how your personal photo ended up on {source} before you posted it... 📸✨"
                    
                else:
                    print(f"✅ Story appears to be authentic")
                    result.update({
                        "message": "Story appears to be authentic - no deception detected!",
                        "is_fake": False
                    })
                
                return result
                
            except Exception as e:
                print(f"❌ Story analysis failed: {e}")
                return {"error": f"Story analysis failed: {str(e)}"}
        
        return analyze_story_authenticity 