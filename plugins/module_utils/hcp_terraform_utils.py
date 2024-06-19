# -*- coding: utf-8 -*-
# Copyright: Raphaël de Gail
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

from ansible.module_utils.basic import AnsibleModule, env_fallback
from ansible.module_utils._text import to_text


def navigate_hash(source, path, default=None):
    """Return values along a dictionary tree.

    Args:
        source: dict, the dictionary to query.
        path: list, the list of nodes to follow in the dictionary.
        default: str, the default return value. defaults to None.

    Returns:
        dict, the found value along the navigated dictionary tree.
    """
    if not source:
        return None

    key = path[0]
    path = path[1:]
    if key not in source:
        return default
    result = source[key]
    if path:
        return navigate_hash(result, path, default)
    return result


class HcpSession(object):
    """A class to handle all HTTP sessions for API calls.

    For each request, the class sets the authentication and REST method.

    Attributes:
        module: ansible_collections.raphaeldegail.hcp_terraform.plugins.module_utils.hcp_terraform_utils.HcpModule, the ansible module.
    """
    def __init__(self, module):
        """Initializes the instance based on attributes.

        Args:
            module: ansible_collections.raphaeldegail.hcp_terraform.plugins.module_utils.hcp_terraform_utils.HcpModule, the ansible module.
        """
        self.module = module
        self._validate()

    def get(self, url, params=None, **kwargs):
        """Implement the GET method for the session request.

        Args:
            url: str, the URL to call for the request.
            params: dict, query-parameters for the reuqest.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            requests.Response, the response from the request.
        """
        try:
            return self.session().get(url, params=params, **kwargs)
        except getattr(requests.exceptions, 'RequestException') as inst:
            self.module.fail_json(msg=inst.message)

    def post(self, url, body=None, headers=None, **kwargs):
        """Implement the POST method for the session request.

        Args:
            url: str, the URL to call for the request.
            body: dict, the body for the request.
            headers: dict, the headers for the request.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            requests.Response, the response from the request.
        """
        kwargs.update({'json': body, 'headers': headers})

        try:
            return self.session().post(url, **kwargs)
        except getattr(requests.exceptions, 'RequestException') as inst:
            self.module.fail_json(msg=inst.message)

    def delete(self, url):
        """Implement the DELETE method for the sessions request.

        Args:
            url: str, the URL to call for the request.

        Returns:
            requests.Response, the response from the request.
        """
        try:
            return self.session().delete(url)
        except getattr(requests.exceptions, 'RequestException') as inst:
            self.module.fail_json(msg=inst.message)

    def patch(self, url, body=None, **kwargs):
        """Implement the PATCH method for the sessions request.

        Args:
            url: str, the URL to call for the request.
            body: dict, the body for the request.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            requests.Response, the response from the request.
        """
        kwargs.update({'json': body})

        try:
            return self.session().patch(url, **kwargs)
        except getattr(requests.exceptions, 'RequestException') as inst:
            self.module.fail_json(msg=inst.message)

    def put(self, url, body=None, **kwargs):
        """Implement the PUT method for the sessions request.

        Args:
            url: str, the URL to call for the request.
            body: dict, the body for the request.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            requests.Response, the response from the request.
        """
        kwargs.update({'json': body})

        try:
            return self.session().put(url, **kwargs)
        except getattr(requests.exceptions, 'RequestException') as inst:
            self.module.fail_json(msg=inst.message)

    def list(self, url, callback, params=None, array_name='data',
             pageToken='next-page', **kwargs):
        """Calls for an API with a LIST format.

        Args:
            url: str, the URL to call for the request.
            callback: func, the function to decode the response.
            params: dict, query-parameters for the request.
            array_name: str, the resource name to look for the list in the API
                response. Defaults to 'data'.
            pageToken: str, the name of the token to follow the page ordering.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            dict, the list response from the API.
        """
        resp = callback(self.module, self.get(url, params, **kwargs))
        items = resp.get(array_name) if resp.get(array_name) else []
        while navigate_hash(resp, ['meta', 'pagination', pageToken]):
            if params:
                params['page[number]'] = navigate_hash(resp, ['meta', 'pagination', pageToken])
            else:
                params = {'page[number]': navigate_hash(resp, ['meta', 'pagination', pageToken])}

            resp = callback(self.module, self.get(url, params, **kwargs))
            if resp.get(array_name):
                items = items + resp.get(array_name)
        return items

    def session(self):
        """Generates an HTTP session.

        Returns:
            requests.Session, the HTTP session.
        """
        s = requests.Session()
        s.headers.update(self._headers())
        return s

    def _validate(self):
        """Verify if module has proper dependencies.
        """
        if not HAS_REQUESTS:
            self.module.fail_json(msg="Please install the requests library")

    def _headers(self):
        """Generates all basic HTTP headers.

        Returns:
            dict, the basic HTTP headers.
        """
        bearer_token = self.module.params['bearer_token']
        if not bearer_token:
            self.module.fail_json(
                msg='An authorization token must be supplied to access the HCP Terraform platform.'
            )
        return {
            'Authorization': f'Bearer {bearer_token}',
            'Content-Type': 'application/vnd.api+json',
        }


class HcpModule(AnsibleModule):
    """A class to handle all basic features for HCP Terraform modules.

    Inherits from the AnsibleModule class.
    """
    def __init__(self, *args, **kwargs):
        """Initializes the instance based on attributes.

        Args:
            *args: Arbitrary arguments.
            **kwargs: Arbitrary keyword arguments.
        """
        arg_spec = kwargs.get('argument_spec', {})

        kwargs['argument_spec'] = self._merge_dictionaries(
            arg_spec,
            dict(
                bearer_token=dict(
                    required=True,
                    fallback=(env_fallback, ['HCP_TERRAFORM_TOKEN']),
                    no_log=True,
                    type='str'),
            )
        )

        AnsibleModule.__init__(self, *args, **kwargs)

    def raise_for_status(self, response):
        """Raises an HTTP exception from the response, if any.

        Args:
            response: requests.Response, the response to parse.
        """
        try:
            response.raise_for_status()
        except getattr(requests.exceptions, 'RequestException') as inst:
            self.fail_json(
                msg="API call returned error: %s" % response.json(),
                request={
                    "url": response.request.url,
                    "body": response.request.body,
                    "method": response.request.method,
                }
            )

    def _merge_dictionaries(self, a, b):
        """Merge two dictionaries into one.

        Args:
            a: dict, the first dictionary.
            b: dict, the second dictionary.

        Returns:
            dict, the result dictionary.
        """
        new = a.copy()
        new.update(b)
        return new


class HcpRequest(object):
    """A class to difference checking two API objects.

    This will be primarily used for checking dictionaries.
    In an equivalence check, the left-hand dictionary will be the request and
    the right-hand side will be the response.
    Extra keys in response will be ignored.
    Ordering of lists does not matter. Exception: lists of dictionaries are
    assumed to be in sorted order.

    Attributes:
        request: obj, the request to check.
    """
    def __init__(self, request):
        """Initializes the instance based on attributes.

        Args:
            request: obj, the request to check.
        """
        self.request = request

    def __eq__(self, other):
        """Defines the equality relationship.

        Args:
            other: obj, the object to compare to self.

        Returns:
            bool, True if self and other are equal.
        """
        # In order to compare empty lists or dictionaries to non empty ones
        # one must put the non empty resource on the left side
        # so the comparison resort to testing with objetcs being put on either
        # side.
        return not self.difference(other) and not other.difference(self)

    def __ne__(self, other):
        """Defines the non-equality relationship.

        Args:
            other: obj, the object to compare to self.

        Returns:
            bool, True if self and other are different.
        """
        return not self.__eq__(other)

    def difference(self, response):
        """Returns the difference between a request and a response.

        While this is used under the hood for __eq__ and __ne__, it is useful
        for debugging.

        Args:
            response: obj, the object to compare to self.

        Returns:
            obj, the differential comparison between self and response.
        """
        return self._compare_value(self.request, response.request)

    def _compare_value(self, req_value, resp_value):
        """Compare two values of arbitrary types.

        Args:
            req_value: obj, the request object.
            resp_value: obj, the response object.

        Returns:
            obj, the differential comparison between request and response.
        """
        diff = None
        # If a None is found, a difference does not exist.
        # Only differing values matter.
        if resp_value is None:
            return None

        # Can assume non-None types at this point.
        try:
            if isinstance(req_value, list):
                diff = self._compare_lists(req_value, resp_value)
            elif isinstance(req_value, dict):
                diff = self._compare_dicts(req_value, resp_value)
            elif isinstance(req_value, bool):
                diff = self._compare_boolean(req_value, resp_value)
            # Always use to_text values to avoid unicode issues.
            elif to_text(req_value) != to_text(resp_value):
                diff = req_value
        # to_text may throw UnicodeErrors.
        # These errors shouldn't crash Ansible and should be hidden.
        except UnicodeError:
            pass

        return diff

    def _compare_dicts(self, req_dict, resp_dict):
        """Compares two dictionaries.

        Args:
            req_dict: dict, the request dictionary.
            resp_dict: dict, the response dictionary.

        Returns:
            dict, the differential comparison between request and response.
        """
        difference = {}
        for key in req_dict:
            if resp_dict.get(key) is not None:
                diff_value = self._compare_value(req_dict.get(key), resp_dict.get(key))
                if diff_value:
                    difference[key] = diff_value

        return difference

    def _compare_lists(self, req_list, resp_list):
        """Compares two lists.

        All things in the list should be identical (even if a dictionary)

        Args:
            req_list: list, the request list.
            resp_list: list, the response list.

        Returns:
            list, the differential comparison between request and response.
        """
        # Have to convert each thing over to unicode.
        # Python doesn't handle equality checks between unicode + non-unicode well.
        difference = []
        new_req_list = self._convert_value(req_list)
        new_resp_list = self._convert_value(resp_list)

        # We have to compare each thing in the request to every other thing
        # in the response.
        # This is because the request value will be a subset of the response value.
        # The assumption is that these lists will be small enough that it won't
        # be a performance burden.
        for req_item in new_req_list:
            found_item = False
            for resp_item in new_resp_list:
                # Looking for a None value here.
                if not self._compare_value(req_item, resp_item):
                    found_item = True
            if not found_item and req_item:
                difference.append(req_item)

        return difference

    def _compare_boolean(self, req_value, resp_value):
        """Compare two boolean values.

        Args:
            req_value: bool, the request boolean.
            resp_value: bool, the response boolean.

        Returns:
            bool, True if boolean are different, None otherwise.
        """
        try:
            if req_value == bool(to_text(resp_value).capitalize() == 'True'):
                return None
            return True

        # to_text may throw UnicodeErrors.
        # These errors shouldn't crash Ansible and should be hidden.
        except UnicodeError:
            return None

    def _convert_value(self, value):
        """Convert to standard format.

        Python (2 esp.) doesn't do comparisons between unicode and non-unicode
        well. This leads to a lot of false positives when diffing values. The
        Ansible to_text() function is meant to get all strings into a standard
        format.

        Args:
            value: obj, the object to format.

        Returns:
            obj, the formatted object.
        """
        if isinstance(value, list):
            new_list = []
            for item in value:
                new_list.append(self._convert_value(item))
            return new_list
        if isinstance(value, dict):
            new_dict = {}
            for key in value:
                new_dict[key] = self._convert_value(value[key])
            return new_dict
        return to_text(value)
