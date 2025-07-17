import requests
import json
import os
import traceback

databricks_token = os.environ.get("DATABRICKS_AAD_TOKEN")
HOST = os.environ.get("DATABRICKS_HOST")

def error_handler(func):
    def wrapper(*args, **kwargs):
        try:
            r = func(*args, **kwargs)
            if r.status_code == 200:
                return True, r.json()
            elif r.status_code == 400:
                return False, r.json()
            else:
                print(r.text)
                return False, 'Internal Error'    
        except:
            print(traceback.format_exc())
            return False, 'Internal Error'
    wrapper.__name__ = func.__name__
    return wrapper

@error_handler
def call_db_api_post(endpoint: str, payload: dict):
    url = f"https://{HOST}/api/"
    headers = {
        'Authorization': f'Bearer {databricks_token}',
        'Content-Type': 'application/json'
    }
    req_url = url + endpoint
    return requests.post(req_url, headers=headers, json=payload)

@error_handler
def call_db_api_get(endpoint: str):
    url = f"https://{HOST}/api/"
    headers = {
        'Authorization': f'Bearer {databricks_token}',
        'Content-Type': 'application/json'
    }
    req_url = url + endpoint
    return requests.get(req_url, headers=headers)


def list_pools():
    endpoint = "2.0/instance-pools/list"
    return call_db_api_get(endpoint)

    
def list_clusters():
    endpoint = "2.0/clusters/list"
    return call_db_api_get(endpoint)

def create_job(payload: dict):
    endpoint = "2.1/jobs/create"
    return call_db_api_post(endpoint, payload)

def update_job(payload: dict):
    endpoint = "2.1/jobs/update"
    return call_db_api_post(endpoint, payload)

def list_jobs():
    endpoint = "2.1/jobs/list?limit=100"
    return call_db_api_get(endpoint)

def run_job(job_id):
    endpoint = "2.1/jobs/run-now"
    payload = {
        "job_id": job_id
    }
    return call_db_api_post(endpoint, payload)

