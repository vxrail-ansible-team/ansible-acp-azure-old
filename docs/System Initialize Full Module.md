System Initialize Full Module for APEX Cloud Platform Azure
=================
### Product Guide

> © 2023 Dell Inc. or its subsidiaries. All rights reserved. Dell 
> EMC, and other trademarks are trademarks of Dell Inc. or its 
> subsidiaries. Other trademarks may be trademarks of their respective owners. 

Synopsis
--------
This module will perform HCI OS provision to specified nodes, initialize LDAPS certificate and
configure and deploy a new APEX Cloud Platform cluster for Microsoft Azure based on the provided day1 json file.
  
Supported Endpoints
--------

* POST /ldaps-certs/initialize
* POST /system/initialize
* GET /system/initialize/status 

Parameters
----------

<table  border=0 cellpadding=0 class="documentation-table">
    <tr>
        <th colspan="1">Parameter</th>
        <th>Choices/<font color="blue">Defaults</font></th>
                    <th width="100%">Comments</th>
    </tr>
    <tr>
        <td colspan="1">
            <div class="ansibleOptionAnchor" id="parameter-primary-node-ip"></div>
            <b>primary_host_ip</b>
            <a class="ansibleOptionLink" href="#parameter-primary-node-ip" title="Permalink to this option"></a>
            <div style="font-size: small">
                <span style="color: purple">type=string</span>
                <br>
                <span style="color: red">required=true</span>
            </div>
        </td>
        <td></td>
        <td>
            <div></div>
            <div>The primary node IP</div>
        </td>
    </tr>
    <tr>
        <td colspan="1">
            <div class="ansibleOptionAnchor" id="parameter-cloud-platform-manager-ip"></div>
            <b>cloud_platform_manager_ip</b>
            <a class="ansibleOptionLink" href="#parameter-cloud-platform-manager-ip" title="Permalink to this option"></a>
            <div style="font-size: small">
                <span style="color: purple">type=string</span>
                <br>
                <span style="color: red">required=true</span>                    
            </div>
        </td>
        <td></td>
        <td>
            <div></div>
            <div>The ip address of APEX Cloud Platform Manager</div>
        </td>
    </tr>
    <tr>
        <td colspan="1">
            <div class="ansibleOptionAnchor" id="parameter-ldaps-cert-file"></div>
            <b>ldaps_cert_file</b>
            <a class="ansibleOptionLink" href="#parameter-ldaps-cert-file" title="Permalink to this option"></a>
            <div style="font-size: small">
                <span style="color: purple">type=string</span>
                <br>
                <span style="color: red">required=true</span>
            </div>
        </td>
        <td></td>
        <td>
            <div></div>
            <div>The path of LDAPs certificate file</div>
        </td>
    </tr>
    <tr>
        <td colspan="1">
            <div class="ansibleOptionAnchor" id="parameter-ldaps-cert-file"></div>
            <b>ldaps_cert_file</b>
            <a class="ansibleOptionLink" href="#parameter-ldaps-cert-file" title="Permalink to this option"></a>
            <div style="font-size: small">
                <span style="color: purple">type=string</span>
                <br>
                <span style="color: red">required=true</span>
            </div>
        </td>
        <td></td>
        <td>
            <div></div>
            <div>The path of LDAPs certificate file</div>
        </td>
    </tr>
    <tr>
        <td colspan="1">
            <div class="ansibleOptionAnchor" id="parameter-day1-json-file"></div>
            <b>day1_json_file</b>
            <a class="ansibleOptionLink" href="#parameter-day1-json-file" title="Permalink to this option"></a>
            <div style="font-size: small">
                <span style="color: purple">type=string</span>
                <br>
                <span style="color: red">required=true</span>                    
            </div>
        </td>
        <td></td>
        <td>
            <div></div>
            <div>The path of day1 json file</div>
        </td>
    </tr>
    <tr>
        <td colspan="1">
            <div class="ansibleOptionAnchor" id="parameter-state"></div>
            <b>timeout</b>
            <a class="ansibleOptionLink" href="#parameter-state" title="Permalink to this option"></a>
            <div style="font-size: small">
                <span style="color: purple">type=integer</span>
                <br>
                <span style="color: red"></span>                    
            </div>
        </td>
        <td>
            <ul style="margin: 0; padding: 0"><b>Default:</b>
                <li>36000s</li>
            </ul>
        </td>
        <td>
            <div>Time out value for performing cluster deployment, the default value is 36000 seconds</div>
            <div>It does not include the cost of OS provision.</div>
        </td>
    </tr>
</table>

Notes
-----
- Make sure your APEX Cloud Platform Azure environment supports the API that you use
- Please check "Chapter 4:Prerequisites" of "Deployment Guide" to prepare system prerequisites before perform module
- Details on execution of module apexcp_azure_system_initialize_full.py can be checked in the logs /tmp/apexcp_azure_system_initialize_full.log

Examples
--------

``` yaml+jinja
- name: Perform full system initialization for APEX Cloud Platform Azure
  dell_apexcp_azure_system_initialize_full
    primary_host_ip: "{{ primary_host_ip }}"
    cloud_platform_manager_ip: "{{ cloud_platform_manager_ip }}"
    ldaps_cert_file: "{{ ldaps_cert_file }}"
    day1_json_file: "{{ day1_json_file }}"
```

Return Values
-------------

The following are the fields unique to this module:

<table border=0 cellpadding=0 class="documentation-table">
    <tr>
        <th colspan="2">Key</th>
        <th>Returned</th>
        <th width="100%">Description</th>
    </tr>
    <tr>
        <td colspan="2">
            <div class="ansibleOptionAnchor" id="return-changed"></div>
            <b>changed</b>
            <a class="ansibleOptionLink" href="#return-changed" title="Permalink to this return value"></a>
            <div style="font-size: small">
              <span style="color: purple">type=boolean</span>
            </div>
        </td>
        <td>Always</td>
        <td>
            <div>Whether or not the resource has changed.</div><br/>
        </td>
    </tr>
    <tr>
        <td colspan="2">
            <div class="ansibleOptionAnchor" id="return-os_provision_result"></div>
            <b>os_provision_result</b>
            <a class="ansibleOptionLink" href="#return-os_provision_result" title="Permalink to this return value"></a>
            <div style="font-size: small"><span style="color: purple">type=dict</span></div>
        </td>
        <td>When calling the /system/initialize?mode=OS_PROVISION API is successful</td>
        <td><div></div><br/></td>
    </tr>
    <tr>
        <td class="elbow-placeholder">&nbsp;</td>
        <td colspan="1">
            <div class="ansibleOptionAnchor" id="return-install-status/request-id"></div>
            <b>request_id</b>
            <a class="ansibleOptionLink" href="#return-install-status/request-id" title="Permalink to this return value"></a>
            <div style="font-size: small"><span style="color: purple">type=string</span></div>
        </td>
        <td></td>
        <td>
            <div>The request id of OS provision.</div>
        </td>
    </tr>
    <tr>
        <td class="elbow-placeholder">&nbsp;</td>
        <td colspan="1">
            <div class="ansibleOptionAnchor" id="return-install-status/status"></div>
            <b>status</b>
            <a class="ansibleOptionLink" href="#return-install-status/status" title="Permalink to this return value"></a>
            <div style="font-size: small"><span style="color: purple">type=string</span></div>
        </td>
        <td></td>
        <td><div>The OS provision result.</div></td>
    </tr>
    <tr>
        <td class="elbow-placeholder">&nbsp;</td>
        <td colspan="1">
            <div class="ansibleOptionAnchor" id="return-install-status/detail"></div>
            <b>install_detail</b>
            <a class="ansibleOptionLink" href="#return-install-status/detail" title="Permalink to this return value"></a>
            <div style="font-size: small"><span style="color: purple">type=dict</span></div>
        </td>
        <td></td>
        <td><div>The OS provision detail.</div></td>
    </tr> 
    <tr>
        <td colspan="2">
            <div class="ansibleOptionAnchor" id="return-initialize_cert_result"></div>
            <b>initialize_cert_result</b>
            <a class="ansibleOptionLink" href="#return-initialize_cert_result" title="Permalink to this return value"></a>
            <div style="font-size: small"><span style="color: purple">type=dict</span></div>
        </td>
        <td>When LDAPS certificate initialization is successful</td>
        <td><div>LDAPS certificate initialization result</div><br/></td>
    </tr>
    <tr>
        <td colspan="2">
            <div class="ansibleOptionAnchor" id="return-cluster_deployment_result"></div>
            <b>cluster_deployment_result</b>
            <a class="ansibleOptionLink" href="#return-cluster_deployment_result" title="Permalink to this return value"></a>
            <div style="font-size: small"><span style="color: purple">type=dict</span></div>
        </td>
        <td>When calling the /system/initialize?mode=CLUSTER_DEPLOYMENT API is successful</td>
        <td><div></div><br/></td>
    </tr>
    <tr>
        <td class="elbow-placeholder">&nbsp;</td>
        <td colspan="1">
            <div class="ansibleOptionAnchor" id="return-install-status/request-id"></div>
            <b>request_id</b>
            <a class="ansibleOptionLink" href="#return-install-status/request-id" title="Permalink to this return value"></a>
            <div style="font-size: small"><span style="color: purple">type=string</span></div>
        </td>
        <td></td>
        <td>
            <div>The request id of cluster deployment.</div>
        </td>
    </tr>
    <tr>
        <td class="elbow-placeholder">&nbsp;</td>
        <td colspan="1">
            <div class="ansibleOptionAnchor" id="return-install-status/status"></div>
            <b>status</b>
            <a class="ansibleOptionLink" href="#return-install-status/status" title="Permalink to this return value"></a>
            <div style="font-size: small"><span style="color: purple">type=string</span></div>
        </td>
        <td></td>
        <td><div>The cluster deployment result.</div></td>
    </tr>
    <tr>
        <td colspan="2">
            <div class="ansibleOptionAnchor" id="return-msg"></div>
            <b>msg</b>
            <a class="ansibleOptionLink" href="#return-msg" title="Permalink to this return value"></a>
            <div style="font-size: small"><span style="color: purple">type=string</span></div>
        </td>
        <td>Always</td>
        <td><div>The message for full system initialization</div></td>
    </tr>
</table>

Authors
-------

-   Dell APEX Cloud Platform for Microsoft Azure Ansible Development Team &lt;<ansible.team@dell.com>&gt;