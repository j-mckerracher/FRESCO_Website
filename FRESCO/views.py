import csv
import json

from django.http import HttpResponse
from django.shortcuts import render
from . import views_helpers as vh
from datetime import datetime
import logging

template_dir = 'FRESCO/'
ROW_LIMIT = 300

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def home(request):
    template = f'{template_dir}home.html'
    return render(request, template)


def about(request):
    template = f'{template_dir}about.html'
    return render(request, template)


def team(request):
    template = f'{template_dir}team.html'
    return render(request, template)


def news(request):
    template = f'{template_dir}news.html'
    return render(request, template)


def repository_simple_search(request):
    logger.warning("Processing repository simple search")
    template = f'{template_dir}simple-repository-search.html'

    context = {'data': None, 'error_message': None, 'user_input': '', 'truncated': False}
    host_search_type = 'host'
    job_search_type = 'job'
    job_search_error = """
              Invalid search query. Valid formats include:
              <div>
                  <p>Group IDs starting with 'GROUP' followed by digits (e.g., 'GROUP87')</p>
                  <p>Job IDs starting with 'JOB' followed by digits (e.g., 'JOB205067')</p>
                  <p>User IDs starting with 'USER' followed by digits (e.g., 'USER240')</p>
                  <p>Job names starting with 'JOBNAME' followed by digits (e.g., 'JOBNAME20502')</p>
                  <p>Node IDs starting with 'NODE' followed by digits (e.g., 'NODE3')</p>
                  <p>Specific exit codes: 'CANCELLED', 'COMPLETED', 'FAILED', 'NODE_FAIL', 'TIMEOUT'</p>
              </div>
              Please try again with a correct format.
              """

    form_type = request.POST.get('form_type')
    context['form_type'] = form_type

    user_input = ""
    result = []

    if request.method == 'POST':
        user_input = request.POST.get('input_field', '')
        user_input = vh.clean_and_uppercase(user_input)
        context['user_input'] = user_input

        if form_type == 'host_data':
            logger.warning("Host data search with user input: %s", user_input)

            if not vh.is_valid_host_search(user_input):
                context['error_message'] = "Invalid search query. Please try again."
                logger.warning("Invalid host search query: %s", user_input)
            else:
                result = vh.send_simple_search_request(user_input, host_search_type)

        elif form_type == 'job_data':
            logger.warning("Job data search with user input: %s", user_input)

            if not vh.is_valid_job_search(user_input):
                context['error_message'] = job_search_error
                logger.warning("Invalid job search query: %s", user_input)
            else:
                result = vh.send_simple_search_request(user_input, job_search_type)

        if result:
            if isinstance(result, dict) and 'content' in result:
                try:
                    context['data'] = json.loads(result['content'])
                except json.JSONDecodeError as e:
                    context['error_message'] = f"Failed to parse JSON data: {str(e)}"
                    logger.error("Failed to parse JSON data: %s", str(e))
            else:
                context['error_message'] = "Unexpected data format received from search request."
                logger.error("Unexpected data format: %s", type(result))
        else:
            context['error_message'] = f"No data found for {user_input}"
            logger.warning("Search did not return data for: %s", user_input)

        if context['data'] and isinstance(context['data'], list) and len(context['data']) >= ROW_LIMIT:
            context['truncated'] = True
            logger.warning("Search results truncated for: %s", user_input)

    logger.warning(f"Processed data type: {type(context['data'])}")
    logger.warning(f"Processed data: {context['data']}")
    return render(request, template, context)


def download_search_results_as_csv(request):
    logger.warning("Initiating download of search results as CSV")

    search_type_map = {'host_data': 'host', 'job_data': 'job'}
    search_type = search_type_map.get(request.POST.get('form_type'), "none")

    if request.method == 'POST':
        search_query = request.POST.get('search_query')
        logger.warning("Downloading CSV for search type: %s, query: %s", search_type, search_query)

        # Perform the search again or retrieve the results
        data = vh.send_simple_search_request(search_query, search_type)

        try:
            # Get current time
            current_time = datetime.now().strftime("%Y%m%d-%H%M")

            # Create the HttpResponse object with the appropriate CSV header.
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="{search_type}_search_results_{current_time}.csv"'

            writer = csv.writer(response)
            if data:
                # Write CSV headers
                writer.writerow(data[0].keys())

                # Write data rows
                for item in data:
                    writer.writerow(item.values())

                logger.warning("CSV file created and data written successfully")
            else:
                logger.warning("No data available to write to CSV")
        except Exception as e:
            logger.error(f"Error occurred while creating CSV: {e}")
            return HttpResponse("An error occurred while generating the CSV file.", status=500)

        return response
