<template>
	<!-- 除左侧域侧边栏后其余第一层界面 实时会议-->
	<div class='theme-dark RealTimeMeeting' style="height:100%;width: 100%;margin-top: 10px">
		<div style="height: 100%;">
		<!-- 上方搜索部分，公用 -->
		<div style="height: 24px;" v-show="picTab">
			<span style="float: right;display: block;	font-size: 0;" >
				<button  @click='typesChange("pic")' :class="['changeCallTerminal',{'active':realTime === 'pic'}]">视图</button>
				<button  @click='typesChange("list")' :class="['changeCallTerminal',{'active':realTime === 'list'}]">列表</button>
				
			</span>
		</div>
		<div v-show="listTab">
			<span style="float: right;display: block;	font-size: 0;" >
				<button  @click='typesChange("pic")' :class="['changeCallTerminal',{'active':realTime === 'pic'}]">视图</button>
				<button  @click='typesChange("list")' :class="['changeCallTerminal',{'active':realTime === 'list'}]">列表</button>
				
			</span>
		</div>
			
			<div class='meetingSearch1 ' style="height: 100%;" v-if="listTab">
        
				<el-select
          v-model="MeetingSearch.conf_type"
          placeholder="多点会议"
          style='width:140px;margin-right: 7px'
          popper-class="theme-dark"
					@change='changeSearch(MeetingSearch.conf_type)'>
          <el-option
            v-for='item in conferenceTypeList'
            :key='item.value'
            :label='item.label'
            :value='item.value'></el-option>
        </el-select>
        <!--<el-select-->
          <!--v-model="MeetingSearch.level"-->
          <!--placeholder="全部体验"-->
          <!--style='width:140px;margin-right: 7px'-->
          <!--popper-class="theme-dark"-->
          <!--disabled="true">-->
          <!--<el-option-->
            <!--v-for='item in conferenceQualityList'-->
            <!--:key='item.value'-->
            <!--:label='item.label'-->
            <!--:value='item.value'></el-option>-->
        <!--</el-select>-->
				
				<!-- 2.0 增加会议资源筛选项 -->
				<el-select
				  v-model="MeetingSearch.conf_media_type"
				  placeholder="全部会议资源类型"
				  style='width:140px;margin-right: 7px'
				  popper-class="theme-dark"
					v-if="this.MeetingSearch.conf_type==='3'">
				  <el-option
				    v-for='item in conferenceResourceType'
				    :key='item.value'
				    :label='item.label'
				    :value='item.value'></el-option>
				</el-select>
				
        <el-date-picker
        v-model='MeetingSearch.searchTime'
        type="datetimerange"
        start-placeholder="开始日期"
        end-placeholder="结束日期"
        popper-class="theme-dark"
        value-format="timestamp"
        format="yyyy-MM-dd HH:mm"
        style="width: 322px;vertical-align: top;margin-right: 7px"
        range-separator=""
        class="clear-close-icon"
        prefix-icon="ops-icons-bg icon-calendar"
        :clearable="false"
        >
        </el-date-picker>
        <el-input
          placeholder='请输入会议名称、会议号码、发起人、终端名称、终端号码'
          v-model='MeetingSearch.keywords'
          style='width:360px;margin-right: 7px' maxlength="100"
					v-if='multiPointMeetingSearch'
					@keydown.enter.native='searchEnterFun'></el-input>
					<el-input
					  placeholder='输入主叫号码名称、被叫号码名称'
					  v-model='MeetingSearch.keywords'
					  style='width:260px;margin-right: 7px' maxlength="100"
						v-if='peerToPeerMeetingSearch'
						@keydown.enter.native='searchEnterFun'></el-input>
        <el-button @click="meetingSearch('MeetingSearch')" :disabled="disabledSearch">搜索</el-button>
			</div>
		<!-- 下方表格部分，分别设置 -->
			<div class='kd-alarm-no'  style="margin-top: 18px;height:100% ;" v-if="picTab">
				<conferenceTopology @change='conferenceTopologyChange'></conferenceTopology>
			</div>
		<div class='kd-alarm-no'  style="height: 100%;margin-top: 18px;width: 100%" v-if="listTab">
			<!-- 传统会议以及端口会议的表格显示 -->
			<el-table stripe :data='MeetingTable'
							v-if='multiPointMeeting'
							v-loading="loadingTableData"
							@row-dblclick="tableRowDblClick"
							element-loading-background="rgba(0, 0, 0, 0.5)">
				<el-table-column type="index" label='序号' min-width="57px"></el-table-column>
        <el-table-column label='会议名称' prop='conf_name' show-overflow-tooltip min-width="167px"></el-table-column>
        <el-table-column label='会议号码' prop='conf_id' show-overflow-tooltip min-width="100px"></el-table-column>
        <el-table-column label='会议类型' prop='会议类型' show-overflow-tooltip min-width="80px"></el-table-column>
				<el-table-column label='会议资源类型' prop='会议资源类型' show-overflow-tooltip min-width="80px"></el-table-column>
        <el-table-column label='开始时间' prop='startTime' show-overflow-tooltip min-width="130px"></el-table-column>
        <el-table-column label='结束时间' prop='endTime' show-overflow-tooltip min-width="130px"> </el-table-column>
        <el-table-column label='会议时长' prop='total_time' show-overflow-tooltip min-width="110px"></el-table-column>
        <el-table-column label='会议质量' prop='desc' show-overflow-tooltip min-width="80px"></el-table-column>
        <el-table-column label='与会方' prop='number'show-overflow-tooltip min-width="60px"></el-table-column>
        <el-table-column label='发起人' prop='organizer'  show-overflow-tooltip min-width="70px"></el-table-column>
        <el-table-column label='操作' min-width="120px">
					<template slot-scope="scope">
						<button type="button" class="button-host-info" @click="Meetingdetails(scope.$index,MeetingTable)">
							<span style="text-decoration: underline;">详情</span>
						</button>
            <button type="button" class="button-host-info" @click="snapShot(scope.$index,MeetingTable)">
              <span style="text-decoration: underline;">会议快照</span>
            </button>
					</template>
				</el-table-column>
			</el-table>
			<!-- 点对点会议的表格显示 -->
			<el-table stripe :data='MeetingTable' v-if='peerToPeerMeeting' v-loading="loadingTableData" element-loading-background="rgba(0, 0, 0, 0.5)">
				<el-table-column type="index" label='序号'></el-table-column>
				<el-table-column label='主叫号码' prop='caller_id' show-overflow-tooltip></el-table-column>
				<el-table-column label='主叫名称' prop='caller_name' show-overflow-tooltip></el-table-column>
				<el-table-column label='被叫号码' prop='callee_id' show-overflow-tooltip></el-table-column>
				<el-table-column label='被叫名称' prop='callee_name' show-overflow-tooltip></el-table-column>
				<el-table-column label='开始时间' prop='startTime' show-overflow-tooltip></el-table-column>
				<el-table-column label='会议时长' prop='total_time' show-overflow-tooltip></el-table-column>
				<el-table-column label='会议质量' prop='desc' show-overflow-tooltip></el-table-column>
				<!-- <el-table-column label='操作'>
					<template slot-scope="scope">
						<button type="button" class="button-host-info" @click="Meetingdetails(scope.$index,MeetingTable)">
							<span style="text-decoration: underline;">详情</span>
						</button>
					</template>
				</el-table-column> -->
			</el-table>
			<div style="margin-top: 20px">
			    <KdPagination
					@current-change="currentChange"
			    :pageSize="this.count"
			    :currentPage="currentPage"
			    :total="this.total"
			    :disabled="pageDisabled">
					</KdPagination>
			</div>
		</div>
		
    <!--会议快照-->
    <el-dialog
      title="会议快照"
      :visible.sync="meetingSnapShot"
      width="500px"
      :close-on-click-modal="false"
      @close="meetingSnapShotclose">
      <!--<div >-->
        <div style="margin:100px auto 100px 50px;" v-if="showSnapShot">
        <TheConferenceSnapshot :tiemRange = 'timeRange' @snapshotsStatu="snapshotsStatu" ref="timeRange" ></TheConferenceSnapshot>
        </div>
        <div align="center" slot='footer' class='theme-dark' style='margin-bottom:10px;' v-if="snapShotStatu === null">
          <el-button @click='giveTimeSpanShot'>确定</el-button>
          <el-button @click='meetingSnapShot=false'>取消</el-button>
        </div>
        <div align="center" slot='footer' class='theme-dark' style='margin-bottom:10px;' v-if="snapShotStatu === 'creating'">
          <el-button @click='meetingSnapShotclose'>取消</el-button>
        </div>
        <div align="center" slot='footer' class='theme-dark' style='margin-bottom:10px;' v-if="snapShotStatu === 'created'">
          <el-button @click='downSnapShot()'>下载文件</el-button>
        </div>
        <div align="center" slot='footer' class='theme-dark' style='margin-bottom:10px;' v-if="snapShotStatu === 'failed'">
          <el-button @click='meetingSnapShotclose'>确定</el-button>
        </div>
      <!--</div>-->
    </el-dialog>
		</div>
	</div>
</template>

<script>
	export default {
    components:{
      MonitorMeetingInfoTerminalSummary: () => import('@/components/monitor/MonitorMeetingInfoTerminalSummary.vue'),
      KdPagination: () => import('@/components/common/KdPagination.vue'),
      TheConferenceSnapshot: () => import('@/components/monitor/TheConferenceSnapshot.vue'),
			conferenceTopology: () => import('@/view/diagnose/ConferenceTopology.vue'),
    },
		props:{
			moid:Array,
			realList:Array,
		},
		'name':'RealTimeMeeting',
		data(){
			return{
				listTab:false,												//列表展示
				picTab:true,												//图形展示
				realTime:'pic',										//展示列表和图形哪一个
				multiPointMeetingSearch:true,
				peerToPeerMeetingSearch:false,
        pageDisabled:false,                  //分页设置是否可用
        disabledSearch:false,               //设置搜索按钮是否可用
        loadingTableData:false,             //数据获取加载
				MeetingSearch:{
				  conf_type:"3",
          level:'',
					conf_media_type:'',
        },
				multiPointMeeting:true,
				peerToPeerMeeting:false,
				conferenceTypeList:[
          {
            label:'多点会议',
            value:"3",
          },{
						label:'点对点会议',
						value:2,
					},],
				conferenceQualityList:[
          {
            label:"全部体验",
            value:''
          },{
						label:"体验不好",
						value:1
					},{
						label:"体验一般",
						value:2
					},{
						label:"体验良好",
						value:3
					},{
						label:"体验优秀",
						value:4
				},],
				//2.0
				conferenceResourceType:[
					{
					  label:"全部资源类型",
					  value:''
					},{
					  label:'云会议',
					  value:1,
					},{
						label:'本地会议',
						value:0,
					},
				],
				MeetingTable:[],
				platform_moid:'',
				user_moid:'',
				currentPage:1,
				count:15,
				start:1,
				total:0,
        timeRange:[],          //快照时间范围
        meetingSnapShot:false,//会议快照
        snapShotStatu:null,   //快照状态
        snapShotObj:{},       //所点击的会议列表的值
        showSnapShot:false,    //是否加载快照组件
        starttime:'',
        endTime:'',
				conf_type:'3',
			}
		},
		methods: {
      conferenceTopologyChange(val){
        // console.log(val.params)
        this.$emit('conferenceTopologyChange',val.params)
      },
			//2.0
			typesChange(value){
				if(value==='list'){
					this.listTab = true
					this.picTab = false
					this.realTime = 'list'
				}else if(value==='pic'){
					this.realTime='pic'
					this.listTab = false
					this.picTab = true
				}

				this.$emit('realTime',this.realTime)
        // 本地缓存
        let storage = window.localStorage;
        if (!storage.getItem("realTimeChange")){
          storage.setItem("realTimeChange",this.realTime);
        }else{
          storage.removeItem('realTimeChange');
          storage.setItem("realTimeChange",this.realTime);
        }
			},
			
			 // add by ywj
      tableRowDblClick(row, column, event){
        this.$emit('detailit',row)
      },
      // add by ywj end

			searchEnterFun(e){									//enter搜索函数
				var keyCode = window.event?e.keyCode:e.which;
				if(keyCode===13){
					this.meetingSearch()
				}
			},
			changeSearch(val){
				// console.log(val)
				
				if(val===2||val==="2"){
					this.peerToPeerMeetingSearch = true
					this.multiPointMeetingSearch = false
				}else if(val==="3"||val===3){
					this.peerToPeerMeetingSearch = false
					this.multiPointMeetingSearch = true
				}
			},
      meetingSnapShotclose(){                     //关闭会议快照弹出框
        this.meetingSnapShot = false
        this.snapShotStatu=null
        this.showSnapShot = false
      },
      giveTimeSpanShot(){                         //传递id
        var params={
          "key":this.snapShotObj.conf_id
        }
        this.$refs.timeRange.createSnapshots(params)
      },
      downSnapShot(){                                         //下载快照
        this.$refs.timeRange.downloadSnapshots()
        this.meetingSnapShot=false
        this.snapShotStatu=null
        this.showSnapShot = false
      },
      snapshotsStatu(val){
        this.snapShotStatu = val
      },
      snapShot(index,data){                                     //会议快照
        this.meetingSnapShot = true
        this.showSnapShot = true
        this.snapShotObj = data[index]
				// console.log(this.snapShotObj.start_time)
        this.timeRange = [this.snapShotObj.start_time-60000 ,(new Date()).valueOf()]
      },
      timestampToTime(timestamp) {                            //时间转换
        var date = new Date(timestamp);//时间戳为10位需*1000，时间戳为13位的话不需乘1000
        var Y = date.getFullYear() + '-';
        var M = (date.getMonth()+1 < 10 ? '0'+(date.getMonth()+1) : date.getMonth()+1) + '-';
        var D = (date.getDate()<10 ? '0'+date.getDate() : date.getDate()) + ' ';
        var h = (date.getHours()<10 ? '0'+date.getHours():date.getHours())  + ':';
        var m = (date.getMinutes()<10 ? '0'+date.getMinutes():date.getMinutes() ) ;
        var s = (date.getSeconds()<10 ? '0'+date.getSeconds():date.getSeconds()) ;
        return Y+M+D+h+m;
      },
			getdata(){                                //初始化数据
        if (this.moid[0]){
          this.platform_moid=this.moid[0].platform_moid
        }
        if(this.moid[1]){
          this.user_moid=this.moid[1].user_moid
        }else{
          this.user_moid=''
        }
				this.conf_type = this.MeetingSearch.conf_type
        var params={
          "conf_type":this.conf_type,
          "conf_status":"1",
          "start":0,
          "count":this.count,
          'platform_moid':this.platform_moid,
          'domain_moid':this.user_moid,
					'conf_media_type':this.MeetingSearch.conf_media_type,
        }
        this.pageDisabled = true
        this.disabledSearch = true
        this.loadingTableData = true
        this.requestFunction(params)
        this.setTimer(20)
			},
			returnit() {																				//返回上一级
				this.$emit('returnit',0)
			},
			Meetingdetails(index,data){																		//详情按钮事件
				this.$emit('detailit',data[index])
			},
			meetingSearch(){			//搜索表单内容
        this.start = 1
        this.currentPage=1
        this.loadingTableData = true
        if (this.moid[0]){
          this.platform_moid=this.moid[0].platform_moid
        }
        if(this.moid[1]){
          this.user_moid=this.moid[1].user_moid
        }else{
          this.user_moid=''
        }
        if (this.MeetingSearch.conf_type === 2){
          this.MeetingTable=[]
          this.multiPointMeeting=false
          this.peerToPeerMeeting=true
        }else{
          this.multiPointMeeting=true
          this.peerToPeerMeeting=false
        }
        if (this.MeetingSearch.searchTime){
          var startdate = new Date(this.MeetingSearch.searchTime[0])
          this.startTime = startdate.valueOf()
          var enddate = new Date(this.MeetingSearch.searchTime[1])
          this.endTime = enddate.valueOf()
        }else {
          this.startTime=''
          this.endTime=''
        }
				this.conf_type = this.MeetingSearch.conf_type
        var params={
          'conf_type':this.conf_type,
          'platform_moid':this.platform_moid,
          'domain_moid':this.user_moid,
          "conf_status":"1",
          "start_time":this.startTime,
          "end_time":this.endTime,
          'level':this.MeetingSearch.level,
          'keywords':this.MeetingSearch.keywords,
          'start':(this.start-1)*this.count,
          'count':this.count,
					'conf_media_type':this.MeetingSearch.conf_media_type,
        }
        if(params.level===''){
          delete params.level
        }
        this.pageDisabled = true
        this.disabledSearch = true
        this.loadingTableData = true
        this.requestFunction(params)
			},
			currentChange(val){         //分页
        if(this.total!==0){
          this.currentPage = val
          if (val>0){
            this.start = val
            var params={
              'conf_type':this.conf_type,
              'platform_moid':this.platform_moid,
              'domain_moid':this.user_moid,
              "conf_status":"1",
              "start_time":this.startTime,
              "end_time":this.endTime,
              'level':this.MeetingSearch.level,
              'keywords':this.MeetingSearch.keywords,
              'start':(this.start-1)*this.count,
              'count':this.count,
							'conf_media_type':this.MeetingSearch.conf_media_type,
            }
          }
          this.pageDisabled = true
          this.disabledSearch = true
          this.loadingTableData = true
          this.requestFunction(params)
        }
			},
      // 定时刷新参数
      timeParams(){
        var params ={
          'conf_type':this.conf_type,
          'platform_moid':this.platform_moid,
          'domain_moid':this.user_moid,
          "conf_status":"1",
          "start_time":this.startTime,
          "end_time":this.endTime,
          'level':this.MeetingSearch.level,
          'keywords':this.MeetingSearch.keywords,
          'start':(this.currentPage-1)*this.count,
          'count':this.count,
					'conf_media_type':this.MeetingSearch.conf_media_type,
        }
        this.requestFunction(params)
      },
      requestFunction(params){
        this.$api.monitor.meetingGet(params).then(res=>{
          if (res.data.success === 1){
            // console.log(res.data.data)
            var nowTime = res.data.data.curr_time
            this.total = res.data.data.total
            this.start = res.data.data.start + 1
            for (var i=0; i<res.data.data.info.length;i++){
              if(res.data.data.info[i].conf_type ===0){
                res.data.data.info[i]['会议类型'] = '传统会议'
              }else if(res.data.data.info[i].conf_type ===1){
                res.data.data.info[i]['会议类型'] = '端口会议'
              }else if(res.data.data.info[i].conf_type===2){
                res.data.data.info[i]['会议类型'] = '点对点会议'
              }
							
							//2.0 会议资源类型
              if(res.data.data.info[i].conf_media_type ===0){
                res.data.data.info[i]['会议资源类型'] = '本地会议'
              }else if(res.data.data.info[i].conf_media_type ===1){
                res.data.data.info[i]['会议资源类型'] = '云会议'
              }
							
              res.data.data.info[i].startTime =	this.timestampToTime(Number(res.data.data.info[i].start_time))
              if(res.data.data.info[i].end_time === "MANUAL"){
                res.data.data.info[i].endTime = "手动结束"
                var total_time = (nowTime -res.data.data.info[i].start_time)/1000
              }else if(res.data.data.info[i].end_time === "ABEND"){
                res.data.data.info[i].endTime = "异常结束"
                var total_time = ""
              }else if(res.data.data.info[i].end_time === "REALTIME"){
                var total_time = (nowTime -res.data.data.info[i].start_time)/1000
              }else {
                res.data.data.info[i].endTime = this.timestampToTime(Number(res.data.data.info[i].end_time))
                var total_time = (nowTime -res.data.data.info[i].start_time)/1000
              }
              if(total_time !==""){
                if (total_time<60){
                  total_time = total_time+'秒'
                }else if (total_time<60*60){
                  total_time = parseInt(total_time/60)+'分'+parseInt((total_time-parseInt(total_time/60)*60))+'秒'
                }else{
                  var miao = total_time-parseInt(total_time/60/60)*60*60-parseInt((total_time-parseInt(total_time/60/60)*60*60)/60)*60
                  total_time = parseInt(total_time/60/60)+'时'+parseInt((total_time-parseInt(total_time/60/60)*60*60)/60)+'分'+parseInt(miao)+'秒'
                }
              }

              res.data.data.info[i]['total_time']=total_time
            }
            this.MeetingTable = res.data.data.info
          }else{
            console.log(res.data.msg)
          }
          this.loadingTableData = false
          this.disabledSearch = false
          this.pageDisabled = false
        }).catch(err=>{
          this.loadingTableData = false
          this.disabledSearch = false
          this.pageDisabled = false
        })
      },
      // 定时刷新
      setTimer(interver=60,range=3600000) {
        this.clearTimer();
        this.timer = setInterval(() => {
          this.timeParams()
        },interver*1000)
      },
      // 清除定时器
      clearTimer(){
        clearInterval(this.timer);
        this.timer = null;
      },
		},
		mounted(){
      // console.log(window.localStorage.getItem("realTimeChange"))
      // 本地缓存
      if(window.localStorage.getItem("realTimeChange")){
        this.typesChange(window.localStorage.getItem("realTimeChange"))
      }

			this.getdata()													//初始化加载

		},
		watch: {																	//监听数据变化
				moid(newV,oldV) {
						this.meetingSearch()
				},
				realList(newV,oldV){
					this.typesChange("list")
				}
		},
    beforeDestroy () {
      this.clearTimer()

    },
		}

</script>

<style>
	.meetingSearch1 .el-form-item{
		margin-right: 0px;
		margin-bottom: 10px;
	}
	.changeCallTerminal.active {
		background-color: #485a6b;
		color: #fff;
		width: 60px;
		height: 24px;
		border: 0;
	}
	.changeCallTerminal:hover{
		color:#00a2ff;
	}
	.changeCallTerminal{
		background-color: #232629;
		color: #fff;
		width: 60px;
		height: 24px;
		border: 1px solid #485a6b;
		font-size: 12px;
		cursor:pointer;
	}

</style>
