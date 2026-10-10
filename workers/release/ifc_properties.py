"""
Planwise Enterprise — buildingSMART IFC Property Sets Engine
Milestone 1 — BIM / IFC Professionalization
Conforms to ISO 16739-1:2024 / buildingSMART Property Set Definitions (PSD).
Generates Pset_WallCommon, Pset_ConcreteElementGeneral, Pset_SlabCommon,
Pset_DoorCommon, and Pset_WindowCommon mapped strictly from CBM attributes.
"""

from typing import List, Dict, Any, Tuple
from workers.release.ifc_guid import generate_deterministic_ifc_guid


class IFCPropertySetBuilder:
    """Compiles standard buildingSMART property sets bound to IFC elements."""

    def __init__(self, release_id: str, owner_history_id: int = 2):
        self.release_id = release_id
        self.owner_history_id = owner_history_id

    def build_wall_properties(
        self,
        elem: Any,
        wall_entity_id: int,
        start_entity_id: int
    ) -> Tuple[List[str], int]:
        """
        Builds Pset_WallCommon for IfcWall.
        Properties: LoadBearing, IsExternal, NominalThickness, Reference.
        """
        lines = []
        curr_id = start_entity_id

        # 1. Properties
        is_loadbearing = getattr(elem, "structuralRole", None)
        lb_val = ".T." if (hasattr(is_loadbearing, "value") and is_loadbearing.value in ["LOADBEARING", "PRIMARY_FRAME"]) or str(is_loadbearing) in ["LOADBEARING", "PRIMARY_FRAME"] else ".F."
        p_lb = curr_id
        lines.append(f"#{p_lb}=IFCPROPERTYSINGLEVALUE('LoadBearing',$,IFCBOOLEAN({lb_val}),$);")
        curr_id += 1

        w_type = getattr(elem, "wallType", None)
        is_ext = ".T." if (hasattr(w_type, "value") and w_type.value == "EXTERNAL") or str(w_type) == "EXTERNAL" or (getattr(elem.geometry, "thicknessM", 0.0) or 0.0) >= 0.20 else ".F."
        p_ext = curr_id
        lines.append(f"#{p_ext}=IFCPROPERTYSINGLEVALUE('IsExternal',$,IFCBOOLEAN({is_ext}),$);")
        curr_id += 1

        thk = (getattr(elem.geometry, "thicknessM", None) if hasattr(elem, "geometry") else None) or 0.20
        p_thk = curr_id
        lines.append(f"#{p_thk}=IFCPROPERTYSINGLEVALUE('NominalThickness',$,IFCLENGTHMEASURE({float(thk):.3f}),$);")
        curr_id += 1

        p_ref = curr_id
        lines.append(f"#{p_ref}=IFCPROPERTYSINGLEVALUE('Reference',$,IFCIDENTIFIER('{elem.elementId}'),$);")
        curr_id += 1

        prop_refs = f"(#{p_lb},#{p_ext},#{p_thk},#{p_ref})"

        # Optional properties from elem.properties
        props = getattr(elem, "properties", {}) or {}
        if "fireRating" in props:
            p_fr = curr_id
            lines.append(f"#{p_fr}=IFCPROPERTYSINGLEVALUE('FireRating',$,IFCLABEL('{props['fireRating']}'),$);")
            curr_id += 1
            prop_refs = prop_refs[:-1] + f",#{p_fr})"

        if "acousticRating" in props:
            p_ar = curr_id
            lines.append(f"#{p_ar}=IFCPROPERTYSINGLEVALUE('AcousticRating',$,IFCLABEL('{props['acousticRating']}'),$);")
            curr_id += 1
            prop_refs = prop_refs[:-1] + f",#{p_ar})"

        # 2. IFCPROPERTYSET
        pset_id = curr_id
        pset_guid = generate_deterministic_ifc_guid(self.release_id, f"PSET_WALL_{elem.elementId}")
        lines.append(f"#{pset_id}=IFCPROPERTYSET('{pset_guid}',#{self.owner_history_id},'Pset_WallCommon',$,{prop_refs});")
        curr_id += 1

        # 3. IFCRELDEFINESBYPROPERTIES
        rel_id = curr_id
        rel_guid = generate_deterministic_ifc_guid(self.release_id, f"REL_PSET_WALL_{elem.elementId}")
        lines.append(f"#{rel_id}=IFCRELDEFINESBYPROPERTIES('{rel_guid}',#{self.owner_history_id},$,$,(#{wall_entity_id}),#{pset_id});")
        curr_id += 1

        return lines, curr_id

    def build_column_properties(
        self,
        elem: Any,
        col_entity_id: int,
        start_entity_id: int
    ) -> Tuple[List[str], int]:
        """
        Builds Pset_ConcreteElementGeneral for IfcColumn.
        Properties: StrengthClass, ConstructionType.
        """
        lines = []
        curr_id = start_entity_id

        # 1. Properties
        mat_id = str(getattr(elem, "materialId", "RCC_M25_FE500"))
        strength = "M25" if "M25" in mat_id else ("M30" if "M30" in mat_id else "M20")
        p_str = curr_id
        lines.append(f"#{p_str}=IFCPROPERTYSINGLEVALUE('StrengthClass',$,IFCLABEL('{strength}'),$);")
        curr_id += 1

        p_ctype = curr_id
        lines.append(f"#{p_ctype}=IFCPROPERTYSINGLEVALUE('ConstructionType',$,IFCLABEL('In-situ'),$);")
        curr_id += 1

        prop_refs = f"(#{p_str},#{p_ctype})"

        # 2. IFCPROPERTYSET
        pset_id = curr_id
        pset_guid = generate_deterministic_ifc_guid(self.release_id, f"PSET_COL_{elem.elementId}")
        lines.append(f"#{pset_id}=IFCPROPERTYSET('{pset_guid}',#{self.owner_history_id},'Pset_ConcreteElementGeneral',$,{prop_refs});")
        curr_id += 1

        # 3. IFCRELDEFINESBYPROPERTIES
        rel_id = curr_id
        rel_guid = generate_deterministic_ifc_guid(self.release_id, f"REL_PSET_COL_{elem.elementId}")
        lines.append(f"#{rel_id}=IFCRELDEFINESBYPROPERTIES('{rel_guid}',#{self.owner_history_id},$,$,(#{col_entity_id}),#{pset_id});")
        curr_id += 1

        return lines, curr_id

    def build_slab_properties(
        self,
        elem: Any,
        slab_entity_id: int,
        start_entity_id: int
    ) -> Tuple[List[str], int]:
        """
        Builds Pset_SlabCommon for IfcSlab.
        """
        lines = []
        curr_id = start_entity_id

        p_lb = curr_id
        lines.append(f"#{p_lb}=IFCPROPERTYSINGLEVALUE('LoadBearing',$,IFCBOOLEAN(.T.),$);")
        curr_id += 1

        is_roof = "roof" in elem.elementId.lower() or "terrace" in str(getattr(elem, "name", "")).lower()
        is_ext = ".T." if is_roof else ".F."
        p_ext = curr_id
        lines.append(f"#{p_ext}=IFCPROPERTYSINGLEVALUE('IsExternal',$,IFCBOOLEAN({is_ext}),$);")
        curr_id += 1

        p_pitch = curr_id
        lines.append(f"#{p_pitch}=IFCPROPERTYSINGLEVALUE('PitchAngle',$,IFCPLANEANGLEMEASURE(0.),$);")
        curr_id += 1

        prop_refs = f"(#{p_lb},#{p_ext},#{p_pitch})"

        pset_id = curr_id
        pset_guid = generate_deterministic_ifc_guid(self.release_id, f"PSET_SLAB_{elem.elementId}")
        lines.append(f"#{pset_id}=IFCPROPERTYSET('{pset_guid}',#{self.owner_history_id},'Pset_SlabCommon',$,{prop_refs});")
        curr_id += 1

        rel_id = curr_id
        rel_guid = generate_deterministic_ifc_guid(self.release_id, f"REL_PSET_SLAB_{elem.elementId}")
        lines.append(f"#{rel_id}=IFCRELDEFINESBYPROPERTIES('{rel_guid}',#{self.owner_history_id},$,$,(#{slab_entity_id}),#{pset_id});")
        curr_id += 1

        return lines, curr_id

    def build_door_properties(
        self,
        opening: Any,
        door_entity_id: int,
        start_entity_id: int
    ) -> Tuple[List[str], int]:
        """Builds Pset_DoorCommon for IfcDoor."""
        lines = []
        curr_id = start_entity_id

        p_w = curr_id
        lines.append(f"#{p_w}=IFCPROPERTYSINGLEVALUE('OverallWidth',$,IFCLENGTHMEASURE({float(opening.widthM):.3f}),$);")
        curr_id += 1

        p_h = curr_id
        lines.append(f"#{p_h}=IFCPROPERTYSINGLEVALUE('OverallHeight',$,IFCLENGTHMEASURE({float(opening.heightM):.3f}),$);")
        curr_id += 1

        prop_refs = f"(#{p_w},#{p_h})"

        pset_id = curr_id
        pset_guid = generate_deterministic_ifc_guid(self.release_id, f"PSET_DOOR_{opening.openingId}")
        lines.append(f"#{pset_id}=IFCPROPERTYSET('{pset_guid}',#{self.owner_history_id},'Pset_DoorCommon',$,{prop_refs});")
        curr_id += 1

        rel_id = curr_id
        rel_guid = generate_deterministic_ifc_guid(self.release_id, f"REL_PSET_DOOR_{opening.openingId}")
        lines.append(f"#{rel_id}=IFCRELDEFINESBYPROPERTIES('{rel_guid}',#{self.owner_history_id},$,$,(#{door_entity_id}),#{pset_id});")
        curr_id += 1

        return lines, curr_id

    def build_window_properties(
        self,
        opening: Any,
        window_entity_id: int,
        start_entity_id: int
    ) -> Tuple[List[str], int]:
        """Builds Pset_WindowCommon for IfcWindow."""
        lines = []
        curr_id = start_entity_id

        p_ext = curr_id
        lines.append(f"#{p_ext}=IFCPROPERTYSINGLEVALUE('IsExternal',$,IFCBOOLEAN(.T.),$);")
        curr_id += 1

        p_w = curr_id
        lines.append(f"#{p_w}=IFCPROPERTYSINGLEVALUE('OverallWidth',$,IFCLENGTHMEASURE({float(opening.widthM):.3f}),$);")
        curr_id += 1

        p_h = curr_id
        lines.append(f"#{p_h}=IFCPROPERTYSINGLEVALUE('OverallHeight',$,IFCLENGTHMEASURE({float(opening.heightM):.3f}),$);")
        curr_id += 1

        prop_refs = f"(#{p_ext},#{p_w},#{p_h})"

        pset_id = curr_id
        pset_guid = generate_deterministic_ifc_guid(self.release_id, f"PSET_WIN_{opening.openingId}")
        lines.append(f"#{pset_id}=IFCPROPERTYSET('{pset_guid}',#{self.owner_history_id},'Pset_WindowCommon',$,{prop_refs});")
        curr_id += 1

        rel_id = curr_id
        rel_guid = generate_deterministic_ifc_guid(self.release_id, f"REL_PSET_WIN_{opening.openingId}")
        lines.append(f"#{rel_id}=IFCRELDEFINESBYPROPERTIES('{rel_guid}',#{self.owner_history_id},$,$,(#{window_entity_id}),#{pset_id});")
        curr_id += 1

        return lines, curr_id
