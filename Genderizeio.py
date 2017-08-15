# -*- coding: utf-8 -*-

import requests, time, json
from requests import Request
from requests.packages.urllib3.exceptions import InsecureRequestWarning, SNIMissingWarning, InsecurePlatformWarning


class Genderizeio(object):
    """
    A simple python wrapper for the Genderize.io API.
    Written to manage rate limiting and keep track of time window resets.
    """

    API_URL = "https://api.genderize.io/"

    def __init__(self, proxies=None):
        """
        Constructor establishes a requests session to be used throughout.

        Args:
            proxies (optional): A dictionary of proxies where the keys are the protocols.
        """

        # Disable requests library SSL warnings.
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
        requests.packages.urllib3.disable_warnings(SNIMissingWarning)
        requests.packages.urllib3.disable_warnings(InsecurePlatformWarning)

        self.proxies = proxies if proxies is not None else {} # Blank dictionary if no proxies provided

        self.session = requests.Session()
        self.session.proxies = self.proxies

        # Response header information to manage rate limiting
        self.last_request_time = 0
        self.time_until_reset = 0
        self._rate_limit = 1000
        self._rate_limit_remaining = 0


    def genderize(self, names):
        """
        Makes API call with provided names and returns a dictionary or array
        of dictionaries with the results.

        Args:
             names: List or String containing names/name to query API with.

        Return:
            Dictionary or list of dictionaries if multiple names queried
        """

        query_names = [names] if isinstance(names, str) else names  # Convert single string input to list

        query_params = {'name[]': [name for name in query_names]}  # Create our GET query parameters

        # Build and prepare our request for easier debugging
        request = Request('GET', self.API_URL, params=query_params)
        prepared_request = self.session.prepare_request(request)

        response = self.session.send(prepared_request)

        self.last_request_time = time.time()  # Record the time we made the request for rate limiting

        # Create a switch/case for our response status
        def response_switch(x):
            return {
                200: {'success': True},
                400: {'success': False, 'reason': 'Bad request'},
                429: {'success': False, 'reason': 'Rate limit hit'},
                500: {'success': False, 'reason': 'Internal Server Error'}
            }[x]

        response_status = response_switch(response.status_code)  # Evaluate our status against our switch/case

        # Raise an exception with the respective reason should our request fail
        if not response_status['success']:
            raise Exception(response_status['reason'])

        # Parse our response headers
        response_headers = response.headers
        self._rate_limit = response_headers['X-Rate-Limit-Limit']
        self._rate_limit_remaining = response_headers['X-Rate-Limit-Remaining']
        self.time_until_reset = int(response_headers['X-Rate-Reset'])

        # Parse our response content
        response_content = json.loads(response.text)

        return response_content


    @property
    def rate_limit_remaining(self):
        return self._rate_limit_remaining

    @property
    def rate_limit(self):
        return self._rate_limit

    @property
    def rate_limit_time_remaining(self):

        # Calculate the time remaining from the last request time
        calculated_time_remaining =  self.time_until_reset - (time.time() - self.last_request_time)

        # Return 0 if the time remaining is a negative value
        return int(calculated_time_remaining) if int(calculated_time_remaining) > 0 else 0


if __name__ == "__main__":

    gen = Genderizeio()  # Create object

    results = gen.genderize(['Emily', 'Jack'])  # Genderize name(s) (String or List)

    for res in results:
        print '{prob}% probability that {name} is a {gender} name.'.format(
            name=res['name'],
            gender=res['gender'],
            prob=int(res['probability']*100)
        )

    print

    print "{remain}/{limit} requests remaining".format(
        remain=gen.rate_limit_remaining,
        limit=gen.rate_limit
    )

    print "{window} seconds until rate limit window resets".format(
        window=gen.time_until_reset
    )