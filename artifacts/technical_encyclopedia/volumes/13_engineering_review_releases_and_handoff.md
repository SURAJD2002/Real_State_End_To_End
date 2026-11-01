# Volume XIII — Engineering Review, Releases, and Construction Handoff

## 1. Seven-Stage Engineering Review Gate Model (G0–G6)
Planwise enforces a rigorous, sequentially locked engineering sign-off gate sequence (`packages/schemas/engineer_review.py`):


<div class="diagram-container">
  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 700 140" width="100%" height="140px" class="svg-diagram" style="max-height:140px; background:#f8fafc; border:1px solid #e2e8f0; border-radius:6px; font-family:-apple-system,BlinkMacSystemFont,Segoe UI,Roboto,sans-serif;">
<defs>
  <marker id="arr" markerWidth="6" markerHeight="6" refX="5" refY="3" orient="auto">
    <path d="M0,0 L6,3 L0,6 Z" fill="#2563eb" />
  </marker>
  <marker id="arr-gray" markerWidth="6" markerHeight="6" refX="5" refY="3" orient="auto">
    <path d="M0,0 L6,3 L0,6 Z" fill="#64748b" />
  </marker>
</defs>

<text x="350" y="24" text-anchor="middle" font-size="13" font-weight="bold" fill="#0f172a">DIAGRAM 6: ENGINEER REVIEW GATES (G0 - G6) & STATUTORY BYPASS PROTECTION</text>
<rect x="25" y="45" width="85" height="75" rx="3" fill="#ffffff" stroke="#3b82f6" stroke-width="1.2"/>
<text x="67" y="65" text-anchor="middle" font-size="9" font-weight="bold" fill="#1e40af">G0: SITE</text>
<text x="67" y="80" text-anchor="middle" font-size="7" fill="#334155">Statutory Rules</text>
<text x="67" y="92" text-anchor="middle" font-size="7" fill="#334155">Setback Check</text>
<text x="67" y="106" text-anchor="middle" font-size="7" font-weight="bold" fill="#059669">AUTOMATED</text>

<line x1="110" y1="82" x2="122" y2="82" stroke="#64748b" stroke-width="1.2" marker-end="url(#arr-gray)"/>

<rect x="122" y="45" width="85" height="75" rx="3" fill="#ffffff" stroke="#3b82f6" stroke-width="1.2"/>
<text x="164" y="65" text-anchor="middle" font-size="9" font-weight="bold" fill="#1e40af">G1: ARCH</text>
<text x="164" y="80" text-anchor="middle" font-size="7" fill="#334155">NBC 2016 Rooms</text>
<text x="164" y="92" text-anchor="middle" font-size="7" fill="#334155">Lighting & Vent</text>
<text x="164" y="106" text-anchor="middle" font-size="7" font-weight="bold" fill="#059669">AUTOMATED</text>

<line x1="207" y1="82" x2="219" y2="82" stroke="#64748b" stroke-width="1.2" marker-end="url(#arr-gray)"/>

<rect x="219" y="45" width="85" height="75" rx="3" fill="#ffffff" stroke="#3b82f6" stroke-width="1.2"/>
<text x="261" y="65" text-anchor="middle" font-size="9" font-weight="bold" fill="#1e40af">G2: STRUCT</text>
<text x="261" y="80" text-anchor="middle" font-size="7" fill="#334155">Grid Alignment</text>
<text x="261" y="92" text-anchor="middle" font-size="7" fill="#334155">Span Checks</text>
<text x="261" y="106" text-anchor="middle" font-size="7" font-weight="bold" fill="#059669">AUTOMATED</text>

<line x1="304" y1="82" x2="316" y2="82" stroke="#64748b" stroke-width="1.2" marker-end="url(#arr-gray)"/>

<rect x="316" y="45" width="85" height="75" rx="3" fill="#ffffff" stroke="#3b82f6" stroke-width="1.2"/>
<text x="358" y="65" text-anchor="middle" font-size="9" font-weight="bold" fill="#1e40af">G3: MEP</text>
<text x="358" y="80" text-anchor="middle" font-size="7" fill="#334155">Shaft Verticality</text>
<text x="358" y="92" text-anchor="middle" font-size="7" fill="#334155">Wet Wall Drops</text>
<text x="358" y="106" text-anchor="middle" font-size="7" font-weight="bold" fill="#059669">AUTOMATED</text>

<line x1="401" y1="82" x2="413" y2="82" stroke="#64748b" stroke-width="1.2" marker-end="url(#arr-gray)"/>

<rect x="413" y="45" width="85" height="75" rx="3" fill="#ffffff" stroke="#3b82f6" stroke-width="1.2"/>
<text x="455" y="65" text-anchor="middle" font-size="9" font-weight="bold" fill="#1e40af">G4: COST</text>
<text x="455" y="80" text-anchor="middle" font-size="7" fill="#334155">IS 1200 QTO</text>
<text x="455" y="92" text-anchor="middle" font-size="7" fill="#334155">Rate Lock</text>
<text x="455" y="106" text-anchor="middle" font-size="7" font-weight="bold" fill="#059669">AUTOMATED</text>

<line x1="498" y1="82" x2="510" y2="82" stroke="#64748b" stroke-width="1.2" marker-end="url(#arr-gray)"/>

<rect x="510" y="45" width="85" height="75" rx="3" fill="#ffffff" stroke="#d97706" stroke-width="1.5"/>
<text x="552" y="65" text-anchor="middle" font-size="9" font-weight="bold" fill="#b45309">G5: SANCTION</text>
<text x="552" y="80" text-anchor="middle" font-size="7" fill="#334155">Architect Signoff</text>
<text x="552" y="92" text-anchor="middle" font-size="7" fill="#334155">Licensed Survey</text>
<text x="552" y="106" text-anchor="middle" font-size="7" font-weight="bold" fill="#b45309">PROFESSIONAL</text>

<line x1="595" y1="82" x2="607" y2="82" stroke="#64748b" stroke-width="1.2" marker-end="url(#arr-gray)"/>

<rect x="607" y="45" width="70" height="75" rx="3" fill="#ffffff" stroke="#059669" stroke-width="1.5"/>
<text x="642" y="65" text-anchor="middle" font-size="9" font-weight="bold" fill="#047857">G6: BUILD</text>
<text x="642" y="80" text-anchor="middle" font-size="7" fill="#334155">Immutable</text>
<text x="642" y="92" text-anchor="middle" font-size="7" fill="#334155">Release Lock</text>
<text x="642" y="106" text-anchor="middle" font-size="7" font-weight="bold" fill="#047857">CERTIFIED</text>

</svg>
  <div class="diagram-caption">Diagram 6: Seven-Stage Sequential Engineering Review Gate Transition Machine (G0–G6)</div>
</div>


```
[G0_SITE] ──> [G1_STRUCTURAL] ──> [G2_ARCHITECTURAL] ──> [G3_MEP]
    │                │                   │                  │
Boundary & GPS   Grid Alignment      NBC 2016 Flow      Plumbing & Power
    │                │                   │                  │
    ▼                ▼                   ▼                  ▼
[G4_STATUTORY] ─────────────────> [G5_COST] ───────> [G6_CONSTRUCTION]
Municipal Setbacks                BOQ & Budget       Contractor Handoff
```

---

## 2. Review Gate Schema Source Code (`engineer_review.py`)

```python
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

```

---

## 3. Review Gate Roadmap Clarification (G7 & G8)
> [!NOTE]
> Historical documentation referenced review gates G0 through G8. In the actual code implementation:
> - **Active Review Gates:** Strictly **G0 through G6** (7 gates) implemented in `GateCode` enum and database tables.
> - **Roadmap Milestones:** `G7` (Site Release & Groundbreaking) and `G8` (Completion Certificate & Handover) represent statutory Critical Path Method (CPM) milestones in scheduling algorithms, but possess no active API review endpoints.
