<template>
  <div class="theme-dark problemTrack" style='margin:20px 20px 0 26px;'>
    <div>
      <el-select
        v-model="problemTrackSearch.status"
        placeholder="请选择问题状态"
        style='width:140px;margin-right: 7px'
        popper-class="theme-dark"
        clearable>
        <el-option
          v-for='item in statusList'
          :key='item.value'
          :label='item.label'
          :value='item.value'></el-option>
      </el-select>
      <el-select
        v-model="problemTrackSearch.priority"
        placeholder="请选择优先级"
        style='width:140px;margin-right: 7px'
        popper-class="theme-dark"
        clearable>
        <el-option
          v-for='item in priorityList'
          :key='item.value'
          :label='item.label'
          :value='item.value'></el-option>
      </el-select>
      <el-input @keydown.enter.native='searchEnterFun' clearable placeholder="请输入问题编号、问题名称" v-model='problemTrackSearch.condition' maxlength="100" style='width:230px;margin-right: 7px'></el-input>
      <el-date-picker
        v-model="problemTrackSearch.searchTime"
        style="width: 320px;vertical-align: top;margin-right: 7px"
        type="datetimerange"
        range-separator=""
        start-placeholder="开始日期"
        end-placeholder="结束日期"
        popper-class="theme-dark"
        format="yyyy-MM-dd HH:mm"
        class="clear-close-icon"
        prefix-icon="ops-icons-bg icon-calendar"
        :clearable="false"
      >
      </el-date-picker>
      <el-button type="info" @click="onSubmit(problemTrackSearch)" :disabled="onSubmitDisabled">搜索</el-button>
      <div style='float: right;'>
        <el-button  @click="addProblem" :disabled="addProblemDisabled">新增</el-button>
        <el-button  @click="deleteProblem" :disabled="deleteProblemDisabled">删除</el-button>
        <el-button  @click="exportList" :disabled="reporterProblemDisabled">导出</el-button>
      </div>
    </div>
<!--下方表格-->
    <div>
      <el-table
        :data="problemData"
        stripe
        @selection-change="handleSelectionChange"
        :header-cell-class-name="setHeaderCellStyle"
        style="margin-top: 18px;"
        class='kd-script'
        v-loading="loadingTableData"
        element-loading-background="rgba(0, 0, 0, 0.5)">
        <el-table-column
          label='序号'
          type="index"
          show-overflow-tooltip
          min-width="10px"
        >
        </el-table-column>
        <el-table-column
          type="selection"
          show-overflow-tooltip
        >
        </el-table-column>
        <el-table-column
          prop="id"
          label="编号"
          min-width="193px"
          show-overflow-tooltip>
        </el-table-column>
        <el-table-column
          prop="issue"
          label="问题名称"
          min-width="160px"
          show-overflow-tooltip>
        </el-table-column>
        <el-table-column
          prop="statusChange"
          label="问题状态"
          min-width="200px"
          show-overflow-tooltip>
        </el-table-column>
        <el-table-column
          label="问题生成时间"
          min-width="190px"
          show-overflow-tooltip>
          <template slot-scope="scope">
            <span>{{new Date(scope.row.timeChange).format('Y m-d H:i')}}</span>
          </template>
        </el-table-column>
        <el-table-column
          prop="creator"
          label="创建人员"
          min-width="240px"
          show-overflow-tooltip>

        </el-table-column>
        <el-table-column
          prop="tracers"
          label="跟踪人员"
          min-width="221px"
          show-overflow-tooltip>
        </el-table-column>
        <el-table-column
          prop="options"
          label='操作'
          min-width="105"
          class='kd-script'
          show-overflow-tooltip>
          <template slot-scope="scope">
            <button type="button" class="button-host-info" @click="dialogDetail(scope.$index,problemData)">
              <span style="text-decoration: underline;">查看</span>
            </button>
            <button type="button" class="button-host-info" @click="dialogEdit(scope.$index,problemData)">
              <span style="text-decoration: underline;">修改</span>
            </button>
          </template>
        </el-table-column>
      </el-table>
    </div>
    <!--增加弹出框-->
    <el-dialog
      title="新增"
      :visible.sync="problemTrackAddDialog"
      width="500px"
      :close-on-click-modal="false"
      class=''>
      <div style="margin-top: 30px;color: #9ca9b1;font-size: 12px;">
        <span style="margin-right:32px">问题名称</span>
        <el-input v-model="addProblemInfo.issue" style="width:340px " maxlength="128" clearable placeholder="请输入问题名称"></el-input>
        <span style="color:#f56c6c;display: inline;margin-left:3px;">*</span>
      </div>
      <div style="margin-top: 20px;color: #9ca9b1;font-size: 12px;" class="questionDesc">
        <span style="margin-right:35px;width: 48px;float: left;">问题描述</span>
        <el-input v-model="addProblemInfo.detail" style="width:340px;display: inline-block " maxlength="1024" type="textarea" clearable></el-input>
      </div>
      <div style="margin-top: 20px;color: #9ca9b1;font-size: 12px;">
        <span style="margin-right:32px">问题状态</span>
        <el-select
          v-model="addProblemInfo.status"
          placeholder="请选择问题状态"
          style='width:340px'
          popper-class="theme-dark">
          <el-option
            v-for='item in statusList'
            :key='item.value'
            :label='item.label'
            :value='item.value'></el-option>
        </el-select>
        <span style="color:#f56c6c;display: inline;margin-left:3px;">*</span>
      </div>
      <div style="margin-top: 20px;color: #9ca9b1;font-size: 12px;">
        <span style="margin-right:32px">客户名称</span>
        <el-input v-model="addProblemInfo.customer" style="width:340px " maxlength="64" clearable placeholder="请输入客户名称"></el-input>
      </div>
      <div style="margin-top: 20px;color: #9ca9b1;font-size: 12px;">
        <span style="margin-right:44px">版本号</span>
        <el-input v-model="addProblemInfo.version" style="width:340px " maxlength="32" clearable placeholder="请输入版本号"></el-input>
      </div>
      <div style="margin-top: 20px;color: #9ca9b1;font-size: 12px;">
        <span style="margin-right:44px">优先级</span>
        <el-select
          v-model="addProblemInfo.priority"
          placeholder="请选择优先级"
          style='width:340px;'
          popper-class="theme-dark">
          <el-option
            v-for='item in priorityList'
            :key='item.value'
            :label='item.label'
            :value='item.value'></el-option>
        </el-select>
        <span style="color:#f56c6c;display: inline;margin-left:3px;">*</span>
      </div>
      <div style="margin-top: 20px;color: #9ca9b1;font-size: 12px;">
        <span style="margin-right:8px">问题生成时间</span>
        <el-date-picker
          v-model="addProblemInfo.begin_time"
          type="datetime"
          range-separator=""
          placeholder="请选择问题生成时间"
          popper-class="theme-dark"
          class="clear-close-icon"
          format="yyyy-MM-dd HH:mm"
          prefix-icon="ops-icons-bg icon-calendar"
          :clearable=false
          style='width: 340px;'
					:picker-options="pickerOptions0"
        >
        </el-date-picker>
        <span style="color:#f56c6c;display: inline;margin-left:3px;">*</span>
      </div>
      <div style="margin-top: 20px;color: #9ca9b1;font-size: 12px;">
        <span style="margin-right:32px">跟踪人员</span>
        <el-input v-model="addProblemInfo.tracers" style="width:340px" maxlength="128" clearable placeholder="请输入跟踪人员"></el-input>
        <span style="color:#f56c6c;display: inline;margin-left:3px;">*</span>
      </div>
      <div style="margin-top: 20px;color: #9ca9b1;font-size: 12px;">
        <span style="margin-right:56px">备注</span>
        <el-input v-model="addProblemInfo.postscript" style="width:340px" maxlength="1024" clearable placeholder="请输入备注"></el-input>
      </div>
      <div align='center' slot='footer' class='theme-dark' style='margin-top:30px;padding-bottom: 10px'>
        <el-button @click='problemTrackAddDialogEnd'>确定</el-button>
        <el-button @click='problemTrackAddDialog = false'>取消</el-button>
      </div>
    </el-dialog>

    <!--详情弹出框-->
    <el-dialog
      title="详情"
      :visible.sync="problemTrackDetailDialog"
      width="500px"
      :close-on-click-modal="false"
      class=''>
      <div style="margin-top: 30px;color: #9ca9b1;font-size: 12px;">
        <span style="margin-right:56px;float: left">编号</span>
        <span v-model="checkProblemInfo.id" style="width:340px ">{{checkProblemInfo.id}}</span>
      </div>
        <div style="margin-top: 20px;color: #9ca9b1;font-size: 12px;">
          <span style="margin-right:32px;float: left">问题名称</span>
          <span v-model="checkProblemInfo.issue" style="width:340px;max-height:26px;overflow:auto;display: inline-block;white-space: pre-line;overflow-wrap: break-word;" >{{checkProblemInfo.issue}}</span>
        </div>
        <div style="margin-top: 20px;color: #9ca9b1;font-size: 12px;">
          <span style="margin-right:32px;float: left">问题描述</span>
          <span v-model="checkProblemInfo.detail" style="width:340px;max-height:60px;overflow:auto;display: inline-block;white-space: pre-line;overflow-wrap: break-word; ">{{checkProblemInfo.detail}}</span>
        </div>
        <div style="margin-top: 20px;color: #9ca9b1;font-size: 12px;">
          <span style="margin-right:32px;float: left">问题状态</span>
          <span v-model="checkProblemInfo.statusChange" style="width:340px;max-height:26px;overflow:auto;display: inline-block;white-space: pre-line;overflow-wrap: break-word;">{{checkProblemInfo.statusChange}}</span>
        </div>
        <div style="margin-top: 20px;color: #9ca9b1;font-size: 12px;">
          <span style="margin-right:32px;float: left">客户名称</span>
          <span v-model="checkProblemInfo.customer" style="width:340px;max-height:26px;overflow:auto;display: inline-block;white-space: pre-line;overflow-wrap: break-word;">{{checkProblemInfo.customer}}</span>
        </div>
        <div style="margin-top: 20px;color: #9ca9b1;font-size: 12px;">
          <span style="margin-right:44px;float: left">版本号</span>
          <span v-model="checkProblemInfo.version" style="width:340px;max-height:26px;overflow:auto;display: inline-block;white-space: pre-line;overflow-wrap: break-word; ">{{checkProblemInfo.version}}</span>
        </div>
        <div style="margin-top: 20px;color: #9ca9b1;font-size: 12px;">
          <span style="margin-right:44px;float: left">优先级</span>
          <span v-model="checkProblemInfo.priorityChange" style="width:340px ">{{checkProblemInfo.priorityChange}}</span>
        </div>
        <div style="margin-top: 20px;color: #9ca9b1;font-size: 12px;">
          <span style="margin-right:8px;float: left">问题生成时间</span>
          <span v-model="checkProblemInfo.timeChange" style="width:340px;white-space: pre-line;word-break: break-all;word-wrap: break-word;overflow:auto; ">{{new Date(checkProblemInfo.timeChange).format('Y m-d H:i')}}</span>
        </div>
        <div style="margin-top: 20px;color: #9ca9b1;font-size: 12px;">
          <span style="margin-right:32px;float: left">创建人员</span>
          <span v-model="checkProblemInfo.creator" style="width:340px;max-height:60px;overflow:auto;display: inline-block;white-space: pre-line;overflow-wrap: break-word;">{{checkProblemInfo.creator}}</span>
        </div>
        <div style="margin-top: 20px;color: #9ca9b1;font-size: 12px;">
          <span style="margin-right:32px;float: left">跟踪人员</span>
          <span v-model="checkProblemInfo.tracers" style="width:340px;max-height:26px;overflow:auto;display: inline-block;white-space: pre-line;overflow-wrap: break-word;">{{checkProblemInfo.tracers}}</span>
        </div>
        <div style="margin-top: 20px;color: #9ca9b1;font-size: 12px;">
          <span style="margin-right:56px;float: left">备注</span>
          <div style="max-height: 100px;overflow: auto;margin-top: 10px">
            <span v-model="checkProblemInfo.postscript" style="width:340px;max-height:26px;overflow:auto;display: inline-block;white-space: pre-line;overflow-wrap: break-word; ">{{checkProblemInfo.postscript}}</span>
          </div>
        </div>
        <div align='center' slot='footer' class='theme-dark' style='margin-top:30px;padding-bottom: 10px'>
          <el-button @click='problemTrackDetailDialog = false'>关闭</el-button>
        </div>
    </el-dialog>

    <!--修改弹出框-->

    <el-dialog
      title="修改"
      :visible.sync="problemTrackEditDialog"
      width="500px"
      :close-on-click-modal="false"
      class=''>
      <div style="margin-top: 30px;color: #9ca9b1;font-size: 12px;">
        <span style="margin-right:32px">问题名称</span>
        <el-input v-model="EditProblemInfo.issue" style="width:340px " maxlength="128" clearable  placeholder="请输入问题名称"></el-input>
        <span style="color:#f56c6c;display: inline;margin-left:3px;">*</span>
      </div>
      <div style="margin-top: 20px;color: #9ca9b1;font-size: 12px;" class="questionDesc">
        <span style="margin-right:35px;float: left;">问题描述</span>
        <el-input v-model="EditProblemInfo.detail" style="width:340px;" maxlength="1024" type="textarea" clearable></el-input>
      </div>
      <div style="margin-top: 20px;color: #9ca9b1;font-size: 12px;">
        <span style="margin-right:32px">问题状态</span>
        <el-select
          v-model="EditProblemInfo.status"
          placeholder="请选择问题状态"
          style='width:340px'
          popper-class="theme-dark">
          <el-option
            v-for='item in statusList'
            :key='item.value'
            :label='item.label'
            :value='item.value'></el-option>
        </el-select>
        <span style="color:#f56c6c;display: inline;margin-left:3px;">*</span>
      </div>
      <div style="margin-top: 20px;color: #9ca9b1;font-size: 12px;">
        <span style="margin-right:32px">客户名称</span>
        <el-input v-model="EditProblemInfo.customer" style="width:340px " maxlength="64" clearable  placeholder="请输入客户名称"></el-input>
      </div>
      <div style="margin-top: 20px;color: #9ca9b1;font-size: 12px;">
        <span style="margin-right:44px">版本号</span>
        <el-input v-model="EditProblemInfo.version" style="width:340px " maxlength="32" clearable  placeholder="请输入版本号"></el-input>
      </div>
      <div style="margin-top: 20px;color: #9ca9b1;font-size: 12px;">
        <span style="margin-right:44px"  >优先级</span>
        <el-select
          v-model="EditProblemInfo.priority"
          placeholder="请选择优先级"
          style='width:340px;'
          popper-class="theme-dark">
          <el-option
            v-for='item in priorityList'
            :key='item.value'
            :label='item.label'
            :value='item.value'></el-option>
        </el-select>
        <span style="color:#f56c6c;display: inline;margin-left:3px;">*</span>
      </div>
      <div style="margin-top: 20px;color: #9ca9b1;font-size: 12px;">
        <span style="margin-right:8px"  >问题生成时间</span>
        <el-date-picker
          v-model="EditProblemInfo.begin_time"
          type="datetime"
          range-separator=""
          placeholder="请选择问题生成时间"
          popper-class="theme-dark"
          class="clear-close-icon"
          format="yyyy-MM-dd HH:mm"
          prefix-icon="ops-icons-bg icon-calendar"
          :clearable=false
          style='width: 340px;'
					:picker-options="pickerOptions0"
        >
        </el-date-picker>
        <span style="color:#f56c6c;display: inline;margin-left:3px;">*</span>
      </div>
      <div style="margin-top: 20px;color: #9ca9b1;font-size: 12px;">
        <span style="margin-right:32px">跟踪人员</span>
        <el-input v-model="EditProblemInfo.tracers" style="width:340px" maxlength="128" clearable placeholder="请输入跟踪人员"></el-input>
        <span style="color:#f56c6c;display: inline;margin-left:3px;">*</span>
      </div>
      <div style="margin-top: 20px;color: #9ca9b1;font-size: 12px;">
        <span style="margin-right:56px">备注</span>
        <el-input v-model="EditProblemInfo.postscript" style="width:340px" maxlength="1024" clearable placeholder="请输入备注"></el-input>
      </div>
      <div align='center' slot='footer' class='theme-dark' style='margin-top:30px;padding-bottom: 10px'>
        <el-button @click='problemTrackEditDialogEnd'>确定</el-button>
        <el-button @click='problemTrackEditDialog = false'>取消</el-button>
      </div>
    </el-dialog>

    <!-- 删除提示框 -->
    <el-dialog title="提示" :visible.sync="delVisible" width="300px" top="15%" :close-on-click-modal="false">
      <div style="margin-top: 40px;margin-bottom: 20px;">
        <span style="margin-right: 7px;font-size: 14px;">
          <i class="ops-icons-bg icon-notice" style="vertical-align: bottom;"></i>
        </span>
        <span>删除不可恢复，是否确定删除？</span>
      </div>
      <div align='center' slot='footer' class='theme-dark' style='margin-top:10px;padding-bottom: 10px'>
        <el-button type="info" @click="deleteRowAll()">确 定</el-button>
        <el-button @click="delVisible = false">取 消</el-button>
      </div>
    </el-dialog>

    <div style='margin-top: 20px;'>
      <kdPagination
        @current-change='handleCurrentChange'
        :pageSize='pageSize'
        :currentPage='currentPage'
        :total='count'
        :disabled = "pageDisabled">
      </kdPagination>
    </div>
  </div>

</template>

<script>
    export default {
      name: "ProblemTrack",
      components:{																							//分页标签注册
        KdPagination: () => import('@/components/common/KdPagination.vue'),
      },
      data() {
        return{
					pickerOptions0:{																				//限制之后时间不能选择
						disabledDate: (time) => {
							return time.getTime() > Date.now() + 1;
						}
					},
          loadingTableData:false,
          statusList:[
            {label:"未处理",value:1},{label:"处理中",value:2},{label:"挂起",value:3},{label:"已处理",value:4},
          ],
          priorityList:[
            {label:"低",value:1},{label:"中",value:2},{label:"高",value:3},{label:"紧急",value:4},
          ],
          start:0,
          count:0,
          currentPage:1,
          pageDisabled:false,
          pageSize:15,
          problemTrackSearch:{},
          options:[],
          onSubmitDisabled:false,
          addProblemDisabled:false,
          deleteProblemDisabled:true,
          reporterProblemDisabled:true,
          problemData:[],
          problemTrackAddDialog:false,
          problemTrackEditDialog:false,
          addProblemInfo:{},
          EditProblemInfo:{},
          problemTrackDetailDialog:false,
          delVisible:false,
          multipleSelection:[],
          delAll:[],
          checkProblemInfo:{},
          begin_time:'',
          end_time:'',
        }
      },
      methods:{
        timestampToTime(timestamp) {                            //时间转换
          var date = new Date(timestamp);//时间戳为10位需*1000，时间戳为13位的话不需乘1000
          var Y = date.getFullYear() + '-';
          var M = (date.getMonth()+1 < 10 ? '0'+(date.getMonth()+1) : date.getMonth()+1) + '-';
          var D = (date.getDate()<10 ? '0'+date.getDate() : date.getDate()) + ' ';
          var h = (date.getHours()<10 ? '0'+date.getHours():date.getHours())  + ':';
          var m = (date.getMinutes()<10 ? '0'+date.getMinutes():date.getMinutes() ) + ':';
          var s = (date.getSeconds()<10 ? '0'+date.getSeconds():date.getSeconds()) ;
          return Y+M+D+h+m+s;
        },
        //默认请求
        getData(params) {
          this.addProblemDisabled = true
          this.loadingTableData = true
          this.onSubmitDisabled = true
          this.$api.problemTrack.getdata(params).then(res=>{
            if(res.data.success === 1){
              this.count = res.data.data.total
              for (var i in res.data.data.info) {
              for (var j in res.data.data.info[i]) {
                if (j === "status") {
                  if (res.data.data.info[i][j] === 1) {
                    res.data.data.info[i]["statusChange"] = "未处理"
                  } else if (res.data.data.info[i][j] === 2) {
                    res.data.data.info[i]["statusChange"] = "处理中"
                  } else if (res.data.data.info[i][j] === 3) {
                    res.data.data.info[i]["statusChange"] = "挂起"
                  } else if (res.data.data.info[i][j] === 4) {
                    res.data.data.info[i]["statusChange"] = "已处理"
                  }
                }
                if (j === "priority") {
                  if (res.data.data.info[i][j] === 1) {
                    res.data.data.info[i]["priorityChange"] = "低"
                  } else if (res.data.data.info[i][j] === 2) {
                    res.data.data.info[i]["priorityChange"] = "中"
                  } else if (res.data.data.info[i][j] === 3) {
                    res.data.data.info[i]["priorityChange"] = "高"
                  } else if (res.data.data.info[i][j] === 4) {
                    res.data.data.info[i]["priorityChange"] = "紧急"
                  }
                }
                if (j === "begin_time") {
                  res.data.data.info[i]["timeChange"] = this.timestampToTime(res.data.data.info[i][j])
                }
              }
            }
              this.problemData=res.data.data.info
              this.loadingTableData = false
              this.addProblemDisabled = false
              this.onSubmitDisabled = false
            }else if(res.data.success===0){
              this.loadingTableData = false
              this.addProblemDisabled = false
              this.onSubmitDisabled = false
          }}).catch(err=>{
            this.loadingTableData = false
            this.addProblemDisabled = false
            this.onSubmitDisabled = false
          })
        },
        //删除
        deleteProblem(){
          this.delVisible = true;		//显示删除弹框
          for (let i = 0; i < this.multipleSelection.length; i++){
            this.delAll.push(this.multipleSelection[i].id)
          }
        },
      //  增加
        addProblem(){
          this.addProblemInfo={}
          this.problemTrackAddDialog = true
        },
      //  导出
        exportList(){
          var list = []
          for (let i = 0; i < this.multipleSelection.length; i++){
            list.push(this.multipleSelection[i].id)
          }
          list = list.toString();
          var params = {"ids":list}
          this.$api.problemTrack.exportProblem(params)
            .then(res=>{
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
            }).catch(err=>{})
        },
      //  查看详情
        dialogDetail(index,val){
          this.checkProblemInfo=val[index]
          this.problemTrackDetailDialog = true
        },
      //  修改问题
        dialogEdit(index,val){
          this.problemTrackEditDialog = true
          this.EditProblemInfo = val[index]
        },
        //确认修改问题
        problemTrackEditDialogEnd(){
          this.$api.problemTrack.putData(this.EditProblemInfo).then(res=>{
            if(res.data.success===1){
              this.$message("修改成功")
              this.problemTrackEditDialog = false
              this.getData({"count":this.pageSize,"start":0})
            }else if(res.data.success===0){
              console.log(res.data.msg)
            }
          }).catch(err=>{})
        },
        //确定增加问题
        problemTrackAddDialogEnd(){
          this.$api.problemTrack.postData(this.addProblemInfo).then(res=>{
            if(res.data.success===1){
              this.$message("添加成功")
              this.problemTrackAddDialog = false
              this.getData({"count":this.pageSize,"start":0})
            }else if (res.data.success===0){
              console.log(res.data.msg)
            }
          }).catch(err=>{})
        },
        setHeaderCellStyle({row, column, rowIndex, columnIndex}){		//去掉表格前两项的竖杠
          if(columnIndex===0||columnIndex===1){
            return "el-table-th-noborder"
          }
        },
        handleSelectionChange(val){		//操作多选
          this.multipleSelection = val;
          if(this.multipleSelection.length!==0){
            this.reporterProblemDisabled = false
            this.deleteProblemDisabled = false
          }else {
            this.deleteProblemDisabled = true
            this.reporterProblemDisabled = true
          }
        },
      //  删除
        deleteRowAll(){
          var param = {"ids":this.delAll}
          this.$api.problemTrack.deleteProblem(param).then(res =>{
            this.multipleSelection = []
            this.delAll=[]
            if (res.data.success === 1){
              this.$message.success('删除成功')
              this.getData({"count":this.pageSize,"start":0})
            }
            else if (res.data.success === 0){
              this.$message.error('删除失败')
              console.log(res.data.msg);
            }
          }).catch(err=>{})
          this.delVisible = false;		//关闭提示框
        },
				searchEnterFun(e){									//enter搜索函数
					// console.log(e)
					var keyCode = window.event?e.keyCode:e.which;
					if(keyCode===13){
						this.onSubmit(this.problemTrackSearch)
					}
				},
        //查询
        onSubmit(val){
          if(!val.searchTime){
            this.begin_time=""
            this.end_time=""
          }else if(val.searchTime.length===2){
            this.begin_time =val.searchTime[0]
            this.end_time =val.searchTime[1]
          }

          var params={
            "begin_time":this.begin_time,
            "end_time":this.end_time,
            "condition":val.condition,
            "start":0,
            "count":this.pageSize,
            "status":val.status,
            "priority":val.priority,
          }
          this.getData(params)
        },
        //  分页
        handleCurrentChange(val){
          this.start = (val-1) * this.pageSize;  //为了规避同名导致点击页数跳转
          if (val =>0){
            var params = {
              "count":this.pageSize,
              "start": this.start,
              "begin_time":this.begin_time,
              "end_time":this.end_time,
              "condition":this.problemTrackSearch.condition,
              "status":this.problemTrackSearch.status,
              "priority":this.problemTrackSearch.priority,
            }
            this.getData(params)
            }
        },
      },
      mounted(){
        this.getData({"count":this.pageSize,"start":0})
      },
    }
</script>

<style >
  .problemTrack .el-dialog__body{
      padding:0 30px   ;
  }
  .problemTrack .el-textarea__inner{
    background-color:#1f2122;
    border:1px solid #383b3c;
    border-radius:0;
    color: #9ca9b1;
    padding:5px 10px;
    height:50px;
    font: 12px"微软雅黑";
  }
  .questionDesc .el-textarea__inner{
    height: 60px !important;
    background-color: #1f2122;
    border-radius: 0;
    border: 1px solid #383b3c;
    color:#9ca9b1;
    padding: 5px 10px;
    font: 12px "微软雅黑";
  }
  .problemTrack {

  }
</style>
