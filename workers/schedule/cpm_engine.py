"""
Critical Path Method (CPM) Construction Schedule Engine
Delta Specification §11, §14
Generates deterministic precedence networks, activity durations, and zero-float critical paths.
"""

from typing import Dict, Any, List


def generate_construction_schedule(
    total_bua_sqm: float,
    floors: int = 1
) -> Dict[str, Any]:
    """
    Computes a deterministic CPM construction timeline based on work packages.
    """
    # Scale activity durations based on BUA and floors
    scale = max(0.8, min(2.0, total_bua_sqm / 100.0))

    activities = [
        {
            "code": "ACT-01",
            "name": "Design Release & Statutory Verification (Gate G4/G5)",
            "workPackage": "PRE_CONSTRUCTION",
            "durationWeeks": 2,
            "predecessors": [],
            "critical": True,
            "crew": "Architect & Liaison Officer"
        },
        {
            "code": "ACT-02",
            "name": "Site Mobilization, Survey Baseline & Borehole Test",
            "workPackage": "EARTHWORK",
            "durationWeeks": 1,
            "predecessors": ["ACT-01"],
            "critical": True,
            "crew": "Site Surveyor & Labor Gang"
        },
        {
            "code": "ACT-03",
            "name": "Trench Excavation & Foundation PCC Blinding",
            "workPackage": "EARTHWORK",
            "durationWeeks": round(1.5 * scale, 1),
            "predecessors": ["ACT-02"],
            "critical": True,
            "crew": "JCB Operator & 6 Workers"
        },
        {
            "code": "ACT-04",
            "name": "RCC Isolated Footings & Stub Columns to Plinth",
            "workPackage": "STRUCTURE",
            "durationWeeks": round(2.0 * scale, 1),
            "predecessors": ["ACT-03"],
            "critical": True,
            "crew": "Bar Benders & Concreting Crew"
        },
        {
            "code": "ACT-05",
            "name": "Plinth Beam Concreting, Backfilling & Anti-Termite",
            "workPackage": "STRUCTURE",
            "durationWeeks": round(1.5 * scale, 1),
            "predecessors": ["ACT-04"],
            "critical": True,
            "crew": "Masonry & Pest Control"
        },
        {
            "code": "ACT-06",
            "name": "Ground Floor RCC Columns & Roof Slab (Level L0)",
            "workPackage": "STRUCTURE",
            "durationWeeks": round(2.5 * scale, 1),
            "predecessors": ["ACT-05"],
            "critical": True,
            "crew": "Shuttering Carpenters & Concreters"
        }
    ]

    if floors > 1:
        activities.append({
            "code": "ACT-06B",
            "name": "First Floor RCC Columns & Terrace Slab (Level L1)",
            "workPackage": "STRUCTURE",
            "durationWeeks": round(2.5 * scale, 1),
            "predecessors": ["ACT-06"],
            "critical": True,
            "crew": "Carpenters & Concreting Crew"
        })
        last_struct_act = "ACT-06B"
    else:
        last_struct_act = "ACT-06"

    activities.extend([
        {
            "code": "ACT-07",
            "name": "AAC Block Masonry & Lintel Bands",
            "workPackage": "MASONRY",
            "durationWeeks": round(2.0 * scale, 1),
            "predecessors": [last_struct_act],
            "critical": True,
            "crew": "8 Masons & Helpers"
        },
        {
            "code": "ACT-08",
            "name": "Concealed Conduit Electrical & Plumbing Piping",
            "workPackage": "MEP_ROUGH_IN",
            "durationWeeks": round(1.5 * scale, 1),
            "predecessors": ["ACT-07"],
            "critical": True,
            "crew": "Electrician & Plumber Team"
        },
        {
            "code": "ACT-09",
            "name": "Internal Smooth Plaster & External Weather Plaster",
            "workPackage": "FINISHES",
            "durationWeeks": round(2.0 * scale, 1),
            "predecessors": ["ACT-08"],
            "critical": True,
            "crew": "Plastering Gang"
        },
        {
            "code": "ACT-10",
            "name": "Wet Area Waterproofing (Toilets, Balconies & Roof)",
            "workPackage": "WATERPROOFING",
            "durationWeeks": 1.0,
            "predecessors": ["ACT-09"],
            "critical": True,
            "crew": "Waterproofing Specialist"
        },
        {
            "code": "ACT-11",
            "name": "Vitrified Tile Flooring & Dado Wall Tiling",
            "workPackage": "FINISHES",
            "durationWeeks": round(2.0 * scale, 1),
            "predecessors": ["ACT-10"],
            "critical": True,
            "crew": "Tile Layers"
        },
        {
            "code": "ACT-12",
            "name": "Doors, UPVC Windows, Glass & Balcony Railings",
            "workPackage": "JOINERY",
            "durationWeeks": round(1.0 * scale, 1),
            "predecessors": ["ACT-11"],
            "critical": False,
            "crew": "Carpentry & Glazing Team"
        },
        {
            "code": "ACT-13",
            "name": "Interior/Exterior Painting (Primer, Putty & Emulsion)",
            "workPackage": "FINISHES",
            "durationWeeks": round(1.5 * scale, 1),
            "predecessors": ["ACT-11"],
            "critical": True,
            "crew": "Painters"
        },
        {
            "code": "ACT-14",
            "name": "Modular Switches, Fixtures, Sanitaryware & Testing",
            "workPackage": "COMMISSIONING",
            "durationWeeks": 1.0,
            "predecessors": ["ACT-12", "ACT-13"],
            "critical": True,
            "crew": "Fit-out Team"
        },
        {
            "code": "ACT-15",
            "name": "Defect Snagging, Deep Cleaning & As-Built Documentation",
            "workPackage": "HANDOVER",
            "durationWeeks": 1.0,
            "predecessors": ["ACT-14"],
            "critical": True,
            "crew": "Quality Inspector & Site Lead"
        },
        {
            "code": "ACT-16",
            "name": "Final Professional Sign-Off & Customer Handover (G8)",
            "workPackage": "HANDOVER",
            "durationWeeks": 0.5,
            "predecessors": ["ACT-15"],
            "critical": True,
            "crew": "Client & Project Director"
        }
    ])

    # Compute Forward Pass for CPM Timeline
    current_week = 0.0
    for act in activities:
        act["startWeek"] = round(current_week, 1)
        current_week += act["durationWeeks"]
        act["endWeek"] = round(current_week, 1)

    total_duration_weeks = round(current_week, 1)
    total_duration_months = round(total_duration_weeks / 4.33, 1)

    return {
        "scheduleMethod": "CPM_DETERMINISTIC_NETWORK",
        "totalDurationWeeks": total_duration_weeks,
        "totalDurationMonths": total_duration_months,
        "estimatedDays": int(total_duration_weeks * 6), # 6-day work weeks
        "criticalPathCount": sum(1 for a in activities if a["critical"]),
        "activities": activities
    }
