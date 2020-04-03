<template>
  <div class="page-host-info theme-dark">

    <!-- 主机列表区 -->
    <div v-if="showArea==='hostinfo'">
      <!-- 分组区域start -->
      <div :class="['area-leftgroup',{'group-collapse':!groupCollapse}]" :style="{'width':groupCollapse?'260px':'0px'}">
        <div class="buttom-group-collapse" :style="{'left':groupCollapse?'260px':'0px'}"
             @click="groupCollapseChange">
          <i :class="['icon-group-collapse','el-icon-arrow-left',{'active':!groupCollapse}]"></i>
        </div>
        <el-scrollbar class="hostinfo-siderbar-scrollbar" :noresize="false">
          <TheHostInfoSidebar ref="theHostinfoSiderbar"
                              :domainMoid="domainMoid"
                              :roomMoid="roomMoid"
                              style="width: 260px;"
                              @change="siderbarChange"></TheHostInfoSidebar>
        </el-scrollbar>
      </div>
      <!-- 分组区域end -->
      <!-- 右侧内容区 -->
      <div class="area-content" :style="{'margin-left':groupCollapse?'286px':'26px'}">
        <div class="area-toolbar">
          <!-- 搜索栏 -->
          <el-input style="width: 260px;margin-right: 7px" v-model="inputSearchHost" maxlength="100"
                    placeholder="请输入服务器名称或者IP地址"
                    @keyup.enter.native="searchHost(inputSearchHost)" clearable></el-input>
          <el-button @click="searchHost(inputSearchHost)">搜索</el-button>
          <!-- 右侧按钮 -->
          <div style="float: right;">
            <el-button @click="postDeploySync" :disabled="deploySyncStatus">一键同步</el-button>
            <el-dropdown trigger="click"
                         @visible-change="dropdownGroupChange"
                         @command="handleGroupChange"
                         v-if="showType === 'table'">
              <el-button style="height: 24px;margin-left: 7px;" :disabled="groupData.length <= 0">
                移动至分组<i class="el-icon-arrow-down el-icon--right"></i>
              </el-button>
              <el-dropdown-menu class="theme-dark" slot="dropdown" style="white-space:nowrap;max-width: 200px;">
                <el-dropdown-item :command="groupitem.id" :key="groupitem.name"
                                  v-for="groupitem in groupData">{{groupitem.name}}
                </el-dropdown-item>
              </el-dropdown-menu>
            </el-dropdown>
            <span style="font-size: 0;margin-left: 7px;">
              <button @click='changeViewType("table")' :class="['button-glass',{'active':showType === 'table'}]">列表</button>
              <button @click='changeViewType("chart")'
                      :class="['button-glass',{'active':showType === 'chart'}]">视图</button>
					  </span>
          </div>
        </div>
        <!-- 表格区域 -->
        <div v-if="showType === 'table'">
          <div class="area-table" style="margin-top: 18px;">
            <el-table ref="hostinfoMultipleTable" tooltip-effect="dark"
                      stripe
                      border
                      style="width: 100%;"
                      :data="hostInfoTableData"
                      @selection-change="hostInfoHandleSelectionChange"
                      @row-dblclick="tableRowDblClick"
                      :row-class-name="classRowSelectChange"
                      :row-key="rowKey"
                      :cell-style="setCellStyle"
                      :header-cell-class-name="setHeaderCellStyle"
                      v-loading="loadingTableData"
                      element-loading-background="rgba(0, 0, 0, 0.5)"
            >
              <el-table-column show-overflow-tooltip type="index" label="序号" width="50">
              </el-table-column>
              <el-table-column :reserve-selection="true" type="selection" width="40">
              </el-table-column>
              <el-table-column show-overflow-tooltip prop="name" label="主机名称">
              </el-table-column>
              <el-table-column show-overflow-tooltip prop="local_ip" label="IP地址">
              </el-table-column>
              <el-table-column show-overflow-tooltip prop="machine_type" label="主机类型">
              </el-table-column>
              <el-table-column show-overflow-tooltip prop="frame_name" label="所属机框">
              </el-table-column>
              <el-table-column show-overflow-tooltip label="主机状态">
                <template slot-scope="scope">
                  <button type="button" class="button-alarm-info" @click="alarmInfoRouter(scope.row)"
                          v-if="scope.row.status">
                    <span style="text-decoration: underline;">异常</span>
                  </button>
                  <span v-else>正常</span>
                </template>
              </el-table-column>
              <el-table-column show-overflow-tooltip prop="cluster" label="工作模式">
              </el-table-column>
              <el-table-column show-overflow-tooltip prop="diskage" label="磁盘寿命">
              </el-table-column>
              <el-table-column show-overflow-tooltip prop="uptime" label="服务器运行时间">
              </el-table-column>
              <el-table-column label="操作">
                <template slot-scope="scope">
                  <button type="button" class="button-host-info" @click="detailHostInfo(scope.row)"
                          v-if="scope.row.has_detail">
                    <span style="text-decoration: underline;">详情</span>
                  </button>
                  <span v-else>此类型设备无详情</span>
                </template>
              </el-table-column>
            </el-table>
          </div>
          <!-- 分页区start -->
          <div style="margin-top: 20px;">
            <KdPagination
              @current-change="pageHandleCurrentChange"
              :page-size="pageSize"
              :currentPage.sync="currentPage"
              :total="pageTotal"></KdPagination>
          </div>
          <!-- 分页区end -->
        </div>
        <!-- 表格区域 end -->

        <div v-if="showType === 'chart'">
          <HostTopology style="margin-top: 20px;" ref="hostTopology" :urlParams="filterParams" @select="hostTopologySelect"></HostTopology>
        </div>
      </div>
    </div>
    <!-- 主机列表区end -->

    <!-- 主机详情区 -->
    <div v-if="showArea==='hostdetail'">
      <HostInfoDetail @back="showAreaChange" :host_moid="hostMoid"></HostInfoDetail>
    </div>

    <!--无数据时显示的页面-->
    <div v-if="showArea==='hostNoData'">
      <el-button @click="postDeploySync" style="float: right;margin-top: 20px;margin-right: 20px;"
                 :disabled="deploySyncStatus">一键同步
      </el-button>
      <div style="position: absolute;  top:280px;width: 100%;text-align: center;">
        <span style="margin-right: 7px;font-size: 14px;">
          <i class="ops-icons-bg icon-notice" style="vertical-align: bottom;"></i>
        </span>
        <span>尚未获取到数据，请点击“</span>
        <span style="color: #299dff;text-decoration:underline;cursor: pointer;" @click="postDeploySync">一键同步</span>
        <span>”手动刷新</span>
      </div>
    </div>
  </div>
</template>


<script>
  export default {
    components: {
      KdPagination: () => import('@/components/common/KdPagination.vue'),
      HostInfoDetail: () => import('@/components/hostmanage/HostInfoDetail.vue'),
      TheHostInfoSidebar: () => import('@/view/hostmanage/TheHostInfoSidebar.vue'),
      HostTopology: () => import('@/view/hostmanage/HostTopology.vue'),
      TheHsotFrame: () => import('@/view/hostmanage/TheHsotFrame.vue'),
    },
    props: {
      domainMoid: String,
      roomMoid: String,
    },
    data() {
      return {
        // 单页面区域展示切换
        showArea: 'hostinfo',
        showType: 'chart',

        filterParams: {},
        // 同步数据状态
        deploySyncStatus: false,
        // 分组侧边栏展开收起状态
        groupCollapse: false,
        // 分组的数据
        groupData: [],
        // 主机搜索数据
        inputSearchHost: '',

        // 主机详情页蒙版
        hostDetailDialogVisible: false,

        // 分页数据
        currentPage: 1,
        pageSize: 15,
        pageTotal: 0,

        // 当前页面展示的主机数据
        hostInfoTableData: [],
        hostInfoMultipleSelection: [],
        hostInfoSelectedChange: {},
        loadingTableData: false,
        // 单台主机的数据
        singleHostData: {},

        // 详情的主机
        hostMoid: '',
        hostRowInfo: null,
      };
    },
    methods: {
      // 主机拓扑页面返回函数
      hostTopologySelect(select) {
        this.detailHostInfo(select)
      },
      // 分组侧边栏展开收起函数
      groupCollapseChange() {
        this.groupCollapse = !this.groupCollapse
        this.$nextTick(() => {
          if (this.$refs.hostTopology) this.$refs.hostTopology.chartsResize()
        })
      },
      // 侧边栏选中变化触发
      siderbarChange(val) {
        if (!val.domain_moid) {
          this.showArea = 'hostNoData'
          return false
        }
        this.currentPage = 1
        this.groupData = val.activeGroup
        this.filterParams = Object.assign({}, this.filterParams, val)  // 强制vue更新
        // this.setHostList()
      },
      // 搜索按钮
      searchHost(val) {
        this.$set(this.filterParams, 'query', val)
        this.currentPage = 1
        this.setHostList()
      },
      // 视图切换
      changeViewType(val){
        this.showType = val
        if(val === 'table') this.setHostList()
      },
      // 移动分组的函数
      handleGroupChange(command) {
        if (this.hostInfoMultipleSelection.length) {
          let idlist = []
          this.hostInfoMultipleSelection.forEach(i => {
            idlist.push(i.moid)
          });
          this.changeGroup(command, idlist)
        }
      },

      tableRowDblClick(row, column, event) {
        if (row.has_detail) {
          this.detailHostInfo(row)
        }
      },
      // 详情按钮函数
      detailHostInfo(row) {
        if (row.has_detail) {
          this.hostMoid = row.moid
          this.showArea = 'hostdetail'
        } else {
          this.$message("此类型设备无详情")
        }

      },
      //告警异常点击跳转
      alarmInfoRouter(row) {
        this.$router.push({
          name: 'monitor-alarm',
          params: {
            type: 'alarmDev',
            urlParams: {
              search: row.name
            }
          }
        });
      },
      // 设置row-key
      rowKey(row) {
        return row.id
      },
      // 改变表头样式
      setHeaderCellStyle({row, column, rowIndex, columnIndex}) {
        if (columnIndex === 0 || columnIndex === 1) {
          return "el-table-th-noborder"
        }
      },
      // 改变单元格样式
      setCellStyle({row, column, rowIndex, columnIndex}) {
        let cellStyle = {
          'color': '#e45959',
        }
        if (row.uptime === '异常' && columnIndex === 9) {
          return cellStyle
        }
      },
      // 全部选中函数
      rowSelectedAll(selection) {
        if (selection) {
          selection.forEach(row => {
            this.$set(this.hostInfoSelectedChange, row.moid, true)
          });
        }
        else {
        }
      },
      // 单行选中变化函数
      hostInfoHandleSelectionChange(val) {
        this.hostInfoSelectedChange = {}
        val.forEach(row => {
          this.$set(this.hostInfoSelectedChange, row.moid, true)
        });
        this.hostInfoMultipleSelection = val;
      },
      // 单行选中函数
      rowSelected(selection, row) {
        if (this.hostInfoSelectedChange[row.moid]) {
          this.$set(this.hostInfoSelectedChange, row.moid, false)
        }
        else {
          this.$set(this.hostInfoSelectedChange, row.moid, true)
        }
      },
      // 选中行选中后变色
      classRowSelectChange({row, rowIndex}) {
        if (this.hostInfoSelectedChange[row.moid]) {
          return "row-selected"
        }
      },

      // 分页函数start
      pageHandleCurrentChange(val) {
        this.currentPage = val
        this.setHostList()
      },
      // 分页函数end

      // 详情页面返回函数
      showAreaChange(val) {
        if (val) {
          this.showArea = 'hostinfo'
        }
      },

      // API处理
      // 同步部署工具
      postDeploySync() {
        if (this.deploySyncStatus) {
          this.$notify({
            title: '正在同步',
          });
        } else {
          this.deploySyncStatus = true
          this.$api.hostManageApi.postDeploySync()
            .then(res => {
              if (res.data.success) {
                this.$refs.theHostinfoSiderbar.init()  // 重新初始化侧边栏
              } else {
                this.$notify.error({
                  title: 'Error Code:' + res.data.error_code,
                  message: res.data.msg,
                });
              }
              this.deploySyncStatus = false
            })
            .catch(err => {
              this.$notify.error({
                title: '未知错误',
              });
              this.deploySyncStatus = false
            })
        }
      },
      // 移动分组
      changeGroup(groupid, machine_moids) {
        let params = {
          machine_moids: machine_moids,
        }
        this.$api.hostManageApi.changeGroup(groupid, params)
          .then(res => {
            this.$refs.theHostinfoSiderbar.refresh(this.filterParams.domain_moid, this.filterParams.room_moid, this.filterParams.group_id)
            if (res.data.success) {
              this.setHostList()
            }
          })
      },
      // 获取主机列表
      async setHostList() {
        this.loadingTableData = true
        let params = {
          domain_moid: this.filterParams.domain_moid,
          room_moid: this.filterParams.room_moid,
          group_id: this.filterParams.group_id,
          query: this.filterParams.query,
          count: this.pageSize,
          start: (this.currentPage - 1) * this.pageSize,
        }
        let res = await this.$api.hostManageApi.hostList(params)
        if (!res) return false
        this.hostInfoTableData = res.data
        for (let item of this.hostInfoTableData) {
          for (let key in item) {
            if (item[key] === '') {
              // console.log(item[key]);
              item[key] = '   ----'
            }
          }
        }
        ;
        this.pageTotal = res.total
        this.loadingTableData = false

        this.setHostDiskInfo()
        this.setHostOnLineInfo()
      },

      // 设置表格数据：磁盘寿命
      async setHostDiskInfo() {
        for (let item of this.hostInfoTableData) {
          // 磁盘寿命
          let res = await this.$api.monitor.handlerGetAllDiskageNodeData(item.moid)
          let diskage = res.map(item => item["system.diskage.count"])
          let max = Math.max.apply(null, diskage)
          if (max && max !== -Infinity) {
            this.$set(item, "diskage", (max * 100).toFixed() + "%")
          } else {
            this.$set(item, "diskage", "该磁盘不支持寿命检测")
          }
        }
      },
      // 设置表格数据：服务器运行时长
      async setHostOnLineInfo() {
        for (let item of this.hostInfoTableData) {
          this.$api.monitor.getUptime(item.moid)
            .then(res => {
              let uptime = res.data.data["system.uptime.duration.ms"]
              if (uptime === -1 || uptime === undefined) {
                if (item.has_detail) {
                  this.$set(item, "uptime", "异常")
                } else {
                  this.$set(item, "uptime", "----")
                }
              } else {
                let time = this.timeMillisecondAnalysis(uptime)
                this.$set(item, "uptime", time)
              }
            })
        }
        ;
      },

      // 单台主机信息
      getSingleHostInfo(row) {
        this.hostDetailDialogVisible = true;
        this.$api.hostManageApi.getSingleHostInfo(1)
          .then(res => {
            this.singleHostData = res.data.data
            // console.log(this.singleHostData);
          })
      },


      // 其他函数（频繁使用可放置通用js）
      timeMillisecondAnalysis(val) {
        let temData;
        if (val > 31536000000) {
          temData = parseInt(val / 31536000000) + "年"
        } else if (val > 2592000000) {
          temData = parseInt(val / 2592000000) + "个月"
        } else if (val > 86400000) {
          temData = parseInt(val / 86400000) + "天"
        } else if (val > 3600000) {
          temData = parseInt(val / 3600000) + "小时"
        } else {
          temData = parseInt(val / 60000) + "分钟"
        }
        return temData
      },
    },
    mounted() {
      // 调整当前route，变化侧边栏高亮
      let activeRouteList = ['/ops/manage/hostinfo', '/ops/manage']
      this.$store.dispatch('activeRouteChange', activeRouteList)
      this.$nextTick(() => {
        Object.keys(this.$route.params).forEach(i => this.$route.params[i] = null)
      })
    },
  };
</script>

<style>
  .page-host-info {
    /* margin-left: 4px;
        padding: 2px; */
    position: relative;
    /* border: 1px solid; */
    /* border-color: #8C939D; */
  }

  .page-host-info .el-tree-node__label {
    display: inline-block;
    max-width: 140px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    vertical-align: bottom;
  }

  .area-leftgroup {
    position: fixed;
    height: calc(100vh - 56px);
    background-color: #232629;
    z-index: 99;
  }

  .hostinfo-siderbar-scrollbar {
    height: 100%;
  }

  .page-host-info .el-scrollbar .el-scrollbar__wrap {
    overflow-x: hidden;
    overflow-y: auto;
  }

  .page-host-info .group-tree {
    box-sizing: border-box;
    padding: 16px 16px 16px 10px;
  }

  .page-host-info .el-tree-node__content {
    position: relative;
  }

  .page-host-info .el-tree-node__content.is-active {
    /*background-color: #00a0e9;*/
    color: #299dff;
  }

  .page-host-info .el-tree-node__content {
    height: 30px;
    color: #9ca9b1;
    margin-bottom: 10px;
  }

  .page-host-info .el-tree-node__content:hover {
    color: #299dff;
    background-color: transparent;
  }

  .area-content {
    padding-top: 16px;
    padding-right: 20px;
  }

  .buttom-group-collapse {
    height: 40px;
    width: 14px;
    border: 1px solid #787c81;
    text-align: center;
    vertical-align: middle;
    line-height: 40px;
    cursor: pointer;
    position: absolute;
    top: calc((100vh - 60px) / 2);
    z-index: 1000;
    background: #232629;
  }

  .icon-group-collapse {
    color: #c0c4cc;
    font-size: 12px;
    transform: rotate(0deg);
    transition: transform .3s ease-in-out;
  }

  .icon-group-collapse.active {
    transform: rotate(-180deg);
  }

  .dialog-footer {
    margin-top: 5%;
  }

  .el-table__row.row-selected td {
    background-color: #485a6b !important;
    color: #fff;
  }

  .button-host-info {
    border-color: transparent;
    color: #00a2ff;
    background: transparent;
    padding-left: 0;
    padding-right: 0;
    display: inline-block;
    line-height: 1;
    white-space: nowrap;
    cursor: pointer;
    text-align: center;
    box-sizing: border-box;
    outline: none;
    margin: 0;
    transition: .1s;
    font-size: 14px;
  }

  .button-alarm-info {
    border-color: transparent;
    color: #e45959;
    background: transparent;
    padding-left: 0;
    padding-right: 0;
    display: inline-block;
    line-height: 1;
    white-space: nowrap;
    cursor: pointer;
    text-align: center;
    box-sizing: border-box;
    outline: none;
    margin: 0;
    transition: .1s;
    font-size: 14px;
  }

</style>
