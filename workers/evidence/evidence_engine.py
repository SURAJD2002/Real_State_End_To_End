"""
Planwise Enterprise — Deterministic Site Confidence & Evidence Engine
Delta Specification M1 — §1, §2

Evaluates site evidence items, computes authoritative site confidence tier (L0 to L4),
and gates the BUILD release workflow against unverified boundary risks.
"""

from typing import List, Dict, Any, Tuple
from packages.schemas.site_evidence import (
    SiteEvidence,
    SiteConfidenceTier,
    EvidenceType,
    VerificationStatus,
    ConfidenceEvaluationSummary
)


def evaluate_site_confidence(
    site_id: str,
    evidence_list: List[SiteEvidence]
) -> ConfidenceEvaluationSummary:
    """
    Computes deterministic site confidence level from accumulated evidence items (§2).
    
    Tiers:
    - L0: GIS-derived only (public basemaps / satellite traces)
    - L1: Customer-uploaded documents (deeds, unverified drawings)
    - L2: Remote verification performed
    - L3: Field-stamped licensed land survey with boundary vertices & levels (Mandatory for BUILD)
    - L4: Comprehensive engineering readiness (L3 + verified geotechnical borehole soil report + utilities)
    """
    if not evidence_list:
        return ConfidenceEvaluationSummary(
            siteId=site_id,
            overallConfidence=SiteConfidenceTier.L0_GIS_ESTIMATE,
            isBlockingForBuildRelease=True,
            highestVerifiedTier=SiteConfidenceTier.L0_GIS_ESTIMATE,
            totalEvidenceCount=0,
            verifiedEvidenceCount=0,
            missingEvidenceForL3=["Licensed Land Survey Boundary", "Site & Road Datum Levels"],
            missingEvidenceForL4=["Licensed Land Survey Boundary", "Site & Road Datum Levels", "Geotechnical Soil Borehole Report", "Subsurface Utility Clearances"],
            explanation="Site relies solely on initial GIS satellite basemaps. Field survey is required before building release."
        )

    verified_evidence = [e for e in evidence_list if e.verificationStatus == VerificationStatus.VERIFIED]
    verified_types = {e.evidenceType for e in verified_evidence}

    has_verified_survey = any(
        e.evidenceType in [EvidenceType.PARCEL_BOUNDARY, EvidenceType.SURVEY_PLAN, EvidenceType.TOTAL_STATION, EvidenceType.GNSS_SURVEY]
        and e.accuracyM <= 0.05
        for e in verified_evidence
    )
    has_site_levels = any(e.evidenceType in [EvidenceType.SITE_LEVEL, EvidenceType.ROAD_LEVEL, EvidenceType.TOPOGRAPHY] for e in verified_evidence)
    has_soil_report = any(e.evidenceType in [EvidenceType.SOIL_REPORT, EvidenceType.GEOTECHNICAL] for e in verified_evidence)
    has_utilities = any(e.evidenceType in [EvidenceType.UTILITY, EvidenceType.EASEMENT] for e in verified_evidence)

    # Determine highest eligible tier
    missing_for_l3: List[str] = []
    if not has_verified_survey:
        missing_for_l3.append("Licensed Land Survey Boundary (Accuracy <= 0.05m)")
    if not has_site_levels:
        missing_for_l3.append("Site / Road Datum Spot Levels")

    missing_for_l4: List[str] = list(missing_for_l3)
    if not has_soil_report:
        missing_for_l4.append("Geotechnical Soil Report with Safe Bearing Capacity (SBC)")
    if not has_utilities:
        missing_for_l4.append("Subsurface Utility / Service Corridor Survey")

    if has_verified_survey and has_site_levels and has_soil_report and has_utilities:
        tier = SiteConfidenceTier.L4_ENGINEERING_READY
        blocking = False
        explanation = "Full Engineering Site Truth achieved (L4). Licensed survey, spot levels, geotechnical borehole data, and utility corridors verified."
    elif has_verified_survey and has_site_levels:
        tier = SiteConfidenceTier.L3_LICENSED_SURVEY
        blocking = False
        explanation = "Authoritative Licensed Land Survey verified (L3). Boundary coordinates and spot levels stamped by licensed surveyor. Safe for BUILD release."
    elif any(e.confidenceLevel == SiteConfidenceTier.L2_REMOTE_VERIFIED and e.verificationStatus == VerificationStatus.VERIFIED for e in evidence_list):
        tier = SiteConfidenceTier.L2_REMOTE_VERIFIED
        blocking = True
        explanation = "Remote analyst verification complete (L2). Boundary cross-checked with municipal revenue maps, but on-ground licensed survey is pending."
    elif any(e.evidenceType in [EvidenceType.SALE_DEED, EvidenceType.LAND_RECORD, EvidenceType.SURVEY_PLAN] for e in evidence_list):
        tier = SiteConfidenceTier.L1_CUSTOMER_DOCUMENT
        blocking = True
        explanation = "Customer title documents / deeds uploaded (L1). Physical ground verification and boundary demarcation are required."
    else:
        tier = SiteConfidenceTier.L0_GIS_ESTIMATE
        blocking = True
        explanation = "GIS satellite parcel trace only (L0). Legal boundary certainty is unverified. Licensed field survey is required."

    return ConfidenceEvaluationSummary(
        siteId=site_id,
        overallConfidence=tier,
        isBlockingForBuildRelease=blocking,
        highestVerifiedTier=tier,
        totalEvidenceCount=len(evidence_list),
        verifiedEvidenceCount=len(verified_evidence),
        missingEvidenceForL3=missing_for_l3,
        missingEvidenceForL4=missing_for_l4,
        explanation=explanation
    )
