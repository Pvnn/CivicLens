# Social Media Youth Opinion Scraper

This system provides live scraping from social media platforms to understand youth opinions and analyze sentiment trends.

## Features

- **Multi-Platform Scraping**: Reddit, Twitter/X, YouTube, and general web sources
- **Sentiment Analysis**: Advanced sentiment analysis using VADER and TextBlob
- **Real-time Data**: Live scraping with intelligent fallback mechanisms
- **Youth-Focused**: Specifically targets youth-relevant content and keywords
- **Interactive Dashboard**: Beautiful React frontend with real-time updates

## Setup Instructions

### 1. Install Dependencies

```bash
# Backend dependencies
cd Civicens/backend
pip install -r requirements.txt

# Frontend dependencies
cd ../frontend
npm install
```

### 2. Configure API Keys

Create a `.env` file in the backend directory with your API credentials:

```bash
# Reddit API (https://www.reddit.com/prefs/apps)
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret
REDDIT_USER_AGENT=YouthOpinionScraper/1.0

# Twitter API (https://developer.twitter.com/)
TWITTER_BEARER_TOKEN=your_twitter_bearer_token
TWITTER_CONSUMER_KEY=your_twitter_consumer_key
TWITTER_CONSUMER_SECRET=your_twitter_consumer_secret
TWITTER_ACCESS_TOKEN=your_twitter_access_token
TWITTER_ACCESS_SECRET=your_twitter_access_secret

# YouTube API (https://console.developers.google.com/)
YOUTUBE_API_KEY=your_youtube_api_key
```

### 3. Get API Credentials

#### Reddit API
1. Go to https://www.reddit.com/prefs/apps
2. Click "Create App" or "Create Another App"
3. Choose "script" as the app type
4. Note down the client ID and secret

#### Twitter API
1. Go to https://developer.twitter.com/
2. Create a new project/app
3. Generate API keys and bearer token
4. Note down all credentials

#### YouTube API
1. Go to https://console.developers.google.com/
2. Create a new project
3. Enable YouTube Data API v3
4. Create credentials (API key)
5. Note down the API key

### 4. Run the Application

```bash
# Start the backend
cd Civicens/backend
python run.py

# Start the frontend (in a new terminal)
cd Civicens/frontend
npm run dev
```

### 5. Access the Dashboard

- Frontend: http://localhost:5173
- Backend API: http://localhost:5000

## API Endpoints

### Social Media Endpoints

- `GET /api/youth-opinions` - Get live youth opinions from social media
- `GET /api/youth-sentiment` - Get sentiment analysis of youth opinions
- `GET /api/youth-topics` - Get trending topics among youth
- `GET /api/social-media-status` - Check status of social media APIs

### Existing Endpoints

- `GET /api/missing-topics` - Get gap analysis between youth and political priorities
- `GET /api/health` - Health check endpoint
- `GET /api/scraping-status` - Check scraping status

## Features Overview

### 1. Live Opinions Tab
- Real-time posts from Reddit, Twitter, YouTube
- Sentiment analysis for each post
- Youth-relevant keyword extraction
- Interactive post details

### 2. Sentiment Analysis Tab
- Overall sentiment distribution (positive/negative/neutral)
- Platform activity breakdown
- Top youth concerns
- Confidence scores

### 3. Trending Topics Tab
- Most discussed topics among youth
- Gap analysis between youth and political focus
- Frequency analysis
- Relevance scoring

## Data Sources

### Reddit Subreddits
- r/india, r/IndianTeenagers, r/IndianStudents
- r/developersIndia, r/IndianAcademia
- r/IndianStreetBets, r/IndianGaming
- City-specific subreddits (Mumbai, Delhi, Bangalore, etc.)

### Twitter Hashtags
- #IndianYouth, #StudentLife, #IndianStudents
- #YouthVoice, #IndianTeenagers, #CampusLife
- #IndianEducation, #YouthPolitics
- #IndianStartups, #TechIndia, #ClimateAction

### YouTube
- Searches for youth-relevant content
- Comments from popular videos
- Educational and political content

### Web Sources
- General web scraping from youth-focused sites
- RSS feeds and accessible APIs

## Youth Keywords

The system identifies youth-relevant content using keywords like:
- Education: student, college, university, school, education
- Career: job, career, future, dream, aspiration, startup, entrepreneur
- Technology: technology, social media, digital, online, mobile, app, coding
- Social Issues: mental health, climate, environment, politics, government
- Innovation: innovation, AI, artificial intelligence, sustainability

## Sentiment Analysis

Uses a hybrid approach combining:
- **VADER Sentiment**: Fast and effective for social media text
- **TextBlob**: Additional polarity and subjectivity analysis
- **Confidence Scoring**: Measures reliability of sentiment analysis

## Error Handling

- Graceful fallback when APIs are unavailable
- Rate limiting to respect platform policies
- Comprehensive error logging
- User-friendly error messages

## Rate Limiting

The system implements respectful rate limiting:
- Reddit: 1 second between requests
- Twitter: 1 second between requests
- YouTube: 1 second between requests
- Web sources: 2 seconds between requests

## Privacy and Ethics

- Only scrapes publicly available content
- Respects platform terms of service
- No personal data storage
- Anonymized analysis results
- Rate limiting to prevent abuse

## Troubleshooting

### Common Issues

1. **API Key Errors**: Ensure all API keys are correctly set in `.env`
2. **Rate Limiting**: Wait a few minutes if you hit rate limits
3. **Network Issues**: Check internet connection and firewall settings
4. **Empty Results**: Some APIs may have limited free tier access

### Debug Mode

Enable debug logging by setting `FLASK_DEBUG=True` in your environment.

### Fallback Mode

If social media APIs are unavailable, the system will:
- Use curated fallback data
- Show appropriate error messages
- Continue functioning with limited data

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is for educational and research purposes. Please respect the terms of service of all platforms being scraped.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review API documentation for each platform
3. Check the logs for detailed error messages
4. Ensure all dependencies are properly installed
