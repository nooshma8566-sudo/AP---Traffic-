from datetime import datetime, timezone
from math import asin, cos, radians, sin, sqrt

from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

CITIES = [
	{"id": "alluri-sitharama-raju", "name": "Alluri Sitharama Raju", "headquarters": "Paderu", "district": "Alluri Sitharama Raju", "lat": 18.0833, "lng": 82.6667},
	{"id": "anakapalli", "name": "Anakapalli", "headquarters": "Anakapalli", "district": "Anakapalli", "lat": 17.6913, "lng": 83.0039},
	{"id": "ananthapuramu", "name": "Ananthapuramu", "headquarters": "Anantapuramu", "district": "Ananthapuramu", "lat": 14.6819, "lng": 77.6006},
	{"id": "annamayya", "name": "Annamayya", "headquarters": "Rayachoti", "district": "Annamayya", "lat": 14.0570, "lng": 78.7510},
	{"id": "bapatla", "name": "Bapatla", "headquarters": "Bapatla", "district": "Bapatla", "lat": 15.9040, "lng": 80.4680},
	{"id": "chitoor", "name": "Chittoor", "headquarters": "Chittoor", "district": "Chittoor", "lat": 13.2172, "lng": 79.1003},
	{"id": "konaseema", "name": "Dr. B. R. Ambedkar Konaseema", "headquarters": "Amalapuram", "district": "Dr. B. R. Ambedkar Konaseema", "lat": 16.5780, "lng": 82.0060},
	{"id": "east-godavari", "name": "East Godavari", "headquarters": "Rajamahendravaram", "district": "East Godavari", "lat": 17.0005, "lng": 81.8040},
	{"id": "eluru", "name": "Eluru", "headquarters": "Eluru", "district": "Eluru", "lat": 16.7107, "lng": 81.0952},
	{"id": "guntur", "name": "Guntur", "headquarters": "Guntur", "district": "Guntur", "lat": 16.3067, "lng": 80.4365},
	{"id": "kakinada", "name": "Kakinada", "headquarters": "Kakinada", "district": "Kakinada", "lat": 16.9891, "lng": 82.2475},
	{"id": "krishna", "name": "Krishna", "headquarters": "Machilipatnam", "district": "Krishna", "lat": 16.1875, "lng": 81.1389},
	{"id": "kurnool", "name": "Kurnool", "headquarters": "Kurnool", "district": "Kurnool", "lat": 15.8281, "lng": 78.0373},
	{"id": "nandyal", "name": "Nandyal", "headquarters": "Nandyal", "district": "Nandyal", "lat": 15.4786, "lng": 78.4836},
	{"id": "ntr", "name": "NTR", "headquarters": "Vijayawada", "district": "NTR", "lat": 16.5062, "lng": 80.6480},
	{"id": "palnadu", "name": "Palnadu", "headquarters": "Narasaraopet", "district": "Palnadu", "lat": 16.2350, "lng": 80.0490},
	{"id": "parvathipuram-manyam", "name": "Parvathipuram Manyam", "headquarters": "Parvathipuram", "district": "Parvathipuram Manyam", "lat": 18.7830, "lng": 83.4250},
	{"id": "prakasam", "name": "Prakasam", "headquarters": "Ongole", "district": "Prakasam", "lat": 15.5057, "lng": 80.0499},
	{"id": "srikakulam", "name": "Srikakulam", "headquarters": "Srikakulam", "district": "Srikakulam", "lat": 18.2949, "lng": 83.8938},
	{"id": "spsr-nellore", "name": "SPSR Nellore", "headquarters": "Nellore", "district": "SPSR Nellore", "lat": 14.4426, "lng": 79.9865},
	{"id": "sri-sathya-sai", "name": "Sri Sathya Sai", "headquarters": "Puttaparthi", "district": "Sri Sathya Sai", "lat": 14.1650, "lng": 77.8110},
	{"id": "tirupati", "name": "Tirupati", "headquarters": "Tirupati", "district": "Tirupati", "lat": 13.6288, "lng": 79.4192},
	{"id": "visakhapatnam", "name": "Visakhapatnam", "headquarters": "Visakhapatnam", "district": "Visakhapatnam", "lat": 17.6868, "lng": 83.2185},
	{"id": "vizianagaram", "name": "Vizianagaram", "headquarters": "Vizianagaram", "district": "Vizianagaram", "lat": 18.1067, "lng": 83.3956},
	{"id": "west-godavari", "name": "West Godavari", "headquarters": "Bhimavaram", "district": "West Godavari", "lat": 16.5449, "lng": 81.5212},
	{"id": "ysr-kadapa", "name": "YSR Kadapa", "headquarters": "Kadapa", "district": "YSR Kadapa", "lat": 14.4674, "lng": 78.8241},
]
UNITS = [f"AP-{number:02}" for number in range(1, 13)]
STATUSES = {"New", "Acknowledged", "Dispatched", "Monitoring", "Resolved"}
MODES = {"Adaptive", "Fixed-time", "Manual"}
PHASES = {"Red", "Amber", "Green"}

signals = []
incidents = []
roads = []
corridors = []

for index, city in enumerate(CITIES):
	lat, lng = city["lat"], city["lng"]
	signals.extend([
		{"id": f"SIG-{index * 2 + 1:03}", "city": city["id"], "name": f"{city['headquarters']} Central Junction", "mode": "Adaptive", "phase": "Green", "cycle_seconds": 90, "health": "Online", "lat": lat + 0.012, "lng": lng + 0.009},
		{"id": f"SIG-{index * 2 + 2:03}", "city": city["id"], "name": f"{city['headquarters']} Bypass Junction", "mode": "Fixed-time", "phase": "Red", "cycle_seconds": 75, "health": "Maintenance" if index == 6 else "Online", "lat": lat - 0.011, "lng": lng - 0.008},
	])
	roads.extend([
		{"id": f"RD-{index * 2 + 1:03}", "city": city["id"], "name": f"{city['headquarters']} Main Road", "state": ["slow", "clear", "busy", "clear"][index % 4], "points": [[lat - 0.018, lng - 0.012], [lat - 0.006, lng], [lat + 0.008, lng + 0.012]]},
		{"id": f"RD-{index * 2 + 2:03}", "city": city["id"], "name": f"{city['headquarters']} Bypass", "state": ["clear", "busy", "clear", "slow"][index % 4], "points": [[lat + 0.018, lng - 0.015], [lat + 0.008, lng - 0.003], [lat - 0.008, lng + 0.014]]},
	])
	corridors.append({
		"city": city["id"],
		"highways": [{"name": f"{city['headquarters']} highway corridor (demo)", "location": f"{city['headquarters']} outer approach", "lat": lat + 0.027, "lng": lng - 0.018}],
		"one_ways": [{"name": f"{city['headquarters']} central market one-way (demo)", "location": f"{city['headquarters']} central market loop", "lat": lat + 0.003, "lng": lng - 0.002}],
		"bypasses": [{"name": f"{city['headquarters']} Bypass", "location": f"{city['headquarters']} bypass junction", "lat": lat - 0.011, "lng": lng - 0.008}],
		"tollgates": [{"name": f"{city['headquarters']} demo toll plaza", "location": f"{city['headquarters']} outer bypass (illustrative site)", "lat": lat - 0.027, "lng": lng + 0.021}],
	})
	incidents.extend([
		{"id": f"INC-{2400 + index * 2}", "city": city["id"], "type": ["Congestion", "Breakdown", "Signal fault", "Road works"][index % 4], "title": ["Slow traffic reported", "Vehicle breakdown", "Signal timing alert", "Road works in progress"][index % 4], "location": f"{city['headquarters']} Main Road", "time": f"{3 + (index * 4) % 41} min ago", "severity": ["high", "medium", "low"][index % 3], "status": ["New", "Monitoring", "Acknowledged", "New", "Dispatched", "Monitoring", "New", "Acknowledged"][index % 8], "unit": UNITS[index % len(UNITS)], "lat": lat + 0.006, "lng": lng + 0.004},
		{"id": f"INC-{2401 + index * 2}", "city": city["id"], "type": "Congestion", "title": "Peak-hour traffic buildup", "location": f"{city['headquarters']} Bypass", "time": f"{9 + (index * 3) % 35} min ago", "severity": "medium", "status": "Resolved" if index % 2 == 0 else "Monitoring", "unit": UNITS[(index + 3) % len(UNITS)], "lat": lat - 0.006, "lng": lng - 0.004},
	])


def selected_city(city_id):
	if city_id in {None, "", "all"}:
		return None
	return next((city for city in CITIES if city["id"] == city_id), False)


def distance_km(start, end):
	lat1, lat2 = radians(start["lat"]), radians(end["lat"])
	delta_lat = lat2 - lat1
	delta_lng = radians(end["lng"] - start["lng"])
	a = sin(delta_lat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(delta_lng / 2) ** 2
	return 6371 * 2 * asin(sqrt(a))


@app.get("/")
def index():
	return render_template("index.html")


@app.get("/api/overview")
def overview():
	city = selected_city(request.args.get("city"))
	if city is False:
		return jsonify({"error": "Unknown city"}), 404
	city_id = city["id"] if city else None
	city_signals = [item for item in signals if city_id is None or item["city"] == city_id]
	city_incidents = [item for item in incidents if city_id is None or item["city"] == city_id]
	city_roads = [item for item in roads if city_id is None or item["city"] == city_id]
	district_inventory = []
	for district in CITIES:
		district_signals = [item for item in signals if item["city"] == district["id"]]
		district_corridors = next(item for item in corridors if item["city"] == district["id"])
		district_inventory.append({
			"district": district["name"],
			"headquarters": district["headquarters"],
			"city": district["id"],
			"counts": {
				"signals": len(district_signals),
				"highways": len(district_corridors["highways"]),
				"one_ways": len(district_corridors["one_ways"]),
				"bypasses": len(district_corridors["bypasses"]),
				"tollgates": len(district_corridors["tollgates"]),
			},
			"locations": {
				"signals": [f"{item['id']} · {item['name']}" for item in district_signals],
				**{key: [f"{item['name']} · {item['location']}" for item in district_corridors[key]] for key in ("highways", "one_ways", "bypasses", "tollgates")},
			},
		})
	active_incidents = [item for item in city_incidents if item["status"] != "Resolved"]
	online_signals = sum(item["health"] == "Online" for item in city_signals)
	return jsonify({
		"updated_at": datetime.now(timezone.utc).isoformat(),
		"cities": CITIES,
		"selected_city": city_id,
		"units": UNITS,
		"metrics": {
			"avg_speed": 31 if city_id is None else 22 + (len(city_id) % 13),
			"active_incidents": len(active_incidents),
			"signals_online": online_signals,
			"signals_total": len(city_signals),
			"network_health": round(100 * online_signals / len(city_signals)) if city_signals else 0,
			"roads_monitored": len(city_roads),
		},
		"incidents": city_incidents,
		"signals": city_signals,
		"roads": city_roads,
		"district_inventory": district_inventory,
		"corridors": [item for item in corridors if city_id is None or item["city"] == city_id],
	})


@app.patch("/api/incidents/<incident_id>")
def update_incident(incident_id):
	incident = next((item for item in incidents if item["id"] == incident_id), None)
	if incident is None:
		return jsonify({"error": "Incident not found"}), 404
	data = request.get_json(silent=True) or {}
	if "status" in data:
		if data["status"] not in STATUSES:
			return jsonify({"error": "Invalid incident status"}), 400
		incident["status"] = data["status"]
	if "unit" in data:
		if data["unit"] not in UNITS:
			return jsonify({"error": "Unknown response unit"}), 400
		incident["unit"] = data["unit"]
	return jsonify(incident)


@app.post("/api/incidents/<incident_id>/resolve")
def resolve_incident(incident_id):
	incident = next((item for item in incidents if item["id"] == incident_id), None)
	if incident is None:
		return jsonify({"error": "Incident not found"}), 404
	incident["status"] = "Resolved"
	return jsonify(incident)


@app.patch("/api/signals/<signal_id>")
def update_signal(signal_id):
	signal = next((item for item in signals if item["id"] == signal_id), None)
	if signal is None:
		return jsonify({"error": "Signal not found"}), 404
	data = request.get_json(silent=True) or {}
	mode = data.get("mode", signal["mode"])
	phase = data.get("phase", signal["phase"])
	cycle_seconds = data.get("cycle_seconds", signal["cycle_seconds"])
	if mode not in MODES or phase not in PHASES:
		return jsonify({"error": "Invalid signal mode or phase"}), 400
	if not isinstance(cycle_seconds, int) or isinstance(cycle_seconds, bool) or not 10 <= cycle_seconds <= 180:
		return jsonify({"error": "Cycle duration must be between 10 and 180 seconds"}), 400
	signal.update(mode=mode, phase=phase, cycle_seconds=cycle_seconds)
	return jsonify(signal)


@app.post("/api/signals/<signal_id>/mode")
def update_signal_mode(signal_id):
	data = request.get_json(silent=True) or {}
	if data.get("mode") not in MODES:
		return jsonify({"error": "Invalid signal mode"}), 400
	signal = next((item for item in signals if item["id"] == signal_id), None)
	if signal is None:
		return jsonify({"error": "Signal not found"}), 404
	signal["mode"] = data["mode"]
	return jsonify(signal)


@app.post("/api/route")
def plan_route():
	data = request.get_json(silent=True) or {}
	start = selected_city(data.get("from"))
	end = selected_city(data.get("to"))
	if not start or not end:
		return jsonify({"error": "Select valid origin and destination cities"}), 400
	if start["id"] == end["id"]:
		return jsonify({"error": "Origin and destination must be different"}), 400
	distance = distance_km(start, end)
	average_speed = 42
	return jsonify({
		"from": start["name"], "to": end["name"], "distance_km": round(distance),
		"eta_minutes": round(distance / average_speed * 60), "traffic": "Demo estimate",
		"points": [[start["lat"], start["lng"]], [end["lat"], end["lng"]]],
	})


if __name__ == "__main__":
	app.run(debug=True)
