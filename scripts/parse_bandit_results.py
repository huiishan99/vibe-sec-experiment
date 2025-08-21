# scripts/parse_bandit_results.py
import os, json, csv, re, glob, datetime
from collections import defaultdict

RUN_ID = os.getenv("RUN_ID") or datetime.datetime.now().strftime("main_%Y%m%d_%H%M")
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
REPORT_DIR = os.path.join(ROOT, "eval", "bandit_reports", RUN_ID)
OUT_SAMPLES = os.path.join(ROOT, "eval", f"bandit_samples_{RUN_ID}.csv")
OUT_AGG = os.path.join(ROOT, "eval", f"bandit_aggregated_{RUN_ID}.csv")

SEV_W = {"LOW":1,"MEDIUM":2,"HIGH":3}

def parse_filename(fp: str):
    # e.g. eval/bandit_reports/RUNID/outputs_main..._baseline_task01_sql_s101.py.json
    base = os.path.basename(fp)
    arm = "baseline" if "_baseline_" in base else "improved"
    m_task = re.search(r"(task\d+_[a-z]+)_s(\d+)\.py\.json", base)
    task = m_task.group(1) if m_task else "unknown"
    seed = int(m_task.group(2)) if m_task else -1
    return task, arm, seed

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
        task, arm, seed = parse_filename(fp)
        ic, swc, vp = parse_json(fp)
        rows.append({"RUN_ID":RUN_ID,"task":task,"arm":arm,"seed":seed,"IC":ic,"SWC":swc,"VP":vp,"file":fp})

    # 写样本级
    os.makedirs(os.path.join(ROOT, "eval"), exist_ok=True)
    with open(OUT_SAMPLES, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["RUN_ID","task","arm","seed","VP","IC","SWC","file"])
        w.writeheader()
        for r in rows: w.writerow(r)
    print(f"[ok] samples -> {OUT_SAMPLES} ({len(rows)} rows)")

    # 汇总
    g = defaultdict(list)
    for r in rows:
        g[(r["task"], r["arm"])].append(r)
    with open(OUT_AGG, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["RUN_ID","task","arm","VP_pct","IC_mean","SWC_mean","n"])
        w.writeheader()
        for (task, arm), lst in sorted(g.items()):
            n = len(lst)
            vp_pct = 100.0 * sum(x["VP"] for x in lst) / max(n,1)
            ic_mean = sum(x["IC"] for x in lst) / max(n,1)
            swc_mean = sum(x["SWC"] for x in lst) / max(n,1)
            w.writerow({"RUN_ID":RUN_ID,"task":task,"arm":arm,
                        "VP_pct":round(vp_pct,1),
                        "IC_mean":round(ic_mean,2),
                        "SWC_mean":round(swc_mean,2),
                        "n":n})
    print(f"[ok] aggregated -> {OUT_AGG}")

if __name__ == "__main__":
    main()
