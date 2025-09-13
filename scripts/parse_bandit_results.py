"""
Parse Bandit JSON reports, produce sample-level and aggregated CSVs.

Input:
  eval/bandit_reports/<RUN_ID>/*.json

Output:
  eval/bandit_samples_<RUN_ID>.csv
  eval/bandit_aggregated_<RUN_ID>.csv
"""
import os, json, csv, re, glob, datetime
from collections import defaultdict

RUN_ID = os.getenv("RUN_ID") or datetime.datetime.now().strftime("main_%Y%m%d_%H%M")
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
REPORT_DIR = os.path.join(ROOT, "eval", "bandit_reports", RUN_ID)
OUT_SAMPLES = os.path.join(ROOT, "eval", f"bandit_samples_{RUN_ID}.csv")
OUT_AGG = os.path.join(ROOT, "eval", f"bandit_aggregated_{RUN_ID}.csv")

SEV_W = {"LOW":1,"MEDIUM":2,"HIGH":3}

def parse_filename(fp: str):
    """
    Supported patterns (json filename is based on scanned .py path):
      outputs/<RUN_ID>/baseline/task01_sql_gemma3-27b-instruct_s101.py -> ..._baseline_task01_sql_gemma3-27b-instruct_s101.py.json
      outputs/<RUN_ID>/improved/task01_sql_gpt-oss-20b_s101.py         -> ..._improved_task01_sql_gpt-oss-20b_s101.py.json
    Fallback to older pattern without model name.
    """
    base = os.path.basename(fp)
    arm = "baseline" if "baseline" in base else "improved" if "improved" in base else "unknown"
    m = re.search(r"(task\d+_[a-z0-9]+)_([a-z0-9\-]+)_s(\d+)\.py\.json", base)
    if m:
        task = m.group(1)
        model = m.group(2).replace("-", ":")
        seed = int(m.group(3))
        return task, model, arm, seed
    m2 = re.search(r"(task\d+_[a-z0-9]+)_s(\d+)\.py\.json", base)
    task = m2.group(1) if m2 else "unknown"
    seed = int(m2.group(2)) if m2 else -1
    return task, "unknown", arm, seed

def parse_json(fp: str):
    with open(fp, "r", encoding="utf-8") as f:
        data = json.load(f)
    issues = data.get("results", [])
    ic = len(issues)
    swc = sum(SEV_W.get((i.get("issue_severity") or "").upper(), 0) for i in issues)
    vp = 1 if any((i.get("issue_severity") or "").upper() in ("HIGH","MEDIUM") for i in issues) else 0
    return ic, swc, vp

def main():
    rows = []
    for fp in glob.glob(os.path.join(REPORT_DIR, "*.json")):
        if os.path.basename(fp).startswith("_meta"):
            continue
        task, model, arm, seed = parse_filename(fp)
        ic, swc, vp = parse_json(fp)
        rows.append({"RUN_ID":RUN_ID,"task":task,"model":model,"arm":arm,"seed":seed,"IC":ic,"SWC":swc,"VP":vp,"file":fp})

    os.makedirs(os.path.join(ROOT, "eval"), exist_ok=True)
    with open(OUT_SAMPLES, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["RUN_ID","task","model","arm","seed","VP","IC","SWC","file"])
        w.writeheader()
        for r in rows: w.writerow(r)
    print(f"[ok] samples -> {OUT_SAMPLES} ({len(rows)} rows)")

    g = defaultdict(list)
    for r in rows:
        g[(r["task"], r["model"], r["arm"])].append(r)

    with open(OUT_AGG, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["RUN_ID","task","model","arm","VP_pct","IC_mean","SWC_mean","n"])
        w.writeheader()
        for (task, model, arm), lst in sorted(g.items()):
            n = len(lst)
            vp_pct = 100.0 * sum(x["VP"] for x in lst) / max(n,1)
            ic_mean = sum(x["IC"] for x in lst) / max(n,1)
            swc_mean = sum(x["SWC"] for x in lst) / max(n,1)
            w.writerow({"RUN_ID":RUN_ID,"task":task,"model":model,"arm":arm,
                        "VP_pct":round(vp_pct,1),
                        "IC_mean":round(ic_mean,2),
                        "SWC_mean":round(swc_mean,2),
                        "n":n})
    print(f"[ok] aggregated -> {OUT_AGG}")

if __name__ == "__main__":
    main()
