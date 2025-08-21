# scripts/run_bandit.py
import os, json, subprocess, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OUT_DIR = os.path.join(ROOT, "outputs")
REPORT_DIR = os.path.join(ROOT, "eval", "bandit_reports")
os.makedirs(REPORT_DIR, exist_ok=True)

BANDIT_CMD = ["bandit", "-r", "-f", "json", "-q"]  # -q 安静些；-r 递归模式也能扫单文件

def scan_one(pyfile: str):
    rel = os.path.relpath(pyfile, ROOT).replace("\\", "/")
    out_json = os.path.join(REPORT_DIR, rel.replace("/", "_") + ".json")
    os.makedirs(os.path.dirname(out_json), exist_ok=True)

    cmd = BANDIT_CMD + [pyfile]
    res = subprocess.run(cmd, capture_output=True, text=True)

    # 退出码含义：0=无问题，1=发现问题，2=执行错误
    if res.returncode in (0, 1) and res.stdout.strip():
        with open(out_json, "w", encoding="utf-8") as f:
            f.write(res.stdout)
        status = "OK" if res.returncode == 0 else "ISSUES"
        print(f"[bandit] {status} -> {out_json}")
    else:
        # 真正失败才报警
        print(f"[bandit] ERROR {pyfile}\n{res.stderr}", file=sys.stderr)

def main():
    any_found = False
    for variant in ("baseline", "improved"):
        folder = os.path.join(OUT_DIR, variant)
        if not os.path.isdir(folder):
            continue
        for fn in os.listdir(folder):
            if fn.endswith(".py"):
                any_found = True
                scan_one(os.path.join(folder, fn))
    if not any_found:
        print(f"[warn] No .py files under {OUT_DIR}/baseline or {OUT_DIR}/improved")

if __name__ == "__main__":
    main()
