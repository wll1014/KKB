<template>
    <div class="theme-dark" style="position: relative;background-color: #232629;">
      <!--下拉菜单区域-->
      <!-- <div style="position: absolute;top:8px;left: 16px;z-index: 1000"> -->
			<div style="position: absolute;top:8px;left: 16px;z-index: 1">
        <el-dropdown placement="bottom-start" trigger="click" @command="handleDropdownChange">
        <span class="el-dropdown-link" style="font-size: 14px;color:#9ca9b1;cursor: pointer;">
          {{activeTable.name}}<i style="font-size: 13px;" class="el-icon-arrow-down el-icon--right"></i>
        </span>
          <el-dropdown-menu class="theme-dark" slot="dropdown" style="width: 150px">
            <el-dropdown-item v-for="item in tableType" :command="item" :key="item.identifier">{{item.name}}</el-dropdown-item>
          </el-dropdown-menu>
        </el-dropdown>
      </div>
      <!--更多按钮区域-->
      <!-- <div style="position: absolute;top:9px;right: 20px;z-index: 1000"> -->
			<div style="position: absolute;top:9px;right: 20px;z-index: 1">	
        <button type="button" class="ops-button-text" @click="buttonMore(activeTable)">
          <span style="font-size: 12px;">更多</span>
        </button>
      </div>
      <!--告警统计数据-->
      <div style="padding-top: 36px;">
        <div style="width: 100%;font-size: 0px;">
          <div class="alarm-info-short-statistics">
            <i class="ops-icons-bg icon-face-critical" style=""></i>
            <span class="alarm-info-short-text">{{alertLvlPct[0]}}</span>
          </div>
          <div class="alarm-info-short-statistics">
            <i class="ops-icons-bg icon-face-important" style=""></i>
            <span class="alarm-info-short-text">{{alertLvlPct[1]}}</span>
          </div>
          <div class="alarm-info-short-statistics">
            <i class="ops-icons-bg icon-face-normal" style=""></i>
            <span class="alarm-info-short-text">{{alertLvlPct[2]}}</span>
          </div>
        </div>
      </div>

      <!--告警信息详细-->
      <div class="area-alarm-table" style="padding-left: 16px;padding-right: 16px;">
          <div class="alarm-table">
            <div v-if="alertInfo.length!==0" style="height: 100%">
              <div :class="['alarm-table-row',{'single-row':!(index%2)}]" v-for="(item,index) in alertInfo" >
                <div class="alarm-table-column" style="width:5%;">
                  <span class="span-column">{{index+1}}</span>
                </div>
                <div class="alarm-table-column" style="width:34%;" >
                    <span class="span-column"
                          @mouseover.self="isHiden($event,item.start_time)"
                          @mouseout="removeTootipLayer">
                      {{item.start_time}}
                    </span>
                </div>
                <div class="alarm-table-column" style="width:22%;">
                  <span class="span-column"
                        @mouseover.self="isHiden($event,item.device_name)"
                        @mouseout="removeTootipLayer">
                      {{item.device_name}}</span>
                </div>
                <div class="alarm-table-column" style="width:39%;">
                  <span class="span-column"
                        @mouseover.self="isHiden($event,item.name)"
                        @mouseout="removeTootipLayer">
                      {{item.description}}</span>
                </div>
              </div>
            </div>
            <div style="color: #9ca9b1;font-size: 24px;height: 100%;text-align: center;line-height: 100%;position: relative;" v-if="noAlarmInfo">
              <span style="vertical-align:middle;position: absolute;top:calc(50% - 12px);left: calc(50% - 96px)">一周内无订阅告警</span>
            </div>
          </div>
      </div>

    </div>
</template>

<script>
export default {
  name: "AreaAlarmInfoShort",
  props:{
    // echart实例化ID
    ChartID:String,
    // 下拉菜单选择项
    chartList:Array,
  },
  data() {
    return {
      // 定时器实例
      timer:'',
      // 判断当前列是否显示
      statusIsHiden:'',

      tableType:[
        {
          name:"终端订阅告警",
          identifier:"alarmMt",
          routerPush:"alarmMt",
        },
        {
          name:"服务器订阅告警",
          identifier:"alarmDev",
          // routerPush:"/ops/monitor/alarm?type=dev",
          routerPush:"alarmDev",
        },
      ],
      activeTable:'',

      // 告警统计信息
      alertLvlPct:[],
      alertInfo:[],

      // 是否有告警的标志
      noAlarmInfo:false,
    }
  },
  methods: {
    // 下拉菜单函数
    handleDropdownChange(command){
      this.clearTimer()
      this.activeTable=command
      this.getAlarmInfoShort()
      this.setTimer(30)
    },

    buttonMore(chartConf){
      this.$router.push({
        name:'monitor-alarm',
        // path:chartConf.routerPush
        params:{type:chartConf.routerPush}
      });
    },

    // 设置行高for 垂直居中
    setSpanColumnLineHeight(){
      let temDom=document.querySelector('div.alarm-table-column')
      if(temDom){
        let divHeight=temDom.offsetHeight
        let spanColumnDomList=document.querySelectorAll('span.span-column')
        // console.log(spanColumnDomList)


        spanColumnDomList.forEach((item)=>{
          item.style["line-height"]=divHeight+"px";
        })
      }
    },

    // 模块功能函数start
    // 判断是否长度超过div
    isHiden(e,text){
      let spanWidth=e.currentTarget.offsetWidth
      let columnWidth=e.currentTarget.parentNode.offsetWidth
      let dom=e.currentTarget

      if(spanWidth+5>columnWidth){
        this.addTootipLayer(e,text)

      }
      // console.log(e.clientX,e.clientY)
    },

    // 添加tootip
    addTootipLayer(e,text){
      let left = e.clientX
      let top = e.clientY
      let bgObj = document.createElement("div");
      bgObj.style.cssText = `position:absolute;
                            top:${top+5}px;
                            left:${left}px;
                            color:#fff;
                            background:#333;
                            max-width:400px;
                            border-radius:5px;
                            padding:10px;
                            display:inline-block;
                            font-size:12px;
                            z-index:999`;

      bgObj.setAttribute('id', 'bgObj');
      document.body.appendChild(bgObj);
      document.querySelector('#bgObj').innerHTML = text;
    },
    // 删除tootip
    removeTootipLayer(){
      let bgObj = document.querySelector('#bgObj');
      if (bgObj) {
        document.body.removeChild(bgObj);
      }
    },

    // 功能函数start
    // 返回值转换；涉及字段：告警级别，时间
    convertTableData(data){
      if(data){
        let alarmType={critical:'严重',important:'重要',normal:'一般'}
        let newData=data.map((item)=>{
          item.level=alarmType[item.level]
          item.start_time=item.start_time ? new Date(item.start_time).format('Y-m-d H:i:s') : ''
          item.resolve_time=item.resolve_time ? new Date(item.start_time).format('Y-m-d H:i:s') : ''
          return item
        })
        return newData
      }
    },
    // 功能函数end
    // 模块功能函数end

    // API start
    async getAlarmInfoShort(startTime,endTime){
      let alarmInfoData=''
      let alarmInfoPct=''
      if(!startTime && !endTime){
        let timestamp = (new Date()).getTime();
        startTime=new Date().setHours(0, 0, 0, 0)-86400000*6
        endTime=timestamp
      }

      // // 测试调整临时params固定时间
      // startTime=1569200400000
      // endTime=1569214800000
      // // 测试调整临时params固定时间end

      // console.log(startTime,endTime)
      if(this.activeTable.identifier==="alarmDev"){
        let params={
          start_time:startTime,
          end_time:endTime,
          level:'',
          // start:0,
          // count:5
        }
        alarmInfoData=await this.$api.monitor.getAlarmInfoServerUnrepaired(params)
        // alarmInfoData=await this.$api.monitor.getAlarmInfoServerRepaired(params)
        alarmInfoPct=await this.$api.homePage.getAlarmInfoServerPct(params)
        // console.log(alarmInfoData)
      }else if(this.activeTable.identifier==="alarmMt") {
        let params = {
          start_time: startTime,
          end_time: endTime,
          level: '',
          // start:0,
          // count:5
        }
        alarmInfoData = await this.$api.monitor.getAlarmInfoTerminalUnrepaired(params)
        alarmInfoPct=await this.$api.homePage.getAlarmInfoTerminalPct(params)
      }
      // console.log(getData)
      this.alertLvlPct=[
        (alarmInfoPct.alert_lvl_pct.data.critical*100).toFixed(0)+"%",
        (alarmInfoPct.alert_lvl_pct.data.important*100).toFixed(0)+"%",
        (alarmInfoPct.alert_lvl_pct.data.normal*100).toFixed(0)+"%",
      ]
      this.alertInfo=this.convertTableData(alarmInfoData.info)

      if (this.alertInfo.length === 0){
        this.noAlarmInfo=true
      } else {
        this.noAlarmInfo=false
      }

      this.$nextTick(() => {
        this.setSpanColumnLineHeight()
      })
    },
    // API end

    // 定时器函数start
    // 设置定时器
    setTimer(interver=60,range=3600000){
      this.clearTimer();
      this.timer = setInterval(() => {
        // console.log(range)
        // console.log(interver)
        this.getAlarmInfoShort()
      },interver*1000)
    },
    // 清除定时器
    clearTimer(){
      clearInterval(this.timer);
      this.timer = null;
    },
    // 定时器函数end

    async init(){
      this.activeTable=this.tableType[0]
      this.getAlarmInfoShort()
      window.addEventListener("resize",this.setSpanColumnLineHeight)
      this.setTimer(30)
    },
  },
  mounted(){
      this.init()
  },
  beforeDestroy () {
    this.clearTimer()
    window.removeEventListener("resize",this.setSpanColumnLineHeight)
  },
}
</script>

<style>
.alarm-info-short-statistics{
  height: 100%;
  display: inline-block;
  text-align: center;
  vertical-align: top;
  width: 33%;
}
.alarm-info-short-icon{
  font-size: 20px;
  vertical-align: middle;
}
.alarm-info-short-text{
  font-size: 14px;
  color: #9ca9b1;
  margin-left: 9px;
  vertical-align: top;
  line-height: 20px;
}

.area-alarm-table{
  /*height: calc(83% - 42px);*/
  height: calc(100% - 76px);
  margin-top: 9px;
}
.alarm-table{
  color: #9ca9b1;
  font-size: 0px;
  height: 100%;
}
.alarm-table-row{
  /*margin-bottom: 8px;*/
  height: 20%;
  display: block;
  vertical-align: middle;
  /*line-height: 24px;*/
}
.alarm-table-row.single-row{
  /*margin-bottom: 8px;*/
  background-color: #272c2e;
}
.alarm-table-column{
  display: inline-block;
  /*margin-top: 2px;*/
  text-align: left;
  /*margin-right: 1px;*/
  vertical-align: middle;
  font-size:12px;
  overflow: hidden;
  text-overflow:ellipsis;
  white-space: nowrap;
  height: 100%;
}
.span-column{
/*line-height: 24px;*/
  margin-left: 4px;
  /*display: inline-block;*/
  /*height: 100%;*/
  /*white-space: nowrap;*/
  /*vertical-align: middle;*/
}
</style>
