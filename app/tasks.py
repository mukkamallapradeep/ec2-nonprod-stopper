from app.celery_app import celery
from app.aws_ec2 import list_instances, stop_instances

@celery.task(name="stop_nonprod_all")
def stop_nonprod_all(dry_run=False):
    instances = list_instances()
    candidates = [
        i["InstanceId"]
        for i in instances
        if i.get("Environment") == "Non-Prod" and i.get("State") == "running"
    ]
    result = stop_instances(candidates, dry_run=dry_run)
    return {"candidates": candidates, "result": result}

@celery.task(name="stop_nonprod_selected")
def stop_nonprod_selected(instance_ids, dry_run=False):
    result = stop_instances(instance_ids, dry_run=dry_run)
    return {"requested": instance_ids, "result": result}
