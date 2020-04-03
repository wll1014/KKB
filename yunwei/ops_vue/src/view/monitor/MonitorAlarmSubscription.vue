<template>
  <div class="page-monitor-alarm-subscription  theme-dark">
    <div class="area-monitor-alarm-top">
      <el-button @click="buttonSettingAlarmSubscription">订阅告警设置</el-button>
    </div>
    <!--顶部搜索区域-->
    <div class="area-header" style="line-height: 26px;height: 26px;vertical-align: top;">

      <el-select @change="alarmSubscriptionTypeChange" popper-class="theme-dark"
                 v-model="optionSelectedAlarmSubscriptionType" placeholder="请选择告警类型"
                 style="width: 160px;margin-right: 7px;">
        <el-option
          v-for="item in optionsAlarmSubscriptionType" :key="item.value" :label="item.type" :value="item.value">
        </el-option>
      </el-select>
      <el-select popper-class="theme-dark" v-model=" optionSelectedPlatformDomain" placeholder="请选择平台域"
                 style="width: 160px;margin-right: 7px;">
        <el-option
          v-for="item in optionsPlatformDomain" :key="item.moid" :label="item.name" :value="item.moid">
        </el-option>
      </el-select>
      <el-select v-show="optionSelectedAlarmSubscriptionType==='alarmDev'" popper-class="theme-dark"
                 v-model=" optionSelectedMachineRoom" placeholder="请选择机房" style="width: 140px;margin-right: 7px;">
        <el-option
          v-for="item in optionsMachineRoom" :key="item.moid" :label="item.name" :value="item.moid">
        </el-option>
      </el-select>
      <el-select popper-class="theme-dark" v-model="optionSelectedMachineType" placeholder="请选择设备类型"
                 style="width: 140px;margin-right: 7px;">
        <el-option
          v-for="item in optionsMachineType" :key="item" :label="item" :value="item">
        </el-option>
      </el-select>
      <el-input style="width: 160px;margin-right: 7px;" v-model="inputSearchHost" maxlength="100"
                placeholder="请输入设备名称搜索" @keyup.enter.native="buttonSearchAlarmSubscription" clearable></el-input>

      <div style="display: inline-block;margin-right: 7px;vertical-align: top;line-height: 25px;">
        <el-date-picker
          style="width: 240px;"
          v-model="datePickerAlarmSubscription"
          type="daterange"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          popper-class="theme-dark "
          value-format="timestamp"
          format="yyyy-MM-dd"
          :default-time="['00:00:00', '23:59:59']"
          range-separator=""
          class="clear-close-icon"
          prefix-icon="ops-icons-bg icon-calendar"
          :clearable=false
        >
        </el-date-picker>
      </div>

      <!--<el-select class="alarmSelectHeight" multiple popper-class="theme-dark" v-model="optionSelectedAlarmLevel" placeholder="请选择级别" style="width: 140px;margin-right: 7px;">
        <el-option
          v-for="item in optionsAlarmLevel" :key="item.value" :label="item.label" :value="item.value">
        </el-option>
      </el-select>-->

      <el-popover
        placement="bottom-start"
        width="114"
        v-model="selectPopover"
        popper-class="theme-dark">
        <div style="text-align: left; margin: 0;">
          <el-checkbox-group v-model="optionSelectedAlarmLevel">
            <div v-for="(v,k) in optionsAlarmLevel" :key="k">
              <el-checkbox :label="k">{{v}}</el-checkbox>
            </div>
          </el-checkbox-group>
        </div>
        <el-input
          slot="reference"
          placeholder="请选择级别"
          suffix-icon="ops-icons-bg icon__caret--arrow-down"
          v-model="inputSelectedAlarmLevel"
          style="width: 140px;margin-right: 7px;"
          :class="selectPopover?'popover-is-reverse':''">
        </el-input>
      </el-popover>

      <el-button @click="buttonSearchAlarmSubscription">搜索</el-button>
      <div style="display: inline-block;float: right;margin-right: 0px;line-height: 27px;">
        <el-button @click="buttonExportAlarmSubscription" style="">导出</el-button>
      </div>

    </div>
    <!--顶部搜索区域end-->

    <!-- 表格区域 -->
    <div class="area-table" style="margin-top: 18px;">
      <el-table ref="tableAlarmSubscription" tooltip-effect="dark"
                stripe
                border
                style="width: 100%;"
                :data="tableDataAlarmSubscription"
                v-loading="loadingTableData"
                element-loading-background="rgba(0, 0, 0, 0.5)"
      >
        <el-table-column show-overflow-tooltip type="index" label="序号" width="56">
        </el-table-column>
        <el-table-column show-overflow-tooltip v-for="item in tableColumnTitle" :prop="item.prop" :label="item.label"
                         :key="item.prop" :width="item.width">
        </el-table-column>
        <!-- yp__start -->
        <el-table-column label='操作' min-width="50px">
          <template slot-scope="scope">
            <button type="button" class="button-host-info" @click="alarmFix(scope.$index,tableDataAlarmSubscription)"
                    v-if='!scope.row.resolve_time'>
              <span style="text-decoration: underline;">忽略告警</span>
            </button>
            <button type="button" class="button-host-info" disabled v-if='scope.row.resolve_time'>
              <span style="text-decoration: underline;color: gray;">已修复</span>
            </button>
          </template>
        </el-table-column>
        <!-- yp__end -->
      </el-table>
    </div>
    <!-- 表格区域end -->
    <!-- 分页区start -->
    <div style="margin-top: 20px;">
      <KdPagination
        @current-change="pageHandleCurrentChange"
        :pageSize="pageSize"
        :currentPage.sync="currentPage"
        :total="pageTotal"
      ></KdPagination>
    </div>
    <!-- 分页区end -->
    <!--订阅告警设置蒙版-->
    <el-dialog
      title="订阅告警设置"
      :visible.sync="dialogVisible"
      width="800px"
    >
      <MonitorAlarmSubscriptionSettings ref="alarmSubscription"></MonitorAlarmSubscriptionSettings>
      <div style="padding: 20px 20px 25px 20px;text-align: center;box-sizing: border-box;">
          <span style="text-align: center;">
            <el-button @click="changeSubAlarmCodes">保 存</el-button>
            <el-button @click="dialogVisible = false">取 消</el-button>
          </span>
      </div>
    </el-dialog>
    <!-- yp__start -->
    <el-dialog title="提示" :visible.sync="fixVisible" width="300px" top="15%" :close-on-click-modal="false">
      <div style="margin-top: 40px;margin-bottom: 20px;margin-left: 50px;">
			    <span style="margin-right: 7px;font-size: 14px;">
			      <i class="ops-icons-bg icon-notice" style="vertical-align: bottom;"></i>
			    </span>
        <span>确定忽略此条告警？</span>
      </div>
      <div align='center' slot='footer' class='theme-dark' style='margin-top:10px;padding-bottom: 10px'>
        <el-button type="info" @click="fixRowAll()">确 定</el-button>
        <el-button @click="fixVisible = false">取 消</el-button>
      </div>
    </el-dialog>
    <!-- yp__end -->
  </div>
</template>

<script>
  export default {
    components: {
      MonitorAlarmSubscriptionSettings: () => import('@/view/monitor/MonitorAlarmSubscriptionSettings.vue'),
      KdPagination: () => import('@/components/common/KdPagination.vue'),
    },
    name: "MonitorAlarmSubscription",
    computed: {
      inputSelectedAlarmLevel() {
        let temList = this.optionSelectedAlarmLevel.map(i => this.optionsAlarmLevel[i])
        return temList.join(", ")
      }
    },
    data() {
      return {
        searchKeepAliveParams: {},
        // 下拉框数据
        optionsAlarmSubscriptionType: [{
          type: '服务器订阅告警',
          value: 'alarmDev'
        }, {
          type: '终端订阅告警',
          value: 'alarmMT'
        }],
        optionSelectedAlarmSubscriptionType: 'alarmDev',

        optionsPlatformDomain: [{
          name: '全部平台域',
          moid: 'all'
        }],
        optionSelectedPlatformDomain: 'all',

        optionsMachineRoom: [{
          name: '全部机房',
          moid: 'all'
        }],
        optionSelectedMachineRoom: 'all',

        optionsMachineType: [
          '全部设备类型',
        ],
        optionSelectedMachineType: '全部设备类型',

        // optionsAlarmLevel:[{label:"严重",value:"critical"},
        //                    {label:"重要",value:"important"},
        //                    {label:"一般",value:"normal"},],
        optionsAlarmLevel: {
          critical: '严重',
          important: '重要',
          normal: '一般'
        },
        selectPopover: false,
        // inputSelectedAlarmLevel:'',
        optionSelectedAlarmLevel: [],

        // 输入框数据
        inputSearchHost: null,

        // 时间选择数据
        datePickerAlarmSubscription: null,

        // 表格数据
        tableColumnTitleConf: {
          'alarmDev': [
            {prop: 'device_name', label: '设备名称', width: 186,},
            {prop: 'description', label: '告警描述',},
            {prop: 'level', label: '告警级别', width: 76,},
            {prop: 'platform_domain_name', label: '所属平台域', width: 146,},
            {prop: 'machine_room_name', label: '所属机房', width: 136,},
            {prop: 'device_type', label: '设备类型', width: 136,},
            {prop: 'device_ip', label: '设备IP', width: 136,},
            {prop: 'start_time', label: '产生时间', width: 186,},
            {prop: 'resolve_time', label: '恢复时间', width: 186,},
          ],
          'alarmMT': [
            {prop: 'device_name', label: '设备名称', width: 186,},
            {prop: 'description', label: '告警描述',},
            {prop: 'level', label: '告警级别', width: 76,},
            {prop: 'domain_name', label: '所属用户域', width: 146,},
            {prop: 'device_type', label: '设备类型', width: 136,},
            {prop: 'device_ip', label: '设备IP', width: 136,},
            {prop: 'device_e164', label: '设备E164', width: 146,},
            {prop: 'start_time', label: '产生时间', width: 186,},
            {prop: 'resolve_time', label: '恢复时间', width: 186,},
          ],
        },

        tableColumnTitle: [],
        tableDataAlarmSubscription: [],
        loadingTableData: false,

        // 分页数据
        currentPage: 1,
        pageSize: 15,
        pageTotal: 0,

        // 蒙版内数据
        dialogVisible: false,
        // // 订阅告警的code
        // subAlarmCodes:{},

        // 导出需要用的传参
        pkfile_ids: [],

        // yp__start
        fixInfo: {},
        fixVisible: false,
        // yp__end
      }
    },
    methods: {
      // 搜索按钮
      buttonSearchAlarmSubscription() {
        this.searchKeepAliveParams = {
          warning_type: this.optionSelectedAlarmSubscriptionType,
          platform_moid: this.optionSelectedPlatformDomain === 'all' ? '' : this.optionSelectedPlatformDomain,
          machine_room_moid: this.optionSelectedMachineRoom === 'all' ? '' : this.optionSelectedMachineRoom,
          device_type: this.optionSelectedMachineType === '全部设备类型' || this.optionSelectedMachineType === '全部终端类型' ? '' : this.optionSelectedMachineType,
          search: this.inputSearchHost,
          start_time: this.datePickerAlarmSubscription[0],
          end_time: this.datePickerAlarmSubscription[1],
          level: this.optionSelectedAlarmLevel.join(','),
        }
        this.currentPage = 1
        this.searchAlarmInfo()
      },
      // 导出按钮
      buttonExportAlarmSubscription() {
        let objAlarmType = {
          alarmDev: 0, //服务器订阅告警
          alarmMT: 1, //终端订阅告警
        }
        let params = {
          warning_type: this.searchKeepAliveParams.warning_type ? objAlarmType[this.searchKeepAliveParams.warning_type] : objAlarmType[this.optionSelectedAlarmSubscriptionType],
          platform_moid: this.searchKeepAliveParams.platform_moid ? this.searchKeepAliveParams.platform_moid : this.optionSelectedPlatformDomain === 'all' ? '' : this.optionSelectedPlatformDomain,
          machine_room_moid: this.searchKeepAliveParams.machine_room_moid ? this.searchKeepAliveParams.machine_room_moid : this.optionSelectedMachineRoom === 'all' ? '' : this.optionSelectedMachineRoom,
          device_type: this.searchKeepAliveParams.device_type ? this.searchKeepAliveParams.device_type : this.optionSelectedMachineType === '全部设备类型' || this.optionSelectedMachineType === '全部终端类型' ? '' : this.optionSelectedMachineType,
          search: this.searchKeepAliveParams.search,
          start_time: this.searchKeepAliveParams.start_time ? this.searchKeepAliveParams.start_time : this.datePickerAlarmSubscription[0],
          end_time: this.searchKeepAliveParams.end_time ? this.searchKeepAliveParams.end_time : this.datePickerAlarmSubscription[1],
          level: this.searchKeepAliveParams.level ? this.searchKeepAliveParams.level : this.optionSelectedAlarmLevel.join(','),
        }
        // let params={pkfile_ids:this.pkfile_ids}
        this.$api.monitor.downloadAlarmEvents(params)
          .then(res => {
            // console.log(res)
            const content = res.data
            const blob = new Blob([content])
            const fileName = res.headers["content-disposition"].split("filename=")[1]
            if ('download' in document.createElement('a')) { // 非IE下载
              const elink = document.createElement('a')
              elink.download = fileName
              elink.style.display = 'none'
              elink.href = URL.createObjectURL(blob)
              document.body.appendChild(elink)
              elink.click()
              URL.revokeObjectURL(elink.href) // 释放URL 对象
              document.body.removeChild(elink)
            } else { // IE10+下载
              navigator.msSaveBlob(blob, fileName)
            }
          })
      },
      // 订阅告警设置按钮
      buttonSettingAlarmSubscription() {
        this.dialogVisible = true
        if (this.$refs.alarmSubscription) {
          this.$refs.alarmSubscription.init()
        }
      },

      // 蒙版内订阅告警确定按钮
      changeSubAlarmCodes() {
        let subAlarmCodes = this.$refs.alarmSubscription.getCheckedAlarmCodes()
        let loginInfo = this.$store.getters.getLoginInfo
        let params = []
        for (let key in subAlarmCodes) {
          subAlarmCodes[key].forEach(item => {
            params.push({
              "domain_moid": loginInfo.virMachineroomMoid,
              "user_id": loginInfo.moid,
              "sub_code": item
            })
          })
        }
        // console.log(params)
        // 先清空再添加
        let loading = this.$loading({
          lock: true,
          text: '正在保存，请稍等...',
          spinner: 'el-icon-loading',
          background: 'rgba(0, 0, 0, 0.7)'
        });
        this.$api.monitor.delSubAlarmCodes({ids: "all"})
          .then(res => {
            // console.log(res.status,res.data.success)

            if (res.status === 200 && res.data.success === 1) {
              this.$api.monitor.addSubAlarmCodes(params)
                .then(res => {
                  loading.close();
                  this.dialogVisible = false
                })
            }
          })
        // this.$refs.alarmSubscription.init()
      },

      // 告警类型切换
      alarmSubscriptionTypeChange(val) {
        if (val === 'alarmDev') {
          this.devInit()
        } else {
          this.terminalInit()
        }
      },
      // 分页变化
      pageHandleCurrentChange(val) {
        // console.log(val)
        this.currentPage = val
        this.searchAlarmInfo()
      },

      // 功能函数start
      // 返回值转换；涉及字段：告警级别，时间
      convertTableData(data) {
        if (data) {
          let alarmType = {critical: '严重', important: '重要', normal: '一般'}
          let newData = data.map((item) => {
            item.level = alarmType[item.level]
            item.start_time = item.start_time ? new Date(item.start_time).format('Y-m-d H:i:s') : ''
            item.resolve_time = item.resolve_time ? new Date(item.resolve_time).format('Y-m-d H:i:s') : ''
            item.device_name = item.device_name ? item.device_name : '----'
            item.device_type = item.device_type ? item.device_type : '----'
            item.device_ip = item.device_ip ? item.device_ip : '----'
            item.platform_domain_name = item.platform_domain_name ? item.platform_domain_name : '----'
            item.machine_room_name = item.machine_room_name ? item.machine_room_name : '----'
            return item
          })
          return newData
        }
      },
      // 功能函数end

      // API START
      // 服务器相关
      async getPaltformDomain() {
        this.optionsPlatformDomain = [{
          name: '全部平台域',
          moid: 'all'
        }].concat(await this.$api.homePage.getAllPlatformDomainInfo())

        this.optionSelectedPlatformDomain = 'all'
      },
      async getAllDevRoom() {
        this.optionsMachineRoom = [{
          name: '全部机房',
          moid: 'all'
        }]
        for (let item of this.optionsPlatformDomain.slice(1,)) {
          this.optionsMachineRoom = this.optionsMachineRoom.concat(await this.$api.homePage.getMachineRoomInfo(item.moid))
        }
        this.optionSelectedMachineRoom = 'all'
        // this.optionsMachineRoom=await this.$api.homePage.getMachineRoomInfo(this.optionSelectedPlatformDomain)
        // this.optionSelectedMachineRoom=this.optionsMachineRoom[0].moid
      },
      async getAllDevType() {
        let typeList = await this.$api.monitor.getServerDevTypes()
        this.optionsMachineType = ['全部设备类型'].concat(typeList.filter(i => i))
        // console.log( this.optionsMachineType)
        this.optionSelectedMachineType = '全部设备类型'
      },
      // 服务器相关end
      // 终端相关
      async getUserDomain() {
        this.optionsPlatformDomain = [{
          name: '全部用户域',
          moid: 'all'
        }].concat(await this.$api.homePage.getAllUserDomainInfo())
        this.optionSelectedPlatformDomain = 'all'
      },
      async getAllTerminalType() {
        let typeList = await this.$api.monitor.getTerminalDevTypes()
        this.optionsMachineType = ['全部终端类型'].concat(typeList.filter(i => i))
        // console.log( this.optionsMachineType)
        this.optionSelectedMachineType = '全部终端类型'
      },

      async searchAlarmInfo() {
        this.loadingTableData = true
        let temPkfile_ids = []
        let temTableData = []
        let alarmInfoData = ''
        let pstart = (this.currentPage - 1) * this.pageSize
        let pcount = this.pageSize
        let start_time = ''
        let end_time = ''
        // 判断时间是否选择
        if (this.datePickerAlarmSubscription) {
          start_time = this.datePickerAlarmSubscription[0]
          end_time = this.datePickerAlarmSubscription[1]
        } else {
          let timestamp = (new Date()).getTime();
          this.datePickerAlarmSubscription = [timestamp - 86400000 * 7, timestamp]
          start_time = this.datePickerAlarmSubscription[0]
          end_time = this.datePickerAlarmSubscription[1]
        }

        if (this.optionSelectedAlarmSubscriptionType === 'alarmDev') {
          this.tableColumnTitle = this.tableColumnTitleConf.alarmDev

          let params = {
            platform_moid: this.optionSelectedPlatformDomain === 'all' ? '' : this.optionSelectedPlatformDomain,
            machine_room_moid: this.optionSelectedMachineRoom === 'all' ? '' : this.optionSelectedMachineRoom,
            device_type: this.optionSelectedMachineType === '全部设备类型' ? '' : this.optionSelectedMachineType,
            search: this.inputSearchHost,
            start_time: start_time,
            end_time: end_time,
            level: this.optionSelectedAlarmLevel.join(','),
            start: pstart,
            count: pcount
          }
          // console.log(params)
          alarmInfoData = await this.$api.monitor.getAlarmInfoServerUnrepaired(params)
          // 统计告警的数量
          let temRepairedData = await this.$api.monitor.getAlarmInfoServerRepaired(params)
          this.pageTotal = alarmInfoData.total + temRepairedData.total

          temTableData = alarmInfoData.info
          temPkfile_ids.push(alarmInfoData.pkfile_id)
          // 判断已修复数据是否足够
          let unrepairedNeedCount = (pstart + pcount) - alarmInfoData.total
          // console.log(unrepairedNeedCount)
          if (unrepairedNeedCount <= 0) {
            // 若数量足够不做其他处理
          } else if (unrepairedNeedCount < this.pageSize) {
            params['start'] = 0
            params['count'] = unrepairedNeedCount
            let repairedData = await this.$api.monitor.getAlarmInfoServerRepaired(params)
            // console.log(repairedData)
            temTableData = temTableData.concat(repairedData.info)
            temPkfile_ids.push(repairedData.pkfile_id)
          } else if (unrepairedNeedCount >= this.pageSize) {
            params['start'] = unrepairedNeedCount - this.pageSize
            params['count'] = this.pageSize
            let repairedData = await this.$api.monitor.getAlarmInfoServerRepaired(params)
            // console.log(repairedData)
            temTableData = repairedData.info
            temPkfile_ids.push(repairedData.pkfile_id)
          }
        } else { //终端告警
          this.tableColumnTitle = this.tableColumnTitleConf.alarmMT
          let params = {
            domain_moid: this.optionSelectedPlatformDomain === 'all' ? '' : this.optionSelectedPlatformDomain,
            device_type: this.optionSelectedMachineType === '全部终端类型' ? '' : this.optionSelectedMachineType,
            search: this.inputSearchHost,
            start_time: start_time,
            end_time: end_time,
            level: this.optionSelectedAlarmLevel.join(','),
            start: pstart,
            count: pcount
          }
          // console.log(params)
          alarmInfoData = await this.$api.monitor.getAlarmInfoTerminalUnrepaired(params)
          // 统计告警的数量
          let temRepairedData = await this.$api.monitor.getAlarmInfoTerminalRepaired(params)
          this.pageTotal = alarmInfoData.total + temRepairedData.total

          temTableData = alarmInfoData.info

          temPkfile_ids.push(alarmInfoData.pkfile_id)
          // 判断已修复数据是否足够
          let unrepairedNeedCount = (pstart + pcount) - alarmInfoData.total
          // console.log(unrepairedNeedCount)
          if (unrepairedNeedCount <= 0) {

          } else if (unrepairedNeedCount < this.pageSize) {
            params['start'] = 0
            params['count'] = unrepairedNeedCount
            let repairedData = await this.$api.monitor.getAlarmInfoTerminalRepaired(params)
            temTableData = temTableData.concat(repairedData.info)
            temPkfile_ids.push(repairedData.pkfile_id)
          } else if (unrepairedNeedCount >= this.pageSize) {
            params['start'] = unrepairedNeedCount - this.pageSize
            params['count'] = this.pageSize
            let repairedData = await this.$api.monitor.getAlarmInfoTerminalRepaired(params)
            // console.log(repairedData)
            temTableData = repairedData.info
            temPkfile_ids.push(repairedData.pkfile_id)
          }
        }
        this.tableDataAlarmSubscription = this.convertTableData(temTableData)
        this.pkfile_ids = temPkfile_ids.filter(item => item)
        // console.log(this.pkfile_ids)
        this.loadingTableData = false
      },
      // 终端相关end
      //修复按钮 by yp __start
      alarmFix(index, val) {
        var params = {}
        if (this.optionSelectedAlarmSubscriptionType === "alarmDev") {
          params = {
            "warning_type": 0,
            "warning_id": val[index].id
          }
        } else if (this.optionSelectedAlarmSubscriptionType === "alarmMT") {
          params = {
            "warning_type": 1,
            "warning_id": val[index].id
          }
        }
        this.fixInfo = params
        this.fixVisible = true

      },
      fixRowAll() {
        this.$api.monitor.postAlarmFix(this.fixInfo).then(res => {
          if (res.data.success === 1) {
            this.$message('设置成功')
            this.currentPage = 1
            this.fixVisible = false
            this.searchAlarmInfo()
          } else {
            let msg = '设置失败'
            if (res.data.error_code === 10404) msg = "告警已恢复"
            this.$message(msg)
            this.fixVisible = false
            this.searchAlarmInfo()
          }
        })
      },
      // yp__end

      // API END
      async devInit() {
        await this.getPaltformDomain()
        this.getAllDevRoom()
        this.getAllDevType()
      },

      async terminalInit() {
        this.getUserDomain()
        this.getAllTerminalType()
      },
      async init() {

        let startTime = new Date().setHours(0, 0, 0, 0) - 86400000 * 6
        let endTime = new Date().setHours(23, 59, 59, 0)
        // let timestamp = (new Date()).getTime();
        this.datePickerAlarmSubscription = [startTime, endTime]

        // 调整当前route，变化侧边栏高亮
        let activeRouteList = ['/ops/manage/alarm', '/ops/manage']
        this.$store.dispatch('activeRouteChange', activeRouteList)
        //根据传参处理
        if (Object.keys(this.$route.params).length !== 0) {
          // 判断显示页面
          let type = this.$route.params.type
          if (type === "alarmMt") {
            this.optionSelectedAlarmSubscriptionType = "alarmMT"
            this.optionSelectedMachineType = '全部终端类型'
            this.terminalInit()
          } else {
            this.devInit()
          }

          // 判断是否带过滤条件
          let urlParams = this.$route.params.urlParams
          if (urlParams) {
            this.inputSearchHost = urlParams.search || ''
          }
          Object.keys(this.$route.params).forEach(i => this.$route.params[i] = null)
        } else {  //默认显示设备定义告警
          this.devInit()
        }

        this.searchAlarmInfo()
      },
    },
    mounted() {
      this.init()
    },
  }
</script>

<style>
  .page-monitor-alarm-subscription {
    position: relative;
    padding: 8px 0px 0px 0px;
  }

  .area-monitor-alarm-top {
    position: absolute;
    top: -43px;
    right: 0px;
  }

  .alarmSelectHeight.el-select .el-input__inner {
    height: 26px !important;
  }
</style>
