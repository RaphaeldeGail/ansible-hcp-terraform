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
module: hcp_terraform_workspace
description:
- Represents an HCP Terraform Workspace.
- Workspaces represent running infrastructure managed by Terraform.
short_description: Creates an HCP Terraform Workspace
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
    - The name of the workspace, which can only include letters, numbers, -, and _.
    - This will be used as an identifier and must be unique in the organization.
    required: true
    type: str
  agent_pool_id:
    description:
    - Required when execution_mode is set to agent.
    - The ID of the agent pool belonging to the workspace's organization.
    - This value must not be specified if execution_mode is set to remote or local.
    type: str
  allow_destroy_plan:
    description:
    - Whether destroy plans can be queued on the workspace.
    default: True
    type: bool
  assessments_enabled:
    description:
    - (previously drift-detection)
    - Whether or not HCP Terraform performs health assessments for the workspace.
    - May be overriden by the organization setting assessments-enforced.
    - Only available for Plus tier organizations, in workspaces running Terraform version 0.15.4+ and operating in Remote execution mode.
    default: False
    type: bool
  auto_apply:
    description:
    - Whether to automatically apply changes when a Terraform plan is successful in runs initiated by VCS, UI or CLI, with some exceptions.
    default: False
    type: bool
  auto_apply_run_trigger:
    description:
    - Whether to automatically apply changes when a Terraform plan is successful in runs initiated by run triggers.
    default: False
    type: bool
  auto_destroy_at:
    description:
    - Timestamp when the next scheduled destroy run will occur, refer to Scheduled Destroy.
    type: str
  auto_destroy_activity_duration:
    description:
    - Value and units for automatically scheduled destroy runs based on workspace activity.
    - Valid values are greater than 0 and four digits or less.
    - Valid units are d and h.
    - 'For example, to queue destroy runs after fourteen days of inactivity set auto_destroy_activity_duration: "14d".'
    type: str
  description:
    description:
    - A description for the workspace.
    default: ''
    type: str
  execution_mode:
    description:
    - Which execution mode to use.
    - When set to local, the workspace will be used for state storage only.
    - This value must not be specified if operations is specified, and must be specified if setting_overwrites.execution-mode is set to true.
    choices:
    - remote
    - local
    - agent
    type: str
  file_triggers_enabled:
    description:
    - Whether to filter runs based on the changed files in a VCS push.
    - If enabled, it uses either trigger_prefixes in conjunction with working_directory
      or trigger_patterns to describe the set of changed files that will start a run.
    - If disabled, any push will trigger a run.
    default: True
    type: bool
  global_remote_state:
    description:
    - Whether the workspace should allow all workspaces in the organization to access its state data during runs.
    - If false, then only specifically approved workspaces can access its state.
    - Manage allowed workspaces using the Remote State Consumers endpoints.
    - Terraform Enterprise admins can choose the default value for new workspaces if this attribute is omitted.
    default: False
    type: bool
  queue_all_runs:
    description:
    - Whether runs should be queued immediately after workspace creation.
    - When set to false, runs triggered by a VCS change will not be queued until at least one run is manually queued.
    default: False
    type: bool
  source_name:
    description:
    - A friendly name for the application or client creating this workspace.
    - If set, this will be displayed on the workspace as "Created via <SOURCE NAME>".
    type: str
  source_url:
    description:
    - A URL for the application or client creating this workspace.
    - This can be the URL of a related resource in another app, or a link to documentation or other info about the client.
    type: str
  speculative_enabled:
    description:
    - Whether this workspace allows automatic speculative plans.
    - Setting this to false prevents HCP Terraform from running plans on pull requests,
      which can improve security if the VCS repository is public or includes untrusted contributors.
    - It doesn't prevent manual speculative plans via the CLI or the runs API.
    default: True
    type: bool
  terraform_version:
    description:
    - The version of Terraform to use for this workspace.
    - This can be either an exact version or a version constraint (like ~> 1.0.0);
      if you specify a constraint, the workspace will always use the newest release that meets that constraint.
    - If omitted when creating a workspace, this defaults to the latest released version.
    type: str
  trigger_patterns:
    description:
    - List of glob patterns that describe the files HCP Terraform monitors for changes.
    - Trigger patterns are always appended to the root directory of the repository.
    default: []
    type: list
    elements: str
  trigger_prefixes:
    description:
    - List of trigger prefixes that describe the paths HCP Terraform monitors for changes, in addition to the working directory.
    - Trigger prefixes are always appended to the root directory of the repository.
    - HCP Terraform will start a run when files are changed in any directory path matching the provided set of prefixes.
    default: []
    type: list
    elements: str
  vcs_repo:
    description:
    - Settings for the workspace's VCS repository.
    - If omitted, the workspace is created without a VCS repo.
    - If included, you must specify at least the oauth-token-id and identifier keys below.
    type: dict
    suboptions:
      branch:
        description:
        - The repository branch that Terraform will execute from.
        - If omitted or submitted as an empty string, this defaults to the repository's default branch (e.g. master) .
        type: str
      identifier:
        description:
        - A reference to your VCS repository in the format :org/:repo where :org and :repo refer to the organization and repository in your VCS provider.
        - The format for Azure DevOps is :org/:project/_git/:repo.
        required: true
        type: str
      ingress_submodules:
        description:
        - Whether submodules should be fetched when cloning the VCS repository.
        default: False
        type: bool
      oauth_token_id:
        description:
        - The VCS Connection (OAuth Connection + Token) to use.
        - This ID can be obtained from the oauth-tokens endpoint.
        required: true
        type: str
      tags_regex:
        description:
        - A regular expression used to match Git tags.
        - HCP Terraform triggers a run when this value is present and a VCS event occurs that contains a matching Git tag for the regular expression.
        type: str
  working_directory:
    description:
    - A relative path that Terraform will execute within.
    - This defaults to the root of your repository and is typically set to
      a subdirectory matching the environment when multiple environments exist within the same repository.
    type: str
  setting_overwrites:
    description:
    - The keys in this object are attributes that have organization-level defaults.
    - Each attribute key stores a boolean value which is true by default.
    - To overwrite the default inherited value, set an attribute's value to false.
    - For example, to set execution-mode as the organization default, you set setting-overwrites.execution-mode = false.
    type: dict
  project:
    description:
    - The ID of the project to create the workspace in.
    - If left blank, the workspace will be created in the organization's default project.
    - You must have permission to create workspaces in the project, either by organization-level permissions or team admin access to a specific project.
    type: str
'''

EXAMPLES = '''
- name: create a workspace
  raphaeldegail.hcp_terraform.hcp_terraform_workspace:
    name: MyDemoWorkspace
    description: 'This is my sample workspace.'
    state: present
- name: update a workspace with a VCS repository
  raphaeldegail.hcp_terraform.hcp_terraform_workspace:
    name: MyDemoWorkspace
    description: 'This is my sample workspace.'
    vcs_repo:
      identifier: 'RaphaeldeGail/ansible-hcp-terraform'
      oauth_token_id: 'ot-000'
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
            agent_pool_id=dict(type='str'),
            allow_destroy_plan=dict(default=True, type='bool'),
            assessments_enabled=dict(default=False, type='bool'),
            auto_apply=dict(default=False, type='bool'),
            auto_apply_run_trigger=dict(default=False, type='bool'),
            auto_destroy_at=dict(type='str'),
            auto_destroy_activity_duration=dict(type='str'),
            description=dict(default='', type='str'),
            execution_mode=dict(choices=['remote', 'local', 'agent'], type='str'),
            file_triggers_enabled=dict(default=True, type='bool'),
            global_remote_state=dict(default=False, type='bool'),
            queue_all_runs=dict(default=False, type='bool'),
            source_name=dict(type='str'),
            source_url=dict(type='str'),
            speculative_enabled=dict(default=True, type='bool'),
            terraform_version=dict(type='str'),
            trigger_patterns=dict(default=[], type='list', elements='str'),
            trigger_prefixes=dict(default=[], type='list', elements='str'),
            vcs_repo=dict(default=None, type='dict', options=dict(
                branch=dict(type='str'),
                identifier=dict(required=True, type='str'),
                ingress_submodules=dict(default=False, type='bool'),
                oauth_token_id=dict(required=True, type='str'),
                tags_regex=dict(type='str'),
            )),
            working_directory=dict(type='str'),
            setting_overwrites=dict(type='dict'),
            project=dict(type='str'),
            organization_name=dict(required=True, type='str'),
        ),
        required_if=[
            ('execution_mode', 'agent', ('agent_pool_id',), True),
        ]
    )

    state = module.params['state']

    resource = fetch_by_name(module, collection(module))
    changed = False

    if resource:
        module.params['workspace_id'] = resource['id']
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
        'search[name]': module.params.get('name'),
        'filter[project][id]': module.params.get('project')
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
    return 'https://app.terraform.io/api/v2/organizations/{organization_name}/workspaces'.format(**module.params)


def self_link(module):
    """The specific URL for the resource module.

    Args:
        module: ansible_collections.raphaeldegail.hcp_terraform.plugins.module_utils.hcp_terraform_utils.HcpModule, the ansible module.

    Returns:
        str, the specific URL for the resource module.
    """
    return 'https://app.terraform.io/api/v2/workspaces/{workspace_id}'.format(**module.params)


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
            'allow-destroy-plan': module.params.get('allow_destroy_plan'),
            'assessments-enabled': module.params.get('assessments_enabled'),
            'auto-apply': module.params.get('auto_apply'),
            'auto-apply-run-trigger': module.params.get('auto_apply_run_trigger'),
            'file-triggers-enabled': module.params.get('file_triggers_enabled'),
            'global-remote-state': module.params.get('global_remote_state'),
            'queue-all-runs': module.params.get('queue_all_runs'),
            'trigger-patterns': module.params.get('trigger_patterns'),
            'trigger-prefixes': module.params.get('trigger_prefixes'),
            'description': module.params.get('description'),
            'auto-destroy-at': module.params.get('auto_destroy_at'),
            'auto-destroy-activity-duration': module.params.get('auto_destroy_activity_duration'),
            'source-name': module.params.get('source_name'),
            'source-url': module.params.get('source_url'),
            'speculative-enabled': module.params.get('speculative_enabled'),
            'working-directory': module.params.get('working_directory'),
            'setting-overwrites': module.params.get('setting_overwrites'),
            'terraform-version': module.params.get('terraform_version'),
            'agent-pool-id': module.params.get('agent_pool_id')
        },
        'type': 'workspaces'
    }
    request.update({
        'relationships': {
            'project': {
                'data': [
                    {'id': module.params.get('project'), 'type': 'projects'}
                ]
            }
        }
    } if module.params.get('project') else {})
    request['attributes'].update({'execution-mode': module.params.get('execution_mode')} if module.params.get('execution_mode') else {})
    vcs_repo = module.params.get('vcs_repo')
    request['attributes'].update({
        'vcs-repo': {
            'branch': vcs_repo.get('branch'),
            'identifier': vcs_repo.get('identifier'),
            'ingress-submodules': vcs_repo.get('ingress_submodules'),
            'oauth-token-id': vcs_repo.get('oauth_token_id'),
            'tags-regex': vcs_repo.get('tags_regex')
        } if vcs_repo else {}
    })

    return request


def response_to_hash(response):
    """Remove unnecessary properties from the response.

    This is for doing comparisons with Ansible's current parameters.

    Args:
        response: dict, The response to process.

    Returns:
        dict, the processed response.
    """
    attributes = response.get('attributes')
    return {
        'attributes': {
            'name': attributes.get('name'),
            'agent-pool-id': attributes.get('agent-pool-id'),
            'allow-destroy-plan': attributes.get('allow-destroy-plan'),
            'assessments-enabled': attributes.get('assessments-enabled'),
            'auto-apply': attributes.get('auto-apply'),
            'auto-apply-run-trigger': attributes.get('auto-apply-run-trigger'),
            'auto-destroy-at': attributes.get('auto-destroy-at'),
            'auto-destroy-activity-duration': attributes.get('auto-destroy-activity-duration'),
            'description': attributes.get('description'),
            'execution-mode': attributes.get('execution-mode'),
            'file-triggers-enabled': attributes.get('file-triggers-enabled'),
            'global-remote-state': attributes.get('global-remote-state'),
            'queue-all-runs': attributes.get('queue-all-runs'),
            'source-name': attributes.get('source-name'),
            'source-url': attributes.get('source-url'),
            'speculative-enabled': attributes.get('speculative-enabled'),
            'terraform-version': attributes.get('terraform-version'),
            'trigger-patterns': attributes.get('trigger-patterns'),
            'trigger-prefixes': attributes.get('trigger-prefixes'),
            'vcs-repo': {
                'branch': attributes.get('vcs-repo', {}).get('branch'),
                'identifier': attributes.get('vcs-repo', {}).get('identifier'),
                'ingress-submodules': attributes.get('vcs-repo', {}).get('ingress-submodules'),
                'oauth-token-id': attributes.get('vcs-repo', {}).get('oauth-token-id'),
                'tags-regex': attributes.get('vcs-repo', {}).get('tags-regex')
            },
            'working-directory': attributes.get('working-directory'),
            'setting-overwrites': attributes.get('setting-overwrites')
        },
        'relationships': {
            'project': {
                'data': response.get('relationships').get('project').get('data')
            }
        }
    }


if __name__ == '__main__':
    main()
