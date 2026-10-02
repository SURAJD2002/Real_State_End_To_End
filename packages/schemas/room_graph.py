"""
Planwise Enterprise — Room Adjacency & Privacy Graph Schema
M2 Milestone — Phase 3

Formal machine-readable topological adjacency graph defining required, preferred,
forbidden adjacencies, minimum separation, and privacy transitions between room types.
Used directly by the CP-SAT layout solver to enforce topological constraints.
"""

from typing import List, Dict, Any, Optional, Set, Tuple
from enum import Enum
from pydantic import BaseModel, Field

from packages.schemas.room_program import RoomType, PrivacyLevel


class AdjacencyRelationshipType(str, Enum):
    REQUIRED_ADJACENCY = "REQUIRED_ADJACENCY"      # Must share an edge / touching boundary
    PREFERRED_ADJACENCY = "PREFERRED_ADJACENCY"    # Soft objective: reward sharing edge or proximity
    FORBIDDEN_ADJACENCY = "FORBIDDEN_ADJACENCY"    # Hard constraint: must NOT share boundary
    MINIMUM_SEPARATION = "MINIMUM_SEPARATION"      # Must maintain Euclidean clearance (e.g. wet to dry)
    PRIVACY_BUFFER = "PRIVACY_BUFFER"              # Cannot open directly to public zone without buffer


class AdjacencyEdge(BaseModel):
    """Directed or undirected adjacency requirement between two room categories or space IDs."""
    fromRoom: str = Field(..., description="Source room type or spaceId")
    toRoom: str = Field(..., description="Target room type or spaceId")
    relationship: AdjacencyRelationshipType = Field(..., description="Type of topological relationship")
    weight: float = Field(default=100.0, description="Penalty/reward weight for soft constraints (0-100)")
    minSeparationM: float = Field(default=0.0, description="Minimum distance in meters if MINIMUM_SEPARATION")
    isBidirectional: bool = Field(default=True, description="Whether rule applies in both directions")
    description: Optional[str] = Field(default=None, description="Architectural rationale (e.g. plumbing cluster)")


class RoomAdjacencyGraph(BaseModel):
    """Complete machine-readable topological room graph."""
    graphId: str = Field(default="GRAPH-NBC2016-RES-01", description="Identifier of the graph topology")
    version: str = Field(default="2026.1", description="Version of the room graph specification")
    edges: List[AdjacencyEdge] = Field(default_factory=list, description="Adjacency edges")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadata and configuration")

    def get_relationship(self, room_a: str, room_b: str) -> Optional[AdjacencyEdge]:
        """Finds any explicit edge between room_a and room_b."""
        for edge in self.edges:
            if edge.fromRoom == room_a and edge.toRoom == room_b:
                return edge
            if edge.isBidirectional and (edge.fromRoom == room_b and edge.toRoom == room_a):
                return edge
        return None

    def get_forbidden_pairs(self) -> List[Tuple[str, str]]:
        """Returns list of all pairs that are forbidden from sharing boundaries."""
        pairs = []
        for edge in self.edges:
            if edge.relationship == AdjacencyRelationshipType.FORBIDDEN_ADJACENCY:
                pairs.append((edge.fromRoom, edge.toRoom))
        return pairs

    def get_required_pairs(self) -> List[Tuple[str, str]]:
        """Returns list of all pairs that MUST be adjacent."""
        pairs = []
        for edge in self.edges:
            if edge.relationship == AdjacencyRelationshipType.REQUIRED_ADJACENCY:
                pairs.append((edge.fromRoom, edge.toRoom))
        return pairs


def build_default_residential_adjacency_graph() -> RoomAdjacencyGraph:
    """
    Constructs the canonical standard Indian residential adjacency graph
    following NBC 2016 Part 3 spatial zoning and functional hierarchy.
    """
    edges: List[AdjacencyEdge] = [
        # Required Adjacencies
        AdjacencyEdge(
            fromRoom=RoomType.LIVING.value,
            toRoom=RoomType.ENTRY.value,
            relationship=AdjacencyRelationshipType.REQUIRED_ADJACENCY,
            weight=100.0,
            description="Entry foyer must connect directly to living room"
        ),
        AdjacencyEdge(
            fromRoom=RoomType.DINING.value,
            toRoom=RoomType.KITCHEN.value,
            relationship=AdjacencyRelationshipType.REQUIRED_ADJACENCY,
            weight=100.0,
            description="Kitchen must be directly adjacent or open to Dining"
        ),
        AdjacencyEdge(
            fromRoom=RoomType.KITCHEN.value,
            toRoom=RoomType.UTILITY.value,
            relationship=AdjacencyRelationshipType.REQUIRED_ADJACENCY,
            weight=95.0,
            description="Utility / wash yard must be adjacent to kitchen for wet service run"
        ),
        AdjacencyEdge(
            fromRoom=RoomType.STAIR.value,
            toRoom=RoomType.CORRIDOR.value,
            relationship=AdjacencyRelationshipType.REQUIRED_ADJACENCY,
            weight=90.0,
            description="Staircase must land into common circulation/corridor or foyer"
        ),

        # Preferred Adjacencies
        AdjacencyEdge(
            fromRoom=RoomType.LIVING.value,
            toRoom=RoomType.DINING.value,
            relationship=AdjacencyRelationshipType.PREFERRED_ADJACENCY,
            weight=80.0,
            description="Living and Dining open-plan or semi-partitioned layout"
        ),
        AdjacencyEdge(
            fromRoom=RoomType.LIVING.value,
            toRoom=RoomType.BALCONY.value,
            relationship=AdjacencyRelationshipType.PREFERRED_ADJACENCY,
            weight=75.0,
            description="Living room deck or outdoor sit-out access"
        ),
        AdjacencyEdge(
            fromRoom=RoomType.MASTER_BEDROOM.value,
            toRoom=RoomType.BATHROOM.value,
            relationship=AdjacencyRelationshipType.PREFERRED_ADJACENCY,
            weight=85.0,
            description="Master suite en-suite bath adjacency"
        ),
        AdjacencyEdge(
            fromRoom=RoomType.PUJA.value,
            toRoom=RoomType.LIVING.value,
            relationship=AdjacencyRelationshipType.PREFERRED_ADJACENCY,
            weight=70.0,
            description="Puja alcove accessible from public/semi-public zone"
        ),
        AdjacencyEdge(
            fromRoom=RoomType.PARKING.value,
            toRoom=RoomType.ENTRY.value,
            relationship=AdjacencyRelationshipType.PREFERRED_ADJACENCY,
            weight=60.0,
            description="Parking portico close to main house entry"
        ),
        AdjacencyEdge(
            fromRoom=RoomType.BATHROOM.value,
            toRoom=RoomType.SHAFT.value,
            relationship=AdjacencyRelationshipType.PREFERRED_ADJACENCY,
            weight=90.0,
            description="Wet areas should cluster around plumbing chase / shaft"
        ),
        AdjacencyEdge(
            fromRoom=RoomType.KITCHEN.value,
            toRoom=RoomType.SHAFT.value,
            relationship=AdjacencyRelationshipType.PREFERRED_ADJACENCY,
            weight=85.0,
            description="Kitchen drainage line aligned with MEP service shaft"
        ),

        # Forbidden Adjacencies
        AdjacencyEdge(
            fromRoom=RoomType.KITCHEN.value,
            toRoom=RoomType.BATHROOM.value,
            relationship=AdjacencyRelationshipType.FORBIDDEN_ADJACENCY,
            weight=100.0,
            description="NBC 2016 Part 3: Kitchen shall not open directly into water closet/bathroom"
        ),
        AdjacencyEdge(
            fromRoom=RoomType.KITCHEN.value,
            toRoom=RoomType.TOILET.value,
            relationship=AdjacencyRelationshipType.FORBIDDEN_ADJACENCY,
            weight=100.0,
            description="Kitchen cannot share direct door or opening to toilet"
        ),
        AdjacencyEdge(
            fromRoom=RoomType.PUJA.value,
            toRoom=RoomType.TOILET.value,
            relationship=AdjacencyRelationshipType.FORBIDDEN_ADJACENCY,
            weight=100.0,
            description="Sacred / prayer space must not abut or share wall with toilet"
        ),
        AdjacencyEdge(
            fromRoom=RoomType.PUJA.value,
            toRoom=RoomType.BATHROOM.value,
            relationship=AdjacencyRelationshipType.FORBIDDEN_ADJACENCY,
            weight=100.0,
            description="Puja room shall not share a partition with bathroom"
        ),
        AdjacencyEdge(
            fromRoom=RoomType.ENTRY.value,
            toRoom=RoomType.MASTER_BEDROOM.value,
            relationship=AdjacencyRelationshipType.FORBIDDEN_ADJACENCY,
            weight=90.0,
            description="Master bedroom must have acoustic and visual privacy buffer from entrance"
        ),

        # Privacy Transitions
        AdjacencyEdge(
            fromRoom=RoomType.LIVING.value,
            toRoom=RoomType.BEDROOM.value,
            relationship=AdjacencyRelationshipType.PRIVACY_BUFFER,
            weight=65.0,
            description="Direct visual opening from formal living into private bedroom discouraged"
        ),
    ]

    return RoomAdjacencyGraph(
        graphId="GRAPH-STD-RESIDENTIAL-2026",
        version="2026.1",
        edges=edges,
        metadata={
            "standard": "NBC 2016 Part 3 + Indian Residential Architectural Practice",
            "edgeCount": len(edges)
        }
    )
