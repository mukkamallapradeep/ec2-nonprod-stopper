import boto3
import os

REGION = os.getenv("AWS_REGION", "ap-south-1")

def ec2_client():
    return boto3.client("ec2", region_name=REGION)

def list_instances():
    ec2 = ec2_client()
    paginator = ec2.get_paginator("describe_instances")
    instances = []

    for page in paginator.paginate():
        for res in page.get("Reservations", []):
            for inst in res.get("Instances", []):
                tags = {t["Key"]: t["Value"] for t in inst.get("Tags", [])}
                instances.append({
                    "InstanceId": inst["InstanceId"],
                    "State": inst["State"]["Name"],
                    "Name": tags.get("Name", ""),
                    "Environment": tags.get("Environment", ""),
                    "InstanceType": inst.get("InstanceType", ""),
                    "AZ": inst.get("Placement", {}).get("AvailabilityZone", ""),
                    "PrivateIp": inst.get("PrivateIpAddress", ""),
                })
    return instances

def is_nonprod(instance_id: str) -> bool:
    ec2 = ec2_client()
    resp = ec2.describe_instances(InstanceIds=[instance_id])
    for res in resp.get("Reservations", []):
        for inst in res.get("Instances", []):
            tags = {t["Key"]: t["Value"] for t in inst.get("Tags", [])}
            return tags.get("Environment") == "Non-Prod"
    return False

def stop_instances(instance_ids, dry_run=False):
    """
    Stop only Non-Prod instances (double-check tag in backend).
    """
    allowed = [iid for iid in instance_ids if is_nonprod(iid)]
    denied = [iid for iid in instance_ids if iid not in allowed]

    if not allowed:
        return {"stopped": [], "denied": denied}

    ec2 = ec2_client()
    ec2.stop_instances(InstanceIds=allowed, DryRun=dry_run)
    return {"stopped": allowed, "denied": denied}