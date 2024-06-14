#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright: Raphaël de Gail
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

################################################################################
# Documentation
################################################################################

ANSIBLE_METADATA = {'metadata_version': '1.1', 'status': ['preview'], 'supported_by': 'community'}

DOCUMENTATION = '''
---
module: hcp_terraform_var
description:
- Represents an HCP Terraform Variable.
short_description: Creates an HCP Terraform Variable
author: Raphaël de Gail (@RaphaeldeGail)
requirements:
- python >= 3.11
- requests >= 2.32.2
extends_documentation_fragment:
- raphaeldegail.hcp_terraform.hcp_terraform
options:
  state:
    description:
    - Whether the given object should exist in HCP Terraform
    choices:
    - present
    - absent
    default: present
    type: str
  key:
    description:
    - The name of the variable.
    required: true
    type: str
  value:
    description:
    - The value of the variable.
    default: ''
    type: str
  description:
    description:
    - The description of the variable.
    default: ''
    type: str
  category:
    description:
    - Whether this is a Terraform or environment variable.
    choices:
    - terraform
    - env
    required: true
    type: str
  hcl:
    description:
    - Whether to evaluate the value of the variable as a string of HCL code.
    - Has no effect for environment variables.
    default: False
    type: bool
  sensitive:
    description:
    - Whether the value is sensitive.
    - If true, variable is not visible in the UI.
    default: False
    type: bool
  varset_id:
    description:
    - The ID of the variable set hosting the variable.
    - It is mutually exclusive with C(workspace_id).
    type: str
  workspace_id:
    description:
    - the ID of the workspace hosting the variable.
    - It is mutually exclusive with C(varset_id).
    type: str
notes:
- One of C(varset_id) of C(workspace_id) must be specified.
'''

EXAMPLES = '''
- name: create a variable
  raphaeldegail.hcp_terraform.hcp_terraform_var:
    key: demovariable
    value: Demo Value
    category: terraform
    state: present
    varset_id: varset-000
'''

RETURN = '''
attributes:
  description:
  - Specify attributes of the object.
  returned: success
  type: dict
  contains:
    created-at:
      description:
      - The time of creattion of the object
      returned: success
      type: str
    key:
      description:
      - The name of the variable.
      returned: success
      type: str
    value:
      description:
      - The value of the variable.
      returned: success
      type: str
    description:
      description:
      - The description of the variable.
      returned: success
      type: str
    category:
      description:
      - Whether this is a Terraform or environment variable.
      returned: success
      type: str
    hcl:
      description:
      - Whether to evaluate the value of the variable as a string of HCL code.
      returned: success
      type: bool
    sensitive:
      description:
      - Whether the value is sensitive.
      returned: success
      type: bool
id:
  description:
  - The ID of the variable.
  returned: success
  type: str
links:
  description:
  - Additional data.
  returned: success
  type: dict
relationships:
  description:
  - Specify other objects that are linked to what you're working with.
  returned: success
  type: dict
type:
  description:
  - What type of API object you're interacting with.
  returned: success
  type: str
'''

ACTIVE = 'ACTIVE'

################################################################################
# Imports
################################################################################

from ansible_collections.raphaeldegail.hcp_terraform.plugins.module_utils.hcp_terraform_utils import (
    navigate_hash,
    HcpSession,
    HcpModule,
    HcpRequest,
)
import json

################################################################################
# Main
################################################################################


def main():
    """Main module function.

    Peforms a differential comparison and apply changes if needed.
    """

    module = HcpModule(
        argument_spec=dict(
            state=dict(default='present', choices=['present', 'absent'], type='str'),
            key=dict(required=True, type='str', no_log=False),
            value=dict(default='', type='str'),
            description=dict(default='', type='str'),
            category=dict(required=True, choices=['terraform', 'env'], type='str'),
            hcl=dict(default=False, type='bool'),
            sensitive=dict(default=False, type='bool'),
            varset_id=dict(type='str'),
            workspace_id=dict(type='str')
        ),
        mutually_exclusive=[
            ('varset_id', 'workspace_id'),
        ],
        required_one_of=[
            ('varset_id', 'workspace_id'),
        ]
    )

    state = module.params['state']

    resource = fetch_by_key(module, collection(module))
    changed = False

    if resource:
        module.params['var_id'] = resource['id']
        if state == 'present':
            if is_different(module, resource):
                update(module, self_link(module))
                resource = fetch_by_key(module, collection(module))
                changed = True
        else:
            delete(module, self_link(module))
            resource = {}
            changed = True
    else:
        if state == 'present':
            resource = create(module, collection(module))
            changed = True
        else:
            resource = {}

    resource.update({'changed': changed})

    module.exit_json(**resource)


def create(module, link):
    """Creates the object.

    Args:
        module: ansible_collections.raphaeldegail.hcp_terraform.plugins.module_utils.hcp_terraform_utils.HcpModule, the ansible module.
        link: str, the URL to call for the API operation.

    Returns:
        dict, the JSON-formatted response for the API call.
    """
    session = HcpSession(module)
    body = {'data': resource_to_request(module)}
    return return_if_object(module, session.post(link, body)).get('data')


def update(module, link):
    """Updates the object.

    Args:
        module: ansible_collections.raphaeldegail.hcp_terraform.plugins.module_utils.hcp_terraform_utils.HcpModule, the ansible module.
        link: str, the URL to call for the API operation.

    Returns:
        dict, the JSON-formatted response for the API call.
    """
    session = HcpSession(module)
    body = {'data': resource_to_request(module)}
    return return_if_object(module, session.patch(link, body)).get('data')


def delete(module, link):
    """Deletes the object.

    Args:
        module: ansible_collections.raphaeldegail.hcp_terraform.plugins.module_utils.hcp_terraform_utils.HcpModule, the ansible module.
        link: str, the URL to call for the API operation.

    Returns:
        None
    """
    session = HcpSession(module)
    return return_if_object(module, session.delete(link))


def fetch_by_key(module, link):
    """Fetch the existing resource by its key.

    Args:
        module: ansible_collections.raphaeldegail.hcp_terraform.plugins.module_utils.hcp_terraform_utils.HcpModule, the ansible module.
        link: str, the URL to call for the API operation.

    Returns:
        dict, the JSON-formatted response for the API call, if it exists.
    """
    session = HcpSession(module)
    return_list = return_if_object(module, session.get(link))
    for var in return_list['data']:
        if var.get('attributes', {}).get('key') == module.params['key'] and var.get('attributes', {}).get('category') == module.params['category']:
            return var
    return None


def collection(module):
    """The generic URL for the resource module.

    Args:
        module: ansible_collections.raphaeldegail.hcp_terraform.plugins.module_utils.hcp_terraform_utils.HcpModule, the ansible module.

    Returns:
        str, the generic URL for the resource module.
    """
    if module.params.get('workspace_id'):
        return 'https://app.terraform.io/api/v2/workspaces/{workspace_id}/vars'.format(**module.params)
    return 'https://app.terraform.io/api/v2/varsets/{varset_id}/relationships/vars'.format(**module.params)


def self_link(module):
    """The specific URL for the resource module.

    Args:
        module: ansible_collections.raphaeldegail.hcp_terraform.plugins.module_utils.hcp_terraform_utils.HcpModule, the ansible module.

    Returns:
        str, the specific URL for the resource module.
    """
    if module.params.get('workspace_id'):
        return 'https://app.terraform.io/api/v2/workspaces/{workspace_id}/vars/{var_id}'.format(**module.params)
    return 'https://app.terraform.io/api/v2/varsets/{varset_id}/relationships/vars/{var_id}'.format(**module.params)


def return_if_object(module, response, allow_not_found=False):
    """The generic URL for the resource module.

    Args:
        module: ansible_collections.raphaeldegail.hcp_terraform.plugins.module_utils.hcp_terraform_utils.HcpModule, the ansible module.
        response: dict, The response to process.
        allow_not_found: bool, Whether a not found response should be processed. Defaults to False.

    Returns:
        str, the JSON-formatted reponse, if it exists.
    """
    # If not found, return nothing.
    if allow_not_found and response.status_code == 404:
        return None

    # If no content, return nothing.
    if response.status_code == 204:
        return None

    # Return on 403 if not exist
    if allow_not_found and response.status_code == 403:
        return None

    try:
        result = response.json()
    except getattr(json.decoder, 'JSONDecodeError', ValueError) as inst:
        module.fail_json(msg=f'Invalid JSON response with error: {str(inst)}')

    if navigate_hash(result, ['errors']):
        module.fail_json(msg=navigate_hash(result, ['errors']))

    return result


def is_different(module, response):
    """Performs a differential comparison between the request and the response.

    Args:
        module: ansible_collections.raphaeldegail.hcp_terraform.plugins.module_utils.hcp_terraform_utils.HcpModule, the ansible module.
        response: dict, The response to process.

    Returns:
        bool, True if request and response are different.
    """
    request = resource_to_request(module)
    response = response_to_hash(response)

    return HcpRequest(request) != HcpRequest(response)


def resource_to_request(module):
    """Build the request for API calls.

    Args:
        module: ansible_collections.raphaeldegail.hcp_terraform.plugins.module_utils.hcp_terraform_utils.HcpModule, the ansible module.

    Returns:
        dict, the JSON-formatted request.
    """
    request = {
        'attributes': {
            'key': module.params.get('key'),
            'value': module.params.get('value'),
            'description': module.params.get('description'),
            'category': module.params.get('category'),
            'hcl': module.params.get('hcl'),
            'sensitive': module.params.get('sensitive')
        },
        'type': 'vars'
    }

    return request


def response_to_hash(response):
    """Remove unnecessary properties from the response.

    This is for doing comparisons with Ansible's current parameters.

    Args:
        response: dict, The response to process.

    Returns:
        dict, the processed response.
    """
    return {
        'attributes': {
            'key': response.get('attributes').get('key'),
            'value': response.get('attributes').get('value'),
            'description': response.get('attributes').get('description'),
            'category': response.get('attributes').get('category'),
            'hcl': response.get('attributes').get('hcl'),
            'sensitive': response.get('attributes').get('sensitive')
        }
    }


if __name__ == '__main__':
    main()
