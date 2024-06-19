# Copyright (c) 2023 Dell Inc. or its subsidiaries. All Rights Reserved.
#
# This software contains the intellectual property of Dell Inc. or is licensed to Dell Inc. from third parties.
# Use of this software and the intellectual property contained therein is expressly limited to the terms and
# conditions of the License Agreement under which it is provided by or on
# behalf of Dell Inc. or its subsidiaries.

import json
import time

import mcp_ansible_utility_az
import urllib3
from mcp_ansible_utility_az.rest import ApiException

from . import dell_apexcp_azure_ansible_utils as utils

CHECK_STATUS_INTERVAL = 60
MAX_ERROR_COUNT = 10
TIMEOUT_OS_PROVISION = 7200
MAX_ERROR_COUNT_OS_PROVISION = 90


def create_installation_and_deployment_api(ip):
    return mcp_ansible_utility_az.InstallationAndDeploymentOfAPEXCloudPlatformForMicrosoftAzureApi(
        mcp_ansible_utility_az.ApiClient(OSProvision.create_configuration(ip)))


class ClusterDeployment(utils.BaseModule):

    def __init__(self, module, logger):
        super().__init__(module=module)
        self.day1_json_file = module.params.get('day1_json_file')
        self.new_cloud_platform_manager_ip = None
        self.new_cloud_platform_manager_ip_is_working = False
        self.logger = logger
        self.logger.info(f"{self.cloud_platform_manager_ip},{self.timeout},{self.day1_json_file}")

    def start_cluster_deployment(self, day1_json):
        request_body = day1_json
        # create an instance of the API class
        api_instance = create_installation_and_deployment_api(self.cloud_platform_manager_ip)
        try:
            # start day1 FirstRun(ex:v1_system_initialize_post)
            call_string = self.get_versioned_response(api_instance, 'Post /system/initialize') + '_system_initialize_post'
            self.logger.info("Using utility method: %s\n", call_string)
            api_initialize_post = getattr(api_instance, call_string)
            response = api_initialize_post(request_body, mode="CLUSTER_DEPLOYMENT")
        except ApiException as e:
            self.logger.error("Exception when calling ClusterInitializeApi->v1_system_initialize_post: %s\n", e)
            return 'error'
        job_id = response.request_id
        return job_id

    def get_request_status(self):
        # create an instance of the API class
        api_instance = create_installation_and_deployment_api(self.cloud_platform_manager_ip)
        if self.new_cloud_platform_manager_ip:
            new_api_instance = create_installation_and_deployment_api(self.new_cloud_platform_manager_ip)

        # get day1 FirstRun status(ex:v1_system_initialize_status_get)
        call_string = self.get_versioned_response(api_instance,
                                                  '/system/initialize/status') + '_system_initialize_status_get'
        try:
            if self.new_cloud_platform_manager_ip_is_working:
                api_system_initialize_status_get = getattr(new_api_instance, call_string)
            else:
                api_system_initialize_status_get = getattr(api_instance, call_string)
            return api_system_initialize_status_get(mode="CLUSTER_DEPLOYMENT")
        except Exception as e:
            self.logger.error("Exception when calling v1_system_initialize_status_get: %s\n", e)
            if not self.new_cloud_platform_manager_ip_is_working and self.new_cloud_platform_manager_ip:
                try:
                    api_system_initialize_status_get = getattr(new_api_instance, call_string)
                    response = api_system_initialize_status_get()
                    self.new_cloud_platform_manager_ip_is_working = True
                    return response
                except Exception:
                    self.logger.error("Get initialization status via %s failed: %s\n", self.new_cloud_platform_manager_ip, e)
            return None

    def check_cluster_deployment_status(self):
        time_out = 0
        error_count = 0
        installation_status = ""
        installation_response = None
        initial_timeout = self.timeout
        last_install_response = None
        while installation_status not in (
                'COMPLETED', 'FAILED') and time_out < initial_timeout and error_count < MAX_ERROR_COUNT:
            installation_response = self.get_request_status()
            if installation_response:
                error_count = 0
                installation_status = installation_response.state
                last_install_response = installation_response
                self.logger.info('Cluster deployment task status: %s.', installation_status)
            else:
                error_count += 1
                self.logger.info('Fail to get cluster deployment status. Count: %s', error_count)

            time.sleep(CHECK_STATUS_INTERVAL)
            time_out = time_out + CHECK_STATUS_INTERVAL
        if last_install_response:
            self.logger.info('The cluster deployment result -> %s.', installation_response)
        if error_count >= MAX_ERROR_COUNT:
            self.logger.info("Exceeded the max count of failed to check the cluster deployment status ")
        if time_out >= initial_timeout:
            self.logger.info("Cluster deployment timeout")
        if installation_status == "COMPLETED":
            self.logger.info("Cluster deployment is successful")
        else:
            self.logger.info("Cluster deployment failed")
        return installation_status


class OSProvision(utils.BaseModule):

    def __init__(self, module, logger, timeout=None):
        super().__init__(module=module)
        self.day1_json_file = module.params.get('day1_json_file')
        self.primary_host_ip = module.params.get('primary_host_ip')
        self.primary_node_installed = False
        self.cloud_manager_is_up = False
        if timeout:
            self.timeout = timeout
        self.logger = logger
        self.logger.info(
            f"{self.primary_host_ip},{self.cloud_platform_manager_ip},{self.timeout},{self.day1_json_file}")

    @staticmethod
    def create_installation_and_deployment_api(ip):
        return mcp_ansible_utility_az.InstallationAndDeploymentOfAPEXCloudPlatformForMicrosoftAzureApi(
            mcp_ansible_utility_az.ApiClient(OSProvision.create_configuration(ip)))

    def start_os_provision(self, install_json):
        # create an instance of the API class
        api_instance = OSProvision.create_installation_and_deployment_api(self.primary_host_ip)
        try:
            # start os provision
            call_string = self.get_versioned_response(api_instance,
                                                      'Post /system/initialize') + '_system_initialize_post'
            self.logger.info("Using utility method: %s\n", call_string)
            api_initialize_post = getattr(api_instance, call_string)
            response = api_initialize_post(install_json, mode="OS_PROVISION")
            job_id = response.request_id
            return job_id
        except Exception as e:
            self.logger.error("Call os provision API failed", e)
            return 'error'

    def get_request_status(self):
        # create an instance of the API class
        api_instance_for_primary_host = create_installation_and_deployment_api(self.primary_host_ip)
        # get GI install status(ex:v1_system_initialize_status_get)
        call_string = self.get_versioned_response(api_instance_for_primary_host,
                                                  '/system/initialize/status') + '_system_initialize_status_get'
        try:
            if not self.primary_node_installed:
                api_system_initialize_status_get = getattr(api_instance_for_primary_host, call_string)
                response = api_system_initialize_status_get(mode="OS_PROVISION", _request_timeout=(3, 60))
                return response
        except Exception as e:
            self.logger.error("Exception when calling v1_system_initialize_status_get: %s\n", e.__str__())
            if type(e) == urllib3.exceptions.MaxRetryError:
                self.primary_node_installed = True
                self.logger.info("The HCI OS has been installed into primary node.")
        return None

    def get_request_status_from_cloud_manager(self):
        api_instance_for_cloud_manager = create_installation_and_deployment_api(self.cloud_platform_manager_ip)
        # get GI install status(ex:v1_system_initialize_status_get)
        call_string = self.get_versioned_response(api_instance_for_cloud_manager,
                                                  '/system/initialize/status') + '_system_initialize_status_get'
        try:
            if not self.primary_node_installed:
                return None
            api_system_initialize_status_get = getattr(api_instance_for_cloud_manager, call_string)
            response = api_system_initialize_status_get(mode="OS_PROVISION", _request_timeout=(3, 60))
            if not self.cloud_manager_is_up:
                self.logger.info("Cloud manager is up.")
                self.cloud_manager_is_up = True
            return response
        except Exception as e:
            self.logger.error("Exception when calling v1_system_initialize_status_get: %s\n", e)
        return None

    def check_os_provision_status(self):
        error_count = 0
        os_provision_status = ""
        time_out = 0
        installation_response = None
        last_os_provision_response = None
        while os_provision_status not in (
                'COMPLETED', 'FAILED') and time_out < TIMEOUT_OS_PROVISION and error_count < MAX_ERROR_COUNT_OS_PROVISION:
            if not self.primary_node_installed:
                installation_response = self.get_request_status()
            else:
                installation_response = self.get_request_status_from_cloud_manager()
            if installation_response:
                error_count = 0
                os_provision_status = installation_response.state
                last_os_provision_response = installation_response
                self.logger.info('OS provision task status: %s.', os_provision_status)
            else:
                if self.primary_node_installed:
                    self.logger.info(f"Waiting for APEX cloud manager host up(error count:{error_count})")
                error_count += 1

            time.sleep(CHECK_STATUS_INTERVAL)
            time_out = time_out + CHECK_STATUS_INTERVAL
        install_detail = None
        if installation_response and installation_response.detail:
            detail = installation_response.detail
            install_detail = json.loads(detail)
        if last_os_provision_response:
            self.logger.info(f"The last os provision response:{last_os_provision_response}")
        return os_provision_status, install_detail
