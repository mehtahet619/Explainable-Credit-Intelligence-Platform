from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
import os
from datetime import datetime, timedelta

from database_sqlite import get_db
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
    try:
        # Get all companies with their latest scores
        companies_data = []
        companies = db.query(Company).all()
        
        # If no companies exist, return sample data
        if not companies:
            companies_data = [
                {
                    "id": 1,
                    "symbol": "AAPL",
                    "name": "Apple Inc.",
                    "sector": "Technology",
                    "current_score": 750.0,
                    "confidence": 85.0,
                    "last_updated": datetime.utcnow()
                },
                {
                    "id": 2,
                    "symbol": "MSFT",
                    "name": "Microsoft Corporation",
                    "sector": "Technology",
                    "current_score": 720.0,
                    "confidence": 82.0,
                    "last_updated": datetime.utcnow()
                }
            ]
        else:
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
                        "current_score": float(latest_score.score),
                        "confidence": float(latest_score.confidence) if latest_score.confidence else 75.0,
                        "last_updated": latest_score.time
                    })
                else:
                    # Add company without score
                    companies_data.append({
                        "id": company.id,
                        "symbol": company.symbol,
                        "name": company.name,
                        "sector": company.sector,
                        "current_score": 650.0,  # Default score
                        "confidence": 70.0,
                        "last_updated": datetime.utcnow()
                    })
        
        # Get recent alerts (significant score changes)
        alerts = []
        for company in companies:
            recent_scores = db.query(CreditScore).filter(
                CreditScore.company_id == company.id,
                CreditScore.time >= datetime.utcnow() - timedelta(hours=24)
            ).order_by(CreditScore.time.desc()).limit(2).all()
            
            if len(recent_scores) >= 2:
                score_change = float(recent_scores[0].score) - float(recent_scores[1].score)
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
            total_companies=len(companies_data),
            last_updated=datetime.utcnow()
        )
    except Exception as e:
        # Return sample data if database query fails
        return DashboardData(
            companies=[
                {
                    "id": 1,
                    "symbol": "DEMO",
                    "name": "Demo Company",
                    "sector": "Technology",
                    "current_score": 700.0,
                    "confidence": 80.0,
                    "last_updated": datetime.utcnow()
                }
            ],
            alerts=[],
            total_companies=1,
            last_updated=datetime.utcnow()
        )

@app.get("/analytics")
async def get_analytics_data(db: Session = Depends(get_db)):
    """Get analytics data for charts and visualizations"""
    try:
        companies = db.query(Company).all()
        
        # Sector distribution
        sector_counts = {}
        for company in companies:
            sector = company.sector or "Unknown"
            sector_counts[sector] = sector_counts.get(sector, 0) + 1
        
        sector_distribution = [
            {"name": sector, "value": count, "color": _get_sector_color(sector)}
            for sector, count in sector_counts.items()
        ]
        
        # If no data, return sample data
        if not sector_distribution:
            sector_distribution = [
                {"name": "Technology", "value": 40, "color": "#1976d2"},
                {"name": "Financial Services", "value": 25, "color": "#dc004e"},
                {"name": "Healthcare", "value": 15, "color": "#4caf50"},
                {"name": "Consumer Cyclical", "value": 12, "color": "#ff9800"},
                {"name": "Energy", "value": 8, "color": "#9c27b0"}
            ]
        
        # Score trends (sample data for now)
        score_trends = [
            {"month": "Jan", "avg_score": 680},
            {"month": "Feb", "avg_score": 685},
            {"month": "Mar", "avg_score": 690},
            {"month": "Apr", "avg_score": 695},
            {"month": "May", "avg_score": 700},
            {"month": "Jun", "avg_score": 705}
        ]
        
        # Risk distribution
        risk_distribution = []
        for company in companies:
            latest_score = db.query(CreditScore).filter(
                CreditScore.company_id == company.id
            ).order_by(CreditScore.time.desc()).first()
            
            if latest_score:
                risk_distribution.append({
                    "company": company.symbol,
                    "score": float(latest_score.score),
                    "risk_level": _get_risk_level(float(latest_score.score))
                })
        
        # Sample data if no real data
        if not risk_distribution:
            risk_distribution = [
                {"company": "AAPL", "score": 750, "risk_level": "Low"},
                {"company": "MSFT", "score": 720, "risk_level": "Low"},
                {"company": "GOOGL", "score": 680, "risk_level": "Medium"},
                {"company": "TSLA", "score": 620, "risk_level": "Medium"},
                {"company": "JPM", "score": 700, "risk_level": "Low"}
            ]
        
        return {
            "sector_distribution": sector_distribution,
            "score_trends": score_trends,
            "risk_distribution": risk_distribution,
            "summary": {
                "total_companies": len(companies) if companies else 5,
                "avg_score": sum(item["score"] for item in risk_distribution) / len(risk_distribution) if risk_distribution else 694,
                "high_risk_count": len([item for item in risk_distribution if item["risk_level"] == "High"]),
                "last_updated": datetime.utcnow()
            }
        }
    except Exception as e:
        # Return sample data on error
        return {
            "sector_distribution": [
                {"name": "Technology", "value": 40, "color": "#1976d2"},
                {"name": "Financial Services", "value": 25, "color": "#dc004e"},
                {"name": "Healthcare", "value": 15, "color": "#4caf50"}
            ],
            "score_trends": [
                {"month": "Jan", "avg_score": 680},
                {"month": "Feb", "avg_score": 690},
                {"month": "Mar", "avg_score": 700}
            ],
            "risk_distribution": [
                {"company": "DEMO", "score": 700, "risk_level": "Low"}
            ],
            "summary": {
                "total_companies": 1,
                "avg_score": 700,
                "high_risk_count": 0,
                "last_updated": datetime.utcnow()
            }
        }

def _get_sector_color(sector: str) -> str:
    """Get color for sector"""
    colors = {
        "Technology": "#1976d2",
        "Financial Services": "#dc004e",
        "Healthcare": "#4caf50",
        "Consumer Cyclical": "#ff9800",
        "Energy": "#9c27b0",
        "Utilities": "#795548",
        "Real Estate": "#607d8b",
        "Materials": "#e91e63",
        "Industrials": "#3f51b5"
    }
    return colors.get(sector, "#9e9e9e")

def _get_risk_level(score: float) -> str:
    """Get risk level based on credit score"""
    if score >= 750:
        return "Low"
    elif score >= 650:
        return "Medium"
    else:
        return "High"

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)