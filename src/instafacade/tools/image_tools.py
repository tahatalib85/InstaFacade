"""
Image analysis tools for InstaFacade
"""

from typing import Dict, Any, Optional
from langchain.tools import tool
from ..core.analyzer import InstaFacadeAnalyzer


class ImageAnalysisTools:
    """Tools for image authenticity analysis"""
    
    def __init__(self, facade_analyzer: Optional[InstaFacadeAnalyzer] = None):
        self.facade_analyzer = facade_analyzer
    
    def get_tools(self):
        """Get all image analysis tools"""
        return [
            self.analyze_image_authenticity,
            self.get_verdict_summary,
            self.debug_test_tool,
            self.list_available_tools
        ]
    
    @property
    def analyze_image_authenticity(self):
        """Create the analyze image tool with proper closure"""
        facade_analyzer = self.facade_analyzer
        
        @tool
        def analyze_image_authenticity(image_path_or_url: str) -> Dict[str, Any]:
            """
            Analyze an image for authenticity using InstaFacade.
            
            Args:
                image_path_or_url: Path to the image file or URL to analyze
                
            Returns:
                Dictionary with analysis results including deception detection
            """
            print(f"🔍 TOOL CALLED: analyze_image_authenticity with input: {image_path_or_url}")
            
            if not facade_analyzer:
                print("❌ InstaFacade analyzer not available")
                return {"error": "InstaFacade analyzer not available"}
            
            try:
                # Check if input is URL or local file
                is_url = image_path_or_url.startswith(('http://', 'https://'))
                
                if is_url:
                    print(f"🌐 Input detected as URL, validating accessibility...")
                    import requests
                    response = requests.head(image_path_or_url, timeout=10)
                    response.raise_for_status()
                    print(f"✅ URL is accessible, starting analysis...")
                else:
                    print(f"📁 Input detected as local file path, checking existence...")
                    import os
                    if not os.path.exists(image_path_or_url):
                        print(f"❌ Image file not found: {image_path_or_url}")
                        return {"error": f"Image file not found: {image_path_or_url}"}
                    print(f"✅ Local file exists, starting analysis...")
                
                print(f"🔍 Analyzing {'URL' if is_url else 'file'}: {image_path_or_url}")
                results = facade_analyzer.analyze_image(image_path_or_url)
                print(f"✅ Analysis completed: {results}")
                return results
            except Exception as e:
                print(f"❌ Image analysis failed: {e}")
                return {"error": f"Analysis failed: {str(e)}"}
        
        return analyze_image_authenticity
    
    @property
    def get_verdict_summary(self):
        """Create the verdict summary tool with proper closure"""
        
        @tool
        def get_verdict_summary(analysis_results: Dict[str, Any]) -> str:
            """
            Get a human-readable summary of the image analysis results.
            
            Args:
                analysis_results: Results from analyze_image_authenticity
                
            Returns:
                Human-readable summary string
            """
            try:
                if "error" in analysis_results:
                    return f"Analysis Error: {analysis_results['error']}"
                
                if analysis_results.get("deception_detected", False):
                    source = analysis_results.get('matching_source', 'Unknown source')
                    title = analysis_results.get('matching_title', 'N/A')
                    return (
                        f"🚨 DECEPTION DETECTED! The image appears to be stolen/copied from online sources.\n"
                        f"📍 Source: {source}\n"
                        f"📄 Title: {title}\n"
                        f"This image is likely fake or misleading."
                    )
                else:
                    reason = analysis_results.get('reason', 'Analysis completed')
                    return (
                        f"✅ No clear deception detected. The image appears to be original or genuinely different "
                        f"from found matches.\n📝 Reason: {reason}"
                    )
            except Exception as e:
                return f"Error generating summary: {str(e)}"
        
        return get_verdict_summary
    
    @property
    def debug_test_tool(self):
        """Create the debug test tool with proper closure"""
        
        @tool
        def debug_test_tool(test_message: str = "test") -> str:
            """
            Debug tool to test if tools are being called properly.
            
            Args:
                test_message: A test message
                
            Returns:
                Confirmation message
            """
            print(f"🧪 DEBUG TOOL CALLED with message: {test_message}")
            return f"✅ Debug tool working! Received: {test_message}"
        
        return debug_test_tool
    
    @property
    def list_available_tools(self):
        """Create the list tools tool with proper closure"""
        
        @tool
        def list_available_tools() -> str:
            """
            List all available tools for debugging.
            
            Returns:
                List of available tools
            """
            print(f"🛠️  LIST TOOLS CALLED")
            return "Available tools: analyze_image_authenticity, get_verdict_summary, debug_test_tool, list_available_tools, check_latest_authentic_story, and Instagram MCP tools"
        
        return list_available_tools 