<template>
    <div class="theme-dark">
      <div :class="ExpressionClass">
        <span>Crontab表达式：</span>
        <span style="width: 540px;max-height:26px;overflow:auto;display: inline-block;white-space: pre-line;overflow-wrap: break-word;vertical-align: bottom;">{{fullRules}}</span>
      </div>
      <KdTabCommon :tab-list="tabList" :active-tab="activeTab" class-name="" @tab-change="tabChange" :width=18></KdTabCommon>

      <div style="margin-top: 29px;" v-show="activeTab!=='devList'">
        <div class="timing__radio-block">
          <div style="margin-bottom: 18px;">
            <el-radio v-model="selectMode" :label=1>循环</el-radio>
            <span style="margin-right: 10px;">每隔</span>
            <el-input style="width: 50px;margin-right:10px;" v-model="inputLoopTime" @input="inputChangeLimit(inputLoopTime)" :disabled="selectMode!==1"></el-input>
            <span style="margin-right: 10px;">{{loopShowContent[activeTab]}}</span>
            <span style="">执行一次</span>
          </div>
          <div style="margin-bottom: 14px;">
            <el-radio v-model="selectMode" :label=2>指定</el-radio>
          </div>
        </div>
        <div class="timing__checkbox-group-block">
          <div v-show="activeTab === 'eachMinute'">
            <el-checkbox-group v-model="checkboxSelect" >
              <el-checkbox :label="i-1" v-for="i in 60" :key="i" :disabled="selectMode!==2">{{i-1}}</el-checkbox>
            </el-checkbox-group>
          </div>
          <div v-show="activeTab === 'eachHour'">
            <el-checkbox-group v-model="checkboxSelect">
              <el-checkbox :label="i-1" v-for="i in 24" :key="i" :disabled="selectMode!==2">{{i-1}}</el-checkbox>
            </el-checkbox-group>
          </div>
          <div v-show="activeTab === 'eachDay'">
            <el-checkbox-group v-model="checkboxSelect">
              <el-checkbox :label="i" v-for="i in 31" :key="i" :disabled="selectMode!==2"></el-checkbox>
              <el-checkbox label="L" >每月最后一天</el-checkbox>
            </el-checkbox-group>
          </div>
          <div v-show="activeTab === 'eachMounth'">
            <el-checkbox-group v-model="checkboxSelect">
              <el-checkbox :label="i" v-for="i in 12" :key="i" :disabled="selectMode!==2"></el-checkbox>
            </el-checkbox-group>
          </div>
          <div v-show="activeTab === 'eachWeek'">
            <el-checkbox-group v-model="checkboxSelect">
              <el-checkbox :label="i.value" v-for="i in checkboxWeek" :key="i.value" :disabled="selectMode!==2">{{i.label}}</el-checkbox>
            </el-checkbox-group>
          </div>
        </div>
      </div>

      <div style="margin-top: 29px;" v-if="activeTab==='devList'">
        <TheTableDevAddFromOrganization @data-change="addFromOrganizationDevChange"
                                        :devList="devList"
                                        :customParams="{device_type:0}"
                                        :tableHeight=270></TheTableDevAddFromOrganization>
      </div>
      <!--<el-button @click="getRules">aaa</el-button>-->
    </div>
</template>

<script>
export default {
  name: "CrontabTiming",
  components:{
    KdTabCommon: () => import('@/components/common/KdTabCommon.vue'),
    TheTableDevAddFromOrganization: () => import('@/components/hostmanage/TheTableDevAddFromOrganization.vue'),
  },
  props:{
    initRules:{
      type: Object,
      default: null,
    },
    devList:{
      type: Array,
      default: null,
    },
    ExpressionClass:{
      type: String,
      default: 'default-expression-class',
    },
  },
  data() {
    return {
      selectMode:1,  //定时类型： 1：循环执行，2：指定时间执行
      inputLoopTime:0,

      // lastTab:'eachMinute',
      activeTab:'eachMinute',

      tabList:[
        ['eachMinute','每分钟'],
        ['eachHour','每小时'],
        ['eachDay','每天'],
        ['eachMounth','每月'],
        ['eachWeek','每周'],
        ['devList','服务器列表'],],

      objRulesKey:{
        eachMinute:'minute',
        eachHour:'hour',
        eachDay:'day',
        eachWeek:'weekday',
        eachMounth:'month',
      },

      limitLength:{
        eachMinute:60,
        eachHour:24,
        eachDay:32,
        eachWeek:7,
        eachMounth:13,
      },

      checkboxSelect:[],
      checkboxWeek:[
        {
          label:'周一',
          value:1,
        },{
          label:'周二',
          value:2,
        },{
          label:'周三',
          value:3,
        },{
          label:'周四',
          value:4,
        },{
          label:'周五',
          value:5,
        },{
          label:'周六',
          value:6,
        },{
          label:'周日',
          value:0,
        },

      ],


      loopShowContent:{
        eachMinute:'分钟',
        eachHour:'小时',
        eachDay:'天',
        eachWeek:'周',
        eachMounth:'月',
      },


      fullRules:'',
      rules:{  //type定时类型： 1：循环执行，2：指定时间执行
        minute:{
          type:1,
          rule:[],
          rule_str:"*",
        },
        hour:{
          type:1,
          rule:[],
          rule_str:"*",
        },
        day:{
          type:1,
          rule:[],
          rule_str:"*",
        },
        weekday:{
          type:1,
          rule:[],
          rule_str:"*",
        },
        month:{
          type:1,
          rule:[],
          rule_str:"*",
        },
      },

      devList:[],
    };
  },

  computed:{
    rulesChange(){
      let objRules = {
        type:this.selectMode,
        loop:this.inputLoopTime,
        select:this.checkboxSelect,
      }
      return objRules
    },
  },
  watch: {
    rulesChange:{
      deep:true,
      handler:function(newRules,oldVal){

        let deepCopy = null
        let key = this.objRulesKey[this.activeTab]
        // let mode = this.selectMode
        if(newRules.type === 1){
          deepCopy = [newRules.loop]
        }else{
          deepCopy = [...newRules.select]
        }

        this.$set(this.rules[key],'type',newRules.type)
        this.$set(this.rules[key],'rule',deepCopy)
        this.transCrontabRules(this.rules)
      },
    },
  },

  methods: {
    // 获取当前规则
    getRules(){
      // for(let i in this.rules){
      //   console.log(i,this.rules[i].type,this.rules[i].rule,this.rules[i].rule_str)
      // }

      let cb = {}
      cb["cron_rule"]=this.rules
      cb["machines"] = this.devList
      return cb
    },

    // tab页变化函数
    tabChange(val){
      // console.log(val)
      if(val !== 'devList'){
        this.inputLoopTime=0
        this.checkboxSelect=[]

        let key = this.objRulesKey[val]
        if(this.rules[key] && this.rules[key].rule.length>0){
          this.selectMode = this.rules[key].type
          if(this.rules[key].type === 1){
            this.inputLoopTime=this.rules[key].rule[0]
          }else{
            this.checkboxSelect=[...this.rules[key].rule]
          }
        }

      };

      this.activeTab=val
    },

    addFromOrganizationDevChange(val){
      this.devList=val
    },

    inputChangeLimit(val){
      val = val.replace(/(^\s*)|(\s*$)/g, "")
      if(!val) {
        this.inputLoopTime = "0";
        return
      }
      let reg = /[^\d]/g

      // 只能是数字和小数点，不能是其他输入
      val = val.replace(reg, "")
      val ? val=parseInt(val) : val="0"
      parseInt(val)>this.limitLength[this.activeTab] ? val=this.limitLength[this.activeTab]-1 :val

      this.inputLoopTime = val;
    },

    // crontab规则生成
    transCrontabRules(cornRule){

      for(let key in cornRule){
        if(key === 'special'){
            continue
        }else{
          let ruleStr=null
          if(cornRule[key].type === 1){
            cornRule[key].rule[0] && cornRule[key].rule[0]!=="0" ? ruleStr="*/" + cornRule[key].rule[0] : ruleStr="*"
            this.$set(cornRule[key],'rule_str',ruleStr)
          }else {
            cornRule[key].rule.length > 0 ? ruleStr=cornRule[key].rule.join(',') : ruleStr="*"
            this.$set(cornRule[key],'rule_str',ruleStr)
          }
        };
      };

      let fullRulesList=[cornRule.minute.rule_str,
                  cornRule.hour.rule_str,
                  cornRule.day.rule_str,
                  cornRule.month.rule_str,
                  cornRule.weekday.rule_str]

      this.fullRules=fullRulesList.join(' ')
    },

    init(){
      if(this.initRules){
        for(let k in this.initRules){
          this.$set(this.rules,k,this.initRules[k])
        }
        this.tabChange('eachMinute')
      }
      this.transCrontabRules(this.rules)
    },
  },
  mounted() {
    this.init()
  }
}
</script>

<style>
.timing__checkbox-group-block{
  padding-left: 81px;
}
.timing__checkbox-group-block .el-checkbox{
  width: 72px;
  margin-bottom: 9px;
}
.timing__radio-block .el-radio{
  margin-right: 26px;
}
.default-expression-class{
  margin-bottom:20px;
  font-size: 12px;
}
</style>
