<template >
	<div  class='theme-dark appDetection' style="padding: 21px 20px 21px 27px;"  >

    <!--上方检测按钮-->
		<div style="">
			<span  style="color: #9ca9b1;font-size: 14px;" v-if="showData">应用检测</span>
			<span v-if="timeShow" style="color: #9ca9b1;font-size: 14px;">({{ timeItTime }})</span>
			<span style="float: right;">
			  <el-button @click='applicationDetection' :disabled="createDetection"><span v-if="showData === false">一键检测</span><span v-if="showData === true">再次检测</span></el-button>
			  <el-button @click='exportAll' :disabled='checkExport'>导出</el-button>
			</span>
    </div>
    <div style="margin: 280px auto auto 520px;font-size: 12px;color:#9ca9b1;" v-if="withoutDetection">
      <span style="margin-right: 10px;"><i class="el-icon-info"></i></span>
      <span >
				<!-- 尚未进行应用检测。请点击“一键检测”进行应用检测，您也可以查看“历史检测”数据 -->
        尚未进行应用检测，请点击 "<span style="color: #299dff;text-decoration:underline;cursor: pointer;" @click="applicationDetection">一键检测</span> " 进行应用检测
				<span v-if="disabledHistory">，您也可以查看"</span><span style="color: #299dff;text-decoration:underline;cursor: pointer;" @click="applicationDetectionHistory" v-if="disabledHistory">历史检测</span>
				<span v-if="disabledHistory">"数据</span>
			</span>
    </div>
    <!--下方循环展示出检测项-->
    <!--循环大项-->
    <!-- v-loading="loading"
      element-loading-background="rgba(0, 0, 0, 0.5)"
      element-loading-text="检测中...请稍后"-->
    <div
      style="background-color: #232629;margin-top:19px;margin-right:20px;padding-top: 18px;height:750px;width:100%;overflow:auto;display: inline-block;white-space: pre-line;overflow-wrap: break-word;"
			class="appDetection "
			popper-class='divAppDetection'
			id="divAppDetection"
      v-if="showData">
      <div  v-for=" (recv , index) in allShow" :key="index" style="margin-right:20px;margin-left:20px;;color: #9ca9b1;font-size: 14px">
        <span style="border:#63cd81 solid 4px;float:left;margin: 6px auto;border-radius:2em;" v-if="recv.status===0"></span>
        <span style="border:#fb265d solid 4px;float:left;margin: 6px auto;border-radius:2em;" v-if="recv.status===1"></span>
        <el-collapse v-model="activeNames"  style="background-color:transparent;color: #9ca9b1;font-size: 14px" >
        <!--展示大项分组-->
          <el-collapse-item  :title="recv.check_types"  :name="recv.check_type" style="background-color: transparent;margin-left: 10px;" >
            <div  v-for="(model,index1) in recv.info"   :key="index1" style=";color: #9ca9b1;font-size: 14px">
              <span style="background: #232629;padding:5px 10px 9px 10px;min-height: 50px;" v-for="(modelOne,indexModelOne) in model" :key="indexModelOne">
                <!--循环小项-->
                <!--加入序号、状态正常异常-->
                <!--循环次数-->
                <span v-if="index1<9" >  {{index1+1}}</span>
								<span v-if="index1<9"  style="margin-left:4px ;">:</span>
								<span v-if="index1>=9">{{index1+1}}:</span>
                <span style="margin-right: 10px;">{{indexModelOne}}</span>
                <span >运行状态 : </span><span v-if="modelOne.status===0" style="color: #63cd81;margin-left: 5px;">正常</span><span v-if="modelOne.status===1" style="color: #fd265d;margin-left: 5px;">异常</span>
								<!--如果异常显示异常信息，正常则不显示 只显示状态-->
								<div v-for="(point,index3) in modelOne.err_info" :key="index3" style="padding:0 10px 0 35px;" v-if="modelOne.status===1">
									<div>
										<span>描述</span><span v-if="modelOne.err_info.length!==1">{{index3+1}}</span><span> : {{point}}</span>
									</div>
									<div>
										<span>原因</span><span v-if="modelOne.err_info.length!==1">{{index3+1}}</span><span> : {{modelOne.check_method[index3]}}</span>
									</div>
								</div>
                <span v-if="modelOne.status===1" style="margin:0 10px 0 35px;">
                  <span>日志 : </span>
                  <span style="display: inline;" v-if="modelOne.log&&modelOne.log===' ----'">{{ modelOne.log}}</span>
                <span  style="width:auto;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;padding-left: 75px;" v-if="modelOne.log&&modelOne.log!==' ----'" >{{ modelOne.log}}</span>
                  <button type="button" class="button-host-info" @click="appDetectionLogDetail(recv.check_type,indexModelOne)" v-if="modelOne.log&&modelOne.log!==' ----'&&modelOne.log.length>=150" style="float: right;">
                    <span style="text-decoration: underline;">详情</span>
                  </button>
                </span>
              </span>
            </div>
          </el-collapse-item>
        </el-collapse>
      </div>
      <div style="padding-left: 20px;color: #9ca9b1;font-size: 14px;padding-bottom: 20px" v-if="withData">
        <span>提示：如若创建会议仍不成功请“</span><button type="button" class="button-host-info" @click="turnLinkChart" >跳转到链路检测</button><span>”进行检测。</span>
      </div>
    </div>

    <!--日志弹出框-->
    <el-dialog
      title="日志详情"
      :visible.sync="appDetectionLog"
      width="800px"
      :close-on-click-modal="false">
      <div style="width:726px;height: 500px;overflow:auto;padding-right: 25px" class="logShowApp">{{appDetectionLogAll}}</div>
      <div align="center" slot='footer' class='theme-dark' style='margin-top:32px;margin-bottom:10px;'>
        <el-button @click='appDetectionLog=false'>关闭</el-button>
      </div>
    </el-dialog>
  <div>
</div>

	</div>
</template>

<script>
	export default{
		data () {
			return{
				disabledHistory:false,				//历史检测
				timeShow:false,
				timeItTime:'',
        createDetection:false,       //创建检测按钮是否disabled
        showData:false,             //是否展示数据
        withData:false,             //有数据时展示页面
				checkExport:true,           //导出按钮是否disabled
        withoutDetection:true,      //无检测时展示界面
        allShow:[],
        //默认展开
        activeNames:[],
        appDetectionLog:false,      //日志弹出框
        appDetectionLogAll:'',
        complete:0,             //是否全部完成检测
        loading:false,
        screenWidth:document.body.clientWidth,
        screenHeight:document.body.clientHeight,
      }
		},
		methods:{
		  //转到链路检测
		  turnLinkChart(){
        var monitor = '/ops/diagnose/linkdetection'
        this.$router.push({path:monitor});
				 let activeRouteList=['/ops/diagnose/linkdetection','/ops/diagnose']
				 this.$store.dispatch('activeRouteChange',activeRouteList)
      },
		  // 点击全部按钮
      appDetectionLogDetail(check_types,val){
        if(check_types==='web业务'){
          check_types = 'web'
        }else if (check_types==='中间件业务'){
          check_types = 'midware'
        }else if (check_types==='平台会议业务'){
          check_types = 'platform'
        }else if(check_types==='其他业务'){
          check_types = 'other'
        }
        var params = {
          "check_types":check_types,
          "val":val
        }
        this.appDetectionLog = true
        this.$api.monitor.getEveryOneDetectionLog(params).then(res=>{
          if(res.data.success===1){
            this.appDetectionLogAll = res.data.data.log
          }
        })
      },
      scrollToBottom() {
        this.$nextTick(() => {
					// var showContent = $(".appDetection");
					// showContent[0].scrollTop = showContent[0].scrollHeight;
          // var container = document.documentElement.clientHeight
          // document.documentElement.scrollTop = container
					// console.log(document.getElementById("divAppDetection").scrollHeight)
					divAppDetection.scrollTop =  divAppDetection.scrollHeight
        })
      } ,
			applicationDetection(){							//一键检测应用
        this.loading = true
        this.createDetection = true
		    this.$api.monitor.appDetectionBegin().then(res=>{
		      if(res.data.success ===1){
            this.allShow = []
            this.complete = 0
            this.requestDetection()
          }else if (res.data.success === 0){
		        this.$message(res.data.msg)
            this.loading = false
            this.createDetection = false
          }
        }).catch(err=>{
          this.loading = false
          this.createDetection = false
        })

			},
			timestampToTime(timestamp) {                            //时间转换
			  var date = new Date(timestamp);//时间戳为10位需*1000，时间戳为13位的话不需乘1000
			  var Y = date.getFullYear() + '-';
			  var M = (date.getMonth()+1 < 10 ? '0'+(date.getMonth()+1) : date.getMonth()+1) + '-';
			  var D = (date.getDate()<10 ? '0'+date.getDate() : date.getDate()) + ' ';
			  var h = (date.getHours()<10 ? '0'+date.getHours():date.getHours())  + ':';
			  var m = (date.getMinutes()<10 ? '0'+date.getMinutes():date.getMinutes() )+':' ;
			  var s = (date.getSeconds()<10 ? '0'+date.getSeconds():date.getSeconds());
			  return Y+M+D+h+m+s;
			},
      //请求一键检测
      requestDetection(){
		    this.checkExport = true
        this.loading = true
				this.showData = true
        this.$api.monitor.appCluster().then(res=>{
          if (res.data.success === 1){
            this.allShow = res.data.data
            this.withoutDetection = false
            if (this.allShow.info!==[]){
              this.withData = true
            }else{
              this.withData = false
            }
            // 循环更改默认展开项
            if(this.allShow !== []){
              this.activeNames = []
              for(var i in this.allShow){
                //更换四个大模块的名字
                if(this.allShow[i].check_type==='web'){
                  this.allShow[i].check_type = 'web业务'
                }else if (this.allShow[i].check_type==='midware'){
                  this.allShow[i].check_type = '中间件业务'
                }else if (this.allShow[i].check_type==='platform'){
                  this.allShow[i].check_type = '平台会议业务'
                }else if(this.allShow[i].check_type==='other'){
                  this.allShow[i].check_type = '其他业务'
                }
                if(this.allShow[i].is_complete === 1){
                  this.allShow[i].check_types = this.allShow[i].check_type+" ( 检测完成 ）"
                }else{
                  this.allShow[i].check_types = this.allShow[i].check_type+" ( 正在检测 ... ）"
                }
                //如果日志没有的话更换
                if(this.allShow[i]){
                  for (var changeLog in this.allShow[i].info){
                    for (var LastChangeLog in this.allShow[i].info[changeLog]){
                      if(!this.allShow[i].info[changeLog][LastChangeLog].log){
                        this.allShow[i].info[changeLog][LastChangeLog].log = " ----"
                      }else{
                        // this.allShow[i].info[changeLog][LastChangeLog].log = this.allShow[i].info[changeLog][LastChangeLog].log.substr[0,200]
												// console.log(this.allShow[i].info[changeLog][LastChangeLog].log,this.allShow[i].info[changeLog][LastChangeLog].log.length)
                      }
                      if(this.allShow[i].info[changeLog][LastChangeLog].err_info.length===0){
                        this.allShow[i].info[changeLog][LastChangeLog].err_info = [" ----"]
                      }
                      if(this.allShow[i].info[changeLog][LastChangeLog].check_method.length===0){
                        this.allShow[i].info[changeLog][LastChangeLog].check_method = [" ----"]
                      }
                    }
                  }
                }
                  this.activeNames.push(this.allShow[i].check_type)
              }
            }
            for (var checkEnd in res.data.data){
              if(res.data.data[checkEnd]["is_complete"] === 0){
                this.complete = 0
              }
            }
            if(res.data.data[0]["is_complete"] ===1&&res.data.data[1]["is_complete"] ===1&&res.data.data[2]["is_complete"] ===1&&res.data.data[3]["is_complete"] ===1 ){
              this.complete = 1
							if(res.data.data[0]["end_time"]){
								// console.log(res.data.data[0]["end_time"])
								this.timeShow = true
								this.timeItTime =this.timestampToTime(Number(res.data.data[0]["end_time"])) 
							}
            }
            if(this.complete === 0){
              this.scrollToBottom()
              this.timer = setTimeout(()=>{
                this.requestDetection()
              },2000)
            }else if (this.complete === 1){
              this.scrollToBottom()
              this.activeNames = []
              for (var status in this.allShow){
                if (this.allShow[status]["status"] ===1){
                  this.activeNames.push(this.allShow[status].check_type)
                }
              }
              this.loading = false
              this.checkExport = false
              this.createDetection = false
              this.$message("检测完成")
            }
          }else if(res.data.success === 0){
            this.scrollToBottom()
            this.loading = false
            this.createDetection = false
            this.$message("检测失败")
          }
        }).catch(err=>{
					console.log(err)
          this.scrollToBottom()
          this.loading = false
          this.createDetection = false
          this.$message("检测失败")
        })
      },
      exportAll(){
        this.$api.monitor.appExport().then(res=>{
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
      //屏幕高度更改
      changeFixed(clientHeight) {                        //动态修改样式
				// console.log(clientHeight)
        this.$refs.appDetection.style.height = clientHeight + 'px';
      },
			// 初始化检测是否有任务存在
			initRequest(){
				this.$api.monitor.appCluster().then(res=>{
				  if (res.data.success === 1){
						var comp = 1
						for(var i in res.data.data){
							if(res.data.data[i].is_complete===0){
								comp=0
							}
						}
						if(comp === 0){
							this.$message("正在恢复检测任务")
							this.requestDetection()
						}else{
							//循环判断是否为空 是否可以显示历史数据
							for(var list in res.data.data){
								if(res.data.data[list].info.length!==0){
									this.disabledHistory = true
								}
							}
							if(this.disabledHistory===false){
								
							}
							// console.log(this.disabledHistory)
						}
						// if()
						
					}
				})
			},
			applicationDetectionHistory(){
				this.requestDetection()
			},
		},
		
		mounted() {
			this.initRequest()
			// var a = "spawn telnet 10.23.46.40 2670Trying 10.23.46.40...Connected to 10.23.46.40.Escape character is '^]'.*===============================================================»¶ӭʹÓÿƴï Telnet ·þÎñÆ÷¡£*===============================================================Username:Password:css->checkIN~~~~~~~[CheckEnv]~~~~~~IN~~~~~~~[ok] [LoadScript_NoLock]Load Script File ./script/deleteresinfo.lua Success, SHA:103b5693a3077374"
			// console.log(a.length)
			// let activeRouteList=['/ops/monitor/linkdetection','/ops/monitor']
   //    this.$store.dispatch('activeRouteChange',activeRouteList)
		},
    watch:{
      clientHeight() {
        this.changeFixed(this.clientHeight)
      },
      screenWidth(){},
      screenHeight(){}
    },
		beforeDestroy () {
		  clearTimeout(this.timer);
		  this.timer = null;
		},
	}
</script>

<style>
	.divAppDetection{
		height:document.documentElement.clientHeight - 85 ;
	} 
  .appDetection .el-collapse-item__wrap{
    background: transparent;
    border: none;
  }
  .appDetection .el-collapse-item__content{
    padding:0 0 38px 0 ;
  }
  .appDetection .el-collapse-item__header{
    background-color: transparent;
    color: #9ca9b1;
    border: none;
    height: 20px;
    margin-left: 10px;
    font-size: 14px;
    font-weight: 700;
    margin-bottom: 16px;
  }
  .appDetection .el-collapse{
    border-top: 0;
    border-bottom:0;
  }
  .logShowApp {
    white-space: pre-line;
    word-break: break-all;
    word-wrap: break-word;
    overflow: hidden;
    line-height: 26px;

  }
  .appDetection .el-dialog__body{
    padding: 29px 15px 0 34px;

  }
</style>
