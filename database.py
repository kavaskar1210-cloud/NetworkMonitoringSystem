import sqlite3

DATABASE = "network_monitor.db"


def get_connection():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def create_table():
    connection = get_connection()

    # Device table
    connection.execute("""
        CREATE TABLE IF NOT EXISTS devices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            ip_address TEXT NOT NULL UNIQUE,
            device_type TEXT NOT NULL,
            status TEXT DEFAULT 'Unknown',
            latency REAL DEFAULT 0,
            last_checked TEXT
        )
    """)

    # Monitoring history table
    connection.execute("""
        CREATE TABLE IF NOT EXISTS monitoring_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            device_id INTEGER,
            status TEXT,
            latency REAL,
            checked_at TEXT,
            FOREIGN KEY (device_id) REFERENCES devices(id)
        )
    """)

    connection.commit()
    connection.close()


def add_device(name, ip_address, device_type):
    connection = get_connection()

    connection.execute("""
        INSERT INTO devices (name, ip_address, device_type)
        VALUES (?, ?, ?)
    """, (name, ip_address, device_type))

    connection.commit()
    connection.close()


def get_devices():
    connection = get_connection()

    devices = connection.execute(
        "SELECT * FROM devices ORDER BY id DESC"
    ).fetchall()

    connection.close()

    return devices


def delete_device(device_id):
    connection = get_connection()

    connection.execute(
        "DELETE FROM devices WHERE id = ?",
        (device_id,)
    )

    connection.execute(
        "DELETE FROM monitoring_history WHERE device_id = ?",
        (device_id,)
    )

    connection.commit()
    connection.close()


def add_history(device_id, status, latency, checked_at):
    connection = get_connection()

    connection.execute("""
        INSERT INTO monitoring_history
        (device_id, status, latency, checked_at)
        VALUES (?, ?, ?, ?)
    """, (
        device_id,
        status,
        latency,
        checked_at
    ))

    connection.commit()
    connection.close()


def get_history():
    connection = get_connection()

    history = connection.execute("""
        SELECT
            monitoring_history.id,
            devices.name,
            devices.ip_address,
            monitoring_history.status,
            monitoring_history.latency,
            monitoring_history.checked_at
        FROM monitoring_history
        JOIN devices
        ON monitoring_history.device_id = devices.id
        ORDER BY monitoring_history.id DESC
        LIMIT 100
    """).fetchall()

    connection.close()

    return history