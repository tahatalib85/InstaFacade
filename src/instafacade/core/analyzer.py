"""
InstaFacade Image Analyzer - Core image authenticity analysis functionality
"""

import os
import requests
import base64
from typing import Dict, Any, Optional
from serpapi import GoogleSearch
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class InstaFacadeAnalyzer:
    """
    InstaFacade - AI-powered image authenticity analyzer
    Detects if someone is lying about their social media story by comparing with reverse image search results
    """
    
    def __init__(self):
        """Initialize the analyzer with API keys from environment variables"""
        self.imgbb_api_key = os.getenv('IMGBB_API_KEY')
        self.serpapi_key = os.getenv('SERPAPI_KEY') 
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        
        # Validate API keys
        self._validate_api_keys()
        
        # Initialize OpenAI client
        self.openai_client = OpenAI(api_key=self.openai_api_key)
        
        # Configuration
        self.download_dir = "reverse_search_images"
        self.max_matches_to_check = 3
        self.chunk_size = 8192
    
    def _validate_api_keys(self):
        """Validate that all required API keys are present"""
        missing_keys = []
        
        if not self.imgbb_api_key:
            missing_keys.append('IMGBB_API_KEY')
        if not self.serpapi_key:
            missing_keys.append('SERPAPI_KEY')
        if not self.openai_api_key:
            missing_keys.append('OPENAI_API_KEY')
        
        if missing_keys:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_keys)}")
    
    def _is_url(self, path_or_url: str) -> bool:
        """Check if the input is a URL or a local file path"""
        return path_or_url.startswith(('http://', 'https://'))
    
    def upload_image_to_imgbb(self, image_path: str) -> str:
        """Upload image file to ImgBB to get a temporary URL"""
        with open(image_path, "rb") as file:
            encoded = base64.b64encode(file.read())
        
        url = "https://api.imgbb.com/1/upload"
        payload = {
            "key": self.imgbb_api_key,
            "image": encoded,
        }
        
        response = requests.post(url, payload)
        if response.status_code == 200:
            return response.json()['data']['url']
        else:
            raise Exception(f"Upload failed: {response.text}")
    
    def upload_image_url_to_imgbb(self, image_url: str) -> str:
        """Upload image from URL to ImgBB to get a temporary URL"""
        response = requests.get(image_url)
        response.raise_for_status()
        
        encoded = base64.b64encode(response.content)
        
        url = "https://api.imgbb.com/1/upload"
        payload = {
            "key": self.imgbb_api_key,
            "image": encoded,
        }
        
        response = requests.post(url, payload)
        if response.status_code == 200:
            return response.json()['data']['url']
        else:
            raise Exception(f"Upload failed: {response.text}")
    
    def search_with_google_lens(self, image_url: str) -> Dict[str, Any]:
        """Search for exact matches using SerpAPI Google Lens"""
        params = {
            "engine": "google_lens",
            "type": "exact_matches",
            "url": image_url,
            "api_key": self.serpapi_key
        }
        
        search = GoogleSearch(params)
        return search.get_dict()
    
    def download_file_from_url(self, url: str, local_path: Optional[str] = None) -> str:
        """Download a file from a URL and save it locally"""
        try:
            print(f"Starting download from: {url}")
            
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            if local_path is None:
                filename = url.split('/')[-1]
                if '?' in filename:
                    filename = filename.split('?')[0]
                if not filename or '.' not in filename:
                    filename = "downloaded_file"
                local_path = filename
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded_size = 0
            
            print(f"Downloading to: {local_path}")
            if total_size > 0:
                print(f"File size: {total_size:,} bytes ({total_size / (1024*1024):.2f} MB)")
            
            with open(local_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=self.chunk_size):
                    if chunk:
                        file.write(chunk)
                        downloaded_size += len(chunk)
                        
                        if total_size > 0:
                            progress = (downloaded_size / total_size) * 100
                            print(f"\rProgress: {progress:.1f}% ({downloaded_size:,}/{total_size:,} bytes)", end='', flush=True)
            
            print(f"\n✅ Download completed successfully!")
            print(f"File saved to: {os.path.abspath(local_path)}")
            
            return local_path
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"Download failed: {e}")
        except IOError as e:
            raise Exception(f"Failed to save file: {e}")
    
    def download_multiple_files(self, urls: list) -> list:
        """Download multiple files from URLs"""
        if not os.path.exists(self.download_dir):
            os.makedirs(self.download_dir)
            print(f"Created directory: {self.download_dir}")
        
        downloaded_files = []
        failed_downloads = []
        
        for i, url in enumerate(urls, 1):
            try:
                print(f"\n📥 Downloading file {i}/{len(urls)}")
                
                filename = url.split('/')[-1]
                if '?' in filename:
                    filename = filename.split('?')[0]
                if not filename or '.' not in filename:
                    filename = f"file_{i}"
                
                local_path = os.path.join(self.download_dir, filename)
                
                downloaded_file = self.download_file_from_url(url, local_path)
                downloaded_files.append(downloaded_file)
                
            except Exception as e:
                print(f"❌ Failed to download {url}: {e}")
                failed_downloads.append(url)
        
        print(f"\n📊 Download Summary:")
        print(f"✅ Successfully downloaded: {len(downloaded_files)} files")
        print(f"❌ Failed downloads: {len(failed_downloads)} files")
        
        return downloaded_files
    
    def download_image_from_url(self, image_url: str, local_path: Optional[str] = None) -> str:
        """Download an image from URL to local file"""
        if local_path is None:
            filename = image_url.split('/')[-1]
            if '?' in filename:
                filename = filename.split('?')[0]
            if not filename or '.' not in filename:
                filename = f"downloaded_image_{hash(image_url) % 10000}.jpg"
            local_path = filename
        
        return self.download_file_from_url(image_url, local_path)
    
    def encode_image_to_base64(self, image_path_or_url: str) -> str:
        """Encode an image file or URL to base64 string"""
        if self._is_url(image_path_or_url):
            response = requests.get(image_path_or_url)
            response.raise_for_status()
            return base64.b64encode(response.content).decode('utf-8')
        else:
            with open(image_path_or_url, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
    
    def compare_images_for_lying(self, story_image_path: str, reverse_search_image_path: str) -> str:
        """Compare two images using OpenAI GPT-4 Vision to detect if someone is lying"""
        try:
            print("Encoding images for analysis...")
            story_image_b64 = self.encode_image_to_base64(story_image_path)
            reverse_image_b64 = self.encode_image_to_base64(reverse_search_image_path)
            
            print("Sending images to OpenAI GPT-4 Vision for analysis...")
            
            prompt = """You are an expert image analyst tasked with detecting deception in social media stories.

CONTEXT:
- Image 1: This is from someone's social media story (they claim this is their original content/experience)
- Image 2: This is the similar image we found through reverse image search from other sources online

TASK:
Analyze both images carefully and determine if they are the same image. Consider:
- Visual similarity in composition, lighting, objects, people, backgrounds
- Identical or near-identical elements that suggest it's the same photo
- Minor differences that could be due to compression, cropping, or filters
- Whether the person posting Image 1 is likely lying about it being their original content
- Be very strict and critical as we will be accusing someone of lying about their story

CRITICAL INSTRUCTIONS:
- If the images are the same or exact copy or slight filter edited copy of the same image (indicating the person copied/stole the image for their story), respond with exactly: YES
- If the images are clearly different (indicating the person's story might be genuine), respond with exactly: NO
- Only respond with "YES" or "NO" - no other words, explanations, or punctuation
- Be strict in your analysis - even minor identical elements that suggest copying should result in "YES"

Analyze the images now:"""

            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{story_image_b64}",
                                    "detail": "high"
                                }
                            },
                            {
                                "type": "image_url", 
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{reverse_image_b64}",
                                    "detail": "high"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=10,
                temperature=0
            )
            
            result = response.choices[0].message.content.strip().upper()
            
            if result not in ["YES", "NO"]:
                if "YES" in result:
                    result = "YES"
                elif "NO" in result:
                    result = "NO"
                else:
                    raise Exception(f"Unexpected response from OpenAI: {result}")
            
            print(f"✅ Analysis complete. Result: {result}")
            return result
            
        except Exception as e:
            raise Exception(f"Image comparison failed: {e}")
    
    def analyze_image(self, image_path_or_url: str) -> Dict[str, Any]:
        """Main pipeline to analyze an image for authenticity"""
        is_url = self._is_url(image_path_or_url)
        
        print(f"🔍 Starting InstaFacade Analysis Pipeline")
        print(f"Original image {'URL' if is_url else 'path'}: {image_path_or_url}")
        print("="*60)
        
        # Handle URL vs local file validation
        if is_url:
            print("🌐 Input detected as URL")
            try:
                response = requests.head(image_path_or_url, timeout=10)
                response.raise_for_status()
                print("✅ URL is accessible")
            except requests.exceptions.RequestException as e:
                raise Exception(f"Cannot access image URL: {e}")
        else:
            print("📁 Input detected as local file path")
            if not os.path.exists(image_path_or_url):
                raise FileNotFoundError(f"Image file not found at {image_path_or_url}")
            print("✅ Local file exists")
        
        try:
            # Step 1: Upload image to ImgBB
            print("📤 Step 1: Uploading to ImgBB...")
            if is_url:
                image_url = self.upload_image_url_to_imgbb(image_path_or_url)
                print(f"✅ Image URL uploaded to ImgBB: {image_url}")
            else:
                image_url = self.upload_image_to_imgbb(image_path_or_url)
                print(f"✅ Image file uploaded to ImgBB: {image_url}")
            
            # For comparison purposes, we need a local file path
            local_image_path = image_path_or_url
            temp_download = False
            
            if is_url:
                print("📥 Downloading image from URL for comparison...")
                local_image_path = self.download_image_from_url(image_path_or_url, "temp_original_image.jpg")
                temp_download = True
                print(f"✅ Downloaded to: {local_image_path}")
            
            # Step 2: Search with Google Lens
            print("\n🔎 Step 2: Searching for exact matches with Google Lens...")
            results = self.search_with_google_lens(image_url)
            
            # Step 3: Process search results
            print("\n📊 Step 3: Processing search results...")
            
            if "exact_matches" in results and results["exact_matches"]:
                exact_matches = results["exact_matches"]
                print(f"Found {len(exact_matches)} total matches")
                
                first_5_matches = exact_matches[:self.max_matches_to_check]
                print(f"Processing first {len(first_5_matches)} matches...")
                
                # Extract thumbnail URLs
                thumbnail_urls = []
                for i, match in enumerate(first_5_matches, 1):
                    if 'thumbnail' in match:
                        thumbnail_urls.append(match['thumbnail'])
                        print(f"Match {i}: {match.get('title', 'N/A')} - {match.get('source', 'N/A')}")
                    else:
                        print(f"Match {i}: No thumbnail available")
                
                if not thumbnail_urls:
                    self._cleanup_temp_file(temp_download, local_image_path)
                    return {
                        "deception_detected": False,
                        "reason": "No thumbnail URLs found for comparison",
                        "matches_found": len(exact_matches)
                    }
                
                # Step 4: Download images
                print(f"\n⬇️ Step 4: Downloading {len(thumbnail_urls)} images...")
                downloaded_files = self.download_multiple_files(thumbnail_urls)
                
                if not downloaded_files:
                    self._cleanup_temp_file(temp_download, local_image_path)
                    return {
                        "deception_detected": False,
                        "reason": "No images were successfully downloaded",
                        "matches_found": len(exact_matches)
                    }
                
                print(f"✅ Successfully downloaded {len(downloaded_files)} images")
                
                # Step 5: Compare images
                print(f"\n🤖 Step 5: AI Analysis - Comparing with original image...")
                print("="*60)
                
                for i, downloaded_image in enumerate(downloaded_files, 1):
                    print(f"\n🔍 Analyzing image {i}/{len(downloaded_files)}: {os.path.basename(downloaded_image)}")
                    
                    try:
                        result = self.compare_images_for_lying(local_image_path, downloaded_image)
                        print(f"📊 Comparison result: {result}")
                        
                        if result == "YES":
                            print(f"\n🚨 DECEPTION DETECTED!")
                            print(f"Image {i} matches the original - person is likely LYING about their story!")
                            print(f"Matching image source: {first_5_matches[i-1].get('source', 'Unknown')}")
                            print(f"Matching image title: {first_5_matches[i-1].get('title', 'N/A')}")
                            
                            self._cleanup_temp_file(temp_download, local_image_path)
                            
                            return {
                                "deception_detected": True,
                                "matching_image_index": i,
                                "matching_source": first_5_matches[i-1].get('source', 'Unknown'),
                                "matching_title": first_5_matches[i-1].get('title', 'N/A'),
                                "total_matches_found": len(exact_matches),
                                "images_analyzed": i
                            }
                        else:
                            print(f"✅ Image {i} is different - continuing analysis...")
                            
                    except Exception as e:
                        print(f"❌ Error analyzing image {i}: {e}")
                        continue
                
                self._cleanup_temp_file(temp_download, local_image_path)
                
                return {
                    "deception_detected": False,
                    "reason": "No matching images found in analysis",
                    "total_matches_found": len(exact_matches),
                    "images_analyzed": len(downloaded_files)
                }
                
            else:
                print("✅ No exact matches found in reverse search")
                self._cleanup_temp_file(temp_download, local_image_path)
                
                return {
                    "deception_detected": False,
                    "reason": "No exact matches found in reverse search",
                    "total_matches_found": 0
                }
        
        except Exception as e:
            if 'temp_download' in locals() and temp_download and 'local_image_path' in locals() and os.path.exists(local_image_path):
                os.remove(local_image_path)
                print(f"🧹 Cleaned up temporary file after error: {local_image_path}")
            raise Exception(f"Pipeline Error: {e}")
    
    def _cleanup_temp_file(self, temp_download: bool, local_image_path: str):
        """Clean up temporary file if needed"""
        if temp_download and os.path.exists(local_image_path):
            os.remove(local_image_path)
            print(f"🧹 Cleaned up temporary file: {local_image_path}")
    
    def print_final_verdict(self, results: Dict[str, Any]):
        """Print the final verdict based on analysis results"""
        print("\n" + "="*60)
        print("🎯 FINAL VERDICT:")
        print("="*60)
        
        if results["deception_detected"]:
            print("🚨 RESULT: DECEPTION DETECTED")
            print("The person is likely LYING about their story!")
            print("The image appears to be stolen/copied from online sources.")
            print(f"Source: {results.get('matching_source', 'Unknown')}")
            print(f"Title: {results.get('matching_title', 'N/A')}")
        else:
            print("✅ RESULT: NO CLEAR DECEPTION DETECTED") 
            print("The image appears to be original or genuinely different from found matches.")
            print("However, this doesn't guarantee 100% authenticity.")
            print(f"Reason: {results.get('reason', 'Analysis completed')}")
        
        print("="*60) 