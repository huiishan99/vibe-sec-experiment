"""
Aggregate probe JSONs into a CSV with per-sample and per-(task,model,arm) RPR.

Input:
  eval/probes_reports/<RUN_ID>/*.json

Output:
  eval/probes_samples_<RUN_ID>.csv
  eval/probes_aggregated_<RUN_ID>.csv
"""
import os, json, csv, glob, datetime
from collections import defaultdict

RUN_ID = os.getenv("RUN_ID") or datetime.datetime.now().strftime("main_%Y%m%d_%H%M")
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
IN_DIR = os.path.join(ROOT, "eval", "probes_reports", RUN_ID)
OUT_SAMPLES = os.path.join(ROOT, "eval", f"probes_samples_{RUN_ID}.csv")
OUT_AGG = os.path.join(ROOT, "eval", f"probes_aggregated_{RUN_ID}.csv")

def main():
    rows = []
    for fp in glob.glob(os.path.join(IN_DIR, "*.json")):
        with open(fp, "r", encoding="utf-8") as f:
            data = json.load(f)
        task = data["task"]; model = data["model"]; arm = data["arm"]; seed = data["seed"]
        probes = data.get("probes", {})
        total = max(len(probes), 1)
        passed = sum(1 for v in probes.values() if v)
        rpr = passed / total
        rows.append({"RUN_ID":RUN_ID,"task":task,"model":model,"arm":arm,"seed":seed,"RPR":round(rpr,3),"num_probes":total,"file":os.path.basename(fp)})

    os.makedirs(os.path.join(ROOT, "eval"), exist_ok=True)
    with open(OUT_SAMPLES, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["RUN_ID","task","model","arm","seed","RPR","num_probes","file"])
        w.writeheader()
        for r in rows: w.writerow(r)
    print(f"[ok] probes samples -> {OUT_SAMPLES} ({len(rows)} rows)")

    g = defaultdict(list)
    for r in rows:
        g[(r["task"], r["model"], r["arm"])].append(r)

    with open(OUT_AGG, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["RUN_ID","task","model","arm","RPR_mean","n"])
        w.writeheader()
        for (task, model, arm), lst in sorted(g.items()):
            n = len(lst)
            mean_rpr = sum(x["RPR"] for x in lst) / max(n,1)
            w.writerow({"RUN_ID":RUN_ID,"task":task,"model":model,"arm":arm,"RPR_mean":round(mean_rpr,3),"n":n})
    print(f"[ok] probes aggregated -> {OUT_AGG}")

if __name__ == "__main__":
    main()
