<template>
    <div>
      <div style="font-size: 14px;">一键抓包</div>
      <div style="margin-top: 40px;">
        <span style="font-size: 12px;display: inline-block;width: 78px;">抓包对象</span>
        <el-input style="width: 220px;margin-right: 7px;" v-model="_inputIDConf" placeholder="请输入会议号" maxlength="7" clearable></el-input>
        <el-input style="width: 240px;margin-right: 7px;" v-model="_inputIDMt" placeholder="请输入终端E164号" maxlength="13" clearable></el-input>
        <el-button @click="clickAudoTcpdump" :disabled="inputIDConf.length === 0 || inputIDMt.length === 0">一键抓包</el-button>
      </div>
      <!--蒙版区域start-->
      <el-dialog
        title="提示"
        :visible.sync="dialogVisibleTask"
        width="400px"
        append-to-body
        custom-class="theme-dark"
        @closed="closeDialog"
        :close-on-click-modal=false
      >
        <div style="width: 100%;text-align: center;margin-top: 15px;">
          <span style="margin-right: 7px;font-size: 14px;">
            <i class="ops-icons-bg icon-notice" style="vertical-align: bottom;"></i>
          </span>
          <span>{{taskComplete === 1 ? '文件生成完成，请下载抓包文件':'文件生成中，请稍后'}}</span>
          <span class="ani_dot" style="margin-right: 7px;font-size: 14px;" v-if="taskComplete !== 1">
            ...
          </span>
        </div>
        <div style="padding: 30px;text-align: center;box-sizing: border-box;">
          <span style="text-align: center;" >
            <el-button @click="closeDialog" v-if="taskComplete !== 1">取 消</el-button>
            <el-button @click="downloadTcpdumpFile" v-if="taskComplete === 1">下载抓包文件</el-button>
          </span>
        </div>
      </el-dialog>
      <!--蒙版区域end-->
    </div>
</template>

<script>
export default {
  name: "IntelligentWiresharkAutoTcpdump",
  data() {
    return {
      inputIDConf:'',
      inputIDMt:'',
      taskID:null,
      taskComplete:null,

      // 蒙版数据
      dialogVisibleTask:false,
    }
  },
  computed: {
    _inputIDConf: {
      set: function(value) {
        this.inputIDConf = value;
      },
      get: function() {
        return this.inputIDConf.replace(/[^0-9]+/g,'')
      }
    },
    _inputIDMt: {
      set: function (value) {
        this.inputIDMt = value;
      },
      get: function () {
        return this.inputIDMt.replace(/[^0-9]+/g, '')
      }
    }
  },
  methods:{
    async clickAudoTcpdump(){
      let checkRes = this.checkIdIsLegal(this.inputIdConf,this.inputIdMt)
      if (checkRes){
        let params = {
          conf_e164:this.inputIDConf,
          mt_e164:this.inputIDMt,
        }
        // console.log(params)
        let res = await this.$api.intelligentWireshark.createAutoTcpdumpTask(params)

        if(res.data.success){
          this.taskID = res.data.data.task_id
          this.dialogVisibleTask = true
          this.getAutoTcpdumpTaskInfo(this.taskID)
        }else{
          this.$message.error('抓包失败,' +  res.data.msg)
        }
      }else{
        this.$message.error('输入格式不合法')
      }
    },

    async getAutoTcpdumpTaskInfo(id){
      if(!this.taskID) return false //如果当前任务取消，这不继续获取
      let res = await this.$api.intelligentWireshark.getAutoTcpdumpTaskInfo(id)
      if(res.success){
        if(res.data.is_complete === 1){
          this.taskComplete = 1
          return 1
        }else if(res.data.is_complete === 2){  //可能不用次参数了，后续确认后可去掉
          this.closeDialog()
          return 2
        }else{
          setTimeout(()=>{this.getAutoTcpdumpTaskInfo(id)},2000)
        }
      }else{
        this.closeDialog()
        this.$message.error('抓包失败,' +  res.msg)
        return 2
      }
    },

    closeDialog(){
      this.dialogVisibleTask=false
      this.taskID=null
      this.taskComplete=null
    },

    downloadTcpdumpFile(){
      // console.log(params)
      let id = this.taskID
      const elink = document.createElement('a')
      // elink.download = "0512110000602.tar.gz"
      elink.style.display = 'none'
      elink.href = `/api/v1/ops/diagnose/download/?type=mtinfo&task_id=${id}`
      // elink.href = "/api/v1/ops/media/snapshot/0512110000602.tar.gz"
      document.body.appendChild(elink)
      elink.click()
      URL.revokeObjectURL(elink.href) // 释放URL 对象
      document.body.removeChild(elink)

      this.closeDialog()
    },

    // 其他功能函数
    checkIdIsLegal(confID,mtID){
      return true
    },

  }
}
</script>

<style scoped>
  .ani_dot {
    font-family: simsun;
  }
  :root .ani_dot { /* 这里使用Hack是因为IE6~IE8浏览器下， vertical-align解析不规范，值为bottom或其他会改变按钮的实际高度*/
    display: inline-block;
    width: 1.5em;
    vertical-align: bottom;
    overflow: hidden;
  }
  @-webkit-keyframes dot {
    0% { width: 0; margin-right: 1.5em; }
    33% { width: .5em; margin-right: 1em; }
    66% { width: 1em; margin-right: .5em; }
    100% { width: 1.5em; margin-right: 0;}
  }
  .ani_dot {
    -webkit-animation: dot 2s infinite step-start;
  }

  @keyframes dot {
    0% { width: 0; margin-right: 1.5em; }
    33% { width: .5em; margin-right: 1em; }
    66% { width: 1em; margin-right: .5em; }
    100% { width: 1.5em; margin-right: 0;}
  }
  .ani_dot {
    animation: dot 2s infinite step-start;
  }
</style>
