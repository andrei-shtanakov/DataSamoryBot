import os
import logging
from dotenv import load_dotenv
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from src.bot.handlers import BotHandlers
from src.services.ai_service import AIService

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


def main():
    print("Starting DataSamoryBot...")
    
    # Get tokens from environment
    bot_token = os.getenv("BOT_TOKEN")
    claude_api_key = os.getenv("CLAUDE_API_KEY")
    
    if not bot_token:
        logger.error("BOT_TOKEN not found in environment variables")
        return
    
    if not claude_api_key:
        logger.error("CLAUDE_API_KEY not found in environment variables")
        return
    
    # Initialize services
    ai_service = AIService(claude_api_key)
    handlers = BotHandlers(ai_service)
    
    # Build application
    app = ApplicationBuilder().token(bot_token).build()
    
    # Add handlers
    app.add_handler(CommandHandler("check", handlers.check_command))
    app.add_handler(MessageHandler(filters.Entity("url"), handlers.url_handler))
    
    # Start polling
    logger.info("Bot started successfully")
    app.run_polling()


if __name__ == "__main__":
    main()
