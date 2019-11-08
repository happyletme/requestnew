import logging
import json,sys
from record.compat import urlparse
from record import utils

IGNORE_REQUEST_HEADERS = [
    "host",
    "accept",
    "content-length",
    "connection",
    "accept-encoding",
    "accept-language",
    "origin",
    "referer",
    "cache-control",
    "pragma",
    "cookie",
    "upgrade-insecure-requests",
    ":authority",
    ":method",
    ":scheme",
    ":path",
    "redirect",
    "user-agent"
]

try:
    from json.decoder import JSONDecodeError
except ImportError:
    JSONDecodeError = ValueError

class HarParser(object):

    def __init__(self, filter_str=None, exclude_str=None):
        self.filter_str = filter_str
        self.exclude_str = exclude_str or ""
        self.teststep_dict = {'request':{}}

    def __make_request_url(self):
        self.teststep_dict["request"]["params"] = ""
        request_params = utils.convert_list_to_dict(
            self.entry_json["request"].get("queryString", [])
        )
        url = self.entry_json["request"].get("url")
        if not url:
            logging.exception("url missed in request.")
            sys.exit(1)

        parsed_object = urlparse.urlparse(url)
        if request_params:
            parsed_object = parsed_object._replace(query='')
            self.teststep_dict["request"]["api"] = parsed_object.path
            self.teststep_dict["request"]["params"] = request_params
        else:
            self.teststep_dict["request"]["api"] = parsed_object.path

            self.teststep_dict["name"] = parsed_object.path

    def __make_request_method(self):
        """ parse HAR entry request method, and make teststep method.
        """
        method = self.entry_json["request"].get("method")
        if not method:
            logging.exception("method missed in request.")
            sys.exit(1)

        if method == "POST":
            postData = self.entry_json["request"].get("postData", {})
            mimeType = postData.get("mimeType")
            if not mimeType:
                pass
            elif mimeType.startswith("application/json"):
                method = "postbody"
            elif mimeType.startswith("application/x-www-form-urlencoded"):
                method = "postform"
            else:
                # TODO: make compatible with more mimeType
                pass

        self.teststep_dict["request"]["method"] = method

    def __make_request_headers(self):
        teststep_headers = {}
        for header in self.entry_json["request"].get("headers", []):
            if header["name"].lower() in IGNORE_REQUEST_HEADERS:
                continue

            teststep_headers[header["name"]] = header["value"]

        if teststep_headers:
            self.teststep_dict["request"]["headers"] = teststep_headers

    def __make_request_data(self):
        self.teststep_dict["request"]["json"] = self.teststep_dict["request"]["data"] = ""
        method = self.entry_json["request"].get("method")
        if method in ["POST", "PUT", "PATCH"]:
            postData = self.entry_json["request"].get("postData", {})
            mimeType = postData.get("mimeType")

            # Note that text and params fields are mutually exclusive.
            if "text" in postData:
                post_data = postData.get("text")
            else:
                params = postData.get("params", [])
                post_data = utils.convert_list_to_dict(params)

            request_data_key = "data"
            if not mimeType:
                pass
            elif mimeType.startswith("application/json"):
                try:
                    post_data = json.loads(post_data)
                    request_data_key = "json"
                except JSONDecodeError:
                    pass
            elif mimeType.startswith("application/x-www-form-urlencoded"):
                post_data = utils.convert_x_www_form_urlencoded_to_dict(post_data)
            else:
                # TODO: make compatible with more mimeType
                pass

            self.teststep_dict["request"][request_data_key] = post_data

    def make_testStep(self, entry):
        self.entry_json = entry
        self.__make_request_url()
        self.__make_request_method()
        self.__make_request_headers()
        self.__make_request_data()
        return self.teststep_dict

#file_path="3.har"
#entries=utils.load_har_log_entries(file_path)

harParser=HarParser()



