<template>
  <div class="theme-dark repoter-day-conf">
    <KdTabCommon :tab-list="tabList" :active-tab="activeTab" @tab-change="tabChange"></KdTabCommon>

    <div style="border-bottom: #3d4046 1px dashed;padding-bottom: 10px;margin-top: 10px;">
      <div style="display: inline-block;margin-right: 7px;vertical-align: top;line-height: 25px;">
        <el-date-picker
          style="width: 140px;"
          v-model="datePickerRepoterDay"
          type="date"
          @change="datePickerChange"
          popper-class="theme-dark "
          value-format="timestamp"
          format="yyyy-MM-dd"
          range-separator=""
          class="clear-close-icon"
          prefix-icon="ops-icons-bg icon-calendar"
          :clearable=false
          :picker-options="pickerOptions"
        >
        </el-date-picker>
        <!--<el-select popper-class="theme-dark" v-model="optionSelectedDomain" style="width: 140px;margin-right: 7px;">
          <el-option
            v-for="item in optionsDomain" :key="item" :label="item" :value="item">
          </el-option>
        </el-select>-->
      </div>
    </div>

    <!--会议数据内容区-->
    <div v-if="activeTab==='RepoterDayConf'" class="repoter-day__content">
      <!--平台概况-->
      <div class="repoter-day__block" style="width: 100%;height: 700px;">
        <div class="repoter-day__block-title">
          平台概况
        </div>
        <div style="width: 100%;">
          <div class="repoter-day__block-child" style="width: 50%;">
            <div>
              <div class="repoter-day__block-child-title">服务器类型概况</div>
              <div class="repoter-day__block-child" style="width: 100%;height: 230px;">
                <ReportDayChart ChartName="reportDayServerDev"
                                ChartID="reportDayServerDev"
                                :params="globalParams"></ReportDayChart>
              </div>
            </div>
          </div>
          <div class="repoter-day__block-child" style="width: 50%;">
            <div>
              <div class="repoter-day__block-child-title">会议客观质量</div>
              <div class="repoter-day__block-child" style="width: 100%;height: 230px;">
                <ReportDayChart ChartName="reportDayConfQuality"
                                ChartID="reportDayConfQuality"
                                :params="globalParams"></ReportDayChart>
              </div>
            </div>
          </div>
        </div>
        <div style="width: 100%;margin-top: 70px;">
          <div class="repoter-day__block-child" style="width: 50%;">
            <div>
              <div class="repoter-day__block-child-title">会议类型概况</div>
              <div class="repoter-day__block-child" style="width: 100%;height: 230px;">
                <ReportDayChart ChartName="reportDayConfType"
                                ChartID="reportDayConfType"
                                :params="globalParams"></ReportDayChart>
              </div>
            </div>
          </div>
          <div class="repoter-day__block-child" style="width: 50%;">
            <div>
              <div class="repoter-day__block-child-title">会议时长概况</div>
              <div class="repoter-day__block-child" style="width: 100%;height: 230px;">
                <ReportDayChart ChartName="reportDayConfTime"
                                ChartID="reportDayConfTime"
                                :params="globalParams"></ReportDayChart>
              </div>
            </div>
          </div>
        </div>
      </div>
      <!--平台概况 end-->

      <!--会议概况概况-->
      <div class="repoter-day__block" style="width: 100%;">
        <div class="repoter-day__block-title">
          会议概况
        </div>
        <div class="repoter-day__block-child" style="width: 40%;">
          <div>
            <div class="repoter-day__block-child-title">会议数据统计</div>
            <!-- 表格区域 -->
            <el-table tooltip-effect="dark"
                      stripe
                      border
                      style="width: 100%;"
                      :data="tableDataConfSummary"
                      :empty-text="emptyText"
            >
              <el-table-column show-overflow-tooltip prop="name" label="">
              </el-table-column>
              <el-table-column show-overflow-tooltip prop="value" label="数量（个）">
              </el-table-column>
              <el-table-column show-overflow-tooltip prop="dailyRingRatio" label="日环比增长率">
              </el-table-column>
            </el-table>
            <!-- 表格区域end -->
          </div>

          <div style="margin-top: 20px;">
            <div class="repoter-day__block-child-title">
              终端概况
            </div>
            <!-- 表格区域 -->
            <el-table tooltip-effect="dark"
                      stripe
                      border
                      style="width: 100%;"
                      :data="tableDataTerminalsPeak"
                      :empty-text="emptyText"
            >
              <el-table-column show-overflow-tooltip prop="name" label="">
              </el-table-column>
              <el-table-column show-overflow-tooltip prop="value" label="数量（个）">
              </el-table-column>
              <el-table-column show-overflow-tooltip prop="dailyRingRatio" label="日环比增长率">
              </el-table-column>
            </el-table>
            <!-- 表格区域end -->
          </div>

        </div>
        <div class="repoter-day__block-child" style="width: 60%;padding-bottom: 10px;">
          <div class="repoter-day__block-child-title">企业启用/停用统计</div>
          <div style="width: 100%;height: 120px;">
            <ReportDayChart ChartName="reportDayCompaniesEnablePercent"
                            ChartID="reportDayCompaniesEnablePercent"
                            :params="globalParams"></ReportDayChart>
          </div>
          <div class="repoter-day__block-child-title">账号启用/停用统计</div>
          <div style="width: 100%;height: 120px;">
            <ReportDayChart ChartName="reportDayTerminalsEnablePercent"
                            ChartID="reportDayTerminalsEnablePercent"
                            :params="globalParams"></ReportDayChart>
          </div>
        </div>

        <div class="repoter-day__block-child" style="width: 100%;padding: 30px 10px;">
          <div class="repoter-day__block-child-title">当日会议体验较差TOP</div>
          <!-- 表格区域 -->
          <el-table tooltip-effect="dark"
                    stripe
                    border
                    style="width: 100%;"
                    :data="tableDataConfBadTop"
                    :empty-text="emptyText"
          >
            <el-table-column show-overflow-tooltip type="index" label="序号" width="50">
            </el-table-column>
            <el-table-column show-overflow-tooltip prop="conf_name" label="会议名">
            </el-table-column>
            <el-table-column show-overflow-tooltip prop="conf_e164" label="会议号">
            </el-table-column>
            <el-table-column show-overflow-tooltip prop="quality_desc" label="会议质量">
            </el-table-column>
            <el-table-column show-overflow-tooltip prop="terminal_count" label="参会终端数">
            </el-table-column>
          </el-table>
          <!-- 表格区域end -->
        </div>
      </div>
      <!--会议概况概况 end-->

      <!--资源统计概况-->
      <div class="repoter-day__block" style="width: 100%;height: 464px;">
        <div class="repoter-day__block-title">转发资源统计</div>
        <div style="width: 100%;height: 420px;">
          <ReportDayChart ChartName="reportDayTransmitResource"
                          ChartID="reportDayTransmitResource"
                          :params="globalParams"></ReportDayChart>
        </div>
      </div>
      <!--资源统计概况 end-->

      <!--服务器性能统计概况-->
      <div class="repoter-day__block" style="width: 100%;padding-bottom: 20px;margin-top: 30px;">
        <div class="repoter-day__block-title">
          服务器性能概况
        </div>
        <div class="repoter-day__block-child" style="width: 33.3%;">
          <div class="repoter-day__block-child-title">CPU使用率TOP</div>
          <!-- 表格区域 -->
          <el-table tooltip-effect="dark"
                    stripe
                    border
                    style="width: 100%;"
                    :data="tableDataTopCPU"
                    :empty-text="emptyText"
          >
            <el-table-column show-overflow-tooltip type="index" label="序号" width="50">
            </el-table-column>
            <el-table-column show-overflow-tooltip prop="name" label="服务器名">
            </el-table-column>
            <el-table-column show-overflow-tooltip prop="value" label="CPU使用率">
            </el-table-column>
          </el-table>
          <!-- 表格区域end -->
        </div>
        <div class="repoter-day__block-child" style="width: 33.3%;">
          <div class="repoter-day__block-child-title">MEM使用率TOP</div>
          <!-- 表格区域 -->
          <el-table tooltip-effect="dark"
                    stripe
                    border
                    style="width: 100%;"
                    :data="tableDataTopMEM"
                    :empty-text="emptyText"
          >
            <el-table-column show-overflow-tooltip type="index" label="序号" width="50">
            </el-table-column>
            <el-table-column show-overflow-tooltip prop="name" label="服务器名">
            </el-table-column>
            <el-table-column show-overflow-tooltip prop="value" label="MEM使用率">
            </el-table-column>
          </el-table>
          <!-- 表格区域end -->
        </div>
        <div class="repoter-day__block-child" style="width: 33.3%;">
          <div class="repoter-day__block-child-title">分区使用率TOP</div>
          <!-- 表格区域 -->
          <el-table tooltip-effect="dark"
                    stripe
                    border
                    style="width: 100%;"
                    :data="tableDataTopDisk"
                    :empty-text="emptyText"
          >
            <el-table-column show-overflow-tooltip type="index" label="序号" width="50">
            </el-table-column>
            <el-table-column show-overflow-tooltip prop="name" label="服务器名">
            </el-table-column>
            <el-table-column show-overflow-tooltip prop="mount_point" label="分区名称">
            </el-table-column>
            <el-table-column show-overflow-tooltip prop="value" label="分区使用率">
            </el-table-column>
          </el-table>
          <!-- 表格区域end -->
        </div>
      </div>
      <!--服务器性能统计概况 end-->

      <!--告警统计概况-->
      <div class="repoter-day__block" style="width: 100%;height: 490px;">
        <div class="repoter-day__block-title">告警统计</div>
        <div class="repoter-day__block-child" style="width: 50%;">
          <div class="repoter-day__block-child-title">服务器告警统计</div>
          <div style="width: 100%;height: 300px;">
            <ReportDayChart ChartName="reportDayAlarmStatisticsDev"
                            ChartID="reportDayAlarmStatisticsDev"
                            :params="globalParams"></ReportDayChart>
          </div>
        </div>
        <div class="repoter-day__block-child" style="width: 50%;">
          <div class="repoter-day__block-child-title">终端告警统计</div>
          <div style="width: 100%;height: 300px;">
            <ReportDayChart ChartName="reportDayAlarmStatisticsMt"
                            ChartID="reportDayAlarmStatisticsMt"
                            :params="globalParams"></ReportDayChart>
          </div>
        </div>
      </div>
      <!--告警统计概况 end-->
    </div>
    <!--会议数据内容区 end-->

    <!--会议室数据内容区-->
    <div v-if="activeTab==='RepoterDayConfRoom'" class="repoter-day__content">
      <!--会议概况概况-->
      <div class="repoter-day__block" style="width: 100%;padding-bottom: 20px;">
        <div class="repoter-day__block-title">
          会议信息
        </div>
        <!-- 表格区域 -->
        <el-table tooltip-effect="dark"
                  stripe
                  border
                  style="width: 100%;"
                  :data="tableDataDayConfRoom"
                  :empty-text="emptyText"
        >
          <el-table-column show-overflow-tooltip type="index" label="序号" width="50">
          </el-table-column>
          <el-table-column show-overflow-tooltip prop="conf_name" label="会议名称" sortable>
          </el-table-column>
          <el-table-column show-overflow-tooltip prop="conf_e164" width="120" label="会议号" sortable>
          </el-table-column>
          <el-table-column show-overflow-tooltip prop="domain_name" label="用户域名称" sortable>
          </el-table-column>
          <el-table-column show-overflow-tooltip prop="resolution" width="120" label="媒体分辨率" sortable>
          </el-table-column>
          <el-table-column show-overflow-tooltip prop="bitrate" width="150" label="会议码率（kbs）" sortable>
          </el-table-column>
          <el-table-column show-overflow-tooltip prop="frame_rate" width="150" label="会议帧率（fps）" sortable>
          </el-table-column>
          <el-table-column show-overflow-tooltip prop="start_time" label="会议开始时间" sortable>
          </el-table-column>
          <el-table-column show-overflow-tooltip prop="end_time" label="会议结束时间" sortable>
          </el-table-column>
          <el-table-column show-overflow-tooltip prop="terminal_count" width="120" label="入会终端数" sortable>
          </el-table-column>

        </el-table>
        <!-- 表格区域end -->
      </div>
    </div>
    <!--会议室数据内容区 end-->
  </div>
</template>

<script>
  export default {
    name: "DayRepoterPlatfrom",
    components: {
      KdTabCommon: () => import('@/components/common/KdTabCommon.vue'),
      ReportDayChart: () => import('@/view/reporter/ReportDayChart.vue'),
      MonitorMeetingInfoConfEventSurvey: () => import('@/components/monitor/MonitorMeetingInfoConfEventSurvey.vue'),
    },
    computed: {
      globalParams() {
        let date = new Date(this.datePickerRepoterDay).format('Y-m-d')
        return {
          domain: this.optionSelectedDomain,
          date: date
        }
      },
    },
    watch: {
      globalParams(newVal) {
        this.init()
      },
    },
    data() {
      return {
        activeTab: 'RepoterDayConf',
        tabList: [['RepoterDayConf', '会议数据'],
          ['RepoterDayConfRoom', '会议信息'],],
        // ['RepoterDayRecorder','问题跟踪'],

        // 表格无数据展示内容
        emptyText: "当日无数据",

        // 时间选择器组件数据
        datePickerRepoterDay: '',
        pickerOptions: {
          disabledDate: this.timePickerLimit
        },
        // 时间选择器组件数据 end

        optionSelectedDomain: '科达平台域',
        optionsDomain: ['科达平台域', '电信平台域'],

        // 会议概况数据
        tableDataConfSummary: [],
        tableDataTerminalsPeak: [],
        tableDataConfBadTop: [],
        // 会议概况数据 end

        // 服务器性能概况
        tableDataTopCPU: [],
        tableDataTopMEM: [],
        tableDataTopDisk: [],
        // 服务器性能概况 end

        // 会议室数据 activeTab = 'RepoterDayConfRoom'
        tableDataDayConfRoom: [],
      }
    },
    methods: {
      tabChange(val) {
        this.activeTab = val
      },

      // 时间选择器组件
      datePickerChange(time) {
        // console.log(new Date(time).format('Y-m-d'))
      },
      timePickerLimit(time) {
        return time.getTime() > (Date.now() - 86400000);
      },
      // 时间选择器组件 end

      // 会议概况
      // 获取会议数量
      async getTableDataConfSummary() {
        // 请求前相关数据初始化
        this.tableDataDayConfRoom = []
        this.tableDataConfSummary = []

        // 获取会议并发峰值
        let p = {
          date: this.globalParams.date,
          type: 'concurrent_confs_peak_num'
        }
        let res = await this.$api.getChartData.getReporterDayCommon(p)
        if (!res) return false

        let concurrentNum = res.report_data
        // 获取会议总数
        p.type = 'total_confs'
        res = await this.$api.getChartData.getReporterDayCommon(p)
        this.tableDataDayConfRoom = res.report_data

        this.tableDataConfSummary = [
          {name: '当日会议并发数峰值', value: concurrentNum},
          {name: '当日会议总数', value: this.tableDataDayConfRoom.length},
        ]

        // yp__start
        // 日环比增长率
        // 会议并发峰值环比
        let beforeP = {
          date: new Date(this.datePickerRepoterDay - 24 * 60 * 60 * 1000).format('Y-m-d'),
          type: 'concurrent_confs_peak_num'
        }
        // 取得前一天会议并发峰值
        let beforeRes = await this.$api.getChartData.getReporterDayCommon(beforeP)
        if (beforeRes) {
          let beforeConcurrentNum = beforeRes.report_data
          if (beforeConcurrentNum === 0) {
            var dailyRingRatio = '昨日数据为0'
          } else {
            var dailyRingRatio = (concurrentNum - beforeConcurrentNum) / beforeConcurrentNum
            dailyRingRatio = (dailyRingRatio * 100).toFixed(2) + '%'
          }
        } else {
          var dailyRingRatio = '昨日无数据'
        }


        // console.log(dailyRingRatio)
        this.tableDataConfSummary = [
          {name: '当日会议并发数峰值', value: concurrentNum, dailyRingRatio: dailyRingRatio},
          {name: '当日会议总数', value: this.tableDataDayConfRoom.length},
        ]
        // 计算会议并发峰值环比
        // 会议总数环比
        // 取得前一天会议总数
        beforeP = {
          date: new Date(this.datePickerRepoterDay - 24 * 60 * 60 * 1000).format('Y-m-d'),
          type: 'total_confs'
        }
        beforeRes = await this.$api.getChartData.getReporterDayCommon(beforeP)
        if (beforeRes) {
          let beforeConcurrentNum = beforeRes.report_data.length
          // console.log(beforeConcurrentNum)
          // 计算会议并发峰值环比
          if (beforeConcurrentNum === 0) {
            var total_confs = '昨日数据为0'
          } else {
            var total_confs = (this.tableDataDayConfRoom.length - beforeConcurrentNum) / beforeConcurrentNum
            total_confs = (total_confs * 100).toFixed(2) + '%'
          }
        } else {
          var total_confs = '昨日无数据'
        }

        this.tableDataConfSummary = [
          {name: '当日会议并发数峰值', value: concurrentNum, dailyRingRatio: dailyRingRatio},
          {name: '当日会议总数', value: this.tableDataDayConfRoom.length, dailyRingRatio: total_confs},
        ]
        // yp__end


      },
      // 获取终端峰值概况
      async getTableDataTerminalsPeak() {
        // 请求前相关数据初始化
        this.tableDataTerminalsPeak = []

        // 获取终端在线峰值
        let p = {
          date: this.globalParams.date,
          type: 'online_terminals_peak_num'
        }
        let res = await this.$api.getChartData.getReporterDayCommon(p)
        if (!res) return false
        let onlineNum = res.report_data
        // 获取终端呼叫峰值
        p.type = 'calls_terminals_peak_num'
        res = await this.$api.getChartData.getReporterDayCommon(p)
        if (!res) return false
        let callsNum = res.report_data

        this.tableDataTerminalsPeak = [
          {name: '当日终端在线峰值', value: onlineNum},
          {name: '当日终端呼叫峰值', value: callsNum},
        ]


        // yp__start
        // 日环比增长率
        // 终端在线峰值环比
        let beforeP = {
          date: new Date(this.datePickerRepoterDay - 24 * 60 * 60 * 1000).format('Y-m-d'),
          type: 'online_terminals_peak_num'
        }
        let beforeRes = await this.$api.getChartData.getReporterDayCommon(beforeP)
        // 取得前一天终端在线峰值
        if (beforeRes) {
          let beforeOnlineNum = beforeRes.report_data
          if (beforeOnlineNum === 0) {
            var dailyRingRatio = '昨日数据为0'
          } else {
            var dailyRingRatio = (onlineNum - beforeOnlineNum) / beforeOnlineNum
            dailyRingRatio = (dailyRingRatio * 100).toFixed(2) + '%'
          }
        } else {
          var dailyRingRatio = '昨日无数据'
        }

        this.tableDataTerminalsPeak = [
          {name: '当日终端在线峰值', value: onlineNum, dailyRingRatio: dailyRingRatio},
          {name: '当日终端呼叫峰值', value: callsNum},
        ]
        // 计算终端呼叫峰值环比
        // 终端呼叫峰值环比
        // 取得前一天终端呼叫峰值
        beforeP = {
          date: new Date(this.datePickerRepoterDay - 24 * 60 * 60 * 1000).format('Y-m-d'),
          type: 'calls_terminals_peak_num'
        }
        beforeRes = await this.$api.getChartData.getReporterDayCommon(beforeP)
        if (beforeRes) {
          let beforeCallsNum = beforeRes.report_data
          // console.log(beforeCallsNum)
          // 计算终端呼叫峰值环比
          if (beforeCallsNum === 0) {
            var callsNumB = '昨日数据为0'
          } else {
            var callsNumB = (callsNum - beforeCallsNum) / beforeCallsNum
            callsNumB = (callsNumB * 100).toFixed(2) + '%'
          }
        } else {
          var callsNumB = '昨日无数据'
        }

        this.tableDataTerminalsPeak = [
          {name: '当日终端在线峰值', value: onlineNum, dailyRingRatio: dailyRingRatio},
          {name: '当日终端呼叫峰值', value: callsNum, dailyRingRatio: callsNumB},
        ]
        // yp__end


      },
      // 获取会议质量
      async getTableDataConfBadTop() {
        // 请求前相关数据初始化
        this.tableDataConfBadTop = []

        // 获取会议并发峰值
        let p = {
          date: this.globalParams.date,
          type: 'bad_experience_top_confs'
        }
        let res = await this.$api.getChartData.getReporterDayCommon(p)
        if (!res) return false
        let data = res.report_data

        this.tableDataConfBadTop = data
      },
      // 会议概况 end

      // 服务器概况
      async getDataTOPCpu() {
        // 请求前相关数据初始化
        this.tableDataTopCPU = []

        let p = {
          date: this.globalParams.date,
          type: 'cpu_top_machines'
        }
        let res = await this.$api.getChartData.getReporterDayCommon(p)
        if (!res) return false
        let data = res.report_data
        data.forEach(i => i.value = (i.value * 100).toFixed(0) + '%')

        this.tableDataTopCPU = data
      },
      async getDataTOPMem() {
        // 请求前相关数据初始化
        this.tableDataTopMEM = []

        let p = {
          date: this.globalParams.date,
          type: 'mem_top_machines'
        }
        let res = await this.$api.getChartData.getReporterDayCommon(p)
        if (!res) return false
        let data = res.report_data
        data.forEach(i => i.value = (i.value * 100).toFixed(0) + '%')

        this.tableDataTopMEM = data
      },
      async getDataTOPDisk() {
        // 请求前相关数据初始化
        this.tableDataTopDisk = []

        let p = {
          date: this.globalParams.date,
          type: 'disk_top_machines'
        }
        let res = await this.$api.getChartData.getReporterDayCommon(p)
        if (!res) return false
        let data = res.report_data
        data.forEach(i => i.value = (i.value * 100).toFixed(0) + '%')

        this.tableDataTopDisk = data
      },
      // 服务器概况 end
      init() {
        this.getTableDataConfSummary()
        this.getTableDataConfBadTop()
        this.getTableDataTerminalsPeak()
        this.getDataTOPCpu()
        this.getDataTOPMem()
        this.getDataTOPDisk()
      },
    },
    mounted() {
      this.init()
    },
    created() {
      let timestamp = new Date() - 86400000;
      this.datePickerRepoterDay = timestamp
    },
  }
</script>

<style>
  .repoter-day-conf {
    padding: 20px;
  }

  .repoter-day__content {
    padding: 10px;
    /*height: 350px;*/
  }

  .repoter-day__block {
    background: #232629;
    margin-bottom: 20px;
    box-sizing: border-box;
    font-size: 0px;

  }

  .repoter-day__block-title {
    width: 100%;
    color: #9ca9b1;
    font-size: 18px;
    font-weight: 700;
    text-align: center;
    padding: 10px 0px;
    border-bottom: #1e2224 3px solid;
  }

  .repoter-day__block-child {
    padding: 0px 10px;
    box-sizing: border-box;
    display: inline-block;
    vertical-align: top;
    font-size: 14px;
    /*box-shadow:0px 2px 10px #23BFF9 inset;*/
    /*background: linear-gradient(to left, #299dff, #299dff) left top no-repeat,*/
    /*linear-gradient(to bottom, #299dff, #299dff) left top no-repeat,*/
    /*linear-gradient(to left, #299dff, #299dff) right top no-repeat,*/
    /*linear-gradient(to bottom, #299dff, #299dff) right top no-repeat,*/
    /*linear-gradient(to left, #299dff, #299dff) left bottom no-repeat,*/
    /*linear-gradient(to bottom, #299dff, #299dff) left bottom no-repeat,*/
    /*linear-gradient(to left, #299dff, #299dff) right bottom no-repeat,*/
    /*linear-gradient(to left, #299dff, #299dff) right bottom no-repeat;*/
    /*background-size: 3px 20px, 20px 3px, 3px 20px, 20px 3px;*/
  }

  .repoter-day__block-child-title {
    width: 100%;
    color: #9ca9b1;
    font-size: 16px;
    text-align: center;
    padding: 10px 0px;
  }

  .repoter-day-conf .el-table .caret-wrapper {
    height: 20px;
    border-color: #c2c2c2 transparent transparent;
  }

  .repoter-day-conf .el-table .sort-caret.ascending {
    top: 0px;
    margin-bottom: 2px;
    /*border-color: transparent transparent #c2c2c2;*/
  }

  .repoter-day-conf .el-table .sort-caret {
    position: unset;
    border-width: 4px;

  }

  .test--line {
    width: 100%;
    height: 2px;
    background: linear-gradient(
      to right,
      rgba(0, 0, 0, 0) 0%,
      rgba(0, 0, 0, 0) 10%,
      rgba(94, 185, 239, 0.3) 20%,
      rgba(94, 185, 239, 0.4) 30%,
      rgba(94, 185, 239, 0.5) 40%,
      rgba(94, 185, 239, 0.8) 50%,
      rgba(94, 185, 239, 0.5) 60%,
      rgba(94, 185, 239, 0.4) 70%,
      rgba(94, 185, 239, 0.3) 80%,
      rgba(0, 0, 0, 0) 90%,
      rgba(0, 0, 0, 0) 100%)
  }
</style>
