from flask import Flask, render_template, request
import copy

app = Flask(__name__)

# --- ฟังก์ชันจำลอง FCFS ---
def simulate_fcfs(processes):
    procs = sorted(copy.deepcopy(processes), key=lambda x: (x["at"], x["id"]))
    time = 0
    results = []
    gantt_blocks = []
    for p in procs:
        if time < p["at"]:
            gantt_blocks.append({"process": "Idle", "start": time, "end": p["at"]})
            time = p["at"]
        start = time
        ct = start + p["bt"]
        time = ct
        gantt_blocks.append({"process": p["id"], "start": start, "end": ct})
        tat = ct - p["at"]
        wt = tat - p["bt"]
        results.append({"id": p["id"], "at": p["at"], "bt": p["bt"], "ct": ct, "tat": tat, "wt": wt})
    avg_tat = sum(r["tat"] for r in results) / len(results) if results else 0
    avg_wt = sum(r["wt"] for r in results) / len(results) if results else 0
    return results, avg_tat, avg_wt, gantt_blocks

# --- ฟังก์ชันจำลอง SJF ---
def simulate_sjf(processes):
    procs = [dict(p, remaining=p["bt"], completed=False) for p in copy.deepcopy(processes)]
    time = 0
    completed = 0
    n = len(procs)
    results = {}
    gantt_blocks = []
    while completed < n:
        available = [p for p in procs if not p["completed"] and p["at"] <= time]
        if not available:
            next_at = min(p["at"] for p in procs if not p["completed"])
            gantt_blocks.append({"process": "Idle", "start": time, "end": next_at})
            time = next_at
            continue
        p = min(available, key=lambda x: (x["bt"], x["at"], x["id"]))
        start = time
        ct = start + p["bt"]
        time = ct
        p["completed"] = True
        completed += 1
        gantt_blocks.append({"process": p["id"], "start": start, "end": ct})
        tat = ct - p["at"]
        wt = tat - p["bt"]
        results[p["id"]] = {"id": p["id"], "at": p["at"], "bt": p["bt"], "ct": ct, "tat": tat, "wt": wt}
    res_list = [results[p["id"]] for p in sorted(copy.deepcopy(processes), key=lambda x: x["id"])]
    avg_tat = sum(r["tat"] for r in res_list) / n if n else 0
    avg_wt = sum(r["wt"] for r in res_list) / n if n else 0
    return res_list, avg_tat, avg_wt, gantt_blocks

# --- ฟังก์ชันจำลอง Round Robin ---
def simulate_rr(processes, quantum):
    procs = [{"id": p["id"], "at": p["at"], "bt": p["bt"], "rem": p["bt"], "ct": 0} for p in copy.deepcopy(processes)]
    time = 0
    queue = []
    n = len(procs)
    completed = 0
    gantt_blocks = []
    inarrival = sorted(procs, key=lambda x: (x["at"], x["id"]))
    if inarrival and inarrival[0]["at"] > time:
        gantt_blocks.append({"process": "Idle", "start": time, "end": inarrival[0]["at"]})
        time = inarrival[0]["at"]
    while completed < n:
        while inarrival and inarrival[0]["at"] <= time:
            queue.append(inarrival.pop(0))
        if not queue:
            if inarrival:
                next_at = inarrival[0]["at"]
                gantt_blocks.append({"process": "Idle", "start": time, "end": next_at})
                time = next_at
                continue
            else:
                break
        curr = queue.pop(0)
        run_t = min(quantum, curr["rem"])
        start = time
        for _ in range(run_t):
            time += 1
            curr["rem"] -= 1
            while inarrival and inarrival[0]["at"] <= time:
                queue.append(inarrival.pop(0))
        gantt_blocks.append({"process": curr["id"], "start": start, "end": time})
        if curr["rem"] == 0:
            curr["ct"] = time
            completed += 1
        else:
            queue.append(curr)
    results = []
    for p in procs:
        tat = p["ct"] - p["at"]
        wt = tat - p["bt"]
        results.append({"id": p["id"], "at": p["at"], "bt": p["bt"], "ct": p["ct"], "tat": tat, "wt": wt})
    avg_tat = sum(r["tat"] for r in results) / n if n else 0
    avg_wt = sum(r["wt"] for r in results) / n if n else 0
    return results, avg_tat, avg_wt, gantt_blocks

@app.route("/", methods=["GET", "POST"])
def index():
    # ค่าเริ่มต้นจำลอง
    default_procs = [
        {"id": "P1", "at": 0, "bt": 5},
        {"id": "P2", "at": 1, "bt": 3},
        {"id": "P3", "at": 2, "bt": 1},
        {"id": "P4", "at": 4, "bt": 2}
    ]
    quantum = 2
    active_algo = "fcfs"
    results, avg_tat, avg_wt, gantt = simulate_fcfs(default_procs)

    if request.method == "POST":
        active_algo = request.form.get("algo", "fcfs")
        quantum = int(request.form.get("quantum", 2))
        
        # ดึงข้อมูลที่ผู้ใช้กรอกเข้ามาจากฟอร์ม
        ids = request.form.getlist("pid[]")
        ats = request.form.getlist("at[]")
        bts = request.form.getlist("bt[]")
        
        user_procs = []
        for i in range(len(ids)):
            if ids[i] and bts[i]:
                user_procs.append({
                    "id": ids[i],
                    "at": int(ats[i]) if ats[i] else 0,
                    "bt": int(bts[i]) if bts[i] else 1
                })
        
        if user_procs:
            if active_algo == "fcfs":
                results, avg_tat, avg_wt, gantt = simulate_fcfs(user_procs)
            elif active_algo == "sjf":
                results, avg_tat, avg_wt, gantt = simulate_sjf(user_procs)
            elif active_algo == "rr":
                results, avg_tat, avg_wt, gantt = simulate_rr(user_procs, quantum)
            default_procs = user_procs

    return render_template("index.html", procs=default_procs, quantum=quantum, active_algo=active_algo, results=results, avg_tat=avg_tat, avg_wt=avg_wt, gantt=gantt)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
    