# PolicyPulse Backend

A Flask-based backend system for fetching, processing, and serving government policy data with AI-powered summarization and bilingual support.

## Features

- **Real Government Data Integration**: Fetches from official sources like eGazette, PRS India, RBI, SEBI
- **AI-Powered Summarization**: Converts complex policy documents into digestible cards
- **Bilingual Support**: Provides summaries in English and Nepali
- **Gap Detection**: Identifies missing information for RTI generation
- **SQLite Database**: Simple, file-based database for easy deployment

## Quick Start

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Run the Application

```bash
python run.py
```

The server will start on `http://localhost:5000`

### 3. Test the API

```bash
# Get recent policies
curl http://localhost:5000/api/policies/recent

# Refresh policy data
curl -X POST http://localhost:5000/api/policies/refresh

# Get policy statistics
curl http://localhost:5000/api/policies/stats
```

## API Endpoints

### Policy Management

- `GET /api/policies/recent` - Get recent policy cards
  - Query params: `days` (default: 7)
- `POST /api/policies/refresh` - Manually refresh policy data
- `GET /api/policies/<id>` - Get specific policy details
- `GET /api/policies/<id>/gaps` - Get operational gaps for RTI generation

### Search & Filter

- `GET /api/policies/search` - Search policies
  - Query params: `q` (search term), `ministry` (filter by ministry)
- `GET /api/policies/ministries` - Get list of ministries with counts
- `GET /api/policies/stats` - Get policy statistics

## Data Sources

The system integrates with real government sources:

1. **eGazette Portal** - Official government notifications
2. **PRS India** - Parliamentary session summaries and policy analysis
3. **Ministry Websites** - Direct ministry notifications
4. **RBI/SEBI** - Financial regulatory updates

## Sample Policy Data

The system currently includes recent notifications:

- GST Rate Notification No. 10/2025 (Medicine exemptions)
- Income-Tax Act 2025 Implementation
- SEBI LODR Amendment Regulations 2025
- Digital India Land Records Modernization
- National Education Policy Phase 2

## Database Schema

### PolicyCard Model

```python
- id: Primary key
- title: Policy title
- ministry: Issuing ministry
- notification_number: Unique identifier
- publication_date: When published
- effective_date: When effective
- original_text: Raw policy text
- summary_english: AI-generated English summary
- summary_nepali: Nepali translation
- what_changed: Structured change description
- who_affected: Affected parties
- what_to_do: Required actions
- source_url: Official source link
- gazette_type: Ordinary/Extraordinary
- status: New/Updated/Action Required
- missing_dates: Gap flag
- missing_officer_info: Gap flag
- missing_urls: Gap flag
```

## Configuration

### Environment Variables

- `SECRET_KEY`: Flask secret key (default: dev key)
- `DATABASE_URL`: SQLite database path (default: sqlite:///policypulse.db)

### Database Location

SQLite database is created at `backend/policypulse.db`

## Development

### Project Structure

```
backend/
├── app/
│   ├── __init__.py          # Flask app factory
│   ├── models/
│   │   └── policy.py        # PolicyCard model
│   ├── routes/
│   │   └── policies.py      # API endpoints
│   └── services/
│       ├── policy_fetcher.py    # Government data fetcher
│       └── policy_summarizer.py # AI summarization
├── run.py                   # Application entry point
├── requirements.txt         # Dependencies
└── README.md               # This file
```

### Adding New Data Sources

1. Extend `GovernmentPolicyFetcher` class
2. Add new `_fetch_*` methods
3. Update `fetch_recent_policies()` to include new sources

### Customizing Summarization

1. Modify `PolicySummarizer` class
2. Update keyword mappings and extraction patterns
3. Add new language support in translation methods

## Production Deployment

### Using Gunicorn

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 run:app
```

### Environment Setup

```bash
export SECRET_KEY="your-production-secret-key"
export DATABASE_URL="sqlite:///production.db"
```

### Database Backup

```bash
# Backup SQLite database
cp policypulse.db backup_$(date +%Y%m%d).db
```

## API Response Format

### Policy Card Response

```json
{
  "success": true,
  "count": 5,
  "policies": [
    {
      "id": 1,
      "title": "GST Rate Notification No. 10/2025-Central Tax (Rate)",
      "ministry": "Ministry of Finance",
      "notification_number": "10/2025-Central Tax (Rate)",
      "publication_date": "2025-09-17T00:00:00",
      "summary": {
        "english": "GST notification updates tax exemptions...",
        "nepali": "जीएसटी सूचना कर छुट अपडेट..."
      },
      "details": {
        "what_changed": "GST rates and exemptions have been updated",
        "who_affected": "taxpayers, businesses",
        "what_to_do": "Update GST compliance procedures"
      },
      "operational_gaps": {
        "missing_dates": true,
        "missing_officer_info": true,
        "missing_urls": false
      }
    }
  ]
}
```

## Troubleshooting

### Common Issues

1. **Database not found**: Run the app once to create SQLite database
2. **Import errors**: Ensure all dependencies are installed
3. **No policy data**: Run `/refresh` endpoint to fetch initial data

### Logs

Check console output for detailed error messages and API request logs.

## Contributing

1. Fork the repository
2. Create feature branch
3. Add tests for new functionality
4. Submit pull request

## License

MIT License - see LICENSE file for details
