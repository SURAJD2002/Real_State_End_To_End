#!/usr/bin/env python3
"""
Planwise Enterprise — Forensic Path Citation Verifier
=====================================================
Automated verification tool and CI gate to guarantee that zero non-existent,
hallucinated, or stale file paths are cited across project documentation,
forensic audit reports, evidence manifests, and report generators.

Exits with code 0 if all cited paths exist in the repository.
Exits with code 1 if any cited path is broken or non-existent.
"""

import os
import re
import sys
import json
from pathlib import Path
from typing import List, Tuple, Set, Dict

REPO_ROOT = Path(__file__).resolve().parent.parent

# Files and directories subject to strict path verification
TARGET_DOC_GLOBS = [
    "*.md",
    "docs/**/*.md",
    "artifacts/planwise_enterprise_forensic_technical_master_report.md",
    "artifacts/planwise_enterprise_evidence_manifest.json",
    "scripts/build_master_report.py",
    "scripts/report_sections/*.py",
]

# Prefixes that indicate a repository-relative path citation
REPO_PREFIXES = (
    "apps/",
    "workers/",
    "packages/",
    "tests/",
    "scripts/",
    "migrations/",
    "artifacts/",
    "docs/",
)

# Regex to capture repository paths, with optional :L123 or :123 suffix
PATH_PATTERN = re.compile(
    r'(?:["\'`(\s]|^)((?:apps|workers|packages|tests|scripts|migrations|artifacts|docs)/[a-zA-Z0-9_\-\./]+\.[a-zA-Z0-9_]+)(?::(?:L)?\d+(?:-(?:L)?\d+)?)?(?:["\'`)\s,]|$)'
)

# Markdown link pattern [text](path)
MD_LINK_PATTERN = re.compile(r'\[([^\]]+)\]\(([^)#\s]+)(?:#[^)]*)?\)')

EXCLUDED_CITED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".svg", ".pdf", ".zip"}


def clean_path_candidate(candidate: str, source_doc: Path) -> str:
    cleaned = candidate.strip(" \t\n\r\"'`()[],;:")
    # Remove :L12-L34 or :123
    cleaned = re.sub(r':L?\d+(?:-L?\d+)?$', '', cleaned)
    return cleaned


def extract_paths_from_file(file_path: Path) -> List[Tuple[str, int]]:
    results = []
    try:
        content = file_path.read_text(encoding="utf-8")
    except Exception as e:
        print(f"Warning: could not read {file_path}: {e}", file=sys.stderr)
        return results

    lines = content.splitlines()
    for idx, line in enumerate(lines, 1):
        # 1. Check repo prefix pattern
        for match in PATH_PATTERN.finditer(line):
            path_str = match.group(1)
            results.append((path_str, idx))

        # 2. Check markdown link pattern
        for match in MD_LINK_PATTERN.finditer(line):
            target = match.group(2)
            if target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            # Resolve relative link
            if target.startswith("../") or target.startswith("./"):
                resolved = (file_path.parent / target).resolve()
                try:
                    rel_to_root = resolved.relative_to(REPO_ROOT).as_posix()
                    results.append((rel_to_root, idx))
                except ValueError:
                    results.append((str(resolved), idx))
            elif any(target.startswith(p) for p in REPO_PREFIXES):
                results.append((target, idx))

    return results


def verify_all_cited_paths() -> Tuple[int, List[Dict[str, str]]]:
    checked_files: Set[Path] = set()
    for glob_pat in TARGET_DOC_GLOBS:
        for p in REPO_ROOT.glob(glob_pat):
            if p.is_file():
                checked_files.add(p)

    violations: List[Dict[str, str]] = []
    total_citations_checked = 0

    for doc_file in sorted(checked_files):
        citations = extract_paths_from_file(doc_file)
        rel_doc = doc_file.relative_to(REPO_ROOT).as_posix()

        for raw_path, line_no in citations:
            path_cleaned = clean_path_candidate(raw_path, doc_file)
            if not path_cleaned:
                continue

            total_citations_checked += 1
            full_path = (REPO_ROOT / path_cleaned).resolve()

            if not full_path.exists():
                violations.append({
                    "sourceDocument": rel_doc,
                    "line": line_no,
                    "citedPath": path_cleaned,
                    "absoluteTarget": str(full_path),
                })

    return total_citations_checked, violations


def main():
    print("=" * 70)
    print(" Planwise Enterprise — Static Path Citation Verification Gate")
    print("=" * 70)

    total_checked, violations = verify_all_cited_paths()
    print(f"Total citations scanned: {total_checked}")

    if violations:
        print(f"\n[FAIL] Found {len(violations)} non-existent or broken file citation(s):\n")
        for v in violations:
            print(f"  • {v['sourceDocument']}:{v['line']}")
            print(f"    Cited path : {v['citedPath']}")
            print(f"    Target     : {v['absoluteTarget']}\n")
        sys.exit(1)
    else:
        print("[PASS] All cited file paths in documentation and reports exist in repository.")
        sys.exit(0)


if __name__ == "__main__":
    main()
