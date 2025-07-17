import argparse
import logging
import os, json
import util_databricks as udb

logging.basicConfig(
    format="[%(asctime)s] %(levelname)-8s %(name)-20s  %(message)s",
    datefmt="%Y-%m-%d,%H:%M:%S",
)
logger = logging.getLogger(__name__)

CLUSTER_NAME = "Chandrayee's Cluster"

def deploy_job(job: dict, email_list="") -> None:
    job_name = "DBT_" + job['name']
    job.setdefault("tags", {})
    job.setdefault("max_retries", 1)

    # Get existing job
    job_id = None
    r, data = udb.list_jobs()
    if not r:
        raise Exception(data)
    for ex_job in data['jobs']:
        if ex_job["settings"]["name"] == job_name:
            job_id = ex_job['job_id']
            break

    # Get cluster ID
    cluster_id = None
    r, data = udb.list_clusters()
    if not r:
        raise Exception(data)
    for ex_clu in data['clusters']:
        if CLUSTER_NAME == ex_clu["cluster_name"]:
            cluster_id = ex_clu['cluster_id']
            break

    # Fail early if no cluster found and new_cluster not provided
    if not cluster_id and 'new_cluster' not in job:
        raise Exception("No cluster found and no new_cluster config provided")

    # Build email notifications
    email_list = email_list.split(",") if email_list else []
    email_notifications = {"on_failure": email_list}

    # Prepend dbt deps
    commands = job.get('commands', [])
    if 'dbt deps' not in commands:
        commands = ['dbt deps'] + commands

    project_dir = job.get("project_directory", "/Workspace/Repos/shared/dbt-lake")

    task = {
        "task_key": "transform",
        "dbt_task": {
            "project_directory": project_dir,
            "commands": commands,
            "source": "WORKSPACE"
        },
        "libraries": [
            {
                "pypi": {
                    "package": "dbt-databricks==1.8.5"
                }
            }
        ],
        "max_retries": job["max_retries"],
        "min_retry_interval_millis": 60 * 1000,
        "retry_on_timeout": False,
        "timeout_seconds": 0,
        "email_notifications": email_notifications,
        "notification_settings": {
            "no_alert_for_skipped_runs": True,
            "no_alert_for_canceled_runs": True
        }
    }

    # Cluster definition: dynamic
    if 'new_cluster' in job:
        task['new_cluster'] = job['new_cluster']
    else:
        task['existing_cluster_id'] = cluster_id

    job_setting = {
        "name": job_name,
        "tags": job["tags"],
        "max_concurrent_runs": 1,
        "tasks": [task]
    }

    if 'schedule' in job:
        job_setting['schedule'] = job['schedule']

    # Create or update job
    if job_id:
        payload = {"job_id": job_id, "new_settings": job_setting}
        r, data = udb.update_job(payload)
        if r:
            logger.info(f"Updated job {job_name} successfully")
    else:
        r, data = udb.create_job(job_setting)
        if r:
            logger.info(f"Created job {job_name} successfully")

    if not r:
        raise Exception(data)

    

def main(args: argparse.Namespace) -> None:
    """
    Main entry point for deploying a single dbt job to Databricks.
    """
    level = logging.DEBUG if args.debug else logging.INFO
    logger.setLevel(level)
    logger.info("Deploying job from file: %s", args.job_file)

    with open(args.job_file) as f:
        job_data = json.load(f)

    deploy_job(job_data)



def parse_arguments() -> argparse.Namespace:
    """
    Parse CLI arguments for deploying a dbt job to Databricks.
    """
    parser = argparse.ArgumentParser(description="Deploy dbt job to Databricks")

    parser.add_argument(
        "--job-file",
        required=True,
        help="Path to the Databricks job definition JSON file"
    )

    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )

    return parser.parse_args()


if __name__ == "__main__":
    main(parse_arguments())
