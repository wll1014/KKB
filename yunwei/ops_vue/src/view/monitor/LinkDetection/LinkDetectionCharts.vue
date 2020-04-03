<template>
	<div class="theme-dark linkCharts" style="background: #232629;padding: 21px 0 0 17px;width:100%;height:100%">
    <!--标题-->
		<span style='font-size: 14px;color:#9ca9b1;float: left;' v-if='meetingLink'>
			{{linkTitle}}
		</span>
    <!--是否失败返回错误信息-->
   <!-- <span style="font-size: 14px;color:#db4c4c;float: left;" v-if="titleAddError!==[]">
      {{titleAddError[0]}}
    </span> -->
    <!--呼叫链路时间选择-->
		<span v-if='callLink'>
			<el-select
				v-model="selectvalue"
				placeholder="请选择影响类型"
				style='float: left;width: 440px;'
				popper-class="theme-dark linkCharts"
				@change="conferenceType"
        @visible-change="getCallId"
				>
				<el-option
					v-for='item in timeOptions'
					:key='item.id'
					:label='item.timestamp+item.id'
					:value='item.id'></el-option>
			</el-select>
		</span>
    <!--图例-->
    <span style="color: #9ca9b1;float: right;margin-right: 37px;font-size: 14px">异常链路</span>
    <i class="ops-icons-bg icon-legend-red" style="float: right;margin-right: 7px;margin-top: 6px"></i>
    <span style="color: #9ca9b1;float: right;margin-right: 27px;font-size: 14px">正常链路</span>
    <i class="ops-icons-bg icon-legend-blue" style="float: right;margin-right: 7px;margin-top: 6px"></i>
    <br><br><br>
    <!--是否展示链路上方图标-->
    <div v-if='showAll&&getData.points!==[]&&timeOptions' >
      <i class='ops-icons-bg icon-link-model-terminal' :style='iconLinkStyleBegin' v-if="getData.points.length === 4"></i>
      <i class='ops-icons-bg icon-link-model-meetting' :style='iconLinkStyleBegin' v-if="getData.points.length === 2"></i>
      <i class='ops-icons-bg icon-link-model-terminal' :style='iconLinkStyleBegin' v-if="getData.points.length === 3"></i>
      <span v-if="getData.points.length===4">
			  <i class='ops-icons-bg icon-link-model-meetting' :style='iconLinkStyleOthers'></i>
        <i class='ops-icons-bg icon-link-model-meetting' :style='iconLinkStyleOthers'></i>
        <i class='ops-icons-bg icon-link-model-platform' :style='iconLinkStyleOthers'></i>
      </span>
      <span v-if="getData.points.length===2">
			  <i class='ops-icons-bg icon-link-model-meetting' :style='iconLinkStyleOthers' ></i>
      </span>
      <span v-if="getData.points.length===3">
        <i class='ops-icons-bg icon-link-model-meetting' :style='iconLinkStyleOthers' ></i>
        <i class='ops-icons-bg icon-link-model-platform' :style='iconLinkStyleOthers' ></i>
      </span>
      <br><br>
    </div>
    <div v-if='showAll&&getData.points!==[]&&!timeOptions'>
      <i class='ops-icons-bg icon-link-model-meetting' :style='iconLinkStyleBegin'></i>
      <span v-for="(picture,index) in getData.points.length-1" :key='index'  v-if="getData.points.length!==3">
			  <i class='ops-icons-bg icon-link-model-meetting' :style='iconLinkStyleOthers'></i>
      </span>
      <span v-if="getData.points.length===3">
        <i class='ops-icons-bg icon-link-model-meetting' :style='iconLinkStyleOthers' ></i>
        <i class='ops-icons-bg icon-link-model-meetting' :style='iconLinkStyleOthers' ></i>
      </span>
      <br><br>
    </div>
		<br>
		<div class="linkChartsActor" v-for=' (modelLink,index) in modelLinkChange' :key='index'>
			<!-- <text :x="modelLink.x-16" :y="modelLink.y" fill='#fff'> -->
				<!-- <tspan :x="modelLink.x-16" > -->
					<!-- {{modelLink.name}} -->
				<!-- </tspan> -->
			<!-- </text> -->
			<!--<el-popover placement="top-start"  trigger="hover" popper-class="theme-dark">-->
			  <!--<div style='margin: 0px;padding: 0px;' >{{modelLink.name}}</div>-->
				<!--<span slot="reference" v-if='index===0&&modelLink.name.length>10' style="text-align:center;font: 微软雅黑 14px;width: 42px;font-size: 14px;" center :style="NameLinkStyleBegin">{{ modelLink.name.substr(0,10)+'...' }}</span>-->
				<!--<span slot="reference" v-if='index===0&&modelLink.name.length<=10' style="text-align:center;font: 微软雅黑 14px;width: 42px;font-size: 14px;" center :style="NameLinkStyleBegin">{{ modelLink.name}}</span>-->
				<!--<span slot="reference" v-if='index!==0&&modelLink.name.length>10' style="text-align:center;font: 微软雅黑 14px;width: 42px;font-size: 14px;" center :style="NameLinkStyleOthers">{{ modelLink.name.substr(0,10)+'...' }}</span>-->
				<!--<span slot="reference" v-if='index!==0&&modelLink.name.length<=10' style="text-align:center;font: 微软雅黑 14px;width: 42px;font-size: 14px;" :style="NameLinkStyleOthers">{{ modelLink.name}}</span>-->
			<!--</el-popover>-->
		<!-- 	<el-tootip style="width:70px" content="Top center" placement="top">
				<span v-if="index===0" :style="iconLinkStyleBegin">{{modelLink.name}}</span>
			</el-tootip> -->
      <span slot="reference" v-if='index===0' style="text-align:center;font: 微软雅黑 14px;width: 42px;font-size: 14px;" center :style="NameLinkStyleBegin">{{ modelLink.name}}</span>
      <span slot="reference" v-if='index!==0' style="text-align:center;font: 微软雅黑 14px;width: 42px;font-size: 14px;" :style="NameLinkStyleOthers">{{ modelLink.name}}</span>
			<!-- <span v-if='index!==0' :style="iconLinkStyleOthers">{{modelLink.name}}</span> -->
		</div>
		<br>
		<svg class="sequence simple linkTest" :width="width" :height="height" style="background: #232629;">
			<!-- 设置箭头长度及样式 -->
			<!-- defs引入箭头容器 -->
			<defs>
				<marker viewBox="0 0 5 5" markerWidth="5" markerHeight="8" orient="auto" refX="5" refY="2.5" id="markerArrowBlockRed" fill="#fb265d">
					<!-- 闭合箭头实心三角形 -->
          <path d="M 0 0 L 5 2.5 L 0 5 z" fill="#fb265d"></path>
				</marker>
        <marker viewBox="0 0 5 5" markerWidth="5" markerHeight="8" orient="auto" refX="5" refY="2.5" id="markerArrowBlockBlue"  fill="#5eb9ef">
          <!-- 闭合箭头实心三角形 -->
          <path d="M 0 0 L 5 2.5 L 0 5 z" fill="#5eb9ef"></path>
        </marker>
			</defs>
			<!-- 设置竖线 -->
			<g class="linkChartsActor" v-for=' modelLink in modelLinkChange' :key='modelLink.index'>
			<!-- 	<text :x="modelLink.x-16" :y="modelLink.y" fill='#fff'>
					<tspan :x="modelLink.x-16" >
						{{modelLink.name}}
					</tspan>
				</text> -->
				<line
					:x1= 'modelLink.x'
					:x2= 'modelLink.x'
					y1=	"33"
					:y2="y2"
					stroke-dasharray='1,1'
					stroke="#5f656a"
					fill="none"
					style="stroke-width: 1px;"
					v-if="processLinkChange">
				</line>
        <line
          :x1= 'modelLink.x'
          :x2= 'modelLink.x'
          y1=	"33"
          y2=	"600"
          stroke-dasharray='1,1'
          stroke="#5f656a"
          fill="none"
          style="stroke-width: 1px;"
          v-if="!processLinkChange">
        </line>
			</g>
			<g class='processLinks' v-for='processLink in processLinkChange' :key='processLink.index'>
				<!-- 向右 -->
				<text :x="(processLink.link1x+processLink.link0x)/2" :y="processLink.y+40-4.5-5" v-if='processLink.link0x<=processLink.link1x' style="text-anchor:middle;">
					<tspan :x="(processLink.link1x+processLink.link0x)/2">{{processLink.description}}</tspan>
				</text>
				<!-- 向左 -->
				<text :x="(processLink.link1x+processLink.link0x)/2" :y="processLink.y+40-4.5-5" v-if='processLink.link0x>processLink.link1x' style="text-anchor:middle;">
					<tspan :x="(processLink.link1x+processLink.link0x)/2">{{processLink.description}}</tspan>
				</text>
				<!-- 横线 -->
        <line
          class="red"
          :x1="processLink.link0x"
          :x2="processLink.link1x"
          :y1="processLink.y+40-4.5"
          :y2="processLink.y+40-4.5"
          stroke="#fb265d"
          fill="#fb265d"
          v-if="processLink.status===0"
          style="stroke-width: 2px; marker-end: url(#markerArrowBlockRed)"
          @mouseover="ShowTooltip(processLink)"
          @mouseleave="HideTooltip(processLink)"></line>

        <line
					:x1="processLink.link0x"
					:x2="processLink.link1x"
					:y1="processLink.y+40-4.5"
					:y2="processLink.y+40-4.5"
            stroke="#5eb9ef"
					fill="#5eb9ef"
          v-if="processLink.status===1"
					style="stroke-width: 2px; marker-end: url(#markerArrowBlockBlue)"
          @mouseover="ShowTooltip(processLink)"
          @mouseleave="HideTooltip(processLink)"></line>


				<!-- 每个小竖行宽度为4 -->
        <line
          :x1= 	"processLink.link0x"
          :x2= 	"processLink.link0x"
          :y1=	"processLink.y"
          :y2=	"processLink.y+40"
          stroke="#8a8989"
          fill="none"
          style="stroke-width: 3px;"
          @mouseover="ShowTooltip(processLink)"
          @mouseleave="HideTooltip(processLink)" v-if="processLink.y===processLinkChange[0].y"></line>
					<line
						:x1= 	"processLink.link1x"
						:x2= 	"processLink.link1x"
						:y1=	"processLink.y+15"
						:y2=	"processLink.y+55"
						stroke="#8a8989"
						fill="none"
						style="stroke-width: 3px;"
            @mouseover="ShowTooltip(processLink)"
            @mouseleave="HideTooltip(processLink)"></line>
			</g>

      <!-- tooptip -->
      <foreignObject
        :x="500"
        :y="reinfo[0].y+60"
        width="500"
        height=" 500px"
        v-if="showit&&this.type===1&&reinfo[0]"
        style="background-color: #141414;border: 1px solid #383b3c;margin-left: 5px;"
        @mouseover="onmouseover(reinfo)"
        @mouseleave="onmouseout(reinfo)"
        id="mouse">
        <div style="height: 500px;overflow: auto" >
          <el-tooptip placement="bottom-start" style="height:150px;overflow: auto">
            <div style="padding-left:14px;margin-top: 12px;font-size:14px;padding-right:14px;color: #9ca9b1; " v-for="reinfoOne in reinfo" :key='reinfoOne'>
              <span v-if="reinfoOne.keys">{{reinfoOne.keys}}:</span>
							<span>{{reinfoOne.i}}</span>
            </div>
          </el-tooptip>
        </div>
      </foreignObject>
      <foreignObject
        :x="91"
        :y="reinfo[0].y+60"
        width="500"
        height=" 500px"
        v-if="showit&&this.type===2&&reinfo[0]"
        style="background-color: #141414;border: 1px solid #383b3c;margin-left: 5px;"
        @mouseover="onmouseover(reinfo)"
        @mouseleave="onmouseout(reinfo)"
        id="mouse">
        <div style="height:500px;overflow: auto">
          <el-tooptip placement="bottom-start" style="height:150px;overflow: auto">
            <div style="padding-left:14px;margin-top: 12px;font-size:14px;padding-right:14px ;color: #9ca9b1;" v-for="reinfoOne in reinfo" :key='reinfoOne'>
              <span v-if="reinfoOne.keys">{{reinfoOne.keys}}:</span>
              <span>{{reinfoOne.i}}</span>
            </div>
          </el-tooptip>
        </div>
      </foreignObject>
			<!-- <foreignObject
				:x="91"
				:y="reinfo[0].y-300"
				width="500"
				height=" 500px"
				v-if="showit&&this.type===2&&reinfo[0]"
				style="background-color: #141414;border: 1px solid #383b3c;margin-left: 5px;"
				@mouseover="onmouseover(reinfo)"
				@mouseleave="onmouseout(reinfo)"
				id="mouse">
				<div style="height:500px;overflow: auto">
				    <el-tooptip placement="bottom-start" style="height:150px;overflow: auto">
				      <div style="padding-left:14px;margin-top: 12px;font-size:14px;padding-right:14px ;color: #9ca9b1;" v-for="reinfoOne in reinfo" :key='reinfoOne'>
				         <span>{{reinfoOne.i}}</span>
				      </div>
				    </el-tooptip>
				  </div>
				</foreignObject> -->
		</svg>
		<!--<div style="height: 42px;background-color: #232629" v-if="callLinkfull"></div>-->
	</div>
</template>
<script>

	export default{
    components:{
      // chartsRed : () => import('@/view/monitor/LinkDetection/chartsRed.vue'),
      // chartsBlue : () => import('@/view/monitor/LinkDetection/chartsBlue.vue'),
    },
		props:{
			leth:{
				type:Number,
				default:10
			},
			getData:{
				type:Object,
			},
			timeOptions:{
				type:Array,
				defaultList:[],
			},
			type:{
				type:Number,
				default:1
			},
      titleAddError:{
			  type:Array,
        defaultList: []
      },
      orLoading:{
			  type:Number,
        default:0
      }
		},
		data() {
			return {
        reinfo:[],                  //tooptip放入数组
        showit:false,               //tooptip是否展示
				showAll:false,              //展示会议链路
				meetingLink:true,           //展示会议信息
				callLink:false,             //展示呼叫链路
        callLinkfull:false,         //补充缺少部分的长度
				selectvalue:'',             //呼叫链路下拉菜单的值
				width:600,                  //屏幕整体宽度
				height:1000,                 //屏幕整体高度
				modelLinks:[],              //取到连线总体几个模块
				linkTitle:"会议链路",
				iconLinkStyleBegin:'',      //第一个图标开始的位置
				iconLinkStyleOthers:'',     //第二个及以后图标的位置
				NameLinkStyleOthers:'',
				NameLinkStyleBegin:'',
				modelLinkChange:[],
				processLinkChanges:[],      //取到连线的信息
				processLinkChange:[],
				strokecolor:'#5eb9ef',
				LinkInterval:300 ,                       //每个模块之间的宽度 整体布局
        y2:1000,
				halfy:0,
			}
		},
		methods:{
		  // tooptip鼠标事件
      onmouseover(reinfo){
        this.reinfo=reinfo
        // console.log(reinfo)
      },
      onmouseout(reinfo){
        setTimeout(()=>{
          this.showit=false
        },100)
      },
      ShowTooltip(e) {                          //tooptip--show
        // console.log(e)
				this.halfy=e.y
        var datas = []
        var y0=0
				// console.log(this.x)
        if(e.data){
          var a = "到达时间:"+this.timestampToTime(e.time)
          if(e.link1x===this.modelLinkChange[this.modelLinkChange.length-1].x){
            datas.push({i:a,il:"111",x:e.link1x-600,y:e.y+y0})
          }else if(e.link0x===this.modelLinkChange[this.modelLinkChange.length-1].x ){
            datas.push({i:a,il:"111",x:e.link0x-600,y:e.y+y0})
          }else {
            if(e.link0x>e.link1x){
              datas.push({i:a,il:"111",x:e.link1x,y:e.y+y0})
            }else if(e.link0x<=e.link1x){
              datas.push({i:a,il:"111",x:e.link0x,y:e.y+y0})
            }
          }
          for(var i in e.data){
            // console.log(i)
            if(e.link1x===this.modelLinkChange[this.modelLinkChange.length-1].x){
              datas.push({i:e.data[i],i1:i,x:e.link1x-600,y:e.y+y0,keys:i})
            }else if(e.link0x===this.modelLinkChange[this.modelLinkChange.length-1].x ){
              datas.push({i:e.data[i],i1:i,x:e.link0x-600,y:e.y+y0,keys:i})
            }else{
              if(e.link0x>e.link1x){
                datas.push({i:e.data[i],i1:i,x:e.link1x,y:e.y+y0,keys:i})
              }else if(e.link0x<=e.link1x){
                datas.push({i:e.data[i],i1:i,x:e.link0x,y:e.y+y0,keys:i})
              }
            }
            y0+=20
          }
        }
        // console.log(e.data[i])
        if(e.raw){
          var a = "到达时间:"+this.timestampToTime(e.time)
          if(e.link1x===this.modelLinkChange[this.modelLinkChange.length-1].x){
            datas.push({i:a,il:"111",x:e.link1x-600,y:e.y+y0})
          }else if(e.link0x===this.modelLinkChange[this.modelLinkChange.length-1].x ){
            datas.push({i:a,il:"111",x:e.link0x-600,y:e.y+y0})
          }else {
            if(e.link0x>e.link1x){
              datas.push({i:a,il:"111",x:e.link1x,y:e.y+y0})
            }else if(e.link0x<=e.link1x){
              datas.push({i:a,il:"111",x:e.link0x,y:e.y+y0})
            }
          }
          for(var i in e.raw){
            if(e.link1x===this.modelLinkChange[this.modelLinkChange.length-1].x ){
              datas.push({i:e.raw[i],i1:i,x:e.link1x-600,y:e.y+y0})
            }else if(e.link0x===this.modelLinkChange[this.modelLinkChange.length-1].x ){
              datas.push({i:e.raw[i],i1:i,x:e.link0x-600,y:e.y+y0})
            }else {
              if(e.link0x>e.link1x){
                datas.push({i:e.raw[i],i1:i,x:e.link1x,y:e.y+y0})
              }else if(e.link0x<=e.link1x){
                datas.push({i:e.raw[i],i1:i,x:e.link0x,y:e.y+y0})
              }
            }
            y0+=20
          }
        }
				
        this.reinfo = datas
        this.showit=true
      },
      HideTooltip() {                             //tooptip--hide
      },
      timestampToTime(timestamp) {                            //时间转换
        var date = new Date(timestamp);//时间戳为10位需*1000，时间戳为13位的话不需乘1000
        var Y = date.getFullYear() + '-';
        var M = (date.getMonth()+1 < 10 ? '0'+(date.getMonth()+1) : date.getMonth()+1) + '-';
        var D = (date.getDate()<10 ? '0'+date.getDate() : date.getDate()) + ' ';
        var h = (date.getHours()<10 ? '0'+date.getHours():date.getHours())  + ':';
        var m = (date.getMinutes()<10 ? '0'+date.getMinutes():date.getMinutes() ) + ':';
        var s = (date.getSeconds()<10 ? '0'+date.getSeconds():date.getSeconds());
        return Y+M+D+h+m+s;
      },
			changeIf(){                         //是否为呼叫链路
				this.meetingLink = false
				this.callLink = true
        this.callLinkfull = true
				// console.log(this.timeOptions)
        if(this.timeOptions.length!==0){
          if(this.timeOptions[0]){
            if(this.timeOptions[0].id){
              this.selectvalue = this.timeOptions[0].id
              this.$emit('timeOptionId',this.timeOptions[0].id)
            }
          }
        }
			},
			changeData(){                     //获取值后的处理
        this.processLinkChange = []
        this.processLinkChanges = []
        this.modelLinks=[]
        this.modelLinkChange=[]
        this.iconLinkStyleBegin=''
        this.iconLinkStyleOthers=''
				this.NameLinkStyleOthers=''
				this.NameLinkStyleBegin=''
        // 如果是type=1,则界面显示 会议或呼叫
				if (this.type === 1){
					this.width = 1350
					this.LinkInterval = 292       //屏幕整体每个模块的间隔
					this.x=249                    //画线开始位置
					this.y=20                     //画线开始位置
					this.iconLinkStyleBegin = 'float:left;margin-left:228px'        //第一个图标开始的位置
					this.NameLinkStyleBegin = 'float:left;margin-left:228px'
					this.NameLinkStyleOthers = 'float:left;margin-left:250px'
					this.iconLinkStyleOthers = 'float:left;margin-left:250px'       //第二个及以后图标的位置
          if(this.getData.points!==[]){
            // console.log(this.getData.info.length)
            if(this.getData.points.length===2){
              this.LinkInterval = 400
              this.x = 400
							this.NameLinkStyleBegin = 'float:left;margin-left:379px'
							this.NameLinkStyleOthers = 'float:left;margin-left:359px'
              this.iconLinkStyleBegin = 'float:left;margin-left:379px'        //第一个图标开始的位置
              this.iconLinkStyleOthers = 'float:left;margin-left:359px'       //第二个及以后图标的位置
            }
          }
          if(this.leth>=10){
            this.height = this.leth*55+600
          }
          if(this.leth>10){
            this.y2 = this.leth	*55+200
          }

				}
				// 如果type=2则显示会议和呼叫两个
				else if (this.type === 2){
				  // console.log(this.getData)
					this.width = 620
					this.LinkInterval = 165
					this.x=91
					this.y=20
					this.NameLinkStyleBegin = 'float:left;margin-left:70px'
					this.NameLinkStyleOthers = 'float:left;margin-left:123px'
					this.iconLinkStyleBegin = 'float:left;margin-left:70px'
					this.iconLinkStyleOthers = 'float:left;margin-left:123px'
          // console.log(this.getData)
          if(this.getData.points!==[]){
            if (this.getData.points.length === 3){
              this.width = 640                //若呼叫链路的模块为三个时
              this.LinkInterval = 247
              this.x=91
              this.y=20
              this.iconLinkStyleBegin = 'float:left;margin-left:70px'
              this.iconLinkStyleOthers = 'float:left;margin-left:205px'
							this.NameLinkStyleBegin = 'float:left;margin-left:70px'
							this.NameLinkStyleOthers = 'float:left;margin-left:205px'
							
            }else if(this.getData.points.length === 2){
							this.LinkInterval = 400
							this.x = 120
							this.NameLinkStyleBegin = 'float:left;margin-left:99px'
							this.NameLinkStyleOthers = 'float:left;margin-left:358px'
							this.iconLinkStyleBegin = 'float:left;margin-left:99px'        //第一个图标开始的位置
							this.iconLinkStyleOthers = 'float:left;margin-left:358px'       //第二个及以后图标的位置
						}
          }
				}
				 if(this.leth>10){
				  this.height = this.leth*55+600
				}
				if(this.leth>10){
				  this.y2 = this.leth	*55+200
				}
				this.showAll=true
				this.modelLinks = this.getData.points
				this.processLinkChanges = this.getData.info
				if (this.processLinkChanges.link0){
					this.processLinkChange = this.processLinkChanges
				}else{
					for ( var i in this.modelLinks ){
						this.modelLinkChange[i] = {
							'x':this.x,
							'y':this.y,
							'name':this.modelLinks[i]
						}
						this.x = this.x + this.LinkInterval
					}
					//取x值
					for (var j in this.processLinkChanges){
						for (var i in this.modelLinkChange){
							if (this.processLinkChanges[j].src === this.modelLinkChange[i].name){
								this.processLinkChanges[j]['link0x'] = this.modelLinkChange[i].x
							}
							if (this.processLinkChanges[j].dst === this.modelLinkChange[i].name){
								this.processLinkChanges[j]['link1x'] = this.modelLinkChange[i].x
							}
						}
						//取y值
            this.processLinkChanges[j]['y'] = 93+55*j

					}
          this.callLinkfull=false
					this.processLinkChange = this.processLinkChanges
				}
				// console.log(this.modelLinks)
				// console.log(this.processLinkChange)
			},
			conferenceType(val){                        //发送值给父组件
				this.$emit('timeOptionId',val)
        this.getdata = ''
			},
      getCallId(){
        // var val = this.callId
        // this.$api.monitor.callConfId(val).then(res=>{
        //   if (res.data.success===1){
        //     //获取呼叫时间选项
        //     this.createTime = res.data.data.create_time
        //     this.endTime = res.data.data.end_time
        //     this.timeOptions = res.data.data.info
        //   }else if (res.data.success === 0){
        //     console.log(res.data.msg)
        //   }
        // })
      },
		},
		mounted(){
		},
		watch: {
			getData(newValue, oldValue){                    //监听父组件传值
				// console.log(newValue)
				this.changeData()
        this.getData = newValue
        // console.log(this.timeOptions)
			},
			timeOptions(newValue, oldValue){
			  // console.log(newValue)
				this.timeOptions = newValue
				this.changeIf()
			},
			type(newValue,oldValue){
			  // console.log(newValue)
				this.changeData()
			},
      titleAddError(newV,oldV){
			  // console.log(newV)
      },
      orLoading(newV,oldV){
			  // console.log(newV)
      },
			leth(newV,oldV){
				// console.log(newV)
				this.changeData()
			},
		},
	}
</script>

<style>
	/* 字体颜色 */
	.linkTest tspan{
		stroke: none;
		fill:#9ca9b1;
		font-size:14px;
	}
  .linkCharts .el-select-dropdown__item {
    padding-left: 10px;
    padding-right: 10px;
  }
  .linkCharts ::-webkit-scrollbar-corner{
    background: #161617;
  }
  .red marker path {
    fill:#fb265d
  }
	.linkChartsActor .el-popover{
		padding: 0;
		background: #141414;
	}
</style>
