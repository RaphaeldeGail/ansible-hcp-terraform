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
module: hcp_terraform_var_info
description:
- Fetches information about an HCP Terraform Variable.
short_description: Query an HCP Terraform Variable
author: Raphaël de Gail (@RaphaeldeGail)
requirements:
- python >= 3.11
- requests >= 2.32.2
extends_documentation_fragment:
- raphaeldegail.hcp_terraform.hcp_terraform
options:
  key:
    description:
    - The name of the variable.
    required: true
    type: str
  category:
    description:
    - Whether this is a Terraform or environment variable.
    choices:
    - terraform
    - env
    required: true
    type: str
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
- name: fetch info about a variable
  raphaeldegail.hcp_terraform.hcp_terraform_var_info:
    key: demovariable
    category: terraform
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
)
import json

################################################################################
# Main
################################################################################


def main():
    """Main module function.

    Fetch the varset on HCP Terraform platform.
    """

    module = HcpModule(
        argument_spec=dict(
            key=dict(required=True, type='str', no_log=False),
            category=dict(required=True, choices=['terraform', 'env'], type='str'),
            varset_id=dict(type='str'),
            workspace_id=dict(type='str')
        ),
        mutually_exclusive=[
            ('varset_id', 'workspace_id'),
        ],
        required_one_of=[
            ('varset_id', 'workspace_id'),
        ],
        supports_check_mode=True
    )

    if module.check_mode:
        result = module.params
        result['changed'] = False
        module.exit_json(**result)

    resource = fetch_by_key(module, collection(module))
    changed = False

    if not resource:
        resource = {}
    resource.update({'changed': changed})

    module.exit_json(**resource)


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
        module.fail_json(msg=collection(module))
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
