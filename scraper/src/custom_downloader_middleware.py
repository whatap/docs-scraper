"""
CustomDownloaderMiddleware
"""

import time

from scrapy.http import HtmlResponse
from urllib.parse import urlparse, unquote_plus

class CustomDownloaderMiddleware:
    driver = None

    def __init__(self):
        self.seen = set()  # Using a set for better performance and to avoid duplicates
        self.driver = CustomDownloaderMiddleware.driver

    def process_request(self, request, spider):
        if not spider.js_render:
            return None

        # Remove GET params if needed
        if spider.remove_get_params:
            o = urlparse(request.url)
            url_without_params = o.scheme + "://" + o.netloc + o.path
            request = request.replace(url=url_without_params)

        # Check if URL has already been seen
        if request.url in self.seen:
            return None

        # Mark URL as seen
        self.seen.add(request.url)

        print("Getting " + request.url + " from selenium")

        # Use Selenium to get the page source
        self.driver.get(unquote_plus(request.url))  # Decode URL
        time.sleep(spider.js_wait)  # Wait for the page to fully render
        body = self.driver.page_source.encode('utf-8')
        url = self.driver.current_url

        # Return a new HtmlResponse with the page source
        return HtmlResponse(
            url=url,
            body=body,
            encoding='utf8'
        )

    def process_response(self, request, response, spider):
        # Since scrappy use start_urls and stop_urls before creating the request
        # If the url get redirected then this url gets crawled even if it's not allowed to
        # So we check if the final url is allowed

        if spider.remove_get_params:
            o = urlparse(response.url)
            url_without_params = o.scheme + "://" + o.netloc + o.path
            response = response.replace(url=url_without_params)

        # Handle URLs ending with '#'
        if response.url == request.url + '#':
            response = response.replace(url=request.url)

        return response
