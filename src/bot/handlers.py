import logging
import re
from telegram.ext import ContextTypes
from telegram import Update
from ..services.ai_service import AIService
from ..services.web_scraper import WebScraper


logger = logging.getLogger(__name__)


class BotHandlers:
    def __init__(self, ai_service: AIService):
        self.ai_service = ai_service
        self.web_scraper = WebScraper()
    
    async def check_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /check command"""
        await update.message.reply_text("I'm ready")
    
    async def url_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle messages containing URLs"""
        message_text = update.message.text
        
        # Send initial response
        await update.message.reply_text("I see")
        
        # Extract URLs from the message
        urls = self._extract_urls(message_text)
        
        if not urls:
            await update.message.reply_text("No valid URLs found in the message.")
            return
        
        # Process each URL
        for url in urls:
            await self._process_url(update, url)
    
    def _extract_urls(self, text: str) -> list:
        """Extract URLs from text"""
        url_pattern = re.compile(
            r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        )
        return url_pattern.findall(text)
    
    async def _process_url(self, update: Update, url: str):
        """Process a single URL: extract content and generate summary"""
        try:
            # Send processing message
            processing_msg = await update.message.reply_text(f"Processing: {url}")
            
            # Extract article content
            article_data = await self.web_scraper.extract_article_content(url)
            
            if not article_data:
                await processing_msg.edit_text(f"❌ Failed to extract content from: {url}")
                return
            
            # Generate summaries
            await processing_msg.edit_text(f"📝 Generating summaries for: {article_data['title']}")
            
            summaries = await self.ai_service.generate_summary(
                article_data['text'], 
                url
            )
            
            # Format and send the response
            response = self._format_summary_response(article_data, summaries)
            await processing_msg.edit_text(response, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Error processing URL {url}: {e}")
            await update.message.reply_text(f"❌ Error processing {url}: {str(e)}")
    
    def _format_summary_response(self, article_data: dict, summaries: dict) -> str:
        """Format the summary response"""
        title = article_data.get('title', 'Untitled')
        url = article_data.get('url', '')
        
        response = f"📰 **{title}**\n\n"
        response += f"🔗 {url}\n\n"
        
        if summaries.get('english'):
            response += f"🇺🇸 **English Summary:**\n{summaries['english']}\n\n"
        
        if summaries.get('russian'):
            response += f"🇷🇺 **Russian Summary:**\n{summaries['russian']}"
        
        return response