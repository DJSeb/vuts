# VUTS Web UI Module

A web-based user interface for viewing sentiment analysis reports, browsing article history, and managing system configurations.

## Features

- **Reports Dashboard**: Overview of sentiment analysis across all monitored topics
- **Topics View**: Detailed sentiment scores and article analysis organized by topic (accessible at `/reports/topics`)
- **Topic Detail**: Deep dive into individual topic analysis with full article content
- **Configuration Page**: View and manage system settings, data sources, and workflow commands
- **REST API**: JSON endpoints for programmatic access to sentiment data

## Quick Start

### 1. Install Dependencies

```bash
cd scratch
pip install -r requirements.txt
```

### 2. Generate Sample Data (Optional)

```bash
cd scratch
python demos/demo_workflow.py
```

This creates sample sentiment analysis data without requiring API keys.

### 3. Start the Web Server

```bash
cd scratch
python src/ui/app.py
```

The server will start at `http://127.0.0.1:5000`

### 4. Access the UI

Open your browser and navigate to:
- Main page: http://127.0.0.1:5000/
- Reports: http://127.0.0.1:5000/reports
- Topics: http://127.0.0.1:5000/reports/topics
- Config: http://127.0.0.1:5000/config

## Command Line Options

```bash
python src/ui/app.py [OPTIONS]

Options:
  --host HOST          Host to bind to (default: 127.0.0.1)
  --port PORT          Port to bind to (default: 5000)
  --debug              Run in debug mode with auto-reload
  --data-dir PATH      Custom data directory path
```

### Examples

```bash
# Run on custom port
python src/ui/app.py --port 8080

# Run with debug mode (auto-reloads on code changes)
python src/ui/app.py --debug

# Use custom data directory
python src/ui/app.py --data-dir /path/to/data

# Allow external connections
python src/ui/app.py --host 0.0.0.0 --port 5000
```

## Data Directory

The UI automatically looks for sentiment analysis data in:
1. `VUTS_DATA_DIR` environment variable (if set)
2. `scratch/output/` (default location)
3. `scratch/demo_output/` (fallback for demo data)

The data directory should contain:
```
data_dir/
├── llm_scores/          # Sentiment scores by topic
│   ├── TSLA/
│   │   ├── 001_article_score.json
│   │   └── 002_article_score.json
│   └── MSFT/
│       └── 001_article_score.json
├── demo_source/         # Original articles (optional)
│   └── TSLA/
│       └── 001_article.json
└── market_data/         # Market data context (optional)
    └── TSLA_market_data.json
```

## API Endpoints

The UI provides REST API endpoints for programmatic access:

### Get All Topics Summary
```bash
GET /api/topics
```

Returns summary statistics for all topics:
```json
{
  "TSLA": {
    "count": 10,
    "avg_score": 2.35,
    "latest_score": 6.75,
    "sentiment": "positive"
  }
}
```

### Get Topic Details
```bash
GET /api/topics/<topic>
```

Returns detailed scores for a specific topic:
```json
{
  "topic": "TSLA",
  "scores": [...],
  "summary": {
    "count": 10,
    "avg_score": 2.35,
    "latest_score": 6.75,
    "sentiment": "positive"
  }
}
```

## Routes

- `/` - Home page (redirects to reports)
- `/reports` - Reports overview dashboard
- `/reports/topics` - Detailed topics view with all articles
- `/reports/topics/<topic>` - Individual topic detail page
- `/config` - Configuration and management page
- `/api/topics` - JSON API for all topics
- `/api/topics/<topic>` - JSON API for specific topic

## Technology Stack

- **Backend**: Flask (Python web framework)
- **Frontend**: HTML5, CSS3 (no JavaScript dependencies)
- **Styling**: Custom CSS with responsive design
- **Data Format**: JSON

## Configuration

The configuration page displays settings from:
- `scratch/example_data/copilot-gpt5-cfg.json` (example config)
- `scratch/config.json` (custom config if exists)

Configuration includes:
- Topics to monitor (stock symbols)
- News sources (googlenews_rss, bingnews, finnhub)
- Article fetching parameters
- Content extraction settings

## Production Deployment

For production use, deploy with a WSGI server like Gunicorn:

```bash
pip install gunicorn
cd scratch
gunicorn -w 4 -b 0.0.0.0:8000 src.ui.app:app
```

Or use Docker (create a Dockerfile):
```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "src.ui.app:app"]
```

## Security Notes

- The default secret key is for development only
- Set `SECRET_KEY` environment variable in production
- The development server should not be used in production
- Use a production WSGI server (Gunicorn, uWSGI) for deployment

## Troubleshooting

### No Data Available
If you see "No Reports Available":
1. Run `python demos/demo_workflow.py` to create sample data
2. Or run the full workflow to analyze real articles
3. Check the data directory path in the footer

### Port Already in Use
If port 5000 is busy:
```bash
python src/ui/app.py --port 8080
```

### Module Import Errors
Ensure you're in the `scratch` directory and have installed dependencies:
```bash
cd scratch
pip install -r requirements.txt
```

## Screenshots

See the PR for screenshots of:
- Reports overview page
- Topics detail page
- Configuration management page

## Future Enhancements

Potential improvements for future versions:
- User authentication and authorization
- Real-time updates via WebSockets
- Interactive charts and visualizations
- Export reports to PDF/CSV
- Custom date range filtering
- Search functionality
- Email notifications setup
- Watchlist management
