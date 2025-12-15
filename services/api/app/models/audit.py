from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, Float, Text, JSON, Numeric, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.models.base import Base

class AuditStatus(str, enum.Enum):
    PENDING_REVIEW = "PENDING_REVIEW"
    IN_REVIEW = "IN_REVIEW"
    COMPLETED = "COMPLETED"
    BLUEPRINT_GENERATED = "BLUEPRINT_GENERATED"
    ARCHIVED = "ARCHIVED"

class AuditItemType(str, enum.Enum):
    TRADELINE = "TRADELINE"
    COLLECTION = "COLLECTION"
    INQUIRY = "INQUIRY"
    PUBLIC_RECORD = "PUBLIC_RECORD"
    PERSONAL_INFO = "PERSONAL_INFO"

class ItemResolution(str, enum.Enum):
    GENERAL_DISPUTE = "GENERAL_DISPUTE"
    FCRA_VIOLATION = "FCRA_VIOLATION"
    IDENTITY_THEFT = "IDENTITY_THEFT"
    DEBT_VALIDATION = "DEBT_VALIDATION"
    PAY_FOR_DELETE = "PAY_FOR_DELETE"
    GOODWILL_LETTER = "GOODWILL_LETTER"
    AUTHORIZED_USER_REMOVAL = "AUTHORIZED_USER_REMOVAL"
    SETTLEMENT_NEGOTIATION = "SETTLEMENT_NEGOTIATION"
    DO_NOT_DISPUTE = "DO_NOT_DISPUTE"
    MONITOR_ONLY = "MONITOR_ONLY"

class BlueprintAudit(Base):
    __tablename__ = "blueprint_audits"

    id = Column(String, primary_key=True, index=True)
    userId = Column(String, ForeignKey("users.id"), nullable=False)
    creditReportId = Column(String, ForeignKey("credit_reports.id"), nullable=False)
    
    # Scores
    transunionScore = Column(Integer, nullable=True)
    equifaxScore = Column(Integer, nullable=True)
    experianScore = Column(Integer, nullable=True)

    # Automated Analysis
    totalViolationsFound = Column(Integer, default=0)
    utilizationPercentage = Column(Numeric(10, 2), nullable=True)
    totalUtilizationBalance = Column(Numeric(10, 2), nullable=True)
    totalCreditLimit = Column(Numeric(10, 2), nullable=True)
    amountToReach20Percent = Column(Numeric(10, 2), nullable=True)
    positiveTradelineCount = Column(Integer, default=0)
    negativeItemCount = Column(Integer, default=0)
    collectionCount = Column(Integer, default=0)
    inquiryCount = Column(Integer, default=0)

    # Flags
    needsStarterAccounts = Column(Boolean, default=False)
    needsRentalTradelines = Column(Boolean, default=False)
    hasAuthorizedUserIssues = Column(Boolean, default=False)

    # Status
    status = Column(String, default=AuditStatus.PENDING_REVIEW)
    reviewedBy = Column(String, nullable=True)
    reviewedAt = Column(DateTime, nullable=True)

    # Docs
    clientBlueprintUrl = Column(String, nullable=True)
    companyBlueprintUrl = Column(String, nullable=True)

    createdAt = Column(DateTime, default=datetime.utcnow)
    updatedAt = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relations
    # user = relationship("User", back_populates="blueprintAudits") 
    # creditReport = relationship("CreditReport", back_populates="blueprintAudits")
    auditItems = relationship("AuditItem", back_populates="audit", cascade="all, delete-orphan")
    recommendations = relationship("AuditRecommendation", back_populates="audit", cascade="all, delete-orphan")
    consultationForm = relationship("ConsultationForm", back_populates="audit", uselist=False)

class AuditItem(Base):
    __tablename__ = "audit_items"

    id = Column(String, primary_key=True, index=True)
    auditId = Column(String, ForeignKey("blueprint_audits.id"))
    
    itemType = Column(String, nullable=False) # Enum
    tradelineId = Column(String, nullable=True)
    # tradeline = relationship("Tradeline")
    
    # Cached Details
    creditorName = Column(String, nullable=True)
    accountNumber = Column(String, nullable=True)
    bureau = Column(String, nullable=True)
    accountType = Column(String, nullable=True)
    currentBalance = Column(Numeric(10, 2), nullable=True)
    creditLimit = Column(Numeric(10, 2), nullable=True)
    utilizationPercent = Column(Numeric(10, 2), nullable=True)
    isAuthorizedUser = Column(Boolean, default=False)
    
    # Detection
    detectedViolations = Column(JSON, nullable=True)
    violationCount = Column(Integer, default=0)
    isNegative = Column(Boolean, default=False)
    negativeReason = Column(String, nullable=True)
    
    # Resolution
    resolution = Column(String, nullable=True) # Enum ItemResolution
    resolutionNotes = Column(Text, nullable=True)
    
    # Flags
    doNotDispute = Column(Boolean, default=False)
    priorityLevel = Column(Integer, default=0)
    
    # Collections
    isSettleable = Column(Boolean, nullable=True)
    estimatedSettlement = Column(Numeric(10, 2), nullable=True)
    originalCreditor = Column(String, nullable=True)

    audit = relationship("BlueprintAudit", back_populates="auditItems")

class AuditRecommendation(Base):
    __tablename__ = "audit_recommendations"

    id = Column(String, primary_key=True, index=True)
    auditId = Column(String, ForeignKey("blueprint_audits.id"))
    
    type = Column(String, nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    priority = Column(Integer, default=0)
    
    productName = Column(String, nullable=True)
    productUrl = Column(String, nullable=True)
    estimatedImpact = Column(String, nullable=True)
    
    audit = relationship("BlueprintAudit", back_populates="recommendations")

class ConsultationForm(Base):
    __tablename__ = "consultation_forms"

    id = Column(String, primary_key=True, index=True)
    auditId = Column(String, ForeignKey("blueprint_audits.id"), unique=True)
    
    clientFirstName = Column(String, nullable=True)
    clientLastName = Column(String, nullable=True)
    clientEmail = Column(String, nullable=True)
    clientPhone = Column(String, nullable=True)
    
    # Financials
    monthlyIncome = Column(Numeric(10, 2), nullable=True)
    monthlyRent = Column(Numeric(10, 2), nullable=True)
    
    # Goals
    primaryGoal = Column(String, nullable=True)
    targetScore = Column(Integer, nullable=True)
    timeframe = Column(String, nullable=True)
    
    consultantNotes = Column(Text, nullable=True)
    
    audit = relationship("BlueprintAudit", back_populates="consultationForm")
