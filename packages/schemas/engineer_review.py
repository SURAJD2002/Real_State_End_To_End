"""
Planwise Enterprise — Engineer Review & Professional Verification Domain Schemas
Delta Specification §12, §13, §14 & Phase 7 Master Specification

Defines immutable audit-traced structures for professional engineering review,
independent verification gates (G0–G6), structured issues, and reviewer decisions.
"""

from typing import List, Optional, Dict, Any
from enum import Enum
from datetime import datetime, timezone
from pydantic import BaseModel, Field
import uuid


class ReviewStatus(str, Enum):
    IN_REVIEW = "IN_REVIEW"
    CHANGES_REQUIRED = "CHANGES_REQUIRED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    STALE = "STALE"


class GateCode(str, Enum):
    G0 = "G0"  # Site & Boundary Verification
    G1 = "G1"  # Regulatory & Feasibility Review
    G2 = "G2"  # Structural Review
    G3 = "G3"  # MEP & Services Review
    G4 = "G4"  # Cost & BOQ Review
    G5 = "G5"  # Build Authorization (LOCKED until G0-G4 satisfied)
    G6 = "G6"  # Contractor Handoff (LOCKED)


class GateStatus(str, Enum):
    PENDING = "PENDING"
    VERIFIED = "VERIFIED"
    SYSTEM_VERIFIED = "SYSTEM_VERIFIED"
    CHANGES_REQUIRED = "CHANGES_REQUIRED"
    REVIEWED = "REVIEWED"
    LOCKED = "LOCKED"


class IssueSeverity(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    BLOCKER = "BLOCKER"


class IssueStatus(str, Enum):
    OPEN = "OPEN"
    RESOLVED = "RESOLVED"
    WAIVED = "WAIVED"


class ReviewDecisionType(str, Enum):
    APPROVE_STAGE = "APPROVE_STAGE"
    REQUEST_CHANGES = "REQUEST_CHANGES"
    CANNOT_PROCEED = "CANNOT_PROCEED"


class ReviewGate(BaseModel):
    id: str = Field(default_factory=lambda: f"gate-{uuid.uuid4().hex[:8]}")
    engineerReviewId: str
    gateCode: GateCode
    title: str
    status: GateStatus = GateStatus.PENDING
    reviewedBy: Optional[str] = None
    reviewedAt: Optional[str] = None
    notes: Optional[str] = None


class ReviewIssue(BaseModel):
    id: str = Field(default_factory=lambda: f"iss-{uuid.uuid4().hex[:8]}")
    engineerReviewId: str
    gateCode: GateCode
    severity: IssueSeverity = IssueSeverity.WARNING
    category: str
    description: str
    requiredAction: str
    status: IssueStatus = IssueStatus.OPEN
    createdBy: str = "ENG-MH-48201"
    createdAt: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class ReviewDecision(BaseModel):
    id: str = Field(default_factory=lambda: f"dec-{uuid.uuid4().hex[:8]}")
    engineerReviewId: str
    decision: ReviewDecisionType
    decidedBy: str
    decidedAt: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    reason: str


class ProfessionalVerification(BaseModel):
    verificationId: str = Field(default_factory=lambda: f"pv-{uuid.uuid4().hex[:8]}")
    engineerReviewId: str
    reviewerLicenseNo: str
    reviewerName: str
    verifiedAt: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    signatureHash: str


class EngineerReview(BaseModel):
    id: str = Field(default_factory=lambda: f"rev-{uuid.uuid4().hex[:10]}")
    projectId: str
    buildRequestId: str
    releaseId: str
    designVersionId: str
    reviewerId: str = "ENG-MH-48201"
    status: ReviewStatus = ReviewStatus.IN_REVIEW
    createdAt: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updatedAt: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    inputManifestHash: str
    designVersionHash: str
    declaredPlotAreaSqFt: float = 1100.0  # Authoritative customer plot area
    gates: List[ReviewGate] = Field(default_factory=list)
    issues: List[ReviewIssue] = Field(default_factory=list)
    decisions: List[ReviewDecision] = Field(default_factory=list)


def create_initial_review_gates(review_id: str) -> List[ReviewGate]:
    """
    Initializes default G0–G6 gates with proper statutory baseline statuses (§3).
    G0, G2, G3 are strictly PENDING.
    G1 is SYSTEM_VERIFIED (computed by statutory engine).
    G4 is REVIEWED (customer preliminary cost).
    G5 & G6 are LOCKED.
    """
    return [
        ReviewGate(
            engineerReviewId=review_id,
            gateCode=GateCode.G0,
            title="Site & Boundary Verification",
            status=GateStatus.PENDING,
            notes="Awaiting registered surveyor physical boundary verification."
        ),
        ReviewGate(
            engineerReviewId=review_id,
            gateCode=GateCode.G1,
            title="Regulatory & Feasibility Review",
            status=GateStatus.SYSTEM_VERIFIED,
            notes="Mumbai DCPR 2034 automated compliance passed by rule engine."
        ),
        ReviewGate(
            engineerReviewId=review_id,
            gateCode=GateCode.G2,
            title="Structural Review",
            status=GateStatus.PENDING,
            notes="Preliminary computational grid available. Requires licensed structural engineer review."
        ),
        ReviewGate(
            engineerReviewId=review_id,
            gateCode=GateCode.G3,
            title="MEP & Services Review",
            status=GateStatus.PENDING,
            notes="Preliminary schematic wet-wall coordination available."
        ),
        ReviewGate(
            engineerReviewId=review_id,
            gateCode=GateCode.G4,
            title="Cost & BOQ Review",
            status=GateStatus.REVIEWED,
            notes="Model-linked IS 1200 preliminary estimate reviewed by customer."
        ),
        ReviewGate(
            engineerReviewId=review_id,
            gateCode=GateCode.G5,
            title="Build Authorization",
            status=GateStatus.LOCKED,
            notes="LOCKED: Requires G0, G1, G2, G3, G4 professional verification."
        ),
        ReviewGate(
            engineerReviewId=review_id,
            gateCode=GateCode.G6,
            title="Contractor Handoff",
            status=GateStatus.LOCKED,
            notes="LOCKED: Requires signed construction release."
        ),
    ]
