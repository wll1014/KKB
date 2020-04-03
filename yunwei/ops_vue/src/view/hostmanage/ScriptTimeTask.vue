<template>
  <div class='theme-dark '>
    <div>
      <!-- 上方表单 -->
      <div >
        <el-input placeholder="请输入任务或脚本名称搜索"  v-model='inputFilterFileName' style="width: 180px;margin-right: 7px" @keyup.enter.native="search" maxlength="100"></el-input>
        <el-select filterable placeholder='全部操作人员' v-model='optionSelectedFilterOperatorPeople' popper-class="theme-dark" style="width: 240px;margin-right: 7px">
          <el-option v-for="item in optionFilterOperatorPeople"
                     :key="item"
                     :label="item"
                     :value="item">
          </el-option>
        </el-select>
        <el-select filterable placeholder='全部修改人员' v-model='optionSelectedFilterModifyPeople' popper-class="theme-dark" style="width: 200px;margin-right: 7px">
          <el-option v-for="item in optionFilterModifyPeople"
                     :key="item"
                     :label="item"
                     :value="item">
          </el-option>
        </el-select>
        <el-select filterable placeholder='全部任务状态' v-model='optionSelectedTaskStatu' popper-class="theme-dark" style="width: 180px;margin-right: 7px">
          <el-option v-for="item in optionTaskStatu"
                     :key="item.value"
                     :label="item.label"
                     :value="item.value">
          </el-option>
        </el-select>
        <el-button @click='search'>搜索</el-button>
        <span style="float: right;">
          <el-button @click='createTask'>创建定时任务</el-button>
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
          <el-table-column prop='script.filename' label="脚本名称" min-width='171px' show-overflow-tooltip></el-table-column>
          <el-table-column prop='operator' label="操作人员" min-width='128px'show-overflow-tooltip></el-table-column>
          <el-table-column label="任务创建时间" min-width='151px' show-overflow-tooltip>
            <template slot-scope="scope">
              <span>{{new Date(scope.row.create_timestamp).format('Y m-d H:i')}}</span>
            </template>
          </el-table-column>
          <el-table-column prop='last_modify_operator' label="任务修改人员" show-overflow-tooltip></el-table-column>
          <el-table-column label="最后修改时间" min-width='151px' show-overflow-tooltip>
            <template slot-scope="scope">
              <span>{{new Date(scope.row.last_modify_timestamp).format('Y m-d H:i')}}</span>
            </template>
          </el-table-column>
          <el-table-column label='任务状态' min-width='70px' show-overflow-tooltip>
            <template slot-scope="scope">
              <span :class="[scope.row.status === 1 ? 'task--executing': scope.row.status === 3 ? 'task--failed':'']">{{objTaskStatu[scope.row.status]}}</span>
            </template>
          </el-table-column>
          <el-table-column label='服务器数量' min-width='70px' show-overflow-tooltip >
            <template slot-scope="scope">
              <span>{{scope.row.machines.length}}</span>
            </template>
          </el-table-column>
          <el-table-column label="操作" min-width='151px'>
            <template slot-scope="scope">
              <button type="button" class="button-host-info" @click="showTaskDetail(scope.row)" style='padding-right: 10px;' >
                <span style="text-decoration: underline;">详情</span>
              </button>
              <button type="button" class="button-host-info" @click="editTaskDetail(scope.row)" style='padding-right: 10px;'>
                <span style="text-decoration: underline;">编辑</span>
              </button>
              <button type="button" class="button-host-info" @click="suspendTask(scope.row)" style='padding-right: 10px;'>
                <span style="text-decoration: underline;">{{scope.row.status === 1?'暂停':'开始'}}</span>
              </button>
              <!-- <el-popover
                placement="top"
                width="135"
                v-model="scope.row.visiblePopoverDel"
                popper-class="theme-dark">
                <p style="margin-bottom: 10px;font-size: 14px;">确认是否删除？</p>
                <div style="text-align: left; margin: 0">
                  <el-button type="primary" size="mini" @click="delCrontask(scope.row)">确定</el-button>
                  <el-button size="mini" type="text" @click="scope.row.visiblePopoverDel = false">取消</el-button>
                </div>
                <button slot="reference" type="button" class="button-host-info" style='padding-right: 10px;'>
                  <span style="text-decoration: underline;" >删除</span>
                </button>
              </el-popover> -->
							<button type="button" class="button-host-info" @click="delTaskDetail(scope.row)" style='padding-right: 10px;'>
							  <span style="text-decoration: underline;">删除</span>
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
        :title="objDialogTitle[dialogShowContent]"
        :visible.sync="dialogVisibleInstantTask"
        width="800px"
        append-to-body
        custom-class="theme-dark"
        @closed="beforeCloseClearNode"
      >
        <div style="margin-top: 20px;padding: 0px 15px;" v-if="dialogShowContent === 'create' || dialogShowContent === 'edit'">
          <div style="margin-bottom: 20px;">
            <span style="width: 75px;display: inline-block;font-size: 12px;">任务名称</span>
            <div style="display: inline-block;">
              <el-input clearable v-model='inputDialogTaskName' style="width: 650px;" maxlength="64"></el-input>
            </div>
          </div>
          <div style="margin-bottom: 20px;">
            <span style="width: 75px;display: inline-block;font-size: 12px;">脚本选择</span>
            <div style="display: inline-block;">
              <el-select style="width: 650px;"
                         filterable placeholder='请选择脚本'
                         v-model='optionDialogSelectedScritName'
                         popper-class="theme-dark instant-task-select">

                <el-option v-for="item in optionDialogScritName"
                           :key="item.id" :label="item.filename" :value="item.id">
                </el-option>
              </el-select>
            </div>
          </div>
          <div style="margin-bottom: 21px;">
            <span style="width: 75px;display: inline-block;font-size: 12px;">脚本参数</span>
            <div style="display: inline-block;">
              <el-input clearable v-model='inputDialogScriptParams' style="width: 650px;" maxlength="100"></el-input>
            </div>
          </div>
          <div style="color: #ff6666;margin-bottom: 10px;font-size: 12px;">{{dialogErrorInfo}}</div>
          <div style="height: 350px;">
            <CrontabTiming ref="crontabTaskTheCT" :devList="taskDetailInfo.machines" :initRules="taskDetailInfo.cron_rule"></CrontabTiming>
          </div>
        </div>
        <div style="margin-top: 20px;padding: 0px 15px;" class="instanttask-dialog__detail" v-if="dialogShowContent === 'detail'">
          <div>
            <span>任务名称</span>
            <span style="width: 540px;max-height:26px;overflow:auto;display: inline-block;white-space: pre-line;overflow-wrap: break-word;">{{taskDetailInfo.task_name}}</span>
          </div>
          <div>
            <span>脚本名称</span>
            <span style="width: 270px;max-height:26px;overflow:auto;display: inline-block;white-space: pre-line;overflow-wrap: break-word;">{{taskDetailInfo.script ? taskDetailInfo.script.filename:''}}</span>
            <span>操作人员</span>
            <span>{{taskDetailInfo.operator}}</span>
          </div>
          <div>
            <span>任务创建时间</span>
            <span style="width: 270px;">{{new Date(taskDetailInfo.create_time).format('Y m-d H:i:s')}}</span>
            <span>最后修改人员</span>
            <span>{{taskDetailInfo.last_modify_operator}}</span>
          </div>
          <div>
            <span>最后修改时间</span>
            <span style="width: 270px;">{{new Date(taskDetailInfo.last_modify_time).format('Y m-d H:i:s')}}</span>
            <span>执行规则</span>
            <span style="width: 220px;max-height:26px;overflow:auto;display: inline-block;white-space: pre-line;overflow-wrap: break-word;">{{rulesTrans(taskDetailInfo.cron_rule)}} </span>
          </div>
          <div>
            <span>任务状态</span>
            <span :class="[taskDetailInfo.status === 1 ? 'task--executing': taskDetailInfo.status === 3 ? 'task--failed':'']">{{objTaskStatu[taskDetailInfo.status]}}</span>
          </div>
          <div>
            <span>执行范围({{tableDataDialogTaskInfo.length}})</span>
          </div>
          <!-- 表格展示 -->
          <div style="height: 270px;">
            <el-table
              tooltip-effect="dark"
              stripe
              border
              max-height="270"
              style="width: 100%;"
              :data='tableDataDialogTaskInfo'>
              <el-table-column style='text-align: center;' min-width="53px" type='index' label="序号"></el-table-column>
              <el-table-column prop='name' label="服务器" show-overflow-tooltip></el-table-column>
              <el-table-column prop='room_name' label="所属平台域" show-overflow-tooltip></el-table-column>
              <el-table-column label='执行状态' show-overflow-tooltip >
                <template slot-scope="scope">
                  <span>{{objTaskStatu[scope.row.status]}}</span>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </div>
        <div style="padding: 30px;text-align: center;box-sizing: border-box;">
          <span style="text-align: center;" >
            <el-button @click="createCronTask()" v-if="dialogShowContent==='create'">确 定</el-button>
            <el-button @click="editCronTask('edit')"  v-if="dialogShowContent==='edit'">确 定</el-button>
            <el-button @click="dialogVisibleInstantTask = false" >{{dialogShowContent === 'detail' ? '关 闭' : '取 消'}}</el-button>
          </span>
        </div>
      </el-dialog>
			
			<!-- yp__start -->
			<el-dialog title="提示" :visible.sync="delVisible" width="300px" top="15%">
			  <div style="margin-top: 40px;margin-bottom: 20px;margin-left: 20px">
			        <span style="margin-right: 7px;font-size: 14px;">
			          <i class="ops-icons-bg icon-notice" style="vertical-align: bottom;"></i>
			        </span>
			    <span>确定删除所选任务吗？</span>
			  </div>
			  <div align='center' slot='footer' class='theme-dark' style='margin-top:10px;padding-bottom: 10px'>
			    <el-button type="info" @click="delCrontask(delInfo)">确 定</el-button>
			    <el-button @click="delVisible = false">取 消</el-button>
			  </div>
			</el-dialog>
			
			<el-dialog title="提示" :visible.sync="breakVisible" width="300px" top="15%">
			  <div style="margin-top: 40px;margin-bottom: 20px;margin-left: 20px">
			        <span style="margin-right: 7px;font-size: 14px;">
			          <i class="ops-icons-bg icon-notice" style="vertical-align: bottom;"></i>
			        </span>
			    <span>确定暂停所选任务吗？</span>
			  </div>
			  <div align='center' slot='footer' class='theme-dark' style='margin-top:10px;padding-bottom: 10px'>
			    <el-button type="info" @click="breakCronTask()">确 定</el-button>
			    <el-button @click="breakVisible = false">取 消</el-button>
			  </div>
			</el-dialog>
			<!-- yp__end -->
			
			
      <!--蒙版区域end-->
    </div>
  </div>
</template>


<script>
  export default {
    components:{
      KdPagination: () => import('@/components/common/KdPagination.vue'),
      CrontabTiming: () => import('@/components/hostmanage/CrontabTiming.vue'),
    },
    name:'ScriptTimeTask',
    computed:{

    },
    data() {
      return {

        inputFilterFileName:null,

        optionSelectedFilterOperatorPeople:null,
        optionFilterOperatorPeople:[],

        optionSelectedFilterModifyPeople:null,
        optionFilterModifyPeople:[],

        optionSelectedTaskStatu:null,
        optionTaskStatu:[{
          label:'全部任务状态',
          value:'all',
        },
          {
            label:'正在执行',
            value:1,
          },
          {
            label:'暂停执行',
            value:2,
          },
          {
            label:'任务创建失败',
            value:3,
          },],
        objTaskStatu:{
          1:'正在执行...',
          2:'暂停执行',
          3:'任务创建失败',
        },


        tableDataTaskList:[],
        loadingTableData:false,
        // 分页数据
        currentPage: 1,
        pageSize: 15,
        pageTotal:0,

        // 蒙版数据
        // 创建页面
        objDialogTitle:{
          'detail':'定时任务信息',
          'create':'创建定时任务',
          'edit':'修改定时任务'
        },
        dialogVisibleInstantTask:false,
        dialogShowContent:null,

        inputDialogTaskName:null,

        optionDialogSelectedScritName:null,
        optionDialogScritName:[],

        inputDialogScriptParams:null,

        tableDataAddDevList:[],

        // 详情页面
        taskDetailInfo:{},
        tableDataDialogTaskInfo:[],

        // 错误提示信息
        dialogErrorInfo:null,

        // 蒙版数据 end
				// yp__start
				delInfo:null,
				delVisible:false,
				breakVisible:false,
				breakInfo:{},
				// yp__end
      }
    },
    methods: {

      // 组件回调函数
      // 分页变化回调
      pageHandleCurrentChange(val) {
        // console.log(val)
        this.currentPage = val
        this.getCronTasks()
      },

      // 选择服务器回调
      addFromOrganizationDevChange(val){
        this.tableDataAddDevList=val
      },

      // 蒙版关闭回调
      beforeCloseClearNode(){
        this.dialogShowContent=null
        this.inputDialogTaskName=null,

        this.optionDialogSelectedScritName=null
        this.optionDialogScritName=[]

        this.inputDialogScriptParams=null

        this.tableDataAddDevList=[]

        // 详情页面
        this.taskDetailInfo={}
        this.tableDataDialogTaskInfo=[]

        // 错误提示信息
        this.dialogErrorInfo=null
      },
      // 组件回调函数end

      // 页面内函数
      search(){												//搜索
        this.currentPage=1
        this.getCronTasks()
      },

      async createTask(){										//创建即时任务

        // // 暂时限制权限
        // this.$notify({
        //   title:'账号无权限'
        // })
        // return false
        // // 暂时限制权限 end

        this.dialogShowContent='create'
        let data =await this.getScriptListForTask()
        this.optionDialogScritName=data

        this.dialogVisibleInstantTask=true
      },

      showTaskDetail(row){
        this.getCronTaskInfo(row.id)
        this.dialogShowContent='detail'
        this.dialogVisibleInstantTask=true
      },

      async editTaskDetail(row){

        // // 暂时限制权限
        // this.$notify({
        //   title:'账号无权限'
        // })
        // return false
        // // 暂时限制权限 end

        await this.getCronTaskInfo(row.id)
        this.inputDialogTaskName=this.taskDetailInfo.task_name
        this.inputDialogScriptParams=this.taskDetailInfo.script_params


        let scriptList = await this.getScriptListForTask()
        if( !scriptList ) { this.$message.error("脚本列表获取失败") ;return false}
        this.optionDialogScritName=scriptList
        this.optionDialogSelectedScritName=row.script.id

        this.dialogShowContent='edit'
        this.dialogVisibleInstantTask=true
      },

      suspendTask(row){
        // this.editCronTask(row)
				// yp__start
				this.breakInfo=row
				// console.log(this.breakInfo)
				if(row.status===1){
					this.breakVisible=true
				}else{
					this.editCronTask(row)
				}
				// yp__end
      },
			// yp__start
			breakCronTask(){
				this.editCronTask(this.breakInfo)
				this.breakVisible = false	
			},
			// yp__end
      rulesTrans(cornRule){
        let fullRulesList=["*","*","*","*","*",]
        if(cornRule){
          fullRulesList=[cornRule.minute.rule_str,
            cornRule.hour.rule_str,
            cornRule.day.rule_str,
            cornRule.month.rule_str,
            cornRule.weekday.rule_str]
        }


        return fullRulesList.join(' ')
      },

      // api start
      async getCronTasks(){
        this.loadingTableData=true
        let params = {
          search : this.inputFilterFileName? this.inputFilterFileName:null,
          status : this.optionSelectedTaskStatu && this.optionSelectedTaskStatu!=='all' ? this.optionSelectedTaskStatu: null,
          operator : this.optionSelectedFilterOperatorPeople ? this.optionSelectedFilterOperatorPeople:null,
          last_modify_operator: this.optionSelectedFilterModifyPeople ? this.optionSelectedFilterModifyPeople:null,
          start:(this.currentPage-1)*this.pageSize,
          count:this.pageSize,
        }
        let res = await this.$api.script.getCronTasks(params)
        this.pageTotal=res.total
        this.tableDataTaskList=res.info
        this.loadingTableData=false

      },

      async getCronTaskInfo(id){
        let res = await this.$api.script.getCronTaskInfo(id)
        this.taskDetailInfo=res
        this.tableDataDialogTaskInfo=res.machines
      },

      async getCronTaskOperators(){
        let res = await this.$api.script.getCronTaskOperators()
        // console.log(res)
        this.optionFilterOperatorPeople=res
      },
      async getCronTaskLastModifyOperators(){
        let res = await this.$api.script.getCronTaskLastModifyOperators()
        // console.log(res)
        this.optionFilterModifyPeople=res
      },

      async getScriptListForTask(){
        let start=0
        let count=50
        let temCacheLength=50
        let temCache=[]
        while (temCacheLength>=count){
          let params={
            start:start,
            count:count
          }
          let data=await this.$api.script.getScriptListForTask(params)
          if(!data){
            return null
          }
          temCacheLength=data.length
          start=start+temCacheLength
          temCache=temCache.concat(data)
        }
        return temCache
      },

      createCronTask(val){
        let cb = this.$refs.crontabTaskTheCT.getRules()
        let params={}
        let machines = cb.machines ? cb.machines.map(item=>item.moid) : null

        let createFlag=false

        machines ? '' : createFlag = "提示：请选择服务器"
        this.optionDialogSelectedScritName ? '' : createFlag = "提示：请选择脚本"
        this.inputDialogTaskName ? '' : createFlag = "提示：请输入任务名称"

        if(createFlag){
          this.dialogErrorInfo = createFlag
          return false
        }

        params={
          machines:machines,
          script:this.optionDialogSelectedScritName,
          task_name:this.inputDialogTaskName,
          script_params:this.inputDialogScriptParams ? this.inputDialogScriptParams:'',
          cron_rule:cb.cron_rule
        }

        this.$api.script.createCronTask(params)
          .then(res => {
            if(res.data.success){
              this.$message("创建成功")
            }else{
              let errInfo = '创建失败，' + res.data.msg
              this.$message.error(errInfo)
            }
            this.getCronTasks()
            this.dialogVisibleInstantTask=false
          })
          .catch(err => {
            this.$message.error("创建失败")
            this.getCronTasks()
            this.dialogVisibleInstantTask=false
          })

      },

      async editCronTask(val){
        let params={}
        let taskId=null
        if(val === 'edit'){
          let cb = this.$refs.crontabTaskTheCT.getRules()
          let machines = cb.machines ? cb.machines.map(item=>item.moid) : null

          let createFlag=false

          machines ? '' : createFlag = "提示：请选择服务器"
          this.optionDialogSelectedScritName ? '' : createFlag = "提示：请选择脚本"
          this.inputDialogTaskName ? '' : createFlag = "提示：请输入任务名称"

          if(createFlag){
            this.dialogErrorInfo = createFlag
            return false
          }

          params={
            machines:machines,
            status:this.taskDetailInfo.status,
            script:this.optionDialogSelectedScritName,
            task_name:this.inputDialogTaskName,
            script_params:this.inputDialogScriptParams ? this.inputDialogScriptParams:'',
            cron_rule:cb.cron_rule
          }

          taskId=this.taskDetailInfo.id
        }else{
          this.loadingTableData=true
          let res = await this.$api.script.getCronTaskInfo(val.id)
          params={
            machines:val.machines,
            status:val.status === 1 ? 2:1,
            script:val.script.id,
            task_name:val.task_name,
            script_params:val.script_params,
            cron_rule:res.cron_rule
          }
          taskId=val.id
        }

        this.$api.script.putEditCronTask(taskId,params)
          .then(res => {
            if(res.data.success){
              this.$message('修改成功');
            }else{
              let errInfo = '修改失败，' + res.data.msg
              this.$message.error(errInfo)
            }
            this.getCronTasks()
            this.dialogVisibleInstantTask=false
          })
          .catch(err => {
            this.$message.error('修改失败');
            this.getCronTasks()
            this.dialogVisibleInstantTask=false
          })

      },

      delCrontask(row){
        this.loadingTableData=true
        this.$api.script.deleteCronTask(row.id)
          .then(res => {
            // console.log(res)
            if(res.status === 204){
              this.$notify({
                message: "删除成功",
              });
            }else{
              this.$notify.error({
                title: 'Error Code:' + res.data.error_code,
                message: "删除失败",
              });
            }
            this.getCronTasks()
          })
          .catch(err => {
            this.$notify.error({
              title: '删除失败',
            });
            this.getCronTasks()
          })
          // this.$set(row,'visiblePopoverDel',false)
					// yp__start
        this.delVisible=false
					// yp__end
        this.delInfo = null
      },
      
			
			// yp__start
			delTaskDetail(val){
				this.delInfo = val
				this.delVisible=true
			},
			// yp__end
			// api end

      init(){
        this.getCronTasks()
      },

    },
    mounted(){
      this.init()
      this.getCronTaskOperators()
      this.getCronTaskLastModifyOperators()

    },

  }
</script>



<style>

  .task--failed{
    color: rgb(228, 89, 89);
  }
  .task--executing{
    color: #00a2ff;
  }
  .theme-dark .el-table--enable-row-hover .el-table__body tr:hover > td .task--executing{
    color: #fff;
  }
  .instant-task-select.el-select-dropdown{
    width: 650px;
  }
  .instant-task-select .el-select-dropdown__item{
    overflow: inherit;
  }
  .button-instant-task--dialog{
    top:-41px;
    right: 0;
    position: absolute;
    z-index: 99;
  }
  .instanttask-dialog__detail>div{
    margin-bottom: 30px;
  }
  .instanttask-dialog__detail>div:last-child{
    margin-bottom: 0px;
  }
  .instanttask-dialog__detail>div:nth-last-child(2){
    margin-bottom: 21px;
  }
  .instanttask-dialog__detail>div>span{
    display: inline-block;
    font-size: 12px;
    color: #9ca9b1;
    vertical-align: bottom;
  }
  .instanttask-dialog__detail>div>span.task--executing{
    color: #00a2ff;
  }
  .instanttask-dialog__detail>div>span.task--failed{
    color: rgb(228, 89, 89);
  }
  .instanttask-dialog__detail>div>span:first-child{
    width: 100px;
  }
  .instanttask-dialog__detail>div>span:nth-child(3){
    width: 100px;
  }
</style>
