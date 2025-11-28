import csv, io, json, random, statistics as stats, datetime as dt, pathlib, urllib.parse, requests
OUT = pathlib.Path.home()/ "HYDRA" / "sim"
OUT.mkdir(parents=True, exist_ok=True)

def now():
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def yahoo_closes(symbol, days=64):
    # Yahoo CSV download via v7 API (no auth); last ~3mo daily
    # We only need Close column; graceful failure → None
    try:
        period2 = int(dt.datetime.now(dt.timezone.utc).timestamp())
        period1 = period2 - 90*24*3600
        base = "https://query1.finance.yahoo.com/v7/finance/download/"
        url = f"{base}{urllib.parse.quote(symbol)}?period1={period1}&period2={period2}&interval=1d&events=history&includeAdjustedClose=true"
        r = requests.get(url, timeout=8)
        r.raise_for_status()
        reader = csv.DictReader(io.StringIO(r.text))
        closes = [round(float(row["Close"]),2) for row in reader if row.get("Close") not in ("null", None, "")]
        return closes[-days:] if len(closes)>=8 else None
    except Exception:
        return None

def mock_closes(n=64, base=100.0):
    x, s = base, []
    for _ in range(n):
        x += random.gauss(0, 0.7)
        s.append(round(x, 2))
    return s

def main():
    symbols = ["SPY","QQQ","IWM","XLF","GLD","BTC-USD"]
    rows = {}
    for s in symbols:
        closes = yahoo_closes(s) or mock_closes()
        mean_s = stats.mean(closes[-32:])
        mean_l = stats.mean(closes)
        drift = (closes[-1]-closes[0])/max(abs(closes[0]),1)
        signal = "BUY" if (closes[-1] > closes[0] and mean_s > mean_l) else "HOLD"
        rows[s] = {
            "close_tail": closes[-16:],
            "mean32": round(mean_s,2),
            "mean_all": round(mean_l,2),
            "drift": round(drift,4),
            "signal": signal
        }
    payload = {"ts": now(), "sim_profile": "HydraHarness-lite-v1.1", "markets": rows}
    (OUT/"hydra_sim_tick.json").write_text(json.dumps(payload, indent=2))
    print(f"[HYDRA·SIM] tick {payload['ts']} {len(rows)} symbols.")
if __name__ == "__main__":
    main()
