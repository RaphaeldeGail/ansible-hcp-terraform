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
module: hcp_terraform_project_info
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
  name:
    description:
    - The user-assigned display name of the Project.
    required: true
    type: str
'''

EXAMPLES = '''
- name: fetch info about a project
  raphaeldegail.hcp_terraform.hcp_terraform_project_info:
    name: My Sample Project
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
)
import json

################################################################################
# Main
################################################################################


def main():
    """Main module function.

    Fetch the project on HCP Terraform platform.
    """

    module = HcpModule(
        argument_spec=dict(
            name=dict(required=True, type='str'),
            organization_name=dict(required=True, type='str'),
        ),
        supports_check_mode=True
    )

    if module.check_mode:
        result = module.params
        result['changed'] = False
        module.exit_json(**result)

    resource = fetch_by_name(module, collection(module))
    changed = False

    if not resource:
        resource = {}
    resource.update({'changed': changed})

    module.exit_json(**resource)


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
    if response.status_code == 404:
        return None

    # If no content, return nothing.
    if response.status_code == 204:
        return None

    try:
        module.raise_for_status(response)
        result = response.json()
    except getattr(json.decoder, 'JSONDecodeError', ValueError) as inst:
        module.fail_json(msg=f'Invalid JSON response with error: {str(inst)}')

    if navigate_hash(result, ['errors']):
        module.fail_json(msg=navigate_hash(result, ['errors']))

    return result


if __name__ == '__main__':
    main()
