import os
import yaml

from constants import COST_REPORTS_URL_PRE, EFFICIENCY_URL_END_POST, EFFICIENCY_URL_START_POST, SHELL_GEN
from datetime import datetime, timedelta

from services.api_requests_svc import get_list, get_workloads_efficiency, get_patch_resource_script
from utils import init_env, convert_to_cpu_request, find_cluster_id


def create_yaml(cluster_id, workload_efficiency_list, start, end):
    with open(f'resources_efficiency_{datetime.now().strftime("%Y%m%d%H%M%S")}.yaml', 'w') as manifest_file:
        for item in workload_efficiency_list:
            url = (f"{COST_REPORTS_URL_PRE}{cluster_id}/namespaces/{item['namespace']}/"
                   f"{item['workloadType']}/{item['workloadName']}/{EFFICIENCY_URL_START_POST}{start}"
                   f"{EFFICIENCY_URL_END_POST}{end}")
            resources_raw_data = get_list(url)
            insert_containers_data(cluster_id, item, manifest_file, resources_raw_data)


def generate_shell(cluster_id, item):
    shell_script = get_patch_resource_script(cluster_id, item)
    with open(f"{item['namespace']}_{item['workloadType']}_{item['workloadName']}.sh", 'w') as script_file:
        script_file.write(shell_script)
    pass


def insert_containers_data(cluster_id, item, manifest_file, resources_raw_data):
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
        if SHELL_GEN:
            generate_shell(cluster_id, item)
        yaml.dump(resource, manifest_file, sort_keys=False)
        manifest_file.write("\n")


def generate_outputs():
    cluster_id = find_cluster_id(cluster_name)
    # Get current UTC time
    current_time_utc = datetime.utcnow()
    # Calculate 7 days ago
    seven_days_ago = current_time_utc - timedelta(days=7)
    # Format times as ISO 8601 strings
    start_time = seven_days_ago.strftime('%Y-%m-%dT%H:%M:%SZ')
    end_time = current_time_utc.strftime('%Y-%m-%dT%H:%M:%SZ')
    workload_efficiency_list = get_workloads_efficiency(cluster_id, start_time, end_time)
    create_yaml(cluster_id, workload_efficiency_list, start_time, end_time)


if __name__ == '__main__':
    init_env()
    cluster_name = os.getenv('CLUSTER_NAME')
    generate_outputs()
