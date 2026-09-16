import platform
import subprocess
import time
from datetime import datetime

from database import get_connection


def ping_device(ip_address):
    system = platform.system().lower()

    if system == "windows":
        command = ["ping", "-n", "1", "-w", "1000", ip_address]
    else:
        command = ["ping", "-c", "1", "-W", "1", ip_address]

    start_time = time.time()

    try:
        result = subprocess.run(
            command,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        latency = round((time.time() - start_time) * 1000, 2)

        if result.returncode == 0:
            return "Online", latency

        return "Offline", 0

    except Exception:
        return "Offline", 0


def monitor_devices():

    connection = get_connection()

    devices = connection.execute(
        "SELECT * FROM devices"
    ).fetchall()

    for device in devices:

        status, latency = ping_device(
            device["ip_address"]
        )

        checked_at = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        # Update current device status
        connection.execute("""
            UPDATE devices
            SET status = ?,
                latency = ?,
                last_checked = ?
            WHERE id = ?
        """, (
            status,
            latency,
            checked_at,
            device["id"]
        ))

        # Save monitoring history
        connection.execute("""
            INSERT INTO monitoring_history
            (device_id, status, latency, checked_at)
            VALUES (?, ?, ?, ?)
        """, (
            device["id"],
            status,
            latency,
            checked_at
        ))

        # Generate alert
        if status == "Offline":
            print(
                f"ALERT: {device['name']} "
                f"({device['ip_address']}) is unreachable!"
            )

    connection.commit()
    connection.close()