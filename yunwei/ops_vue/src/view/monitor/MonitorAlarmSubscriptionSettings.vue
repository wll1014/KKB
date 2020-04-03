
<template>
	<div style="background-color: #222526;">
    <div v-if="!isDetail">
      <div v-if="isSubSetting">
        <span style="color:#9ca9b1;font-size: 12px;margin: 0px 0px 0px 25px;line-height: 40px;">告警级别</span>
        <div style="display: inline-block;">
          <el-checkbox style="color:#9ca9b1;margin-left: 60px;" v-for="item in alarmType" v-model="checkedType[item.type]" :key="item.type" @change="handleCheckTypeChange($event,item)">{{item.label}}</el-checkbox>
        </div>
      </div>
      <div v-for="item in alarmCodes">
        <KdCheckboxGroup :title="item.name" :checkboxProps="checkboxProps" :checkboxData="item.data" @checked-change="handleCheckedAlarmCodesChange"></KdCheckboxGroup>
      </div>
    </div>
    <div v-if="isDetail" style="padding: 0px 25px;font-size: 12px;">
        <div v-for="(val,key) in detailPageData" class="alarmsub-block">
          <div class="alarmsub-block--title">
            <span>{{key}}</span>
            <span style="float: right;">已选 {{val.length}}</span>
          </div>
          <div style="width: 100%;box-sizing: border-box;padding: 0px 24px;">
            <div v-for="item in val" class="alarmsub-block--content">
              <span>{{item.name}}</span>
            </div>
          </div>
        </div>
    </div>
    <!--<div>
      <el-button @click="configSave">确定</el-button>
      <el-button @click="configCancel">取消</el-button>
    </div>-->
	</div>
</template>
<script>
  export default {
    components: {
      KdTabCommon: () => import('@/components/common/KdTabCommon.vue'),
      KdCheckboxGroup: () => import('@/components/common/KdCheckboxGroup.vue'),
    },
    props:{
      isSubSetting:{
        type: Boolean,
        default: true,
      },
      checkedCodes:{
        type: Array,
        default: function () {
          return []
        },
      },
      isDetail:{
        type:Boolean,
        default:false,
      }
    },
    computed:{
      codesChange(){

        let codeList = []
        // for(let k in this.checkedAlarmCodes){
        //   codeList=codeList.concat(this.checkedAlarmCodes[k])
        // }
        codeList=Object.values(this.checkedAlarmCodes).flat()
        // console.log(this.alarmRawData.filter(item => item.code === codeList[0]))
        let s = codeList.flatMap(item => this.alarmRawData.filter(i => i.code === item))
        return s
      },
    },
    watch:{
      codesChange:{
        deep:true,
        handler:function(newVal,oldVal){
          if(this.isSubSetting){ //如果是订阅告警页面
            let criticalLen=this.alarmRawData.filter(item => item.level==='critical').length
            let importantLen=this.alarmRawData.filter(item => item.level==='important').length
            let normalLen=this.alarmRawData.filter(item => item.level==='normal').length

            if(newVal.length === this.alarmRawData.length){
              // this.$set(this.checkedType,'critical',true)
              this.$set(this.checkedType,'all',true)
            }else {
              this.$set(this.checkedType,'all',false)
            }
            if(newVal.filter(item => item.level==='critical').length === criticalLen){
              this.$set(this.checkedType,'critical',true)
            }else{
              this.$set(this.checkedType,'critical',false)
            }
            if(newVal.filter(item => item.level==='important').length === importantLen){
              // console.log(importantLen,newVal.filter(item => item.level==='important').length)
              this.$set(this.checkedType,'important',true)
            }else{
              this.$set(this.checkedType,'important',false)
            }
            if(newVal.filter(item => item.level==='normal').length === normalLen){
              this.$set(this.checkedType,'normal',true)
            }else{
              this.$set(this.checkedType,'normal',false)
            }
          }
        }
      },
    },
    data() {
      return {

        checkboxProps:{
          id: 'code',
          label: 'name',
          isChecked:'sub',
        },

        alarmType:[
          {
            type:'all',
            label:'全部'
          },{
            type:'critical',
            label:'严重'
          },{
            type:'important',
            label:'重要'
          },{
            type:'normal',
            label:'一般'
          }
        ],
        checkedType:{},

        alarmCodes:[],
        checkedAlarmCodes: {},

        detailPageData:{},

        //  记录原始的数据
        alarmRawData:[],
      };
    },
    methods: {
      // 四种类型选中触发的函数
      handleCheckTypeChange(val,alarmType){
        let checkedCodes=Object.values(this.checkedAlarmCodes).flat()
        this.alarmCodes.forEach(item => {
          item.data.forEach(i => {
            if(checkedCodes.indexOf(i.code) !== -1){
              i.sub=1
            }else{
              i.sub=0
            }
          })
        })
        // 选中状态时的操作
        if(val){
          if(alarmType.type==="all"){
            this.alarmCodes.forEach(item => {
              item.data.forEach(i => {
                i.sub=1
              })
            })
            this.checkedType={
              all:true,critical:true,important:true,normal:true,
            }
          }else{
            this.alarmCodes.forEach(item => {
              item.data.forEach(i => {
                i.level === alarmType.type ? i.sub=1 : ''
              })
            })
          }
        }
        else{  // 未选中状态时的操作
          if(alarmType.type==="all"){
            this.alarmCodes.forEach(item => {
              item.data.forEach(i => {
                i.sub=0
              })
            })
            this.checkedType={
              all:false,critical:false,important:false,normal:false,
            }
          }else{
            this.alarmCodes.forEach(item => {
              item.data.forEach(i => {
                i.level === alarmType.type ? i.sub=0 : ''
              })
            })
          }
        }
      },

      // KdCheckboxGroup回调选项变化函数
      handleCheckedAlarmCodesChange(title,value) {
        this.$set(this.checkedAlarmCodes,title,value)
      },

      getCheckedAlarmCodes(){
        // console.log(this.checkedAlarmCodes)
        return this.checkedAlarmCodes

      },
      configCancel(){

      },
      async init(){
        let alarmCodesList = await this.$api.monitor.getAlarmCodes()
        // console.log(alarmCodesList)
        // 记录最初的数据
        this.alarmRawData=alarmCodesList

        this.checkedType={
          all:false,critical:false,important:false,normal:false,
        }
        // this.checkedType={}
        // console.log(this.checkedType)
        // let listTerminal=alarmCodesList.filter(item => item.type==="terminal")
        // let listServer=alarmCodesList.filter(item => item.type==="server")
        // let listMcu=alarmCodesList.filter(item => item.type==="mcu")
        // let checkedCodes=alarmCodesList.filter(item => item.sub===1 )
        // console.log(alarmCodesList)
        // 若果不是订阅告警页面，则做其他默认选中处理
        if(!this.isSubSetting){
          this.checkboxProps={
            id: 'code',
            label: 'name',
            isChecked:'notification',
          };
          if(this.checkedCodes.length>0){
              // console.log(this.checkedCodes)
            alarmCodesList.filter((item)=> {
              if(this.checkedCodes.indexOf(item.code) > -1){
                item.notification=1
              }
            })
          }
        }
        if(this.isDetail){  //如果是告警通知详情页面如下处理
          let selectedCodes = alarmCodesList.filter((item)=> this.checkedCodes.indexOf(item.code) > -1)
          // this.detailPageData["MCU告警"]=selectedCodes.filter(item => item.type==="mcu")
          // this.detailPageData["服务器设备告警"]=selectedCodes.filter(item => item.type==="server")
          // this.detailPageData["终端设备告警"]=selectedCodes.filter(item => item.type==="terminal")

          // 记录告警类型
          this.$set(this.detailPageData,"MCU告警",selectedCodes.filter(item => item.type==="mcu"))
          this.$set(this.detailPageData,"服务器设备告警",selectedCodes.filter(item => item.type==="server"))
          this.$set(this.detailPageData,"终端设备告警",selectedCodes.filter(item => item.type==="terminal"))
        }

        let combinationAlarm=[
          {
            name:"MCU告警",
            type:"mcu",
            data:alarmCodesList.filter(item => item.type==="mcu")
          },{
            name:"服务器设备告警",
            type:"server",
            data:alarmCodesList.filter(item => item.type==="server")
          },{
            name:"终端设备告警",
            type:"terminal",
            data:alarmCodesList.filter(item => item.type==="terminal")
          },
        ]
        this.alarmCodes=combinationAlarm

        // console.log(this.alarmCodes.data)
      },
    },
    mounted(){
      this.init()
    },
  };
	
</script>
<style>
.alarmsub-block{
  margin-bottom: 19px;
}
.alarmsub-block--title{
  /*border-bottom: 1px #595757 solid;*/
  /*margin-bottom: 10px;*/
  height: 30px;
  background-color: #292e30;
  padding: 0px 20px 0px 24px;
  line-height: 30px;
  margin-bottom: 14px;
}
.alarmsub-block--content{
  display: inline-block;
  width: 50%;
  margin-bottom: 11px;
}
.alarmsub-block--content span{
  display: inline-block;

}
</style>
