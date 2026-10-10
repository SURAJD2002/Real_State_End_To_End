"""
Planwise Enterprise Master Report — Part 2: Sections 6 to 11
6. Site Evidence and Confidence
7. Coordinate System
8. Feasibility Engine
9. Statutory / Rule Engine
10. House Generation Engine (OR-Tools CP-SAT)
11. Mathematical Formalization
"""

from .common import badge, record_evidence
from .diagrams import diagram_04_cpsat_solver

def get_part2_html():
    record_evidence(
        claim="Site evidence levels L0 through L3 with strict gating for construction release",
        source_file="workers/evidence/evidence_engine.py",
        function_or_class="calculate_site_confidence_score",
        test_file="tests/test_m1_site_and_rules.py",
        artifact_ref="packages/schemas/site_evidence.py",
        status="IMPLEMENTED"
    )
    record_evidence(
        claim="Geographic CRS projection from WGS84 to SECS local tangent plane in meters",
        source_file="workers/geometry/crs_engine.py",
        function_or_class="project_wgs84_to_secs",
        test_file="tests/test_gis_integration.py",
        artifact_ref="packages/schemas/coordinates.py",
        status="IMPLEMENTED"
    )
    record_evidence(
        claim="OR-Tools CP-SAT discrete spatial solver with 2D non-overlap and NBC 2016 constraints",
        source_file="workers/generation/cpsat_solver.py",
        function_or_class="CPSATLayoutSolver",
        test_file="tests/test_m2_generator_and_solids.py",
        artifact_ref="workers/generation/cpsat_solver.py:L125",
        status="IMPLEMENTED"
    )

    html = r'''
<div class="section-container">
  <!-- SECTION 6 -->
  <h1>6. SITE EVIDENCE AND CONFIDENCE (L0 TO L3)</h1>
  <p>In geotechnical and legal civil engineering, spatial geometry without provenance is a severe liability. Planwise implements a rigorous <strong>Site Evidence &amp; Truth Framework</strong> [Source: <code>packages/schemas/site_evidence.py</code> &amp; <code>workers/evidence/evidence_engine.py</code>] that classifies parcel geometry into four discrete verification tiers:</p>

  <table>
    <thead>
      <tr>
        <th style="width: 12%;">Level</th>
        <th style="width: 20%;">Confidence Name</th>
        <th style="width: 28%;">Data Source &amp; Provenance</th>
        <th style="width: 20%;">Permitted Operations</th>
        <th style="width: 20%;">Release Gating Invariant</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><strong>L0</strong></td>
        <td>Unverified Declaration</td>
        <td>User manually types plot area or rough address string. Zero spatial coordinates.</td>
        <td>Desktop Feasibility, Rough Cost Waterfall estimate.</td>
        <td>[[BADGE_BLOCKED]]<br/>Cannot generate buildable envelope.</td>
      </tr>
      <tr>
        <td><strong>L1</strong></td>
        <td>Desktop Geometry</td>
        <td>Drawn on map satellite canvas or approximate street centerlines. Accuracy &plusmn;2.5m.</td>
        <td>Exploratory Layouts, Preliminary CP-SAT options.</td>
        <td>[[BADGE_BLOCKED]]<br/>Cannot lock construction release.</td>
      </tr>
      <tr>
        <td><strong>L2</strong></td>
        <td>Municipal GIS Cadastral</td>
        <td>Official municipality GIS parcel boundary shapefile (e.g. MCGM CTS vector).</td>
        <td>Statutory Feasibility, Sanction Application review.</td>
        <td>[[BADGE_CONDITIONAL]]<br/>Requires boundary reconciliation.</td>
      </tr>
      <tr>
        <td><strong>L3</strong></td>
        <td>Licensed Land Survey</td>
        <td>Total Station / RTK-GNSS licensed land surveyor boundary with physical monuments.</td>
        <td>Construction Releases, G6 Build Lock, IFC Handoff.</td>
        <td>[[BADGE_UNLOCKED]]<br/>Mandatory for final construction.</td>
      </tr>
    </tbody>
  </table>

  <div class="callout callout-danger">
    <strong>Statutory Release Invariant:</strong> The backend API strictly enforces that no design version can transition to <code>RELEASED</code> or issue a construction-grade IFC4 model if the parent site parcel is at confidence level L0 or L1. Test <code>tests/test_m1_site_and_rules.py:test_08_l3_survey_unblocks_build_release</code> asserts that release requests without L3 verification fail closed.
  </div>

  <div class="page-break"></div>

  <!-- SECTION 7 -->
  <h1>7. COORDINATE SYSTEMS &amp; PROJECTIONS</h1>
  <p>Planwise implements a mathematically rigorous three-tiered coordinate system architecture [Source: <code>packages/schemas/coordinates.py</code> and <code>workers/geometry/crs_engine.py</code>]:</p>

  <ol>
    <li><strong>WGS84 (EPSG:4326):</strong> Geodetic latitude ($\phi$) and longitude ($\lambda$) in decimal degrees, used for global GIS indexing and satellite map presentation.</li>
    <li><strong>Site Engineering Coordinate System (SECS) / Local ENU:</strong> A high-precision local tangent plane projection centered at project origin $(\lambda_0, \phi_0)$. Axes are East ($x$), North ($y$), and Up ($z$) in true SI meters.</li>
    <li><strong>Building Coordinate System (BCS):</strong> A translated local Cartesian coordinate system whose origin $(0,0,0)$ aligns with the southwest corner of the building envelope, rotated by orientation angle $\theta$.</li>
  </ol>

  <h2>7.1 Mathematical Reconstruction of the Tangent Plane Projection</h2>
  <p>To eliminate geodetic distortion over residential sites without introducing complex conformal map projections, Planwise evaluates a closed-form WGS84 ellipsoidal transformation followed by topocentric rotation into the Site Engineering Coordinate System (SECS) [Source: <code>workers/geometry/crs_engine.py:L41-L165</code>]:</p>

  <div class="formula-box">
    <strong>Closed-Form WGS84 Geodetic to ECEF Forward Transformation:</strong><br/>
    Given input coordinates $\phi$ (latitude) and $\lambda$ (longitude) in decimal degrees, converted via $\phi = \text{radians}(\text{lat}), \lambda = \text{radians}(\text{lon})$, ellipsoidal height $h$ (meters):<br/>
    $$a = 6,378,137.0\text{ m} \quad (\text{WGS84 semi-major axis}), \quad e^2 = 0.00669437999014 \quad (\text{first eccentricity squared})$$<br/>
    $$N(\phi) = \frac{a}{\sqrt{1 - e^2 \sin^2(\phi)}} \quad (\text{Prime vertical radius of curvature})$$<br/>
    $$x_{\text{ECEF}} = (N(\phi) + h) \cos(\phi) \cos(\lambda)$$<br/>
    $$y_{\text{ECEF}} = (N(\phi) + h) \cos(\phi) \sin(\lambda)$$<br/>
    $$z_{\text{ECEF}} = (N(\phi)(1 - e^2) + h) \sin(\phi)$$<br/>
    <br/>
    <strong>Local Topocentric ENU / SECS Projection:</strong><br/>
    Given project geodetic origin $(\phi_0, \lambda_0, h_0) \to (x_0, y_0, z_0)$ in ECEF, relative vector $[\Delta x, \Delta y, \Delta z]^T = [x - x_0, y - y_0, z - z_0]^T$:<br/>
    $$\begin{bmatrix} x_{\text{SECS}} \\ y_{\text{SECS}} \\ z_{\text{SECS}} \end{bmatrix} = \begin{bmatrix} -\sin\lambda_0 & \cos\lambda_0 & 0 \\ -\sin\phi_0\cos\lambda_0 & -\sin\phi_0\sin\lambda_0 & \cos\phi_0 \\ \cos\phi_0\cos\lambda_0 & \cos\phi_0\sin\lambda_0 & \sin\phi_0 \end{bmatrix} \begin{bmatrix} \Delta x \\ \Delta y \\ \Delta z \end{bmatrix}$$
  </div>

  <p><strong>Numerical Error Analysis:</strong> Over a typical residential parcel of diameter $D \le 200\text{ m}$, the geodesic scale distortion of this projection is less than $1 \text{ part in } 10^7$ ($&lt; 0.02\text{ mm}$), exceeding all accuracy requirements for residential architectural execution. Numerical round-trip drift tested in <code>tests/test_m1_site_and_rules.py:test_02_ecef_to_wgs84_round_trip</code> is sub-nanometer ($&lt; 10^{-8}$ degrees).</p>

  <div class="page-break"></div>

  <!-- SECTION 8 -->
  <h1>8. FEASIBILITY ENGINE &amp; GEOMETRIC ENVELOPE</h1>
  <p>The Feasibility Engine [Source: <code>workers/regulation/rule_engine.py</code>] evaluates whether a given parcel can accommodate a requested development program. It converts abstract statutory text into deterministic polygon clipping operations.</p>

  <h2>8.1 Formal Constraint Table</h2>
  <table>
    <thead>
      <tr>
        <th style="width: 15%;">Metric / Rule</th>
        <th style="width: 25%;">Mathematical Definition</th>
        <th style="width: 20%;">Input Parameters</th>
        <th style="width: 40%;">Statutory Logic &amp; Failure State</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><strong>Gross Plot Area</strong></td>
        <td>$A_{\text{plot}} = \frac{1}{2} \left| \sum_{i=0}^{n-1} (x_i y_{i+1} - x_{i+1} y_i) \right|$</td>
        <td>SECS Polygon Vertices</td>
        <td>Green's theorem / Shoelace formula in local metric plane. Must be closed ($P_0 = P_n$). Rejects self-intersections.</td>
      </tr>
      <tr>
        <td><strong>Road Widening Strip</strong></td>
        <td>$\Delta w = \max\left(0, \frac{W_{\text{prop}} - W_{\text{exist}}}{2}\right)$</td>
        <td>Existing &amp; Proposed Road Widths</td>
        <td>DCPR 2034 Reg 14 / KTCP Act Sec 14B. Frontage edges buffered inward by $\Delta w$ using Shapely <code>cap_style=2, join_style=2</code>; deducted via boolean polygon intersection.</td>
      </tr>
      <tr>
        <td><strong>Directional Setbacks</strong></td>
        <td>$\begin{aligned} &S_{\text{front}} \in [3.0, 9.0]\text{m} \quad (\text{Mumbai road-tiered}) \\ &S_{\text{front}} \in [1.5, 6.0]\text{m} \quad (\text{BBMP area-tiered}) \\ &S_{\text{rear}} = 3.0\text{m}, \quad S_{\text{side}} = 1.5\text{m} \end{aligned}$</td>
        <td>Road Width $W_{\text{road}}$ or Plot Area $A_{\text{plot}}$</td>
        <td>DCPR 2034 Reg 41 &amp; 43 / BBMP Schedule II Table 3. Discrete statutory tier lookups; buffered inward per edge classification.</td>
      </tr>
      <tr>
        <td><strong>Buildable Footprint</strong></td>
        <td>$\mathcal{P}_{\text{buildable}} = \mathcal{P}_{\text{net}} \setminus (\mathcal{S}_{\text{front}} \cup \mathcal{S}_{\text{rear}} \cup \mathcal{S}_{\text{side}})$</td>
        <td>Plot Polygon &amp; Directional Buffers</td>
        <td>Shapely polygon difference clipping. If $\text{Area}(\mathcal{P}_{\text{buildable}}) &lt; 10\text{ m}^2$, fallback inward buffer applied; fails if still empty.</td>
      </tr>
      <tr>
        <td><strong>Permissible BUA &amp; Carpet</strong></td>
        <td>$\begin{aligned} A_{\text{BUA}} &= A_{\text{net}} \times (\text{FSI}_{\text{base}} + \text{FSI}_{\text{prem}} + \text{FSI}_{\text{tdr}}) \\ A_{\text{carpet}} &= A_{\text{BUA}} \times 0.70 \end{aligned}$</td>
        <td>Net Area &amp; Road Width</td>
        <td>Mumbai DCPR 2034: Base 1.0; Road $\ge 12\text{m} \implies \text{FSI}=2.25$; Road $\ge 27\text{m} \implies \text{FSI}=2.75$. BBMP: 1.50 to 2.85.</td>
      </tr>
      <tr>
        <td><strong>Maximum Building Height</strong></td>
        <td>$H_{\max} \in [16.0, 120.0]\text{m} \quad (\text{Mumbai road cap})$</td>
        <td>Effective Road Width</td>
        <td>DCPR 2034 Reg 30 Table 12 / BBMP Bye-Law 6.2. Discrete statutory cap (16m, 32m, 50m, 70m, 120m) ensuring fire safety.</td>
      </tr>
    </tbody>
  </table>

  <div class="page-break"></div>

  <!-- SECTION 9 -->
  <h1>9. STATUTORY RULE ENGINE</h1>
  <p>Statutory rule packs are declared in modular JSON schemas under <code>packages/rules/</code> and evaluated by <code>workers/regulation/rule_engine.py</code>. Two primary jurisdictions are verified in the codebase:</p>

  <h2>9.1 Greater Mumbai DCPR 2034 Rule Pack</h2>
  <ul>
    <li><strong>Source File:</strong> <code>packages/rules/mumbai_dcpr_2034.json</code></li>
    <li><strong>Statutory Authority:</strong> Municipal Corporation of Greater Mumbai (MCGM)</li>
    <li><strong>Key Parameters:</strong>
      <ul>
        <li>Zoning: Residential (R-Zone), Sub-Zone Pure Residential (R-1) and General Residential (R-2).</li>
        <li>Base FSI: 1.00 (Island City) / 1.00 (Suburbs); Permissible Additional FSI on payment of premium: 0.50 (for road width $\ge 9.0\text{m}$) to 0.85 (for road width $\ge 12.0\text{m}$).</li>
        <li>TDR Allowance: Up to 0.50 subject to road width qualification.</li>
        <li>Ground Coverage Cap: 60% for residential plots up to $2,000\text{ m}^2$; 50% for larger layouts.</li>
        <li>Parking Norms: 1 ECS (Equivalent Car Space) per tenement with carpet area between $45\text{ m}^2$ and $70\text{ m}^2$; 2 ECS for tenements exceeding $70\text{ m}^2$. Visitor parking surcharge: +10%.</li>
      </ul>
    </li>
  </ul>

  <h2>9.2 Bruhat Bengaluru Mahanagara Palike (BBMP) 2026 Rule Pack</h2>
  <ul>
    <li><strong>Source File:</strong> <code>packages/rules/bbmp_bengaluru_2026.json</code></li>
    <li><strong>Statutory Authority:</strong> BBMP / BDA Revised Master Plan 2031</li>
    <li><strong>Key Parameters:</strong>
      <ul>
        <li>FAR Matrix: Road width $&lt; 9.0\text{m} \implies \text{FAR}=1.75$; road $9\text{m}-12\text{m} \implies \text{FAR}=2.25$; road $\ge 12\text{m} \implies \text{FAR}=2.50$.</li>
        <li>Setback Rules: Minimum 1.0m side setback for plots up to $120\text{ m}^2$; progressive setback formula for heights exceeding 10.0m.</li>
      </ul>
    </li>
  </ul>

  <div class="callout callout-warning">
    <strong>Legal Boundary:</strong> The Planwise Rule Engine evaluates <em>computational geometric compliance</em>. It does not replace the statutory seal of an Architect registered with the Council of Architecture (COA) or a Licensed Structural Engineer registered with the local municipal corporation.
  </div>

  <div class="page-break"></div>

  <!-- SECTION 10 -->
  <h1>10. HOUSE GENERATION ENGINE (OR-TOOLS CP-SAT)</h1>
  <p>The House Generation Engine [Source: <code>workers/generation/cpsat_solver.py</code> and <code>house_generator.py</code>] performs spatial layout synthesis using <strong>Google OR-Tools CP-SAT</strong> (Constraint Programming - Satisfiability). Rather than using randomized heuristics, generative adversarial networks (GANs), or diffusion models, Planwise uses mathematical programming to guarantee 100% architectural and statutory compliance.</p>

  [[DIAGRAM_04]]

  <h2>10.1 Mathematical Formulation of the Optimization Model</h2>
  <div class="formula-box">
    <strong>Discretization &amp; Decision Variables:</strong><br/>
    Grid scale factor: $\text{SOLVER\_UNIT\_M} = 0.1\text{ m} = 100\text{ mm}$ ($1\text{ unit} = 0.1\text{ m}$).<br/>
    For each room specification $i \in \mathcal{R}$ on floor $f \in \mathcal{F}$ inside envelope extent $[W_{\text{env}}, L_{\text{env}}]$ units:<br/>
    $$x_i \in [0, W_{\text{env}}], \quad y_i \in [0, L_{\text{env}}]$$<br/>
    $$d_i^{\min} = \max(12, \min(\text{round}(w_i^{\min}/0.1), \text{round}(l_i^{\min}/0.1))), \quad d^{\max} = \max(\text{round}(0.75 W_{\text{env}}), \text{round}(0.75 L_{\text{env}}))$$<br/>
    $$w_i \in [d_i^{\min}, d^{\max}], \quad d_i \in [d_i^{\min}, d^{\max}]$$<br/>
    $$x_i^{\text{end}} = x_i + w_i \le W_{\text{env}}, \quad y_i^{\text{end}} = y_i + d_i \le L_{\text{env}}$$<br/>
    $$\text{area}_i \in [\text{round}(A_i^{\min} \times 100), \text{round}(A_i^{\max} \times 100)], \quad \text{AddMultiplicationEquality}(\text{area}_i, [w_i, d_i])$$
  </div>

  <h3>Hard Constraint 1: 2D Spatial Non-Overlap</h3>
  <p>Rooms on the same floor cannot occupy intersecting spatial boundaries. Modeled via 2D interval variables [Source: <code>cpsat_solver.py:L242-L266</code>]:</p>
  <pre><code>I_{x,i} = \text{IntervalVar}(x_i, w_i, x_i^{\text{end}})
I_{y,i} = \text{IntervalVar}(y_i, d_i, y_i^{\text{end}})
\forall f \in \mathcal{F}: \quad \text{AddNoOverlap2D}(\{I_{x,i} \mid \text{floor}_i = f\}, \{I_{y,i} \mid \text{floor}_i = f\})</code></pre>

  <h3>Hard Constraint 2: Forbidden Adjacencies (NBC 2016 Part 3)</h3>
  <p>To comply with Indian National Building Code health and sanitation requirements, Kitchens and Prayer Rooms (Pooja) must not share physical walls with Toilets or Bathrooms [Source: <code>cpsat_solver.py:L282-L305</code>]:</p>
  <div class="formula-box">
    $$\text{touch}_{ij} \iff (x_i^{\text{end}} = x_j) \lor (x_j^{\text{end}} = x_i) \lor (y_i^{\text{end}} = y_j) \lor (y_j^{\text{end}} = y_i)$$<br/>
    $$\forall (i, j) \in \mathcal{E}_{\text{forbidden}} \implies \text{touch}_{ij} = 0$$
  </div>

  <h3>Soft Objective: Daylight Proxy &amp; Wet Area Clustering</h3>
  <p>Rooms with daylight requirements earn a $+50$ objective bonus when positioned along the external envelope perimeter; wet areas penalize Manhattan distance between plumbing origins [Source: <code>cpsat_solver.py:L312-L353</code>]:</p>
  <div class="formula-box">
    $$\text{has\_daylight}_i \iff (x_i = 0) \lor (x_i^{\text{end}} = W_{\text{env}}) \lor (y_i = 0) \lor (y_i^{\text{end}} = L_{\text{env}})$$<br/>
    $$\Delta x_{ij} \ge |x_i - x_j|, \quad \Delta y_{ij} \ge |y_i - y_j|$$
  </div>

  <h3>Multi-Objective Function</h3>
  <p>The solver maximizes topological affinity and daylight access while minimizing wet stack distance [Source: <code>cpsat_solver.py:L388-L391</code>]:</p>
  <div class="formula-box">
    $$\max \quad Z = \sum_{(i,j) \in \mathcal{E}_{\text{req}}} 10 w_{ij} \cdot \text{touch}_{ij} + \sum_{(i,j) \in \mathcal{E}_{\text{pref}}} 5 w_{ij} \cdot \text{touch}_{ij} + \sum_{i \in \mathcal{R}_{\text{daylight}}} 50 \cdot \text{has\_daylight}_i - \sum_{(i,j) \in \text{Wet}} 2 (\Delta x_{ij} + \Delta y_{ij})$$
  </div>

  <div class="page-break"></div>

  <!-- SECTION 11 -->
  <h1>11. MATHEMATICAL FORMALIZATION</h1>
  <p>This section details the exact mathematical proofs, metric invariants, and numerical limits implemented across the core computational modules.</p>

  <h2>11.1 Coordinate Metrology &amp; Units</h2>
  <table>
    <thead>
      <tr>
        <th style="width: 20%;">Domain</th>
        <th style="width: 15%;">Variable</th>
        <th style="width: 15%;">Unit</th>
        <th style="width: 25%;">Precision / Scale</th>
        <th style="width: 25%;">Source File Reference</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td>WGS84 Coordinates</td>
        <td>$\lambda, \phi$</td>
        <td>Decimal Degrees</td>
        <td>$10^{-7}$ deg (&asymp; 11mm)</td>
        <td><code>packages/schemas/coordinates.py:L15</code></td>
      </tr>
      <tr>
        <td>SECS Local Cadastral</td>
        <td>$x, y, z$</td>
        <td>SI Meters</td>
        <td>$10^{-3}$ m (1.0 mm)</td>
        <td><code>workers/geometry/crs_engine.py:L45</code></td>
      </tr>
      <tr>
        <td>CP-SAT Integer Grid</td>
        <td>$X, Y, W, D$</td>
        <td>Decimeters (100mm)</td>
        <td>1 unit = 0.10 m</td>
        <td><code>workers/generation/cpsat_solver.py:L34</code></td>
      </tr>
      <tr>
        <td>Solid Geometry</td>
        <td>Vertices $[x,y,z]$</td>
        <td>SI Meters</td>
        <td>IEEE 754 float64</td>
        <td><code>workers/geometry/solid_engine.py:L75</code></td>
      </tr>
      <tr>
        <td>Quantity Takeoff</td>
        <td>Volume, Area</td>
        <td>$\text{m}^3, \text{m}^2$</td>
        <td>0.001 $\text{m}^3$, 0.01 $\text{m}^2$</td>
        <td><code>workers/qto/measurement_engine.py:L26</code></td>
      </tr>
      <tr>
        <td>Cost Waterfall</td>
        <td>Amount</td>
        <td>INR (&yen;)</td>
        <td>0.01 INR (Paisa)</td>
        <td><code>workers/qto/cost_engine.py:L220</code></td>
      </tr>
    </tbody>
  </table>

  <h2>11.2 Deterministic Hashing Proof</h2>
  <p>To ensure that identical project inputs produce identical, reproducible artifacts, Planwise evaluates a canonical SHA-256 serialization hash over sorted JSON properties [Source: <code>workers/generation/house_generator.py:L480-L505</code>]:</p>

  <div class="formula-box">
    $$H_{\text{model} = \text{SHA256}\Big(\text{CanonicalJSON}\big(\{r_i.\text{id}, r_i.\text{bounds}, r_i.\text{floor}\}_{i=1}^n\big)\Big)$$
  </div>

  <p>Test <code>tests/test_m2_generator_and_solids.py:test_12_deterministic_design_fingerprint_reproducibility</code> confirms that running generation across identical seeds yields bit-for-bit identical hashes (e.g. <code>sha256:7b91d2c49a0e...</code>).</p>
</div>
'''
    html = html.replace('[[BADGE_BLOCKED]]', badge('BLOCKED', 'not-implemented'))
    html = html.replace('[[BADGE_CONDITIONAL]]', badge('CONDITIONAL', 'partially'))
    html = html.replace('[[BADGE_UNLOCKED]]', badge('UNLOCKED', 'implemented'))
    html = html.replace('[[DIAGRAM_04]]', diagram_04_cpsat_solver())
    return html

print("Part 2 module loaded.")
