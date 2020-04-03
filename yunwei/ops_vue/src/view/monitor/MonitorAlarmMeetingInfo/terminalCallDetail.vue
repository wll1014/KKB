<template class="theme-dark terminalDetail" style="height: 100%;">
	<div >
			<!-- 图 -->
			<div v-if="media==='pic'" style="background: #232629 ;width:100%;height:100%" class="theme-dark">
				<div style="font-size: 16px;color:#9ca9b1;padding-top: 200px;padding-left: 520px;padding-bottom: 150px" v-show="!showAll">
				  <span style="padding-right: 10px;"><i class="el-icon-info"></i></span>
				  <span >
				    尚 无 呼 叫 链 路 数 据
				  </span>
				</div>
				<div style="height: 100%" v-show="showAll">
				  <linkdetectioncharts style='width: 1500px;' :leth='leth' :timeOptions='timeOptions' :type='1' :getData='linkGetCallData' @timeOptionId='timeOptionId'></linkdetectioncharts>
				</div>
			</div>
		<!--表-->
		<div v-if="media==='list'">
			<div style="background: #232629;font-size: 16px;color:#9ca9b1;padding-top: 200px;padding-left: 520px;padding-bottom: 150px" v-if="withoutCallDetail">
			  <span style="padding-right: 10px;"><i class="el-icon-info"></i></span>
			  <span >
			    尚 无 呼 叫 详 情 数 据
			  </span>
			</div>
			<!-- 呼叫详情 -->
			<div style="overflow: auto" v-if="showAll">
			  <el-select
			    v-model="selectvalue"
			    placeholder="请选择时间"
			    style='float: left;width: 470px;margin-bottom:15px;'
			    popper-class="theme-dark linkCharts"
			    @change="conferenceType(item)"
			  >
			    <el-option
			      v-for='item in timeOptions'
			      :key='item.id'
			      :label='item.timestamp+item.id'
			      :value='item.id'></el-option>
			  </el-select>
			  <el-select
			    v-model="callType"
			    placeholder="请选择呼叫类型"
			    style='float: left;width: 130px;margin-bottom:15px;margin-left: 10px'
			    popper-class="theme-dark linkCharts"
			    @change="conferenceType">
			    <el-option
			      v-for='item in callTypes'
			      :key='item.key'
			      :label='item.types'
			      :value='item.value'
			    ></el-option>
			  </el-select>
				<el-table :data='callDetailTableList' style="" v-loading="loadingTableData" element-loading-background="rgba(0, 0, 0, 0.5)" stripe class="detail">
					<el-table-column type="index" label='序号' min-width="57px"></el-table-column>
					<el-table-column label='消息' prop='cseq' show-overflow-tooltip min-width="173px"></el-table-column>
					<el-table-column label='src' prop='src' show-overflow-tooltip min-width="170px"></el-table-column>
					<el-table-column label='dst' prop='dst' show-overflow-tooltip min-width="200px"></el-table-column>
					<el-table-column label='时间' prop='time' show-overflow-tooltip min-width="210px"></el-table-column>
					<el-table-column label='详细内容'  min-width="525px">
			      <template slot-scope="scope">
			        <span> {{callDetailTableList[scope.$index].raw | ellipsis}} </span>
			        <button type="button" class="button-host-info" @click="terminalCallDetailInfo(callDetailTableList[scope.$index].raw)"  style="float: right;">
			          <span style="text-decoration: underline;">详情</span>
			        </button>
			      </template>
			    </el-table-column>
				</el-table>
			  <div style="right: 0;bottom: 10px;margin-top: 10px">
			    <KdPagination
			      @current-change="handleCurrentChange"
			      :pageSize="this.count"
			      :currentPage="currentPage"
			      :total="this.total">
			    </KdPagination>
			  </div>
			  <el-dialog
			    title="详情"
			    :visible.sync="terminalDetailInfo"
			    width="800px"
			    :close-on-click-modal="false">
			    <div style="width:726px;height: 500px;overflow:auto;padding-right: 25px" class="logShowApp">{{rowAll}}</div>
			    <div align="center" slot='footer' class='theme-dark' style='margin-top:32px;margin-bottom:10px;'>
			      <el-button @click='terminalDetailInfo=false'>关闭</el-button>
			    </div>
			  </el-dialog>
			</div>
		</div>
	</div>

</template>

<script>
	export default {
    components:{
      KdPagination: () => import('@/components/common/KdPagination.vue'),
			linkdetectioncharts: () => import('@/view/monitor/LinkDetection/LinkDetectionCharts.vue'),
    },
		props:{
			callDetailTable:{
				type:Object,
				defaultList:{}
			},
			media:{
				type:String,
				default:'pic'
			},
		},
		data() {
			return {
				withoutCallDetail:true,
				showAll:false,
        terminalDetailInfo:false,
        loadingTableData:false,
				callDetailTableList:[],
				currentPage:1,
				count:11,
        total:0,
        start:0,
        selectvalue:'',
        timeOptions:[],
        callType:'',
        callTypes:[],
        rowAll:'',
				// 图
				linkGetMeetingData:{},
				linkGetCallData:{},
				start_time:'',
				end_time:'',
				withoutDetetion:true,
				withoutDetection1:true,
				leth:10,
				// timeOptions1:[],
        call_type:'',
			}
		},
    filters: {
      ellipsis(value) {					//限制字符显示详情
        if (!value) return "";
        if (value.length > 60) {
          return value.slice(0, 60) + "...";
        }
        return value;
      }
    },
		methods: {
			timeOptionId(val){
				//用传来的时间call_id获取呼叫链路的信息
        for(var i in this.timeOptions){
          if(val===this.timeOptions[i].id){
            this.call_type = this.timeOptions[i].call_type
          }
        }
			  if(!this.callDetailTable[0].mt_e164){
			    var mtE164 = this.callDetailTable[0].mt_addr
			  }else {
			    var mtE164 = this.callDetailTable[0].mt_e164
			  }
			  var params = {
			    "conf_id":this.callDetailTable[0].conf_id,
			    "mt_e164":mtE164,
					"call_id":val,
					"start_time":this.start_time,
					"end_time":this.end_time,
          "call_type":this.call_type,
				}
				this.$api.monitor.meetingInfoLinkCallInfo(params).then(res=>{
					if (res.data.success === 1){
						if(res.data.data.info.length>this.leth){
							this.leth = res.data.data.info.length
						}
						this.linkGetCallData = res.data.data
					}else if(res.data.success===0){
					  console.log(res.data.msg)
			    }
				}).catch(err=>{
			    console.log(err)
			  })
			},
      terminalCallDetailInfo(val){
        this.rowAll = val
        this.terminalDetailInfo=true
      },
			getData() {
				if(this.media==='list'){
					// if(this.callDetailTable[1].mt_prot==="SIP"){
						this.withoutCallDetail=false
						this.showAll=true
						if(!this.callDetailTable[0].mt_e164){
						  var mtE164 = this.callDetailTable[0].mt_addr
						}else {
						  var mtE164 = this.callDetailTable[0].mt_e164
						}
						var params = {
						  "conf_id":this.callDetailTable[0].conf_id,
						  "mt_e164":mtE164,
						  "start_time":this.callDetailTable[0].start_time,
						  "end_time":this.callDetailTable[0].end_time
						}
						this.$api.monitor.meetingInfoLinkCallId(params).then(res=>{
						  if (res.data.success===1){
						    //获取呼叫时间选项
						    this.startTime = res.data.data.start_time
						    this.endTime = res.data.data.end_time
						    if(res.data.data.info!==[]){
						      for (var i in res.data.data.info){
						        res.data.data.info[i].timestamp = res.data.data.info[i].timestamp.replace("T", " ");
						        res.data.data.info[i].timestamp = res.data.data.info[i].timestamp.replace("Z", " ");
						      }
						    }
						    this.timeOptions = res.data.data.info
						    if(this.timeOptions){
						      if(this.timeOptions[0]){
						        if(this.timeOptions[0].id){
						          this.selectvalue = this.timeOptions[0].id
                      var callInfo = {
                        "conf_id":this.callDetailTable[0].conf_id,
                        "mt_e164":mtE164,
                        "start_time":this.callDetailTable[0].start_time,
                        "end_time":this.callDetailTable[0].end_time,
                        "call_id":this.timeOptions[0].id,
                        "call_type":this.timeOptions[0].call_type
                      }
                      this.$api.monitor.meetingInfoLinkCallIdMethod(callInfo).then(res1=>{
                        if(res1.data.success===1){
                          this.callTypes=[]
                          this.callTypes.push({"key":0,'types':'全部','value':''})
                          for(var i in res1.data.data.info){
                            this.callTypes.push({"key":i+1,"types":res1.data.data.info[i],"value":res1.data.data.info[i]})
                          }
                        }
                      })

						          // if(this.callTypes){
						          //   if(this.callTypes[0]){
						          //     if(this.callTypes[0].types){
						          //       this.callType=this.callTypes[0].types
						          //     }
						          //   }
						          // }
						          this.conferenceType()
						        }
						      }
						    }
						  }else if (res.data.success === 0){
						    console.log(res.data.msg)
						  }
						}).catch(err=>{
						  console.log(err)
						})
					// }
					// else{
					// 	this.withoutCallDetail=true
					// 	this.showAll=false
					// }
				}	else if(this.media==='pic'){
					// if(this.callDetailTable[1].mt_prot==="SIP"){
						if(!this.callDetailTable[0].mt_e164){
						  var mtE164 = this.callDetailTable[0].mt_addr
						}else {
						  var mtE164 = this.callDetailTable[0].mt_e164
						}
						var params = {
						  "conf_id":this.callDetailTable[0].conf_id,
						  "mt_e164":mtE164,
						  "start_time":this.callDetailTable[0].start_time,
						  "end_time":this.callDetailTable[0].end_time
						}
						this.$api.monitor.meetingInfoLinkCallId(params).then(res=>{
						  if(res.data.success === 1){
								this.showAll=true
								this.withoutDetection=false
						    if(res.data.data.info!==[]&&res.data.data.info.length!==0){
						      for (var i in res.data.data.info){
						        res.data.data.info[i].timestamp = res.data.data.info[i].timestamp.replace("T", " ");
						        res.data.data.info[i].timestamp = res.data.data.info[i].timestamp.replace("Z", " ");
						      }
									
						    }
						    this.timeOptions =[... res.data.data.info]
								// console.log(this.timeOptions)
						    this.start_time = res.data.data.start_time
						    this.end_time = res.data.data.end_time
						  }
						}).catch(err=>{
						  console.log(err)
						})
					// }
					// else{
					// 	this.showAll=false
					// 	this.withoutDetection=true
					// }
				}
				
        
			},
      conferenceType(item){
			  // 查询列表信息，已有call-id
        this.start=0
        this.currentPage = 1
        for(var i in this.timeOptions){
          if(this.timeOptions[i].id===this.selectvalue){
            this.call_type = this.timeOptions[i].call_type
          }
        }
        if(!this.callDetailTable[0].mt_e164){
          var mtE164 = this.callDetailTable[0].mt_addr
        }else {
          var mtE164 = this.callDetailTable[0].mt_e164
        }
        var params={
          "conf_id":this.callDetailTable[0].conf_id,
          "mt_e164":mtE164,
          "start_time":this.callDetailTable[0].start_time,
          "end_time":this.callDetailTable[0].end_time,
          "call_id":this.selectvalue,
          "start":this.start,
          "count":this.count,
          "methods":this.callType,
          "call_type":this.call_type
        }
        this.callListInfo(params)
      },
      //查询呼叫列表信息
      timestampToTime(timestamp) {                            //时间转换
        var date = new Date(timestamp);//时间戳为10位需*1000，时间戳为13位的话不需乘1000
        var Y = date.getFullYear() + '-';
        var M = (date.getMonth()+1 < 10 ? '0'+(date.getMonth()+1) : date.getMonth()+1) + '-';
        var D = (date.getDate()<10 ? '0'+date.getDate() : date.getDate()) + ' ';
        var h = (date.getHours()<10 ? '0'+date.getHours():date.getHours())  + ':';
        var m = (date.getMinutes()<10 ? '0'+date.getMinutes():date.getMinutes())+':';
        var s = (date.getSeconds()<10 ? '0'+date.getSeconds():date.getSeconds())+'.' ;
        var ms= timestamp.toString().slice(-3)
        return Y+M+D+h+m+s+ms;
      },
      callListInfo(params){
        this.loadingTableData =true
        this.$api.monitor.meetingInfoCallDetail(params).then(res =>{
          if(res.data.success === 1){
            this.total = res.data.data.total
            for(var i in res.data.data.info){
              for(var j in res.data.data.info[i]){
                if(j==="time"){
                  res.data.data.info[i][j] =this.timestampToTime(res.data.data.info[i][j])
                }
                if(j==='raw'){
                  res.data.data.info[i][j] = res.data.data.info[i][j]
                }
              }
            }
            this.callDetailTableList = res.data.data.info
          }
          this.loadingTableData = false
        }).catch(err=>{
          this.loadingTableData = false
        })
      },
			handleCurrentChange(currentPage){   //点击第几页
			  this.currentPage = currentPage
        if (currentPage>0) {
          this.start = currentPage
        }
        if(!this.callDetailTable[0].mt_e164){
          var mtE164 = this.callDetailTable[0].mt_addr
        }else {
          var mtE164 = this.callDetailTable[0].mt_e164
        }
				var params = {
          "conf_id":this.callDetailTable[0].conf_id,
          "mt_e164":mtE164,
          "start_time":this.callDetailTable[0].start_time,
          "end_time":this.callDetailTable[0].end_time,
          "call_id":this.selectvalue,
          "start":(this.start-1)*this.count,
          "count":this.count,
          "methods":this.callType,
          "call_type":this.call_type,
				}
        this.callListInfo(params)
			},
		},

    mounted(){
			// this.media = 'pic'
		  this.getData()
			
    },
    watch:{
      callDetailTable(newValue,oldValue){
        this.getData()
      },
			media(newValue,oldValue){
				// console.log(newValue)
				this.getData()
				
			},
    }
	}
</script>

<style scoped>
  .terminalDetail >>> .el-tooltip__popper {
    width: 800px;
  }
  .linkCharts .el-select-dropdown__item {
    padding-left: 10px;
    padding-right: 10px;
  }
  .logShowApp {
    white-space: pre-line;
    word-break: break-all;
    word-wrap: break-word;
    overflow: hidden;
    line-height: 26px;

  }

</style>

