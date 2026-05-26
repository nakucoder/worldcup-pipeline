# World Cup Pipeline

An automated data pipeline that fetches live FIFA World Cup 2026 match results and group standings and stores them in AWS S3 — built with FastAPI, Docker, and Python.

## What it does

- Fetches live match results and group standings from API-Football
- Cleans and transforms raw API data into an optimized JSON format
- Saves data to AWS S3 every 60 minutes automatically
- Stores both a latest snapshot and a full historical log
- S3 path structure: `worldcup/history/YYYY/MM/DD/HH-MM-SS.json`
- Static shortcut for frontend: `worldcup/latest.json`
- Exposes a REST API to trigger the pipeline manually

## Tech Stack

- **FastAPI** — REST API framework
- **Docker** — containerized for local development
- **AWS Lambda** — serverless execution in production
- **AWS S3** — cloud storage for all pipeline data
- **EventBridge** — triggers Lambda every 60 minutes
- **API-Football** — official football data provider
- **GitHub Actions** — CI/CD auto-deploy on every push to main

## API Endpoints

| Endpoint | Description |
|---|---|
| `GET /` | Check if pipeline is running |
| `GET /health` | Health check for monitoring |
| `GET /run` | Trigger pipeline manually and save to S3 |

## Data Structure

Each S3 snapshot contains:

```json
{
  "fetched_at": "2026-06-11T18:00:00+00:00",
  "standings": {
    "Group A": [
      {
        "rank": 1,
        "team_name": "Brazil",
        "team_logo": "https://...",
        "points": 9,
        "goals_diff": 5,
        "played": 3,
        "win": 3,
        "draw": 0,
        "lose": 0
      }
    ]
  },
  "matches": [
    {
      "id": 123,
      "date": "2026-06-11T18:00:00+00:00",
      "status": "FT",
      "home_team": {"name": "Brazil", "logo": "https://..."},
      "away_team": {"name": "Argentina", "logo": "https://..."},
      "score": {"home": 2, "away": 1},
      "venue": "Hard Rock Stadium",
      "is_hard_rock_stadium": true
    }
  ]
}
```

## How to run locally

1. Clone the repo
2. Copy `.env.example` to `.env` and fill in your credentials
3. Run: `docker-compose up -d`
4. Test: `curl http://localhost:8003/health`
5. Trigger pipeline: `curl http://localhost:8003/run`

## Deploy to Lambda

```bash
python3 make_zip.py
bash deploy.sh
```

Or just push to `main` — GitHub Actions deploys automatically.

## Related Repositories

- [weather-pipeline](https://github.com/nakucoder/weather-pipeline)
- [crypto-pipeline](https://github.com/nakucoder/crypto-pipeline)
- [stock-pipeline](https://github.com/nakucoder/stock-pipeline)
- [miami-dashboard](https://github.com/nakucoder/miami-dashboard)

## Author

Juan Spinelli — [GitHub](https://github.com/nakucoder) | [LinkedIn](https://linkedin.com/in/juan-spinelli)
