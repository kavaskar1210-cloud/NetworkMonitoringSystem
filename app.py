from flask import Flask, render_template, request, redirect, url_for

from database import (
    create_table,
    add_device,
    get_devices,
    delete_device,
    get_history
)
from monitor import monitor_devices

app = Flask(__name__)

# Create database table
create_table()


@app.route("/")
def index():
    monitor_devices()

    devices = get_devices()
    history_data = get_history()

    total = len(devices)
    online = sum(1 for device in devices if device["status"] == "Online")
    offline = sum(1 for device in devices if device["status"] == "Offline")

    if total > 0:
        average_latency = round(
            sum(device["latency"] for device in devices) / total,
            2
        )
    else:
        average_latency = 0

    return render_template(
    "index.html",
    devices=devices,
    total=total,
    online=online,
    offline=offline,
    average_latency=average_latency,
    history=history_data
)

@app.route("/devices")
def devices():
    monitor_devices()
    device_list = get_devices()

    return render_template(
        "devices.html",
        devices=device_list
    )


@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":

        name = request.form["name"]
        ip_address = request.form["ip_address"]
        device_type = request.form["device_type"]

        try:
            add_device(name, ip_address, device_type)
        except Exception:
            pass

        return redirect(url_for("devices"))

    return render_template("add_device.html")


@app.route("/delete/<int:device_id>")
def delete(device_id):
    delete_device(device_id)

    return redirect(url_for("devices"))

@app.route("/history")
def history():
    monitor_devices()

    history_data = get_history()

    return render_template(
        "history.html",
        history=history_data
    )
if __name__ == "__main__":
    app.run(debug=True)