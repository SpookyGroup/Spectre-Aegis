import json, pathlib, datetime, glob
root = pathlib.Path.home()/ "HYDRA" / "out"
week = datetime.datetime.now(datetime.timezone.utc).strftime("%G%V")
outd = root/"weekly"; outd.mkdir(parents=True, exist_ok=True)
dailies = sorted(glob.glob(str(root/"daily"/"*.json")))
payload={"week":week,"count":len(dailies),"sources":[str(x) for x in dailies[-7:]]}
(outd/f"weekly_{week}.json").write_text(json.dumps(payload,indent=2))
(outd/"weekly_latest.json").write_text(json.dumps({"latest":str(outd/f'weekly_{week}.json')},indent=2))
print(f"[weekly] wrote weekly_{week}.json")
