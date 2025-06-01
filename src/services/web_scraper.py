import aiohttp
import logging
from bs4 import BeautifulSoup
from newspaper import Article
from typing import Optional


logger = logging.getLogger(__name__)


class WebScraper:
    def __init__(self):
        self.timeout = aiohttp.ClientTimeout(total=30)
    
    async def extract_article_content(self, url: str) -> Optional[dict]:
        """Extract article content from URL"""
        try:
            # First try with newspaper3k
            article_data = await self._extract_with_newspaper(url)
            
            if article_data and article_data.get('text'):
                return article_data
            
            # Fallback to manual scraping
            return await self._extract_with_bs4(url)
            
        except Exception as e:
            logger.error(f"Error extracting content from {url}: {e}")
            return None
    
    async def _extract_with_newspaper(self, url: str) -> Optional[dict]:
        """Extract content using newspaper3k library"""
        try:
            article = Article(url)
            article.download()
            article.parse()
            
            if article.text and len(article.text.strip()) > 100:
                return {
                    'title': article.title or 'Untitled',
                    'text': article.text,
                    'url': url,
                    'authors': article.authors or [],
                    'publish_date': article.publish_date
                }
            
            return None
            
        except Exception as e:
            logger.warning(f"Newspaper3k extraction failed for {url}: {e}")
            return None
    
    async def _extract_with_bs4(self, url: str) -> Optional[dict]:
        """Fallback extraction using BeautifulSoup"""
        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.get(url) as response:
                    if response.status != 200:
                        logger.error(f"HTTP {response.status} for {url}")
                        return None
                    
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Remove script and style elements
                    for script in soup(["script", "style"]):
                        script.decompose()
                    
                    # Try to find title
                    title = None
                    title_tags = soup.find_all(['h1', 'title'])
                    if title_tags:
                        title = title_tags[0].get_text(strip=True)
                    
                    # Extract text content
                    # Look for common article containers
                    content_selectors = [
                        'article', '.article', '.content', '.post-content',
                        '.entry-content', 'main', '.main-content'
                    ]
                    
                    text_content = ""
                    for selector in content_selectors:
                        elements = soup.select(selector)
                        if elements:
                            text_content = elements[0].get_text(separator=' ', strip=True)
                            break
                    
                    # If no specific content area found, get body text
                    if not text_content:
                        body = soup.find('body')
                        if body:
                            text_content = body.get_text(separator=' ', strip=True)
                    
                    if len(text_content.strip()) > 100:
                        return {
                            'title': title or 'Untitled',
                            'text': text_content,
                            'url': url,
                            'authors': [],
                            'publish_date': None
                        }
                    
                    return None
                    
        except Exception as e:
            logger.error(f"BeautifulSoup extraction failed for {url}: {e}")
            return None