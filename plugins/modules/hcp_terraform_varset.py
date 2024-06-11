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
module: hcp_terraform_varset
description:
- Represents an HCP Terraform Variable set.
- A variable set is a container for variables with bindings to workspaces or projects.
short_description: Creates an HCP Terraform Variable set
author: Raphaël de Gail (@RaphaeldeGail)
requirements:
- python >= 3.11
- requests >= 2.32.2
extends_documentation_fragment:
- raphaeldegail.hcp_terraform.hcp_terraform
- raphaeldegail.hcp_terraform.hcp_terraform.organization
options:
  state:
    description:
    - Whether the given object should exist in HCP Terraform
    choices:
    - present
    - absent
    default: present
    type: str
  name:
    description:
    - The name of the variable set.
    required: true
    type: str
  description:
    description:
    - Text displayed in the UI to contextualize the variable set and its purpose.
    default: ''
    type: str
  global_set:
    description:
    - When true, HCP Terraform automatically applies the variable set to all current and future workspaces in the organization.
    default: False
    type: bool
  priority:
    description:
    - When true, the variables in the set override any other variable values with a more specific scope, including values set on the command line.
    default: False
    type: bool
  workspaces:
    description:
    - Array of references to workspaces that the variable set should be assigned to.
    default: []
    type: list
    elements: str
  projects:
    description:
    - Array of references to projects that the variable set should be assigned to.
    default: []
    type: list
    elements: str
notes:
  - variables inside variable set are treated in a separate module, hcp_terraform_varset_var.
'''

EXAMPLES = '''
- name: create a variable set
  raphaeldegail.hcp_terraform.hcp_terraform_varset:
    name: MySampleVariableSet
    description: 'This is my sample variable set.'
    state: present
- name: update a variable set with projects bindings
  raphaeldegail.hcp_terraform.hcp_terraform_varset:
    name: MySampleVariableSet
    description: 'This is my sample variable set.'
    # This is a list of projects ID in the organization.
    projects:
    - 'prj-000'
    - 'prj-123'
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
      - The time of creation of the object
      returned: success
      type: str
    description:
      description:
      - Text displayed in the UI to contextualize the variable set and its purpose.
      returned: success
      type: str
    name:
      description:
      - The name of the variable set.
      returned: success
      type: str
    global_set:
      description:
      - When true, HCP Terraform automatically applies the variable set to all current and future workspaces in the organization.
      type: bool
    priority:
      description:
      - When true, the variables in the set override any other variable values with a more specific scope, including values set on the command line.
      type: bool
id:
  description:
  - The ID of the project.
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
  contains:
    workspaces:
      description:
      - Array of references to workspaces that the variable set is assigned to.
      returned: success
      type: list
      elements: dict
      contains:
        id:
          description:
          - The ID of the workspace.
          returned: success
          type: str
        type:
          description:
          - Must be 'workspaces'.
          returned: success
          type: str
    projects:
      description:
      - Array of references to projects that the variable set is assigned to.
      returned: success
      type: list
      elements: dict
      contains:
        id:
          description:
          - The ID of the project.
          returned: success
          type: str
        type:
          description:
          - Must be 'projects'.
          returned: success
          type: str
    vars:
      description:
      - Array of references to variables that comprise the variable set.
      returned: success
      type: list
      elements: dict
      contains:
        id:
          description:
          - Must be 'vars'.
          returned: success
          type: str
        type:
          description:
          - What type of API object you're interacting with.
          returned: success
          type: str
type:
  description:
  - What type of API object you're interacting with.
  - Must be 'varsets'.
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
            name=dict(required=True, type='str'),
            description=dict(default='', type='str'),
            global_set=dict(default=False, type='bool'),
            priority=dict(default=False, type='bool'),
            workspaces=dict(default=[], type='list', elements='str'),
            projects=dict(default=[], type='list', elements='str'),
            organization_name=dict(required=True, type='str'),
        )
    )

    state = module.params['state']

    resource = fetch_by_name(module, collection(module))
    changed = False

    if resource:
        module.params['varset_id'] = resource['id']
        if state == 'present':
            if is_different(module, resource):
                update(module, self_link(module))
                resource = get(module, self_link(module))
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


def get(module, link):
    """Fetch the existing resource by its ID.

    Args:
        module: ansible_collections.raphaeldegail.hcp_terraform.plugins.module_utils.hcp_terraform_utils.HcpModule, the ansible module.
        link: str, the URL to call for the API operation.

    Returns:
        dict, the JSON-formatted response for the API call, if it exists.
    """
    session = HcpSession(module)
    return return_if_object(module, session.get(link)).get('data')


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
    return return_if_object(module, session.put(link, body)).get('data')


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


def fetch_by_name(module, link):
    """Fetch the existing resource by its name.

    Args:
        module: ansible_collections.raphaeldegail.hcp_terraform.plugins.module_utils.hcp_terraform_utils.HcpModule, the ansible module.
        link: str, the URL to call for the API operation.

    Returns:
        dict, the JSON-formatted response for the API call, if it exists.
    """
    session = HcpSession(module)
    params = {
        'q': module.params.get('name')
    }
    return_list = session.list(link, return_if_object, params=params)
    if len(return_list) > 1:
        module.fail_json(msg=f'Expected 1 result, found: {len(return_list)}: {str(return_list)}')
    if return_list:
        return return_list.pop(0)
    return None


def collection(module):
    """The generic URL for the resource module.

    Args:
        module: ansible_collections.raphaeldegail.hcp_terraform.plugins.module_utils.hcp_terraform_utils.HcpModule, the ansible module.

    Returns:
        str, the generic URL for the resource module.
    """
    return 'https://app.terraform.io/api/v2/organizations/{organization_name}/varsets'.format(**module.params)


def self_link(module):
    """The specific URL for the resource module.

    Args:
        module: ansible_collections.raphaeldegail.hcp_terraform.plugins.module_utils.hcp_terraform_utils.HcpModule, the ansible module.

    Returns:
        str, the specific URL for the resource module.
    """
    return 'https://app.terraform.io/api/v2/varsets/{varset_id}'.format(**module.params)


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
            'name': module.params.get('name'),
            'description': module.params.get('description'),
            'global': module.params.get('global_set'),
            'priority': module.params.get('priority')
        },
        'relationships': {
            'workspaces': {
                'data': [
                    {'id': workspace, 'type': 'workspaces'} for workspace in module.params.get('workspaces')
                ]
            },
            'projects': {
                'data': [
                    {'id': project, 'type': 'projects'} for project in module.params.get('projects')
                ]
            }
        },
        'type': 'varsets'
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
            'name': response.get('attributes').get('name'),
            'description': response.get('attributes').get('description') or '',
            'global': response.get('attributes').get('global'),
            'priority': response.get('attributes').get('priority')
        },
        'relationships': {
            'workspaces': {
                'data': response.get('relationships').get('workspaces').get('data')
            },
            'projects': {
                'data': response.get('relationships').get('projects').get('data')
            }
        }
    }


if __name__ == '__main__':
    main()
