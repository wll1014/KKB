<template>
	<div class='theme-dark '>
		<div>
			<!-- 上方表单 -->
			<div >
        <el-date-picker
          v-model='datePickerInstantTask'
          style="width: 322px;vertical-align: top;margin-right: 7px"
          type="datetimerange"
          range-separator=""
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          popper-class="theme-dark"
          format="yyyy-MM-dd HH:mm"
          value-format="timestamp"
          class="clear-close-icon"
          prefix-icon="ops-icons-bg icon-calendar"
          :clearable=false
        >
        </el-date-picker>
        <el-input placeholder="请输入任务名称搜索" v-model='inputFilterFileName' style="width: 180px;margin-right: 7px" @keyup.enter.native="search" maxlength="100"></el-input>
        <el-select filterable placeholder='全部操作人员' v-model='optionSelectedFilterPeople' popper-class="theme-dark" style="width: 240px;margin-right: 7px">
          <el-option v-for="item in optionFilterPeople"
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
          <el-button @click='createTask'>创建即时任务</el-button>
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
					<el-table-column label="任务开始时间" min-width='151px' show-overflow-tooltip>
            <template slot-scope="scope">
              <span>{{new Date(scope.row.begin_timestamp).format('Y m-d H:i')}}</span>
            </template>
          </el-table-column>
					<el-table-column label="任务执行时长" min-width='90px' show-overflow-tooltip>
            <template slot-scope="scope">
              <span>{{parseFloat(scope.row.duration).toFixed(1)}} 秒</span>
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
					<el-table-column label="操作" >
            <template slot-scope="scope">
              <button type="button" class="button-host-info" @click="showTaskDetail(scope.row)" style='padding-right: 10px;' >
                <span style="text-decoration: underline;">详情</span>
              </button>
              <button type="button" class="button-host-info" @click="showTaskReStartDialog(scope.row)" style='padding-right: 10px;' v-if="scope.row.status === 3">
                <span style="text-decoration: underline;">再次执行</span>
              </button>
              <!--<el-popover
                placement="top"
                width="135"
                v-model="scope.row.visiblePopoverDel"
                popper-class="theme-dark">
                <p style="margin-bottom: 10px;font-size: 14px;">确认再次执行？</p>
                <div style="text-align: left; margin: 0">
                  <el-button type="primary" size="mini" @click="createRealTimeTask(scope.row)">确定</el-button>
                  <el-button size="mini" type="text" @click="scope.row.visiblePopoverDel = false">取消</el-button>
                </div>
                <button slot="reference" type="button" class="button-host-info" style='padding-right: 10px;' >
                  <span style="text-decoration: underline;">再次执行</span>
                </button>
              </el-popover>-->

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
        <div style="margin-top: 20px;padding: 0px 15px;" v-if="dialogShowContent === 'create'">
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
          <div style="margin-bottom: 41px;">
            <span style="width: 75px;display: inline-block;font-size: 12px;">脚本参数</span>
            <div style="display: inline-block;">
              <el-input clearable v-model='inputDialogScriptParams' style="width: 650px;" maxlength="100"></el-input>
            </div>
          </div>
          <div style="margin-bottom: 20px;font-size: 12px;">执行范围({{tableDataAddDevList.length}})</div>
          <div style="height: 350px;">
          <TheTableDevAddFromOrganization ref="instantTaskTheTDAFO"
                                          @data-change="addFromOrganizationDevChange"
                                          :customParams="{device_type:0}"
                                          buttonClass="button-instant-task--dialog"></TheTableDevAddFromOrganization>
          </div>
        </div>
        <div style="margin-top: 20px;padding: 0px 15px;" class="instanttask-dialog__detail" v-if="dialogShowContent === 'detail'">
          <div>
            <span>任务名称</span>
            <span style="max-height:26px;overflow:auto;display: inline-block;white-space: pre-line;overflow-wrap: break-word;width:540px;">{{taskDetailInfo.task_name}}</span>
          </div>
          <div>
            <span>脚本选择</span>
            <span style="width: 270px;max-height:26px;overflow:auto;display: inline-block;white-space: pre-line;overflow-wrap: break-word;">{{taskDetailInfo.script ? taskDetailInfo.script.filename:''}}</span>
            <span>操作人员</span>
            <span>{{taskDetailInfo.operator}}</span>
          </div>
          <div>
            <span>任务开始时间</span>
            <span style="width: 270px;">{{new Date(taskDetailInfo.begin_timestamp).format('Y m-d H:i:s')}}</span>
            <span>任务执行时长</span>
            <span>{{parseFloat(taskDetailInfo.duration).toFixed(1)}} 秒</span>
          </div>
          <div>
            <span>任务状态</span>
            <span :class="[taskDetailInfo.status === 1 ? 'task--executing': taskDetailInfo.status === 3 ? 'task--failed':'']">{{objTaskStatu[taskDetailInfo.status]}}</span>
          </div>
          <div>
            <span>执行范围({{tableDataDialogTaskInfo.length}})</span>
          </div>
          <!-- 表格展示 -->
          <div style="height: 350px">
            <el-table
              tooltip-effect="dark"
              stripe
              border
              style="width: 100%;"
              max-height="350"
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
            <el-button @click="createRealTimeTask()" v-if="dialogShowContent === 'create'">确 定</el-button>
            <el-button @click="dialogVisibleInstantTask = false">{{dialogShowContent === 'create' ? '取 消' : '关 闭'}}</el-button>
          </span>
        </div>
      </el-dialog>

      <!--再次执行蒙版-->
      <el-dialog title="提示" :visible.sync="dialogVisibleRestart" @closed="beforeCloseClearReStartInfo" width="550px" top="15%">
        <div style="margin-top: 40px;margin-bottom: 20px;margin-left: 20px">
          <span style="margin-right: 7px;font-size: 14px;">
            <i class="ops-icons-bg icon-notice" style="vertical-align: bottom;"></i>
          </span>
          <span style="margin-bottom: 10px;">确定再次执行所选任务吗？</span>
          <div style="color: #ff6666;margin: 10px 0px;font-size: 12px;">{{dialogErrorInfo}}</div>
          <div>
            <span style="width: 75px;display: inline-block;font-size: 12px;">新任务名称</span>
            <div style="display: inline-block;">
              <el-input clearable v-model='inputDialogTaskName' style="width: 350px;" maxlength="64"></el-input>
            </div>
          </div>

        </div>
        <div align='center' slot='footer' class='theme-dark' style='margin-top:10px;padding-bottom: 10px'>
          <el-button type="info" @click="createRealTimeTask(activedRestatRow)">确 定</el-button>
          <el-button @click="dialogVisibleRestart = false">取 消</el-button>
        </div>
      </el-dialog>
      <!--蒙版区域end-->
		</div>
	</div>
</template>


<script>
export default {
  components:{
    KdPagination: () => import('@/components/common/KdPagination.vue'),
    TheTableDevAddFromOrganization: () => import('@/components/hostmanage/TheTableDevAddFromOrganization.vue'),
  },
  name:'ScriptInstantTask',
  computed:{

  },
  data() {
    return {
      timer:null,
      lastSearchParams:{},

      datePickerInstantTask:null,

      inputFilterFileName:null,

      optionSelectedFilterPeople:null,
      optionFilterPeople:[],

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
        label:'执行成功',
        value:2,
      },
      {
        label:'执行失败',
        value:3,
      },],
      objTaskStatu:{
        1:'正在执行...',
        2:'执行成功',
        3:'执行失败',
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
        'detail':'即时任务信息',
        'create':'创建即时任务'
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

      // 再次执行页面
      dialogVisibleRestart:false,
      activedRestatRow:null,
      dialogErrorInfo:null,
      // 蒙版数据 end
    }
  },
  methods: {

    // 组件回调函数
    // 分页变化回调
    pageHandleCurrentChange(val) {
      // console.log(val)
      this.currentPage = val
      this.getRealTimeTasks()
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
    },
    // 组件回调函数end

    // 页面内函数
    search(){												//搜索
      this.currentPage=1
      this.getRealTimeTasks()
      this.lastSearchParams={
        start_time : this.datePickerInstantTask ? this.datePickerInstantTask[0]:null,
        end_time : this.datePickerInstantTask ? this.datePickerInstantTask[1]:null,
        search : this.inputFilterFileName? this.inputFilterFileName:null,
        status : this.optionSelectedTaskStatu && this.optionSelectedTaskStatu!=='all' ? this.optionSelectedTaskStatu: null,
        operator : this.optionSelectedFilterPeople ? this.optionSelectedFilterPeople:null,
      }
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
      this.getRealTimeTaskInfo(row.id)
      this.dialogShowContent='detail'
      this.dialogVisibleInstantTask=true
    },
    showTaskReStartDialog(row){
      this.activedRestatRow = row
      let timestamp = parseInt(new Date().getTime()/1000)
      // timestamp =timestamp.format('_Y-m-d\\TH:i:s\\Zv')

      let newTaskName = row.task_name.replace(/_再次执行[0-9]{10}/g,'') + "_再次执行" + timestamp
      if(newTaskName.length > 64){
        this.dialogErrorInfo = "任务名称长度超过限制(>64个字符)，请重新输入"
        // newTaskName = row.task_name
      }
      this.inputDialogTaskName = newTaskName
      this.dialogVisibleRestart = true
    },
    beforeCloseClearReStartInfo(){
      this.activedRestatRow = null
      this.inputDialogTaskName = null
      this.dialogErrorInfo = null
    },
    // api start
    async getRealTimeTasks(){
      this.loadingTableData=true
      let params = {
        start_time : this.datePickerInstantTask ? this.datePickerInstantTask[0]:null,
        end_time : this.datePickerInstantTask ? this.datePickerInstantTask[1]:null,
        search : this.inputFilterFileName? this.inputFilterFileName:null,
        status : this.optionSelectedTaskStatu && this.optionSelectedTaskStatu!=='all' ? this.optionSelectedTaskStatu: null,
        operator : this.optionSelectedFilterPeople ? this.optionSelectedFilterPeople:null,
        start:(this.currentPage-1)*this.pageSize,
        count:this.pageSize,
      }
      // console.log(params)
     let res = await this.$api.script.getRealTimeTasks(params)
      // console.log(res)
     this.pageTotal=res.total
     this.tableDataTaskList=res.info
     this.loadingTableData=false
     this.setTimer()

    },

    async getRealTimeTaskInfo(id){
      let res = await this.$api.script.getRealTimeTaskInfo(id)
      this.taskDetailInfo=res
      this.tableDataDialogTaskInfo=res.machines
    },

    async getRealTimeTaskOperators(){
      let res = await this.$api.script.getRealTimeTaskOperators()
      // console.log(res)
      this.optionFilterPeople=res

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
        temCacheLength=data.length
        start=start+temCacheLength
        temCache=temCache.concat(data)
      }
      return temCache
    },

    async createRealTimeTask(val){
      // // 暂时限制权限
      // this.$notify({
      //   title:'账号无权限'
      // })
      // return false
      // // 暂时限制权限 end

      let params={}
      if(val){  //点击再次执行时的参数
        if(this.inputDialogTaskName && this.inputDialogTaskName.length > 64) return false //当长度超过64字符时不允许提交
        params={
          machines:val.machines,
          script:val.script.id,
          task_name:this.inputDialogTaskName,
          script_params:val.script_params ? val.script_params:'',
        }
      }else{  //蒙版内添加任务时的参数
        let machines = this.tableDataAddDevList.map(item=>item.moid)
        params={
          machines:machines,
          script:this.optionDialogSelectedScritName,
          task_name:this.inputDialogTaskName,
          script_params:this.inputDialogScriptParams ? this.inputDialogScriptParams:'',
        }
      }

      await this.$api.script.createRealTimeTask(params)
        .then(res => {
          if(res.data.success){
            this.$message('创建成功');
          }else{
            let errInfo = '创建失败，' + res.data.msg
            this.$message.error(errInfo)
          }
        })
        .catch(err => {
          this.$notify.error({
            title: '创建失败',
          });
        })

      this.getRealTimeTasks()
      this.dialogVisibleInstantTask=false
      this.dialogVisibleRestart = false
    },
    // api end

    // 定时器
    setTimer(){
      this.clearTimer();
      this.timer = setInterval(async () => {
        if(!this.dialogVisibleInstantTask){
          let flag = this.tableDataTaskList.find(i=>i.status===1)
          // console.log(flag)
          if(flag){
            let params = {...this.lastSearchParams}
            params.start = (this.currentPage-1) * this.pageSize
            params.count = this.pageSize
            // console.log(params)
            let res = await this.$api.script.getRealTimeTasks(params)
            // console.log(res)
            this.pageTotal=res.total
            this.tableDataTaskList=res.info
          }else{
            this.clearTimer();
          }
        }
      },4000)
    },
    // 清楚定时器
    clearTimer(){
      clearInterval(this.timer);
      this.timer = null;
    },

    init(){
      this.getRealTimeTasks()
    },

  },
  mounted(){
    this.init()
    this.getRealTimeTaskOperators()
  },
  beforeDestroy () {
    this.clearTimer()
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
