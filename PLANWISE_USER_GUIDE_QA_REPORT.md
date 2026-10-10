# PLANWISE ENTERPRISE — USER GUIDE QA REPORT
**Document Reference:** User Guide Quality Assurance, Defect Reconciliation & Content Audit
**Date of Audit:** October 9, 2026
**Auditor:** Senior Product Documentation & Technical Verification Architect

---

## 1. Executive Summary

This Quality Assurance (QA) Report records the forensic documentation inspection conducted on the *Planwise Enterprise User Guide*. Following the strict **Zero-Fabrication Policy**, every instruction, UI button label, workflow transition, mathematical equation, and troubleshooting step was checked against the running codebase and verified artifacts.

---

## 2. Contradictions Discovered & Reconciled

During the audit of the forensic master report and UI components, several documentation discrepancies and historical assumptions were identified. In all cases, the User Guide has been corrected to reflect the **actual code implementation**:

| Discrepancy ID | Historical Documentation / PDF Claim | Actual Inspected Code Implementation | Resolution in User Guide |
|---|---|---|---|
| **QA-DISC-01** | Section 7 of forensic PDF claimed SECS coordinates were computed from radians while multiplying by $\pi/180$. | `workers/geometry/crs_engine.py:L41-L165` takes **decimal degrees**, converts via `math.radians()`, and evaluates closed-form ellipsoidal WGS84 $\to$ ECEF $\to$ ENU transformation. | Guide explains that users enter standard latitude/longitude decimal degrees or address strings, which the engine converts directly without manual angle manipulation. |
| **QA-DISC-02** | Section 13 claimed the building envelope for 1,500 sq ft was $10.0\text{m} \times 13.94\text{m}$ based on $60\%$ coverage. | `workers/generation/house_generator.py:L317-L322` derives a 16:9 proportional envelope: $W = \text{round}(\sqrt{A_{\text{m}^2} \times 16/9}, 2) = 15.74\text{m}$, $L = 8.85\text{m}$. | Guide uses the verified $15.74\text{m} \times 8.85\text{m}$ ($51\text{'-}8\text{"} \times 29\text{'-}0\text{"}$) envelope dimensions in Chapter 3, 6, and 7. |
| **QA-DISC-03** | Marketing and architectural benchmark PDF referenced a static 28' $\times$ 46' sample drawing. | Frontend CAD viewer renders dynamic SVG blueprints directly from the project's live CBM Pydantic model (`apps/web/src/components/CadBlueprintView.tsx`). | Guide explicitly warns that the 28' $\times$ 46' PDF was merely a styling benchmark, and demonstrates dynamic generation across 1,100, 1,500, 2,400, and 10,000 sq ft. |
| **QA-DISC-04** | Section 12 claimed wall solids satisfy $\chi = 2(1 - n_{\text{openings}})$. | When door cutouts touch the floor slab ($z=0$), they form boundary notches, preserving topological genus $g=0$ ($\chi=2$). Window cutouts create handles ($g=1, \chi=0$). | Guide accurately explains Manifold3D watertight solid validation without false topological oversimplifications. |
| **QA-DISC-05** | Previous technical documentation implied native multi-tenant user authentication and PostgreSQL Row-Level Security (RLS) were active. | The current prototype runs as a single-tenant local web application with an in-memory dictionary cache (`PROJECTS_DB` in `apps/api-gateway/main.py`). | Guide clearly states that authentication, user registration, and multi-tenant organization management are **not implemented in the current prototype**, and all projects share the local API session. |

---

## 3. Unsupported Features Removed / Explicitly Gated

The following features were reviewed and intentionally excluded from customer operating instructions because they are not yet supported by the active software:

1. **User Login / Organization Signup:** Omitted. Documented that accessing `http://localhost:5173` immediately loads the active project workspace.
2. **Automated Municipal Portal Submission:** Omitted. The platform produces downloadable compliance dossiers and IFC4 files, but does NOT integrate directly with municipal portals (e.g. MCGM AutoDCR or BBMP Suvarna).
3. **Structural Finite Element Analysis (FEA):** Omitted. Preliminary column placement is rule-based; structural sizing requires licensed engineering analysis outside the platform.
4. **Dynamic MEP Pipe/Conduit Routing:** Omitted. The system outputs preliminary fixture counts and plumbing stacks, not 3D spatial pipe routing.
5. **Geotechnical Borehole Ingestion:** Omitted. Foundation depths are calculated using default empirical bearing assumptions ($150\text{ kN/m}^2$).

---

## 4. Visual Evidence Audit

All 13 visual figures embedded in the User Guide were audited against the files in `artifacts/e2e_live_test/`:
- **Resolution:** Uniform $1440 \times 960$ desktop browser viewports.
- **Color Space:** 8-bit RGB, non-interlaced PNG.
- **Source:** Captured autonomously by Google Chrome v144 during live end-to-end execution of `scripts/live_frontend_e2e.js`.
- **Integrity:** Zero AI-generated images; zero synthetic mockups; all timestamps and project IDs match live runs (`proj-mumbai-real-1100`, `proj-cust-*`).

---

## 5. Mathematical & Terminology Invariant Audit

The guide adheres strictly to verified architectural and financial definitions:
- **Plot Area:** The declared boundary extent ($A_{\text{plot}}$ in sq ft and $\text{m}^2$).
- **Road Widening Surrender:** Statutory land deduction ($\Delta w = \max(0, (W_{\text{prop}} - W_{\text{exist}})/2)$).
- **Net Developable Area:** $A_{\text{net}} = A_{\text{plot}} - A_{\text{widening}}$.
- **Buildable Envelope:** Net parcel geometry less statutory directional setbacks ($\mathcal{P}_{\text{net}} \setminus \mathcal{S}_{\text{setbacks}}$).
- **Gross Built-Up Area (BUA):** Total covered floor area across all levels ($A_{\text{net}} \times \text{FSI}$).
- **Usable Carpet Area:** Usable floor area measured between internal wall faces ($\approx 70\%$ of BUA per RERA definitions).
- **Cost Waterfall:**
  $$\text{Direct Hard Cost} \xrightarrow{+8\%} \text{Prelims} \xrightarrow{+5\%} \text{Contingency} \xrightarrow{\text{Subtotal}} \xrightarrow{+18\%} \text{GST} \xrightarrow{=} \text{Turnkey Total}$$
  The guide **never** divides total cost by plot area to report a fake "cost per sq ft". All square-foot rates are explicitly based on **Gross Built-Up Area (BUA)**.

---

## 6. QA Certification

I hereby certify that the *Planwise Enterprise User Guide* reflects the exact state of the software as of October 9, 2026. All actions described can be executed by a user interacting with the current web interface and API gateway.

*Signed,*
**Senior Product Documentation & Technical Verification Architect**
Planwise Enterprise Engineering Verification Group
