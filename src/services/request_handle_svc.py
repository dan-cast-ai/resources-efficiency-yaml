import requests
import logging

# Set up logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CustomHTTPError(Exception):
    pass


def handle_request(url, headers, method, data):
    response = None
    try:
        if method == 'GET':
            response = requests.get(url, headers=headers)
        elif method == 'POST':
            response = requests.post(url, headers=headers, json=data)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
        response.raise_for_status()
        return response
    except requests.exceptions.HTTPError as errh:
        logger.error(f"HTTP Error: {errh}")
        raise CustomHTTPError(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        logger.error(f"Error Connecting: {errc}")
        raise CustomHTTPError(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        logger.error(f"Timeout Error: {errt}")
        raise CustomHTTPError(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        logger.error(f"Something went wrong: {err}")
        raise CustomHTTPError(f"Something went wrong: {err}")
