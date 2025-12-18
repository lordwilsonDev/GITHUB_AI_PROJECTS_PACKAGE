import os, json, time, subprocess

TASKS_PATH = os.path.expanduser("~/nanoapex-rade/vy_tasks.jsonl")

def load_tasks():
    tasks = []
    if not os.path.exists(TASKS_PATH):
        return tasks
    with open(TASKS_PATH, "r") as f:
        for line in f:
            line = line.strip()
            if line:
                tasks.append(json.loads(line))
    return tasks

def run_task(task):
    print(f"▶ Running: {task['id']}")
    subprocess.run(task["command"], shell=True)

if __name__ == "__main__":
    print("🔁 Vy Task Runner Online")
    next_runs = {}
    while True:
        tasks = load_tasks()
        now = time.time()
        for task in tasks:
            interval = task.get("interval_seconds", 1800)
            tid = task["id"]
            if tid not in next_runs or now >= next_runs[tid]:
                next_runs[tid] = now + interval
                run_task(task)
        time.sleep(5)

