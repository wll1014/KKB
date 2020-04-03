<template>
	<div class='theme-dark kd-script'>
			<!-- 上方表单 -->
		<el-date-picker
		v-model='scriptTop.formdata'
		style="width: 322px;vertical-align: top"
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
		<el-input clearable placeholder="请输入文件名称搜索" v-model='scriptTop.filename' maxlength="100" style='width:180px;margin-left: 7px' @keydown.enter.native='searchEnterFun'></el-input>
		<el-select clearable filterable placeholder='全部上传人员' v-model='scriptTop.person' popper-class="theme-dark" style='width:240px;;margin-left: 7px' >
			<el-option v-for="item in options"
				:key="item.value"
				:label="item.label"
				:value="item.value">
			</el-option>
		</el-select>
		<el-button @click='search("scriptTop")' style="margin-left: 7px" :disabled="searchDisabled">搜索</el-button>
		<el-button v-show='allShow' @click='getdata()' style="margin-left: 7px" :disabled="clearDisabled">还原</el-button>
		<el-button @click='del()' style="float: right;margin-left: 6px" :disabled="delDisabled">删除</el-button>
		<el-button @click='upScript()' style="float: right;" :disabled="upFileDisabled">上传脚本</el-button>
		<!-- 表格展示 -->
		<div class='kd-script'>
			<el-table 
			:data='script'
			stripe
			@selection-change="handleSelectionChange"
      :header-cell-class-name="setHeaderCellStyle"
			style="margin-top: 18px;"
      v-loading="loadingTableData"
      element-loading-background="rgba(0, 0, 0, 0.5)"
			>
				<el-table-column style='text-align: center;'  type='index' label="序号"></el-table-column>
				<el-table-column  type='selection'></el-table-column>
				<el-table-column label="上传日期" min-width="121px" show-overflow-tooltip>
          <template slot-scope="scope">
            <span>{{new Date(scope.row.upload_time).format('Y-m-d H:i')}}</span>
          </template>
        </el-table-column>
				<el-table-column prop='filename' label="脚本名称" min-width="171px" show-overflow-tooltip></el-table-column>
				<el-table-column prop='size' label="文件大小" min-width="90px" show-overflow-tooltip></el-table-column>
				<el-table-column prop='uploader' label="上传人员" min-width="130px" show-overflow-tooltip></el-table-column>
				<el-table-column prop='postscript' label="备注" min-width="300px" show-overflow-tooltip></el-table-column>
				<el-table-column prop="optionss" label="操作" min-width="100px">
					<template slot-scope="scope">
						<a :href="url" style='padding-right: 10px;' @click="updown(scope.row)" :download='downname'>
							<span style="text-decoration: underline;" class="button-host-info" >下载</span>
						</a>
						<button type="button" class="button-host-info" @click="remark(scope.row)">
							<span style="text-decoration: underline;">备注</span>
						</button>
					</template>
				</el-table-column>
			</el-table>
		</div>
		
		<!-- 文件选择弹出框 -->
		<el-dialog title='上传脚本' :visible.sync='dialogUp' :close-on-click-modal='false' width="800px" >
      <div style="margin-left: 15px;margin-top: 31px;float: left">文件列表</div>
      <el-upload
      class='upload-demo'
      ref="upload"
      :action='action'
      multiple
      :on-progress='handleProgress'
      :on-exceed='handleExceed'
      :on-success='handleSuccess'
      :on-change="handleChange"
      :file-list='fileList'
      :limit="5"
      style='float:right;padding-bottom: 6px;margin-top: 31px;margin-right: 15px;'
      :show-file-list='false'
      :before-upload='handleUpload'
      accept=".sh,.py"
      >
        <el-button>文件选择</el-button>
      </el-upload>
			<div style='padding-top:17px;margin-left: 15px' >
				<el-table stripe  :data='smallTable' height='400px' style='padding-top: 6px;background: none'>
					<el-table-column prop='index' type='index' label='序号' width="57px"></el-table-column>
					<el-table-column prop='name' show-overflow-tooltip label='文件名称' width="443px" ></el-table-column>
					<el-table-column prop='size' label='文件大小' width="103px"></el-table-column>
					<el-table-column prop='percentage' label='状态' width="124px">
						<template slot-scope="scope">
							<span style="color:#e45959;margin-right: 3px;" class="button-host-info" v-if="scope.row.percentage==='失败'">失败</span>
						<!-- 	<button type="button" class="button-host-info" @click='reupload(scope.row)' v-show="scope.row.percentage==='失败'">
								<span style="text-decoration: underline;">重新上传</span>
							</button> -->
							<span v-if="scope.row.percentage==='成功'">成功</span>
						</template>
					</el-table-column>
					<!--<button type='text' @click='reupload()' v-show='uploadError'>重新上传</button>-->
				</el-table> 
			</div>
      <div>
        <div style="padding-bottom: 9px">提示：</div>
        <div style="padding-bottom: 9px">1.文件格式仅限 "sh"和"py"，文件大小不超过2MB.</div>
        <div style="padding-bottom: 9px">2.上传的脚本必须为非交互式脚本，为确保安全，请先在本地调试通过后再上传。</div>
        <div style="padding-bottom: 9px">3.脚本执行的 "返回值"将作为系统判断执行成功或失败的标志 </div>
        <div style="padding-bottom: 9px">（"返回值"为0则判定为执行成功，"返回值"不为0则判定为执行失败。）</div>
      </div>
			<div align="center" slot='footer' class='theme-dark' style='margin-bottom:10px;'>
				<el-button @click='uploadClose("smallTable")' class='closeit' :disabled='false'>关闭</el-button>
        <span style='color: red;' v-show='closeScript' >脚本正在上传中，请勿关闭！</span><br>
			</div>
		</el-dialog>
		
		<!-- 备注弹出框 -->
		<el-dialog title='备注' :visible.sync="dialogRemark" :close-on-click-modal='false' class='theme-dark kd-script kd-remark' width="500px" style="color: #9ca9b1">
			<!--<span >-->
				<!--<el-form :model='remarkForm'-->
					<!--label-position="left"-->
					<!--label-width="70px"-->
					<!--style='margin: 20px 35px 0 15px;color: #9ca9b1'-->
					<!--&gt;-->
      <div style="margin-top: 30px;margin-bottom: 30px;color: #9ca9b1;font-size: 12px">
        <span style="margin-right:35px">上传日期</span>
        <span :v-model='remarkForm.upload_time'>{{ new Date(remarkForm.upload_time).format('Y-m-d H:i')}}</span>
      </div>
      <div style="margin-bottom: 30px;color: #9ca9b1;font-size: 12px">
        <span style="margin-right:35px;float: left;">脚本名称</span>
        <span :v-model='remarkForm.filename' style="width:340px;max-height:26px;overflow:auto;display: inline-block;white-space: pre-line;overflow-wrap: break-word;">{{ remarkForm.filename }}</span>
      </div>
      <div style="margin-bottom: 30px;color: #9ca9b1;font-size: 12px">
        <span style="margin-right:35px">文件大小</span>
        <span :v-model='remarkForm.size'>{{ remarkForm.size }}</span>
      </div>
      <div style="margin-bottom: 30px;color: #9ca9b1;font-size: 12px">
        <span style="margin-right:35px">上传人员</span>
        <span :v-model='remarkForm.uploader'>{{ remarkForm.uploader }}</span>
      </div>
      <div style="margin-bottom:16px;color: #9ca9b1;font-size: 12px">备注
        <span style="color: #5d6266;float: right" >仅限64个字符</span>
      </div>

      <el-input type='textarea' v-model='remarkForm.postscripts' placeholder="请输入备注" maxlength="64"></el-input>
      <!--</el-form>-->
      <div align='center' slot='footer' class='theme-dark' style='margin-top:30px;padding-bottom: 10px'>
        <el-button @click='dialogReSave'>保存</el-button>
        <el-button @click='dialogRemark = false'>取消</el-button>
      </div>
		</el-dialog>
		
		<!-- 删除提示框 -->
    <el-dialog title="提示" :visible.sync="delVisible" width="300px" top="15%" :close-on-click-modal="false">
      <div style="margin-top: 40px;margin-bottom: 20px;margin-left: 20px">
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

		
		<!-- 分页 -->
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
	import base from '@/api/base' // 导入接口域名列表
	export default {
    components:{																							//分页标签注册
      KdPagination: () => import('@/components/common/KdPagination.vue'),
    },
		name:'scriptList',
		data() {
			return {
        pageDisabled:false,
        searchDisabled:false,
        clearDisabled:false,
        delDisabled:true,
        upFileDisabled:false,
        loadingTableData:false,     //列表加载时提示框
				closeScript:false,					//脚本上传时触发关闭按钮后的显示
				options:[],
				uploadError:false,  				//上传失败时展示出重新上传字样
				start:0,
				count:0,
        pageSize:15,
				currentPage:1,
				script:[],									//界面上脚本的表格
				dialogUp:false, 						//文件选择弹出框
				fileList:[],								//上传脚本时文件的存放
				smallTable:[],							//上传脚本弹出框表格
				scriptTop:{},								//页面上方表单对象
				dialogRemark:false,					//备注的弹出框
				remarkForm:{},							//备注的表单
				delAll:[],									//删除时的id
				multipleSelection:[],				//删除时多选的数据
				allShow:false,							//还原键
				delVisible:false,						//删除按钮的弹框控制
        originData:{},              //存文件
				startTime:'',
				endTime:'',
				action:`${base.master}/hosts_oper/scripts/`,
				beurl:`${base.master}/`,
				url:'',
				downname:'',
			}
		},
		methods: {
			getdata(){										//初始加载
				this.allShow=false
        this.pageDisabled=true;
        this.searchDisabled=true;
        this.clearDisabled=true;
        this.delDisabled=true;
        this.upFileDisabled=true;
        this.loadingTableData=true;
        this.scriptTop={}
        var params={
          "start":this.start,
          "count":this.pageSize
        }
				this.$api.script.getscript(params).then(res =>{
					if (res.data.success === 1){
					  for (var message in  res.data.data.info){
              if (res.data.data.info[message].size/1024<1){															//判断size的单位
                res.data.data.info[message].size = res.data.data.info[message].size +'B'
              } else if(res.data.data.info[message].size / 1024 / 1024 < 1){
                var refile = res.data.data.info[message].size / 1024
                res.data.data.info[message].size = refile.toString().split('.')[0] +'KB'
              }else if (res.data.data.info[message].size /1024 / 1024 >= 1){
                var refile = res.data.data.info[message].size / 1024 / 1024
                res.data.data.info[message].size = refile.toString().split('.')[0] +'MB'
              }
            }
						this.script = res.data.data.info
						this.count = res.data.data.total
            this.pageDisabled=false;
            this.searchDisabled=false;
            this.clearDisabled=false;
            this.upFileDisabled=false;
            this.loadingTableData=false;
					}
					else if (res.data.success === 0){
						console.log(res.data.msg);
            this.pageDisabled=false;
            this.searchDisabled=false;
            this.clearDisabled=false;
            this.upFileDisabled=false;
            this.loadingTableData=false;
					}
				}).catch(err=>{
          this.pageDisabled=false;
          this.searchDisabled=false;
          this.clearDisabled=false;
          this.upFileDisabled=false;
          this.loadingTableData=false;
        })
				this.$api.script.getadminList().then(res =>{
					if (res.data.success === 1){
					  this.options=[]
						var lists = res.data.data
						for (var i=0 ; i < lists.length;i++){
							var a = lists[i]
							this.options.push({"label":a,"value":a})
						}
					}
					else if (res.data.success === 0){
						console.log(res.data.msg);
					}
				}).catch(err=>{})
			},
			handleSelectionChange(val){		//操作多选
				this.multipleSelection = val;
				if(this.multipleSelection.length===0){
				  this.delDisabled   = true
        }else {
				  this.delDisabled = false
        }
			},
			del(){ 												//删除
				const length = this.multipleSelection.length;
        this.delVisible = true;		//显示删除弹框
        for (let i = 0; i < length; i++){
          this.delAll.push(this.multipleSelection[i].id)
        }
			},
			deleteRowAll(){								//确定删除
				var param = {"ids":this.delAll}
				this.$api.script.deleteScript(param).then(res =>{
					this.multipleSelection = []
					this.delAll=[]
					if (res.data.success === 1){
						this.$message.success('删除成功')
						this.getdata()
					}
					else if (res.data.success === 0){
						this.$message.error('删除失败')
						console.log(res.data.msg);
					}
				}).catch(err=>{})
				this.delVisible = false;		//关闭提示框
			},
			upScript(){										//上传框弹出
				this.dialogUp=true    
				this.closeScript = false
				this.smallTable=[]					//清空表格文件
				this.fileList=[]						//清空上传文件列表
			},
			uploadClose(smallTable){			//关闭提示框
				if (this.event){
					// this.closeScript = true
				}else{
					this.dialogUp=false
				}
			},
			handleSuccess(res){							//文件上传成功时进行的操作
				this.disabled = false;
				this.closeScript = false;
        this.uploadError = false
        if (res.success === 0){
          for (var j=0; j<this.smallTable.length; j++){
            if (res.filename === this.smallTable[j].filename){
              this.smallTable[j].percentage = '失败'
              this.uploadError = true
              this.originData = res.raw
            }
          }
				}
				this.getdata()
			},
			handleExceed(files,fileList) {													//限制文件个数
				this.$message.warning(`当前限制选择 5 个文件`);
			},
			handleChange(file,fileList){
				// console.log(fileList)
				this.fileList = fileList
			},
			handleProgress(event,file,fileList){										//进度条
					// console.log(fileList)
					this.uploadError=false
					this.closeScript = true
					if (file.size/1024<1){															//判断size的单位
							file.size = file.size +'B'
					} else if(file.size / 1024 / 1024 < 1){
						var refile = file.size / 1024
						file.size = refile.toString().split('.')[0] +'KB'
					}else if (file.size /1024 / 1024 >= 1){
						var refile = file.size / 1024 / 1024
						file.size = refile.toString().split('.')[0] +'MB'
					}
					if(event){
						if (event.percent === 100){													//显示百分比
							event.percent = '成功'
						}else{
							event.percent = event.percent.toString().split('.')[0] + '%'
						}
					}
					this.smallTable = fileList													//表格赋值
				},
			handleUpload(file){																			//前期判断文件大小
        var testmsg=file.name.substring(file.name.lastIndexOf('.')+1)
			  const isType = testmsg === 'py' || testmsg === 'sh'
				const isLt2M = file.size /1024/1024 <2;
        if(!isType){
          this.$message.error('上传文件为sh或py格式')
          return false;
        }
				if (!isLt2M) {
					this.$message.error('上传文件大小不能超过2M')
					return false;
				}
				this.closeScript = true;
				this.disabled = true;
				},
			remark(row){																					//备注
			  this.dialogRemark = true
        this.remarkForm = {
          postscripts:row.postscript,
          upload_time:row.upload_time,
          filename:row.filename,
          size:row.size,
          uploader:row.uploader,
          id:row.id,
          url:row.url
        }
			},
			dialogReSave(){																					//保存备注
				this.$api.script.putscript(this.remarkForm).then(res=>{
					if (res.data.success === 1){
						this.$message.success('保存成功')
						this.getdata()
						this.dialogRemark = false
					}
					else if (res.data.success === 0){
						console.log(msg)
					}else{
						this.$message.error('未知错误')
					}
				}).catch(err=>{})
			},
			searchEnterFun(e){									//enter搜索函数
				// console.log(e)
				var keyCode = window.event?e.keyCode:e.which;
				if(keyCode===13){
					this.search()
				}
			},
			search(){			//搜索
        this.pageDisabled=true;
        this.searchDisabled=true;
        this.clearDisabled=true;
        this.delDisabled=true;
        this.upFileDisabled=true;
        this.loadingTableData=true;
				this.allShow = true;
				if (!this.scriptTop.formdata){
					this.startTime= ''
					this.endTime =  ''
				}
				else if (this.scriptTop.formdata.length === 2){
					this.startTime=this.scriptTop.formdata[0]
					this.endTime = this.scriptTop.formdata[1]
				}
				this.currentPage = 1
        this.start=0
				var params={ 							//降低传入后端参数
					"starttime":this.startTime,
					"endtime":this.endTime,
					"filename" :this.scriptTop.filename,
					"uploader":this.scriptTop.person,
          "count":this.pageSize,
          "start":this.start
				}
				this.$api.script.getscript(params).then(res=>{
					if (res.data.success === 1){
            this.count = res.data.data.total
            for (var message in  res.data.data.info){
              if (res.data.data.info[message].size/1024<1){															//判断size的单位
                res.data.data.info[message].size = res.data.data.info[message].size +'B'
              } else if(res.data.data.info[message].size / 1024 / 1024 < 1){
                var refile = res.data.data.info[message].size / 1024
                res.data.data.info[message].size = refile.toString().split('.')[0] +'KB'
              }else if (res.data.data.info[message].size /1024 / 1024 >= 1){
                var refile = res.data.data.info[message].size / 1024 / 1024
                res.data.data.info[message].size = refile.toString().split('.')[0] +'MB'
              }
            }
						this.script = res.data.data.info
            this.pageDisabled=false;
            this.searchDisabled=false;
            this.clearDisabled=false;
            // this.delDisabled=false;
            this.upFileDisabled=false;
            this.loadingTableData=false;
					}
					else if (res.data.success === 0){
						console.log(res.data.msg);
						this.pageDisabled=false;
            this.searchDisabled=false;
            this.clearDisabled=false;
            // this.delDisabled=false;
            this.upFileDisabled=false;
            this.loadingTableData=false;
					}else{
						this.$message.error('未知错误')
            this.pageDisabled=false;
            this.searchDisabled=false;
            this.clearDisabled=false;
            // this.delDisabled=false;
            this.upFileDisabled=false;
            this.loadingTableData=false;
					}
				}).catch(err=>{
          this.pageDisabled=false;
          this.searchDisabled=false;
          this.clearDisabled=false;
          // this.delDisabled=false;
          this.upFileDisabled=false;
          this.loadingTableData=false;
        })
			},
			handleCurrentChange(currentPage){												//分页
        this.pageDisabled=true;
        this.searchDisabled=true;
        this.clearDisabled=true;
        this.delDisabled=true;
        this.upFileDisabled=true;
        this.loadingTableData=true;
			  this.currentPage = currentPage
				this.start = (currentPage - 1)*this.pageSize;
				if (this.scriptTop.formdata){
					var params = {
						"count":this.pageSize,
						"start":this.start,
						'starttime':this.startTime,
						"endtime":this.endTime,
						"filename" :this.scriptTop.filename,
						"uploader":this.scriptTop.person,
					}
				}else{
					var params = {
						"count":this.pageSize,
						"start":this.start,
						"filename" :this.scriptTop.filename,
						"uploader":this.scriptTop.person,
					}
				}
				this.$api.script.getscript(params).then(res =>{
					if (res.data.success === 1){
            for (var message in  res.data.data.info){
              if (res.data.data.info[message].size/1024<1){															//判断size的单位
                res.data.data.info[message].size = res.data.data.info[message].size +'B'
              } else if(res.data.data.info[message].size / 1024 / 1024 < 1){
                var refile = res.data.data.info[message].size / 1024
                res.data.data.info[message].size = refile.toString().split('.')[0] +'KB'
              }else if (res.data.data.info[message].size /1024 / 1024 >= 1){
                var refile = res.data.data.info[message].size / 1024 / 1024
                res.data.data.info[message].size = refile.toString().split('.')[0] +'MB'
              }
            }
						this.script = res.data.data.info;
            this.pageDisabled=false;
            this.searchDisabled=false;
            this.clearDisabled=false;
            // this.delDisabled=false;
            this.upFileDisabled=false;
            this.loadingTableData=false;
					}
					else if (res.data.success === 0){
						console.log(res.data.msg);
            this.pageDisabled=false;
            this.searchDisabled=false;
            this.clearDisabled=false;
            // this.delDisabled=false;
            this.upFileDisabled=false;
            this.loadingTableData=false;
					}
				}).catch(err=>{
          this.pageDisabled=false;
          this.searchDisabled=false;
          this.clearDisabled=false;
          // this.delDisabled=false;
          this.upFileDisabled=false;
          this.loadingTableData=false;
        })
			},
			setHeaderCellStyle({row, column, rowIndex, columnIndex}){		//去掉表格前两项的竖杠
        if(columnIndex===0||columnIndex===1){
          return "el-table-th-noborder"
        }
      },
			updown(val){
				this.url =val.url
				this.downname = val.filename
			},
      reupload(){
        this.$refs.upload.submit()
      },
		},
		mounted(){																								//初始化加载
			this.getdata();
		},

	}
</script>

<style>
  .kd-remark .el-textarea__inner{
    background-color: #1f2122;
    border-radius: 0;
    border: 1px solid #383b3c;
    height: 215px !important;
    color: #9ca9b1;
    padding:5px 10px;
    font: 12px"微软雅黑";
  }
  .kd-remark .el-dialog__body{
    padding: 0 35px;
  }
  .kd-remark .el-dialog__footer{
    padding-top: 0px;
  }
  .kd-remark .el-textarea__inner::-webkit-input-placeholder {
    color:#5d6266;
    font-size: 12px;
  }
</style>
