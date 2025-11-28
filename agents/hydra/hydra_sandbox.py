import json, random, statistics as stats, pathlib, sys
from datetime import datetime, timezone
def now(): return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
def mock_prices(n=60, base=100.0):
  x=base; out=[]; random.seed(707)
  for _ in range(n): x += random.gauss(0, 0.6); out.append(round(x,2))
  return out
def mock_odds():
  return {"WOLVES@EAGLES":{"home":-115,"away":+105},"TITANS@LIONS":{"home":-102,"away":-102},"BILLS@JETS":{"home":+120,"away":-140}}
def suggest_bets(odds):
  rec=[]; 
  for k,v in odds.items():
    fav = "home" if (v["home"]<0 and abs(v["home"])>abs(v["away"])) else ("away" if v["away"]<0 else ("home" if v["home"]<=-105 else "away"))
    kelly = 0.01 if fav else 0.005
    rec.append({"game":k,"side":fav or "home","kelly_frac":round(kelly,4)})
  return rec
def portfolio_tick(bankroll,recs):
  stakes=[round(bankroll*r["kelly_frac"],2) for r in recs]
  return {"bankroll_start":bankroll,"paper_stakes":stakes,"risk_sum":round(sum(stakes),2),"bankroll_end":bankroll}
def main():
  out = pathlib.Path.home()/ "HYDRA" / "out"; out.mkdir(parents=True, exist_ok=True)
  prices=mock_prices(); odds=mock_odds(); recs=suggest_bets(odds)
  signal = "BUY" if prices[-1]>prices[0] and stats.mean(prices[-10:])>stats.mean(prices[-30:]) else "HOLD"
  payload={"ts":now(),"mode":"sandbox","signal":signal,"prices":prices[-12:],"odds":odds,"recs":recs,"portfolio":portfolio_tick(10000.0,recs)}
  (out/"hydra_signal.json").write_text(json.dumps(payload,indent=2))
  print(f"[HYDRA] sandbox tick {payload['ts']} → {out/'hydra_signal.json'}")
if __name__=="__main__":
  try: main()
  except Exception as e: print(f"[HYDRA] sandbox ERROR: {e}", file=sys.stderr); sys.exit(1)
