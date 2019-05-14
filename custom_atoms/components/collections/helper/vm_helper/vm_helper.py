# -*- coding: UTF-8 -*-
from base import Base
from pyVmomi import vim,vmodl
from pyVim.task import WaitForTask
from common.log import logger
import datetime
import time


class Virtualmachine(Base):

    # 获取虚拟机
    def get_vm_info(self):
        try:
            si = self._connect_vc()
            content = si.RetrieveContent()
            vm_list = content.viewManager.CreateContainerView(content.rootFolder, [vim.VirtualMachine], True).view
            vms_list = []
            for vm in vm_list:
                summary = vm.summary
                hardware = vm.config.hardware
                device = hardware.device
                all_disk_size = 0
                for j in device:
                    if isinstance(j, vim.vm.device.VirtualDisk):
                        all_disk_size += int(j.capacityInKB / 1024 / 1024)
                if summary.config.template == False:
                    device = vm.config.hardware.device
                    ds_list = []
                    for dev in device:
                        if isinstance(dev, vim.vm.device.VirtualDisk):
                            ds_list.append(dev)
                    if summary.runtime.powerState == 'poweredOn':
                        Status = u"运行中"
                    elif summary.runtime.powerState == 'poweredOff':
                        Status = u"已停止"
                    else:
                        Status = u"暂停的"
                    vms_list.append({"resource_id": vm._moId,
                                     "resource_name": vm.name,
                                     "resource_type": "vm",
                                     "moId": vm._moId,
                                     "name": vm.name,
                                     "vm_os": summary.config.guestFullName.decode("utf8"),
                                     "Cpu": hardware.numCPU,
                                     "Memory": hardware.memoryMB / 1024,
                                     "DiskSize": all_disk_size,
                                     "IpAddress": summary.guest.ipAddress,
                                     "Status": Status})
            self._deconnect_vc(si)
            return {"result": True, "data": vms_list}
        except Exception,e:
            logger.exception("get_vm_info")
            return {"result": False, "message": str(e)}


    # 关闭虚拟机
    def stop_vm(self, vm_moId):
        si = self._connect_vc()
        content = si.RetrieveContent()
        try:
            vm = self._get_obj_bymoId(content, [vim.VirtualMachine], vm_moId)
            powerstate = vm.summary.runtime.powerState
            if powerstate == "poweredOn":
                vm.ShutdownGuest()
                return {"result": True}
            else:
                return {"result": False, "data": u"已关机状态的虚拟机无法进行关机操作"}
        except Exception, e:
            error_msg = e.message if e.message else str(e)
            return {"result": False, "data": error_msg}


    # 重启虚拟机
    def restart_vm(self, vm_moId):
        si = self._connect_vc()
        content = si.RetrieveContent()
        try:
            vm = self._get_obj_bymoId(content, [vim.VirtualMachine], vm_moId)
            powerstate = vm.summary.runtime.powerState
            if powerstate == "poweredOn":
                vm.RebootGuest()
                return {"result": True}
            else:
                return {"result": False, "data": u"已关机状态的虚拟机无法进行重启操作"}
        except Exception, e:
            error_msg = e.message if e.message else str(e)
            return {"result": False, "data": error_msg}


    # 开启虚拟机电源
    def start_vm(self, vm_moId):
        si = self._connect_vc()
        content = si.RetrieveContent()
        try:
            vm = self._get_obj_bymoId(content, [vim.VirtualMachine], vm_moId)
            powerstate = vm.summary.runtime.powerState
            if powerstate != "poweredOn":
                task = vm.PowerOn()
                task_result = self._wait_for_task(task)
                return task_result
            else:
                return {"result": False, "data": u"已开机状态的虚拟机无法进行开机操作"}
        except Exception, e:
            error_msg = e.message if e.message else str(e)
            return {"result": False, "data": error_msg}


    # 关闭虚拟机电源
    def poweroff_vm(self, vmargs):
        si = self._connect_vc()
        content = si.RetrieveContent()
        try:
            vm = self._get_obj_bymoId(content, [vim.VirtualMachine], vmargs["vm_moId"])
            task = vm.PowerOff()
            task_result = self._wait_for_task(task)
            return task_result
        except Exception, e:
            error_msg = e.message if e.message else str(e)
            return {"result": False, "data": error_msg}


    # 重置虚拟机
    def reset_vm(self, vmargs):
        si = self._connect_vc()
        content = si.RetrieveContent()
        try:
            vm = self._get_obj_bymoId(content, [vim.VirtualMachine], vmargs["vm_moId"])
            task = vm.Reset()
            task_result = self._wait_for_task(task)
            return task_result
        except Exception, e:
            error_msg = e.message if e.message else str(e)
            return {"result": False, "data": error_msg}


    # 挂起虚拟机
    def suspend_vm(self, vmargs):
        si = self._connect_vc()
        content = si.RetrieveContent()
        try:
            vm = self._get_obj_bymoId(content, [vim.VirtualMachine], vmargs["vm_moId"])
            task = vm.Suspend()
            task_result = self._wait_for_task(task)
            return task_result
        except Exception, e:
            error_msg = e.message if e.message else str(e)
            return {"result": False, "data": error_msg}


    # 删除虚拟机
    def delete_vm(self, vm_moId):
        si = self._connect_vc()
        content = si.RetrieveContent()
        try:
            vm = self._get_obj_bymoId(content, [vim.VirtualMachine], vm_moId)
            task = vm.Destroy()
            task_result = self._wait_for_task(task)
            return task_result
        except Exception, e:
            error_msg = e.message if e.message else str(e)
            return {"result": False, "data": error_msg}


    # 移除虚拟机
    def remove_vm(self, vmargs):
        si = self._connect_vc()
        content = si.RetrieveContent()
        try:
            vm = self._get_obj_bymoId(content, [vim.VirtualMachine], vmargs["vm_moId"])
            vm.UnregisterVM()
            return {"result": True}
        except Exception, e:
            error_msg = e.message if e.message else str(e)
            return {"result": False, "data": error_msg}


    def get_datacenter_info(self):
        try:
            si = self._connect_vc()
            content = si.RetrieveContent()
            container = content.viewManager.CreateContainerView(content.rootFolder, [vim.Datacenter], True)
            dc_data = []
            for i in container.view:
                dc_data.append({"dc_moId": i._moId, "dc_name": i.name})
            return {"result": True, "data": dc_data}
        except Exception, e:
            logger.exception("get_datacenter_info")
            return {"result": False, "data": str(e)}


    # 获取主机和群集
    def get_hc_info(self, dc_moId):
        try:
            si = self._connect_vc()
            content = si.RetrieveContent()
            dc = self._get_obj_bymoId(content, [vim.Datacenter], dc_moId)
            container = content.viewManager.CreateContainerView(dc.hostFolder, [vim.ComputeResource], True)
            hc_data = []
            for i in container.view:
                if isinstance(i, vim.ClusterComputeResource):
                    hc_data.append({"hc_moId": i._moId, "hc_name": i.name, "type": "ClusterComputer"})
                else:
                    hc_data.append({"hc_moId": i._moId, "hc_name": i.name, "type": "Computer"})
            return {"result": True, "data": hc_data}
        except Exception, e:
            logger.exception("get_hc_info")
            return {"result": False, "message": str(e)}


    # 获取hc存储
    def get_ds_info(self, hc_moId):
        try:
            si = self._connect_vc()
            content = si.RetrieveContent()
            hc = self._get_obj_bymoId(content, [vim.ClusterComputeResource], hc_moId)
            if hc == None:
                hc =self._get_obj_bymoId(content, [vim.ComputeResource], hc_moId)
            datastore = hc.datastore
            datastore_list = []
            for i in datastore:
                if isinstance(i.parent, vim.StoragePod):
                    i = i.parent
                summary = i.summary
                if hasattr(summary, "accessible"):
                    if summary.accessible == True:
                        if {"ds_moId": i._moId, "ds_name": i.name} not in datastore_list:
                            datastore_list.append({"ds_moId": i._moId, "ds_name": i.name})
                else:
                    if {"ds_moId": i._moId, "ds_name": i.name} not in datastore_list:
                        datastore_list.append({"ds_moId": i._moId, "ds_name": i.name})
            return {"result": True, "data": datastore_list}
        except Exception, e:
            logger.exception("get_ds_info")
            return {"result": False, "message": str(e)}


    # 获取hc的虚拟交换机网络
    def get_vswitch_info(self, hc_moId):
        try:
            si = self._connect_vc()
            content = si.RetrieveContent()
            hc = self._get_obj_bymoId(content, [vim.ClusterComputeResource], hc_moId)
            if hc == None:
                hc = self._get_obj_bymoId(content, [vim.ComputeResource], hc_moId)
            vswitch = hc.network
            vswitch_list = []
            for i in vswitch:
                if i.summary.accessible:
                    if isinstance(i, vim.dvs.DistributedVirtualPortgroup):
                        if hasattr(i.config, "uplink"):
                            if not i.config.uplink:
                                vswitch_list.append({"vs_moId": i._moId, "vs_name": i.name.encode('utf8')})
                        else:
                            vswitch_list.append({"vs_moId": i._moId, "vs_name": i.name.encode('utf8')})
                    else:
                        vswitch_list.append({"vs_moId": i._moId, "vs_name": i.name.encode('utf8')})
            return {"result": True, "data": vswitch_list}
        except Exception, e:
            logger.exception("get_vswitch_hc")
            return {"result": False, "message": str(e)}


    # 获取文件夹
    def get_folder_info(self, dc_moId):
        try:
            si = self._connect_vc()
            content = si.RetrieveContent()
            dc = self._get_obj_bymoId(content, [vim.Datacenter], dc_moId)
            folder = dc
            folder_list = self._get_child_folder(folder)
            if not len(folder_list):
                folder_list = [{"fo_moId": folder._moId, "fo_name": folder.name, "children": [], "id": folder._moId}]
            return {"result": True, "data": folder_list}
        except Exception, e:
            logger.exception("get_folder")
            return {"result": False, "message": str(e)}


    def _get_child_folder(self, folder):
        folder_child = []
        folder_temp = folder.childEntity
        for i in folder_temp:
            if hasattr(i, 'childEntity'):
                child_obj = {"moId": i._moId, "name": i.name, "children": [], "id": i._moId}
                child_obj["children"] = self._get_child_folder(i)
                folder_child.append(child_obj)
        return folder_child

    # 创建虚拟机，无tools
    def clone_vm_sample(self, args):
        logger.error("args:")
        logger.error(args)
        # 连接VC
        si = self._connect_vc()
        content = si.RetrieveContent()
        # 接受链接返回的数据
        config = self._get_vmconfig(content, args["cpu"], args["mem"], args["vmtemplate_moId"],
                                  args["vs_moId"],
                              args["vs_name"], args["disk"], args["disk_type"])
        logger.error("config:")
        logger.error(config)
        # 设置RelocateSpec
        RelocateSpec = vim.vm.RelocateSpec()
        logger.error('RelocteSpec:')
        logger.error(RelocateSpec)
        datastore = self._get_obj_bymoId(content, [vim.Datastore], args["ds_moId"])
        if datastore == None:
            StoragePod = self._get_obj_bymoId(content, [vim.StoragePod], args["ds_moId"])
            datastore = self._get_datastore_bysp(StoragePod)
        RelocateSpec.datastore = datastore
        hc = self._get_obj_bymoId(content, [vim.ComputeResource], args["hc_moId"])
        if not hc:
            hc = self._get_obj_bymoId(content, [vim.ClusterComputeResource], args["hc_moId"])
        # if args["rp_moId"]:
        #     resource_Pool = self._get_obj_bymoId(content, [vim.ResourcePool], args["rp_moId"])
        #     RelocateSpec.pool = resource_Pool
        # else:
        RelocateSpec.pool = hc.resourcePool
        if args["hc_moId"]:
            host = self._get_obj_bymoId(content, [vim.HostSystem], args["hc_moId"])
            RelocateSpec.host = host
        # 设置clonespec
        clonespec = vim.vm.CloneSpec()
        clonespec.location = RelocateSpec
        clonespec.config = config
        clonespec.powerOn = True
        # 设置目标文件夹
        dc = self._get_obj_bymoId(content, [vim.Datacenter], args["dc_moId"])
        if args["folder_moId"]:
            folder = self._get_obj_bymoId(content, [vim.Folder], args["folder_moId"])
        else:
            folder = dc.vmFolder
        # 克隆虚拟机
        vmtemplate = self._get_obj_bymoId(content, [vim.VirtualMachine], args["vmtemplate_moId"])
        task = vmtemplate.Clone(folder, args["vm_name"], clonespec)
        return task


    # 根据自定义条件创建虚拟机，有tools
    def clone_vm_custom(self, args):
        # 连接VC
        # si = connect_vc(args["vc_id"])
        # content = si.RetrieveContent()
        # args["DNS"] = [DNS1,DNS2]
        si = self._connect_vc()
        content = si.RetrieveContent()
        customizationspec = self._get_customizationspec(args["ip"], args["mask"], args["gateway"],
                                                        args["dns"],
                                                  args["vmtemplate_os"], args["computer_name"], args["vmtemplate_pwd"])
        config = self._get_vmconfig(content, args["cpu"], args["mem"], args["vmtemplate_moId"], args["vs_moId"],
                              args["vs_name"], args["disk"], args["disk_type"])
        # 设置RelocateSpec
        RelocateSpec = vim.vm.RelocateSpec()
        datastore = self._get_obj_bymoId(content, [vim.Datastore], args["ds_moId"])
        if datastore == None:
            StoragePod = self._get_obj_bymoId(content, [vim.StoragePod], args["ds_moId"])
            datastore = self._get_datastore_bysp(StoragePod)
        RelocateSpec.datastore = datastore
        hc = self._get_obj_bymoId(content, [vim.ComputeResource], args["hc_moId"])
        if hc == None:
            hc = self._get_obj_bymoId(content, [vim.ClusterComputeResource], args["hc_moId"])
        RelocateSpec.pool = hc.resourcePool
        # 设置clonespec
        clonespec = vim.vm.CloneSpec()
        clonespec.customization = customizationspec
        clonespec.location = RelocateSpec
        clonespec.config = config
        clonespec.powerOn = True
        # 设置目标文件夹
        dc = self._get_obj_bymoId(content, [vim.Datacenter], args["dc_moId"])
        if args["folder_moId"]:
            folder = self._get_obj_bymoId(content, [vim.Folder], args["folder_moId"])
        else:
            folder = dc.vmFolder
        # 克隆虚拟机
        vmtemplate = self._get_obj_bymoId(content, [vim.VirtualMachine], args["vmtemplate_moId"])
        task = vmtemplate.Clone(folder, args["vm_name"], clonespec)
        return task


    def _get_customizationspec(self, ipaddr, mask, gateway, dns_list, vmtemplate_os, computer_name, passwordstr):
        # 设置IP
        if ipaddr:
            ip = vim.CustomizationFixedIp()
            ip.ipAddress = ipaddr
        else:
            ip = vim.CustomizationDhcpIpGenerator()
        # 设置网卡
        adapter_ipsetting = vim.CustomizationIPSettings()
        adapter_ipsetting.ip = ip
        if mask:
            adapter_ipsetting.subnetMask = mask
        if gateway:
            adapter_ipsetting.gateway = gateway
        # adapter_ipsetting.dnsServerList = dns_list
        # 设置nicMap
        nicSettingMap = vim.CustomizationAdapterMapping()
        nicSettingMap.adapter = adapter_ipsetting
        nicSettingMaps = []
        nicSettingMaps.append(nicSettingMap)
        # 设置globalIPSettings
        globalIPSettings = vim.CustomizationGlobalIPSettings()
        globalIPSettings.dnsServerList = dns_list
        if vmtemplate_os.startswith("win"):
            identity = self._get_identity_win(computer_name, passwordstr)
        else:
            identity = self._get_identity_Linux(computer_name)
        # 设置customizationspec
        customizationspec = vim.CustomizationSpec()
        customizationspec.nicSettingMap = nicSettingMaps
        customizationspec.globalIPSettings = globalIPSettings
        customizationspec.identity = identity
        return customizationspec


    def _get_vmconfig(self, content, cpu_cores, mem, vmtemplate_moId, vswitch_moId, vswitch_name, data_disk_size,
                     disk_type):
        # 设置网卡和硬盘设备

        vmtemplate = self._get_obj_bymoId(content, [vim.VirtualMachine], vmtemplate_moId)
        devices = vmtemplate.config.hardware.device
        deviceChange = []
        unitNumber = 0
        disk_temp = vim.vm.device.VirtualDisk()
        for i in devices:
            if isinstance(i, vim.VirtualEthernetCard):
                nic_change0 = vim.VirtualDeviceConfigSpec()
                nic_change0.device = i
                nic_change0.operation = vim.vm.device.VirtualDeviceSpec.Operation.remove
                deviceChange.append(nic_change0)
            elif isinstance(i, vim.VirtualDisk):
                if unitNumber <= int(i.unitNumber):
                    unitNumber = int(i.unitNumber)
                    disk_temp = i
        nic_change = vim.VirtualDeviceConfigSpec()
        nic_change.device = vim.vm.device.VirtualVmxnet3()
        # nic_change.device.deviceInfo = vim.Description()
        # nic_change.device.deviceInfo.summary = vswitch_name
        netnic = self._get_obj_bymoId(content, [vim.Network], vswitch_moId)
        if isinstance(netnic, vim.dvs.DistributedVirtualPortgroup):
            nic_change.device.backing = vim.vm.device.VirtualEthernetCard.DistributedVirtualPortBackingInfo()
            nic_change.device.backing.port = vim.dvs.PortConnection()
            nic_change.device.backing.port.switchUuid = netnic.config.distributedVirtualSwitch.uuid
            nic_change.device.backing.port.portgroupKey = netnic.key
        else:
            nic_change.device.backing = vim.vm.device.VirtualEthernetCard.NetworkBackingInfo()
            nic_change.device.backing.network = netnic
            nic_change.device.backing.deviceName = vswitch_name
            # nic_change.device.backing.deviceName = netnic.name
            nic_change.device.backing.useAutoDetect = False
        nic_change.device.connectable = vim.vm.device.VirtualDevice.ConnectInfo()
        nic_change.device.connectable.startConnected = True
        nic_change.device.connectable.allowGuestControl = True
        nic_change.device.connectable.connected = False
        # nic_change.device.connectable.status = 'untried'
        nic_change.device.wakeOnLanEnabled = True
        nic_change.device.addressType = 'assigned'
        nic_change.operation = vim.vm.device.VirtualDeviceSpec.Operation.add
        deviceChange.append(nic_change)
        if data_disk_size != "0":
            unit_number = unitNumber + 1
            if unit_number == 7:
                unit_number += 1
            disk_add = vim.VirtualDeviceConfigSpec()
            disk_add.device = vim.vm.device.VirtualDisk()
            disk_add.device.capacityInKB = (int(data_disk_size)) * 1024 * 1024
            disk_add.device.controllerKey = disk_temp.controllerKey
            disk_add.device.unitNumber = unit_number
            # disk_add.device.key = int(disk_temp.key)+1
            disk_add.device.backing = vim.vm.device.VirtualDisk.FlatVer2BackingInfo()
            disk_add.device.backing.diskMode = 'persistent'
            if disk_type == 'thin':
                disk_add.device.backing.thinProvisioned = True
            elif disk_type == 'eager':
                disk_add.device.backing.thinProvisioned = False
                disk_add.device.backing.eagerlyScrub = True
            disk_add.fileOperation = "create"
            disk_add.operation = "add"
            deviceChange.append(disk_add)
        # 设置config（内存、CPU、设备）
        config = vim.VirtualMachineConfigSpec()
        config.memoryMB = (int(mem)) * 1024
        # config.numCoresPerSocket = (int(cpu_cores))/2
        config.numCPUs = int(cpu_cores)
        config.deviceChange = deviceChange
        return config

    def _get_datastore_bysp(self, StoragePod):
        datastores = [i for i in StoragePod.childEntity if i.summary.accessible]
        datastore = datastores[0]
        for i in datastores:
            if i.summary.freeSpace > datastore.summary.freeSpace:
                datastore = i
        return datastore

    def _get_identity_win(self, computer_name, passwordstr):
        # windows配置
        # 设置Unattend
        guiUnattended = vim.CustomizationGuiUnattended()
        guiUnattended.autoLogon = False
        guiUnattended.autoLogonCount = 0
        guiUnattended.timeZone = 210
        # 设置密码
        if passwordstr:
            password = vim.CustomizationPassword()
            password.plainText = True
            password.value = passwordstr
            guiUnattended.password = password
        # 设置identification
        identification = vim.CustomizationIdentification()
        identification.joinWorkgroup = "WorkGroup"
        # 设置计算机名
        if computer_name:
            computerName = vim.CustomizationFixedName()
            computerName.name = computer_name
        else:
            computerName = vim.CustomizationVirtualMachineName()
        # 设置userData
        userData = vim.CustomizationUserData()
        userData.computerName = computerName
        userData.fullName = "user"
        userData.orgName = "org"
        userData.productId = ""
        # 设置identity
        identity = vim.CustomizationSysprep()
        identity.guiUnattended = guiUnattended
        identity.identification = identification
        identity.userData = userData
        return identity

    def _get_identity_Linux(self, computer_name):
        # Linux配置
        # 设置计算机名
        if computer_name:
            hostName = vim.CustomizationFixedName()
            hostName.name = computer_name
        else:
            hostName = vim.CustomizationVirtualMachineName()
        # 设置identity
        identity = vim.CustomizationLinuxPrep()
        identity.hostName = hostName
        identity.domain = ""
        # identity.timeZone = "Asia/Shanghai"
        return identity

    def wait_for_vmclone_finish(self, args):
        # si = connect_vc(args["vc_id"])
        # content = si.RetrieveContent()
        si = self._connect_vc()
        content = si.RetrieveContent()
        logger.error(u"strat config")
        logger.error(u"开始进行配置")
        # if args["dns_list"]:
        #     args["dns_list"] = str(args["dns_list"]).split(",")
        # else:
        #     args["dns_list"] = []
        # logger.info(args)
        # args["dns_list"] = eval(args["dns_list"])
        if args["vmtemplate_toolstatus"] == "toolsNotInstalled":
            logger.error(u'ok,in clone_vm_sample')
            task = self.clone_vm_sample(args)
            logger.error(u'ok,next')
            task_result = self._wait_for_task(task)
            logger.error(u'ok,last')
            return task_result
        else:
            task = self.clone_vm_custom(args)
            task_result = self._wait_for_task(task)
            if task_result["result"] == True:
                newvm = task_result["data"]
                event_filter = vim.event.EventFilterSpec()
                filter_spec_entity = vim.event.EventFilterSpec.ByEntity()
                filter_spec_entity.entity = newvm
                filter_spec_entity.recursion = vim.event.EventFilterSpec.RecursionOption.all
                event_filter.entity = filter_spec_entity
                task_fi = False
                a = datetime.datetime.now()
                logger.error(u"自定义配置属性设置完成，开始应用")
                while not task_fi:
                    events = content.eventManager.QueryEvents(filter=event_filter)
                    for event in events:
                        if isinstance(event, vim.event.CustomizationSucceeded):
                            # if ("custom_list" in args.keys()) and args["custom_list"]:
                            #     set_customvalue(newvm, args["custom_list"])
                            return {"result": True, "data": newvm}
                    b = datetime.datetime.now()
                    if (b - a).seconds > 3600:
                        self.delete_failvm(newvm)
                        return {"result": False, "data": u"虚拟机创建成功，自定义配置应用超时"}
            else:
                return {"result": False, "data": task.info.error.msg}

    # 获取创建失败的虚拟机
    def get_failvm(self, args):
        si = self._connect_vc()
        content = si.RetrieveContent()
        folder = self._get_obj_bymoId(content, [vim.Folder], args["folder_moId"])
        vm = None
        for i in folder.childEntity:
            if isinstance(i, vim.VirtualMachine) and i.name == args["vm_name"]:
                vm = i
        return vm

    # 删除创建失败的虚拟机
    def delete_failvm(self, fail_vm):
        try:
            n = 0
            while n < 3:
                if fail_vm.summary.runtime.powerState == "poweredOn":
                    task1 = fail_vm.PowerOff()
                    task_result1 = self._wait_for_task(task1)
                    n += 1
                    if task_result1["result"]:
                        break
                else:
                    break
            time.sleep(3)
            task2 = fail_vm.Destroy()
            task_result = self._wait_for_task(task2)
            return task_result
        except Exception, e:
            error_msg = e.message if e.message else str(e)
            return {"result": False, "data": error_msg}


    def change_vm_cpu(self, new_numCPU, vm_moId):
        si = self._connect_vc()
        content = si.RetrieveContent()
        vm_obj = self._get_obj_bymoId(content, [vim.VirtualMachine], vm_moId)
        vm_numCoresPerSocket = int(vm_obj.config.hardware.numCoresPerSocket)
        try:
            if vm_obj.summary.runtime.powerState == "poweredOff":
                spec = vim.vm.ConfigSpec()
                spec.numCPUs = int(new_numCPU)
                task = vm_obj.ReconfigVM_Task(spec=spec)
                WaitForTask(task)
                return {'result': True}
            else:
                if vm_obj.config.cpuHotAddEnabled == True:
                    if not isinstance(int(new_numCPU)/vm_numCoresPerSocket, int):
                        return {"result": False, "data": u"每个插槽的内核数为" + str(vm_numCoresPerSocket) + u",请输入其整数倍数值"}
                    if new_numCPU > 24 or new_numCPU < 1:
                        return {"result": False, "data": u"总CPU内核数必须介于1~24之间"}
                    else:
                        spec = vim.vm.ConfigSpec()
                        spec.numCPUs = new_numCPU
                        task = vm_obj.ReconfigVM_Task(spec=spec)
                        WaitForTask(task)
                        return {'result': True}
                else:
                    return {"result": False, "data": u"未启用热插拔，无法在线更改CPU！"}
        except Exception, e:
            error_msg = e.message if e.message else str(e)
            return {"result": False, "data": error_msg}

    # 内存扩缩容
    def change_vm_mem(self, new_memoryMB, vm_moId):
        si = self._connect_vc()
        content = si.RetrieveContent()
        vm_obj = self._get_obj_bymoId(content, [vim.VirtualMachine], vm_moId)
        vm_memoryMB = int(vm_obj.config.hardware.memoryMB)
        new_memoryMB = int(new_memoryMB * 1024)
        try:
            if vm_obj.summary.runtime.powerState == "poweredOff":
                spec = vim.vm.ConfigSpec()
                spec.memoryMB = int(new_memoryMB)
                task = vm_obj.ReconfigVM_Task(spec=spec)
                WaitForTask(task)
                return {'result': True}
            else:
                if vm_obj.config.memoryHotAddEnabled == True:
                    if not isinstance(int(new_memoryMB) / 4, int):
                        return {"result": False, "data": u"内存必须是4M的倍数"}
                    if new_memoryMB < vm_memoryMB:
                        return {"result": False, "data": u"内存必须介于" + str(vm_memoryMB / 1024) + "GB和64GB之间"}
                    else:
                        spec = vim.vm.ConfigSpec()
                        spec.memoryMB = int(new_memoryMB)
                        task = vm_obj.ReconfigVM_Task(spec=spec)
                        # tasks.wait_for_tasks(si, [task])
                        WaitForTask(task)
                        return {'result': True}
                else:
                    return {"result": False, "data": u"未启用热插拔，无法在线更改内存！"}
        except Exception, e:
            logger.exception("change_vm_mem")
            error_msg = e.message if e.message else str(e)
            return {"result": False, "data": error_msg}

    # 磁盘Disk扩容
    def change_vm_disk(self, disk_label, new_disk_size, vm_moId):
        si = self._connect_vc()
        content = si.RetrieveContent()
        vm_obj = self._get_obj_bymoId(content, [vim.VirtualMachine], vm_moId)
        try:
            virtual_disk_device = None
            if not vm_obj.rootSnapshot:
                for dev in vm_obj.config.hardware.device:
                    if isinstance(dev, vim.vm.device.VirtualDisk) and dev.deviceInfo.label == disk_label:
                        virtual_disk_device = dev
                if not virtual_disk_device:
                    return RuntimeError('Virtual {} could not be found.'.format(disk_label))

                virtual_disk_spec = vim.vm.device.VirtualDeviceSpec()
                virtual_disk_spec.operation = vim.vm.device.VirtualDeviceSpec.Operation.edit
                virtual_disk_spec.device = virtual_disk_device
                virtual_disk_spec.device.capacityInKB = int(new_disk_size) * 1024 * 1024

                dev_changes = []
                dev_changes.append(virtual_disk_spec)
                spec = vim.vm.ConfigSpec()
                spec.deviceChange = dev_changes
                task = vm_obj.ReconfigVM_Task(spec=spec)
                # tasks.wait_for_tasks(si, [task])
                WaitForTask(task)
                return {'result': True}
        except Exception, e:
            error_msg = e.message if e.message else str(e)
            return {"result": False, "data": error_msg}

    # 磁盘Disk新增
    def add_vm_disk(self, new_disk_size, new_disk_type, vm_moId):
        si = self._connect_vc()
        content = si.RetrieveContent()
        vm_obj = self._get_obj_bymoId(content, [vim.VirtualMachine], vm_moId)
        try:
            unit_number = 0
            for dev in vm_obj.config.hardware.device:
                if hasattr(dev.backing, "fileName"):
                    unit_number = int(dev.unitNumber) + 1
                    if unit_number == 7:
                        unit_number += 1
                    if unit_number >= 16:
                        return {"result": False, "data": u"磁盘数据已达到上限"}

                if isinstance(dev, vim.vm.device.VirtualSCSIController):
                    controller = dev

            dev_changes = []
            virtual_disk_spec = vim.vm.device.VirtualDeviceSpec()
            virtual_disk_spec.fileOperation = "create"
            virtual_disk_spec.operation = vim.vm.device.VirtualDeviceSpec.Operation.add
            virtual_disk_spec.device = vim.vm.device.VirtualDisk()
            virtual_disk_spec.device.backing = vim.vm.device.VirtualDisk.FlatVer2BackingInfo()
            if new_disk_type == "thin":
                virtual_disk_spec.device.backing.thinProvisioned = True
            virtual_disk_spec.device.backing.diskMode = "persistent"
            virtual_disk_spec.device.unitNumber = unit_number
            virtual_disk_spec.device.capacityInKB = int(new_disk_size) * 1024 * 1024
            virtual_disk_spec.device.controllerKey = controller.key

            dev_changes.append(virtual_disk_spec)
            spec = vim.vm.ConfigSpec()
            spec.deviceChange = dev_changes
            task = vm_obj.ReconfigVM_Task(spec=spec)
            WaitForTask(task)
            return {'result': True}
        except Exception, e:
            error_msg = e.message if e.message else str(e)
            return {"result": False, "data": error_msg}


    #重命名虚拟机
    def rename_vm(self, vm_moId, new_name):
        try:
            si = self._connect_vc()
            content = si.RetrieveContent()
            vm = self._get_obj_bymoId(content, [vim.VirtualMachine], vm_moId)
            spec = vim.vm.ConfigSpec()
            spec.name = new_name
            vm.ReconfigVM_Task(spec=spec)
            self._deconnect_vc(si)
            return {"result": True, "data": ""}
        except Exception,e:
            logger.exception("rename_vm")
            return {"result": False, "data": str(e)}
