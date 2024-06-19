# -*- coding: utf-8 -*-
# Copyright: Raphaël de Gail
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
import unittest

from ansible_collections.raphaeldegail.hcp_terraform.plugins.module_utils.hcp_terraform_utils import (
    navigate_hash,
    HcpRequest
)


class NavigateHashTestCase(unittest.TestCase):
    """A class to test the navigate_hash function.
    """
    def test_one_level(self):
        """Test the navigation with one node in the dictionary tree.
        """
        value = {"key": "value"}
        self.assertEqual(navigate_hash(value, ["key"]), value["key"])

    def test_multilevel(self):
        """Test the navigation with several nodes in the dictionary tree.
        """
        value = {"key": {"key2": "value"}}
        self.assertEqual(navigate_hash(value, ["key", "key2"]), value["key"]["key2"])

    def test_default(self):
        """Test the default value.
        """
        value = {"key": "value"}
        default = "not found"
        self.assertEqual(navigate_hash(value, ["key", "key2"], default), default)


class HCPRequestDifferenceTestCase(unittest.TestCase):
    """A class to test the HcpRequest difference function.
    """
    def test_simple_no_difference(self):
        """Test if no difference with one onde in the dictionary tree.
        """
        value1 = {"foo": "bar", "test": "original"}
        request = HcpRequest(value1)
        self.assertEqual(request, request)

    def test_simple_different(self):
        """Test if different with only alphanumetic values.
        """
        value1 = {"foo": "bar", "test": "original"}
        value2 = {"foo": "bar", "test": "different"}
        difference = {"test": "original"}
        request1 = HcpRequest(value1)
        request2 = HcpRequest(value2)
        self.assertNotEqual(request1, request2)
        self.assertEqual(request1.difference(request2), difference)

    def test_nested_dictionaries_no_difference(self):
        """Test if no difference with two nodes in the dictionary tree.
        """
        value1 = {"foo": {"quiet": {"tree": "test"}, "bar": "baz"}, "test": "original"}
        request = HcpRequest(value1)
        self.assertEqual(request, request)

    def test_nested_dictionaries_with_difference(self):
        """Test if different with two nodes in the dictionary tree.
        """
        value1 = {"foo": {"quiet": {"tree": "test"}, "bar": "baz"}, "test": "original"}
        value2 = {"foo": {"quiet": {"tree": "baz"}, "bar": "hello"}, "test": "original"}
        difference = {"foo": {"quiet": {"tree": "test"}, "bar": "baz"}}
        request1 = HcpRequest(value1)
        request2 = HcpRequest(value2)
        self.assertNotEqual(request1, request2)
        self.assertEqual(request1.difference(request2), difference)

    def test_arrays_strings_no_difference(self):
        """Test if no difference in list.
        """
        value1 = {"foo": ["baz", "bar"]}
        request = HcpRequest(value1)
        self.assertEqual(request, request)

    def test_arrays_strings_with_difference(self):
        """Test if different in list.
        """
        value1 = {
            "foo": [
                "baz",
                "bar",
            ]
        }

        value2 = {"foo": ["baz", "hello"]}
        difference = {
            "foo": [
                "bar",
            ]
        }
        request1 = HcpRequest(value1)
        request2 = HcpRequest(value2)
        self.assertNotEqual(request1, request2)
        self.assertEqual(request1.difference(request2), difference)

    def test_arrays_strings_with_difference_and_empty_initial(self):
        """Test if different in list.
        """
        value1 = {
            "foo": []
        }

        value2 = {"foo": ["baz", "hello"]}
        difference = {
            "foo": ["baz", "hello"]
        }
        request1 = HcpRequest(value1)
        request2 = HcpRequest(value2)
        self.assertNotEqual(request1, request2)
        self.assertEqual(request1.difference(request2), {})
        self.assertEqual(request2.difference(request1), difference)

    def test_arrays_dicts_with_no_difference(self):
        """Test if no difference with a list of dictionaries.
        """
        value1 = {"foo": [{"test": "value", "foo": "bar"}, {"different": "dict"}]}
        request = HcpRequest(value1)
        self.assertEqual(request, request)

    def test_arrays_dicts_with_difference(self):
        """Test if different with a list of dictionaries.
        """
        value1 = {"foo": [{"test": "value", "foo": "bar"}, {"different": "dict"}]}
        value2 = {
            "foo": [
                {"test": "value2", "foo": "bar2"},
            ]
        }
        difference = {"foo": [{"test": "value", "foo": "bar"}]}
        request1 = HcpRequest(value1)
        request2 = HcpRequest(value2)
        self.assertNotEqual(request1, request2)
        self.assertEqual(request1.difference(request2), difference)

    def test_dicts_boolean_with_difference(self):
        """Test if different with boolean.
        """
        value1 = {
            "foo": True,
            "bar": False,
            "baz": True,
            "qux": False,
        }

        value2 = {
            "foo": True,
            "bar": False,
            "baz": False,
            "qux": True,
        }

        difference = {
            "baz": True,
            "qux": True,
        }
        request1 = HcpRequest(value1)
        request2 = HcpRequest(value2)
        self.assertNotEqual(request1, request2)
        self.assertEqual(request1.difference(request2), difference)
