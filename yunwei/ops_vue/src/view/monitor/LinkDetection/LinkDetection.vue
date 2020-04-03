<template>
	<!-- 链路检测 -->
	<div class="theme-dark linkTest" style="margin: 15px 20px 20px 28px">
		<div >
			<el-select  v-model="LinkTypes" @change="conferenceType" placeholder="会议链路" popper-class="theme-dark" style='width: 140px;'>
				<el-option
					v-for="item in options"
					:key="item.value"
					:label="item.label"
					:value="item.value"
					>
				</el-option>
			</el-select>
      <!--请输入创会所需账号  请输入账号对应密码-->
      <el-input placeholder="请输入创会登录账号" v-model='username' style='width: 200px;' @change="changeInput" maxlength="100" clearable></el-input>
      <el-input class="passWordStyle" placeholder="请输入账号登录密码" v-model="password" style='width: 200px;' @change="changeInput"  show-password maxlength="100"></el-input>
			<el-input  v-if='callLinkSearch' class='theme-dark' style='width: 200px;'  placeholder='请输入会议呼叫终端E164号'  maxlength="13"  v-model="_E164Search"   @change="changeInput" clearable></el-input>
			<el-button @click='showTestStart' :disabled="disabled" style="margin-left: 7px">一键检测</el-button>
		</div>
    <div style="margin: 258px auto auto 520px;font-size: 12px;color:#9ca9b1" v-if="withoutDetection">
      <span style="margin-right: 10px;"><i class="el-icon-info"></i></span>
      <span >
        尚无链路检测数据，请点击"一键检测"进行链路检测
      </span>
    </div>
		<div v-if="showCharts" style="padding-top: 20px;" >
      <el-row style="margin-right: 20px;z-index: 1;" v-loading="loading" element-loading-background="rgba(0, 0, 0, 0.5)" element-loading-text="检测中...请稍后">
        <el-col :span="24">
          <linkdetectioncharts :getData='linkGetMeetingData' :type='type' :titleAddError="titleAddError"></linkdetectioncharts>
        </el-col>
      </el-row>
		</div>
		<div v-if="callLinks">
			<!--<el-row style="margin-right: 20px">-->
				<el-col :span="12" style="padding-top: 20px;padding-right: 18px;z-index: 1;"  v-loading="loading" element-loading-background="rgba(0, 0, 0, 0.5)" element-loading-text="检测中...请稍后">
          <linkdetectioncharts :getData='linkGetMeetingData' :type='type'  :titleAddError="titleAddError" :leth='leth' ></linkdetectioncharts>
				</el-col>
				<el-col :span="12" style="padding-top: 20px;padding-left: 18px;z-index: 1;" v-loading="loading" element-loading-background="rgba(0, 0, 0, 0.5)" element-loading-text="检测中...请稍后">
          <linkdetectioncharts  :timeOptions='timeOptions' :type='type' :getData='linkGetCallData'  @timeOptionId='timeOptionId' :leth='leth'></linkdetectioncharts>
				</el-col>
			<!--</el-row>-->
		</div>
	</div>
</template>

<script>
	export default {
    components:{
      linkdetectioncharts: () => import('@/view/monitor/LinkDetection/LinkDetectionCharts.vue'),
    },
    data () {
      return {
        options:[
        	{
        		label:'会议链路',
        		value:1
        	},
        	{
        		label:'呼叫链路',
        		value:2
        	}
        ],
        LinkTypes:1,											//链路类型
				showCharts:false,									//显示会议链路
        type:1,
				callLinkSearch:false,
				callLinks:false,									//显示呼叫链路
				E164Search:'',
				disabled:true,
				task_id:'',
				linkGetMeetingData:{},
				linkGetCallData:{},
				timeOptions:[],											//呼叫用户时间选项
				createTime:'',											//呼叫链路传入后端的任务开始时间
				endTime:'',													//呼叫链路传入后端的任务结束时间
        withoutDetection:true,              //没有检测任务
        username:"",
        password:"",
        timeNumber:0,
        titleAddError:[],
        loading:false,                       //是否处于加载中(默认 未加载)
				leth:10,
        call_type:'',
      };
    },
		methods:{
      getCheckDetection(){
        this.$api.monitor.getConfLink().then(res=>{
          if (res.data.success===1){
            if(res.data.data){
              if (res.data.data.info[0].status === 1){
                this.withoutDetection = false
              }
            }
          }else if (res.data.success===0){
            axios.Notification({
              message: res.data.msg,
            })
          }
        }).catch(err=>{})
      },
			showTestStart(){								//一键检测
        this.titleAddError=[]
        this.disabled = true
        this.timeNumber = 0
				if (this.type===1){											//会议链路
				  if(this.username&&this.password){
            var params = {
              "user":this.username,
              "password":this.password
            }
            this.$api.monitor.createConf(params).then(res=>{
              if(res.data.success === 1){
                this.withoutDetection = false
                this.showCharts = true
                this.task_id = res.data.task_id
                this.meetingLinkInfo(this.task_id)
              }else if(res.data.success === 0){
                if(res.data.error_code === 401){
                  this.$message('检测中，请稍后。。。')
                  this.disabled=false
                  this.getconf()
                }
              }
            }).catch(err=>{})
          }}else if(this.type===2){									//呼叫链路
          if(this.username&&this.password){
            this.showCharts = false
            this.callLinks = true
            var params = {
              "mt_id":this.E164Search,
              "user":this.username,
              "password":this.password
            }
            this.$api.monitor.createConf(params).then(res=>{
              if(res.data.success === 1){
                this.withoutDetection = false
                this.task_id = res.data.task_id
								var params={
									"task_id":this.task_id,
									"start_time":this.createTime,
									"end_time":this.endTime,
								}
                this.callLinkId(params)
                this.meetingLinkInfo(this.task_id)
              }else if(res.data.success===0){
                this.disabled=false
              }
            }).catch(err=>{})
          }}

			},
			//查询链路检测任务ID
			async getconf(){
				let res = await this.$api.monitor.getConfLink()
					if(res.data.success === 1){
						//判断为哪一种链路类型
						this.task_id = res.data.data.info[0].task_id
						if (res.data.data.info[0].link_type === 1){	//会议链路
							this.meetingLinkInfo(this.task_id)
						}else if(res.data.data.info[0].link_type===2){ //呼叫链路
							this.E164Search = res.data.data.info[0].params.device_id
							var params={
								"task_id":this.task_id,
								"start_time":this.createTime,
								"end_time":this.endTime,
							}
							this.callLinkId(params)
							this.meetingLinkInfo(this.task_id)
						}
					}else if(res.data.success === 0){
						console.log(res.data.error_code,res.data.msg)
					}
			},
			//查询呼叫链路Call_id以及显示的时间选项
			async callLinkId(val){
				let res = await this.$api.monitor.callConfId(val)
				if (res.data.success===1){
					//获取呼叫时间选项
					this.createTime = res.data.data.start_time
					this.endTime = res.data.data.end_time
					if(res.data.data.info!==[]&&res.data.data.info.length!==0){
						for (var i in res.data.data.info){
							res.data.data.info[i].timestamp = res.data.data.info[i].timestamp.replace("T", " ");
							res.data.data.info[i].timestamp = res.data.data.info[i].timestamp.replace("Z", " ");
						}
					}
					// console.log(res)
					this.timeOptions = res.data.data.info
					// console.log(this.timeOptions ,'11111')
				}else if (res.data.success === 0){
					console.log(res.data.msg)
				}
			},
			//组件传来
			async timeOptionId(val){
				//用传来的时间call_id获取呼叫链路的信息
				// console.log(val)
        for(var i in this.timeOptions){
          if(val===this.timeOptions[i].id){
            this.call_type = this.timeOptions[i].call_type
          }
        }
				var params={
					call_id:val,
					start_time:this.createTime,
					end_time:this.endTime,
          call_type:this.call_type
				}
				// console.log(this.createTime,this.endTime)
				let resInfo = await this.$api.monitor.callConfResult(params)
				if (resInfo.data.success === 1){
					// console.log(resInfo.data.data.info.length)
					if(resInfo.data.data.info.length>10){
						this.leth = resInfo.data.data.info.length
					}
					this.linkGetCallData = resInfo.data.data
				}
			},
			//查询会议链路检测结果
      meetingLinkInfo(){
				 this.$api.monitor.meetingLinkResult(this.task_id).then(res=>{
					if(res.data.success === 1){
						//传给链路组件绘图所需要的信息
            this.loading = true
            this.orLoading = 0
            if (res.data.data.is_complete === 1){
              this.timeNumber+=1
              if(res.data.data.conf_error!==""){
								this.$message.error(res.data.data.conf_error)
                var arr = res.data.data.conf_error
                this.titleAddError.push(arr)
                this.titleAddError = [...this.titleAddError]
                this.linkGetMeetingData = res.data.data
                this.disabled=false
                this.loading = false
              }else {
                if(res.data.data.info!==[]){
                  if(res.data.data.info.length===6){
                    this.disabled=false
                    this.loading = false
                    this.linkGetMeetingData = res.data.data
                  }else{
                    this.linkGetMeetingData = res.data.data
                    setTimeout(()=>{
                      if(this.timeNumber===15){
                        this.loading = false
                        this.disabled=false
                      }
                      if(this.timeNumber<15){
                        this.meetingLinkInfo()
                      }
                    },2000)
                  }
                }
                if(this.type ===2){
									var params={
										"task_id":this.task_id,
										"start_time":this.createTime,
										"end_time":this.endTime,
									}
									this.callLinkId(params)
                }
              }
            }else if(res.data.data.is_complete===0){
              setTimeout(()=>{
                  this.meetingLinkInfo()
              },3000)
            }
					}else if(res.data.success===0){
					  console.log(res.data.msg)
          }
				}).catch(err=>{})
			},

			conferenceType(val){
				if (val === 1 ){
					this.type = 1
					this.callLinkSearch = false
					this.callLinks = false
					this.disabled = false
          this.withoutDetection = true
          this.showCharts = false
				}else if (val === 2){
					this.type = 2
					this.callLinkSearch = true
					this.showCharts = false
          this.withoutDetection = true
					if (this.E164Search){
						this.disabled = false
					}else{
						this.disabled = true
					}
					
				}
			},
			changeInput(){
        if(this.type===1){
          if(this.username===""||this.password===""){
            this.disabled = true
          }else if(this.username&&this.password){
            this.disabled = false
          }
        }
        if(this.type===2){
          // console.log(this.E164Search.length)
          if(this.username===""||this.password===""||this.disabled===""||this.E164Search.length!==13){
            this.disabled = true
          }else if(this.username&&this.password&&this.E164Search.length===13){
            this.disabled = false
          }
        }
			},
		},
		mounted() {
			
		},
		computed: {
			_E164Search: {
			  set: function (value) {
			    this.E164Search = value;
			  },
			  get: function () {
			    return this.E164Search.replace(/[^0-9]+/g, '')
			  }
			}
		},

	};
</script>

<style>
	.passWordStyle .el-input__inner{
		padding: 0 30px 0 10px;
	}
	
	
</style>




