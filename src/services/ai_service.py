import asyncio
import logging
from anthropic import AsyncAnthropic
from typing import Optional


logger = logging.getLogger(__name__)


class AIService:
    def __init__(self, api_key: str):
        self.client = AsyncAnthropic(api_key=api_key)
    
    async def generate_summary(self, article_text: str, url: str) -> dict:
        """Generate English and Russian summaries of the article"""
        try:
            prompt = f"""
            Please provide a short summary of the following article in both English and Russian.
            
            Article URL: {url}
            Article Text: {article_text[:4000]}
            
            Please format your response as:
            ENGLISH:
            [English summary here]
            
            RUSSIAN:
            [Russian summary here]
            
            Keep each summary to 2-3 sentences and focus on the main points.
            """
            
            message = await self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            response_text = message.content[0].text
            
            # Parse the response to extract English and Russian summaries
            summaries = self._parse_summaries(response_text)
            
            return {
                "english": summaries.get("english", "Summary generation failed"),
                "russian": summaries.get("russian", "Не удалось создать резюме"),
                "url": url
            }
            
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            return {
                "english": "Error generating summary",
                "russian": "Ошибка при создании резюме",
                "url": url
            }
    
    def _parse_summaries(self, response_text: str) -> dict:
        """Parse English and Russian summaries from Claude's response"""
        summaries = {}
        
        lines = response_text.split('\n')
        current_section = None
        current_text = []
        
        for line in lines:
            line = line.strip()
            if line.startswith('ENGLISH:'):
                if current_section and current_text:
                    summaries[current_section] = ' '.join(current_text).strip()
                current_section = 'english'
                current_text = []
                # Check if there's text after ENGLISH:
                after_colon = line[8:].strip()
                if after_colon:
                    current_text.append(after_colon)
            elif line.startswith('RUSSIAN:'):
                if current_section and current_text:
                    summaries[current_section] = ' '.join(current_text).strip()
                current_section = 'russian'
                current_text = []
                # Check if there's text after RUSSIAN:
                after_colon = line[8:].strip()
                if after_colon:
                    current_text.append(after_colon)
            elif line and current_section:
                current_text.append(line)
        
        # Don't forget the last section
        if current_section and current_text:
            summaries[current_section] = ' '.join(current_text).strip()
        
        return summaries