"""
Planwise Enterprise — buildingSMART IFC Classification Reference Engine
Milestone 1 — BIM / IFC Professionalization
Conforms to ISO 16739-1:2024 / buildingSMART IfcClassificationReference specification.
Maps canonical building elements to international Uniclass 2015 tables deterministically.
"""

from typing import List, Dict, Any, Tuple
from workers.release.ifc_guid import generate_deterministic_ifc_guid


# Deterministic Uniclass 2015 product codes for building elements
UNICLASS_2015_TABLE: Dict[str, Dict[str, str]] = {
    "WALL_AAC": {
        "identification": "Pr_20_85_12_02",
        "name": "Autoclaved aerated concrete block units"
    },
    "CONCRETE_STRUCTURAL": {
        "identification": "Pr_20_85_16_40",
        "name": "In situ concrete"
    },
    "DOOR_SET": {
        "identification": "Pr_30_59_24",
        "name": "Door sets"
    },
    "WINDOW_SET": {
        "identification": "Pr_30_59_98",
        "name": "Window sets"
    }
}


class IFCClassificationBuilder:
    """Serializes IfcClassification, IfcClassificationReference, and associates with elements."""

    def __init__(self, release_id: str, owner_history_id: int = 2):
        self.release_id = release_id
        self.owner_history_id = owner_history_id

    def build_classification_system(self, start_entity_id: int) -> Tuple[List[str], int, int]:
        """
        Builds the root IFCCLASSIFICATION entity for Uniclass 2015.
        Returns:
            (lines, classification_entity_id, next_entity_id)
        """
        lines = []
        curr_id = start_entity_id

        # #id=IFCCLASSIFICATION('NBS','2015',$,'Uniclass 2015','Uniclass 2015 Classification Table','https://www.thenbs.com/our-tools/uniclass-2015',$);
        class_id = curr_id
        lines.append(
            f"#{class_id}=IFCCLASSIFICATION('NBS','2015',$,'Uniclass 2015',"
            f"'Uniclass 2015 Classification System','https://www.thenbs.com/our-tools/uniclass-2015',$);"
        )
        curr_id += 1
        return lines, class_id, curr_id

    def build_classification_reference(
        self,
        key: str,
        system_entity_id: int,
        start_entity_id: int
    ) -> Tuple[List[str], int, int]:
        """
        Builds an IFCCLASSIFICATIONREFERENCE entity for a Uniclass item.
        """
        lines = []
        curr_id = start_entity_id

        info = UNICLASS_2015_TABLE.get(key, UNICLASS_2015_TABLE["WALL_AAC"])
        ref_id = curr_id
        lines.append(
            f"#{ref_id}=IFCCLASSIFICATIONREFERENCE($,'{info['identification']}',"
            f"'{info['name']}',#{system_entity_id},$,$);"
        )
        curr_id += 1
        return lines, ref_id, curr_id

    def associate_classification(
        self,
        element_ids: List[int],
        reference_entity_id: int,
        element_tag: str,
        start_entity_id: int
    ) -> Tuple[List[str], int]:
        """
        Associates one or more elements with an IFCCLASSIFICATIONREFERENCE
        using IFCRELASSOCIATESCLASSIFICATION.
        """
        lines = []
        curr_id = start_entity_id

        elem_refs = ",".join([f"#{eid}" for eid in element_ids])
        rel_guid = generate_deterministic_ifc_guid(self.release_id, f"REL_CLASS_{element_tag}")
        lines.append(
            f"#{curr_id}=IFCRELASSOCIATESCLASSIFICATION('{rel_guid}',#{self.owner_history_id},"
            f"$,$,({elem_refs}),#{reference_entity_id});"
        )
        curr_id += 1
        return lines, curr_id
