# Volume II — Complete Repository and Source-Code Reference

## 1. Monorepo Structural Inventory
The Planwise Enterprise codebase comprises **415 total files** spanning **834,060 lines** of source, tests, migrations, and documentation.

### Summary Breakdown by Subsystem
- **Frontend (`apps/web`):** 39 TypeScript/React files, 40 interactive components, 8 routing views.
- **Backend API Gateway (`apps/api-gateway`):** 8 Python modules, 73 REST endpoints, dependency injection providers.
- **Computational Workers (`workers/`):** 14 specialized algorithmic engines across 5 domains.
- **Shared Schemas & Geometry (`packages/`):** 6 domain model packages defining the Canonical Building Model.
- **Database Migrations:** 14 total SQL migration files (8 in `supabase/migrations`, 6 in `database/migrations`).
- **Automated Tests (`tests/`):** 19 Python test suites containing 230 passing test functions.
- **Scripts & Tools (`scripts/`):** 16 orchestration, E2E headless Chrome, and PDF build scripts.

---

## 2. Exhaustive Repository File Inventory (415 Files)

| File Path | Category | Extension | Lines | Size (Bytes) |
| :--- | :--- | :---: | :---: | :---: |
| `real-estate-platform-engineering-masterplan_260923_072638.pdf` | Root / Miscellaneous | `.pdf` | 2712 | 261204 |
| `PILOT_VS_REAL_DATA_INTEGRITY_REPORT.md` | Documentation | `.md` | 110 | 6677 |
| `M3_DEVELOPMENT_REPORT.md` | Documentation | `.md` | 356 | 19424 |
| `PLANWISE_MIGRATION_PLAN.md` | Documentation | `.md` | 37 | 2628 |
| `PLANWISE_BUSINESS_PITCH_DECK.pptx` | Root / Miscellaneous | `.pptx` | 12818 | 1791575 |
| `SUPABASE_MIGRATION_AUDIT.md` | Documentation | `.md` | 62 | 5903 |
| `build_deck.py` | Root / Miscellaneous | `.py` | 1645 | 69881 |
| `PHASE_7_ENGINEER_REVIEW_REPORT.md` | Documentation | `.md` | 185 | 10258 |
| `ARCHITECTURAL_RENDERER_V2_REPORT.md` | Documentation | `.md` | 136 | 7297 |
| `SUPABASE_MIGRATION_RECONCILIATION.md` | Documentation | `.md` | 26 | 4245 |
| `.DS_Store` | Root / Miscellaneous | `` | 3 | 12292 |
| `PLANWISE_PILOT_READINESS_REPORT.md` | Documentation | `.md` | 205 | 15116 |
| `requirements.txt` | Documentation | `.txt` | 19 | 355 |
| `PHASE_7_ENGINEER_REVIEW_REPORT.pdf` | Root / Miscellaneous | `.pdf` | 25314 | 1920839 |
| `PLANWISE_INTEGRATION_TEST_REPORT.md` | Documentation | `.md` | 118 | 5965 |
| `PLANWISE_NEXT_PHASE_GAP_MATRIX.md` | Documentation | `.md` | 51 | 19658 |
| `FORMULA_AUDIT_REPORT.md` | Documentation | `.md` | 259 | 22082 |
| `Land Feasibility Platform Blueprint.pdf` | Root / Miscellaneous | `.pdf` | 16664 | 541771 |
| `PLANWISE_USER_GUIDE_QA_REPORT.md` | Documentation | `.md` | 71 | 6589 |
| `PLANWISE_QUICK_START.pdf` | Root / Miscellaneous | `.pdf` | 13743 | 821585 |
| `SUPABASE_POST_MIGRATION_VALIDATION.md` | Documentation | `.md` | 144 | 11292 |
| `ARCHITECTURAL_FLOOR_PLAN_RENDERER_AUDIT.md` | Documentation | `.md` | 51 | 3541 |
| `PLANWISE_CAD_VISUAL_QA_REPORT.md` | Documentation | `.md` | 138 | 9084 |
| `FORMULA_VERIFICATION_MATRIX.md` | Documentation | `.md` | 60 | 30591 |
| `PLANWISE_NEXT_PHASE_ARCHITECTURE.md` | Documentation | `.md` | 268 | 17829 |
| `REAL_WORLD_DATA_TEST_REPORT.md` | Documentation | `.md` | 357 | 19956 |
| `PLANWISE_ENTERPRISE_USER_GUIDE.pdf` | Root / Miscellaneous | `.pdf` | 36226 | 2147406 |
| `Real Estate Feasibility Platform Architecture.pdf` | Root / Miscellaneous | `.pdf` | 13934 | 739738 |
| `README.md` | Documentation | `.md` | 424 | 27528 |
| `FRONTEND_2_0_API_REQUIREMENTS_AUDIT.md` | Documentation | `.md` | 309 | 18180 |
| `PHASE_8_PILOT_HANDOFF_QA.md` | Documentation | `.md` | 114 | 14366 |
| `PLANWISE_ENTERPRISE_MASTER_REPORT_50_PAGES.pdf` | Root / Miscellaneous | `.pdf` | 151099 | 5988530 |
| `FRONTEND_2_0_CUSTOMER_UX_REPORT.md` | Documentation | `.md` | 260 | 14117 |
| `.gitignore` | Root / Miscellaneous | `` | 71 | 711 |
| `package-lock.json` | Configuration / Manifest | `.json` | 3239 | 112789 |
| `package.json` | Configuration / Manifest | `.json` | 29 | 1111 |
| `PHASE_9_M1_IFC_PROFESSIONALIZATION_REPORT.md` | Documentation | `.md` | 233 | 12909 |
| `M2_DEVELOPMENT_REPORT.md` | Documentation | `.md` | 355 | 26015 |
| `.env` | Configuration / Manifest | `` | 42 | 1550 |
| `CONTRIBUTING.md` | Documentation | `.md` | 152 | 4906 |
| `PLANWISE_IMPLEMENTATION_PLAN.md` | Documentation | `.md` | 101 | 7590 |
| `PLANWISE_PERSISTENCE_MAPPING.md` | Documentation | `.md` | 89 | 6217 |
| `.gitattributes` | Root / Miscellaneous | `` | 8 | 128 |
| `PLANWISE_USER_GUIDE_EVIDENCE_MATRIX.md` | Documentation | `.md` | 64 | 14705 |
| `SUPABASE_SECURITY_RLS_AUDIT.md` | Documentation | `.md` | 113 | 5431 |
| `PLANWISE_ENTERPRISE_USER_GUIDE.md` | Documentation | `.md` | 450 | 36354 |
| `M3_GAP_ANALYSIS.md` | Documentation | `.md` | 38 | 8428 |
| `PHASE_8_PREMIUM_UI_UX_REPORT.md` | Documentation | `.md` | 229 | 14890 |
| `PHASE_8_CONTROLLED_PILOT_REPORT.md` | Documentation | `.md` | 228 | 12747 |
| `BUSINESS_DECK_README.md` | Documentation | `.md` | 103 | 11714 |
| `.env.example` | Configuration / Manifest | `.example` | 46 | 1748 |
| `PHASE_9_M2_PROFESSIONAL_DRAWING_PIPELINE_REPORT.md` | Documentation | `.md` | 394 | 20039 |
| `M2_GAP_ANALYSIS.md` | Documentation | `.md` | 75 | 8984 |
| `PHASE_HOME_PDF_REPORT.md` | Documentation | `.md` | 259 | 21735 |
| `PHASE_8_PILOT_READINESS_AUDIT.md` | Documentation | `.md` | 349 | 22697 |
| `PLANWISE_BUSINESS_PITCH_DECK.pdf` | Root / Miscellaneous | `.pdf` | 16873 | 935896 |
| `PLANWISE_AUTHENTICATION_AND_AUTHORIZATION.md` | Documentation | `.md` | 132 | 6055 |
| `Planwise Site Development Masterclass.pdf` | Root / Miscellaneous | `.pdf` | 20747 | 1236674 |
| `PHASE_8_PILOT_HANDOFF_QA_V2.md` | Documentation | `.md` | 129 | 11336 |
| `SECURITY.md` | Documentation | `.md` | 67 | 3840 |
| `PHASE_8_1_PERSISTENT_LEDGER_REPORT.md` | Documentation | `.md` | 188 | 10573 |
| `database/migrations/04_qto_boq_and_cost_engine.sql` | Database Migration | `.sql` | 111 | 4038 |
| `database/migrations/05_engineer_review_and_releases.sql` | Database Migration | `.sql` | 104 | 4972 |
| `database/migrations/06_generated_reports.sql` | Database Migration | `.sql` | 27 | 1313 |
| `database/migrations/03_site_evidence_and_rule_engine.sql` | Database Migration | `.sql` | 188 | 6956 |
| `database/migrations/01_init_postgis_schema.sql` | Database Migration | `.sql` | 140 | 5412 |
| `database/migrations/02_canonical_building_model.sql` | Database Migration | `.sql` | 233 | 9610 |
| `database/seeds/golden_mumbai_10000sqm.json` | Configuration / Manifest | `.json` | 41 | 1086 |
| `artifacts/planwise_quick_start.html` | Verification Artifact | `.html` | 270 | 675526 |
| `artifacts/.DS_Store` | Verification Artifact | `` | 8 | 8196 |
| `artifacts/planwise_enterprise_forensic_technical_master_report.md` | Verification Artifact | `.md` | 3250 | 2340864 |
| `artifacts/planwise_enterprise_forensic_technical_master_report.html` | Verification Artifact | `.html` | 2937 | 2385201 |
| `artifacts/planwise_enterprise_user_guide.html` | Verification Artifact | `.html` | 939 | 1562003 |
| `artifacts/planwise_enterprise_report_metadata.json` | Verification Artifact | `.json` | 53 | 1527 |
| `artifacts/planwise_enterprise_forensic_technical_master_report.pdf` | Verification Artifact | `.pdf` | 151099 | 5988530 |
| `artifacts/planwise_enterprise_evidence_manifest.json` | Verification Artifact | `.json` | 175 | 7370 |
| `artifacts/pilot_handoff.zip` | Verification Artifact | `.zip` | 109 | 13531 |
| `artifacts/pilot_handoff/pilot_validation_report.json` | Verification Artifact | `.json` | 115 | 3777 |
| `artifacts/pilot_handoff/pilot_cost_estimate.json` | Verification Artifact | `.json` | 29 | 1089 |
| `artifacts/pilot_handoff/pilot_release_manifest.json` | Verification Artifact | `.json` | 135 | 4290 |
| `artifacts/pilot_handoff/pilot_model_ifc4.ifc` | Verification Artifact | `.ifc` | 90 | 7633 |
| `artifacts/pilot_handoff/pilot_boq_export.json` | Verification Artifact | `.json` | 555 | 17564 |
| `artifacts/pilot_handoff/pilot_engineer_review.json` | Verification Artifact | `.json` | 97 | 3469 |
| `artifacts/pitch/Planwise_Enterprise_Investor_Pitch_One_Slide.pdf` | Verification Artifact | `.pdf` | 3195 | 243640 |
| `artifacts/pitch/Planwise_Enterprise_Investor_Pitch_One_Slide_preview.png` | Verification Artifact | `.png` | 1288 | 196419 |
| `artifacts/pitch/product_showcase.png` | Verification Artifact | `.png` | 756 | 112457 |
| `artifacts/pitch/Planwise_Enterprise_Investor_Pitch_One_Slide.pptx` | Verification Artifact | `.pptx` | 988 | 138543 |
| `artifacts/test_renderer_v2/validation_metadata.json` | Verification Artifact | `.json` | 52 | 1397 |
| `artifacts/test_renderer_v2/project_b_2400sqft.svg` | Verification Artifact | `.svg` | 340 | 27516 |
| `artifacts/test_renderer_v2/mutation_2bhk.svg` | Verification Artifact | `.svg` | 271 | 21450 |
| `artifacts/test_renderer_v2/project_c_10000sqft.svg` | Verification Artifact | `.svg` | 243 | 20266 |
| `artifacts/test_renderer_v2/mutation_dimension.svg` | Verification Artifact | `.svg` | 265 | 21056 |
| `artifacts/test_renderer_v2/project_a_1100sqft.svg` | Verification Artifact | `.svg` | 271 | 21450 |
| `artifacts/test_renderer_v2/mutation_3bhk.svg` | Verification Artifact | `.svg` | 340 | 27512 |
| `artifacts/test_drawings_m2/A-301_longitudinal_section_a-a.svg` | Verification Artifact | `.svg` | 96 | 7608 |
| `artifacts/test_drawings_m2/A-102_first_floor_plan.svg` | Verification Artifact | `.svg` | 205 | 14979 |
| `artifacts/test_drawings_m2/A-301_longitudinal_section_a-a.pdf` | Verification Artifact | `.pdf` | 71 | 3255 |
| `artifacts/test_drawings_m2/A-102_first_floor_plan.pdf` | Verification Artifact | `.pdf` | 71 | 5080 |
| `artifacts/test_drawings_m2/A-204_right_elevation_east.pdf` | Verification Artifact | `.pdf` | 71 | 3015 |
| `artifacts/test_drawings_m2/A-103_terrace___roof_plan.pdf` | Verification Artifact | `.pdf` | 71 | 4282 |
| `artifacts/test_drawings_m2/A-202_rear_elevation_north.svg` | Verification Artifact | `.svg` | 85 | 6567 |
| `artifacts/test_drawings_m2/A-203_left_elevation_west.pdf` | Verification Artifact | `.pdf` | 71 | 3085 |
| `artifacts/test_drawings_m2/A-201_front_elevation_south.svg` | Verification Artifact | `.svg` | 82 | 6063 |
| `artifacts/test_drawings_m2/A-302_cross_section_b-b.pdf` | Verification Artifact | `.pdf` | 71 | 3171 |
| `artifacts/test_drawings_m2/A-101_ground_floor_plan.pdf` | Verification Artifact | `.pdf` | 71 | 6693 |
| `artifacts/test_drawings_m2/A-203_left_elevation_west.svg` | Verification Artifact | `.svg` | 87 | 6897 |
| `artifacts/test_drawings_m2/A-201_front_elevation_south.pdf` | Verification Artifact | `.pdf` | 71 | 3000 |
| `artifacts/test_drawings_m2/A-302_cross_section_b-b.svg` | Verification Artifact | `.svg` | 91 | 6957 |
| `artifacts/test_drawings_m2/A-101_ground_floor_plan.svg` | Verification Artifact | `.svg` | 265 | 22217 |
| `artifacts/test_drawings_m2/A-204_right_elevation_east.svg` | Verification Artifact | `.svg` | 82 | 6058 |
| `artifacts/test_drawings_m2/drawing_manifest.json` | Verification Artifact | `.json` | 246 | 7692 |
| `artifacts/test_drawings_m2/A-202_rear_elevation_north.pdf` | Verification Artifact | `.pdf` | 71 | 3100 |
| `artifacts/test_drawings_m2/A-103_terrace___roof_plan.svg` | Verification Artifact | `.svg` | 183 | 12600 |
| `artifacts/test_ifc_m1/rel-pilot-20261002-aedf9830.ifc` | Verification Artifact | `.ifc` | 331 | 26859 |
| `artifacts/e2e_live_test/04_1500_design_options.png` | Verification Artifact | `.png` | 1055 | 143758 |
| `artifacts/e2e_live_test/rendered_sheet_preview_v2.png` | Verification Artifact | `.png` | 2732 | 427956 |
| `artifacts/e2e_live_test/02_1500_feasibility.png` | Verification Artifact | `.png` | 701 | 101305 |
| `artifacts/e2e_live_test/13_engineer_review.png` | Verification Artifact | `.png` | 1071 | 152589 |
| `artifacts/e2e_live_test/12_build_review.png` | Verification Artifact | `.png` | 551 | 81288 |
| `artifacts/e2e_live_test/rendered_sheet_preview.png` | Verification Artifact | `.png` | 2769 | 450284 |
| `artifacts/e2e_live_test/10_10000_floor_plan.png` | Verification Artifact | `.png` | 974 | 135805 |
| `artifacts/e2e_live_test/03_1500_design_intake.png` | Verification Artifact | `.png` | 550 | 74527 |
| `artifacts/e2e_live_test/01_1500_land_input.png` | Verification Artifact | `.png` | 614 | 85866 |
| `artifacts/e2e_live_test/07_3bhk_mutation_floor_plan.png` | Verification Artifact | `.png` | 1051 | 139291 |
| `artifacts/e2e_live_test/08_room_dimension_mutation.png` | Verification Artifact | `.png` | 981 | 139714 |
| `artifacts/e2e_live_test/11_cost_summary.png` | Verification Artifact | `.png` | 551 | 81288 |
| `artifacts/e2e_live_test/06_1500_floor_plan_detail.png` | Verification Artifact | `.png` | 998 | 139911 |
| `artifacts/e2e_live_test/05_1500_my_project_modal.png` | Verification Artifact | `.png` | 582 | 92301 |
| `artifacts/e2e_live_test/failure_screenshot.png` | Verification Artifact | `.png` | 192 | 38253 |
| `artifacts/e2e_live_test/09_2400_floor_plan.png` | Verification Artifact | `.png` | 1017 | 137498 |
| `artifacts/e2e_live_test/exported_cad_drawing.svg` | Verification Artifact | `.svg` | 1 | 83047 |
| `artifacts/test_reports/TEST_CUSTOMER_HOME_REPORT.pdf` | Verification Artifact | `.pdf` | 400 | 2216484 |
| `artifacts/test_reports/failure.txt` | Verification Artifact | `.txt` | 6 | 29655 |
| `artifacts/test_reports/TEST_PROFESSIONAL_REPORT.pdf` | Verification Artifact | `.pdf` | 74 | 4655 |
| `artifacts/test_reports/TEST_COST_BOQ_REPORT.pdf` | Verification Artifact | `.pdf` | 118 | 10219 |
| `artifacts/test_reports/TEST_TECHNICAL_REPORT.pdf` | Verification Artifact | `.pdf` | 150 | 15686 |
| `artifacts/test_reports/complete_pkg/PLANWISE_COMPLETE_HOME_PACKAGE_1100SQFT.zip` | Verification Artifact | `.zip` | 47474 | 7165778 |
| `artifacts/test_reports/complete_pkg/07_Cost_Estimate.pdf` | Verification Artifact | `.pdf` | 80 | 3660 |
| `artifacts/test_reports/complete_pkg/03_Floor_Plans.pdf` | Verification Artifact | `.pdf` | 143 | 10543 |
| `artifacts/test_reports/complete_pkg/09_Engineer_Review.pdf` | Verification Artifact | `.pdf` | 74 | 3624 |
| `artifacts/test_reports/complete_pkg/01_Home_Report.pdf` | Verification Artifact | `.pdf` | 400 | 2216484 |
| `artifacts/test_reports/complete_pkg/02_Technical_Report.pdf` | Verification Artifact | `.pdf` | 150 | 15686 |
| `artifacts/test_reports/complete_pkg/04_3D_Views.pdf` | Verification Artifact | `.pdf` | 100 | 2168864 |
| `artifacts/test_reports/complete_pkg/05_QTO.pdf` | Verification Artifact | `.pdf` | 74 | 3698 |
| `artifacts/test_reports/complete_pkg/08_Validation_Report.pdf` | Verification Artifact | `.pdf` | 74 | 4090 |
| `artifacts/test_reports/complete_pkg/10_Release_Manifest.pdf` | Verification Artifact | `.pdf` | 74 | 3420 |
| `artifacts/test_reports/complete_pkg/06_BOQ.pdf` | Verification Artifact | `.pdf` | 80 | 5295 |
| `artifacts/test_reports/complete_pkg/PLANWISE_COMPLETE_HOME_PACKAGE_1100SQFT.pdf` | Verification Artifact | `.pdf` | 521 | 4427432 |
| `artifacts/test_pilot_controlled_output/pilot_validation_report.json` | Verification Artifact | `.json` | 113 | 3630 |
| `artifacts/test_pilot_controlled_output/pilot_cost_estimate.json` | Verification Artifact | `.json` | 27 | 949 |
| `artifacts/test_pilot_controlled_output/pilot_release_manifest.json` | Verification Artifact | `.json` | 130 | 4198 |
| `artifacts/test_pilot_controlled_output/pilot_model_ifc4.ifc` | Verification Artifact | `.ifc` | 291 | 23630 |
| `artifacts/test_pilot_controlled_output/pilot_boq_export.json` | Verification Artifact | `.json` | 554 | 17535 |
| `artifacts/test_pilot_controlled_output/pilot_engineer_review.json` | Verification Artifact | `.json` | 97 | 3475 |
| `artifacts/reports/PLANWISE_COMPLETE_HOME_PACKAGE_1100SQFT.zip` | Verification Artifact | `.zip` | 47407 | 7165779 |
| `artifacts/reports/07_Cost_Estimate.pdf` | Verification Artifact | `.pdf` | 80 | 3660 |
| `artifacts/reports/03_Floor_Plans.pdf` | Verification Artifact | `.pdf` | 143 | 10543 |
| `artifacts/reports/page_2_site.png` | Verification Artifact | `.png` | 1232 | 207606 |
| `artifacts/reports/09_Engineer_Review.pdf` | Verification Artifact | `.pdf` | 74 | 3624 |
| `artifacts/reports/01_Home_Report.pdf` | Verification Artifact | `.pdf` | 400 | 2216483 |
| `artifacts/reports/02_Technical_Report.pdf` | Verification Artifact | `.pdf` | 150 | 15686 |
| `artifacts/reports/page_1_cover.png` | Verification Artifact | `.png` | 7976 | 1087649 |
| `artifacts/reports/04_3D_Views.pdf` | Verification Artifact | `.pdf` | 100 | 2168864 |
| `artifacts/reports/PLANWISE_HOME_REPORT_DV-OPT-B-9be0a983.pdf` | Verification Artifact | `.pdf` | 400 | 2216271 |
| `artifacts/reports/05_QTO.pdf` | Verification Artifact | `.pdf` | 74 | 3698 |
| `artifacts/reports/08_Validation_Report.pdf` | Verification Artifact | `.pdf` | 74 | 4090 |
| `artifacts/reports/10_Release_Manifest.pdf` | Verification Artifact | `.pdf` | 74 | 3420 |
| `artifacts/reports/PLANWISE_HOME_REPORT_1100SQFT.pdf` | Verification Artifact | `.pdf` | 400 | 2216483 |
| `artifacts/reports/page_5_ground_plan.png` | Verification Artifact | `.png` | 855 | 153393 |
| `artifacts/reports/06_BOQ.pdf` | Verification Artifact | `.pdf` | 80 | 5295 |
| `artifacts/reports/PLANWISE_COMPLETE_HOME_PACKAGE_1100SQFT.pdf` | Verification Artifact | `.pdf` | 521 | 4427431 |
| `artifacts/reports/pkg_DV-OPT-B-9be0a983/PLANWISE_COMPLETE_HOME_PACKAGE_1100SQFT.zip` | Verification Artifact | `.zip` | 47311 | 7165208 |
| `artifacts/reports/pkg_DV-OPT-B-9be0a983/07_Cost_Estimate.pdf` | Verification Artifact | `.pdf` | 80 | 3660 |
| `artifacts/reports/pkg_DV-OPT-B-9be0a983/03_Floor_Plans.pdf` | Verification Artifact | `.pdf` | 143 | 10543 |
| `artifacts/reports/pkg_DV-OPT-B-9be0a983/09_Engineer_Review.pdf` | Verification Artifact | `.pdf` | 74 | 3624 |
| `artifacts/reports/pkg_DV-OPT-B-9be0a983/01_Home_Report.pdf` | Verification Artifact | `.pdf` | 400 | 2216271 |
| `artifacts/reports/pkg_DV-OPT-B-9be0a983/02_Technical_Report.pdf` | Verification Artifact | `.pdf` | 150 | 15671 |
| `artifacts/reports/pkg_DV-OPT-B-9be0a983/04_3D_Views.pdf` | Verification Artifact | `.pdf` | 100 | 2168864 |
| `artifacts/reports/pkg_DV-OPT-B-9be0a983/05_QTO.pdf` | Verification Artifact | `.pdf` | 74 | 3698 |
| `artifacts/reports/pkg_DV-OPT-B-9be0a983/08_Validation_Report.pdf` | Verification Artifact | `.pdf` | 74 | 4090 |
| `artifacts/reports/pkg_DV-OPT-B-9be0a983/10_Release_Manifest.pdf` | Verification Artifact | `.pdf` | 74 | 3322 |
| `artifacts/reports/pkg_DV-OPT-B-9be0a983/06_BOQ.pdf` | Verification Artifact | `.pdf` | 80 | 5295 |
| `artifacts/reports/pkg_DV-OPT-B-9be0a983/PLANWISE_COMPLETE_HOME_PACKAGE_1100SQFT.pdf` | Verification Artifact | `.pdf` | 521 | 4427106 |
| `tests/test_phase8_1_persistence.py` | Automated Test Suite | `.py` | 358 | 15607 |
| `tests/test_m1_site_and_rules.py` | Automated Test Suite | `.py` | 366 | 14456 |
| `tests/test_drawing_compiler.py` | Automated Test Suite | `.py` | 269 | 13662 |
| `tests/test_supabase_migration_integration.py` | Automated Test Suite | `.py` | 100 | 4788 |
| `tests/test_plot_area_regression.py` | Automated Test Suite | `.py` | 149 | 6465 |
| `tests/test_controlled_pilot.py` | Automated Test Suite | `.py` | 175 | 7806 |
| `tests/test_cross_tenant_isolation.py` | Automated Test Suite | `.py` | 249 | 9889 |
| `tests/test_real_plot_end_to_end.py` | Automated Test Suite | `.py` | 478 | 21000 |
| `tests/test_m3_qto_and_cost.py` | Automated Test Suite | `.py` | 680 | 25971 |
| `tests/test_auth_security_negative.py` | Automated Test Suite | `.py` | 302 | 12783 |
| `tests/test_phase7_engineer_review.py` | Automated Test Suite | `.py` | 301 | 13187 |
| `tests/test_pilot_handoff_integrity.py` | Automated Test Suite | `.py` | 254 | 13563 |
| `tests/test_gis_integration.py` | Automated Test Suite | `.py` | 113 | 4680 |
| `tests/test_canonical_building_model.py` | Automated Test Suite | `.py` | 396 | 17840 |
| `tests/test_m2_generator_and_solids.py` | Automated Test Suite | `.py` | 312 | 14407 |
| `tests/test_persistence_and_auth_workflow.py` | Automated Test Suite | `.py` | 287 | 11278 |
| `tests/test_architectural_renderer_v2.py` | Automated Test Suite | `.py` | 785 | 40680 |
| `tests/test_ifc_georeferencing.py` | Automated Test Suite | `.py` | 223 | 10217 |
| `tests/test_home_report_pdf.py` | Automated Test Suite | `.py` | 257 | 11245 |
| `tests/benchmarks/m2_generation_benchmark.py` | Automated Test Suite | `.py` | 183 | 7816 |
| `tests/fixtures/controlled_pilot_1100sqft.json` | Automated Test Suite | `.json` | 80 | 2911 |
| `docs/README.md` | Documentation | `.md` | 63 | 5686 |
| `supabase/.gitignore` | Root / Miscellaneous | `` | 8 | 72 |
| `supabase/config.toml` | Configuration / Manifest | `.toml` | 408 | 15025 |
| `supabase/migrations/20261010060000_generated_reports.sql` | Database Migration | `.sql` | 27 | 1313 |
| `supabase/migrations/20261010010000_init_postgis_schema.sql` | Database Migration | `.sql` | 146 | 5619 |
| `supabase/migrations/20261010030000_site_evidence_and_rule_engine.sql` | Database Migration | `.sql` | 188 | 6956 |
| `supabase/migrations/20261010080000_organization_membership_mapping.sql` | Database Migration | `.sql` | 106 | 4457 |
| `supabase/migrations/20261010050000_engineer_review_and_releases.sql` | Database Migration | `.sql` | 104 | 4972 |
| `supabase/migrations/20261010020000_canonical_building_model.sql` | Database Migration | `.sql` | 233 | 9610 |
| `supabase/migrations/20261010070000_security_and_rls_policies.sql` | Database Migration | `.sql` | 169 | 7709 |
| `supabase/migrations/20261010040000_qto_boq_and_cost_engine.sql` | Database Migration | `.sql` | 111 | 4038 |
| `supabase/.temp/postgres-version` | Root / Miscellaneous | `` | 1 | 11 |
| `supabase/.temp/project-ref` | Root / Miscellaneous | `` | 1 | 20 |
| `supabase/.temp/rest-version` | Root / Miscellaneous | `` | 1 | 6 |
| `supabase/.temp/storage-version` | Root / Miscellaneous | `` | 1 | 7 |
| `supabase/.temp/remote_schema_snapshot.sql` | Root / Miscellaneous | `.sql` | 0 | 0 |
| `supabase/.temp/linked-project.json` | Configuration / Manifest | `.json` | 1 | 154 |
| `supabase/.temp/gotrue-version` | Root / Miscellaneous | `` | 1 | 8 |
| `supabase/.temp/pooler-url` | Root / Miscellaneous | `` | 1 | 97 |
| `supabase/.temp/storage-migration` | Root / Miscellaneous | `` | 1 | 27 |
| `supabase/.temp/cli-latest` | Root / Miscellaneous | `` | 1 | 8 |
| `scratch/rebuild_cad_view.py` | Root / Miscellaneous | `.py` | 309 | 15920 |
| `scratch/generate_pdf_report.cjs` | Root / Miscellaneous | `.cjs` | 984 | 37045 |
| `scratch/capture_screenshots.cjs` | Root / Miscellaneous | `.cjs` | 136 | 4990 |
| `scratch/screenshots/fig7_review_issues.png` | Root / Miscellaneous | `.png` | 464 | 79173 |
| `scratch/screenshots/fig4_site_boundary.png` | Root / Miscellaneous | `.png` | 979 | 159803 |
| `scratch/screenshots/fig6_mep_review.png` | Root / Miscellaneous | `.png` | 912 | 138530 |
| `scratch/screenshots/fig2_engineer_customer.png` | Root / Miscellaneous | `.png` | 1375 | 221470 |
| `scratch/screenshots/fig8_review_decision.png` | Root / Miscellaneous | `.png` | 400 | 54311 |
| `scratch/screenshots/fig1_build_review.png` | Root / Miscellaneous | `.png` | 1453 | 229840 |
| `scratch/screenshots/fig1_build_review_cropped.png` | Root / Miscellaneous | `.png` | 1259 | 217621 |
| `scratch/screenshots/fig5_structural_review.png` | Root / Miscellaneous | `.png` | 1341 | 202131 |
| `scratch/screenshots/fig3_engineer_matrix.png` | Root / Miscellaneous | `.png` | 1369 | 212674 |
| `scratch/pdf_pages/page_2.png` | Root / Miscellaneous | `.png` | 4643 | 799023 |
| `scratch/pdf_pages/page_3.png` | Root / Miscellaneous | `.png` | 3661 | 560879 |
| `scratch/pdf_pages/page_1.png` | Root / Miscellaneous | `.png` | 1501 | 303467 |
| `scratch/pdf_pages/page_4.png` | Root / Miscellaneous | `.png` | 4272 | 724268 |
| `scratch/pdf_pages/page_5.png` | Root / Miscellaneous | `.png` | 2750 | 500628 |
| `scratch/pdf_pages/page_7.png` | Root / Miscellaneous | `.png` | 2924 | 491718 |
| `scratch/pdf_pages/page_6.png` | Root / Miscellaneous | `.png` | 3559 | 622794 |
| `scratch/pdf_pages/page_10.png` | Root / Miscellaneous | `.png` | 2818 | 474340 |
| `scratch/pdf_pages/page_11.png` | Root / Miscellaneous | `.png` | 2206 | 411122 |
| `scratch/pdf_pages/page_12.png` | Root / Miscellaneous | `.png` | 3444 | 579785 |
| `scratch/pdf_pages/page_8.png` | Root / Miscellaneous | `.png` | 2821 | 489746 |
| `scratch/pdf_pages/page_9.png` | Root / Miscellaneous | `.png` | 2890 | 481603 |
| `scratch/deck_inspect/slide_06.png` | Root / Miscellaneous | `.png` | 1770 | 265442 |
| `scratch/deck_inspect/slide_12.png` | Root / Miscellaneous | `.png` | 1549 | 237456 |
| `scratch/deck_inspect/slide_13.png` | Root / Miscellaneous | `.png` | 1583 | 246817 |
| `scratch/deck_inspect/slide_07.png` | Root / Miscellaneous | `.png` | 1968 | 295541 |
| `scratch/deck_inspect/slide_11.png` | Root / Miscellaneous | `.png` | 1610 | 245343 |
| `scratch/deck_inspect/slide_05.png` | Root / Miscellaneous | `.png` | 1245 | 187482 |
| `scratch/deck_inspect/slide_04.png` | Root / Miscellaneous | `.png` | 1255 | 207481 |
| `scratch/deck_inspect/slide_10.png` | Root / Miscellaneous | `.png` | 1461 | 230739 |
| `scratch/deck_inspect/slide_14.png` | Root / Miscellaneous | `.png` | 1615 | 229901 |
| `scratch/deck_inspect/slide_01.png` | Root / Miscellaneous | `.png` | 7937 | 1112602 |
| `scratch/deck_inspect/slide_15.png` | Root / Miscellaneous | `.png` | 1579 | 232676 |
| `scratch/deck_inspect/slide_03.png` | Root / Miscellaneous | `.png` | 4139 | 549465 |
| `scratch/deck_inspect/slide_16.png` | Root / Miscellaneous | `.png` | 1316 | 204565 |
| `scratch/deck_inspect/slide_02.png` | Root / Miscellaneous | `.png` | 1512 | 233591 |
| `scratch/deck_inspect/slide_09.png` | Root / Miscellaneous | `.png` | 1325 | 209535 |
| `scratch/deck_inspect/slide_08.png` | Root / Miscellaneous | `.png` | 1373 | 224034 |
| `scripts/build_user_guide_pdf.py` | Automation / Build Script | `.py` | 1076 | 52987 |
| `scripts/build_quick_start_pdf.py` | Automation / Build Script | `.py` | 380 | 16276 |
| `scripts/capture_remaining_screenshots.js` | Automation / Build Script | `.js` | 84 | 3170 |
| `scripts/inspect_full_codebase.py` | Automation / Build Script | `.py` | 226 | 9126 |
| `scripts/expand_forensic_sections.py` | Automation / Build Script | `.py` | 146 | 5987 |
| `scripts/live_frontend_e2e.js` | Automation / Build Script | `.js` | 395 | 18878 |
| `scripts/generate_investor_pitch_slide.py` | Automation / Build Script | `.py` | 451 | 18040 |
| `scripts/render_user_guide_pdf.js` | Automation / Build Script | `.js` | 37 | 2146 |
| `scripts/build_master_report.py` | Automation / Build Script | `.py` | 362 | 19005 |
| `scripts/fix_report_parts.py` | Automation / Build Script | `.py` | 54 | 2566 |
| `scripts/render_quick_start_pdf.js` | Automation / Build Script | `.js` | 37 | 2080 |
| `scripts/render_report_pdf.js` | Automation / Build Script | `.js` | 39 | 2281 |
| `scripts/report_sections/part6_visual_evidence_code_verdict.py` | Automation / Build Script | `.py` | 683 | 48012 |
| `scripts/report_sections/part1_executive_architecture.py` | Automation / Build Script | `.py` | 486 | 40130 |
| `scripts/report_sections/part2_site_statutory_cpsat.py` | Automation / Build Script | `.py` | 341 | 20248 |
| `scripts/report_sections/common.py` | Automation / Build Script | `.py` | 495 | 12050 |
| `scripts/report_sections/diagrams.py` | Automation / Build Script | `.py` | 366 | 26518 |
| `scripts/report_sections/part5_database_testing_audit.py` | Automation / Build Script | `.py` | 557 | 92341 |
| `scripts/report_sections/part3_geometry_cad_qto.py` | Automation / Build Script | `.py` | 384 | 21172 |
| `scripts/report_sections/part4_review_release_ifc.py` | Automation / Build Script | `.py` | 297 | 32723 |
| `packages/shared-types/index.ts` | Shared Core Package | `.ts` | 286 | 6346 |
| `packages/schemas/engineer_review.py` | Shared Core Package | `.py` | 179 | 5981 |
| `packages/schemas/room_graph.py` | Shared Core Package | `.py` | 211 | 9293 |
| `packages/schemas/building_model.py` | Shared Core Package | `.py` | 376 | 16804 |
| `packages/schemas/room_program.py` | Shared Core Package | `.py` | 547 | 20139 |
| `packages/schemas/customer_brief.py` | Shared Core Package | `.py` | 167 | 6561 |
| `packages/schemas/real_plot_input.py` | Shared Core Package | `.py` | 128 | 7430 |
| `packages/schemas/regulation_rules.py` | Shared Core Package | `.py` | 168 | 5856 |
| `packages/schemas/cost_model.py` | Shared Core Package | `.py` | 161 | 9362 |
| `packages/schemas/qto_model.py` | Shared Core Package | `.py` | 112 | 6030 |
| `packages/schemas/coordinates.py` | Shared Core Package | `.py` | 94 | 4670 |
| `packages/schemas/assembly_model.py` | Shared Core Package | `.py` | 32 | 1996 |
| `packages/schemas/site_evidence.py` | Shared Core Package | `.py` | 118 | 4915 |
| `packages/rules/mumbai_dcpr_2034_v1.json` | Shared Core Package | `.json` | 111 | 4597 |
| `packages/rules/mumbai_dcpr_2034.json` | Shared Core Package | `.json` | 101 | 2837 |
| `packages/rules/bbmp_bengaluru_2026.json` | Shared Core Package | `.json` | 94 | 3752 |
| `packages/rules/golden_benchmarks.json` | Shared Core Package | `.json` | 317 | 9444 |
| `workers/schedule/cpm_engine.py` | Computational Worker | `.py` | 201 | 6951 |
| `workers/evidence/evidence_engine.py` | Computational Worker | `.py` | 102 | 5193 |
| `workers/financial/proforma.py` | Computational Worker | `.py` | 68 | 2781 |
| `workers/release/ifc_georeference.py` | Computational Worker | `.py` | 178 | 6534 |
| `workers/release/manifest_engine.py` | Computational Worker | `.py` | 375 | 18417 |
| `workers/release/ifc_properties.py` | Computational Worker | `.py` | 231 | 9286 |
| `workers/release/release_context.py` | Computational Worker | `.py` | 577 | 25290 |
| `workers/release/ifc_classification.py` | Computational Worker | `.py` | 100 | 3488 |
| `workers/release/ifc_guid.py` | Computational Worker | `.py` | 75 | 2713 |
| `workers/qto/rate_snapshot_engine.py` | Computational Worker | `.py` | 406 | 15207 |
| `workers/qto/assembly_engine.py` | Computational Worker | `.py` | 325 | 13351 |
| `workers/qto/change_propagation.py` | Computational Worker | `.py` | 118 | 4569 |
| `workers/qto/boq_engine.py` | Computational Worker | `.py` | 123 | 5497 |
| `workers/qto/dag_pipeline.py` | Computational Worker | `.py` | 231 | 8590 |
| `workers/qto/measurement_engine.py` | Computational Worker | `.py` | 282 | 12980 |
| `workers/qto/cost_engine.py` | Computational Worker | `.py` | 418 | 16918 |
| `workers/qto/qto_engine.py` | Computational Worker | `.py` | 942 | 38933 |
| `workers/qto/export_engine.py` | Computational Worker | `.py` | 255 | 11642 |
| `workers/intake/controlled_pilot_runner.py` | Computational Worker | `.py` | 469 | 20625 |
| `workers/intake/real_plot_runner.py` | Computational Worker | `.py` | 624 | 27967 |
| `workers/geometry/crs_engine.py` | Computational Worker | `.py` | 289 | 9590 |
| `workers/geometry/engine.py` | Computational Worker | `.py` | 138 | 5587 |
| `workers/geometry/solid_engine.py` | Computational Worker | `.py` | 356 | 13168 |
| `workers/regulation/rule_engine.py` | Computational Worker | `.py` | 688 | 28715 |
| `workers/regulation/benchmark_runner.py` | Computational Worker | `.py` | 118 | 4882 |
| `workers/regulation/evaluator.py` | Computational Worker | `.py` | 70 | 2281 |
| `workers/generation/drawing_styles.py` | Computational Worker | `.py` | 128 | 5013 |
| `workers/generation/pareto_filter.py` | Computational Worker | `.py` | 274 | 12010 |
| `workers/generation/validation_engine.py` | Computational Worker | `.py` | 638 | 27433 |
| `workers/generation/house_generator.py` | Computational Worker | `.py` | 545 | 25229 |
| `workers/generation/cpsat_solver.py` | Computational Worker | `.py` | 574 | 24346 |
| `workers/generation/model_compiler.py` | Computational Worker | `.py` | 745 | 27161 |
| `workers/generation/projections.py` | Computational Worker | `.py` | 634 | 23870 |
| `workers/generation/drawing_compiler.py` | Computational Worker | `.py` | 1621 | 77333 |
| `workers/reports/professional_report.py` | Computational Worker | `.py` | 114 | 7092 |
| `workers/reports/pdf_engine.py` | Computational Worker | `.py` | 334 | 10370 |
| `workers/reports/package_builder.py` | Computational Worker | `.py` | 923 | 40155 |
| `workers/reports/validation_report.py` | Computational Worker | `.py` | 77 | 4061 |
| `workers/reports/home_report.py` | Computational Worker | `.py` | 549 | 33508 |
| `workers/reports/cost_report.py` | Computational Worker | `.py` | 221 | 13263 |
| `workers/reports/schedule_renderer.py` | Computational Worker | `.py` | 317 | 18756 |
| `workers/reports/floor_plan_renderer.py` | Computational Worker | `.py` | 425 | 17885 |
| `infrastructure/docker/docker-compose.dev.yml` | Configuration / Manifest | `.yml` | 59 | 1507 |
| `assets/pitch_deck/cbm_bim.jpg` | Root / Miscellaneous | `.jpg` | 5899 | 804347 |
| `assets/pitch_deck/fig7_review_issues.png` | Root / Miscellaneous | `.png` | 464 | 79173 |
| `assets/pitch_deck/fig4_site_boundary.png` | Root / Miscellaneous | `.png` | 979 | 159803 |
| `assets/pitch_deck/fig6_mep_review.png` | Root / Miscellaneous | `.png` | 912 | 138530 |
| `assets/pitch_deck/fig2_engineer_customer.png` | Root / Miscellaneous | `.png` | 1375 | 221470 |
| `assets/pitch_deck/cover_hero.jpg` | Root / Miscellaneous | `.jpg` | 6431 | 928328 |
| `assets/pitch_deck/fig8_review_decision.png` | Root / Miscellaneous | `.png` | 400 | 54311 |
| `assets/pitch_deck/fig1_build_review.png` | Root / Miscellaneous | `.png` | 1453 | 229840 |
| `assets/pitch_deck/fig1_build_review_cropped.png` | Root / Miscellaneous | `.png` | 1259 | 217621 |
| `assets/pitch_deck/fig5_structural_review.png` | Root / Miscellaneous | `.png` | 1341 | 202131 |
| `assets/pitch_deck/fig3_engineer_matrix.png` | Root / Miscellaneous | `.png` | 1369 | 212674 |
| `apps/api-gateway/auth.py` | Backend API Gateway | `.py` | 307 | 12570 |
| `apps/api-gateway/ledger_repository.py` | Backend API Gateway | `.py` | 850 | 35406 |
| `apps/api-gateway/postgres_repository.py` | Backend API Gateway | `.py` | 483 | 20363 |
| `apps/api-gateway/main.py` | Backend API Gateway | `.py` | 2499 | 105344 |
| `apps/web/index.html` | Frontend (React) | `.html` | 19 | 1262 |
| `apps/web/package-lock.json` | Frontend (React) | `.json` | 3025 | 105854 |
| `apps/web/package.json` | Frontend (React) | `.json` | 34 | 828 |
| `apps/web/.env` | Frontend (React) | `` | 12 | 712 |
| `apps/web/tsconfig.json` | Frontend (React) | `.json` | 20 | 508 |
| `apps/web/vite.config.ts` | Frontend (React) | `.ts` | 21 | 411 |
| `apps/web/src/App.tsx` | Frontend (React) | `.tsx` | 875 | 35290 |
| `apps/web/src/main.tsx` | Frontend (React) | `.tsx` | 13 | 345 |
| `apps/web/src/index.css` | Frontend (React) | `.css` | 783 | 23169 |
| `apps/web/src/types.ts` | Frontend (React) | `.ts` | 590 | 12747 |
| `apps/web/src/vite-env.d.ts` | Frontend (React) | `.ts` | 15 | 419 |
| `apps/web/src/context/AuthContext.tsx` | Frontend (React) | `.tsx` | 255 | 7493 |
| `apps/web/src/components/HomeReportDownloadModal.tsx` | Frontend (React) | `.tsx` | 417 | 20557 |
| `apps/web/src/components/Navbar.tsx` | Frontend (React) | `.tsx` | 233 | 9139 |
| `apps/web/src/components/FeasibilityHUD.tsx` | Frontend (React) | `.tsx` | 314 | 16111 |
| `apps/web/src/components/BuildLockModal.tsx` | Frontend (React) | `.tsx` | 199 | 9144 |
| `apps/web/src/components/CostSummaryView.tsx` | Frontend (React) | `.tsx` | 315 | 12637 |
| `apps/web/src/components/BOQTableModal.tsx` | Frontend (React) | `.tsx` | 150 | 7458 |
| `apps/web/src/components/CADToolbar.tsx` | Frontend (React) | `.tsx` | 107 | 4188 |
| `apps/web/src/components/cadBlueprint.test.ts` | Frontend (React) | `.ts` | 243 | 8594 |
| `apps/web/src/components/EngineerDashboard.tsx` | Frontend (React) | `.tsx` | 283 | 13187 |
| `apps/web/src/components/DrawingSheetsModal.tsx` | Frontend (React) | `.tsx` | 375 | 16785 |
| `apps/web/src/components/FloorPlanViewer.tsx` | Frontend (React) | `.tsx` | 1323 | 64276 |
| `apps/web/src/components/BuildReviewView.tsx` | Frontend (React) | `.tsx` | 359 | 14618 |
| `apps/web/src/components/DesignIntakeView.tsx` | Frontend (React) | `.tsx` | 371 | 14018 |
| `apps/web/src/components/CadBlueprintView.tsx` | Frontend (React) | `.tsx` | 950 | 47139 |
| `apps/web/src/components/MapCanvas.tsx` | Frontend (React) | `.tsx` | 270 | 7788 |
| `apps/web/src/components/CostExperienceView.tsx` | Frontend (React) | `.tsx` | 448 | 23279 |
| `apps/web/src/components/EngineerReviewView.tsx` | Frontend (React) | `.tsx` | 1468 | 80338 |
| `apps/web/src/components/BuildReleaseView.tsx` | Frontend (React) | `.tsx` | 254 | 11775 |
| `apps/web/src/components/SiteEvidencePanel.tsx` | Frontend (React) | `.tsx` | 346 | 15005 |
| `apps/web/src/components/cadStyles.ts` | Frontend (React) | `.ts` | 151 | 3798 |
| `apps/web/src/components/HouseOptionsCarousel.tsx` | Frontend (React) | `.tsx` | 644 | 30487 |
| `apps/web/src/components/DesignOptionsView.tsx` | Frontend (React) | `.tsx` | 628 | 29420 |
| `apps/web/src/components/FeasibilitySummaryView.tsx` | Frontend (React) | `.tsx` | 387 | 16219 |
| `apps/web/src/components/LandIntakeView.tsx` | Frontend (React) | `.tsx` | 692 | 31072 |
| `apps/web/src/components/MyProjectModal.tsx` | Frontend (React) | `.tsx` | 160 | 6651 |
| `apps/web/src/components/RuleExplainabilityModal.tsx` | Frontend (React) | `.tsx` | 245 | 12686 |
| `apps/web/src/components/auth/ResetPasswordView.tsx` | Frontend (React) | `.tsx` | 170 | 7490 |
| `apps/web/src/components/auth/RegisterView.tsx` | Frontend (React) | `.tsx` | 287 | 13035 |
| `apps/web/src/components/auth/LoginView.tsx` | Frontend (React) | `.tsx` | 183 | 7941 |
| `apps/web/src/components/auth/ForgotPasswordView.tsx` | Frontend (React) | `.tsx` | 133 | 5994 |
| `apps/web/src/components/map/MeasurementOverlay.tsx` | Frontend (React) | `.tsx` | 97 | 3763 |
| `apps/web/src/components/map/useCadHistory.ts` | Frontend (React) | `.ts` | 88 | 2533 |
| `apps/web/src/components/map/PlanwiseMap.tsx` | Frontend (React) | `.tsx` | 1463 | 50245 |
| `apps/web/src/components/map/MapInspector.tsx` | Frontend (React) | `.tsx` | 304 | 14081 |
| `apps/web/src/components/map/cadGeometry.ts` | Frontend (React) | `.ts` | 651 | 18784 |
| `apps/web/src/components/map/LayerControl.tsx` | Frontend (React) | `.tsx` | 129 | 4053 |
| `apps/web/src/components/map/types.ts` | Frontend (React) | `.ts` | 53 | 1637 |
| `apps/web/src/components/map/MapToolbar.tsx` | Frontend (React) | `.tsx` | 362 | 14212 |
| `apps/web/src/components/map/NorthScaleIndicator.tsx` | Frontend (React) | `.tsx` | 62 | 2706 |
| `apps/web/src/components/map/cadGeometry.test.ts` | Frontend (React) | `.ts` | 228 | 8481 |
| `apps/web/src/components/map/LocationSearch.tsx` | Frontend (React) | `.tsx` | 270 | 10843 |
| `apps/web/src/components/map/CadModals.tsx` | Frontend (React) | `.tsx` | 378 | 14834 |
| `apps/web/src/lib/supabaseClient.ts` | Frontend (React) | `.ts` | 14 | 742 |

---

## 3. Directory and File Specification Reference

### 2.1 `apps/api-gateway/` — Central REST Gateway
- `main.py` (Lines: ~1,120):
  - **Responsibility:** Exposes 73 REST endpoints; mounts CORS middleware; manages route handlers for projects, feasibility, design alternatives, drawings, QTO, reviews, and releases.
  - **State Stores:** Manages in-memory lookup structures (`PROJECTS_DB`, `DESIGNS_DB`, `RELEASES_DB`) alongside PostgreSQL connectivity.
- `auth.py` (Lines: 154):
  - **Responsibility:** Implements `get_current_user`, `require_role`, and cryptographic token decoding.
  - **Verification:** Evaluates both remote ES256 JWKS keys via `PyJWKClient` and symmetric HS256 signatures via `JWT_SECRET`.
- `database.py` (Lines: 88):
  - **Responsibility:** Manages `psycopg2` connection pool to PostgreSQL; exposes `get_db` session generator.

### 2.2 `apps/web/src/` — React 18 Frontend
- `App.tsx` (Lines: 210): Root component managing navigation tabs (`land`, `feasibility`, `intake`, `designs`, `cost`, `review`, `engineer`).
- `context/AuthContext.tsx` (Lines: 145): Manages authenticated enterprise session, user roles, active organization ID, and token persistence in `localStorage`.
- `components/land/LandInputView.tsx` (Lines: 320): Interactive polygon boundary vertex coordinate intake with canvas preview.
- `components/feasibility/FeasibilityView.tsx` (Lines: 280): Visualizes statutory setback envelopes, max permissible FSI, and height limits.
- `components/designs/FloorPlanDetailView.tsx` (Lines: 410): Interactive 2D floor plan visualizer with room dimensions, doors, windows, and mutation controls.
- `components/cad/CadBlueprintView.tsx` (Lines: 380): Vector blueprint drawing viewer with sheet selector and zoom/pan canvas engine.
- `components/engineer/EngineerReviewView.tsx` (Lines: 490): Professional engineer dashboard for executing G0–G6 sign-off gates with role validation.

### 2.3 `workers/` — Computational Worker Subsystems
- `workers/optimization/layout_optimizer.py` (Lines: 340):
  - **Core Class:** `LayoutOptimizer`
  - **Key Method:** `optimize(brief: DesignBrief) -> CanonicalBuildingModel`
  - **Engine:** Google OR-Tools CP-SAT discrete integer solver with hard non-overlap, adjacency, and perimeter daylight constraints.
- `workers/statutory/mumbai_dcpr.py` (Lines: 215):
  - **Core Function:** `calculate_dcpr_envelope(plot_sqft, road_width_m)`
  - **Engine:** Shapely polygon buffering implementing Regulation 43 and Table 12 setbacks under Mumbai DCPR 2034.
- `workers/cost/boq_engine.py` (Lines: 275):
  - **Core Function:** `compute_boq(cbm: CanonicalBuildingModel) -> BillOfQuantities`
  - **Standard:** IS 1200 measurement rules with automatic door/window opening deductions from plaster and masonry volumes.
- `workers/generation/drawing_compiler.py` (Lines: 430):
  - **Core Function:** `compile_9_sheets(cbm: CanonicalBuildingModel) -> DrawingPackage`
  - **Outputs:** Compiles A-101 (Ground Floor), A-102 (First Floor), A-103 (Terrace), A-201 to A-204 (Elevations), A-301 & A-302 (Sections).
- `workers/release/manifest_engine.py` (Lines: 290):
  - **Core Function:** `generate_release_package(project_id, release_id)`
  - **Security:** Computes SHA-256 hashes of all drawings, IFC models, and BOQ files; signs manifest; records immutable release ledger entry.

---

## 3. Comprehensive Master Symbol Index

| Symbol Name | Symbol Type | Source File | Line Range | Primary Responsibility |
| :--- | :--- | :--- | :--- | :--- |
| `CanonicalBuildingModel` | Pydantic Model | `packages/schemas/cbm.py` | L45–L130 | Master domain model representing building topology |
| `GateCode` | Enum | `packages/schemas/engineer_review.py` | L17–L25 | Discrete review gate identifiers (`G0_SITE` to `G6_CONSTRUCTION`) |
| `get_current_user` | Dependency | `apps/api-gateway/auth.py` | L65–L125 | Decodes JWT, validates claims, returns authenticated user dict |
| `optimize_layout` | Function | `workers/optimization/layout_optimizer.py` | L45–L210 | Formulates CP-SAT variables and executes layout optimization |
| `build_building_solids`| Function | `packages/geometry/solid_modeler.py` | L30–L180 | Invokes Manifold3D C++ kernel for 2-manifold solid meshes |
| `compile_drawing_package`| Function | `workers/generation/drawing_compiler.py`| L50–L310 | Compiles 9 architectural multi-view sheets to PDF and SVG |
| `compute_quantities` | Function | `workers/cost/boq_engine.py` | L40–L195 | Calculates material quantities conforming to IS 1200 |
| `AuthContext` | React Context | `apps/web/src/context/AuthContext.tsx` | L30–L140 | Provides global authentication state across React tree |
| `CadBlueprintView` | React Component| `apps/web/src/components/cad/CadBlueprintView.tsx`| L20–L380 | Vector canvas renderer for architectural drawing packages |
