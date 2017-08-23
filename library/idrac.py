#!/usr/bin/env python
# -*- coding: utf-8 -*-

# (c) 2017, Dell EMC Inc.
#
# This file is part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.
#

DOCUMENTATION = '''
---
module: idrac
author: "jose.delarosa@dell.com"
short_description: Manage Dell PowerEdge Servers through iDRAC Redfish APIs
requirements: [ ]
description: Manage Dell PowerEdge servers BIOS, NIC, PERC, iDRAC

options:
    subsystem:
        required: true
        default: None
        choices: [ system, chassis, event, session, manager, jobs, FW ]
        description:
            - sub modules in Redfish Service Root
    cmd:
        required: true
        default: None
        description:
            - sub module command is going to execute 
    idracip:
        required: true
        default: None
        description:
          - iDRAC IP address
    idracuser:
        required: true
        default: root
        description:
          - iDRAC user name
    idracpswd:
        required: true
        default: calvin
        description:
          - iDRAC user password
          
    eth_interface:
        required: False
        default: None
        description:
          - Ethernet interface name i.e NIC.Slot.2-1-1 or NIC.Integrated.1-2-1
          
    storage_controller:
        required: False
        default: None
        description:
          - storage controller name i.e.  RAID.Slot.1-1 or  AHCI.Embedded.1-1
          
    ResetType:
        required: False
        default: None
        choices: ["On", "ForceOff", "GracefulRestart", "GracefulShutdown", "PushPowerButton", "Nmi"]
        description:
          - reset system based on type
    OneTimeBoot:
        required: False
        default: None
        choices=["None","Pxe","Floppy","Cd","Hdd","BiosSetup","Utilities","UefiTarget","SDCard","UefiHttp"])
        description:
          - system set to onetime boot from sources
    FAN:
        required: False
        default: None
        description:
            - This is fan name in chassis i.e Fan.Embedded.A1, Fan.Embedded.A2 etc
    CPU:
        required: False
        default: None
        description:
            - This is CPU socket name in chassis i.e CPU1, CPU2 etc 
    
'''
ANSIBLE_METADATA = {'status': ['preview'],
                    'supported_by': 'community',
                    'version': '0.1'}
import requests
import os
import json
from ansible.module_utils.basic import AnsibleModule
from requests.packages.urllib3.exceptions import InsecureRequestWarning

class iDRAC(object):
    def __init__(self, module):
        self.module = module
        root_uri = ''.join(["https://%s" % module.params['idracip'] , "/redfish/v1"])
        self.system_uri = root_uri + "/Systems/System.Embedded.1"
        self.chassis_uri = root_uri + "/Chassis/System.Embedded.1"
        self.manager_uri = root_uri + "/Managers/iDRAC.Embedded.1"
        self.eventsvc_uri = root_uri + "/EventService"
        self.session_uri = root_uri + "/Sessions"
        self.tasksvc_uri = root_uri + "/TaskService"
        self.updatesvc_uri = root_uri + "/UpdateService"
        
    def send_get_request(self, uri):
        try:
            response = requests.get(uri, verify=False, auth=(self.module.params['idracuser'], self.module.params['idracpswd']))
            
        except:
            pass
        return response.json()
    
    def send_post_request(self,uri, pyld, hdrs):
        try:
            response = requests.post(uri, data=json.dumps(pyld), headers=hdrs,verify=False, auth=(self.module.params['idracuser'], self.module.params['idracpswd']))
        except:
            raise   
        
        return str(response.status_code)
    
    def send_patch_request(self,uri, pyld, hdrs):
        try:
            response = requests.patch(uri, data=json.dumps(pyld), headers=hdrs,verify=False, auth=(self.module.params['idracuser'], self.module.params['idracpswd']))
        except:
            raise   
        
        return str(response.status_code)
    def get_system_health(self):
        resp = self.send_get_request(self.system_uri)
        return str(resp[u'Status'][u'Health'])
    
    def get_system_serial_number(self):
        resp = self.send_get_request(self.system_uri)
        return str(resp[u'SerialNumber'])
    
    def get_system_service_tag(self):
        resp = self.send_get_request(self.system_uri)
        return str(resp[u'SKU'])
    
    def get_server_part_number(self):
        resp = self.send_get_request(self.system_uri)
        return str(resp[u'PartNumber'])
    
    def get_system_Manufacturer(self):
        resp = self.send_get_request(self.system_uri)
        return str(resp[u'Manufacturer'])
    
    def get_system_bios_version(self):
        resp = self.send_get_request(self.system_uri)
        return str(resp[u'BiosVersion'])
    
    def get_system_type(self):
        resp = self.send_get_request(self.system_uri)
        return str(resp[u'SystemType'])
    
    def get_system_power_state(self):
        resp = self.send_get_request(self.system_uri)
        return str(resp[u'PowerState'])
    
    def get_system_memory_health(self):
        resp = self.send_get_request(self.system_uri)
        return str(resp[u'MemorySummary'][u'Status'][u'Health'])
    
    def get_system_memory_in_GB(self):
        resp = self.send_get_request(self.system_uri)
        return str(resp[u'MemorySummary'][u'TotalSystemMemoryGiB'])
    
    def get_processor_count(self):
        resp = self.send_get_request(self.system_uri)
        return str(resp[u'ProcessorSummary'][u'Count'])
    
    def get_processor_health(self):
        resp = self.send_get_request(self.system_uri)
        return str(resp[u'ProcessorSummary'][u'Status'][u'Health'])
    
    def get_processor_model(self):
        resp = self.send_get_request(self.system_uri)
        return str(resp[u'ProcessorSummary'][u'Model'])
    
    def get_boot_sources(self):
        sources = []
        resp = self.send_get_request(self.system_uri + u'/BootSources')
        if u'UefiBootSeq' in resp[u'Attributes']:
                for i in resp[u'Attributes'][u'UefiBootSeq']:
                        sources.append(i[u'Name'])
        return ",".join(str(x) for x in sources)
        
    def get_system_ethernet_interfaces(self):
        eth = []
        resp = self.send_get_request(self.system_uri + u'/EthernetInterfaces')
        for i in resp[u'Members']:
            eth.append(os.path.basename(i[u'@odata.id']))
        return json.dumps(eth)

    def get_system_ethernet_permanent_MAC_address(self):
        resp = self.send_get_request(self.system_uri + u'/EthernetInterfaces/%s' % self.module.params[u'eth_interface'])
        return resp[u'PermanentMACAddress']
    
    def get_system_secure_boot_status(self):
        resp = self.send_get_request(self.system_uri + u'/SecureBoot')
        return resp[u'SecureBootCurrentBoot']
    
    def get_system_secure_boot_certificates(self):
        cert = []
        resp = self.send_get_request(self.system_uri + u'/SecureBoot/Certificates')
        for i in resp[u'Members']:
            cert.append(os.path.basename(i[u'@odata.id']))
        return ",".join(str(x) for x in cert)
    def get_system_cpus(self):
        cpus=[]
        resp = self.send_get_request(self.system_uri+u'/Processors')
        if not 'error' in resp.keys():
            for i in resp[u'Members']:
                cpus.append("CPU%s"%(os.path.basename(i[u'@odata.id']).split('.')[2]))
            return (json.dumps(cpus),None)
        return (None,resp['error']['@Message.ExtendedInfo'][0]['Message'])
            
    def get_system_storage_controllers(self):
        ctrls = []
        resp = self.send_get_request(self.system_uri + u'/Storage/Controllers')
        for i in resp[u'Members']:
            ctrls.append(os.path.basename(i[u'@odata.id']))
        return json.dumps(ctrls)
        
        
    def get_system_storage_controller_disks(self):
        resp = self.send_get_request(self.system_uri + u'/Storage/Controllers/%s' % self.module.params[u'storage_controller'])
        if len(resp[u'Devices']) > 1:
            return json.dumps(resp[u'Devices'])
        else:
            return json.dumps([])
    def system_reset(self):
        payload = {'ResetType': self.module.params[u'ResetType']}
        headers = {'content-type': 'application/json'}
        return self.send_post_request(self.system_uri+u'/Actions/ComputerSystem.Reset',payload,headers )
    def system_onetime(self):
        payload = {'Boot': {'BootSourceOverrideTarget' : self.module.params[u'Target']}}
        headers = {'content-type': 'application/json'}
        return self.send_patch_request(self.system_uri,payload,headers )
    
    # Redfish Chassis API
    
    def get_chassis_health(self):
        resp = self.send_get_request(self.chassis_uri)
        if not 'error' in resp.keys():
            return (str(resp[u'Status'][u'Health']),None)
        else:
            return (None,resp['error']['@Message.ExtendedInfo'][0]['Message'])
        
    def get_chassis_indicator_LED_status(self):
        resp = self.send_get_request(self.chassis_uri)
        if not 'error' in resp.keys():
            return (str(resp[u'IndicatorLED']),None)
        else:
            return (None,resp['error']['@Message.ExtendedInfo'][0]['Message'])
        
    
    def get_chassis_type(self):
        resp = self.send_get_request(self.chassis_uri)
        if not 'error' in resp.keys():
            return (str(resp[u'ChassisType']),None)
        else:
            return (None,resp['error']['@Message.ExtendedInfo'][0]['Message'])
        
        return str(resp[u'ChassisType'])
    
    def get_chassis_reset_options(self):
        resp = self.send_get_request(self.chassis_uri)
        if not 'error' in resp.keys():
            return (str(resp[u'Actions'][u'#Chassis.Reset'][u'ResetType@Redfish.AllowableValues']),None)
        else:
            return (None,resp['error']['@Message.ExtendedInfo'][0]['Message'])
        
    def get_chassis_fans(self):
        fan=[]
        resp = self.send_get_request(self.chassis_uri)
        for i in resp[u'Links'][u'CooledBy']:
            fan.append(os.path.basename(i[u'@odata.id']).split('||')[1])
        if not 'error' in resp.keys():
            return (json.dumps(fan),None)
        else:
            return (None,resp['error']['@Message.ExtendedInfo'][0]['Message'])
    
    def get_chassis_fan_health(self):
        resp = self.send_get_request(self.chassis_uri)
        if not 'error' in resp.keys():
            return (str(resp[u'Status'][u'Health']),None)
        else:
            return (None,resp['error']['@Message.ExtendedInfo'][0]['Message'])
        
    
    def get_chassis_fan_reading(self):
        pass
    def get_chassis_powered_by(self):
        PSU=[]
        resp = self.send_get_request(self.chassis_uri)
        for i in resp[u'Links'][u'PoweredBy']:
            PSU.append(os.path.basename(i[u'@odata.id']))
        if not 'error' in resp.keys():
            return (json.dumps(PSU),None)
        else:
            return (None,resp['error']['@Message.ExtendedInfo'][0]['Message'])
        
    
    def get_chassis_part_number(self):
        resp = self.send_get_request(self.chassis_uri)
        if not 'error' in resp.keys():
            return (str(resp[u'PartNumber']),None)
        else:
            return (None,resp['error']['@Message.ExtendedInfo'][0]['Message'])
        
    
    def get_chassis_model(self):
        resp = self.send_get_request(self.chassis_uri)
        if not 'error' in resp.keys():
            return (str(resp[u'Model']),None)
        else:
            return (None,resp['error']['@Message.ExtendedInfo'][0]['Message'])
        
    
    def get_chassis_manufacturer(self):
        resp = self.send_get_request(self.chassis_uri)
        if not 'error' in resp.keys():
            return (str(resp[u'Manufacturer']),None)
        else:
            return (None,resp['error']['@Message.ExtendedInfo'][0]['Message'])
        
    
    def get_chassis_power_state(self):
        resp = self.send_get_request(self.chassis_uri)
        if not 'error' in resp.keys():
            return (str(resp[u'PowerState']),None)
        else:
            return (None,resp['error']['@Message.ExtendedInfo'][0]['Message'])
        
    
    def get_chassis_serial_number(self):
        resp = self.send_get_request(self.chassis_uri)
        if not 'error' in resp.keys():
            return (str(resp[u'SerialNumber']),None)
        else:
            return (None,resp['error']['@Message.ExtendedInfo'][0]['Message'])
        
    
    def get_chassis_SKU(self):
        resp = self.send_get_request(self.chassis_uri)
        if not 'error' in resp.keys():
            return (str(resp[u'SKU']),None)
        else:
            return (None,resp['error']['@Message.ExtendedInfo'][0]['Message'])
        
    
    def get_chassis_board_inlet_Temp(self):
        resp = self.send_get_request(self.chassis_uri+u'/Sensors/Temperatures/iDRAC.Embedded.1%23SystemBoardInletTemp')
        if not 'error' in resp.keys():
            return (str(resp[u'ReadingCelsius']),None)
        else:
            return (None,resp['error']['@Message.ExtendedInfo'][0]['Message'])

    
    def get_chassis_board_exhaust_temp(self):
        resp = self.send_get_request(self.chassis_uri+u'/Sensors/Temperatures/iDRAC.Embedded.1%23SystemBoardExhaustTemp')
        if not 'error' in resp.keys():
            return (str(resp[u'ReadingCelsius']),None)
        else:
            return (None,resp['error']['@Message.ExtendedInfo'][0]['Message'])

    def get_chassis_cpu_temp(self):
        resp = self.send_get_request(self.chassis_uri + u'/Sensors/Temperatures/iDRAC.Embedded.1%%23%sTemp' % self.module.params[u'CPU'])
        if not 'error' in resp.keys():
            return (str(resp[u'ReadingCelsius']),None)
        
        return (None,resp['error']['@Message.ExtendedInfo'][0]['Message'])
    
    def get_chassis_power_consumed_watts(self):
        resp = self.send_get_request(self.chassis_uri+'/Power/PowerControl')
        if not 'error' in resp.keys():
            return (str(resp[u'PowerConsumedWatts']),None)
        return (None,resp['error']['@Message.ExtendedInfo'][0]['Message'])
    
    def get_chassis_fan_rpm(self):
        resp = self.send_get_request(self.chassis_uri + u'/Sensors/Fans/0x17||%s' % self.module.params[u'FAN'])
        if not 'error' in resp.keys():
            return (str(resp[u'Reading']),None)
        
        return (None,resp['error']['@Message.ExtendedInfo'][0]['Message'])
    
        
    # iDRAC manager API
    def get_manager_health(self):
        resp = self.send_get_request(self.manager_uri)
        return str(resp[u'"Status"'][u'Health'])
    
    def get_manager_reset_options(self):
        resp = self.send_get_request(self.manager_uri)
        return str(resp[u'Actions'][u'#Manager.Reset'][u'ResetType@Redfish.AllowableValues'])
    
    def get_manager_command_shells(self):
        resp = self.send_get_request(self.manager_uri)
        return str(resp[u'CommandShell'][u'ConnectTypesSupported'])
    
    def get_manager_ethernet_interfaces(self):
        eth = []
        resp = self.send_get_request(self.manager_uri + u'/EthernetInterfaces')
        for i in resp[u'Members']:
            eth.append(os.path.basename(i[u'@odata.id']))
        return ",".join(str(x) for x in eth)
    
    def get_manager_firmware(self):
        resp = self.send_get_request(self.manager_uri)
        return str(resp[u'FirmwareVersion'])
    
    def get_manager_graphical_console(self):
        resp = self.send_get_request(self.manager_uri)
        return str(resp[u'GraphicalConsole'][u'ConnectTypesSupported'])
    
    def get_manager_sel_log(self):
        resp = self.send_get_request(self.manager_uri + u'/Logs/Sel')
        return str(resp[u'Members'])
        
    
    def get_manager_lc_log(self):
        resp = self.send_get_request(self.manager_uri + u'/Logs/Lclog')
        return str(resp[u'Members'])
    
    def get_manager_jobs(self):
        jobs = []
        resp = self.send_get_request(self.manager_uri + u'/Jobs')
        for i in resp[u'Members']:
            jobs.append(os.path.basename(i[u'@odata.id']))
        return ",".join(str(x) for x in jobs)

    def get_manager_host_name(self):
        resp = self.send_get_request(self.manager_uri + u'/NetworkProtocol')
        return str(resp[u'HostName'])
    
    def manager_reset(self):
        payload = {u'ResetType': u"%s"%(self.module.params[u'ResetType'])}
        headers = {u'content-type': u'application/json'}
        return self.send_post_request(self.manager_uri+u'/Actions/Manager.Reset',payload,headers )
         
    
    def get_event_type_for_subscription(self):
        resp = self.send_get_request(self.eventsvc_uri)
        return str(resp[u'EventTypesForSubscription'])
    
    def get_event_service_health(self):
        resp = self.send_get_request(self.eventsvc_uri)
        return str(resp[u'Status'][u'Health'])
    
    def get_event_state(self):
        resp = self.send_get_request(self.eventsvc_uri)
        return str(resp[u'Status'][u'State'])
    
    def get_session_id(self):
        mem = []
        resp = self.send_get_request(self.session_uri)
        for i in resp[u'Members']:
            mem.append(os.path.basename(i[u'@odata.id']))
        return ",".join(str(x) for x in mem)
    
    def get_firmware_inventory(self):
        fw = dict()
        resp = self.send_get_request(self.updatesvc_uri + u'/FirmwareInventory')
        for i in resp[u'Members']:
            fw_info = self.send_get_request(self.updatesvc_uri + u'/FirmwareInventory/' + '%s' % os.path.basename(i[u'@odata.id']))
            fw[fw_info[u'Name']] = fw_info[u'Version']
        return json.dumps(fw)
        

    
def main():
    # Parsing argument file
    module = AnsibleModule(
            argument_spec = dict(
                subsystem = dict(required=True, type='str', default=None, choices=['System', 'Manager', 'Session', 'Event', 'Chassis', 'FW']),
                idracip = dict(required=True, type='str', default=None),
                idracuser = dict(required=False, type='str', default='root'),
                idracpswd = dict(required=False, type='str', default='calvin'),
                cmd = dict(required=False, type='str', default=None),
                eth_interface = dict(required=False, type='str', default=None),
                storage_controller = dict(required=False, type='str', default=None),
                ResetType = dict(required=False, type='str', default=None,choices=["On", "ForceOff", "GracefulRestart", "GracefulShutdown", "PushPowerButton", "Nmi"]),
                Target = dict(required=False, type='str', default=None, choices=["None","Pxe","Floppy","Cd","Hdd","BiosSetup","Utilities","UefiTarget","SDCard","UefiHttp"]),
                FAN = dict(required=False, type='str', default=None),
                CPU = dict(required=False, type='str', default=None),
            ),
            supports_check_mode=True
    )
    idrac = iDRAC(module)
    params = module.params
    rc = None
    out = ''
    err = ''
    result = {}

    # Disable insecure-certificate-warning message
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    
    if not 'subsystem' in params.keys():
        module.fail_json(msg="You haven't specified a subsystem name")
        
    if not 'cmd' in params.keys():
        module.fail_json(msg="You haven't specified a subsystem command")
        
    result['subsystem'] = params['subsystem']
    
    if params['subsystem'] == "System":
        if params['cmd'] == 'Health':
            
            out = idrac.get_system_health()
            
        if params['cmd'] == 'SerialNumber':
            out = idrac.get_system_serial_number()
            
        if params['cmd'] == 'ServiceTag':
            out = idrac.get_system_service_tag()
            
        if params['cmd'] == 'AssetTag':
            out = idrac.get_boot_sources()
            
        if params['cmd'] == 'Manufacturer':
            out = idrac.get_system_Manufacturer()
            
        if params['cmd'] == 'BiosVersion':
            out = idrac.get_system_bios_version()
            
        if params['cmd'] == 'SystemType':
            out = idrac.get_system_type()
            
        if params['cmd'] == 'PowerState':
            out = idrac.get_system_power_state()
            
        if params['cmd'] == 'MemoryHealth':
            out = idrac.get_system_memory_health()
            
        if params['cmd'] == 'TotalSystemMemoryGiB':
            out = idrac.get_system_memory_in_GB()
            
        if params['cmd'] == 'ProcessorCount':
            out = idrac.get_processor_count()
            
        if params['cmd'] == 'ProcessorHealth':
            out = idrac.get_processor_health()
            
        if params['cmd'] == 'ProcessorModel':
            out = idrac.get_processor_model()
            
        if params['cmd'] == 'BootSources':
            out = idrac.get_boot_sources()
            
        if params['cmd'] == 'EthernetInterfaces':
            out = idrac.get_system_ethernet_interfaces()
            
        if params['cmd'] == 'PermanentMACAddress':
            out = idrac.get_system_ethernet_permanent_MAC_address()
            
        if params['cmd'] == 'SecureBoot':
            out = idrac.get_system_secure_boot_status()
            
        if params['cmd'] == 'SecureBootCerts':
            out = idrac.get_system_secure_boot_certificates()
            
        if params['cmd'] == 'StorageControllers':
            out = idrac.get_system_storage_controllers()
            
        if params['cmd'] == 'StorageControllerDisks':
            out = idrac.get_system_storage_controller_disks()
        if params['cmd'] == 'CPUs':
            (out,err)=idrac.get_system_cpus()
        if params['cmd'] == 'Reset':
            if params['ResetType'] != None:
                resp=idrac.system_reset()
                if resp == '204':
                    rc=resp
                    out='OK'
                else:
                    err="system reset failed. Error code:%s"%(resp)
            else:
                module.fail_json(msg="Please provide type of reset")
                   
        if params['cmd'] == 'OneTimeBoot':
            if params['Target'] != None:
                resp=idrac.system_onetime()
                if resp == '200':
                    rc=resp
                    out='OK'
                else:
                    err="system OneTimeBoot setting failed. Error code:%s"%(resp)
            else:
                module.fail_json(msg="Please provide Target name for oneTimeBoot")
            
    if params['subsystem'] == "Manager":
        if params['cmd'] == 'Health':
            out = idrac.get_manager_health()
            
        if params['cmd'] == 'ResetOptions':
            out = idrac.get_manager_reset_options()
            
        if params['cmd'] == 'CommandShells':
            out = idrac.get_manager_command_shells()
            
        if params['cmd'] == 'EthernetInterfaces':
            out = idrac.get_manager_ethernet_interfaces()
            
        if params['cmd'] == 'FirmwareVersion':
            out = idrac.get_manager_firmware()
            
        if params['cmd'] == 'GraphicalConsole':
            out = idrac.get_manager_graphical_console()
            
        if params['cmd'] == 'SELLogs':
            out = idrac.get_manager_sel_log()
            
        if params['cmd'] == 'LCLogs':
            out = idrac.get_manager_lc_log()
            
        if params['cmd'] == 'Jobs':
            out = idrac.get_manager_jobs()
        if params['cmd'] == 'Reset':
            if params['ResetType'] != None:
                resp=idrac.manager_reset()
                if resp == '204':
                    rc=resp
                    out='OK'
                else:
                    err="Manager reset failed. Error code:%s"%(resp)
            else:
                module.fail_json(msg="Please provide type of reset")

    if params['subsystem'] == "Chassis":
        if params['cmd'] == 'IndicatorLED':
            (out,err)=idrac.get_chassis_indicator_LED_status()
            
        if params['cmd'] == 'ChassisType':
            (out,err)=idrac.get_chassis_type()
        
        if params['cmd'] == 'ResetTypes':
            (out,err)=idrac.get_chassis_reset_options()
            
        if params['cmd'] == 'CooledBy':
            (out,err)=idrac.get_chassis_fans()
            
        if params['cmd'] == 'Health':
            (out,err)=idrac.get_chassis_health()
        
        if params['cmd'] == 'PoweredBy':
            (out,err)=idrac.get_chassis_powered_by()
        
        if params['cmd'] == 'PartNumber':
            (out,err)=idrac.get_chassis_part_number()
            
        if params['cmd'] == 'Model':
            (out,err)=idrac.get_chassis_model()
            
        if params['cmd'] == 'Manufacturer':
            (out,err)=idrac.get_chassis_manufacturer()
        
        if params['cmd'] == 'PowerState':
            (out,err)=idrac.get_chassis_power_state()
        if params['cmd'] == 'SKU':
            (out,err)=idrac.get_chassis_SKU()
        
        if params['cmd'] == 'BoardInletTemp':
            (out,err)=idrac.get_chassis_board_inlet_Temp()
            
        if params['cmd'] == 'BoardExhaustTemp':
            (out,err)=idrac.get_chassis_board_exhaust_temp()
            
        if params['cmd'] == 'CPUTemp':
            (out,err)=idrac.get_chassis_cpu_temp()
        
        if params['cmd'] == 'PowerConsumedWatts':
            (out,err)=idrac.get_chassis_power_consumed_watts()
        
        if params['cmd'] == 'FANRPM':
            (out,err)=idrac.get_chassis_fan_rpm()
              
    if params['subsystem'] == "Event":
        if params['cmd'] == 'types':
            out = idrac.get_event_type_for_subscription()
            
        if params['cmd'] == 'health':
            out = idrac.get_event_service_health()
            
        if params['cmd'] == 'state':
            out = idrac.get_event_state()
            
    if params['subsystem'] == "Session":
        if params['cmd'] == 'id':
            out = idrac.get_session_id()
            
    if params['subsystem'] == "FW":  
        if params['cmd'] == 'FirmwareInventory':
            out = idrac.get_firmware_inventory()
    if rc is None:
        result['changed'] = False
    else:
        result['changed'] = True
    if out:
        result['stdout'] = out
    if err:
        result['stderr'] = err
        
    module.exit_json(**result)

if __name__ == '__main__':
    main()
    
    
