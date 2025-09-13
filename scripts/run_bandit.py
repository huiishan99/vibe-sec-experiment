"""
Run Bandit on generated Python files and write JSON reports.

Outputs:
  eval/bandit_reports/<RUN_ID>/*.json
  eval/bandit_reports/<RUN_ID>/_meta.json  (RUN_ID + bandit version)
"""
import os
import sys
import json
import subprocess
import datetime

RUN_ID = os.getenv("RUN_ID") or datetime.datetime.now().strftime("main_%Y%m%d_%H%M")
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OUT_ROOT = os.path.join(ROOT, "outputs", RUN_ID)
REPORT_DIR = os.path.join(ROOT, "eval", "bandit_reports", RUN_ID)
os.makedirs(REPORT_DIR, exist_ok=True)

def get_bandit_version() -> str:
    try:
        out = subprocess.check_output(["bandit", "--version"], text=True).strip()
        return out
    except Exception:
        return "unknown"

def scan_file(pyfile: str):
    rel = os.path.relpath(pyfile, ROOT).replace("\\", "/")
    out_name = rel.replace("/", "_") + ".json"
    out_json = os.path.join(REPORT_DIR, out_name)
    cmd = ["bandit", "-f", "json", "-q", pyfile]  # single file scan
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode in (0, 1) and res.stdout.strip():
        with open(out_json, "w", encoding="utf-8") as f:
            f.write(res.stdout)
        tag = "OK" if res.returncode == 0 else "ISSUES"
        print(f"[bandit] {tag} -> {out_json}")
    else:
        print(f"[bandit] ERROR {pyfile}\n{res.stderr}", file=sys.stderr)

def main():
    # meta info
    with open(os.path.join(REPORT_DIR, "_meta.json"), "w", encoding="utf-8") as f:
        json.dump({"RUN_ID": RUN_ID, "bandit_version": get_bandit_version()}, f, indent=2)

    if not os.path.isdir(OUT_ROOT):
        print(f"[warn] outputs/{RUN_ID} not found")
        return
    for root, _, files in os.walk(OUT_ROOT):
        for fn in files:
            if fn.endswith(".py"):
                scan_file(os.path.join(root, fn))

if __name__ == "__main__":
    main()
