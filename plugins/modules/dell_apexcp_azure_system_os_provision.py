# Copyright (c) 2023 Dell Inc. or its subsidiaries. All Rights Reserved.
#
# This software contains the intellectual property of Dell Inc. or is licensed to Dell Inc. from third parties.
# Use of this software and the intellectual property contained therein is expressly limited to the terms and
# conditions of the License Agreement under which it is provided by or on
# behalf of Dell Inc. or its subsidiaries.
from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

DOCUMENTATION = r'''
---
module: dell_apexcp_azure_system_os_provision

short_description: Perform OS provision process

# If this is part of a collection, you need to use semantic versioning,
# i.e. the version is of the form "2.5.0" and not "2.4".
version_added: "1.0.0"

description:
- This module will install Azure Stack HCI OS on specified hosts. 
options:
  primary_host_ip:
    description:
      The primary node IP
    required: True
    type: str

  cloud_platform_manager_ip:
    description:
      The ip address of APEX Cloud Platform Manager.
    required: True
    type: str

  day1_json_file:
    description:
      The path of Day1 Json file.
    required: True
    type: str

  timeout:
    description:
      Time out value for system os provision, the default value is 7200 seconds
    required: false
    type: int
    default: 7200

author:
    - APEX Cloud Platform Ansible Development Team(@xxxx) <ansible.team@dell.com>
'''

EXAMPLES = r'''
- name: OS Provision
  dell_apexcp_azure_system_os_provision
    primary_host_ip: "{{ primary_host_ip }}"
    cloud_platform_manager_ip: "{{ cloud_platform_manager_ip }}"
    day1_json_file: "{{ day1_json_file }}"
'''

RETURN = r'''
changed:
    description: Whether or not the resource has changed.
    returned: always
    type: bool
os_provision_result:
  description: Azure Stack HCI OS installation status summary
  returned: always
  type: dict
msg:
  description: The message for OS provision.
  returned: always
  type: string
  sample: >-
   {
    "changed": true,
    "os_provision_result": {
        "request_id": "433d0a61-06e7-4cb8-a1eb-985ab9a8b5dd",
        "status": "COMPLETED",
        "install_detail":{}
    }
    "msg": "HCI OS installation is successful. Please see the /tmp/apexcp_azure_system_os_provision.log for more details"
   }
'''

import urllib3
from ansible.module_utils.basic import AnsibleModule
import json
import os
# from plugins.module_utils import dellemc_apexcp_azure_ansible_utils as utils
from ansible_collections.dellemc.apexcp_azure.plugins.module_utils import dell_apexcp_azure_ansible_utils as utils
from ansible_collections.dellemc.apexcp_azure.plugins.module_utils import install_and_deployment_utils

log_file_name = "/tmp/apexcp_azure_system_os_provision.log"
LOGGER = utils.get_logger(module_name="dell_apexcp_azure_system_os_provision",
                          log_file_name=log_file_name)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

MAX_ERROR_COUNT = 90
CHECK_STATUS_INTERVAL = 60
MAX_CHECK_COUNT = 120


def main():
    ''' Entry point into execution flow '''
    global module
    # define available arguments/parameters a user can pass to the module
    module_args = dict(
        primary_host_ip=dict(required=True),
        cloud_platform_manager_ip=dict(required=True),
        day1_json_file=dict(required=True),
        timeout=dict(type='int', default=MAX_CHECK_COUNT * CHECK_STATUS_INTERVAL)
    )
    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True,
    )
    LOGGER.info(f'The parameter is {json.dumps(module.params)}')
    file = module.params.get('day1_json_file')
    if os.path.isfile(file):
        LOGGER.info('HCI OS installation using JSON file %s', module.params.get('day1_json_file'))
        with open(file, encoding='utf_8') as f:
            config_json = json.load(f)
    else:
        LOGGER.error('File cannot not be opened or does not exit, please verify and try again')
        module.fail_json(msg="JSON file not found!")

    os_provision_utility = install_and_deployment_utils.OSProvision(module, LOGGER, timeout=7200)
    LOGGER.info("----Install GI----")
    installation_request_id = os_provision_utility.start_os_provision(config_json)
    if installation_request_id == "error":
        LOGGER.info("------HCI OS installation task startup Failed-----")
        module.fail_json(
            msg=f"HCI OS installation task startup Failed. Please see the {log_file_name} for more details")

    LOGGER.info('HCI OS Initialization: task ID: %s.', installation_request_id)
    os_provision_status, install_detail = os_provision_utility.check_os_provision_status()

    os_provision_result = {'status': os_provision_status,
                              'request_id': installation_request_id,
                              'install_detail': install_detail
                              }
    if os_provision_status == 'COMPLETED':
        LOGGER.info("-----HCI OS provision Completed-----")
        msg = f'HCI OS installation is successful. Please see the {log_file_name}  for more details'
        facts_result = dict(changed=True, os_provision_result=os_provision_result, msg=msg)
    else:
        LOGGER.info("------HCI OS provision Failed-----")
        msg = f'HCI OS installation failed. Please see the {log_file_name} for more details'
        facts_result = dict(failed=True, os_provision_result=os_provision_result, msg=msg)
    module.exit_json(**facts_result)


if __name__ == '__main__':
    main()
