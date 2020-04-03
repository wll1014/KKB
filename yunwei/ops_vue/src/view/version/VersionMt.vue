<template>
  <div class="theme-dark" style="margin-top: 10px">
    <el-input placeholder="请输入版本文件名称搜索" v-model='keyWords' style="display:inline-block;width: 247px" maxlength="100" clearable @keydown.enter.native='searchEnterFun'></el-input>
    <el-button @click='searchForm()' :disabled="versionSearch" style="margin-left: 7px">搜索</el-button>
    <span style="float: right">
      <el-button @click='upVersion()' :disabled="versionUp">上传</el-button>
      <el-button @click='delVersion()' :disabled="versionDel">删除</el-button>
    </span>
    <div  style="height: 100%;margin-top: 18px;width: 100%">
      <!-- 所有版本表格显示 -->
      <el-table
        stripe
        :data='versionTable'
        v-loading="loadingTableData"
        element-loading-background="rgba(0, 0, 0, 0.5)"
        @selection-change="handleSelectionChange"
        :header-cell-class-name="setHeaderCellStyle">
        <el-table-column type="index" label='序号' min-width="45px"></el-table-column>
        <el-table-column type="selection" min-width="20px"></el-table-column>
        <el-table-column label='上传日期' show-overflow-tooltip min-width="193px">
          <template slot-scope="scope">
            <span>{{ new Date(scope.row.upload_time).format('Y-m-d H:i') }}</span>
          </template>
        </el-table-column>
        <el-table-column label='上传用户' prop='uploader' show-overflow-tooltip min-width="160px"></el-table-column>
        <el-table-column label='版本文件' prop='name' show-overflow-tooltip min-width="200px"></el-table-column>
        <el-table-column label='版本信息' prop='version' show-overflow-tooltip min-width="190px"></el-table-column>
        <el-table-column label='版本描述' prop='describe' show-overflow-tooltip min-width="240px"></el-table-column>
        <el-table-column label='备注' prop='postscript'  popper-class='version' min-width="221px">
        	 <template slot-scope="scope">
            <el-popover placement="top-start" trigger="hover" popper-class="povPost"  v-if="scope.row.postscript.length>30">
              <div style='margin: 0px;padding: 0px;' >{{scope.row.postscript}}</div>
        			<span slot="reference" >{{ scope.row.postscript.substr(0,30)+'...' }}</span>
        		</el-popover>
        		<span slot="reference" v-if="scope.row.postscript.length<=30">{{ scope.row.postscript }}</span>
          </template>
        </el-table-column>
        <el-table-column label='操作' min-width="105px">
          <template slot-scope="scope">
            <button type="button" class="button-host-info" @click="versionEdit(scope.$index,versionTable)">
              <span style="text-decoration: underline;">编辑</span>
            </button>
            <button type="button" class="button-host-info" @click="downVersion(scope.$index,versionTable)">
              <span style="text-decoration: underline;">下载</span>
            </button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!--上传弹出框-->
    <el-dialog
      title="上传"
      :visible.sync="upVersionDialog"
      width="500px"
      :close-on-click-modal="false"
      @close="upVersionClose">
      <div  style="margin: 30px 90px 20px 90px">
      	<div v-if="ftpUsing">
      		<div style="margin-bottom: 20px;font-size:14px ;">ftp已被占用,是否强制重启ftp服务</div>
      		<div style="color: red;">注：重启ftp服务将中断所有正在进行的任务</div>
      		<div style="margin-left:28px ;font-size:14px ;color: red;">请确认当前无人使用</div>
      	</div>
      	
      	<div v-if="!ftpUsing">
      		<div style="color: red;margin-bottom: 30px" >注：上传版本过程中请勿将此框关闭</div>
      		<div>请通过ftp上传版本文件到如下文件目录</div>
      		<div style="margin-top: 10px;max-height: 120px;overflow:auto;max-width: 320px;white-space: pre-line;overflow-wrap: break-word;display: inline-block; ">
      		  <span v-for="(value,index) in upVersionUrl" :key="index" >
      				{{value}}
      			</span>
      		</div>
      	</div>
      </div>
      <div v-if="ftpUsing" align="center" slot='footer' class='theme-dark' style='margin-bottom:10px;'>
      	<el-button @click='ftpUpUsingClose'>确定</el-button>
        <el-button @click='upVersionDialog=false'>取消</el-button>
      </div>
      <div v-if="!ftpUsing" align="center" slot='footer' class='theme-dark' style='margin-bottom:10px;'>
        <el-button @click='upVersionDialog=false'>关闭</el-button>
      </div>
    </el-dialog>

    <!--编辑弹出框-->
    <el-dialog
      title="编辑"
      :visible.sync="EditVersionDialog"
      width="500px"
      :close-on-click-modal="false"
      class="editDialog">
      <div style="margin-top: 30px;color: #9ca9b1;font-size: 12px">
        <span style="margin-right:32px">上传用户</span>
        <span >{{ EditVersion.uploader }}</span>
      </div>
      <div style="margin-top: 30px;color: #9ca9b1;font-size: 12px">
        <span style="margin-right:32px">版本文件</span>
        <span style="width:340px;max-height:26px;overflow:auto;display: inline-block;white-space: pre-line;overflow-wrap: break-word;">{{ EditVersion.name }}</span>
      </div>
      <div style="margin-top: 30px;color: #9ca9b1;font-size: 12px">
        <span style="margin-right:32px">版本信息</span>
        <el-input v-model='EditVersion.versions' maxlength="32" style="width: 340px" placeholder="请输入不超过32字符"></el-input>
      </div>
      <div style="margin-top: 30px;color: #9ca9b1;font-size: 12px">
        <span style="margin-right:32px">版本描述</span>
        <el-input v-model='EditVersion.describes' maxlength="32" style="width: 340px" placeholder="请输入不超过32字符"></el-input>
      </div>
      <div style="margin-top: 20px;color: #9ca9b1;font-size: 12px;">
        <span style="margin-right:44px;float: left">备注</span>
        <el-input v-model='EditVersion.postscripts' type="textarea"  maxlength="512" style="width: 340px;margin-left: 15.5px" placeholder="请输入不超过512字符"></el-input>
      </div>
      <div align="center" slot='footer' class='theme-dark' style='margin-bottom:10px;margin-top: 137px'>
        <el-button @click='EditVersionDialogSure()'>确定</el-button>
        <el-button @click='EditVersionDialog=false'>取消</el-button>
      </div>
    </el-dialog>

    <!--删除弹出-->
    <el-dialog title="提示" :visible.sync="delVisible" width="300px"  top="15%" center>
      <div style="margin-top: 40px;margin-bottom: 40px;margin-left: 10px"><i class="ops-icons-bg icon-notice" style="display: inline-block;margin-right: 5px"></i>删除不可恢复，是否确定删除？</div>
      <span slot="footer" class="dialog-footer" >
        <el-button @click="deleteRowAll">确 定</el-button>
				<el-button @click="delVisible = false">取 消</el-button>
			</span>
    </el-dialog>

    <!--下载弹出框-->
    <el-dialog
      title="下载"
      :visible.sync="downVersionDialog"
      width="500px"
      :close-on-click-modal="false"
			@close="downVersionClose">
      <div  style="height: 200px;margin: 30px 90px">
      	<div v-if="ftpUsing">
      		<div style="margin-bottom: 20px;font-size:14px ;">ftp已被占用,是否强制重启ftp服务</div>
      		<div style="color: red;">注：重启ftp服务将中断所有正在进行的任务</div>
      		<div style="margin-left:28px ;font-size:14px ;color: red;">请确认当前无人使用</div>
      	</div>
      	<div v-if="!ftpUsing">
      		<div style="color: red;margin-bottom: 20px">注：下载版本过程中请勿将此框关闭</div>
      		<div>请到该路径下下载版本文件</div>
      		<div style="margin-top: 10px;max-height: 120px;overflow:auto;max-width: 320px;white-space: pre-line;overflow-wrap: break-word;display: inline-block; ">
      			<span v-for="(value,index) in downVersionUrl" :key="index" >
      				{{value}}
      			</span>
      		</div>
      		<!-- <div style="margin-top: 10px;">{{ downVersionUrl }}</div> -->
      	</div>
      </div>
      
      <div v-if="ftpUsing" align="center" slot='footer' class='theme-dark' style='margin-bottom:10px;'>
      	<el-button @click='ftpDownUsingClose'>确定</el-button>
        <el-button @click='upVersionDialog=false'>取消</el-button>
      </div>
      <div v-if="!ftpUsing" align="center" slot='footer' class='theme-dark' style='margin-bottom:10px;'>
        <el-button @click='downVersionDialog=false'>关闭</el-button>
      </div>
    </el-dialog>

    <!-- 页码 -->
    <div style="margin-top: 20px;">
      <KdPagination
        @current-change="handleCurrentChange"
        :pageSize="pageSize"
        :currentPage="currentPage"
        :total="count"
        :disabled="versionPage">
      </KdPagination>
    </div>
  </div>
</template>

<script>
  export default {
    name: "VersionPlatform",
    components: {
      KdPagination: () => import('@/components/common/KdPagination.vue'),

    },
    data(){
      return {
        keyWords:'',          //搜索关键字
        versionTable:[],      //表格内容
        upVersionDialog:false,  //上传弹出框
        upVersionUrl:'',      //上传路径
        EditVersionDialog:false , //编辑弹出框
        EditVersion:{},       //编辑内容
        versionDel:true,   //置灰删除键
        versionUp:false,
        versionSearch:false,
        versionPage:false,
        multipleSelection:[],   //放入选中信息
        delVisible:false,     //删除弹出框
        delArr:[],          //放入删除id
        downVersionDialog:false,  //下载弹框
        pageSize:15,
        currentPage:1,
        start:0,
        count:0,
        loadingTableData:false,
        downVersionUrl:'',
				sendRequest:false,						//是否发送关闭请求参数
				ftpUsing:false,
				index:'',
      }
    },
    methods: {
			ftpDownUsingClose(){
				this.$api.version.upMtClose().then(res=>{
					if(res.data.success===1){
						// console.log("11111")
						
						this.downVersion(this.index,this.versionTable)
					}else if(res.data.success===0){
						this.$message(res.data.msg)
					}
				}).catch(err=>{})
			},
			ftpUpUsingClose(){
					this.$api.version.upMtClose().then(res=>{
						if(res.data.success===1){
							this.upVersion()
						}else if(res.data.success===0){
							this.$message(res.data.msg)
						}
					}).catch(err=>{})
			},
      timestampToTime(timestamp) {                            //时间转换
        var date = new Date(timestamp);//时间戳为10位需*1000，时间戳为13位的话不需乘1000
        var Y = date.getFullYear() + '-';
        var M = (date.getMonth()+1 < 10 ? '0'+(date.getMonth()+1) : date.getMonth()+1) + '-';
        var D = (date.getDate()<10 ? '0'+date.getDate() : date.getDate()) + ' ';
        var h = (date.getHours()<10 ? '0'+date.getHours():date.getHours())  + ':';
        var m = (date.getMinutes()<10 ? '0'+date.getMinutes():date.getMinutes() )+':' ;
        var s = (date.getSeconds()<10 ? '0'+date.getSeconds():date.getSeconds()) ;
        return Y+M+D+h+m+s;
      },
      getData(params){
        this.loadingTableData = true
        this.versionUp=true
        this.versionSearch=true
        this.versionPage=true
        // this.versionTable = [{"version":1,"uploader":"zhangsan","id":6,"upload_time":1574732631304}]
        this.$api.version.getMtData(params).then(res=>{
          if(res.data.success===1){
            this.count = res.data.data.total
            for(var infoOne in res.data.data.info){
              for(var index in infoOne){
                if(index==="upload_time"){
                  // console.log("111")
                  res.data.data.info[infoOne][index] = this.timestampToTime(res.data.data.info[infoOne][index])
                }
              }
            }
            this.versionTable = res.data.data.info
            this.loadingTableData = false
            this.versionUp=false
            this.versionSearch=false
            this.versionPage=false
          }else if(res.data.success===0){
            console.log(res.data.msg)
            this.loadingTableData = false
            this.versionUp=false
            this.versionSearch=false
            this.versionPage=false
          }
        }).catch(err=>{
          this.loadingTableData = false
          this.versionUp=false
          this.versionSearch=false
          this.versionPage=false
        })
      },
			searchEnterFun(e){									//enter搜索函数
				// console.log(e)
				var keyCode = window.event?e.keyCode:e.which;
				if(keyCode===13){
					this.searchForm()
				}
			},
      searchForm(){                                       //搜索
        var params = {
          "condition":this.keyWords,
          "start":0,
          "count":this.pageSize,
        }
        this.start = 0
        this.currentPage = 1
        this.getData(params)
      },
      upVersion(){                                        //上传
				this.upVersionDialog = true
				this.upVersionUrl = ''
				this.$api.version.getMtVersionUrl().then(res=>{
					if(res.data.success === 1){
						this.sendRequest = true
						this.ftpUsing = false
						this.upVersionUrl = res.data.msg
					}else if(res.data.success===0){
						this.sendRequest = false
						if(res.data.error_code===404){
							this.ftpUsing = true
						}else{
							this.$message(res.data.msg)
							this.ftpUsing = false
						}
						
					}
				}).catch(err=>{this.sendRequest = false;this.ftpUsing=false})
      },
			delVersion(){                                   //点击删除键
			  const length = this.multipleSelection.length
			  this.delVisible = true;   	//显示删除弹框
			  for (let i = 0; i < length; i++){
			    this.delArr.push(this.multipleSelection[i].id)
			  }
			},
			handleSelectionChange(val){		//操作多选
			  this.multipleSelection = val;
			  if(this.multipleSelection.length===0){
			    this.versionDel = true
			  }else if(this.multipleSelection.length!==0){
			    this.versionDel = false
			  }
			},
			deleteRowAll(){                 //确认删除
			  var param = {"ids":this.delArr}
			  this.$api.version.versionMtDelete(param).then(res =>{
			    this.multipleSelection = []
			    this.delArr=[]
			    if (res.data.success === 1){
						this.start = 0
			      this.$message.success('删除成功')
			      this.getData({"start":this.start,"count":this.pageSize})
			      this.delVisible = false;
			    }
			    else if (res.data.success === 0){
			      this.$message.error('删除失败')
			      this.delVisible = false;
			    }
			  }).catch(err=>{this.delVisible = false;this.$message.error('删除失败')})
			   //关闭提示框
			},
      versionEdit(index,versionTable){                  //点击编辑按钮显示信息
        this.EditVersionDialog = true
        this.EditVersion = {
          "versions":versionTable[index].version,
          "describes":versionTable[index].describe,
          "postscripts":versionTable[index].postscript,
          "name":versionTable[index].name,
          "uploader":versionTable[index].uploader,
					"id":versionTable[index].id
        }
      },
      EditVersionDialogSure(){          //编辑确定版本信息
        var params=this.EditVersion
				this.start = 0
        this.$api.version.editMtVersion(params).then(res=>{
          if(res.data.success===1){
            this.EditVersionDialog=false
						this.getData({"start":this.start,"count":this.pageSize})
            this.$message("修改成功")
          }else if(res.data.success===0){
            this.EditVersionDialog=false
						this.getData({"start":this.start,"count":this.pageSize})
            this.$message("修改失败")
          }
        }).catch(err=>{this.EditVersionDialog=false; this.$message("修改失败");this.getData({"start":this.start,"count":this.pageSize})})

      },
      downVersion(index,versionTable){                  //下载请求url
				this.index = index
				this.downVersionDialog = true
				this.downVersionUrl = ''
				// console.log(this.index,this.versionTable)
				this.$api.version.downMtUrl(this.versionTable[this.index].id).then(res=>{
				  if(res.data.success===1){
						this.sendRequest = true
						this.ftpUsing = false	
						// for(var i in res.data.msg){
						// 	this.downVersionUrl+=res.data.msg[i]
						// }
						// console.log("1111111111")
				    this.downVersionUrl = res.data.msg
						
				  }else if(res.data.success===0){
						this.sendRequest = false
						if(res.data.error_code===404){
							this.ftpUsing = true
						}else{
							this.ftpUsing = false
							this.$message(res.data.msg)
						}
				    
				  }
				}).catch(err=>{this.sendRequest = false;this.ftpUsing = false})
      },
			downVersionClose(){
				if(!this.ftpUsing){
					// if(this.sendRequest){
						this.$api.version.upMtClose().then(res=>{
						  if(res.data.success===1){
								this.start = 0
								this.currentPage = 1
								// this.getData({"start":this.start,"count":this.pageSize})
						  }else if(res.data.success===0){
						    this.$message(res.data.msg)
						  }
						}).catch(err=>{})
					}
					
					// this.sendRequest = false
				// }
				
			},
      setHeaderCellStyle({row, column, rowIndex, columnIndex}){
        if(columnIndex===0||columnIndex===1){
          return "el-table-th-noborder"
        }
      },
      handleCurrentChange(currentPage){   //点击第几页
        this.currentPage = currentPage
        this.start = (this.currentPage-1)*this.pageSize
        var params={
          "condition":this.keyWords,
          "start":this.start,
          "count":this.pageSize,
        }
        this.getData(params)
      },
      upVersionClose(){                 //上传关闭按钮
			if(!this.ftpUsing){
				// if(this.sendRequest){
					 this.$api.version.upMtClose().then(res=>{
						if(res.data.success===1){
							this.start = 0
							this.currentPage = 1
							this.getData({"start":this.start,"count":this.pageSize})
						}else if(res.data.success===0){
							this.$message(res.data.msg)
						}
					}).catch(err=>{})
				}
				// this.sendRequest = false
			// }	
      },
    },
    mounted(){
      this.getData({"start":this.start,"count":this.pageSize})
    },

  }
</script>

<style >
  .editDialog .el-dialog__body{
    margin-left: 35px;
    /*margin-right: 20px;*/
    padding: 0;
  }
  .editDialog .el-textarea__inner::-webkit-input-placeholder {
    color:#5d6266;
    font: 12px "微软雅黑";
  }
  .editDialog .el-textarea__inner{
    background-color: #1f2122;
    border-radius: 0;
    border: 1px solid #383b3c;
    height: 80px !important;
    color:#9ca9b1;
    padding: 5px 10px;
    font: 12px "微软雅黑";
  }
</style>
