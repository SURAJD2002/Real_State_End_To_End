"""
Planwise Enterprise Master Report — Part 3: Sections 12 to 19
12. Computational Geometry Engine
13. Building Envelope Generation
14. Room / Space Model
15. Walls / Doors / Windows / Stairs
16. Architectural Floor Plan Renderer
17. QTO / IS 1200 Measurement Engine
18. BOQ Assembly & Trade Mapping
19. Cost Engine & Waterfall Breakdown
"""

from .common import badge, record_evidence
from .diagrams import diagram_05_manifold3d_geometry

def get_part3_html():
    record_evidence(
        claim="Manifold3D constructive solid geometry with watertight boolean subtractions",
        source_file="workers/geometry/solid_engine.py",
        function_or_class="SolidModelingEngine.create_wall_solid",
        test_file="tests/test_m2_generator_and_solids.py",
        artifact_ref="workers/geometry/solid_engine.py:L64",
        status="IMPLEMENTED"
    )
    record_evidence(
        claim="Dynamic architectural CAD vector rendering with doors, windows, and parametric stairs",
        source_file="apps/web/src/components/CadBlueprintView.tsx",
        function_or_class="CadBlueprintView",
        test_file="tests/test_architectural_renderer_v2.py",
        artifact_ref="artifacts/e2e_live_test/06_1500_floor_plan_detail.png",
        status="VISUALLY VERIFIED"
    )
    record_evidence(
        claim="IS 1200 measurement rules with opening deductions exceeding 0.1 m2 and cost waterfall",
        source_file="workers/qto/measurement_engine.py",
        function_or_class="MEASUREMENT_RULES_REGISTRY",
        test_file="tests/test_m3_qto_and_cost.py",
        artifact_ref="workers/qto/cost_engine.py:L260",
        status="IMPLEMENTED"
    )

    html = r'''
<div class="section-container">
  <!-- SECTION 12 -->
  <h1>12. COMPUTATIONAL GEOMETRY ENGINE (SHAPELY &amp; MANIFOLD3D)</h1>
  <p>Planwise implements a high-performance, two-stage computational geometry kernel:</p>
  <ul>
    <li><strong>2D Topology &amp; Polygon Boundary Kernel:</strong> Built on <strong>Shapely 2.1.2</strong> (backed by GEOS C++). Handles polygon orientation, Minkowski setback offsetting, boolean clipping, and centroid computation [Source: <code>workers/geometry/engine.py</code>].</li>
    <li><strong>3D Constructive Solid Geometry (CSG) Kernel:</strong> Built on <strong>Manifold3D 3.5.4</strong> (libmanifold). Guarantees that every structural wall, floor slab, column, and staircase is represented as a mathematically watertight 2-manifold mesh with zero non-manifold edges, positive volume, and topological invariants [Source: <code>workers/geometry/solid_engine.py</code>].</li>
  </ul>

  [[DIAGRAM_05]]

  <h2>12.1 Constructive Solid Geometry &amp; Boolean Subtractions</h2>
  <p>In traditional CAD systems, punching window and door openings into walls frequently results in degenerate zero-thickness faces, T-junctions, and inverted surface normals. Planwise eliminates this using Manifold3D's exact boolean arithmetic [Source: <code>workers/geometry/solid_engine.py:L104-L140</code>]:</p>

  <pre><code># Base wall solid: length x thickness x height
base_wall = Manifold.cube([wall_len, thickness_m, height_m])
base_wall = base_wall.translate([0.0, -thickness_m / 2.0, 0.0])

# Boolean subtraction: Cutters are scaled 1.5x in thickness to ensure clean manifold intersection
if openings:
    for op in openings:
        cutter_thickness = thickness_m * 1.5
        cutter = Manifold.cube([op_width, cutter_thickness, op_height])
        cutter = cutter.translate([op_dist, -cutter_thickness / 2.0, sill_height])
        base_wall = base_wall - cutter  # CSG Boolean Difference</code></pre>

  <h2>12.2 The 2-Manifold Invariant Proof</h2>
  <p>A solid $\mathcal{M}$ is defined as a valid 2-manifold if and only if every point on its surface has a neighborhood homeomorphic to an open disk in $\mathbb{R}^2$. In discrete mesh representation, this requires:</p>
  <div class="formula-box">
    $$1. \quad \text{Every edge is shared by exactly two triangles (zero boundary edges and zero non-manifold edges)}.$$<br/>
    $$2. \quad \text{Every vertex has a single connected umbrella of adjacent triangles}.$$<br/>
    $$3. \quad \text{The Euler characteristic } \chi = V - E + F = 2(1 - g), \text{ where } g = \text{solid.genus()} \text{ is the topological genus (tunnel count)}.$$
  </div>
  <p>Test suite <code>tests/test_m2_generator_and_solids.py:test_05_manifold3d_wall_solid_with_openings_is_watertight</code> programmatically validates that every compiled wall satisfies Manifold3D status <code>Error.NoError</code>, zero boundary edges, strictly positive volume, and Euler characteristic $\chi = 2(1 - g)$ where $g = \text{solid.genus()}$. Note that door cutouts intersecting the floor slab ($z=0$) form boundary notches rather than through-tunnels ($g=0 \implies \chi=2$), while window cutouts create topological handles ($g=1 \implies \chi=0$).</p>

  <div class="page-break"></div>

  <!-- SECTION 13 -->
  <h1>13. BUILDING ENVELOPE GENERATION</h1>
  <p>A critical requirement of the Planwise platform is that the building envelope must be <strong>dynamically synthesized</strong> from the customer's actual declared plot area rather than copying static templates.</p>

  <h2>13.1 Mathematical Derivation from Declared Area</h2>
  <p>When a customer inputs an arbitrary declared area $A_{\text{declared}}$ in square feet, the system evaluates the envelope dimensions via the following verified 16:9 aspect ratio formulation [Source: <code>workers/generation/house_generator.py:L317-L322</code>]:</p>

  <div class="formula-box">
    Given declared plot area in square feet: $A_{\text{declared}}$<br/>
    Metric area conversion factor: $A_{\text{m}^2} = A_{\text{declared}} \times 0.092903$<br/>
    Aspect ratio derivation (16:9 proportion):<br/>
    $$W_{\text{envelope}} = \text{round}\left(\sqrt{A_{\text{m}^2} \times \frac{16}{9}}, 2\right)$$<br/>
    $$L_{\text{envelope}} = \text{round}\left(\frac{A_{\text{m}^2}}{W_{\text{envelope}}}, 2\right)$$
  </div>

  <h2>13.2 Envelope Divergence Matrix Across Verified Test Plots</h2>
  <table>
    <thead>
      <tr>
        <th style="width: 20%;">Plot Declaration</th>
        <th style="width: 20%;">Metric Area ($A_{\text{plot}}$)</th>
        <th style="width: 20%;">Formula Derivation</th>
        <th style="width: 20%;">Derived $W \times L$</th>
        <th style="width: 20%;">Imperial Dimension</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><strong>1,100 sq ft</strong></td>
        <td>102.19 m²</td>
        <td>$\sqrt{102.19 \times \frac{16}{9}} = 13.48\text{m}$</td>
        <td><strong>13.48m &times; 7.58m</strong></td>
        <td>44'-3" &times; 24'-10"</td>
      </tr>
      <tr>
        <td><strong>1,500 sq ft</strong></td>
        <td>139.35 m²</td>
        <td>$\sqrt{139.35 \times \frac{16}{9}} = 15.74\text{m}$</td>
        <td><strong>15.74m &times; 8.85m</strong></td>
        <td>51'-8" &times; 29'-0"</td>
      </tr>
      <tr>
        <td><strong>2,400 sq ft</strong></td>
        <td>222.97 m²</td>
        <td>$\sqrt{222.97 \times \frac{16}{9}} = 19.91\text{m}$</td>
        <td><strong>19.91m &times; 11.20m</strong></td>
        <td>65'-4" &times; 36'-9"</td>
      </tr>
      <tr>
        <td><strong>10,000 sq ft</strong></td>
        <td>929.03 m²</td>
        <td>$\sqrt{929.03 \times \frac{16}{9}} = 40.64\text{m}$</td>
        <td><strong>40.64m &times; 22.86m</strong></td>
        <td>133'-4" &times; 75'-0"</td>
      </tr>
    </tbody>
  </table>

  <div class="page-break"></div>

  <!-- SECTION 14 -->
  <h1>14. ROOM / SPACE MODEL &amp; NBC 2016 COMPLIANCE</h1>
  <p>The National Building Code of India (NBC 2016 Part 3: Development Control Rules and General Building Requirements) prescribes mandatory minimum carpet areas, clear widths, and heights for residential rooms. Planwise enforces these standards as immutable bounds within the room program [Source: <code>packages/schemas/room_program.py:L40-L115</code>]:</p>

  <table>
    <thead>
      <tr>
        <th style="width: 22%;">Room Typology</th>
        <th style="width: 18%;">NBC 2016 Min Area</th>
        <th style="width: 18%;">NBC Min Width</th>
        <th style="width: 18%;">Clear Height</th>
        <th style="width: 24%;">Statutory Daylight Clause</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><strong>Living / Dining Room</strong></td>
        <td>9.50 m² (102 sq ft)</td>
        <td>2.40 m (7'-10")</td>
        <td>2.75 m (9'-0")</td>
        <td>NBC Part 3 Cl 4.2: Direct Window &ge; 10% carpet area</td>
      </tr>
      <tr>
        <td><strong>Master Bedroom</strong></td>
        <td>9.50 m² (102 sq ft)</td>
        <td>2.40 m (7'-10")</td>
        <td>2.75 m (9'-0")</td>
        <td>NBC Part 3 Cl 4.2: Exterior wall window opening</td>
      </tr>
      <tr>
        <td><strong>Secondary Bedroom</strong></td>
        <td>7.50 m² (81 sq ft)</td>
        <td>2.10 m (6'-11")</td>
        <td>2.75 m (9'-0")</td>
        <td>NBC Part 3 Cl 4.2: Exterior wall window opening</td>
      </tr>
      <tr>
        <td><strong>Kitchen</strong></td>
        <td>4.50 m² (48 sq ft)</td>
        <td>1.80 m (5'-11")</td>
        <td>2.75 m (9'-0")</td>
        <td>NBC Part 3 Cl 4.3: Direct ventilation &ge; 1.0 m²</td>
      </tr>
      <tr>
        <td><strong>Bath / Attached Toilet</strong></td>
        <td>1.80 m² (19 sq ft)</td>
        <td>1.20 m (3'-11")</td>
        <td>2.10 m (6'-11")</td>
        <td>NBC Part 3 Cl 4.4: Shaft / exterior louvre &ge; 0.3 m²</td>
      </tr>
      <tr>
        <td><strong>Staircase Core</strong></td>
        <td>Parametric (L&times;W)</td>
        <td>1.00 m (Flight width)</td>
        <td>2.20 m Headroom</td>
        <td>NBC Part 4 Cl 4.10: Riser &le; 190mm, Tread &ge; 250mm</td>
      </tr>
    </tbody>
  </table>

  <div class="page-break"></div>

  <!-- SECTION 15 -->
  <h1>15. STRUCTURAL ELEMENTS, OPENINGS &amp; STAIRS</h1>
  <p>During CBM compilation [Source: <code>workers/generation/model_compiler.py:L190-L450</code>], discrete room intervals are transformed into physical structural elements:</p>

  <h2>15.1 Structural Wall Generation</h2>
  <ul>
    <li><strong>External Perimeter Walls:</strong> Synthesized along the outer envelope boundary. Thickness: $230\text{ mm}$ ($0.23\text{ m}$) RCC or country brickwork. Role: <code>LOADBEARING</code> / Structural Enclosure [Source: <code>model_compiler.py:L260</code>].</li>
    <li><strong>Internal Partition Walls:</strong> Synthesized along room boundary intersections. Thickness: $115\text{ mm}$ ($0.115\text{ m}$) AAC blockwork. Role: <code>NON_LOADBEARING</code> Partition [Source: <code>model_compiler.py:L285</code>].</li>
  </ul>

  <h2>15.2 Host-Linked Openings</h2>
  <ul>
    <li><strong>Doorway Openings:</strong> Clear width $0.90\text{ m}$ ($3\text{'-}0\text{"}$) for habitable rooms, $0.75\text{ m}$ ($2\text{'-}6\text{"}$) for bathrooms. Standard height: $2.10\text{ m}$ ($7\text{'-}0\text{"}$). Host-linked to supporting wall centerline [Source: <code>model_compiler.py:L350</code>].</li>
    <li><strong>Window Openings:</strong> Clear width $1.20\text{ m}$ to $1.80\text{ m}$, height $1.20\text{ m}$, sill height $0.90\text{ m}$ above finished floor level [Source: <code>model_compiler.py:L390</code>].</li>
  </ul>

  <h2>15.3 Parametric Dog-Legged Staircase</h2>
  <p>For multi-floor houses ($G+1$ duplex), the CBM models a parametric dog-legged reinforced concrete staircase with exact tread/riser calculations [Source: <code>model_compiler.py:L530-L565</code>]:</p>
  <div class="formula-box">
    $$H_{\text{floor}} = 3.15\text{ m} \quad (\text{Structural floor-to-floor height})$$<br/>
    $$N_{\text{risers}} = 18, \quad R = \frac{3.15}{18} = 0.175\text{ m} \quad (175\text{ mm per riser})$$<br/>
    $$T = 0.250\text{ m} \quad (250\text{ mm tread depth}) \implies 2R + T = 2(175) + 250 = 600\text{ mm} \quad (\text{Blondel's Formula Invariant})$$<br/>
    $$\text{Mid-Landing Elevation} = 1.575\text{ m}, \quad \text{Flight Width} = 1.00\text{ m}$$
  </div>

  <div class="page-break"></div>

  <!-- SECTION 16 -->
  <h1>16. ARCHITECTURAL FLOOR PLAN RENDERER</h1>
  <p>The vector floor plan presentation engine is implemented in <code>apps/web/src/components/CadBlueprintView.tsx</code> and <code>FloorPlanViewer.tsx</code>. It consumes the authoritative CBM model and renders an architectural blueprint conforming to professional CAD standards.</p>

  <h2>16.1 Rendering Standards &amp; Graphical Conventions</h2>
  <ul>
    <li><strong>Wall Polygons:</strong> Rendered with exact millimeter-accurate strokes. External walls: thick $1.6\text{pt}$ solid black line with $0.05$ subtle grey fill; Internal partitions: $1.0\text{pt}$ stroke [Source: <code>CadBlueprintView.tsx:L110-L123</code>].</li>
    <li><strong>Doors &amp; Swing Arcs:</strong> Rendered with a solid leaf line representing the door leaf open at 90&deg;, accompanied by a quarter-circle dashed arc line indicating swing trajectory [Source: <code>CadBlueprintView.tsx:L175-L197</code>].</li>
    <li><strong>Architectural Windows:</strong> Rendered as double lines with outer wall cut lines and inner glass pane centerline [Source: <code>CadBlueprintView.tsx:L200-L215</code>].</li>
    <li><strong>Staircase Treads &amp; Direction:</strong> Rendered with parallel step tread lines, solid landing division line, and an arrow pointing in the direction of ascent with the bold annotation <strong>"UP"</strong> [Source: <code>CadBlueprintView.tsx:L125-L167</code>].</li>
    <li><strong>Dimension Strings:</strong> Dimension lines with 45&deg; architectural tick marks, displaying imperial measurements in feet and inches (e.g. <code>38'-9"</code>) and metric equivalents [Source: <code>CadBlueprintView.tsx:L77-L98</code>].</li>
    <li><strong>Furniture Stencils:</strong> Deterministic 2D CAD furniture overlays (beds with pillows, living sofas, kitchen counters, sanitary fixtures) placed strictly within room boundaries [Source: <code>CadBlueprintView.tsx:L274-L306</code>].</li>
    <li><strong>SVG Vector Export:</strong> The browser renders directly to an <code>&lt;svg id="cad-drawing-svg"&gt;</code> element that can be exported directly to standard vector SVG (20,738 bytes verified in live test) [Source: <code>FloorPlanViewer.tsx:L66-L78</code>].</li>
  </ul>

  <div class="callout callout-success">
    <strong>Clarification Regarding Reference Drawings:</strong> The architect PDF previously uploaded to the project was an illustrative <em>visual benchmark</em> for CAD styling. In the current implementation, zero hardcoded 28&times;46 reference geometries exist; all SVG polygons and dimension text are dynamically generated from the live project CBM.
  </div>

  <div class="page-break"></div>

  <!-- SECTION 17 -->
  <h1>17. QUANTITY TAKEOFF (QTO) &amp; IS 1200</h1>
  <p>The Quantity Takeoff Engine [Source: <code>workers/qto/measurement_engine.py</code> and <code>qto_engine.py</code>] extracts physical construction quantities from the CBM adhering strictly to <strong>IS 1200: Indian Standard Method of Measurement of Building and Civil Engineering Works</strong>.</p>

  <h2>17.1 Authoritative Measurement Rules Registry</h2>
  <table>
    <thead>
      <tr>
        <th style="width: 15%;">Rule ID</th>
        <th style="width: 25%;">Standard Clause</th>
        <th style="width: 20%;">Unit &amp; Discipline</th>
        <th style="width: 40%;">Measurement Formula &amp; Deduction Policy</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><code>QTO-WALL-001</code></td>
        <td>IS 1200 Part 3 (Brickwork) Clause 4.1</td>
        <td>m³ (Civil)</td>
        <td>$V = \sum (L \times H \times T) - \sum V_{\text{openings}}$. Strict deduction for all door and window openings $> 0.1\text{ m}^2$.</td>
      </tr>
      <tr>
        <td><code>QTO-SLAB-001</code></td>
        <td>IS 1200 Part 2 (Concrete) Clause 4.2</td>
        <td>m³ (Civil)</td>
        <td>$V = (A_{\text{boundary}} - \sum A_{\text{shafts}}) \times T_{\text{slab}}$. Excludes stairwell voids $> 0.1\text{ m}^2$.</td>
      </tr>
      <tr>
        <td><code>QTO-COL-001</code></td>
        <td>IS 1200 Part 2 (Concrete) Clause 4.4</td>
        <td>m³ (Civil)</td>
        <td>$V = \sum (W_{\text{col}} \times D_{\text{col}} \times H_{\text{clear}})$. Measured clear floor-to-soffit.</td>
      </tr>
      <tr>
        <td><code>QTO-STAIR-001</code></td>
        <td>IS 1200 Part 2 (Concrete) Clause 4.8</td>
        <td>m³ (Civil)</td>
        <td>Waist slab volume $+ (0.5 \times R \times T \times W \times N_{\text{steps}}) +$ Mid-landing volume.</td>
      </tr>
      <tr>
        <td><code>QTO-PLASTER-001</code></td>
        <td>IS 1200 Part 12 (Plastering) Clause 4.2</td>
        <td>m² (Architectural)</td>
        <td>Internal 12mm plaster: Wall faces $+$ ceiling soffits. Openings $> 0.5\text{ m}^2$ deducted with jamb additions.</td>
      </tr>
      <tr>
        <td><code>QTO-TILE-001</code></td>
        <td>IS 1200 Part 11 (Flooring) Clause 3.1</td>
        <td>m² (Finishes)</td>
        <td>Net carpet area of habitable rooms and bathrooms. Measured out-to-out between wall faces.</td>
      </tr>
    </tbody>
  </table>

  <div class="page-break"></div>

  <!-- SECTION 18 & 19 -->
  <h1>18 &amp; 19. BILL OF QUANTITIES &amp; COST ENGINE</h1>
  <p>The Cost Engine [Source: <code>workers/qto/cost_engine.py</code>] binds validated TakeoffRecords to an immutable regional cost rate snapshot (e.g. <code>INDIA-MUMBAI-2026-Q4-V1</code>) to generate an itemized Bill of Quantities (BOQ) and a complete financial waterfall.</p>

  <h2>18.1 Trade Mapping &amp; Rate Snapshot Structure</h2>
  <p>Every takeoff item maps deterministically to a CPWD-aligned trade code and specification [Source: <code>cost_engine.py:L38-L150</code>]:</p>
  <ul>
    <li><code>01 Site / Earthwork:</code> Foundation trench excavation ($₹450 / \text{m}^3$) per CPWD DSR Item 2.8.</li>
    <li><code>02 RCC Structural Works:</code> M25 concrete ($₹7,800 / \text{m}^3$) including Fe500D rebar and shuttering.</li>
    <li><code>03 Masonry:</code> 230mm external brickwork ($₹5,200 / \text{m}^3$) and 115mm internal AAC blockwork ($₹3,600 / \text{m}^3$).</li>
    <li><code>04 Plaster:</code> 12mm internal cement plaster ($₹280 / \text{m}^2$) and 20mm external sand-faced ($₹390 / \text{m}^2$).</li>
    <li><code>05 Flooring:</code> 800&times;800mm vitrified nano-sealed tile flooring ($₹1,650 / \text{m}^2$).</li>
    <li><code>06 Doors &amp; Windows:</code> Engineered flush doors ($₹12,500 / \text{unit}$) and UPVC sliding windows ($₹5,800 / \text{m}^2$).</li>
  </ul>

  <h2>19.1 The Cost Waterfall Formulation</h2>
  <p>The cost calculation executes an immutable mathematical chain [Source: <code>cost_engine.py:L256-L280</code>]:</p>
  <div class="formula-box">
    $$1. \quad \text{Direct Hard Cost: } C_{\text{hard}} = \sum_{k=1}^m (\text{Quantity}_k \times \text{UnitRate}_k)$$<br/>
    $$2. \quad \text{Contractor Prelims & Site Overheads: } C_{\text{prelims}} = \text{round}(C_{\text{hard}} \times 0.08, 2) \quad (8.0\%)$$<br/>
    $$3. \quad \text{Physical Contingency Buffer: } C_{\text{contingency}} = \text{round}(C_{\text{hard}} \times 0.05, 2) \quad (5.0\%)$$<br/>
    $$4. \quad \text{Construction Subtotal: } S = C_{\text{hard}} + C_{\text{prelims}} + C_{\text{contingency}}$$<br/>
    $$5. \quad \text{Statutory Goods & Services Tax (GST): } T = \text{round}(S \times 0.18, 2) \quad (18.0\% \text{ if applicable})$$<br/>
    $$6. \quad \text{Total Estimated Construction Cost: } C_{\text{total}} = S + T$$
  </div>

  <h2>19.2 Sample Verification Calculation (1,500 sq ft Project)</h2>
  <table>
    <thead>
      <tr>
        <th style="width: 40%;">Waterfall Stage</th>
        <th style="width: 25%;">Basis / Rate</th>
        <th style="width: 35%;">Calculated Amount (INR)</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td>Direct Hard Construction Cost</td>
        <td>Sum of all 16 BOQ Line Items</td>
        <td><strong>₹31,45,200.00</strong></td>
      </tr>
      <tr>
        <td>Contractor Prelims &amp; Site Overheads</td>
        <td>8.0% on Hard Cost</td>
        <td>₹2,51,616.00</td>
      </tr>
      <tr>
        <td>Physical Contingency Buffer</td>
        <td>5.0% on Hard Cost</td>
        <td>₹1,57,260.00</td>
      </tr>
      <tr>
        <td><strong>Subtotal Construction Cost</strong></td>
        <td>Hard Cost + Prelims + Contingency</td>
        <td><strong>₹35,54,076.00</strong></td>
      </tr>
      <tr>
        <td>Statutory GST</td>
        <td>18.0% on Subtotal</td>
        <td>₹6,39,733.68</td>
      </tr>
      <tr>
        <td><strong>Total Construction Cost (Incl. Tax)</strong></td>
        <td>Gross Project Cost</td>
        <td><strong>₹41,93,809.68</strong></td>
      </tr>
      <tr>
        <td><strong>Cost per sq ft BUA</strong></td>
        <td>Total Cost / 1,500 sq ft</td>
        <td><strong>₹2,795.87 / sq ft</strong></td>
      </tr>
    </tbody>
  </table>
</div>
'''
    html = html.replace('[[DIAGRAM_05]]', diagram_05_manifold3d_geometry())
    return html

print("Part 3 module loaded.")
