<template>
  <div class="childpage-request-detail">
    <div class="button-back " style="">
      <el-button icon="ops-icons-bg icon-arrow-circle-left" @click="back" circle></el-button>
      <span>详情</span>
    </div>
    <div class="head-right">
      <el-button @click="exportTable" v-loading.fullscreen.lock="fullscreenLoading">导出</el-button>
    </div>
    <div style="padding: 34px 20px 0px 53px">
      <div style="padding-left: 7px;margin: 5px 0px;">
        <KdTabCommon :tab-list="tabList"
                     :active-tab="activeTab"
                     class-name="tab-request-detail"
                     @tab-change="tabChange"></KdTabCommon>
      </div>
      <div class="area-filter">
        <SelectPlatformDomain @change="changeFilter($event,'selectPlatformDomain')"
                              @loadSelectedOption="loadSelectedOption($event,'selectPlatformDomain')"
                              :filterDomainType=1
                              :hasOptionAll=true
                              :selectedMoidPlatform="defaultSelected.selectedMoidPlatform"
                              :selectedMoidMachineRoom="defaultSelected.selectedMoidMachineRoom"
                              showSelectMachineRoom></SelectPlatformDomain>
        <!--<SelectTimeRange @loadSelectedOption="loadSelectedOption($event,'selectTimeRange')"
                         @change="changeFilter($event,'selectTimeRange')"
                         :hasTimer=false></SelectTimeRange>-->
        <el-date-picker
          style="width: 322px;margin-right: 7px;vertical-align: top;"
          v-model="datePickerTimeRange"
          type="datetimerange"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          popper-class="theme-dark "
          value-format="timestamp"
          format="yyyy-MM-dd HH:mm"
          :default-time="['00:00:00', '23:59:59']"
          range-separator=""
          class="clear-close-icon"
          prefix-icon="ops-icons-bg icon-calendar"
          :clearable=false
          @change="datePickerChange"
        >
        </el-date-picker>


        <!--耗时选择-->
        <el-select popper-class="theme-dark"
                   v-model="optionSelectedSlowResponses"
                   @change="changeFilter($event,'selectSlowResponses')"
                   v-if="showOtherSelect.selectSlowResponses"
                   placeholder="请选择耗时">
          <el-option
            v-for="item in optionsSlowResponses"
            :key="item.value"
            :label="item.name"
            :value="item.value"
          >
          </el-option>
        </el-select>

        <!--客户端的选择-->
        <el-select popper-class="theme-dark"
                   v-model="optionSelectedWebEngine"
                   @change="changeFilter($event,'selectWebEngine')"
                   v-if="showOtherSelect.selectWebEngine"
                   placeholder="请选择耗时">
          <el-option
            v-for="item in optionsWebEngine"
            :key="item.value"
            :label="item.name"
            :value="item.value"
          >
          </el-option>
        </el-select>

        <!--状态码-->
        <el-select popper-class="theme-dark"
                   v-model="optionSelectedHTTPCode"
                   @change="changeFilter($event,'selectHTTPCode')"
                   v-if="showOtherSelect.selectHTTPCode"
                   placeholder="请选择耗时">
          <el-option
            v-for="item in optionsHTTPCode"
            :key="item.value"
            :label="item.name"
            :value="item.value"
          >
          </el-option>
        </el-select>

        <el-input clearable
                  v-model='inputSearch'
                  style="margin-right: 10px;width: 290px;"
                  @keyup.enter.native="handleInputSearch('searchInput')"
                  @blur="handleInputSearch('searchInput')"
                  @clear="handleInputSearch('searchInput')"
                  v-if="showOtherSelect.searchInput"
                  placeholder="请输入请求URL搜索"
                  maxlength="100">
        </el-input>
        <el-button style="vertical-align: 1px;" @click="refreshPage" :disabled="refreshButtonDisabled">搜索</el-button>
      </div>
      <div class="area-content">
        <!-- 表格区域 -->
        <div class="area-table" style="margin-top: 18px;padding-left: 7px;">
          <el-table tooltip-effect="dark"
                    stripe
                    border
                    style="width: 100%;"
                    :data="tableData"
                    @row-dblclick="tableRowDblClick"
                    v-loading="loadingTableData"
                    element-loading-background="rgba(0, 0, 0, 0.5)"
          >
            <el-table-column show-overflow-tooltip type="index" label="序号" width="56">
            </el-table-column>
            <el-table-column show-overflow-tooltip
                             v-for="item in tableColumn"
                             :prop="item.prop"
                             :label="item.title"
                             :key="item.prop"
                             :width="item.width">
            </el-table-column>
            <el-table-column label='操作' width="100px" v-if='showTableButton.detail'>
              <template slot-scope="scope">
                <button type="button" class="button-host-info" @click="showTableButton.detailMethod(scope.row)">
                  <span style="text-decoration: underline;">详情</span>
                </button>
              </template>
            </el-table-column>
          </el-table>
        </div>
        <!-- 表格区域end -->
      </div>
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
    </div>
  </div>
</template>

<script>
  export default {
    components: {
      KdTabCommon: () => import('@/components/common/KdTabCommon.vue'),
      SelectPlatformDomain: () => import('@/components/common/SelectPlatformDomain.vue'),
      SelectTimeRange: () => import('@/components/common/SelectTimeRange.vue'),
      KdPagination: () => import('@/components/common/KdPagination.vue'),
    },
    name: "StatsAppRequest",
    props: {
      tab: String,
      defaultSelected: Object,
    },
    data() {
      return {
        activeTab: 'requestsIP',
        tabList: [
          ['requestsDetail', '请求详情'],
          ['requestsIP', '请求IP统计'],
          ['requestsSlowResponses', '慢响应统计'],
          ['requestURL', '请求URL统计'],
          ['webEngine', '客户端统计'],
          ['errRequest', '异常统计'],
        ],

        fullscreenLoading: false, //增加导出交互
        refreshButtonDisabled: false,
        // table data
        tableColumn: [],
        tableData: [],
        showTableButton: {},
        loadingTableData: false,

        // filter 相关数据
        filterComponentLoad: {
          selectPlatformDomain: false,
          // selectTimeRange: false
        },
        filterParams: {},
        otherSelectedParams: {}, // 其他可选的selected参数

        datePickerTimeRange: null,
        // select 相关数据
        showOtherSelect: {},
        // 慢响应 耗时
        optionSelectedSlowResponses: 'all',
        optionsSlowResponses: [{
          name: '全部耗时',
          value: 'all'
        }, {
          name: '耗时>1s',
          value: 1
        }, {
          name: '耗时>2s',
          value: 2
        }, {
          name: '耗时>3s',
          value: 3
        }, {
          name: '耗时>5s',
          value: 5
        }, {
          name: '耗时>8s',
          value: 8
        }, {
          name: '耗时>10s',
          value: 10
        },],

        // 客户端类型
        optionSelectedWebEngine: 'all',
        optionsWebEngine: [{
          name: '全部客户端',
          value: 'all'
        }, {
          name: '谷歌',
          value: 'chrome'
        }, {
          name: '火狐',
          value: 'firefox'
        }, {
          name: 'IE',
          value: 'ie'
        }, {
          name: '摩云',
          value: 'movision'
        }, {
          name: '其他',
          value: 'other'
        },],

        // http code
        optionSelectedHTTPCode: 'all',
        optionsHTTPCode: [{
          name: '全部状态码',
          value: 'all'
        }, {
          name: '1xx',
          value: '1xx'
        }, {
          name: '2xx',
          value: '2xx'
        }, {
          name: '3xx',
          value: '3xx'
        }, {
          name: '4xx',
          value: '4xx'
        }, {
          name: '5xx',
          value: '5xx'
        },],
        // select 相关数据 end
        inputSearch: '', // 搜索 input

        pageConf: {
          requestsIP: {
            name: '请求IP统计',
            customModule: false,
            url: ['common', '/statistics/requests/ip/'],
            renderMethod: 'common',
            tableConf: [
              {prop: "url", title: "IP"},
              {prop: "data", title: "数量", width: "100"},
            ],
          },
          requestsSlowResponses: {
            name: '慢响应统计',
            customModule: false,
            url: ['common', '/statistics/requests/slow_responses/'],
            renderMethod: 'common',
            otherSelect: ['selectSlowResponses'],
            defaultSelect: {
              optionSelectedSlowResponses: 1,
            },
            showTableButton: {
              detail: true,
              detailMethod: this.requestsSlowResponsesDetail
            },
            tableConf: [
              {prop: "url", title: "请求URL"},
              {prop: "data", title: "数量", width: "100"},
            ],
          },
          requestURL: {
            name: '请求URL统计',
            customModule: false,
            url: ['common', '/statistics/requests/urls/'],
            renderMethod: 'common',
            tableConf: [
              {prop: "url", title: "请求URL"},
              {prop: "data", title: "数量", width: "100"},
            ],
          },
          webEngine: {
            name: '客户端统计',
            customModule: false,
            url: ['common', '/statistics/requests/clients/'],
            renderMethod: 'common',
            otherSelect: ['selectWebEngine'],
            tableConf: [
              {prop: "url", title: "客户端信息"},
              {prop: "data", title: "数量", width: "100"},
            ],
          },
          errRequest: {
            name: '异常统计',
            customModule: false,
            url: ['common', '/statistics/requests/errors/'],
            renderMethod: 'common',
            showTableButton: {
              detail: true,
              detailMethod: this.errRequestDetail
            },
            tableConf: [
              {prop: "url", title: "请求URL"},
              {prop: "data", title: "数量", width: "100"},
              {prop: "status", title: "状态码", width: "120"},
              {prop: "upstream_status", title: "upstream状态码", width: "120"},
            ],
          },
          requestsDetail: {
            name: '请求详情',
            customModule: false,
            url: ['requestsDetail', '/statistics/requests/errors/'],
            renderMethod: 'requestsDetail',
            otherSelect: ['selectHTTPCode', 'selectSlowResponses', 'searchInput'],
            defaultSelect: {
              optionSelectedSlowResponses: 'all',
            },
            tableConf: [
              {prop: "@timestamp", title: "时间", width: "170"},
              {prop: "remote_addr", title: "源IP", width: "120"},
              {prop: "request_uri", title: "请求URL"},
              {prop: "uri", title: "响应URL", width: "190"},
              {prop: "request_time", title: "响应时间/ms", width: "100"},
              {prop: "status", title: "状态码", width: "120"},
              {prop: "upstream_status", title: "upstream状态码", width: "120"},
              {prop: "body_bytes_sent", title: "请求大小/Kbytes", width: "120"},
            ],
          },
        },
        // 分页数据
        currentPage: 1,
        pageSize: 15,
        pageTotal: 0,
      }
    },
    methods: {
      back() {
        this.$emit('back', true)
      },
      // tab变化
      tabChange(val) {
        this.activeTab = val
        this.currentPage = 1
        this.pageChange(val)
        this.renderInit()
      },

      // 表格双击，详情跳转函数 start
      tableRowDblClick(row, column, event){
        if(this.showTableButton.detail) this.showTableButton.detailMethod(row)
      },
      errRequestDetail(row) {
        let key = 'requestsDetail'
        let customSelect = {
          inputSearch:row.url.slice(0,99)
        }
        this.activeTab = key
        this.currentPage = 1
        this.pageChange(key,customSelect)
        this.renderInit()
      },
      requestsSlowResponsesDetail(row){
        let key = 'requestsDetail'
        let customSelect = {
          inputSearch:row.url.slice(0,99),
          optionSelectedSlowResponses:this.optionSelectedSlowResponses
        }
        this.activeTab = key
        this.currentPage = 1
        this.pageChange(key,customSelect)
        this.renderInit()
      },
      // 表格双击，详情跳转函数 end

      // 页面变化函数
      pageChange(key, customSelect) {
        this.showOtherSelect = {}
        if (this.pageConf[key].defaultSelect) {
          for (let k in this.pageConf[key].defaultSelect) {
            this[k] = this.pageConf[key].defaultSelect[k]  //默认参数
          }
        }
        if (customSelect) {
          for (let k in customSelect) {
            this[k] = customSelect[k]  //自定义参数
          }
        }
        if (this.pageConf[key].otherSelect) {
          let defaultSelected = {
            module: 'module', //暂时未用
            selectHTTPCode: this.optionSelectedHTTPCode,
            selectSlowResponses: this.optionSelectedSlowResponses,
            selectWebEngine: this.optionSelectedWebEngine,
            searchInput: this.inputSearch,
          }
          this.pageConf[key].otherSelect.forEach(item => {
            this.$set(this.showOtherSelect, item, true)
            this.$set(this.otherSelectedParams, item, defaultSelected[item])
          })
        }
        this.tableColumn = this.pageConf[key].tableConf
        this.showTableButton = this.pageConf[key].showTableButton || {}
        this.tableData = []
      },
      // 过滤项改变触发的函数
      datePickerChange(val) {
        if (val) {
          let timeParams = {
            select: 'custom',
            dateRange: val
          }
          this.changeFilter(timeParams, 'selectTimeRange')
        } else { //若清空，则赋值null
          this.$set(this.filterParams, 'dateRange', val)
        }
      },
      refreshPage() {
        this.refreshButtonDisabled = true
        this.currentPage = 1
        this.renderInit()
        setTimeout(() => this.refreshButtonDisabled = false, 1000)
      },

      handleInputSearch(k) {
        this.changeFilter(this.inputSearch, k)
      },
      changeFilter(val, k) {
        this.setFilterParams(val, k)
        let loadingFlag = Object.values(this.filterComponentLoad).includes(false)
        if (!loadingFlag) {
          this.renderInit()
        }
      },
      // 用于处理所有过滤条件初始化完成后，做第一次带参请求
      loadSelectedOption(val, k) {
        this.setFilterParams(val, k)
        this.$set(this.filterComponentLoad, k, true)
        let loadingFlag = Object.values(this.filterComponentLoad).includes(false)
        if (!loadingFlag) {
          this.renderInit()
        }
      },
      setFilterParams(val, k) {
        if (k === 'selectPlatformDomain') {
          let domainMoid = val.domainMoid === 'all' ? '' : val.domainMoid
          let roomMoid = val.roomMoid === 'all' ? '' : val.roomMoid
          this.$set(this.filterParams, 'domainMoid', domainMoid)
          this.$set(this.filterParams, 'roomMoid', roomMoid)
        } else if (k === 'selectTimeRange') {
          this.$set(this.filterParams, 'timeSelect', val.select)
          this.$set(this.filterParams, 'dateRange', val.dateRange)
        } else {
          this.$set(this.otherSelectedParams, k, val)
        }
      },

      // 分页变化
      pageHandleCurrentChange(val) {
        this.currentPage = val
        this.renderInit()
      },
      // 渲染函数,负责将当前展示项用不同的方法渲染
      renderInit() {
        let renderTypeMethod = {
          'common': this.renderCommon, //常规渲染
          'requestsDetail': this.renderRequestsDetail,
        };
        let gloablConf = {} //用于配置默认或全局的参数
        let method = this.pageConf[this.activeTab].renderMethod
        this.judgeTimeRange()
        let gParams = {
          start_time: this.filterParams.dateRange[0],
          end_time: this.filterParams.dateRange[1],
          platform_moid: this.filterParams.domainMoid,
          room_moid: this.filterParams.roomMoid,
          start: (this.currentPage - 1) * this.pageSize,
          count: this.pageSize,
        }

        // 如果有其他的 select 选项则加进gParams
        if (this.pageConf[this.activeTab].otherSelect) {
          let apiKey = {  //api支持的所有筛选条件
            module: 'module', //暂时未用
            selectHTTPCode: 'status_code',
            selectSlowResponses: 'slow_time_threshold',
            selectWebEngine: 'client',
            searchInput: 'key',
          }
          this.pageConf[this.activeTab].otherSelect.forEach(i =>
            gParams[apiKey[i]] = this.otherSelectedParams[i] && this.otherSelectedParams[i] !== 'all'
              ? this.otherSelectedParams[i] : '')
        }
        // console.log(gParams)
        if (method) renderTypeMethod[method](gloablConf, this.activeTab, gParams)
      },

      async renderCommon(gloablConf, key, gParams) {
        this.loadingTableData = true

        let params = this.pageConf[key].staticUrlParams
        params = {...params, ...gParams}

        let method = this.pageConf[key].url[0]
        let data = []
        // 处理数据形成表格数据
        if (method === 'common') {
          let res = await this.$api.appReuqestData.requestTopData(this.pageConf[key].url[1], params)
          this.pageTotal = res.total
          let dataList = res.info || []
          if (dataList.length) {
            data = dataList.map((item, indexItem) => {
              let tempDict = {}
              this.pageConf[key].tableConf.forEach((i, indexI) => {
                let prop = i.prop
                tempDict[prop] = item[indexI]
              })
              return tempDict
            });
          }
        } else if (method === 'webEngine') {
          let res = await this.$api.getChartData.getAppRequestWebEngine(params)
          let dataList = res.info ? res.info[0].data : []
          if (dataList && dataList.length) {
            data = dataList.map((item, indexItem) => {
              let tempDict = {}
              item.forEach((i, indexI) => {
                let prop = this.pageConf[key].tableConf[indexI].prop
                tempDict[prop] = i
              })
              return tempDict
            });
          }
        }
        ;
        // 处理数据形成表格数据 end
        this.loadingTableData = false
        this.tableData = data
      },

      async renderRequestsDetail(gloablConf, key, gParams) {
        this.loadingTableData = true

        let params = this.pageConf[key].staticUrlParams
        params = {...params, ...gParams}

        let data = []
        // 处理数据形成表格数据
        let res = await this.$api.appReuqestData.requestDetail(params)
        if (res) {
          for (let i of res.info) {
            i["@timestamp"] = i["@timestamp"] ? new Date(i["@timestamp"]).format('Y-m-d H:i:s') : i["@timestamp"]
            i.body_bytes_sent = (i.body_bytes_sent / 1000).toFixed(2)
            i.request_time = i.request_time * 1000
          }

          this.pageTotal = res.total
          this.tableData = res.info
        }
        // 处理数据形成表格数据 end
        this.loadingTableData = false
      },


      // 导出数据api
      async exportTable() {
        this.fullscreenLoading = true;
        let tabToApiParams = {
          requestsIP: 'ip',
          requestsSlowResponses: 'slow_responses',
          requestURL: 'urls',
          webEngine: 'clients',
          errRequest: 'errors',
          requestsDetail: 'detail'
        }

        let gParams = {
          start_time: this.filterParams.dateRange[0],
          end_time: this.filterParams.dateRange[1],
          platform_moid: this.filterParams.domainMoid,
          room_moid: this.filterParams.roomMoid,
        }

        // 如果有其他的 select 选项则加进gParams
        if (this.pageConf[this.activeTab].otherSelect) {
          let apiKey = {  //api支持的所有筛选条件
            module: 'module', //暂时未用
            selectHTTPCode: 'status_code',
            selectSlowResponses: 'slow_time_threshold',
            selectWebEngine: 'client',
            searchInput: 'key',
          }
          this.pageConf[this.activeTab].otherSelect.forEach(i =>
            gParams[apiKey[i]] = this.otherSelectedParams[i] && this.otherSelectedParams[i] !== 'all'
              ? this.otherSelectedParams[i] : '')
        }

        gParams['export_type'] = tabToApiParams[this.activeTab]

        await this.$api.appReuqestData.downloadRequestExport(gParams)
          .then(res => {
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

        this.fullscreenLoading = false;
      },

      // 其他函数
      // 用于判断当前时间选择器是否为空，若为空则赋予默认值
      judgeTimeRange() {
        if (!this.filterParams.dateRange) {
          let timestamp = (new Date()).getTime();
          let defaultTimeRange = [timestamp - 3600000, timestamp]
          this.datePickerTimeRange = defaultTimeRange
          this.$set(this.filterParams, 'dateRange', defaultTimeRange)
        }
      },
    },
    mounted() {
      this.activeTab = this.tab || 'requestsIP'
      if (this.defaultSelected) this.datePickerTimeRange = this.defaultSelected.timeRange || null
      this.$set(this.filterParams, 'dateRange', this.datePickerTimeRange)
      this.pageChange(this.activeTab)
    },
  }
</script>

<style>
  .childpage-request-detail {
    position: relative;
  }

  .childpage-request-detail .button-back {
    position: absolute;
    top: 3px;
    left: 10px;
    z-index: 10;
  }

  .childpage-request-detail .button-back span {
    margin-left: 20px;
    vertical-align: 8px;
  }

  .childpage-request-detail .head-right {
    display: inline-block;
    float: right;
    width: 80px;
  }

  .area-filter > div {
    margin-top: 10px;
    margin-left: 7px;
  }
</style>
