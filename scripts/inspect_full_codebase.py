import os
import re
import csv
import json
import glob
from pathlib import Path

REPO_ROOT = Path("/Users/surajkumar/Desktop/Real_state_dev")
ENCYCLOPEDIA_DIR = REPO_ROOT / "artifacts" / "technical_encyclopedia"

def scan_files():
    file_inventory = []
    for root, dirs, files in os.walk(REPO_ROOT):
        # Skip node_modules, .git, .venv, __pycache__, dist, build
        if any(ignored in root for ignored in ["node_modules", ".git", ".venv", "__pycache__", "dist", "build", ".tempmediaStorage"]):
            continue
        for f in files:
            p = Path(root) / f
            rel_p = p.relative_to(REPO_ROOT)
            try:
                size_bytes = p.stat().st_size
                with open(p, "r", encoding="utf-8", errors="ignore") as fh:
                    lines = fh.readlines()
                    line_count = len(lines)
            except Exception:
                size_bytes = 0
                line_count = 0
            
            ext = p.suffix
            file_inventory.append({
                "path": str(rel_p),
                "extension": ext,
                "size_bytes": size_bytes,
                "lines": line_count,
                "category": categorize_file(str(rel_p))
            })
    return file_inventory

def categorize_file(rel_path: str) -> str:
    if rel_path.startswith("apps/web"):
        return "Frontend (React)"
    elif rel_path.startswith("apps/api-gateway"):
        return "Backend API Gateway"
    elif rel_path.startswith("packages/"):
        return "Shared Core Package"
    elif rel_path.startswith("workers/"):
        return "Computational Worker"
    elif rel_path.startswith("supabase/migrations") or rel_path.startswith("database/migrations"):
        return "Database Migration"
    elif rel_path.startswith("tests/"):
        return "Automated Test Suite"
    elif rel_path.startswith("scripts/"):
        return "Automation / Build Script"
    elif rel_path.startswith("artifacts/"):
        return "Verification Artifact"
    elif rel_path.endswith((".md", ".txt", ".rst")):
        return "Documentation"
    elif rel_path.endswith((".json", ".yaml", ".yml", ".toml", ".env", ".example")):
        return "Configuration / Manifest"
    else:
        return "Root / Miscellaneous"

def scan_api_endpoints():
    endpoints = []
    main_api = REPO_ROOT / "apps" / "api-gateway" / "main.py"
    if not main_api.exists():
        return endpoints
    
    with open(main_api, "r", encoding="utf-8") as f:
        content = f.read()

    # Regex for @app.get(...), @app.post(...), etc.
    pattern = r'@app\.(get|post|put|delete|patch|options)\s*\(\s*["\']([^"\']+)["\'](?:[^\)]*)\)\s*(?:async\s+)?def\s+([a-zA-Z0-9_]+)\s*\(([^)]*)\)'
    matches = re.finditer(pattern, content)
    for m in matches:
        method = m.group(1).upper()
        path = m.group(2)
        func_name = m.group(3)
        params = m.group(4)
        
        # Check authentication / role dependency
        requires_auth = "get_current_user" in params
        requires_role = "require_role" in params or "role" in params
        
        endpoints.append({
            "method": method,
            "path": path,
            "handler_function": func_name,
            "file": "apps/api-gateway/main.py",
            "authenticated": requires_auth,
            "role_restricted": requires_role,
            "parameters": params.strip().replace("\n", " ")
        })
    return endpoints

def scan_migrations():
    migrations = []
    dirs_to_check = [
        ("supabase/migrations", REPO_ROOT / "supabase" / "migrations"),
        ("database/migrations", REPO_ROOT / "database" / "migrations")
    ]
    for cat, d in dirs_to_check:
        if not d.exists():
            continue
        for f in sorted(d.glob("*.sql")):
            with open(f, "r", encoding="utf-8") as fh:
                sql = fh.read()
            tables_created = re.findall(r'CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?([a-zA-Z0-9_\.]+)', sql, re.IGNORECASE)
            rls_enabled = re.findall(r'ALTER\s+TABLE\s+([a-zA-Z0-9_\.]+)\s+ENABLE\s+ROW\s+LEVEL\s+SECURITY', sql, re.IGNORECASE)
            migrations.append({
                "directory": cat,
                "filename": f.name,
                "tables_created": tables_created,
                "rls_enabled_tables": rls_enabled,
                "lines": len(sql.splitlines()),
                "size_bytes": len(sql.encode('utf-8'))
            })
    return migrations

def scan_tests():
    tests = []
    test_dir = REPO_ROOT / "tests"
    for f in sorted(test_dir.glob("test_*.py")):
        with open(f, "r", encoding="utf-8") as fh:
            content = fh.read()
        test_funcs = re.findall(r'def\s+(test_[a-zA-Z0-9_]+)\s*\(', content)
        test_classes = re.findall(r'class\s+([a-zA-Z0-9_]+)\s*\(', content)
        tests.append({
            "file": str(f.relative_to(REPO_ROOT)),
            "classes": test_classes,
            "test_count": len(test_funcs),
            "test_functions": test_funcs
        })
    return tests

def scan_frontend_components():
    components = []
    web_src = REPO_ROOT / "apps" / "web" / "src"
    for p in web_src.rglob("*.tsx"):
        with open(p, "r", encoding="utf-8") as fh:
            content = fh.read()
        comp_matches = re.findall(r'(?:export\s+(?:default\s+)?(?:function|const)\s+([A-Z][a-zA-Z0-9_]+))', content)
        hooks_used = list(set(re.findall(r'\b(use[A-Z][a-zA-Z0-9_]+)\b', content)))
        components.append({
            "file": str(p.relative_to(REPO_ROOT)),
            "components": comp_matches,
            "hooks": hooks_used,
            "lines": len(content.splitlines())
        })
    return components

def main():
    ENCYCLOPEDIA_DIR.mkdir(parents=True, exist_ok=True)
    
    files = scan_files()
    with open(ENCYCLOPEDIA_DIR / "file_inventory.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["path", "category", "extension", "size_bytes", "lines"])
        w.writeheader()
        w.writerows(files)
        
    endpoints = scan_api_endpoints()
    with open(ENCYCLOPEDIA_DIR / "endpoint_inventory.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["method", "path", "handler_function", "file", "authenticated", "role_restricted", "parameters"])
        w.writeheader()
        w.writerows(endpoints)
        
    migrations = scan_migrations()
    with open(ENCYCLOPEDIA_DIR / "database_inventory.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["directory", "filename", "tables_created", "rls_enabled_tables", "lines", "size_bytes"])
        w.writeheader()
        for m in migrations:
            w.writerow({
                "directory": m["directory"],
                "filename": m["filename"],
                "tables_created": "; ".join(m["tables_created"]),
                "rls_enabled_tables": "; ".join(m["rls_enabled_tables"]),
                "lines": m["lines"],
                "size_bytes": m["size_bytes"]
            })
            
    tests = scan_tests()
    with open(ENCYCLOPEDIA_DIR / "test_inventory.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["file", "classes", "test_count", "test_functions"])
        w.writeheader()
        for t in tests:
            w.writerow({
                "file": t["file"],
                "classes": "; ".join(t["classes"]),
                "test_count": t["test_count"],
                "test_functions": "; ".join(t["test_functions"])
            })

    frontend = scan_frontend_components()
    with open(ENCYCLOPEDIA_DIR / "frontend_components.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["file", "components", "hooks", "lines"])
        w.writeheader()
        for fc in frontend:
            w.writerow({
                "file": fc["file"],
                "components": "; ".join(fc["components"]),
                "hooks": "; ".join(fc["hooks"]),
                "lines": fc["lines"]
            })

    summary = {
        "total_files": len(files),
        "total_source_lines": sum(f["lines"] for f in files),
        "total_api_endpoints": len(endpoints),
        "total_migration_files": len(migrations),
        "total_test_files": len(tests),
        "total_test_functions": sum(t["test_count"] for t in tests),
        "total_frontend_components": sum(len(fc["components"]) for fc in frontend)
    }
    with open(ENCYCLOPEDIA_DIR / "inventory_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print(f"[OK] Source scanning complete:")
    print(f"     Total Files: {summary['total_files']}")
    print(f"     Total Lines: {summary['total_source_lines']}")
    print(f"     API Endpoints: {summary['total_api_endpoints']}")
    print(f"     Migration Files: {summary['total_migration_files']}")
    print(f"     Test Files: {summary['total_test_files']} (functions: {summary['total_test_functions']})")
    print(f"     Frontend Files: {len(frontend)}")

if __name__ == "__main__":
    main()
