import json, csv, sys, time, pathlib, statistics as stats
home = pathlib.Path.home()
out_dir = home/"HYDRA"/"out"
sig = out_dir/"hydra_signal.json"
csv_path = out_dir/"hydra_metrics.csv"
log_path = home/".termux"/"logs"/"ao7_analytics.log"

def load_json(p):
    try:
        return json.loads(p.read_text())
    except Exception as e:
        return {"error": str(e)}

def ensure_headers(path, headers):
    new = not path.exists()
    f = path.open("a", newline="")
    w = csv.DictWriter(f, fieldnames=headers)
    if new: w.writeheader()
    return f, w

def main():
    ts = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    payload = load_json(sig) if sig.exists() else {"mode":"sandbox","signal":"NONE","recs":[],"portfolio":{}}
    recs = payload.get("recs", []) or []
    pf = payload.get("portfolio", {})
    prices = payload.get("prices", [])
    risk_sum = round(pf.get("risk_sum", 0.0), 2)
    bankroll = round(pf.get("bankroll_end", pf.get("bankroll_start", 0.0)), 2)
    n_recs = len(recs)
    kelly_sum = round(sum(r.get("kelly_frac",0.0) for r in recs), 4)
    signal = payload.get("signal","NONE")
    price_chg = round((prices[-1]-prices[0]) if len(prices)>=2 else 0.0, 2)
    row = {
        "ts": ts,
        "mode": payload.get("mode","sandbox"),
        "signal": signal,
        "recs": n_recs,
        "risk_sum": risk_sum,
        "kelly_sum": kelly_sum,
        "bankroll": bankroll,
        "px_delta": price_chg
    }
    headers = list(row.keys())
    f,w = ensure_headers(csv_path, headers)
    try:
        w.writerow(row)
    finally:
        f.close()
    with open(log_path, "a") as lf:
        lf.write(f"[BRIDGE] {ts} mode={row['mode']} sig={signal} recs={n_recs} risk={risk_sum} kelly={kelly_sum} pxΔ={price_chg}\n")
    print(f"[BRIDGE] wrote {csv_path.name} + analytics log")
if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"[BRIDGE] ERROR: {e}", file=sys.stderr)
        sys.exit(0)  # never break AO-7 loop
