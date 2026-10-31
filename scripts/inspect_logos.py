import os

root_dir = os.path.join("behavioral-agentic-ai", "frontend")
for root, dirs, files in os.walk(root_dir):
    for f in files:
        if f.endswith((".html", ".js", ".css")):
            fp = os.path.join(root, f)
            with open(fp, "r", encoding="utf-8", errors="ignore") as file:
                for idx, line in enumerate(file):
                    if any(term in line.lower() for term in ["favicon", "logo-icon", "sidebar-logo"]):
                        rel = os.path.relpath(fp, root_dir)
                        print(f"{rel}:{idx+1} -> {line.strip()[:90]}")
