"""
Pydantic schemas for payments, customer records, and deterministic classification.
"""
from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field


class PaymentStatus(str, Enum):
    COMPLETED = "COMPLETED"
    PENDING = "PENDING"
    FAILED = "FAILED"


class PriorityLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class Customer(BaseModel):
    customer_id: str
    name: str
    email: str
    company: Optional[str] = None
    tier: str = "Standard"  # Enterprise, Business, Standard


class PaymentRecord(BaseModel):
    payment_id: str = Field(..., description="Unique payment identifier e.g. PAY-1001")
    customer_id: str
    customer_name: str
    customer_email: str
    amount: float = Field(..., ge=0.0)
    currency: str = "USD"
    status: PaymentStatus
    failure_reason: Optional[str] = None
    created_at: str
    age_days: int = 0
    tier: str = "Standard"
    requires_action: bool = False
    priority: PriorityLevel = PriorityLevel.LOW
    recommended_action: Optional[str] = None


class PaymentClassificationSummary(BaseModel):
    total_analyzed: int
    require_attention: int
    failed_count: int
    pending_count: int
    completed_count: int
    critical_count: int
    high_count: int
    medium_count: int
    low_count: int
    total_at_risk_amount: float
    affected_customers: List[str]
