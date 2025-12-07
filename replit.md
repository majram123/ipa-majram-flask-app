# Overview

This is a Telegram bot built with Pyrogram that downloads media content from multiple social media platforms including Instagram, TikTok, YouTube, Pinterest, Snapchat, and SoundCloud. The bot provides users with an interface to download videos and audio from these platforms by sending URLs through Telegram messages.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Bot Framework
- **Technology**: Pyrogram (Telegram Bot API wrapper)
- **Rationale**: Provides async/await support and easy integration with Telegram's MTProto API
- **Key Features**:
  - Plugin-based handler system (handlers loaded from `Bot/handlers/` directory)
  - 20 concurrent workers for handling multiple requests
  - In-memory session disabled for persistent session storage
  - Built-in flood wait handling for rate limiting

## Download Engine
- **Technology**: yt-dlp (for YouTube, Pinterest, Snapchat, SoundCloud)
- **Rationale**: Universal media downloader supporting multiple platforms with automatic quality selection
- **Alternatives**: Platform-specific APIs (chosen for broader platform support)

## Instagram Integration
- **Technology**: instagrapi library
- **Session Management**: Persistent session storage in JSON files to avoid frequent re-authentication
- **Session Refresh**: 30-minute interval (1800 seconds) to maintain active sessions
- **Retry Logic**: Maximum 3 login attempts with exponential backoff
- **Challenges**: Handles LoginRequired and ChallengeRequired exceptions

## TikTok Integration
- **API**: Custom API endpoint (tikmate.app)
- **Quality Options**: Supports HD and standard quality downloads
- **Token-based**: Uses temporary tokens for media access

## Data Storage
- **Type**: File-based JSON storage
- **Location**: `Bot/database/` directory
- **Collections**:
  - `users.json`: Registered user IDs
  - `admins.json`: Administrator user IDs
  - `banned.json`: Banned user IDs
  - `channels.json`: Required channel subscriptions
  - `instagram_cookies.json`: Instagram authentication credentials
  - `instagram_session.json`: Instagram session data (device info, tokens, cookies)
  - `others.json`: Bot configuration options (forward settings, new member notifications)

**Rationale**: Simple JSON files chosen for lightweight deployment without database dependencies. Suitable for moderate user bases.

**Pros**: 
- Zero infrastructure setup
- Easy to inspect and modify
- No database server required

**Cons**: 
- Limited scalability
- No concurrent write protection
- Performance degrades with large datasets

## User Management
- **Subscription System**: Optional channel membership verification before bot usage
- **Ban System**: Prevents banned users from accessing bot features
- **Admin Notifications**: Alerts admins when new users join (configurable)
- **User Tracking**: Maintains list of all users who have interacted with the bot

## Async Architecture
- **HTTP Client**: aiohttp for non-blocking API requests
- **File I/O**: aiofiles for async file operations
- **Download Handling**: Executor-based thread pool for blocking yt-dlp operations
- **Rationale**: Prevents blocking the event loop during long-running download operations

## Error Handling
- **FloodWait**: Automatic retry with exponential backoff
- **Session Errors**: Clear and re-authenticate for Instagram
- **Download Failures**: User-friendly error messages in Arabic
- **File Cleanup**: Temporary downloaded files removed after sending

## Message Flow
1. User sends /start command
2. Bot checks subscription status and ban list
3. User selects platform via callback query
4. Bot prompts for URL using pyromod's ask() feature
5. URL validated and media extracted
6. File downloaded to local storage
7. File uploaded to Telegram
8. Local file deleted

# External Dependencies

## Telegram API
- **API ID & Hash**: Required for MTProto authentication
- **Bot Token**: Telegram bot authentication token
- **Purpose**: Core messaging and file transfer functionality

## Social Media APIs
- **TikTok**: tikmate.app API for video extraction
- **Instagram**: Direct instagrapi integration with Instagram's private API
- **YouTube**: yt-dlp's built-in YouTube extractor
- **Pinterest**: yt-dlp's Pinterest support
- **Snapchat**: yt-dlp's Snapchat support
- **SoundCloud**: yt-dlp's SoundCloud support

## Python Libraries
- **pyrogram**: Telegram bot framework with MTProto support
- **tgcrypto**: Cryptographic acceleration for Pyrogram
- **pyromod**: Extends Pyrogram with conversation features (ask/listen)
- **instagrapi**: Instagram private API client
- **yt-dlp**: Universal media downloader
- **aiohttp**: Async HTTP client for API requests
- **aiofiles**: Async file I/O operations
- **beautifulsoup4**: HTML parsing (dependency for scrapers)
- **validators**: URL validation

## Environment Variables
- `TELEGRAM_API_ID`: Telegram API ID from my.telegram.org
- `TELEGRAM_API_HASH`: Telegram API hash
- `TELEGRAM_BOT_TOKEN`: Bot token from @BotFather

## File System
- Local storage for temporary media downloads
- Session persistence files in `Bot/database/`
- Automatic cleanup after successful uploads