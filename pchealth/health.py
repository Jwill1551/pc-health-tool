import platform
import socket
import time
import psutil

# Flag system if numbers are above than usual
## Notes: Defined dictionary "Thresholds" to store pre-defined system values.
THRESHOLDS = {
    "disk": { "warning": 80, "critical": 90 }, # percent
    "memory": { "warning": 85, "critical": 95}, # percent
    "cpu": { "warning": 90 }, # percent
    "uptime": { "warning": 7, "critical": 30 } # days
}

## Notes: 'Grade' or compare the value outputed by the data returend by my system functions with threshold values.
def grade(value, warning, critical=None):
    if critical is not None and value >= critical:
        return "CRITICAL"
    elif value >= warning:
        return "WARNING"
    else:
        return "OK"


# Get hostname, OS, and uptime
def get_system_info():
    boot_time = psutil.boot_time()
    uptime_seconds = time.time() - boot_time #minus boot time
    return {
        "hostname": socket.gethostname(),
        "os": platform.system() + " " + platform.release(),
        "uptime_days": round(uptime_seconds / 86400, 1)
    }

# Get memory information
def get_memory_info():
    mem = psutil.virtual_memory()
    return {
        "total_gb": round(mem.total / 1024**3, 1), # bytes to GB
        "percent_used": mem.percent,
    }

# Get disk informaiton
def get_disk_info():
    disks = []
    for part in psutil.disk_partitions():
        try:
            usage = psutil.disk_usage(part.mountpoint)
        except PermissionError:
            continue # skip drives we can't read, like an empty card.
        disks.append({
            "mount": part.mountpoint,
            "total_gb": round(usage.total / 1024**3, 1),
            "percent_used": usage.percent,
        })
    return disks

# Get CPU information
def get_cpu_info():
    cpu_usage = psutil.cpu_percent(interval=1)
    cpu_cores = psutil.cpu_count()

    return {
        "percent_used": cpu_usage,
        "cores": cpu_cores
    }
    
if __name__ == "__main__":
    system = get_system_info()
    memory = get_memory_info()
    cpu = get_cpu_info()
    disks = get_disk_info()
    
    print(f"Computer: {system['hostname']} ({system['os']})")

    ## Note: Passed 'THRESHOLDS' dictionary memory location to variable 'mem_limits'.
    mem_limits = THRESHOLDS["memory"]
    mem_status = grade(memory["percent_used"], mem_limits['warning'], mem_limits['critical'])
    print(f"{mem_status} - Memory: {memory['percent_used']}% used of {memory['total_gb']} GB")

    disk_limits = THRESHOLDS["disk"]
    for disk in disks:
        disk_status = grade(disk['percent_used'], disk_limits["warning"], disk_limits["critical"])
        print(f"{disk_status} - Disk {disk['mount']}: {disk['percent_used']}% used of {disk['total_gb']} GB")
    
    cpu_limits = THRESHOLDS['cpu']
    cpu_status = grade(cpu["percent_used"], cpu_limits['warning'])
    print(f"{cpu_status} - CPU: {cpu['percent_used']}% used of {cpu['cores']} cores")

    uptime_limits = THRESHOLDS["uptime"]
    uptime_status = grade(system["uptime_days"], uptime_limits["warning"], uptime_limits["critical"])
    print(f"{uptime_status} - Uptime: {system['uptime_days']} days")