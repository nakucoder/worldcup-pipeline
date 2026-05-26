from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import sys
import os

# Append root directory so we can import lambda_function cleanly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import lambda_function

app = FastAPI(title="Miami World Cup Data Pipeline — Local Dev")

# Enable CORS exactly like the dashboard infrastructure expects
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"status": "World Cup Pipeline Dev Server Running"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.get("/run")
def run_pipeline():
    """Manually triggers the lambda function handler locally to test API and S3 uploads"""
    result = lambda_function.handler(event={}, context=None)
    if result["statusCode"] != 200:
        raise HTTPException(status_code=result["statusCode"], detail=result["body"])
    return {"message": "Pipeline run executed successfully", "log": result["body"]}
