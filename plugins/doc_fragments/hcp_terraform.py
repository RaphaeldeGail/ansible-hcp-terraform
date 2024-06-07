# -*- coding: utf-8 -*-
#
# Copyright: Raphaël de Gail
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)

__metaclass__ = type


class ModuleDocFragment(object):
    # HCP Terraform doc fragment.
    DOCUMENTATION = r'''
options:
    bearer_token:
        description:
        - An API token credential to access the HCP Terraform platform.
        required: true
        type: str
notes:
  - for authentication, you can set bearer_token using the
    c(HCP_TERRAFORM_TOKEN) env variable.
  - the bearer_token is not logged.
'''

    ORGANIZATION = r'''
options:
  organization_name:
    description:
    - The name of the organization to create the Project in.
    - The organization must already exist in the system, and the user must have permissions to create new projects.
    required: true
    type: str
'''
