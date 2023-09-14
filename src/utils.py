from constants import SECRETS_ENV_FILE
from dotenv import load_dotenv

from services.api_requests_svc import get_clusters


def init_env():
    load_dotenv(dotenv_path=SECRETS_ENV_FILE)


def find_cluster_id(name: str) -> str:
    clusters_list = get_clusters()
    for cluster in clusters_list:
        if cluster['name'] == name:
            return cluster['id']
    raise Exception(f"Cluster with name '{name}' not found")


def convert_to_cpu_request(cpu_fraction):
    # print(cpu_fraction)
    cpu_fraction = float(cpu_fraction)  # Convert to float
    # print(cpu_fraction)

    millicores = int(cpu_fraction * 1000)
    return f"{millicores}m"
