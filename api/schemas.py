from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional, Dict, Any
from decimal import Decimal

class CompanyResponse(BaseModel):
    id: int
    symbol: str
    name: str
    sector: Optional[str]
    industry: Optional[str]
    market_cap: Optional[int]
    
    class Config:
        from_attributes = True

class CreditScoreResponse(BaseModel):
    time: datetime
    company_id: int
    score: Decimal
    confidence: Optional[Decimal]
    model_version: Optional[str]
    
    class Config:
        from_attributes = True

class FeatureContribution(BaseModel):
    feature: str
    importance: Decimal
    shap_value: Optional[Decimal]
    current_value: Optional[Decimal]

class RecentEvent(BaseModel):
    timestamp: datetime
    headline: str
    sentiment: Optional[Decimal]
    impact: Optional[Decimal]
    event_type: Optional[str]

class ExplanationResponse(BaseModel):
    score: Decimal
    confidence: Optional[Decimal]
    timestamp: datetime
    feature_contributions: List[FeatureContribution]
    recent_events: List[RecentEvent]
    summary: str

class CompanyDashboardData(BaseModel):
    id: int
    symbol: str
    name: str
    sector: Optional[str]
    current_score: Decimal
    confidence: Optional[Decimal]
    last_updated: datetime

class Alert(BaseModel):
    company_symbol: str
    company_name: str
    score_change: Decimal
    timestamp: datetime
    severity: str

class DashboardData(BaseModel):
    companies: List[CompanyDashboardData]
    alerts: List[Alert]
    total_companies: int
    last_updated: datetime