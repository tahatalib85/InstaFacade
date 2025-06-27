"""
Message sending tools for InstaFacade
"""

from typing import Dict, Any, Optional
from langchain.tools import tool
import logging

logger = logging.getLogger(__name__)


class MessageTools:
    """Tools for sending messages via Instagram DM"""
    
    def get_tools(self):
        """Get all message tools"""
        return [
            self.send_snarky_message_with_proof,
            self.send_post_snarky_message_with_proof,
        ]
    
    @property
    def send_snarky_message_with_proof(self):
        """Create tool to send the snarky message to the user"""
        
        @tool
        def send_snarky_message_with_proof(username: str, snarky_message: str, proof_source: str) -> Dict[str, Any]:
            """
            Send a snarky message to a user who posted a fake story, including proof.
            
            Args:
                username: Username to send the message to
                snarky_message: The snarky message to send
                proof_source: Source URL as proof of the fake content
                
            Returns:
                Dictionary with sending results
            """
            print(f"📤 TOOL CALLED: send_snarky_message_with_proof to @{username}")
            
            # Combine the snarky message with proof
            full_message = f"{snarky_message}\n\nProof: {proof_source}"
            
            print(f"📝 Full message to send: {full_message}")
            
            # This will instruct the agent to use the send_message MCP tool
            return {
                "instruction": f"Please call the send_message tool with username '{username}' and message '{full_message}'",
                "username": username,
                "message": full_message,
                "ready_to_send": True
            }
        
        return send_snarky_message_with_proof
    
    @property
    def send_post_snarky_message_with_proof(self):
        """Create tool to send the snarky message about a fake post to the user"""
        
        @tool
        def send_post_snarky_message_with_proof(username: str, snarky_message: str, proof_source: str) -> Dict[str, Any]:
            """
            Send a snarky message to a user who posted a fake image, including proof.
            
            Args:
                username: Username to send the message to
                snarky_message: The snarky message to send
                proof_source: Source URL as proof of the stolen content
                
            Returns:
                Dictionary with sending results
            """
            print(f"📤 TOOL CALLED: send_post_snarky_message_with_proof to @{username}")
            
            # Combine the snarky message with proof
            full_message = f"{snarky_message}\n\n🔍 Proof: {proof_source}\n\n#BustedByInstaFacade 📸✨"
            
            print(f"📝 Full message to send: {full_message}")
            
            # This will instruct the agent to use the send_message MCP tool
            return {
                "instruction": f"Please call the send_message tool with username '{username}' and message '{full_message}'",
                "username": username,
                "message": full_message,
                "ready_to_send": True
            }
        
        return send_post_snarky_message_with_proof

    def generate_savage_message(
        self,
        username: str,
        content_type: str,  # "story" or "post"
        is_fake: bool,
        evidence_details: Dict[str, Any],
        style: str = "savage"
    ) -> str:
        """
        Internal function to generate a savage message. THIS IS NOT A TOOL.
        It is called by other tools after analysis is complete.
        """
        try:
            from openai import OpenAI
            import os
            
            client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
            
            if is_fake:
                evidence_text = f"""
    EVIDENCE FOUND:
    - Original Source: {evidence_details.get('source', 'Unknown')}
    - Original Title: {evidence_details.get('title', 'N/A')}
    - Evidence URL: {evidence_details.get('url', 'N/A')}
    - Detection Confidence: {evidence_details.get('confidence', 0.0) * 100:.1f}%
    """
                
                style_instructions = {
                    "savage": "Be absolutely brutal and savage. No mercy. Call them out HARD.",
                    "unhinged": "Go completely unhinged. Maximum chaos energy. All caps allowed. Be absolutely chaotic.",
                    "chaotic": "Pure chaotic energy. Dramatic, over-the-top, theatrical. Think reality TV drama.",
                    "dramatic": "Shakespeare-level drama. Theatrical, poetic, but still savage.",
                    "gen_z": "Use Gen Z slang, internet culture, modern memes. Be savage but in Gen Z language."
                }
                
                prompt = f"""You are the most savage AI content detective ever created. You just caught @{username} red-handed posting STOLEN content on their Instagram {content_type}.

    {evidence_text}

    Your job is to generate an absolutely SAVAGE message to call them out. Style: {style} - {style_instructions.get(style, 'Be savage')}.

    REQUIREMENTS:
    1. Be absolutely savage and unforgiving
    2. Include the evidence URL in the message for proof
    3. Call out the specific platform where you found the original (e.g., Pinterest)
    4. Make fun of them for thinking they wouldn't get caught
    5. Use emojis strategically for maximum impact
    6. Keep it under 280 characters for Instagram DM
    7. Make it so savage that they'll think twice before stealing content again

    DO NOT be nice or polite. This is about calling out content theft. Be RUTHLESS but clever.

    Generate the message now:"""

            else:
                prompt = f"""Generate a message congratulating @{username} for posting authentic, original content on their Instagram {content_type}. Be enthusiastic and supportive, but keep the same energy level as if you were being savage. Make it fun and engaging. Style: {style}. Keep under 280 characters."""

            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a savage AI content detective that generates brutal but clever callout messages for content thieves."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=150,
                temperature=0.9  # High creativity for savage content
            )
            
            message = response.choices[0].message.content.strip()
            logger.info(f"Generated savage message: {message}")
            return message
            
        except Exception as e:
            logger.error(f"Failed to generate savage message: {e}")
            # Fallback savage message
            if is_fake:
                evidence_url = evidence_details.get('url', 'N/A')
                source = evidence_details.get('source', 'the internet')
                return f"@{username} really thought we wouldn't catch this STOLEN content from {source}?! 💀🔍 We got receipts: {evidence_url} The audacity is UNMATCHED! 😤🚨"
            else:
                return f"@{username} said 'I'm gonna post ORIGINAL content' and actually DID! The authenticity is immaculate! 💅✨👑" 