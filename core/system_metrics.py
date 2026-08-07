"""Lightweight Windows GPU and per-program resource sampling."""

import csv
import os
import re
import subprocess

import psutil


CREATE_NO_WINDOW = 0x08000000
GPU_COUNTER = r"\GPU Engine(*)\Utilization Percentage"


def sample_windows_gpu(timeout=5.0):
    """Return Task-Manager-style total GPU usage and usage grouped by PID.

    Windows exposes vendor-neutral GPU Engine counters, so this supports Intel,
    AMD and NVIDIA without loading a vendor SDK. Overall and per-process values
    use the busiest physical engine, matching the most useful dashboard view.
    """
    if os.name != "nt":
        return None, {}

    system_root = os.environ.get("SystemRoot", r"C:\Windows")
    typeperf = os.path.join(system_root, "System32", "typeperf.exe")
    try:
        result = subprocess.run(
            [typeperf, GPU_COUNTER, "-sc", "1"],
            capture_output=True,
            text=True,
            errors="replace",
            timeout=timeout,
            creationflags=CREATE_NO_WINDOW,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return None, {}

    if result.returncode != 0:
        return None, {}

    csv_rows = []
    for line in result.stdout.splitlines():
        if not line.strip().startswith('"'):
            continue
        try:
            csv_rows.append(next(csv.reader([line])))
        except (csv.Error, StopIteration):
            continue
    if len(csv_rows) < 2:
        return None, {}

    headers = csv_rows[0]
    values = csv_rows[-1]
    engine_totals = {}
    process_engines = {}
    for header, raw_value in zip(headers[1:], values[1:]):
        pid_match = re.search(r"pid_(\d+)", header, re.IGNORECASE)
        luid_match = re.search(r"luid_(.+?)_phys_", header, re.IGNORECASE)
        engine_match = re.search(
            r"_phys_(\d+)_eng_(\d+)_engtype_([^\\)]+)", header, re.IGNORECASE
        )
        if not (pid_match and luid_match and engine_match):
            continue
        try:
            value = max(0.0, float(raw_value.replace(",", ".")))
        except (TypeError, ValueError):
            continue

        pid = int(pid_match.group(1))
        engine_key = (
            luid_match.group(1),
            engine_match.group(1),
            engine_match.group(2),
            engine_match.group(3).lower(),
        )
        engine_totals[engine_key] = engine_totals.get(engine_key, 0.0) + value
        process_key = (pid,) + engine_key
        process_engines[process_key] = process_engines.get(process_key, 0.0) + value

    if not engine_totals:
        # The counter exists but there are currently no active GPU engines.
        return 0.0, {}

    total_usage = min(100.0, max(engine_totals.values()))
    usage_by_pid = {}
    for process_key, value in process_engines.items():
        pid = process_key[0]
        usage_by_pid[pid] = max(usage_by_pid.get(pid, 0.0), min(100.0, value))
    return total_usage, usage_by_pid


def sample_program_usage(gpu_by_pid, process_cache, limit=10):
    """Aggregate CPU, RAM and GPU percentages by executable name."""
    logical_cpus = max(1, psutil.cpu_count(logical=True) or 1)
    seen_pids = set()
    programs = {}

    for listed_process in psutil.process_iter(["pid", "name", "memory_percent", "memory_info"]):
        try:
            pid = listed_process.info["pid"]
            if pid == 0:
                continue
            seen_pids.add(pid)
            process = process_cache.get(pid)
            if process is None or not process.is_running():
                process = listed_process
                process.cpu_percent(interval=None)
                process_cache[pid] = process
                cpu_percent = 0.0
            else:
                cpu_percent = max(0.0, process.cpu_percent(interval=None) / logical_cpus)

            name = (listed_process.info.get("name") or f"PID {pid}").strip()
            memory_percent = max(0.0, listed_process.info.get("memory_percent") or 0.0)
            memory_info = listed_process.info.get("memory_info")
            memory_mb = (memory_info.rss / (1024 * 1024)) if memory_info else 0.0
            gpu_percent = max(0.0, gpu_by_pid.get(pid, 0.0))
        except (psutil.AccessDenied, psutil.NoSuchProcess, psutil.ZombieProcess, OSError):
            continue

        key = name.casefold()
        row = programs.setdefault(
            key,
            {"name": name, "cpu": 0.0, "ram": 0.0, "ram_mb": 0.0, "gpu": 0.0},
        )
        row["cpu"] += cpu_percent
        row["ram"] += memory_percent
        row["ram_mb"] += memory_mb
        row["gpu"] += gpu_percent

    for stale_pid in set(process_cache) - seen_pids:
        process_cache.pop(stale_pid, None)

    rows = list(programs.values())
    for row in rows:
        row["cpu"] = min(100.0, row["cpu"])
        row["ram"] = min(100.0, row["ram"])
        row["gpu"] = min(100.0, row["gpu"])
    rows.sort(key=lambda row: (max(row["cpu"], row["ram"], row["gpu"]), row["ram_mb"]), reverse=True)
    return rows[:limit]
