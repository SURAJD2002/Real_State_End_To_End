"""
Script to convert part2, part3, part4 to safe raw multiline strings and replace dynamic placeholders.
"""

import re

# Fix Part 2
with open("scripts/report_sections/part2_site_statutory_cpsat.py", "r", encoding="utf-8") as f:
    p2 = f.read()

# Replace badges and diagrams with markers
p2 = p2.replace('{badge("BLOCKED", "not-implemented")}', '[[BADGE_BLOCKED]]')
p2 = p2.replace('{badge("CONDITIONAL", "partially")}', '[[BADGE_CONDITIONAL]]')
p2 = p2.replace('{badge("UNLOCKED", "implemented")}', '[[BADGE_UNLOCKED]]')
p2 = p2.replace('{diagram_04_cpsat_solver()}', '[[DIAGRAM_04]]')

# Unescape double curly braces inside code blocks in part 2
p2 = p2.replace('{{', '{').replace('}}', '}')

# Convert html = f""" to html = r'''
p2 = re.sub(r'html\s*=\s*f"""', "html = r'''", p2)
p2 = re.sub(r'"""\s*return html', "'''\n    html = html.replace('[[BADGE_BLOCKED]]', badge('BLOCKED', 'not-implemented'))\n    html = html.replace('[[BADGE_CONDITIONAL]]', badge('CONDITIONAL', 'partially'))\n    html = html.replace('[[BADGE_UNLOCKED]]', badge('UNLOCKED', 'implemented'))\n    html = html.replace('[[DIAGRAM_04]]', diagram_04_cpsat_solver())\n    return html", p2)

with open("scripts/report_sections/part2_site_statutory_cpsat.py", "w", encoding="utf-8") as f:
    f.write(p2)
print("Part 2 fixed.")


# Fix Part 3
with open("scripts/report_sections/part3_geometry_cad_qto.py", "r", encoding="utf-8") as f:
    p3 = f.read()

p3 = p3.replace('{diagram_05_manifold3d_geometry()}', '[[DIAGRAM_05]]')
p3 = re.sub(r'html\s*=\s*f"""', "html = r'''", p3)
p3 = re.sub(r'"""\s*return html', "'''\n    html = html.replace('[[DIAGRAM_05]]', diagram_05_manifold3d_geometry())\n    return html", p3)

with open("scripts/report_sections/part3_geometry_cad_qto.py", "w", encoding="utf-8") as f:
    f.write(p3)
print("Part 3 fixed.")


# Fix Part 4
with open("scripts/report_sections/part4_review_release_ifc.py", "r", encoding="utf-8") as f:
    p4 = f.read()

p4 = p4.replace('{diagram_07_change_propagation_dag()}', '[[DIAGRAM_07]]')
p4 = p4.replace('{diagram_06_engineer_review_gates()}', '[[DIAGRAM_06]]')
p4 = p4.replace('{{id}}', '{id}').replace('{{g}}', '{g}')
p4 = re.sub(r'html\s*=\s*f"""', "html = r'''", p4)
p4 = re.sub(r'"""\s*return html', "'''\n    html = html.replace('[[DIAGRAM_07]]', diagram_07_change_propagation_dag())\n    html = html.replace('[[DIAGRAM_06]]', diagram_06_engineer_review_gates())\n    return html", p4)

with open("scripts/report_sections/part4_review_release_ifc.py", "w", encoding="utf-8") as f:
    f.write(p4)
print("Part 4 fixed.")
