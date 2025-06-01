# Telegram Article Bot Project Organization

I need a Telegram bot written in python that will process the links that I send to it as follows:

1. Print a short summary of the article via an online link in English and Russian using the API to Claude or ChatGPT
2. Save them as .md of the file (including the link at the beginning of the file under the header).
3. Attach tags to the text. Tags are taken from the project file, where new tags can be added if the existing ones do not fit or do not cover all the topics of the article.

The next stage:

1. commit and create a pool request.

Stage 3

1. Working with the Obsidian API

## Project Structure

```plaintext
DataSamoryBot/
├── src/
│   ├── bot/
│   │   ├── handlers.py          # Command and message handlers
│   │   ├── middleware.py        # Middleware for logging
│   │   └── keyboards.py         # Inline keyboards for interface
│   ├── services/
│   │   ├── ai_service.py        # Claude/ChatGPT API integration
│   │   ├── web_scraper.py       # Content extraction from URLs
│   │   ├── file_manager.py      # .md file management
│   │   ├── tag_manager.py       # Tagging system
│   │   ├── git_service.py       # Git operations and PR creation
│   │   └── obsidian_service.py  # Obsidian integration
│   ├── models/
│   │   ├── article.py           # Article model
│   │   └── tag.py               # Tag model
│   └── utils/
│       ├── config.py            # Configuration
│       ├── logger.py            # Logging setup
│       └── validators.py        # URL and data validation
├── data/
│   ├── tags.json                # Tag database
│   ├── articles/                # Folder with .md files
│   └── templates/               # Templates for .md files
├── tests/
├── requirements.txt
├── .env.example
├── README.md
└── main.py
```

## Architectural Decisions

Database: SQLite for storing article metadata, processing history, and article-tag relationships.
Task Queue: Redis + Celery for asynchronous processing of long operations (parsing, AI analysis, Git operations).
Caching: Redis for caching AI analysis results and parsing of frequently requested URLs.

## Processing Workflow

URL Validation → check availability and content type
Content Extraction → article parsing (Beautiful Soup + Readability)
AI Analysis → parallel requests to Claude/ChatGPT for summaries in both languages
Tagging → automatic tag suggestions + manual addition capability
.md File Creation → template-based with metadata
Git Operations → commit and PR creation (optional)
Obsidian Sync → vault updates via API

## Key Features

Fallback Strategy: If one AI service is unavailable, automatically switches to another.
Interactivity: Inline buttons for tag confirmation, summary editing, action selection.
Configurability: Settings via .env file (API keys, repository paths, templates).
Monitoring: Logging of all operations, performance metrics.

## Technology Stack

aiogram 3.x for Telegram Bot API
aiohttp for asynchronous HTTP requests
Beautiful Soup 4 + newspaper3k for parsing
SQLAlchemy with async support
Celery + Redis for background tasks
GitPython for Git operations
Pydantic for data validation
