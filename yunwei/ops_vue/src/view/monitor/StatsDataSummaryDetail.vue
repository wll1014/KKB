<template>
  <div class="childpage-data-summary">
    <div class="button-back">
      <el-button icon="ops-icons-bg icon-arrow-circle-left" @click="back" circle></el-button>
      <span>{{activePageConf.name}}</span>
    </div>
    <div class="head-right">
      <el-button @click="exportTable" v-if="activePageConf.exportUrl"
                 v-loading.fullscreen.lock="fullscreenLoading">导出</el-button>
    </div>
    <div style="padding: 34px 20px 0px 53px">
      <div class="area-filter">
        <!--用户域选择 selectUserDomain-->
        <el-select popper-class="theme-dark"
                   v-model="selectedUserDomain"
                   @change="changeFilter($event,'selectUserDomain')"
                   v-if="showFilter.selectUserDomain"
                   placeholder="请选择用户域">
          <el-option
            v-for="item in selectOptionUserDomain"
            :key="item.user_domain_moid"
            :label="item.user_domain_name"
            :value="item.user_domain_moid"
          >
          </el-option>
        </el-select>
        <!--时间范围选择 selectTimeRange-->
        <el-select @change="selectTimeRangeChange"
                   popper-class="theme-dark"
                   v-model="selectedTimeRange"
                   v-if="showFilter.selectTimeRange"
                   placeholder="请选择"
                   style="width: 120px;margin-right: 7px;">
          <el-option
            v-for="item in selectOptionTimeRange" :key="item.label" :label="item.label" :value="item.value">
          </el-option>
        </el-select>
        <!--dataPicker-->
        <el-date-picker
          style="width: 322px;margin-right: 7px;vertical-align: top;"
          v-if="showFilter.selectTimeRange"
          v-model="datePickerTimeRange"
          type="datetimerange"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          popper-class="theme-dark"
          value-format="timestamp"
          @change="datePickerChange"
          format="yyyy-MM-dd HH:mm"
          :default-time="['00:00:00', '23:59:59']"
          range-separator=""
          class="clear-close-icon"
          prefix-icon="ops-icons-bg icon-calendar"
          :clearable=false
        >
        </el-date-picker>
        <!--搜索框 searchInput-->
        <el-input clearable
                  v-model='inputSearch'
                  style="margin-right: 10px;width: 290px;"
                  @keyup.enter.native="handleInputSearch('searchInput')"
                  @blur="handleInputSearch('searchInput')"
                  @clear="handleInputSearch('searchInput')"
                  v-if="showFilter.searchInput"
                  placeholder="请输入关键字搜索"
                  maxlength="100">
        </el-input>
        <el-button style="vertical-align: 1px;" @click="refreshPage" :disabled="refreshButtonDisabled">搜索</el-button>
      </div>
      <div class="area-content">
        <!-- 表格区域 -->
        <div class="area-table" v-if="renderType === 'table'" style="margin-top: 18px;padding-left: 7px;">
          <el-table tooltip-effect="dark"
                    stripe
                    border
                    style="width: 100%;"
                    :data="tableData"
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
      // KdTabCommon: () => import('@/components/common/KdTabCommon.vue'),
      SelectPlatformDomain: () => import('@/components/common/SelectPlatformDomain.vue'),
      SelectTimeRange: () => import('@/components/common/SelectTimeRange.vue'),
      KdPagination: () => import('@/components/common/KdPagination.vue'),
    },
    name: "StatsDataSummaryDetail",
    props: {
      name: String,
      defaultSelected: Object,
    },
    data() {
      return {
        timer: null, // 定时器

        fullscreenLoading: false, // 增加导出交互
        refreshButtonDisabled: false,
        renderType: null, // 内容区展示哪一块
        activePageConf: {}, // 当前展示的页面conf

        // table data
        tableColumn: [],  // 表格的列
        tableData: [],  // 表格的数据
        showTableButton: {},  // 表格的按钮
        loadingTableData: false, // 表格数据加载flag

        // filter初始化 相关数据
        showFilter: {}, // 展示哪些 filter
        filterParams: {}, // 请求所需要的filter value

        // filter options and selected 相关数据 start
        // 用户域
        selectedUserDomain: '',
        selectOptionUserDomain: [],
        // 时间选择器
        selectedTimeRange: '',
        selectOptionTimeRange: [
          {label: "自定义", value: ''},
          {label: "最近 30分钟", value: 1800000, timerInterver: 30},
          {label: "最近 1小时", value: 3600000, timerInterver: 30},
          {label: "最近 5小时", value: 18000000, timerInterver: 30},
          {label: "最近 一天", value: 86400000, timerInterver: 30},
          {label: "最近 一周", value: 604800000, timerInterver: 30},
          {label: "最近 30天", value: 2592000000, timerInterver: 30},
        ],
        datePickerTimeRange: null, // 时间选择器
        inputSearch: '', // 搜索 input

        // filter options and selected 相关数据 end

        // 页面支持展示的内容
        pageConf: {
          mtInConfCount: {
            name: '终端参会统计(单位：次)',
            customModule: false,
            url: ['arrayType', '/statistics/terminal_meeting_freq/'],
            renderType: 'table',
            renderMethod: 'table',
            timerInterver: 30,
            exportUrl:'/statistics/terminal_meeting_freq_export/',
            showSelect: ['selectUserDomain', 'selectTimeRange', 'searchInput'],
            defaultSelect: {
              selectedTimeRange: '',
              datePickerTimeRange: [new Date().setHours(0, 0, 0, 0), (new Date()).getTime()],
            },
            hasPagination: true,  // 是否有分页
            tableConf: [
              {prop: "column0", title: "终端名称"},
              {prop: "column1", title: "参会次数", width: "150"},
            ],
          },
          mtInConfTime: {
            name: '终端参会时长(单位：分钟)',
            customModule: false,
            url: ['arrayType', '/statistics/terminal_meeting_time/'],
            renderType: 'table',
            renderMethod: 'table',
            timerInterver: 30,
            showSelect: ['selectUserDomain', 'selectTimeRange', 'searchInput'],
            defaultSelect: {
              selectedTimeRange: '',
              datePickerTimeRange: [new Date().setHours(0, 0, 0, 0), (new Date()).getTime()],
            },
            hasPagination: true,  // 是否有分页
            tableConf: [
              {prop: "column0", title: "终端名称"},
              {prop: "column1", title: "参会时长", width: "150"},
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
      // 页面变化函数 (设置显示的filter 和 第一次请求的params 及 显示的内容类型)
      pageChange(pageConf, customSelect) {
        this.showFilter = {}
        if (pageConf.defaultSelect) {  // 默认选项
          for (let k in pageConf.defaultSelect) {
            this[k] = pageConf.defaultSelect[k]
            if (k === 'selectedTimeRange' && pageConf.defaultSelect[k]) {  //如果是时间范围有选择则触发修改相关时间选择器
              let timestamp = (new Date()).getTime();
              this.datePickerTimeRange = [timestamp - pageConf.defaultSelect[k], timestamp]
              if (this.activePageConf.timerInterver) this.setTimer(pageConf.defaultSelect[k], this.activePageConf.timerInterver)
            }
            ;
          }
        }
        if (customSelect) {  // 自定义选项
          for (let k in customSelect) {
            this[k] = customSelect[k]
          }
        }
        if (pageConf.showSelect) {  // 设置展示的filter和请求的params
          let defaultSelected = {
            selectUserDomain: this.selectedUserDomain,
            selectTimeRange: this.datePickerTimeRange,
            searchInput: this.inputSearch,
          }
          pageConf.showSelect.forEach(item => {
            this.$set(this.showFilter, item, true)
            this.setFilterParams(defaultSelected[item], item)
          })
        }

        this.renderType = pageConf.renderType
        if (pageConf.renderType === 'table') {  // 展示内容为表格时
          this.tableColumn = pageConf.tableConf
          this.showTableButton = pageConf.showTableButton || {}
          this.tableData = []
        }
      },
      // 过滤项改变触发的函数 start
      // 搜索按钮触发
      refreshPage() {
        this.refreshButtonDisabled = true
        this.renderInit(this.activePageConf)
        setTimeout(() => this.refreshButtonDisabled = false, 1000)
      },
      // 时间范围选择
      selectTimeRangeChange(val) {
        if (val) {
          let timestamp = (new Date()).getTime();
          this.datePickerTimeRange = [timestamp - val, timestamp]
          if (this.activePageConf.timerInterver) this.setTimer(val, this.activePageConf.timerInterver)
        } else {
          this.datePickerTimeRange = null
          this.clearTimer()
        }
        this.changeFilter(this.datePickerTimeRange, 'selectTimeRange')
      },
      // datePicker变化
      datePickerChange(val) {
        this.selectedTimeRange = ''
        this.changeFilter(val, 'selectTimeRange')
      },

      // 搜索框变化
      handleInputSearch(k) {
        this.changeFilter(this.inputSearch, k)
      },

      // Filter 变化
      changeFilter(val, k) {
        this.setFilterParams(val, k)
        if (k === 'selectTimeRange' && !val) return false  // 如果时间为空则不发请求
        this.renderInit(this.activePageConf)
      },
      // 设置filter参数
      setFilterParams(val, k) {
        this.$set(this.filterParams, k, val)
      },

      // 分页变化
      pageHandleCurrentChange(val) {
        this.currentPage = val
        this.renderInit()
      },

      // 过滤项改变触发的函数 end

      // 渲染函数,负责将当前展示项用不同的方法渲染 start
      renderInit(pageConf) {
        let renderTypeMethod = {
          'table': this.rendertable, // 表格渲染
        };
        let method = pageConf.renderMethod
        this.judgeTimeRange()  // 判断时间是否为空

        let selectToApiKey = {
          selectUserDomain: 'user_domain_moid',
          selectTimeRange: 'selectTimeRange',
          searchInput: 'key',
        }
        let fParams = {}
        pageConf.showSelect.forEach((item) => {
          if (item === 'selectTimeRange') {
            fParams['start_time'] = this.filterParams[item][0]
            fParams['end_time'] = this.filterParams[item][1]
          } else {
            fParams[selectToApiKey[item]] = this.filterParams[item]
          }
        })

        if (pageConf.hasPagination) {
          fParams.start = (this.currentPage - 1) * this.pageSize
          fParams.count = this.pageSize
        }
        // let fParams = {
        //   start_time: this.filterParams.dateRange[0],
        //   end_time: this.filterParams.dateRange[1],
        //   platform_moid: this.filterParams.domainMoid,
        //   room_moid: this.filterParams.roomMoid,
        //   // start: (this.currentPage - 1) * this.pageSize,
        //   // count: this.pageSize,
        // }
        if (method) renderTypeMethod[method](pageConf, fParams)
      },

      async rendertable(pageConf, fParams) {
        this.loadingTableData = true

        let params = pageConf.staticUrlParams
        params = {...params, ...fParams}

        let data = await this.getTableData(pageConf.url[0], pageConf.url[1], params)

        // 处理数据形成表格数据 end
        this.tableData = data.info
        this.pageTotal = data.total || 0
        this.loadingTableData = false
      },

      async getTableData(type, url, params) {
        let data = []
        if (type === 'arrayType') {
          data = await this.$api.getChartData.getArrayTypeTableData(url, params)
        } else {
          data = await this.$api.getChartData[url](params)
        }
        return data
      },
      // 渲染函数,负责将当前展示项用不同的方法渲染 end

      // 导出数据api
      async exportTable() {
        this.fullscreenLoading = true;
        let selectToApiKey = {
          selectUserDomain: 'user_domain_moid',
          selectTimeRange: 'selectTimeRange',
          searchInput: 'key',
        }
        let fParams = {}
        this.activePageConf.showSelect.forEach((item) => {
          if (item === 'selectTimeRange') {
            fParams['start_time'] = this.filterParams[item][0]
            fParams['end_time'] = this.filterParams[item][1]
          } else {
            fParams[selectToApiKey[item]] = this.filterParams[item]
          }
        })

        await this.$api.globalData.exportFile(this.activePageConf.exportUrl, fParams)

        this.fullscreenLoading = false;
      },

      // 其他函数
      // 用于判断当前时间选择器是否为空，若为空则赋予默认值
      judgeTimeRange() {
        if (!this.filterParams.selectTimeRange) {
          let timestamp = (new Date()).getTime();
          this.selectedTimeRange = 3600000
          this.datePickerTimeRange = [timestamp - this.selectedTimeRange, timestamp]
          if (this.activePageConf.timerInterver) this.setTimer(this.selectedTimeRange, this.activePageConf.timerInterver)
          this.$set(this.filterParams, 'selectTimeRange', this.datePickerTimeRange)
        }
      },
      // 定时器
      setTimer(range = 3600000, iTime) {
        this.clearTimer();
        this.timer = setInterval(() => {
          let timestamp = (new Date()).getTime();
          this.changeFilter([timestamp - range, timestamp], 'selectTimeRange')
        }, Number(iTime) * 1000)
      },
      // 清楚定时器
      clearTimer() {
        clearInterval(this.timer);
        this.timer = null;
      },

      // 用户域 options初始化
      async setSelectUserDomain() {
        let data = await this.$api.globalData.allUserDomain()
        this.selectOptionUserDomain = [{
          user_domain_name: '全部平台域',
          user_domain_moid: ''
        }]
        this.selectOptionUserDomain = this.selectOptionUserDomain.concat(data)
        this.selectedUserDomain = ''
      },

      // 页面加载时触发
      async init() {
        this.activePageConf = this.pageConf[this.name]
        await this.setSelectUserDomain()
        this.pageChange(this.activePageConf)
        this.renderInit(this.activePageConf)
      },
    },
    mounted() {
      this.init()
    },
    beforeDestroy() {
      this.clearTimer()
    },
  }
</script>

<style>
  .childpage-data-summary {
    position: relative;
    padding: 10px 10px 10px 10px;
  }

  .childpage-data-summary .button-back {
    position: absolute;
    top: 13px;
    left: 20px;
    z-index: 10;
  }

  .childpage-data-summary .button-back span {
    margin-left: 20px;
    vertical-align: 8px;
  }

  .childpage-data-summary .head-right {
    display: inline-block;
    float: right;
    width: 80px;
    margin-top: 10px;
  }

  .area-filter > div {
    margin-top: 10px;
    margin-left: 7px;
  }
</style>
