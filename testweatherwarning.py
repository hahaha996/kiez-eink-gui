import requests, datetime as dt

URL = "https://s3.eu-central-1.amazonaws.com/app-prod-static.warnwetter.de/v16/gemeinde_warnings_v2.json"
 #nina	(3)[ "110070007007", "Tempelhof-Schöneberg", "Stadt-/Ortsteil bzw. Stadtbezirk" ]
j = requests.get(URL, timeout=15).json()
print("test")
print(j)
berlin = [w for w in j.get("warnings", []) if "berlin" in (w.get("regionName","").lower())]
for w in berlin:
    def ts(ms): 
        return dt.datetime.fromtimestamp(ms/1000).strftime("%Y-%m-%d %H:%M")
    print(f"[{w.get('level')}] {w.get('event')}  {ts(w['start'])} ? {ts(w['end'])}")
    print(w.get("description","").strip(), "\n")