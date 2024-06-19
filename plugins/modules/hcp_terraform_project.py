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
module: hcp_terraform_project
description:
- Represents an HCP Terraform Project.
- A project is a container for terraform workspaces with specific variables.
short_description: Creates an HCP Terraform Project
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
    - The user-assigned display name of the Project.
    - The name can contain letters, numbers, spaces, -, and _, but cannot start or end with spaces.
    - It must be at least 3 characters long and no more than 40 characters long.
    required: true
    type: str
  description:
    description:
    - The description of the Project.
    - It must be no more than 256 characters long.
    type: str
'''

EXAMPLES = '''
- name: create a project
  raphaeldegail.hcp_terraform.hcp_terraform_project:
    name: My Sample Project
    state: present
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
    description:
      description:
      - The description of the project.
      returned: success
      type: str
    name:
      description:
      - The name of the project.
      returned: success
      type: str
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
            name=dict(required=True, type='str'),
            description=dict(type='str'),
            organization_name=dict(required=True, type='str'),
        )
    )

    state = module.params['state']

    resource = fetch_by_name(module, collection(module))
    changed = False

    if resource:
        module.params['project_id'] = resource['id']
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
        'filter[names]': module.params.get('name')
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
    return 'https://app.terraform.io/api/v2/organizations/{organization_name}/projects'.format(**module.params)


def self_link(module):
    """The specific URL for the resource module.

    Args:
        module: ansible_collections.raphaeldegail.hcp_terraform.plugins.module_utils.hcp_terraform_utils.HcpModule, the ansible module.

    Returns:
        str, the specific URL for the resource module.
    """
    return 'https://app.terraform.io/api/v2/projects/{project_id}'.format(**module.params)


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
        },
        'type': 'projects'
    }
    # Clears any entry with a null value
    return_vals = {}
    for k, v in request.items():
        if v or v is False:
            return_vals[k] = v

    return return_vals


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
            'description': response.get('attributes').get('description') or ''
        }
    }


if __name__ == '__main__':
    main()
