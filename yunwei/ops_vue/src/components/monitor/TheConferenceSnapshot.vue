<template>
    <div class="theme-dark">
      <!--<el-button @click="downloadSnapshots(19)">aaaaaaaa</el-button>-->
      <div v-if="snapshotsStatu" >
        <div style="width: 100%; ">
          <span v-if="snapshotsStatu === 'creating'" style="margin-left:60px">
            <span style="margin-right: 7px;font-size: 14px;">
            <i class="ops-icons-bg icon-notice" style="vertical-align: bottom;z-index: 1000"></i>
            </span>
            文件正在生成，请稍后......
          </span>
          <span v-if="snapshotsStatu === 'created'" style="margin-left:60px">
            <span style="margin-right: 7px;font-size: 14px;">
            <i class="ops-icons-bg icon-notice" style="vertical-align: bottom;z-index: 1000"></i>
            </span>
            文件生成完成，请下载文件！
          </span>
          <span v-if="snapshotsStatu === 'failed'" style="margin-left:30px">
            <span style="margin-right: 7px;font-size: 14px;">
            <i class="ops-icons-bg icon-notice" style="vertical-align: bottom;z-index: 1000"></i>
            </span>
            {{'文件生成失败' + errMsg}}
          </span>
        </div>
      </div>
      <div v-else>
        <el-date-picker
          style="width: 350px;"
          v-model="datePickerConferenceSnapshot"
          type="datetimerange"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          popper-class="theme-dark "
          value-format="timestamp"
          range-separator=""
          class="clear-close-icon"
          prefix-icon="ops-icons-bg icon-calendar"
          :clearable="false"
					@change="changeTime"
        >
        </el-date-picker>
      </div>
    </div>
</template>

<script>
export default {
  name: "TheConferenceSnapshot",
  props:{
    tiemRange:{
      type: Array,
      default: [],
    },
    // apiParams:null,
  },
  watch: {
    tiemRange(newVal) {
      // console.log(newVal,this.chartConf)
      this.init()
    },
    // apiParams:{
    //   deep:true,
    //   handler:function(newVal,oldVal){
    //     // console.log("ChartExtend-Watch:" + newVal.name)
    //     this.init()
    //   }
    // },
  },
  data() {
    return {
      datePickerConferenceSnapshot:[],

      // 定时器实例
      timer:null,
      // 快照状态
      snapshotsStatu:null,
      snapsshotsID:null,

      loop:false,

      errMsg:'', // 生成文件失败是的提示
  }},
  methods: {
		// yp__start
		changeTime(){
			// console.log(this.datePickerConferenceSnapshot)
			if(this.datePickerConferenceSnapshot){
				if(this.datePickerConferenceSnapshot[0]<this.tiemRange[0]||this.datePickerConferenceSnapshot[1]>this.tiemRange[1]){
					this.$message('请选择会议范围内的时间')
					this.datePickerConferenceSnapshot = this.tiemRange
				}
			}else{
				this.$message('请选择会议范围内的时间')
				this.datePickerConferenceSnapshot = this.tiemRange
			}
		},
		// yp__end
    createSnapshots(params){
      let p={
        start_time:this.datePickerConferenceSnapshot[0],
        end_time:this.datePickerConferenceSnapshot[1],
      }
      // p={...params,...p}
      Object.assign(params, p);
      this.snapsshotsID=null
      this.$api.monitor.postCreateSnapshots(params)
        .then(res => {
          let d = res.data
          if(d.data){
            this.snapshotsStatuSetting('creating')
            this.snapsshotsID=d.data.task_id
            this.setTimer(2,this.snapsshotsID)
          }else{
            this.snapshotsStatuSetting('failed')
            this.errMsg = ' , ' + d.msg
          }
        })
        .catch(err => {
          this.snapshotsStatuSetting('failed')
          this.$notify({
            message: '创建快照失败',
            duration: 6000
          })
        })
    },

    getSnapshotsStatus(id){
      this.loop=true  //查询状态中
      this.$api.monitor.getSnapshotsStatus(id)
        .then(res => {
          let d = res.data
          if(d.success){
            if(d.data && d.data.is_complete === 1){ // 完成打包
              // this.downloadSnapshots()
              this.snapshotsStatuSetting('created')
              this.clearTimer()
            }else {
              this.loop=false  //查询结束,可以开始下次查询
            }
          }else{
            this.snapshotsStatuSetting('failed')
            this.clearTimer()
          }
        })
        .catch(err => {
          this.snapshotsStatuSetting('failed')
          this.clearTimer()
          this.$notify({
            type:"error",
            message:err
          })
        });
    },

    downloadSnapshots(){
      // console.log(params)
      let id = this.snapsshotsID
      const elink = document.createElement('a')
      // elink.download = "0512110000602.tar.gz"
      elink.style.display = 'none'
      elink.href = `/api/v1/ops/diagnose/download/?task_id=${id}`
      // elink.href = "/api/v1/ops/media/snapshot/0512110000602.tar.gz"
      document.body.appendChild(elink)
      elink.click()
      URL.revokeObjectURL(elink.href) // 释放URL 对象
      document.body.removeChild(elink)
    },

    // 定时器函数start
    // 设置定时器
    setTimer(interver=60,id){
      this.clearTimer();
      this.timer = setInterval(() => {
        // console.log(id)
        if(!this.loop){
          this.getSnapshotsStatus(id)
        }
      },interver*1000)
    },
    // 清除定时器
    clearTimer(){
      clearInterval(this.timer);
      this.timer = null;
    },
    // 定时器函数end

    snapshotsStatuSetting(val){
      this.snapshotsStatu = val

      this.$emit('snapshotsStatu', this.snapshotsStatu);
    },

    init(){
      this.datePickerConferenceSnapshot=this.tiemRange
      // this.snapshotsStatu=null
      // this.snapshotsStatuSetting(null)
    }
  },
  mounted(){
    this.init()
  },
  beforeDestroy () {
    // console.log("beforeDestroy")
    this.snapshotsStatu=null
    this.errMsg = ''
    this.clearTimer()
  },
}
</script>

<style scoped>

</style>
