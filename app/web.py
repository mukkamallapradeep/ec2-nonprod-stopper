import os
from flask import Flask, render_template, request, redirect, url_for, flash
from app.aws_ec2 import list_instances
from app.celery_app import celery

TZ = os.getenv("TZ", "Asia/Kolkata")

def create_app():
    app = Flask(__name__)
    app.secret_key = os.getenv("FLASK_SECRET", "dev-secret")

    @app.get("/")
    def home():
        return redirect(url_for("instances_page"))

    @app.get("/instances")
    def instances_page():
        data = list_instances()
        data.sort(key=lambda x: (x.get("Environment") != "Non-Prod", x.get("Name", "")))
        return render_template("instances.html", instances=data, tz=TZ)

    # Manual STOP selected (async)
    @app.post("/stop-selected")
    def stop_selected():
        instance_ids = request.form.getlist("instance_ids")
        dry_run = request.form.get("dry_run") == "on"

        if not instance_ids:
            flash("Select at least one Non-Prod instance.", "warning")
            return redirect(url_for("instances_page"))

        celery.send_task("stop_nonprod_selected", args=[instance_ids, dry_run])
        flash(f"Stop requested in background for: {instance_ids}", "success")
        return redirect(url_for("instances_page"))

    @app.get("/schedule")
    def schedule_page():
        return render_template("schedule.html", tz=TZ)

    # Run AFTER N minutes (one-time)
    @app.post("/schedule-once")
    def schedule_once():
        minutes = int(request.form.get("minutes", "1"))
        dry_run = request.form.get("dry_run") == "on"

        celery.send_task("stop_nonprod_all", args=[dry_run], countdown=minutes * 60)
        flash(f"Scheduled: stop Non-Prod instances once after {minutes} minute(s).", "success")
        return redirect(url_for("schedule_page"))

    # Run NOW
    @app.post("/run-now")
    def run_now():
        dry_run = request.form.get("dry_run") == "on"
        celery.send_task("stop_nonprod_all", args=[dry_run])
        flash("Triggered stop job now (Celery).", "success")
        return redirect(url_for("schedule_page"))

    return app

app = create_app()
