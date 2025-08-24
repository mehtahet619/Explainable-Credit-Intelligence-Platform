from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
import os
from datetime import datetime, timedelta

from database import get_db
from models import CreditScore, Company, FeatureImportance, NewsEvent
from schemas import (
    CreditScoreResponse, 
    CompanyResponse, 
    ExplanationResponse,
    DashboardData
)

app = FastAPI(
    title="CredTech API",
    description="Explainable Credit Intelligence Platform API",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://frontend:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "CredTech API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}

@app.get("/companies", response_model=List[CompanyResponse])
async def get_companies(db: Session = Depends(get_db)):
    """Get all companies in the system"""
    companies = db.query(Company).all()
    return companies

@app.get("/companies/{company_id}/score", response_model=CreditScoreResponse)
async def get_latest_score(company_id: int, db: Session = Depends(get_db)):
    """Get the latest credit score for a company"""
    score = db.query(CreditScore).filter(
        CreditScore.company_id == company_id
    ).order_by(CreditScore.time.desc()).first()
    
    if not score:
        raise HTTPException(status_code=404, detail="Score not found")
    
    return score

@app.get("/companies/{company_id}/scores", response_model=List[CreditScoreResponse])
async def get_score_history(
    company_id: int, 
    days: int = 30,
    db: Session = Depends(get_db)
):
    """Get credit score history for a company"""
    start_date = datetime.utcnow() - timedelta(days=days)
    
    scores = db.query(CreditScore).filter(
        CreditScore.company_id == company_id,
        CreditScore.time >= start_date
    ).order_by(CreditScore.time.desc()).all()
    
    return scores

@app.get("/companies/{company_id}/explanation", response_model=ExplanationResponse)
async def get_score_explanation(company_id: int, db: Session = Depends(get_db)):
    """Get explanation for the latest credit score"""
    # Get latest score
    latest_score = db.query(CreditScore).filter(
        CreditScore.company_id == company_id
    ).order_by(CreditScore.time.desc()).first()
    
    if not latest_score:
        raise HTTPException(status_code=404, detail="Score not found")
    
    # Get feature importance
    features = db.query(FeatureImportance).filter(
        FeatureImportance.company_id == company_id,
        FeatureImportance.timestamp >= latest_score.time - timedelta(minutes=5)
    ).all()
    
    # Get recent news events
    recent_events = db.query(NewsEvent).filter(
        NewsEvent.company_id == company_id,
        NewsEvent.timestamp >= datetime.utcnow() - timedelta(days=7)
    ).order_by(NewsEvent.timestamp.desc()).limit(5).all()
    
    return ExplanationResponse(
        score=latest_score.score,
        confidence=latest_score.confidence,
        timestamp=latest_score.time,
        feature_contributions=[
            {
                "feature": f.feature_name,
                "importance": f.importance_value,
                "shap_value": f.shap_value,
                "current_value": f.feature_value
            } for f in features
        ],
        recent_events=[
            {
                "timestamp": e.timestamp,
                "headline": e.headline,
                "sentiment": e.sentiment_score,
                "impact": e.impact_score,
                "event_type": e.event_type
            } for e in recent_events
        ],
        summary=f"Credit score of {latest_score.score} with {latest_score.confidence}% confidence"
    )

@app.get("/dashboard", response_model=DashboardData)
async def get_dashboard_data(db: Session = Depends(get_db)):
    """Get aggregated data for the dashboard"""
    # Get all companies with their latest scores
    companies_data = []
    companies = db.query(Company).all()
    
    for company in companies:
        latest_score = db.query(CreditScore).filter(
            CreditScore.company_id == company.id
        ).order_by(CreditScore.time.desc()).first()
        
        if latest_score:
            companies_data.append({
                "id": company.id,
                "symbol": company.symbol,
                "name": company.name,
                "sector": company.sector,
                "current_score": latest_score.score,
                "confidence": latest_score.confidence,
                "last_updated": latest_score.time
            })
    
    # Get recent alerts (significant score changes)
    alerts = []
    for company in companies:
        recent_scores = db.query(CreditScore).filter(
            CreditScore.company_id == company.id,
            CreditScore.time >= datetime.utcnow() - timedelta(hours=24)
        ).order_by(CreditScore.time.desc()).limit(2).all()
        
        if len(recent_scores) >= 2:
            score_change = recent_scores[0].score - recent_scores[1].score
            if abs(score_change) > 5:  # Alert for changes > 5 points
                alerts.append({
                    "company_symbol": company.symbol,
                    "company_name": company.name,
                    "score_change": score_change,
                    "timestamp": recent_scores[0].time,
                    "severity": "high" if abs(score_change) > 10 else "medium"
                })
    
    return DashboardData(
        companies=companies_data,
        alerts=alerts,
        total_companies=len(companies),
        last_updated=datetime.utcnow()
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)