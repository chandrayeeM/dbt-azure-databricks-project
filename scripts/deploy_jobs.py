import argparse
import logging
import os, json
import util_databricks as udb

logging.basicConfig(
    format="[%(asctime)s] %(levelname)-8s %(name)-20s  %(message)s",
    datefmt="%Y-%m-%d,%H:%M:%S",
)
logger = logging.getLogger(__name__)

CLUSTER_NAME = "dbt-uc-tmp"

def deploy_job(job: dict, email_list="") -> None:
    job_name = "DBT_" + job['name']
    
    job_id = None
    r, data = udb.list_jobs()
    if not r:
        raise Exception(data)
    for ex_job in data['jobs']:
        if ex_job["settings"]["name"] == job_name:
            job_id = ex_job['job_id']
            break
        
    cluster_id = None
    r, data = udb.list_clusters()
    if not r:
        raise Exception(data)
    for ex_clu in data['clusters']:
        if CLUSTER_NAME == ex_clu["cluster_name"]:
            cluster_id = ex_clu['cluster_id']
            break

    email_list = email_list.split(",")
    email_notifications = {"on_failure": email_list}
    
    commands = job['commands']
    if 'dbt deps' not in commands:
        commands = ['dbt deps'] + commands
    
    job_setting = {
        "name": job_name,
        "tags": job["tags"],
        "max_concurrent_runs": 1,
        "tasks": [
            {
                "task_key": "transform",
                "dbt_task": {
                    "project_directory": "/Repos/shared/dbt-lake",
                    "commands": commands,
                    "source": "WORKSPACE"
                },
                "libraries": [
                    {
                        "pypi": {
                            "package": "dbt-databricks==1.8.5"
                        },
                    }
                ],
                "existing_cluster_id": cluster_id,
                "max_retries": job["max_retries"],
                "min_retry_interval_millis": 60 * 1000,
                "retry_on_timeout": False,
                "timeout_seconds": 0,
                "email_notifications": email_notifications,
                "notification_settings": {
                    "no_alert_for_skipped_runs": True,
                    "no_alert_for_canceled_runs": True,
                },
            }
        ],
        "schedule": job['schedule'] if 'schedule' in job else None
    }
    
    # Update the job if it already exist
    if job_id:
        payload = {
            "job_id": job_id,
            "new_settings": job_setting
        }
        r, data = udb.update_job(payload)
        if r:
            logger.info(f"Updated job {job_name} successfully")
    else:
        r, data = udb.create_job(job_setting)
        if r:
            logger.info(f"Created job {job_name} successfully")
    
    if not r:
        raise Exception(data)


def get_cluster_config(cluster_id=None):
    databricks_host = os.environ.get("DATABRICKS_HOST")
    organization = databricks_host.split('.')[0].split('adb-')[1]
    environment = os.environ.get("ENV")
    return {
        "cluster_name": CLUSTER_NAME,
        "spark_version": "14.3.x-scala2.12",
        "spark_conf": {
            "spark.databricks.secureVariableSubstitute.enabled": "false",
            "spark.databricks.delta.preview.enabled": "true",
            "spark.mart.serverName": "{{secrets/mart/serverName}}",
            "spark.mart.adminUsername": "{{secrets/mart/sqlAdministratorUsername}}",
            "spark.mart.adminPassword": "{{secrets/mart/sqlAdministratorPassword}}",
            "spark.mart.prodSqlUsername": "{{secrets/mart/prodSqlUsername}}",
            "spark.mart.prodSqlPassword": "{{secrets/mart/prodSqlPassword}}",
            "spark.mart.prodServerName": "{{secrets/mart/prodServerName}}",
            "spark.databricks.io.cache.enabled": "true",
            "spark.databricks.delta.properties.defaults.autoOptimize.optimizeWrite": "true",
            "spark.databricks.delta.properties.defaults.autoOptimize.autoCompact": "true"
        },
        "spark_env_vars": {
            "DATABRICKS_HOST": databricks_host,
            "DATABRICKS_TOKEN": "{{secrets/mart/DBAADToken}}",
            "DATABRICKS_ORGANIZATION": organization,
            "DATABRICKS_HTTP_PATH": f"sql/protocolv1/o/{organization}/{cluster_id}",
            "DATABRICKS_SCHEMA": "main",
            "ENV": environment,
            "LANDING_PATH": f"abfss://landing@stifdpinges{environment}.dfs.core.windows.net",
            "EXT_LANDING_PATH": f"abfss://extlanding@stifdperpin{environment}.dfs.core.windows.net"
        },
        "autoscale": {
            "min_workers": 1,
            "max_workers": 5
        },
        "node_type_id": "Standard_DS3_v2",
        "driver_node_type_id": "Standard_DS3_v2",
        "ssh_public_keys": [],
        "custom_tags": {},
        "autotermination_minutes": 10,
        "policy_id": get_shared_policy()
    }

def get_shared_policy():
    r, data = udb.list_cluster_policies()
    for p in data["policies"]:
        if p["name"] == "Shared Compute":
            return p["policy_id"]


def update_cluster():
    # first update secret
    token = os.environ.get("DATABRICKS_AAD_TOKEN")
    r, data = udb.put_secret("DBAADToken", token)
    if r:
        logger.info("Secrets updated successfully")
    else:
        raise Exception(data)
    
    r, data = udb.list_clusters()
    clu_id = None
    if r:
        for clu in data['clusters']:
            if clu['cluster_name'] == CLUSTER_NAME:
                clu_id = clu["cluster_id"]
    
    payload = get_cluster_config(clu_id)
    if clu_id:
        payload['cluster_id'] = clu_id
        r, data = udb.update_cluster(payload)
        if r:
            logger.info("Cluster updated successfully")
    else:
        r, data = udb.create_cluster(payload)
        if r:
            logger.info("Cluster created successfully")
        # update the http path after creating the cluster
        r, data = update_cluster()
    if not r:
        logger.error(data)

def get_new_job_cluster(pool_id):
    return {
        "num_workers": 0,
        "spark_version": "14.3.x-scala2.12",
        "spark_conf": {
            "spark.master": "local[*, 4]",
            "spark.databricks.cluster.profile": "singleNode",
            "spark.databricks.delta.retryWriteConflict.enabled": "true",
            "spark.databricks.delta.retryWriteConflict.limit": 10,
            "spark.streaming.eventhubConnStr": "{{secrets/streaming/eventhubConnStr}}",
            "spark.mart.serverName": "{{secrets/mart/serverName}}",
            "spark.mart.adminUsername": "{{secrets/mart/sqlAdministratorUsername}}",
            "spark.mart.adminPassword": "{{secrets/mart/sqlAdministratorPassword}}",
            "spark.databricks.delta.properties.defaults.autoOptimize.autoCompact": "true",
            "spark.databricks.delta.properties.defaults.autoOptimize.optimizeWrite": "true",
        },
        "azure_attributes": {
            "first_on_demand": 1,
            "availability": "ON_DEMAND_AZURE",
            "spot_bid_max_price": -1,
        },
        "ssh_public_keys": [],
        "custom_tags": {"ResourceClass": "SingleNode"},
        "spark_env_vars": {
            "PYSPARK_PYTHON": "/databricks/python3/bin/python3"
        },
        "cluster_source": "JOB",
        "init_scripts": [],
        "data_security_mode": "SINGLE_USER",
        "runtime_engine": "STANDARD",
        "instance_pool_id": pool_id,
    }
    

def main(args: argparse.Namespace) -> None:
    """
    The main entry point for deploying databricks jobs

    Parameters
    ----------
    args : argparse.Namespace
        The script arguments
    """
    level = logging.DEBUG if args.debug else logging.INFO
    logger.setLevel(level)
    logger.info("Authenticated against databricks workspace")
    
    if args.update_cluster:
        update_cluster()
    
    
    job_files = os.listdir("jobs")
    for job_fn in job_files:
        if not job_fn.endswith('.json'):
            continue
        with open(f"jobs/{job_fn}") as f:
            job_data = json.load(f)
        deploy_job(
            job=job_data,
            email_list=args.email_list,
        )



def str2bool(arg_value):
    if isinstance(arg_value, bool):
        return arg_value
    if arg_value.lower() in ("yes", "true", "t", "y", "1"):
        return True
    elif arg_value.lower() in ("no", "false", "f", "n", "0"):
        return False
    else:
        raise argparse.ArgumentTypeError("Boolean value expected.")


def parse_arguments() -> argparse.Namespace:
    """
    Parse the command arguments

    Returns
    -------
    argparse.NameSpace
        The parsed arguments.
    """
    parser = argparse.ArgumentParser("Deploy cdc streaming job")
    parser.add_argument("--debug", action="store_true")

    parser.add_argument(
        "--update-cluster",
        help="Update or create the cluster",
        type=str2bool,
        default=False,
    )
    parser.add_argument(
        "--email-list",
        help="Existing cluster name on which the job will start running",
        default="",
    )
    return parser.parse_args()


if __name__ == "__main__":
    main(parse_arguments())
