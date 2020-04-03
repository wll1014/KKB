<template>
  <div class='theme-dark'>
    <div v-if="showAera === 'main'" style="height: 100%;width: 100%;box-sizing: border-box;padding: 20px;">
      <!-- 上方表单 -->
      <div>

        <el-select filterable placeholder='全部操作人员' v-model='optionSelectedFilterOperatorPeople'
                   popper-class="theme-dark" style="width: 240px;margin-right: 7px">
          <el-option v-for="item in optionFilterOperatorPeople"
                     :key="item"
                     :label="item"
                     :value="item">
          </el-option>
        </el-select>
        <el-input placeholder="请输入文件名称搜索" v-model='inputFilterFileName' style="width: 180px;margin-right: 7px"
                  @keyup.enter.native="search" maxlength="100"></el-input>
        <el-button @click='search'>搜索</el-button>
        <span style="float: right;">
          <el-button @click='dialogCreateTask'>文件下发</el-button>
        </span>

      </div>

      <!-- 表格展示 -->
      <div style="padding-top: 18px;">
        <el-table
          tooltip-effect="dark"
          stripe
          border
          style="width: 100%;"
          v-loading="loadingTableData"
          element-loading-background="rgba(0, 0, 0, 0.5)"
          :data='tableDataTaskList'>
          <el-table-column style='text-align: center;' min-width="53px" type='index' label="序号"></el-table-column>
          <el-table-column prop='task_name' min-width='171px' label="任务名称" show-overflow-tooltip></el-table-column>
          <el-table-column label="操作时间" min-width='151px' show-overflow-tooltip>
            <template slot-scope="scope">
              <span>{{new Date(scope.row.create_time).format('Y m-d H:i')}}</span>
            </template>
          </el-table-column>
          <el-table-column prop='operator' label="操作人员" min-width='128px' show-overflow-tooltip></el-table-column>
          <el-table-column label="源文件和大小" min-width='151px' show-overflow-tooltip>
            <template slot-scope="scope">
              <span>{{transFileInfo(scope.row.file)}}</span>
            </template>
          </el-table-column>
          <el-table-column label='服务器数量' min-width='70px' show-overflow-tooltip>
            <template slot-scope="scope">
              <span>{{scope.row.machines.length}}</span>
            </template>
          </el-table-column>
          <el-table-column label='发送状态' min-width='70px' show-overflow-tooltip>
            <template slot-scope="scope">
              <span :class="[scope.row.status === 1 ? 'task--executing': scope.row.status === 3 ? 'task--failed':'']">{{objTaskStatu[scope.row.status]}}</span>
            </template>
          </el-table-column>
          <el-table-column label="操作" min-width='151px'>
            <template slot-scope="scope">
              <button type="button" class="button-host-info" @click="showTaskDetail(scope.row)"
                      style='padding-right: 10px;'>
                <span style="text-decoration: underline;">详情</span>
              </button>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <!-- 分页区start -->
      <div style="margin-top: 20px;">
        <KdPagination
          @current-change="pageHandleCurrentChange"
          :pageSize="pageSize"
          :currentPage.sync="currentPage"
          :total="pageTotal"></KdPagination>
      </div>
      <!-- 分页区end -->

      <!--蒙版区域start-->
      <el-dialog
        title="文件分发"
        :visible.sync="dialogVisibleTask"
        width="800px"
        append-to-body
        custom-class="theme-dark"
        :before-close="dialogBeforeClose"
        @closed="closeClearNode"
        :close-on-click-modal=false
      >
        <div style="margin-top: 20px;padding: 0px 15px;" v-if="!clearDialogNode">
          <div style="margin-bottom: 20px;">
            <span style="width: 75px;display: inline-block;font-size: 12px;">任务名称</span>
            <div style="display: inline-block;">
              <el-input clearable v-model='inputDialogTaskName'
                        style="width: 650px;" maxlength="64"
                        placeholder="请输入任务名称，最多输入64个字符"></el-input>
            </div>
          </div>
          <div style="margin-bottom: 20px;">
            <span style="width: 75px;display: inline-block;font-size: 12px;">上传路径</span>
            <div style="display: inline-block;">
              <el-input clearable v-model='inputDialogTaskPath' style="width: 650px;" maxlength="100"
                        placeholder="请输入上传路径，例：/home;最多输入64个字符"></el-input>
            </div>
          </div>
          <div style="color: #ff6666;margin-bottom: 10px;font-size: 12px;">{{dialogErrorInfo}}</div>
          <div style="height: 400px;">
            <KdTabCommon :tab-list="tabList" :active-tab="activeTab" class-name="" @tab-change="tabChange"
                         :width=18></KdTabCommon>
            <div style="margin-top: 20px;position: relative;" v-show="activeTab==='fileList'">
              <el-upload
                class=""
                action="/api/v1/ops/hosts_oper/oper_tasks/distribution_files/"
                :show-file-list=false
                with-credentials
                ref="fileDistributionUpload"
                :data="uploadPostData"
                :before-upload="beforeUpload"
                :on-change="uploadStatuChange"
                :on-progress="uploadProgress"
                :on-success="uploadOnSuccess"
                :on-error="uploadOnError"
                :multiple=false
                :file-list="fileListUpload">
                <el-button style="position: absolute;z-index: 99;right: 0;top:-41px;"
                           :disabled="tableDataUploadList.length >= 5">文件选择
                </el-button>
              </el-upload>
              <!-- 表格展示 -->
              <div style="margin-top: -19px;">
                <el-table
                  tooltip-effect="dark"
                  stripe
                  border
                  style="width: 100%;"
                  :data='tableDataUploadList'>
                  <el-table-column style='text-align: center;' min-width="53px" type='index'
                                   label="序号"></el-table-column>
                  <el-table-column prop='name' min-width='171px' label="文件名称" show-overflow-tooltip></el-table-column>
                  <el-table-column label="文件大小" min-width='151px' show-overflow-tooltip>
                    <template slot-scope="scope">
                      <span>{{(scope.row.size/1024).toFixed(2)}} kb</span>
                    </template>
                  </el-table-column>
                  <el-table-column label="状态" min-width='128px' show-overflow-tooltip>
                    <template slot-scope="scope">
                      <span>{{scope.row.percentage === 'error' ? '上传失败' : (scope.row.percentage).toFixed(0) + '%'}}</span>
                    </template>
                  </el-table-column>
                  <el-table-column label="操作" min-width='151px'>
                    <template slot-scope="scope">
                      <button type="button" class="button-host-info" @click="deleteUploadFile(scope.row)"
                              style='padding-right: 10px;'>
                        <span style="text-decoration: underline;">删除</span>
                      </button>
                    </template>
                  </el-table-column>
                </el-table>
              </div>

            </div>
            <div style="margin-top: 20px;" v-show="activeTab==='devList'">
              <TheTableDevAddFromOrganization :devList="tableDataAddDevList"
                                              @data-change="addFromOrganizationDevChange"
                                              :tableHeight=270
                                              :customParams="{device_type:0}"
                                              buttonClass="file-distribution-ttdafo"></TheTableDevAddFromOrganization>
            </div>
          </div>
          <div style="font-size: 12px;color: #5d6266;">
            <div style="margin-bottom: 9px;">提示：</div>
            <div style="margin-bottom: 9px;">1.每次只能上传1个文件，最多上传5个</div>
            <div>2.每个文件大小不超过50MB</div>
          </div>
        </div>
        <div style="padding: 30px;text-align: center;box-sizing: border-box;">
          <span style="text-align: center;">
            <el-button @click="putFileDistributionTask()" :disabled="fileUploadFlag">确 定</el-button>
            <el-button @click="dialogVisibleTask = false" :disabled="fileUploadFlag">取 消</el-button>
          </span>
        </div>
      </el-dialog>
      <!--蒙版区域end-->
    </div>
    <div v-if="showAera === 'child'" style="height: 100%;width: 100%;box-sizing: border-box;padding: 20px;">
      <FileDistributionDetail :taskID="childTaskID" @back="backMainPage"></FileDistributionDetail>
    </div>
  </div>
</template>

<script>
  import {mapGetters} from 'vuex'

  export default {
    components: {
      KdPagination: () => import('@/components/common/KdPagination.vue'),
      KdTabCommon: () => import('@/components/common/KdTabCommon.vue'),
      TheTableDevAddFromOrganization: () => import('@/components/hostmanage/TheTableDevAddFromOrganization.vue'),
      FileDistributionDetail: () => import('@/view/hostmanage/FileDistributionDetail.vue'),
    },
    data() {
      return {
        timer: null,

        optionSelectedFilterOperatorPeople: null,
        optionFilterOperatorPeople: [],
        inputFilterFileName: null,

        tableDataTaskList: [],
        loadingTableData: false,
        // 分页数据
        currentPage: 1,
        pageSize: 15,
        pageTotal: 0,

        objTaskStatu: {
          1: '正在执行',
          2: '执行成功',
          3: '执行失败',
        },

        showAera: 'main',  //main or child
        childTaskID: null,

        lastSearchParams: {},
        // 蒙版数据
        taskID: null,
        putFlag: false, // 用于保存关闭时不会删除任务
        fileUploadFlag: false, //用于文件上传时不可做蒙版关闭操作

        uploadPostData: {},

        keepAliveUploadFileObj: {},

        dialogVisibleTask: false,
        clearDialogNode: true,  // 用于关闭蒙版时清空调用子组件的缓存

        inputDialogTaskName: null,
        inputDialogTaskPath: null,

        fileListUpload: [], //用于更新el-upload内部list

        tableDataUploadList: [],
        tableDataAddDevList: [],

        activeTab: 'fileList',

        tabList: [
          ['fileList', '文件列表'],
          ['devList', '服务器列表'],],
        // 错误提示信息
        dialogErrorInfo: null,

        // 蒙版数据 end
      }
    },
    methods: {
      // 其他函数
      // 转换fileinfo
      transFileInfo(l) {
        let newl = l.map(item => item.filename + " : " + Math.ceil(item.size / 1024) + 'kb')
        return newl.join('\n')
      },
      // 其他函数end

      // 子页面回调
      backMainPage(val) {
        if (val) {
          this.showAera = 'main'
          this.childTaskID = null
        }
      },

      // 分页变化回调
      pageHandleCurrentChange(val) {
        // console.log(val)
        this.currentPage = val
        this.getFileDistributionTasks()
      },

      // tab页变化函数
      tabChange(val) {
        this.activeTab = val
      },

      addFromOrganizationDevChange(val) {
        this.tableDataAddDevList = val
      },

      // 蒙版关闭回调
      closeClearNode() {
        if (this.taskID && !this.putFlag) {
          this.deleteFileDistributionTask(this.taskID)
        }

        this.dialogVisibleTask = false
        this.clearDialogNode = true
        this.taskID = null
        this.uploadPostData = {}

        this.activeTab = 'fileList'
        this.inputDialogTaskName = null
        this.inputDialogTaskPath = null

        this.fileListUpload = []

        this.keepAliveUploadFileObj = {}

        this.tableDataUploadList = []
        this.tableDataAddDevList = []

        // 错误提示信息
        this.dialogErrorInfo = null
      },

      // 蒙版关闭二次确认
      dialogBeforeClose(done) {
        if (this.fileUploadFlag) {
          this.$notify.info({
            title: '文件正在上传，请等待...',
          });
          return false
        }

        this.$confirm('检测到任务未完成，是否离开当前页面？', '确认信息', {
          center: true,
          customClass: 'theme-dark',
        })
          .then(_ => {
            done();
          })
          .catch(_ => {
          });
      },

      // 上传回调
      beforeUpload(file) {
        // console.log(file)
        let maxSize = 50 * 1024 * 1024
        if (file.size > maxSize) {
          this.$notify.error({
            title: '文件大小超过50M',
          });
          return false
        }
        this.fileUploadFlag = true

      },

      uploadStatuChange(file, fileList) {

      },

      uploadProgress(event, file, fileList) {
        this.tableDataUploadList = fileList
      },

      uploadOnSuccess(response, file, fileList) {
        if (!response.success) {
          this.$notify.error({
            title: '上传失败',
          });
          file.percentage = 'error'
        }

        this.fileUploadFlag = false
      },
      uploadOnError(err, file, fileList) {
        this.fileUploadFlag = false
      },
      // 上传回调 end

      // 页面内函数
      search() {												//搜索
        this.currentPage = 1
        this.getFileDistributionTasks()
        this.lastSearchParams = {
          search: this.inputFilterFileName ? this.inputFilterFileName : null,
          operator: this.optionSelectedFilterOperatorPeople ? this.optionSelectedFilterOperatorPeople : null,
        }
      },

      showTaskDetail(row) {
        this.childTaskID = row.id
        this.showAera = 'child'
      },


      async dialogCreateTask() {										//创建即时任务

        // // 暂时限制权限
        // this.$notify({
        //   title:'账号无权限'
        // })
        // return false
        // // 暂时限制权限 end

        let params = {
          "before_upload_files": 1
        }
        let res = await this.createFileDistributionTask(params)
        this.taskID = res.task_id
        this.uploadPostData = {
          task_id: this.taskID
        }
        // console.log('dialog -->',res)
        this.putFlag = false
        this.dialogVisibleTask = true
        this.clearDialogNode = false
      },


      async deleteUploadFile(row) {
        // console.log(this.fileListUpload)
        // 如果是上传成功的文件
        if (row.response) {
          const newItems = [...this.tableDataUploadList]
          const index = newItems.indexOf(row)
          newItems.splice(index, 1)

          if (row.response.success) {
            let res = await this.deleteFileDistributionFile(row.response.data.id)
            if (res.status === 204) {
              // console.log(newItems)
              this.tableDataUploadList = newItems
              this.fileListUpload = newItems
            } else {
              this.$notify.error({
                title: '删除失败',
              });
            }
          } else {
            this.tableDataUploadList = newItems
            this.fileListUpload = newItems
          }

        } else {
          // 删除还在上传的文件
          // console.log(row)
          this.$refs.fileDistributionUpload.abort(row)
          const newItems = [...this.tableDataUploadList]
          const index = newItems.indexOf(row)
          newItems.splice(index, 1)
          // console.log(newItems)
          this.tableDataUploadList = newItems
          this.fileListUpload = newItems
        }

      },

      // 页面内函数end

      // api start
      async getFileDistributionTasks() {
        this.loadingTableData = true
        let params = {
          search: this.inputFilterFileName ? this.inputFilterFileName : null,
          operator: this.optionSelectedFilterOperatorPeople ? this.optionSelectedFilterOperatorPeople : null,
          start: (this.currentPage - 1) * this.pageSize,
          count: this.pageSize,
        }
        let res = await this.$api.fileDistribution.getFileDistributionTasks(params)
        this.pageTotal = res.total
        this.tableDataTaskList = res.info
        // console.log(this.tableDataTaskList[0].file)
        this.loadingTableData = false
        this.setTimer()
      },

      async getFileDistributionTaskOperators() {
        let res = await this.$api.fileDistribution.getFileDistributionTaskOperators()
        // console.log(res)
        this.optionFilterOperatorPeople = res
      },

      async createFileDistributionTask(params) {
        let data = await this.$api.fileDistribution.createFileDistributionTask(params)
        return data.data.data
      },

      async deleteFileDistributionTask(id) {
        this.loadingTableData = true
        this.$api.fileDistribution.deleteFileDistributionTask(id)
          .then(res => {
            // console.log(res)
            if (res.status === 204) {
              this.$message('任务取消')
            } else {
              this.$notify.error({
                title: 'Error Code:' + res.data.error_code,
                message: "任务取消失败",
              });
            }
            this.getFileDistributionTasks()
          })
          .catch(err => {
            this.$message.error('任务取消失败')
            this.getFileDistributionTasks()
          })
      },

      deleteFileDistributionFile(id) {
        return this.$api.fileDistribution.deleteFileDistributionFile(id)
      },

      putFileDistributionTask() {
        this.putFlag = true

        let cb = this.tableDataAddDevList
        let params = {}
        let machines = cb ? cb.map(item => item.moid) : null

        let createFlag = false

        this.tableDataUploadList && this.tableDataUploadList.length > 0 ? '' : createFlag = "提示：请选择文件"
        machines && machines.length > 0 ? params['machines'] = machines : createFlag = "提示：请选择服务器"
        this.inputDialogTaskPath ? params['remote_path'] = this.inputDialogTaskPath : createFlag = "提示：请输入分发路径"
        this.inputDialogTaskName ? params['task_name'] = this.inputDialogTaskName : createFlag = "提示：请输入任务名称"

        let uploadFileErrorFlag = this.tableDataUploadList.find(i => i.percentage === 'error')
        if (uploadFileErrorFlag) createFlag = "提示：请删除上传失败的文件"

        if (createFlag) {
          this.dialogErrorInfo = createFlag
          return false
        }

        let id = this.taskID
        params['begin_distribution_task'] = 1
        this.dialogVisibleTask = false
        this.$api.fileDistribution.putFileDistributionTask(id, params)
          .then(res => {
            if (res.data.success) {
              this.$message('任务执行中...');
            } else {
              let errInfo = '操作失败，' + res.data.msg
              this.$message.error(errInfo)
            }
            this.getFileDistributionTasks()
            this.dialogVisibleTask = false
          })
          .catch(err => {
            this.$message.error('任务执行失败')
            this.getFileDistributionTasks()
            this.dialogVisibleTask = false
          })
          .finally()
      },
      // api end

      // 定时器
      setTimer() {
        this.clearTimer();
        this.timer = setInterval(async () => {
          if (!this.dialogVisibleTask) {
            let flag = this.tableDataTaskList.find(i => i.status === 1)
            // 如果有正在执行的任务则重新获取数据刷新
            if (flag) {
              let params = {...this.lastSearchParams}
              params.start = (this.currentPage - 1) * this.pageSize
              params.count = this.pageSize
              // console.log(params)
              let res = await this.$api.fileDistribution.getFileDistributionTasks(params)
              this.pageTotal = res.total
              this.tableDataTaskList = res.info
            } else {
              this.clearTimer();
            }
          }
        }, 4000)
      },
      // 清楚定时器
      clearTimer() {
        clearInterval(this.timer);
        this.timer = null;
      },


      init() {
        // 调整当前route，变化侧边栏高亮
        let activeRouteList = ["/ops/operation/distribution", "/ops/operation"]
        this.$store.dispatch('activeRouteChange', activeRouteList)

        this.getFileDistributionTasks()
        this.getFileDistributionTaskOperators()
      }
    },
    mounted() {
      this.init()
    },

  }
</script>

<style>
  .discribtions .el-form-item__content {
    color: #9ca9b1;
    height: 19px;
  }

  .discribtions .el-form-item__label {
    color: #5d6266;
    height: 19px;
  }

  .file-distribution-ttdafo {
    position: absolute;
    z-index: 99;
    right: 0;
    top: -41px;
  }
</style>
