<template>
   <div>
     <div style="display: inline-block;">
      <el-select @change="selectDataChange" popper-class="theme-dark" v-model="timeRnageSelectedOptions" placeholder="请选择平台域" style="width: 120px;margin-right: 7px;">
        <el-option
        v-for="item in timeRnageList" :key="item[0]" :label="item[0]" :value="item[1]">
        </el-option>
      </el-select>
     </div>
     <div style="display: inline-block;vertical-align: 1px;">
      <el-date-picker
        style="width: 322px;margin-right: 7px;"
        v-model="datePickerTimeRange"
        type="datetimerange"
        start-placeholder="开始日期"
        end-placeholder="结束日期"
        popper-class="theme-dark"
        value-format="timestamp"
        @focus="recoderDatePicker(datePickerTimeRange)"
        @blur="judgeDatePickerChange(datePickerTimeRange)"
        format="yyyy-MM-dd HH:mm"
        range-separator=""
        class="clear-close-icon"
        prefix-icon="ops-icons-bg icon-calendar"
        :clearable=false
        >
      </el-date-picker>
     </div>
     <div style="display: inline-block;height: 26px;line-height: 26px;">
       <el-button @click="searchMonitor" >搜索</el-button>
     </div>
  </div>
</template>

<script>
export default {
  props:{
    // 加载组件第一次是否触发时间变化回调
    firstLoad:{
      type:Boolean,
      default:true,
    },
  },
  data() {
  	return {
      timer:null,
      theTimeRange:3600000,
      datePickerTimeRange:'',
      timeRnageSelectedOptions:'最近 1小时',
      timeRnageList:[["自定义","customer"],
                     ["最近 30分钟",1800000],
                     ["最近 1小时",3600000],
                     ["最近 5小时",18000000],
                     ["最近 一天",86400000],
                     ["最近 30天",2592000000],
                    ],
                    
      // 记录上一次时间的选择
      frontDatePickerTimeRange:null,
    };
  },
  methods: {
    dataChange(timeRange){
      this.$emit('dataChange',timeRange);
    },
    // 选择器函数
    selectDataChange(val){
      // console.log(val)
      this.theTimeRange=val
      if(val==="customer"){
        // this.clearTimer();
        this.datePickerTimeRange='';
      }else{
        let timestamp = (new Date()).getTime();
        // console.log(timestamp,timestamp-val)
        this.datePickerTimeRange=[timestamp-val,timestamp]
      }
      // this.getData(timestamp-3600000,timestamp)
    },
    // 搜索按钮
    searchMonitor(){
      if(this.theTimeRange==="customer"){
        this.clearTimer(); 
        this.dataChange(this.datePickerTimeRange)
      }else{
        this.dataChange(this.datePickerTimeRange)
        this.setTimer(this.theTimeRange)
      }
    },
    
    // 选中时间组件时判断时间是否有改变，若改变下拉框改为“自定义”
    recoderDatePicker(val){
      this.frontDatePickerTimeRange=val
    },
    judgeDatePickerChange(val){
      if(this.frontDatePickerTimeRange!==this.datePickerTimeRange){
        this.timeRnageSelectedOptions="自定义"
        this.theTimeRange="customer"
      }
    },
    
    // 定时器
    setTimer(range=3600000){ 
        this.clearTimer(); 
        this.timer = setInterval(() => {
          // console.log(range)
          let timestamp = (new Date()).getTime();
          // console.log(timestamp,timestamp-range)
          // this.datePickerTimeRange=[timestamp-range,timestamp]
          this.dataChange([timestamp-range,timestamp])
        },30000)
    },
    // 清楚定时器
    clearTimer(){
      clearInterval(this.timer);        
      this.timer = null;
    },
  },
  mounted() {
  	this.selectDataChange(3600000);
    this.setTimer(3600000);
    if(this.firstLoad){
      this.searchMonitor()
    }
  },
  beforeDestroy () {
   this.clearTimer()
  },
}
</script>

<style>
</style>
