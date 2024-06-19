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
module: dell_apexcp_azure_cluster_deployment

short_description: Perform the Day1 first run initialization of a Anacortes Cluster

# If this is part of a collection, you need to use semantic versioning,
# i.e. the version is of the form "2.5.0" and not "2.4".
version_added: "1.0.0"

description:
- This module will initialize LDAPS certificate, configure and deploy a new APEX Cloud Platform cluster 
  for Microsoft Azure based on the provided day1 json file.
options:
  cloud_platform_manager_ip:
    description:
      The ip address of APEX Cloud Platform Manager.
    required: True
    type: str

  ldaps_cert_file:
    description:
      The path of LDAPS certificate file
    required: True
    type: str

  day1_json_file:
    description:
      The path of Day1 Json file.
    required: True
    type: str

  timeout:
    description:
      Time out value for cluster deployment, the default value is 36000 seconds
    required: false
    type: int
    default: 36000

author:
    - Apex Cloud Platform Ansible Development Team(@xxxx) <ansible.team@dell.com>

'''

EXAMPLES = r'''
- name: Configure and deploy a new APEX Cloud Platform cluster for Azure
  dell_apexcp_azure_cluster_deployment:
    cloud_platform_manager_ip: "{{ cloud_platform_manager_ip }}"
    day1_json_file: "{{ day1_json_file }}"s
'''

RETURN = r'''
changed:
    description: Whether or not the resource has changed.
    returned: always
    type: bool
cluster_deployment_result:
  description: Cluster deployment status summary
  returned: always
  type: dict
  sample: >-
   {
    "cluster_deployment_result": {
        "request_id": "433d0a61-06e7-4cb8-a1eb-985ab9a8b5dd",
        "status": "COMPLETED"
    }
    "msg": "Cluster deployment is successful. Please see the /tmp/apexcp_azure_cluster_deployment.log for more details"
   }
'''

import urllib3
from ansible.module_utils.basic import AnsibleModule

import json
import os
from ansible_collections.dellemc.apexcp_azure.plugins.module_utils import dell_apexcp_azure_ansible_utils as utils
from ansible_collections.dellemc.apexcp_azure.plugins.module_utils import auth_api_utils
from ansible_collections.dellemc.apexcp_azure.plugins.module_utils import install_and_deployment_utils

# from plugins.module_utils import dell_apexcp_azure_ansible_utils as utils

log_file_name = "/tmp/apexcp_azure_cluster_deployment.log"
LOGGER = utils.get_logger(module_name="dell_apexcp_azure_cluster_deployment",
                          log_file_name=log_file_name)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

MAX_ERROR_COUNT = 10
CHECK_STATUS_INTERVAL = 60
MAX_CHECK_COUNT = 600


def main():
    ''' Entry point into execution flow '''
    global module
    # define available arguments/parameters a user can pass to the module
    module_args = dict(
        cloud_platform_manager_ip=dict(required=True),
        day1_json_file=dict(required=True),
        ldaps_cert_file=dict(required=True),
        timeout=dict(type='int', default=MAX_CHECK_COUNT * CHECK_STATUS_INTERVAL)
    )
    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True,
    )
    LOGGER.info(f'The parameter is {json.dumps(module.params)}')
    initial_timeout = module.params.get('timeout')
    file = module.params.get('day1_json_file')
    if os.path.isfile(file):
        LOGGER.info('Apex for azure initialize using JSON file %s', file)
        with open(file, encoding='utf_8') as f:
            config_json = json.load(f)
    else:
        LOGGER.error('Day1 json file cannot not be opened or does not exit, please verify and try again')
        module.fail_json(msg="Day1 json file not found!")

    cert_file = module.params.get('ldaps_cert_file')
    if os.path.isfile(cert_file):
        LOGGER.info('Initialize LDAPS certificate by using file %s', file)
        with open(cert_file, encoding='utf_8') as f:
            ldaps_cert_content = "".join(f.readlines())
    else:
        LOGGER.error('LDAPS certificate File can not be opened or does not exit, please verify and try again')
        module.fail_json(msg="LDAPS certificate file not found!")

    LOGGER.info("----Initialize LDAPS certificate----")
    response = auth_api_utils.InitializeLdapsCert(module, LOGGER).initialize_cert(ldaps_cert_content)
    LOGGER.info(f"----Result of initialize LDAPS certificate {response}-----")
    if response == "error":
        module.fail_json(
            msg=f"Call initialize LDAPS certificate API failed. Please see the {log_file_name} for more details")
    else:
        LOGGER.info(f"Initialize LDAPS certificate is successful.")

    deployment_utility = install_and_deployment_utils.ClusterDeployment(module, LOGGER)
    cloud_platform_manager_ip_in_json = config_json.get("cloud_platform_manager", {}).get("ip")
    if cloud_platform_manager_ip_in_json != module.params.get('cloud_platform_manager_ip'):
        new_cloud_platform_manager_ip = cloud_platform_manager_ip_in_json
    else:
        new_cloud_platform_manager_ip = None
    if new_cloud_platform_manager_ip:
        LOGGER.info('Cloud platform manager IP will change to %s during installation', new_cloud_platform_manager_ip)
        deployment_utility.new_cloud_platform_manager_ip = new_cloud_platform_manager_ip

    request_body = config_json
    LOGGER.info("----Configure and deploy a new APEX Azure cluster----")
    installation_request_id = deployment_utility.start_cluster_deployment(request_body)
    LOGGER.info('Cluster deployment task ID: %s.', installation_request_id)
    if installation_request_id == "error":
        LOGGER.info("------Cluster deployment task startup failed-----")
        module.fail_json(
            msg=f"Cluster deployment task startup failed. Please see the {log_file_name} for more details")
    installation_status = deployment_utility.check_cluster_deployment_status()
    if installation_status == 'COMPLETED':
        LOGGER.info("-----Cluster deployment completed-----")
        cluster_deployment_result = {'status': installation_status, 'request_id': installation_request_id}
        facts_result = dict(changed=True, cluster_deployment_result=cluster_deployment_result,
                            msg=f"Cluster deployment is successful. Please see the {log_file_name} for more details")
        module.exit_json(**facts_result)
    else:
        LOGGER.info("------Cluster deployment failed-----")
        cluster_deployment_result = {'request_id': installation_request_id}
        facts_result = dict(failed=True, cluster_deployment_result=cluster_deployment_result,
                               msg=f'Cluster deployment has failed. Please see the {log_file_name} for more details')
        module.exit_json(**facts_result)


if __name__ == '__main__':
    main()
