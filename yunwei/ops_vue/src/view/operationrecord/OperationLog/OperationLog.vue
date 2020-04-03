<template>
	<div class='theme-dark' style='padding:20px 20px 0 26px;'>
		<div>
			<!-- <el-input placeholder="请输入用户名" v-model='formInLine.username' style='width:230px;margin-right: 7px' maxlength="100"></el-input> -->
			<el-select 
			v-model="formInLine.opertype" 
			placeholder="操作类型"
			style='width:140px;margin-right: 7px'
			popper-class="theme-dark"
			clearable>
				<el-option
					v-for="item in options1"
					:key="item.value"
					:label="item.label"
					:value="item.value">
				</el-option>
			</el-select>
			<el-date-picker
      v-model="formInLine.time"
      style="width: 320px;vertical-align: top;margin-right: 7px"
      type="datetimerange"
      range-separator=""
      start-placeholder="开始日期"
      end-placeholder="结束日期"
      popper-class="theme-dark"
      value-format="timestamp"
      format="yyyy-MM-dd HH:mm"
      class="clear-close-icon"
      prefix-icon="ops-icons-bg icon-calendar"
      :clearable="false"
				>
			</el-date-picker>
			<el-button type="info" @click="onSubmit('formInLine')" :disabled="onSubmitDisabled">查询</el-button>
			<el-button style='float: right;' @click="exportList" :disabled="reporterDisabled">导出</el-button>
		</div>
		<!-- 表格 -->
		<div >
			<el-table
				:data="tableData"
				stripe
				style="margin-top: 18px;"
				class='kd-script'
        v-loading="loadingTableData"
        element-loading-background="rgba(0, 0, 0, 0.5)">
				<template>
					<el-table-column
						label='序号'
						type="index">
					</el-table-column>
					<el-table-column
						prop="username"
						label="用户名"
            min-width="193px">
					</el-table-column>
          <el-table-column
            prop="ip"
            label="IP地址"
            min-width="160px">
          </el-table-column>
					<el-table-column
						label="操作时间"
            min-width="200px">
            <template slot-scope="scope">
              <span>{{new Date(scope.row.time).format('Y-m-d H:i')}}</span>
            </template>
					</el-table-column>
					<el-table-column
						prop="opertype"
						label="操作类型"
            min-width="190px">
					</el-table-column>
					<el-table-column
						prop="operdesc"
						label="操作内容"
            min-width="230px">
					</el-table-column>
					<el-table-column
						prop="operrest"
						label="操作结果"
            min-width="221px">
					</el-table-column>
					<el-table-column
						prop="detail"
						label="操作"
            min-width="105px">
						<template slot-scope="scope">
							<button type="button" class="button-host-info" @click="detailinfo(scope.$index,tableData)">
								<span style="text-decoration: underline;">详情</span>
							</button>
						</template>
					</el-table-column>
				</template>
			</el-table>
		</div>
		<!-- 页码 -->
		<div style="margin-top: 20px;">
			<KdPagination
			@current-change="handleCurrentChange" 
			:pageSize="pageSize"
			:currentPage="currentPage"
			:total="count"
      :disabled="pageDisabled">
			</KdPagination>
		</div>

    <el-dialog :visible.sync="diaDetailInfo" style="color: #9ca9b1" :close-on-click-modal="false" title='日志详情' width="500px" height='500px' class='kd-script kd-operationlog'>
      <div style="margin-top: 30px;color: #9ca9b1;font-size: 12px">
        <span style="margin-right:32px">操作用户</span>
        <span :v-model='info.username'>{{ info.username }}</span>
      </div>
      <div style="margin-top: 30px;color: #9ca9b1;font-size: 12px">
        <span style="margin-right:45px">IP地址</span>
        <span :v-model='info.ip'>{{ info.ip }}</span>
      </div>
      <div style="margin-top: 30px;color: #9ca9b1;font-size: 12px">
        <span style="margin-right:32px">操作时间</span>
        <span :v-model='info.time'>{{ new Date(info.time).format('Y-m-d H:i') }}</span>
      </div>
      <div style="margin-top: 30px;color: #9ca9b1;font-size: 12px">
        <span style="margin-right:35px">操作类型</span>
        <span :v-model='info.opertype'>{{ info.opertype }}</span>
      </div>
      <div style="margin-top: 30px;color: #9ca9b1;font-size: 12px">
        <span style="margin-right:35px">操作内容</span>
        <span :v-model='info.opertype'>{{ info.operdesc }}</span>
      </div>
      <div style="margin-top: 26px;margin-bottom: 26px;color: #9ca9b1;font-size: 12px">
        <span style="margin-right:32px">操作结果</span>
        <span :v-model='info.operrest' class='copy' >{{ info.operrest }}
        </span>
				<el-button class='tag' :data-clipboard-text='info.detail' style='float: right;' icon="ops-icons-bg icon-operation-log" circle @click='copyToClipboard(info.detail)'></el-button>
      </div>
      <div class='detailAllInfo' style="border: 1px solid #383b3c;overflow:auto;display: inline-block;white-space: pre-line;overflow-wrap: break-word;width: 430px;height: 80px">
        <span style="font-size: 12px;padding: 10px;">{{info.detail}}</span>
        <!--<el-input type="textarea"  v-model="info.detail" ></el-input>-->
      </div>
      <div align="center" slot='footer' style="margin-top:30px;padding-bottom: 10px">
        <el-button @click='diaDetailInfo=false'>关闭</el-button>
      </div>
    </el-dialog>
	</div>	
</template>
		
		
		
<script>
	import Clipboard from 'clipboard'
	export default {
    components:{
      KdPagination: () => import('@/components/common/KdPagination.vue'),
    },
		data() {
			return {
        loadingTableData:false, //数据获取时加载
        reporterDisabled:false,//导出按钮是否可点
        onSubmitDisabled:false, //查询按钮
        pageDisabled:false,     //分页按钮是否可点击
				diaDetailInfo:false, 		//详情弹出框
				info:{},								//详情表单
				pageSize:15,
				count:0,
				currentPage:1,        //初始页
				options1:[
					{label:'登录',value:1,},
					{label:'注销',value:2,}, 
					{label:'新增',value:3,}, 
					{label:'删除',value:4,}, 
					{label:'编辑',value:5,}, 
					{label:'上传',value:6,}, 
					// {label:'其他',value:7,}, 
					
				],	
				formInLine: {              //搜索框的各项
					time: [],
					username: '',
				},			 
				tableData: [],             //数据接收传递
				startTime:"",
				endTime:"",
        startcount:0,             //开始条数

		}},
		methods:{
      timestampToTime(timestamp) {
        var date = new Date(timestamp);//时间戳为10位需*1000，时间戳为13位的话不需乘1000
        var Y = date.getFullYear() + '-';
        var M = (date.getMonth()+1 < 10 ? '0'+(date.getMonth()+1) : date.getMonth()+1) + '-';
        var D = (date.getDate()<10 ? '0'+date.getDate() : date.getDate()) + ' ';
        var h = (date.getHours()<10 ? '0'+date.getHours():date.getHours())  + ':';
        var m = (date.getMinutes()<10 ? '0'+date.getMinutes():date.getMinutes() ) + ':';
        var s = (date.getSeconds()<10 ? '0'+date.getSeconds():date.getSeconds()) ;
        return Y+M+D+h+m+s;
      },
			getaction(){   						//接收后端传来的数据
        this.loadingTableData = true;
        this.reporterDisabled=true;
        this.onSubmitDisabled=true;
        this.pageDisabled=true;
        var params={
          "start":0,
          "count":this.pageSize
        }
				this.$api.operationlog.getAction(params)
				.then(res=>{
					if (res.data.success === 1){
						this.count = res.data.data.total
            for (var i in res.data.data.info){
              res.data.data.info[i].time = this.timestampToTime(res.data.data.info[i].time)
            }
						this.tableData=res.data.data.info;
            this.loadingTableData =false;
            this.reporterDisabled= false;
            this.onSubmitDisabled= false;
            this.pageDisabled= false;
					}	
					else if (res.data.success === 0){
						console.log(res.data.msg);
            this.loadingTableData =false;
            this.reporterDisabled= false;
            this.onSubmitDisabled= false;
            this.pageDisabled= false;
					}
				}).catch(err=>{
          this.loadingTableData =false;
          this.reporterDisabled= false;
          this.onSubmitDisabled= false;
          this.pageDisabled= false;
        })
			},
			onSubmit(){  										//查询按钮
				if (!this.formInLine.time){   //处理当formInline为空的时候报错问题
					this.startTime= ''
					this.endTime =  ''
				}
				else if (this.formInLine.time.length === 2){
					this.startTime=this.formInLine.time[0]
					this.endTime = this.formInLine.time[1]
				}
				this.startcount = 0
        this.currentPage=1
				var params={ 									//降低传入后端参数
					"starttime":this.startTime,
					"endtime":this.endTime,
					// "username" :this.formInLine.username,
					"opertype":this.formInLine.opertype,
          "count":this.pageSize,
          "start":this.startcount
				}
        this.loadingTableData = true;
        this.reporterDisabled=true;
				this.onSubmitDisabled=true;
        this.pageDisabled=true;
				this.$api.operationlog.getAction(params)
				.then(res=>{
					if (res.data.success === 1){
            this.loadingTableData =false;
            this.reporterDisabled= false;
					  this.onSubmitDisabled=false
            this.pageDisabled=false
            this.count = res.data.data.total
            for (var i in res.data.data.info){
              res.data.data.info[i].time = this.timestampToTime(res.data.data.info[i].time)
            }
            this.tableData=res.data.data.info;
					}	
					else if (res.data.success === 0){
						console.log(res.data.msg);
            this.loadingTableData =false;
            this.reporterDisabled= false;
            this.onSubmitDisabled=false
            this.pageDisabled=false
					}	
				}).catch(err=>{
          this.loadingTableData =false;
          this.reporterDisabled= false;
				  this.onSubmitDisabled=false
          this.pageDisabled=false
        })
			},
      detailinfo(id,event){
        this.diaDetailInfo = true
        this.info = event[id]
			},
			handleCurrentChange(currentPage){   //点击第几页
        this.currentPage = currentPage
        if (currentPage>0){
          var startcount = (currentPage-1)*16 //为了规避同名导致点击页数跳转
          this.startcount = startcount
          var params = {
            "count": this.pageSize,
            "start": startcount,
            "starttime":this.startTime,
            "endtime":this.endTime,
            // "username" :this.formInLine.username,
						"opertype":this.formInLine.opertype,
          }
          this.loadingTableData = true;
          this.reporterDisabled=true;
          this.onSubmitDisabled=true;
          this.pageDisabled=true;
          this.$api.operationlog.getAction(params).then(res =>{
            if (res.data.success === 1){
              this.loadingTableData =false;
              this.reporterDisabled= false;
              this.onSubmitDisabled=false;
              this.pageDisabled=false;
              for (var i in res.data.data.info){
                res.data.data.info[i].time = this.timestampToTime(res.data.data.info[i].time)
              }
              this.tableData=res.data.data.info;
            }
            else if (res.data.success === 0){
              this.loadingTableData =false;
              this.reporterDisabled= false;
              this.onSubmitDisabled=false;
              this.pageDisabled=false;
              console.log(res.data.msg);
            }
          }).catch(err=>{
            this.loadingTableData =false;
            this.reporterDisabled= false;
            this.onSubmitDisabled=false;
            this.pageDisabled=false;
          })
        }

			},
			copyToClipboard(val){											//复制使用
				var clipboard = new Clipboard('.tag')
				clipboard.on('success',e => {
					this.$message('已复制到粘贴板')
					clipboard.destroy()		
				})
				clipboard.on('error', e => {
          this.$message('复制失败，请手动复制')
					clipboard.destroy()
				})
				if(!this.val){
					this.$message('无可复制内容')
				}
			},
      exportList(){                         //导出功能
        var params = {
          "count": this.pageSize,
          "start": this.startcount,
          "starttime":this.startTime,
          "endtime":this.endTime,
          // "username" :this.formInLine.username,
					"opertype":this.formInLine.opertype,
        }
        this.$api.operationlog.downloadOperationLog(params)
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
      }
		
		
		
		},
		mounted(){ 
			this.getaction();  //初始化加载
		},

};
</script>


<style>
.copy .el-button{
	background: #2b2b2b;
	border: #fff 1px solid;
	width:30px;
	height: 30px;

}
.kd-operationlog .el-textarea__inner{
  background-color: #1f2122;
  border-radius: 0;
  border: 1px solid #383b3c;
  height: 215px;
}
.kd-operationlog .el-dialog__body{
  padding: 0 35px;
}
.kd-operationlog .el-dialog__footer{
  padding-top: 0px;
}
.kd-operationlog .el-textarea__inner::-webkit-input-placeholder {
  color:#5d6266;
  font-size: 12px;
}

</style>
