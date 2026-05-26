import json
import boto3
import requests
import os
from datetime import datetime, timezone

S3_BUCKET = os.environ.get("S3_BUCKET", "miami-worldcup-pipeline-juan")
REGION = os.environ.get("AWS_REGION", "us-east-2")

# Official API-Football Credentials & IDs
API_KEY = os.environ.get("API_FOOTBALL_KEY")
API_HOST = "v3.football.api-sports.io"
LEAGUE_ID = 1      # Static ID for FIFA World Cup
SEASON_YEAR = 2022 # Target tournament year


def fetch_from_api(endpoint: str) -> dict:
    """Helper to fetch data securely from the official API-Football endpoints"""
    url = f"https://{API_HOST}/{endpoint}?league={LEAGUE_ID}&season={SEASON_YEAR}"
    headers = {
        "x-rapidapi-key": API_KEY,
        "x-rapidapi-host": API_HOST
    }
    response = requests.get(url, headers=headers, timeout=15)
    response.raise_for_status()
    return response.json().get("response", [])


def clean_and_transform(raw_standings, raw_fixtures):
    """Cleans raw API payloads into an optimized layout for our Bento Grid"""
    cleaned_matches = []
    
    for item in raw_fixtures:
        fixture = item.get("fixture", {})
        teams = item.get("teams", {})
        goals = item.get("goals", {})
        venue_name = fixture.get("venue", {}).get("name", "") or ""
        
        cleaned_matches.append({
            "id": fixture.get("id"),
            "date": fixture.get("date"),
            "status": fixture.get("status", {}).get("short"),
            "elapsed": fixture.get("status", {}).get("elapsed"),
            "venue": venue_name,
            "is_hard_rock_stadium": "Hard Rock Stadium" in venue_name or "Miami" in venue_name,
            "home_team": {
                "name": teams.get("home", {}).get("name"),
                "logo": teams.get("home", {}).get("logo")
            },
            "away_team": {
                "name": teams.get("away", {}).get("name"),
                "logo": teams.get("away", {}).get("logo")
            },
            "score": {
                "home": goals.get("home"),
                "away": goals.get("away")
            }
        })

    # Flatten group tables into standard JSON arrays
    cleaned_standings = {}
    for league_data in raw_standings:
        for group in league_data.get("league", {}).get("standings", []):
            for row in group:
                group_name = row.get("group", "Unknown Group")
                if group_name not in cleaned_standings:
                    cleaned_standings[group_name] = []
                
                cleaned_standings[group_name].append({
                    "rank": row.get("rank"),
                    "team_name": row.get("team", {}).get("name"),
                    "team_logo": row.get("team", {}).get("logo"),
                    "points": row.get("points"),
                    "goals_diff": row.get("goalsDiff"),
                    "played": row.get("all", {}).get("played"),
                    "win": row.get("all", {}).get("win"),
                    "draw": row.get("all", {}).get("draw"),
                    "lose": row.get("all", {}).get("lose")
                })
                
    return {
        "standings": cleaned_standings,
        "matches": cleaned_matches
    }


def save_to_s3(data: dict):
    s3 = boto3.client("s3", region_name=REGION)
    now = datetime.now(timezone.utc)
    payload_string = json.dumps(data, indent=2)
    
    # Path A: Historical log tracking for Recharts
    history_key = f"worldcup/history/{now.strftime('%Y/%m/%d/%H-%M-%S')}.json"
    s3.put_object(Bucket=S3_BUCKET, Key=history_key, Body=payload_string, ContentType="application/json")
    
    # Path B: Static Quick-Access Shortcut for frontend fetches
    latest_key = "worldcup/latest.json"
    s3.put_object(Bucket=S3_BUCKET, Key=latest_key, Body=payload_string, ContentType="application/json")
    
    return latest_key


def handler(event, context):
    try:
        if not API_KEY:
            raise ValueError("API_FOOTBALL_KEY environment variable is missing!")
            
        now = datetime.now(timezone.utc).isoformat()
        
        raw_standings = fetch_from_api("standings")
        raw_fixtures = fetch_from_api("fixtures")
        
        core_data = clean_and_transform(raw_standings, raw_fixtures)
        
        payload = {
            "fetched_at": now,
            "standings": core_data["standings"],
            "matches": core_data["matches"]
        }
        
        s3_key = save_to_s3(payload)
        print(f"[worldcup-lambda] Saved successfully to S3.")
        
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
            "body": json.dumps({"message": "World Cup system refreshed", "fetched_at": now})
        }
    except Exception as e:
        print(f"[worldcup-lambda] CRITICAL ERROR: {e}")
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
            "body": json.dumps({"error": str(e)})
        }
