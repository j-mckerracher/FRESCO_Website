import logging
import os
import re
import requests
from time import sleep

MAX_RETRIES = 3
INITIAL_DELAY = 1

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_authorization():
    logger.info("Starting authorization process")

    username = "api_user"  # os.environ["API_USER"]
    password = os.environ["API_USER_AUTH"]  # Example password
    data = {"username": username, "password": password}
    url = os.environ["AUTH_URL"]

    logger.info("Sending authorization request to %s", url)
    response = retry_request(url, get_or_post="post", data=data, max_retries=MAX_RETRIES, initial_delay=INITIAL_DELAY)

    if response:
        logger.info("Authorization successful")
        return response.json()["access_token"]
    else:
        logger.error("Encountered an error getting API authorization")
        return None


def get_api_endpoint(form_data: str, search_type: str) -> str:
    if search_type == 'host':
        pass
    elif search_type == 'job':
        pass

    return os.getenv("BASE_API_ADDRESS")


def send_simple_search_request(form_data: str, search_type: str):
    """
    Sends a simple search request based on form data and retrieves data from a specified host.

    This function first acquires an authorization JWT token. If the token is obtained successfully, it constructs a
    specific URL based on the input type identified in 'form_data' (job, node, or date). It then attempts to send a
    GET request to the constructed URL using the retry_request function with global retry and delay settings. If the
    request is successful and a response is received, the function returns the JSON content of the response.
    Otherwise, it returns a failure message.

    :param: form_data (str): The input data used to determine the type of search request.

    :return: response (dict or str): A dictionary containing the JSON response from the request if successful,
    or a failure message string if the request fails or the authorization token is not obtained.
    """
    logger.info("Sending simple search request for form data: %s, search type: %s", form_data, search_type)

    global MAX_RETRIES, INITIAL_DELAY
    # jwt = get_authorization()
    # if not jwt:
    #     logger.error("Failed to get API authorization")
    #     return "Failed to get API authorization!"

    # logger.info("Received JWT for authorization")
    # headers = {"Authorization": f"Bearer {jwt}"}

    url = get_api_endpoint(form_data, search_type)
    logger.info("Constructed URL for request: %s", url)

    response = retry_request(
        url,
        get_or_post="get",
        headers=None,
        max_retries=MAX_RETRIES,
        initial_delay=INITIAL_DELAY
    )

    if type(response) == str:
        logger.warning("Received string response, indicating a possible error: %s", response)
        return response
    elif response is not None and response.json():
        logger.info("Received successful JSON response")
        return response.json()
    else:
        logger.error("Couldn't connect to the Database or empty response")
        return "Couldn't connect to the Database!"


def make_post_request(url, data):
    """
    Makes a POST request to a specified URL with given headers.

    :param: url (str): The URL to send the POST request to.
    :param: data (dict): A dictionary of data to include in the request.

    :return: response: The response object returned by the requests library.
    """
    logger.info("Making POST request to %s", url)

    try:
        response = requests.post(url, data=data)
        logger.info("POST request to %s successful", url)
        return response
    except requests.RequestException as e:
        logger.error("Post request failed: %s", e)
        return None


def make_get_request(url, headers):
    """
    Sends a GET request to the specified URL with the provided headers.

    :param: url (str): The URL to which the GET request is to be sent.
    :param: headers (dict): A dictionary of headers to include in the request.

    :return: response (requests.Response or None): The response object from the request, or None if the request fails
    due to an exception.
    """
    logger.info("Making GET request to %s", url)

    try:
        response = requests.get(url, headers=headers)
        logger.info("GET request to %s successful", url)
        return response
    except requests.RequestException as e:
        logger.error("Request failed: %s", e)
        return None


def retry_request(url, get_or_post, headers=None, data=None, max_retries=3, initial_delay=1):
    """
    Attempts to send a request to a specified URL, retrying a certain number of times upon failure.

    This function will attempt to send either a GET or a POST request (based on the 'get_or_post' parameter) to the
    provided URL. It will retry up to 'max_retries' times if the request fails. The delay between retries starts at
    'initial_delay' seconds and doubles with each subsequent attempt. If a successful response (status code 200) is
    received, it is returned; otherwise, None is returned after all retries have failed.

    :param: url (str): The URL to send the request to.
    :param: get_or_post (str): Specifies whether to make a 'GET' or 'POST' request.
    :param: headers (dict, optional): Headers to include in the request.
    :param: data (dict, optional): Data to include in the request for a POST.
    :param: max_retries (int, optional): Maximum number of times to retry the request. Defaults to 3.
    :param: initial_delay (int, optional): Initial delay in seconds before the first retry. Defaults to 1.

    :return: response (requests.Response or None): The response object from the successful request, or None if all
    retries fail.
    """
    delay = initial_delay
    for attempt in range(max_retries):
        logger.info(f"Attempt {attempt + 1} of {max_retries} to send {get_or_post.upper()} request to {url}")

        if get_or_post.casefold() == "get":
            response = make_get_request(url, headers)
        else:
            response = make_post_request(url, data)

        if response is not None and response.status_code == 200:
            logger.info("Request successful")
            return response

        logger.warning(f"Request failed. Waiting for {delay} seconds before retrying...")
        sleep(delay)
        delay *= 2  # Double the delay with each attempt

    logger.error("Request failed after all retries.")
    return None


def identify_input_type_host_search(input_str: str):
    """
    Determines the type of input string based on predefined patterns.

    This function checks if the input string matches a specific pattern for job or node identifiers. Job identifiers
    must start with 'JOB' followed by digits (e.g., 'JOB123'), and node identifiers must start with 'NODE' followed by
    digits (e.g., 'NODE456'). It returns a string indicating the type ('job', 'node', or 'unknown') based on the input
    string's conformity to these patterns.

    :param: input_str (str): The input string to be evaluated.

    :return: str: Returns 'job' if the input string matches the job identifier pattern, 'node' if it matches the node
    identifier pattern, or 'unknown' if it matches neither.
    """
    logger.info("Identifying input type for host search: %s", input_str)

    job_id_pattern = r"^JOB\d+$"
    node_id_pattern = r"^NODE\d+$"

    # Check if the input matches any of the patterns
    if re.match(job_id_pattern, input_str):
        logger.info("Input identified as job ID")
        return "job"
    elif re.match(node_id_pattern, input_str):
        logger.info("Input identified as node ID")
        return "node"
    else:
        logger.info("Input type is unknown")
        return "unknown"


def identify_input_type_job_search(input_str: str) -> str:
    """
    Determines the type of input string based on predefined job search patterns.

    The function checks if the input string matches specific patterns for different job search types or job status.
    It returns a string indicating the type based on the input string's conformity to these patterns.

    :param: input_str (str): The input string to be evaluated.

    :return: str: Returns the type of job search or job status ('group', 'job', 'user', 'jobname', 'node',
    specific statuses, or 'unknown').
    """
    logger.info("Identifying input type for job search: %s", input_str)

    # Specific job status values
    valid_statuses = {'CANCELLED', 'COMPLETED', 'FAILED', 'NODE_FAIL', 'TIMEOUT'}
    if input_str in valid_statuses:
        logger.info("Input identified as a job exit status")
        return 'exit_code'

    # Check for prefixes with digits
    prefixes = ["JOBNAME", "GROUP", "JOB", "USER", "NODE"]  # JOBNAME must precede JOB!
    for prefix in prefixes:
        if input_str.startswith(prefix):
            # Extract the numerical part and check if it's all digits
            prefix_length = len(prefix)
            if input_str[prefix_length:].isdigit():
                logger.info(f"Input identified as {prefix.lower()}")
                return prefix.lower()  # Return the prefix type in lowercase

    logger.info("Input type is unknown")
    return "unknown"


def is_valid_host_search(search: str) -> bool:
    """
    Determines if a given search string is a valid host search identifier.

    This function checks if the string starts with 'NODE' or 'JOB', followed by digits. It returns True if the string
    conforms to one of these formats (e.g., 'NODE123', 'JOB456'), and False otherwise.

    :param: search (str): The search string to be validated.

    :return: bool: True if the search string is a valid host search identifier, False otherwise.
    """
    logger.info("Validating host search identifier: %s", search)

    if search.startswith("NODE"):
        is_valid = search[4:].isdigit()  # Check if everything after "NODE" is digits
        logger.info("Validation result for NODE: %s", is_valid)
        return is_valid
    elif search.startswith("JOB"):
        is_valid = search[3:].isdigit()  # Check if everything after "JOB" is digits
        logger.info("Validation result for JOB: %s", is_valid)
        return is_valid

    logger.info("Search string does not conform to valid host search identifiers")
    return False


def is_valid_job_search(search: str) -> bool:
    """
    Determines if a given search string is a valid search identifier.

    The function checks if the string starts with specific keywords ('GROUP', 'JOB', 'USER', 'JOBNAME', 'NODE')
    followed by digits, or if it matches specific job status values ('CANCELLED', 'COMPLETED', 'FAILED',
    'NODE_FAIL', 'TIMEOUT'). It returns True if the string conforms to any of these formats, and False otherwise.

    :param: search (str): The search string to be validated.

    :return: bool: True if the search string is a valid search identifier, False otherwise.
    """
    logger.info("Validating job search identifier: %s", search)

    # Check for job status values
    valid_statuses = {'CANCELLED', 'COMPLETED', 'FAILED', 'NODE_FAIL', 'TIMEOUT'}
    if search in valid_statuses:
        logger.info("Search string is a valid job status value")
        return True

    # Check for prefixes with digits
    prefixes = ["GROUP", "JOBNAME", "JOB", "USER", "NODE"]  # 'JOBNAME' must precede JOB!
    for prefix in prefixes:
        if search.startswith(prefix):
            # Correctly extract the numerical part and check if it's all digits
            prefix_length = len(prefix)  # Get the length of the prefix
            is_valid = search[prefix_length:].isdigit()  # Check if the remaining part is all digits
            logger.info("Validation result for %s: %s", prefix, is_valid)
            return is_valid

    logger.info("Search string does not conform to valid job search identifiers")
    return False


def clean_and_uppercase(input_str: str):
    """
    Cleans the given input string by removing all characters that are not letters or numbers and converts the remaining
    characters to uppercase.

    :param: input_str (str): The string to be cleaned and converted to uppercase.

    :return: str: The cleaned string, containing only letters and numbers in uppercase format.
    """
    logger.info("Cleaning and converting to uppercase: %s", input_str)

    if input_str is None:
        logger.info("Input string is None, returning empty string")
        return ""

    cleaned_str = ''.join(char for char in input_str if char.isalnum() or char == '_').upper()
    logger.info("Cleaned and uppercased string: %s", cleaned_str)

    return cleaned_str
