import json
c = json.load(open("cache_geocoding.json", encoding="utf-8"))
c["Thüringen"] = [47.21, 9.79]
c["Leningrado"] = c["San Pietroburgo"]
json.dump(c, open("cache_geocoding.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("fatto")
