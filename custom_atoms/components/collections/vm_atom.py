# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _

from pipeline.component_framework.component import Component
from pipeline.conf import settings
from pipeline.core.flow.activity import Service
from ..collections.helper.password_crypt import *
from ..collections.helper.vm_helper.vm_helper import Virtualmachine

__group_name__ = _(u"vmware接口(vmware)")

#创建虚拟机

class CreateVmService(Service):
    __need_schedule__ = False  # 异步轮巡

    def execute(self, data, parent_data):  # 执行函数
        try:
            # is_interface = data.get_one_of_inputs('is_interface')
            host = data.get_one_of_inputs('host')
            account = data.get_one_of_inputs('account')
            password = data.get_one_of_inputs('password')
            dc_moId = data.get_one_of_inputs('dc_moId')
            hc_moId = data.get_one_of_inputs('hc_moId')
            ds_moId = data.get_one_of_inputs('ds_moId')
            vs_moId = data.get_one_of_inputs('vs_moId')
            vs_name = data.get_one_of_inputs('vs_name')
            folder_moId = data.get_one_of_inputs('folder_moId')
            vmtemplate_os = data.get_one_of_inputs('vmtemplate_os')
            vmtemplate_moId = data.get_one_of_inputs('vmtemplate_moId')
            computer_name = data.get_one_of_inputs('computer_name')
            vm_name = data.get_one_of_inputs('vm_name')
            vmtemplate_pwd = data.get_one_of_inputs('vmtemplate_pwd')
            cpu = data.get_one_of_inputs('cpu')
            mem = data.get_one_of_inputs('mem')
            disk_size = data.get_one_of_inputs('disk_size')
            disk_type = data.get_one_of_inputs('disk_type')
            ip = data.get_one_of_inputs('ip')
            mask = data.get_one_of_inputs('mask')
            gateway = data.get_one_of_inputs('gateway')
            dns = data.get_one_of_inputs('dns')

            # if is_interface == 'true':
            #     res, password = aes_decrypt(password)
        # try:
        #     host = '192.168.102.200'
        #     account = 'administrator@vsphere.local'
        #     password = '1qaz@WSX'
        #     dc_moId = 'datacenter-21'
        #     hc_moId = 'domain-c26'
        #     ds_moId = 'datastore-30'
        #     vs_moId = 'network-31'
        #     vs_name = 'VM Network'
        #     folder_moId = 'group-v28'
        #     vmtemplate_os = 'windows8Server64Guest'
        #     vmtemplate_moId = 'vm-47'
        #     computer_name = 'win2012R2_template'
        #     vm_name = 'test-windows2'
        #     vmtemplate_pwd = '1qaz@WSX'
        #     cpu = '1'
        #     mem = '2'
        #     disk_size = '50'
        #     disk_type = 'thin'
        #     ip = '10.10.10.21'
        #     mask = '255.0.0.0'
        #     gateway = '10.10.10.1'
        #     dns = '127.0.0.1'


            vm = Virtualmachine(account, password, host)
            params = {
                "dc_moId": dc_moId,
                "hc_moId": hc_moId,
                "ds_moId": ds_moId,
                "vs_moId": vs_moId,
                "vs_name": vs_name,
                "folder_moId": folder_moId,
                "vmtemplate_os": vmtemplate_os,
                "vmtemplate_moId": vmtemplate_moId,
                "computer_name": computer_name,
                "vm_name": vm_name,
                "vmtemplate_pwd": vmtemplate_pwd,
                "cpu": int(cpu),
                "mem": int(mem),
                "disk": int(disk_size),
                "disk_type": disk_type,
                "ip": ip,
                "mask": mask,
                "gateway": gateway,
                "dns": dns.split(","),
                "vmtemplate_toolstatus": "toolsNotInstalled"
            }
            logger.error(params)
            result = vm.wait_for_vmclone_finish(params)

            if result["result"]:
                vm_moId = result["data"]._moId
                data.set_outputs('result', u"虚拟机ID为:{0}".format(vm_moId))
                data.set_outputs('atom_res', "true")
                data.set_outputs('message', "")
            else:
                data.set_outputs('result', u"创建虚拟机失败")
                data.set_outputs('atom_res', "false")
                data.set_outputs('message', result["data"])
            return True
        except Exception,e:
            data.set_outputs('result', u"创建虚拟机失败")
            data.set_outputs('atom_res', "false")
            data.set_outputs('message', str(e))
            return True

    def schedule(self, data, parent_data, callback_data=None):  # 轮巡函数

        return True

    def outputs_format(self):  # 输出结果
        return [
            self.OutputItem(name=_(u'result'), key='result', type='str'),
            self.OutputItem(name=_(u'执行结果'), key='atom_res', type='str'),
            self.OutputItem(name=_(u'执行信息'), key='message', type='str'),
        ]


class CreateVmComponent(Component):
    name = u'创建vm虚拟机'
    code = 'create_vm'
    bound_service = CreateVmService
    form = settings.STATIC_URL + 'custom_atoms/vmware/create_vm.js'

# 启动虚拟机

class StartVmService(Service):
    __need_schedule__ = False  # 异步轮巡

    def execute(self, data, parent_data):  # 执行函数
        try:
            is_interface = data.get_one_of_inputs('is_interface')
            host = data.get_one_of_inputs('host')
            account = data.get_one_of_inputs('account')
            password = data.get_one_of_inputs('password')
            vm_moId = data.get_one_of_inputs('vm_moId')
            if is_interface == 'true':
                res, password = aes_decrypt(password)

            vm = Virtualmachine(account, password, host)
            task_result = vm.start_vm(vm_moId)
            if task_result["result"]:
                data.set_outputs('result', u"开机成功")
                data.set_outputs('atom_res', "true")
                data.set_outputs('message', "")
            else:
                data.set_outputs('result', u"开启虚拟机失败")
                data.set_outputs('atom_res', "false")
                data.set_outputs('message', task_result["data"])
            return True
        except Exception,e:
            data.set_outputs('result', u"开启虚拟机失败")
            data.set_outputs('atom_res', "false")
            data.set_outputs('message', str(e))
            return True


    def schedule(self, data, parent_data, callback_data=None):  # 轮巡函数

        return True

    def outputs_format(self):  # 输出结果
        return [
            self.OutputItem(name=_(u'result'), key='result', type='str'),
            self.OutputItem(name=_(u'执行结果'), key='atom_res', type='str'),
            self.OutputItem(name=_(u'执行信息'), key='message', type='str'),
        ]


class StartVmComponent(Component):
    name = u'启动vm虚拟机'
    code = 'start_vm'
    bound_service = StartVmService
    form = settings.STATIC_URL + 'custom_atoms/vmware/start_vm.js'


#停止虚拟机

class StopVmService(Service):
    __need_schedule__ = False  # 异步轮巡

    def execute(self, data, parent_data):  # 执行函数
        try:
            is_interface = data.get_one_of_inputs('is_interface')
            host = data.get_one_of_inputs('host')
            account = data.get_one_of_inputs('account')
            password = data.get_one_of_inputs('password')
            vm_moId = data.get_one_of_inputs('vm_moId')
            if is_interface == 'true':
                res, password = aes_decrypt(password)

            vm = Virtualmachine(account, password, host)
            task_result = vm.stop_vm(vm_moId)
            if task_result["result"]:
                data.set_outputs('result', u"关机成功")
                data.set_outputs('atom_res', "true")
                data.set_outputs('message', "")
            else:
                data.set_outputs('result', u"关闭虚拟机失败")
                data.set_outputs('atom_res', "false")
                data.set_outputs('message', task_result["data"])
            return True
        except Exception,e:
            data.set_outputs('result', u"关闭虚拟机失败")
            data.set_outputs('atom_res', "false")
            data.set_outputs('message', str(e))
            return True

    def schedule(self, data, parent_data, callback_data=None):  # 轮巡函数

        return True

    def outputs_format(self):  # 输出结果
        return [
            self.OutputItem(name=_(u'result'), key='result', type='str'),
            self.OutputItem(name=_(u'执行结果'), key='atom_res', type='str'),
            self.OutputItem(name=_(u'执行信息'), key='message', type='str'),
        ]


class StopVmComponent(Component):
    name = u'关闭vm虚拟机'
    code = 'stop_vm'
    bound_service = StopVmService
    form = settings.STATIC_URL + 'custom_atoms/vmware/stop_vm.js'

#重启虚拟机

class RestartVmService(Service):
    __need_schedule__ = False  # 异步轮巡

    def execute(self, data, parent_data):  # 执行函数
        try:
            is_interface = data.get_one_of_inputs('is_interface')
            host = data.get_one_of_inputs('host')
            account = data.get_one_of_inputs('account')
            password = data.get_one_of_inputs('password')
            vm_moId = data.get_one_of_inputs('vm_moId')
            if is_interface == 'true':
                res, password = aes_decrypt(password)

            vm = Virtualmachine(account, password, host)
            task_result = vm.restart_vm(vm_moId)
            if task_result["result"]:
                data.set_outputs('result', u"重启成功")
                data.set_outputs('atom_res', "true")
                data.set_outputs('message', "")
            else:
                data.set_outputs('result', u"重启虚拟机失败")
                data.set_outputs('atom_res', "false")
                data.set_outputs('message', task_result['data'])
            return True
        except Exception,e:
            data.set_outputs('result', u"重启虚拟机失败")
            data.set_outputs('atom_res', "false")
            data.set_outputs('message', str(e))
            return True

    def schedule(self, data, parent_data, callback_data=None):  # 轮巡函数

        return True

    def outputs_format(self):  # 输出结果
        return [
            self.OutputItem(name=_(u'result'), key='result', type='str'),
            self.OutputItem(name=_(u'执行结果'), key='atom_res', type='str'),
            self.OutputItem(name=_(u'执行信息'), key='message', type='str'),
        ]


class RestartVmComponent(Component):
    name = u'重启vm虚拟机'
    code = 'restart_vm'
    bound_service = RestartVmService
    form = settings.STATIC_URL + 'custom_atoms/vmware/restart_vm.js'

# 移除虚拟机

class RemoveVmService(Service):
    __need_schedule__ = False  # 异步轮巡

    def execute(self, data, parent_data):  # 执行函数
        try:
            is_interface = data.get_one_of_inputs('is_interface')
            host = data.get_one_of_inputs('host')
            account = data.get_one_of_inputs('account')
            password = data.get_one_of_inputs('password')
            vm_moId = data.get_one_of_inputs('vm_moId')
            if is_interface == 'true':
                res, password = aes_decrypt(password)

            vm = Virtualmachine(account, password, host)
            task_result = vm.delete_vm(vm_moId)
            if task_result["result"]:
                data.set_outputs('result', u"删除成功")
                data.set_outputs('atom_res', "true")
                data.set_outputs('message', "")
            else:
                data.set_outputs('result', u"删除虚拟机失败")
                data.set_outputs('atom_res', "false")
                data.set_outputs('message', task_result["data"])
            return True
        except Exception,e:
            data.set_outputs('result', u"删除虚拟机失败")
            data.set_outputs('atom_res', "false")
            data.set_outputs('message', str(e))
            return True

    def schedule(self, data, parent_data, callback_data=None):  # 轮巡函数

        return True

    def outputs_format(self):  # 输出结果
        return [
            self.OutputItem(name=_(u'result'), key='result', type='str'),
            self.OutputItem(name=_(u'执行结果'), key='atom_res', type='str'),
            self.OutputItem(name=_(u'执行信息'), key='message', type='str'),
        ]


class RemoveVmComponent(Component):
    name = u'删除vm虚拟机'
    code = 'remove_vm'
    bound_service = RemoveVmService
    form = settings.STATIC_URL + 'custom_atoms/vmware/remove_vm.js'

# 重命名虚拟机

class RenameVmService(Service):
    __need_schedule__ = False  # 异步轮巡

    def execute(self, data, parent_data):  # 执行函数
        try:
            is_interface = data.get_one_of_inputs('is_interface')
            host = data.get_one_of_inputs('host')
            account = data.get_one_of_inputs('account')
            password = data.get_one_of_inputs('password')
            vm_moId = data.get_one_of_inputs('vm_moId')
            name = data.get_one_of_inputs('name')
            if is_interface == 'true':
                res, password = aes_decrypt(password)

            vm = Virtualmachine(account, password, host)
            task_result = vm.rename_vm(vm_moId, name)
            if task_result["result"]:
                data.set_outputs('result', u"修改成功")
                data.set_outputs('atom_res', "true")
                data.set_outputs('message', "")
            else:
                data.set_outputs('result', u"修改失败")
                data.set_outputs('atom_res', "false")
                data.set_outputs('message', task_result["data"])
            return True
        except Exception,e:
            data.set_outputs('result', u"修改失败")
            data.set_outputs('atom_res', "false")
            data.set_outputs('message', str(e))
            return True

    def schedule(self, data, parent_data, callback_data=None):  # 轮巡函数

        return True

    def outputs_format(self):  # 输出结果
        return [
            self.OutputItem(name=_(u'result'), key='result', type='str'),
            self.OutputItem(name=_(u'执行结果'), key='atom_res', type='str'),
            self.OutputItem(name=_(u'执行信息'), key='message', type='str'),
        ]


class RenameVmComponent(Component):
    name = u'修改vm虚拟机名称'
    code = 'rename_vm'
    bound_service = RemoveVmService
    form = settings.STATIC_URL + 'custom_atoms/vmware/rename_vm.js'
