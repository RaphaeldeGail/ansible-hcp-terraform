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
module: hcp_terraform_workspace_info
description:
- Fetches information about an HCP Terraform Workspace.
- Workspaces represent running infrastructure managed by Terraform.
short_description: Query an HCP Terraform Workspace
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
    - The name of the workspace.
    required: true
    type: str
'''

EXAMPLES = '''
- name: fetch info about a workspace
  raphaeldegail.hcp_terraform.hcp_terraform_workspace_info:
    name: MyDemoWorkspace
  register: workspace
- name: print the ID fo the workspace
  ansible.builtin.debug:
    msg: "{{ workspace.id }}"
'''

RETURN = '''
attributes:
  description:
  - Specify attributes of the object.
  returned: success
  type: dict
  contains:
    agent-pool-id:
      description:
      - The ID of the agent pool belonging to the workspace's organization.
      returned: success
      type: str
    allow-destroy-plan:
      description:
      - Whether destroy plans can be queued on the workspace.
      returned: success
      type: bool
    apply-duration-average:
      description:
      - This is the average time runs spend in the apply phase, represented in milliseconds
      returned: success
      type: int
    assessments-enabled:
      description:
      - (previously drift-detection) Whether or not HCP Terraform performs health assessments for the workspace.
      returned: success
      type: bool
    auto-apply:
      description:
      - Whether to automatically apply changes when a Terraform plan is successful in runs initiated by VCS, UI or CLI, with some exceptions.
      returned: success
      type: bool
    auto-apply-run-trigger:
      description:
      - Whether to automatically apply changes when a Terraform plan is successful in runs initiated by run triggers.
      returned: success
      type: bool
    auto-destroy-activity-duration:
      description:
      - Value and units for automatically scheduled destroy runs based on workspace activity. Valid values are greater than 0 and four digits or less.
      - Valid units are d and h.
      returned: success
      type: str
    auto-destroy-at:
      description:
      - Timestamp when the next scheduled destroy run will occur, refer to Scheduled Destroy.
      returned: success
      type: str
    description:
      description:
      - A description for the workspace.
      returned: success
      type: str
    execution-mode:
      description:
      - Which execution mode to use.
      - Valid values are remote, local, and agent.
      returned: success
      type: str
    file-triggers-enabled:
      description:
      - Whether to filter runs based on the changed files in a VCS push.
      returned: success
      type: bool
    global-remote-state:
      description:
      - Whether the workspace should allow all workspaces in the organization to access its state data during runs.
      returned: success
      type: bool
    name:
      description:
      - The name of the workspace.
      returned: success
      type: str
    plan-duration-average:
      description:
      - This is the average time runs spend in the plan phase, represented in milliseconds.
      returned: success
      type: int
    policy-check-failures:
      description:
      - Reports the number of run failures resulting from a policy check failure.
      returned: success
      type: int
    queue-all-runs:
      description:
      - Whether runs should be queued immediately after workspace creation.
      returned: success
      type: bool
    run-failures:
      description:
      - Reports the number of failed runs.
      returned: success
      type: int
    setting-overwrites:
      description:
      - The keys in this object are attributes that have organization-level defaults.
      returned: success
      type: dict
    source-name:
      description:
      - A friendly name for the application or client creating this workspace.
      returned: success
      type: str
    source-url:
      description:
      - A URL for the application or client creating this workspace.
      returned: success
      type: str
    speculative-enabled:
      description:
      - Whether this workspace allows automatic speculative plans.
      returned: success
      type: bool
    terraform-version:
      description:
      - The version of Terraform to use for this workspace.
      returned: success
      type: str
    trigger-patterns:
      description:
      - List of glob patterns that describe the files HCP Terraform monitors for changes.
      returned: success
      type: list
    trigger-prefixes:
      description:
      - List of trigger prefixes that describe the paths HCP Terraform monitors for changes, in addition to the working directory.
      returned: success
      type: list
    vcs-repo:
      description:
      - Settings for the workspace's VCS repository.
      returned: success
      type: dict
      contains:
        branch:
          description:
          - The repository branch that Terraform will execute from.
          returned: success
          type: str
        identifier:
          description:
          - A reference to your VCS repository in the format :org/:repo where :org and :repo refer to the organization and repository in your VCS provider.
          returned: success
          type: str
        ingress-submodules:
          description:
          - Whether submodules should be fetched when cloning the VCS repository.
          returned: success
          type: bool
        oauth-token-id:
          description:
          - The VCS Connection (OAuth Connection + Token) to use.
          returned: success
          type: str
        tags-regex:
          description:
          - A regular expression used to match Git tags.
          returned: success
          type: str
    working-directory:
      description:
      - A relative path that Terraform will execute within.
      returned: success
      type: str
    workspace-kpis-runs-count:
      description:
      - Total number of runs taken into account by these metrics.
      returned: success
      type: int
id:
  description:
  - The ID of the workspace.
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
    project:
      description:
      - The ID of the project hosting the workspace.
      returned: success
      type: dict
      contains:
        data:
          description:
          - The data about the project
          returned: success
          type: dict
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
      - Array of references to variables that comprise the workspace.
      returned: success
      type: dict
      contains:
        data:
          description:
          - The data about the variables
          returned: success
          type: list
          elements: dict
          contains:
            id:
              description:
              - The ID of the variable.
              returned: success
              type: str
            type:
              description:
              - Must be 'vars'.
              returned: success
              type: str
type:
  description:
  - What type of API object you're interacting with.
  - Must be 'workspaces'.
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
        'search[name]': module.params.get('name')
    }
    return_list = session.list(link, return_if_object, params=params)
    for item in return_list:
        if item.get('attributes', {}).get('name') == module.params.get('name'):
            return item
    return None


def collection(module):
    """The generic URL for the resource module.

    Args:
        module: ansible_collections.raphaeldegail.hcp_terraform.plugins.module_utils.hcp_terraform_utils.HcpModule, the ansible module.

    Returns:
        str, the generic URL for the resource module.
    """
    return 'https://app.terraform.io/api/v2/organizations/{organization_name}/workspaces'.format(**module.params)


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
