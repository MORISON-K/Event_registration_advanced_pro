"""Checks that real imports match the Clean Architecture diagram. Run: python tools/check_dependencies.py"""
import ast, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent / "event_registration"
ALLOWED = {
    "domain":         {"domain"},
    "application":    {"domain", "application"},
    "infrastructure": {"domain", "application", "infrastructure"},
    "interface":      {"domain", "application", "infrastructure", "interface"},
}
bad = 0
for layer, allowed in ALLOWED.items():
    used = set()
    for f in (ROOT / layer).glob("*.py"):
        for node in ast.walk(ast.parse(f.read_text())):
            mods = []
            if isinstance(node, ast.ImportFrom):
                if node.level:                       # relative import stays inside the layer
                    continue
                mods = [node.module or ""]
            elif isinstance(node, ast.Import):
                mods = [a.name for a in node.names]
            for m in mods:
                parts = m.split(".")
                if parts[0] == "event_registration" and len(parts) > 1:
                    used.add(parts[1])
                    if parts[1] not in allowed:
                        print(f"VIOLATION: {f.name} ({layer}) imports {m}"); bad += 1
    print(f"{layer:15} depends on: {sorted(used - {layer}) or 'nothing'}")
print("RESULT:", "FAIL" if bad else "OK - dependencies point inward only")
sys.exit(1 if bad else 0)
