from constants import CLUSTERS_URL, CLUSTER_NAME, WORKLOADS_URL_POST, EXTERNAL_CLUSTERS_URL, \
    COST_REPORTS_URL_PRE, WORKLOAD_EFFICIENCY_URL_START_POST, EFFICIENCY_URL_END_POST, \
    EFFICIENCY_URL_START_POST, GB_BYTES, API_KEY

from datetime import datetime, timedelta
import json
import requests
import yaml
import os


def get_list(url):
    api_key = os.getenv('CAST_AI_API_KEY')
    if not api_key:
        api_key = API_KEY
    headers = {
        "accept": "application/json",
        "X-API-Key": api_key
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an exception for HTTP error status codes

        # If the request was successful (status code 200), return the response text
        if response.status_code == 200:
            return json.loads(response.content.decode('utf-8'))

        # If the response had an unexpected status code, raise an exception
        raise ValueError("Request failed with status code: " + str(response.status_code))

    except requests.exceptions.HTTPError as http_err:
        # Handle HTTP errors and raise an exception with the appropriate status code
        raise ValueError(f"HTTP Error: {http_err}") from http_err
    except requests.exceptions.RequestException as req_err:
        # Handle network-related errors (e.g., connection issues)
        raise ValueError(f"Network Error: {req_err}") from req_err
    except Exception as err:
        # Handle other exceptions (e.g., unexpected errors) and raise an exception with status code 500
        raise ValueError(f"Internal Server Error: {err}") from err


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


def find_cluster_id(clusters, name: str) -> str:
    for cluster in clusters:
        if cluster['name'] == name:
            return cluster['id']
    raise Exception(f"Cluster with name '{name}' not found")


def create_yaml(workload_efficiency_list, start, end):
    with open(f'resources_efficiency_{datetime.now().strftime("%Y%m%d%H%M%S")}.yaml', 'w') as manifest_file:
        for item in workload_efficiency_list:
            url = (f"{COST_REPORTS_URL_PRE}{cluster_id}/namespaces/{item['namespace']}/"
                   f"{item['workloadType']}/{item['workloadName']}/{EFFICIENCY_URL_START_POST}{start}"
                   f"{EFFICIENCY_URL_END_POST}{end}")
            resources_raw_data = get_list(url)

            containers = []
            resource = {
                "containers": containers
            }

            for container_raw_data in resources_raw_data['containers']:
                if len(container_raw_data['items']):
                    memory = f"{container_raw_data['items'][0]['info']['recommendation']['memoryGib']}Gi"
                    requests = {
                        "memory": memory,
                        "cpu": convert_to_cpu_request(container_raw_data['items'][0]['info']['recommendation']['cpu'])
                    }
                    limits = {
                        "memory": memory
                    }
                    container = {
                        "name": container_raw_data['name'],
                        "requests": requests,
                        "limits": limits
                    }
                containers.append(container)
            if len(containers):
                manifest_file.write(f"--- {item['workloadName']} (Workload Name) "
                                    f"--- {item['workloadType']} (Workload Type)"
                                    f"--- {item['namespace']} (Namespace) ---\n\n")

                yaml.dump(resource, manifest_file, sort_keys=False)
                manifest_file.write("\n")


def convert_gb_to_bytes(gb):
    bytes_per_gb = GB_BYTES  # 1 GB = 1,073,741,824 bytes
    gb = float(gb)  # Convert to float
    # print(gb)
    return int(gb * bytes_per_gb)


def convert_to_cpu_request(cpu_fraction):
    # print(cpu_fraction)
    cpu_fraction = float(cpu_fraction)  # Convert to float
    if cpu_fraction < 0 or cpu_fraction > 1:
        raise ValueError("CPU fraction must be between 0 and 1")

    millicores = int(cpu_fraction * 1000)
    return f"{millicores}m"


if __name__ == '__main__':
    clusters_list = get_clusters()
    cluster_id = find_cluster_id(clusters_list, CLUSTER_NAME)
    # workloads_list = get_workloads(cluster_id)

    # Get current UTC time
    current_time_utc = datetime.utcnow()

    # Calculate 7 days ago
    seven_days_ago = current_time_utc - timedelta(days=7)

    # Format times as ISO 8601 strings
    start_time = seven_days_ago.strftime('%Y-%m-%dT%H:%M:%SZ')
    end_time = current_time_utc.strftime('%Y-%m-%dT%H:%M:%SZ')
    workload_efficiency_list = get_workloads_efficiency(cluster_id, start_time, end_time)
    create_yaml(workload_efficiency_list, start_time, end_time)
