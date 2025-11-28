import json, pathlib, datetime
p = pathlib.Path.home()/ "HYDRA" / "out"
day = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%d")
src = p/"hydra_signal.json"; outd = p/"daily"; outd.mkdir(exist_ok=True, parents=True)
data = json.loads(src.read_text()) if src.exists() else {"note":"no hydra_signal"}
data.update({"day":day})
(outd/f"{day}.json").write_text(json.dumps(data,indent=2))
(outd/f"{day}.txt").write_text(f"signal={data.get('signal')} recs={len(data.get('recs',[]))} ts={data.get('ts')}\n")
(outd/"daily_latest.json").write_text(json.dumps({"latest":str(outd/f'{day}.json')},indent=2))
print(f"[daily] wrote {day}.json + {day}.txt")
