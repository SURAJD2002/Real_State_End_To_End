# ARCHITECTURAL FLOOR PLAN RENDERER AUDIT

## 1. Source of Truth
**FAIL.** The rendered floor plan in the default mode (`blueprintSource === 'REFERENCE_28X46'`) is 100% hardcoded to match the visual reference image. It does not derive its geometry from the Canonical Building Model (CBM) or the actual project layout. While there is a `DYNAMIC_CBM` branch, it is not the default, and even within the dynamic branch, critical architectural elements like doors, furniture, stairs, and interior partition walls are placed using hardcoded relative offsets rather than actual CBM elements (e.g. doors always placed at `rx + 8, ry`).

## 2. Hardcoded Reference Values Found
**FAIL.** The following values are hardcoded in `CadBlueprintView.tsx` as default rendering logic:
- Building envelope: 28' x 46'
- Dimension strings: 28', 46', 36', 10', 11'-6", 16'-6"
- Room sizes and coordinates:
  - BED ROOM 12'-0"x10'-4"
  - TOILET 12'-6"x5'-0"
  - TOILET 7'-6"x5'-0"
  - KITCHEN 8'-4"x6'-4"
  - HALL 12'-6"x11'-0"
  - BED ROOM 12'-0"x10'-0"
  - BED ROOM 12'-6"x10'-0"

## 3. Dynamic Geometry Verification
**FAIL.** The default viewer relies entirely on the hardcoded reference. If switched to `DYNAMIC_CBM`, it generates room boxes but fails to derive actual door placements, stair geometry, or detailed architectural linework from the CBM. Furniture is deterministically injected based on room names (e.g. `room.name.includes('bed')`) rather than parsed from the model.

## 4. CBM Traceability
**FAIL.** SVG elements (walls, rooms, doors) lack `data-cbm-id` attributes connecting them to the canonical model. They are purely visual artifacts mapped from `layout.rooms` (in the dynamic branch) but lack deep traceability for individual architectural primitives like openings and walls.

## 5. 1100 sq ft Test
**FAIL.** Renders the hardcoded 28' x 46' (1,288 sq ft) reference layout if the default mode is used. When using the dynamic mode, it renders boxes but not a fully integrated architectural floor plan.

## 6. 10,000 sq ft Test
**FAIL.** Renders the hardcoded 28' x 46' layout. The dynamic mode handles scale but fails to render a detailed architectural drawing (just boxes with a compass and basic door arcs).

## 7. 2BHK → 3BHK Mutation Test
**FAIL.** In default mode, the layout remains a static 3BHK.

## 8. Dimension Mutation Test
**FAIL.** Changing a bedroom dimension does not update adjacent geometry properly in the dynamic mode (rooms can overlap), and has zero effect in the default mode.

## 9. SVG Validation
**PASS.** The SVG exported from both modes is structurally valid XML, but it exports the hardcoded geometry rather than the real project geometry in default mode.

## 10. PDF Validation
**FAIL.** The PDF simply wraps the SVG output; since the SVG geometry is flawed/hardcoded, the PDF inherits these flaws.

## 11. Screenshots
*N/A - the dynamic floor plan tests failed due to hardcoded defaults, meaning materially different projects render either as identical hardcoded diagrams or as broken dynamic boxes.*

---

## FINAL STATUS
**ARCHITECTURAL_RENDERER_BLOCKED**

**Reason:** The implementation prioritized visually matching the reference PDF over building a genuine architectural CAD renderer derived from the Canonical Building Model. The reference image was treated as Planwise geometry rather than a visual benchmark. The frontend must be refactored to consume CBM geometry (walls, spaces, openings, slabs) and trace them accurately, rather than relying on deterministic UI overlays and hardcoded SVG elements.
