"""
Post analysis tools for InstaFacade
"""

from typing import Dict, Any, Optional
from langchain.tools import tool
from langchain_openai import ChatOpenAI
from ..core.analyzer import InstaFacadeAnalyzer
from .message_tools import MessageTools


class PostAnalysisTools:
    """Tools for Instagram post authenticity analysis"""
    
    def __init__(self, facade_analyzer: Optional[InstaFacadeAnalyzer] = None, llm: Optional[ChatOpenAI] = None, message_tools: Optional[MessageTools] = None):
        self.facade_analyzer = facade_analyzer
        self.llm = llm
        self.message_tools = message_tools
    
    def get_tools(self):
        """Get all post analysis tools"""
        return [
            # Temporarily disabled for web interface to avoid conflicts with MCP tools
            # self.check_latest_authentic_post,
            self.analyze_post_authenticity,
            # self.regenerate_post_snarky_message, # This is a secondary action, not a primary tool
        ]
    
    @property
    def check_latest_authentic_post(self):
        """Create the check latest authentic post tool with proper closure"""
        facade_analyzer = self.facade_analyzer
        
        @tool
        def check_latest_authentic_post(username: str) -> Dict[str, Any]:
            """
            Starts the authenticity analysis for a user's latest Instagram post.
            This is the primary tool for post analysis. It initiates a multi-step process
            to fetch the post and perform a reverse image search analysis.
            Its job is to return the facts about the post's authenticity.
            """
            print(f"🕵️ TOOL CALLED: check_latest_authentic_post for user: {username}")
            
            if not facade_analyzer:
                print("❌ InstaFacade analyzer not available")
                return {"error": "InstaFacade analyzer not available"}
            
            try:
                print(f"📱 Step 1: Getting latest posts from @{username}...")
                
                return {
                    "step": "get_posts",
                    "instruction": f"Please call the get_user_posts tool with username '{username}' and count 5 to get their latest posts, then pass the media_url of the first post to analyze_post_authenticity",
                    "username": username
                }
                
            except Exception as e:
                print(f"❌ Post check failed: {e}")
                return {"error": f"Post check failed: {str(e)}"}
        
        return check_latest_authentic_post
    
    @property
    def analyze_post_authenticity(self):
        """Create tool to analyze post authenticity and generate snarky messages"""
        facade_analyzer = self.facade_analyzer
        llm = self.llm
        
        @tool
        def analyze_post_authenticity(post_media_url: str, username: str, post_caption: str = "", generate_snarky_message: bool = True) -> Dict[str, Any]:
            """
            Analyze a post image for authenticity and generate snarky message if fake.
            
            Args:
                post_media_url: URL of the post image to analyze
                username: Username of the person who posted
                post_caption: Caption of the post (for context in snarky message)
                generate_snarky_message: Whether to generate a snarky message if fake
                
            Returns:
                Dictionary with analysis results and optional snarky message
            """
            print(f"🔍 TOOL CALLED: analyze_post_authenticity for {username}'s post: {post_media_url}")
            
            if not facade_analyzer:
                return {"error": "InstaFacade analyzer not available"}
            
            try:
                print(f"🔎 Analyzing post image for authenticity...")
                analysis_results = facade_analyzer.analyze_image(post_media_url)
                
                result = {
                    "username": username,
                    "post_url": post_media_url,
                    "post_caption": post_caption,
                    "analysis": analysis_results,
                    "is_fake": analysis_results.get("deception_detected", False)
                }
                
                if analysis_results.get("deception_detected", False):
                    print(f"🚨 FAKE POST DETECTED!")
                    
                    source = analysis_results.get('matching_source', 'Unknown source')
                    title = analysis_results.get('matching_title', 'N/A')
                    
                    if generate_snarky_message:
                        print(f"😈 Generating snarky message for fake post...")
                        
                        try:
                            if self.message_tools:
                                evidence_details = {
                                    "source": source,
                                    "title": title,
                                    "url": analysis_results.get('matching_image_url', post_media_url),
                                    "confidence": analysis_results.get('confidence', 0.9)
                                }
                                snarky_message = self.message_tools.generate_savage_message(
                                    username=username,
                                    content_type="post",
                                    is_fake=True,
                                    evidence_details=evidence_details,
                                    style="savage"
                                )
                            else:
                                # Fallback if message_tools is not available
                                snarky_message = f"Hey @{username}, love the 'original' content! 🤔 Just curious how your photo ended up on {source} before you posted it... 📸✨"
                            
                            result.update({
                                "snarky_message": snarky_message,
                                "proof_source": source,
                                "proof_title": title,
                                "message_ready": True
                            })
                            
                            print(f"✅ Snarky message generated: {snarky_message}")
                            
                        except Exception as e:
                            print(f"❌ Failed to generate snarky message: {e}")
                            result["snarky_message"] = f"Hey @{username}, love the 'original' content! 🤔 Just curious how your photo ended up on {source} before you posted it... 📸✨"
                    
                else:
                    print(f"✅ Post appears to be authentic")
                    result.update({
                        "message": "Post appears to be authentic - no deception detected!",
                        "is_fake": False
                    })
                
                return result
                
            except Exception as e:
                print(f"❌ Post analysis failed: {e}")
                return {"error": f"Post analysis failed: {str(e)}"}
        
        return analyze_post_authenticity 