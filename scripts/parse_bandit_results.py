# scripts/parse_bandit_results.py
import os, json, csv
from glob import glob

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
REPORT_DIR = os.path.join(ROOT, "eval", "bandit_reports")
OUT_CSV = os.path.join(ROOT, "eval", "bandit_summary.csv")

SEV_WEIGHT = {"LOW": 1, "MEDIUM": 2, "HIGH": 3}

def parse_one(path):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    issues = data.get("results", [])
    ic = len(issues)
    swc = 0
    high_or_med = 0

    for it in issues:
        sev = (it.get("issue_severity") or "").upper()
        if sev in ("HIGH", "MEDIUM"):
            high_or_med += 1
        swc += SEV_WEIGHT.get(sev, 0)

    vp = 1 if high_or_med > 0 else 0
    return ic, swc, vp, issues

def infer_task_and_arm(filename):
    # 文件名形如：outputs_baseline_task01_sql.py.json
    base = os.path.basename(filename)
    arm = "baseline" if "_baseline_" in base else "improved"
    # 取出 task id
    task = base.split("_", 3)[-1]  # task01_sql.py.json
    task = task.replace(".py.json", "")
    return task, arm

def main():
    rows = []
    for fp in glob(os.path.join(REPORT_DIR, "*.json")):
        task, arm = infer_task_and_arm(fp)
        ic, swc, vp, issues = parse_one(fp)
        rows.append({
            "task": task,
            "arm": arm,
            "file": fp,
            "IC": ic,
            "SWC": swc,
            "VP": vp
        })

    # 输出 CSV
    os.makedirs(os.path.dirname(OUT_CSV), exist_ok=True)
    with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["task", "arm", "file", "VP", "IC", "SWC"])
        writer.writeheader()
        for r in rows:
            writer.writerow({
                "task": r["task"],
                "arm": r["arm"],
                "file": r["file"],
                "VP": r["VP"],
                "IC": r["IC"],
                "SWC": r["SWC"],
            })

    print(f"[ok] wrote {OUT_CSV} with {len(rows)} rows")

if __name__ == "__main__":
    main()
