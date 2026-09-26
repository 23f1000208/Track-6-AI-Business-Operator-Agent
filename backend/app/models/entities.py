"""
SQLAlchemy ORM Entities for OpsPilot AI.
Persists Agent runs, steps, tool calls, business actions, approvals, and audit trail.
"""
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Boolean, Float, ForeignKey, JSON
)
from sqlalchemy.orm import relationship
from app.models.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True, nullable=False)
    role = Column(String(50), default="Business Manager")
    created_at = Column(DateTime, default=datetime.utcnow)


class BusinessRequest(Base):
    __tablename__ = "business_requests"

    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(String(64), unique=True, index=True, nullable=False)
    raw_prompt = Column(Text, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class AgentRun(Base):
    __tablename__ = "agent_runs"

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(String(64), unique=True, index=True, nullable=False)
    user_request = Column(Text, nullable=False)
    intent = Column(String(255), nullable=True)
    objective = Column(Text, nullable=True)
    status = Column(String(50), default="RUNNING")  # RUNNING, PENDING_APPROVAL, COMPLETED, FAILED, STOPPED
    is_demo_mode = Column(Boolean, default=True)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    duration_seconds = Column(Float, nullable=True)
    metrics = Column(JSON, default=dict)
    final_result = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)

    steps = relationship("AgentStep", back_populates="run", cascade="all, delete-orphan")
    tool_calls = relationship("ToolCall", back_populates="run", cascade="all, delete-orphan")
    actions = relationship("ActionRecord", back_populates="run", cascade="all, delete-orphan")
    approvals = relationship("ApprovalRequest", back_populates="run", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="run", cascade="all, delete-orphan")


class AgentStep(Base):
    __tablename__ = "agent_steps"

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(String(64), ForeignKey("agent_runs.run_id"), index=True, nullable=False)
    step_number = Column(Integer, nullable=False)
    action = Column(String(100), nullable=False)  # UNDERSTAND, PLAN, TOOL_SELECT, EXECUTE, OBSERVE, DECIDE, VERIFY
    tool = Column(String(50), nullable=True)
    status = Column(String(50), default="COMPLETED")  # STARTED, COMPLETED, FAILED, SKIPPED
    result_summary = Column(Text, nullable=True)
    structured_details = Column(JSON, default=dict)
    timestamp = Column(DateTime, default=datetime.utcnow)

    run = relationship("AgentRun", back_populates="steps")


class ToolCall(Base):
    __tablename__ = "tool_calls"

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(String(64), ForeignKey("agent_runs.run_id"), index=True, nullable=False)
    tool_name = Column(String(100), nullable=False)
    input_summary = Column(Text, nullable=True)
    output_summary = Column(Text, nullable=True)
    raw_input = Column(JSON, default=dict)
    raw_output = Column(JSON, default=dict)
    status = Column(String(50), default="SUCCESS")  # SUCCESS, FAILED, RETRIED, TIMEOUT
    latency_ms = Column(Float, default=0.0)
    retry_count = Column(Integer, default=0)
    timestamp = Column(DateTime, default=datetime.utcnow)

    run = relationship("AgentRun", back_populates="tool_calls")


class ActionRecord(Base):
    __tablename__ = "actions"

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(String(64), ForeignKey("agent_runs.run_id"), index=True, nullable=False)
    action_type = Column(String(50), nullable=False)  # JIRA_TASK, GMAIL_EMAIL, SLACK_NOTIFICATION, NOTION_UPDATE
    target = Column(String(255), nullable=False)
    payload = Column(JSON, default=dict)
    status = Column(String(50), default="PENDING")  # PENDING, EXECUTED, VERIFIED, SKIPPED_IDEMPOTENT, FAILED
    verification_id = Column(String(255), nullable=True)
    verification_status = Column(String(50), nullable=True)
    idempotent_hash = Column(String(64), index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    executed_at = Column(DateTime, nullable=True)

    run = relationship("AgentRun", back_populates="actions")


class ApprovalRequest(Base):
    __tablename__ = "approvals"

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(String(64), ForeignKey("agent_runs.run_id"), index=True, nullable=False)
    action_id = Column(String(64), unique=True, index=True, nullable=False)
    action_type = Column(String(50), nullable=False)
    description = Column(Text, nullable=False)
    target = Column(String(255), nullable=False)
    impact = Column(String(100), default="Medium")
    risk_level = Column(String(50), default="MEDIUM")  # LOW, MEDIUM, HIGH, CRITICAL
    evidence = Column(JSON, default=dict)
    status = Column(String(50), default="PENDING")  # PENDING, APPROVED, REJECTED
    approved_by = Column(String(100), nullable=True)
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    decided_at = Column(DateTime, nullable=True)

    run = relationship("AgentRun", back_populates="approvals")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(String(64), ForeignKey("agent_runs.run_id"), index=True, nullable=True)
    event = Column(String(100), nullable=False)
    details = Column(JSON, default=dict)
    timestamp = Column(DateTime, default=datetime.utcnow)

    run = relationship("AgentRun", back_populates="audit_logs")
