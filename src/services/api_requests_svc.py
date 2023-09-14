import json

import logging

from constants import EXTERNAL_CLUSTERS_URL, WORKLOADS_URL_POST, CLUSTERS_URL, COST_REPORTS_URL_PRE, \
    WORKLOAD_EFFICIENCY_URL_START_POST, EFFICIENCY_URL_END_POST, PATCH_URL_POST
from services.loads_keys_svc import get_api_key_headers, get_api_key
from services.request_handle_svc import handle_request, CustomHTTPError


def get_patch_resource_script(cluster_id, item):
    try:
        url = f"{COST_REPORTS_URL_PRE}{cluster_id}{PATCH_URL_POST}"
        api_key = get_api_key()
        # user_agent = 'curl/7.68.0'
        headers = {
            'accept': 'text/x-shellscript',
            'Authorization': f'Bearer {api_key}',
            'X-API-Key': f'{api_key}',
            'Content-Type': 'application/json',
        }
        data = {
            "workloads": [
                {
                    "namespace": f"{item['namespace']}",
                    "workloadName": f"{item['workloadName']}",
                    "workloadType": f"{item['workloadType']}"
                }
            ]
        }
        response = handle_request(url, headers, method="POST", data=data)
        logging.info(response.text)
        return response.text
    except CustomHTTPError as e:
        logging.error(str(e))
        raise e


def get_clusters():
    url = EXTERNAL_CLUSTERS_URL
    return get_list(url)['items']


def get_workloads(cluster_id):
    workload_url = f"{CLUSTERS_URL}{cluster_id}{WORKLOADS_URL_POST}"
    return get_list(workload_url)['workloads']


def get_workloads_efficiency(cluster_id, start, end):
    workload_efficiency_url = (f"{COST_REPORTS_URL_PRE}{cluster_id}"
                               f"{WORKLOAD_EFFICIENCY_URL_START_POST}{start}"
                               f"{EFFICIENCY_URL_END_POST}{end}")
    return get_list(workload_efficiency_url)['items']


def get_list(url):
    headers = get_api_key_headers()

    try:
        response = handle_request(url, headers, method="GET", data=None)
        return json.loads(response.content.decode('utf-8'))
    except CustomHTTPError as custom_err:
        raise custom_err


