<template>
  <div style="width: 100%;height:100%;">
    <SelectDataRange @dataChange="dataChange" style="display: inline-block;"></SelectDataRange>

    <div style="display: inline-block;float: right;">
      <el-button @click="exportTopN">导出</el-button>
    </div>
    <div class="area-topn">
      <div style="">
        <el-row :gutter="18">
          <el-col  :span="12">
            <el-table ref="hostinfoMultipleTable" tooltip-effect="dark"
                      stripe
                      border
                      style="width: 100%;"
                      :data="tableDataCpu"
            >
              <el-table-column show-overflow-tooltip prop="name" label="应用名称  (CPU使用率TOP)" >
              </el-table-column>

              <el-table-column show-overflow-tooltip prop="value" label="CPU占用率" width="128">
              </el-table-column>
            </el-table>
          </el-col>
          <el-col  :span="12">
            <el-table ref="hostinfoMultipleTable" tooltip-effect="dark"
                      stripe
                      border
                      style="width: 100%;"
                      :data="tableDataMem"
            >
              <el-table-column show-overflow-tooltip prop="name" label="应用名称  (MEM使用率TOP)" >
              </el-table-column>

              <el-table-column show-overflow-tooltip prop="value" label="MEM占用率" width="128">
              </el-table-column>
            </el-table>
          </el-col>
        </el-row>
      </div>
    </div>
  </div>
</template>

<script>
	export default {
  components: {
    SelectDataRange: ()=> import('@/components/monitor/SelectDataRange.vue'),
  },
  props:{
    host_moid:String,
  },
	data(){
		return{
      tableDataCpu:[],
      tableDataMem:[],
      timeRange:[]
		}
	},
	methods: {
    exportTopN(){
      let params = {
        start_time:this.timeRange[0],
        end_time:this.timeRange[1]
      }
      this.$api.hostManageApi.exportTopN(this.host_moid,10,params)
        .then(res=>{
          // console.log(res)
          const content = res.data
          const blob = new Blob([content])
          const fileName = res.headers["content-disposition"].split("filename=")[1]
          if ('download' in document.createElement('a')) { // 非IE下载
            const elink = document.createElement('a')
            elink.download = fileName
            elink.style.display = 'none'
            elink.href = URL.createObjectURL(blob)
            document.body.appendChild(elink)
            elink.click()
            URL.revokeObjectURL(elink.href) // 释放URL 对象
            document.body.removeChild(elink)
          } else { // IE10+下载
            navigator.msSaveBlob(blob, fileName)
          }
        })
    },

    dataChange(val){
      if(!val){
        val=[undefined,undefined]
      }
      this.timeRange=val
      let params = {
        start_time:val[0],
        end_time:val[1]
      }
      this.getData(10,params)
    },

    getData(topn,params){
        this.getCpuData(topn,params)
        this.getMemData(topn,params)
    },

    async getCpuData(topn,params){
      let dataCpu = await this.$api.monitor.getProcessTopNCpu(this.host_moid,topn,params)
      this.tableDataCpu=dataCpu
    },
    async getMemData(topn,params){
      let dataMem = await this.$api.monitor.getProcessTopNMem(this.host_moid,topn,params)
      this.tableDataMem=dataMem
    },
    // 定时器
    setTimer(){
      const timer = setInterval(()=>{
        this.getData()
      },10000)
      this.$once('hook:beforeDestroy',()=>{
        clearInterval(timer)
      })
    },

    init(){
      this.getData()
    },
	},
	mounted(){
    // this.getData()
    // this.setTimer()
	},
}  
</script>

<style>
.area-topn{
  width: 100%;
  height: 515px;
  background: #1e2224;
  margin-top: 40px;
}
/*.table-topn{*/
  /*border: 1px solid #4f4f4f;*/
/*}*/
/*.table-info{*/
  /*width: 100%;*/
  /*line-height: 40px;*/
  /*font-size: 18px;*/
  /*color: #fff;*/
/*}*/
/*.table-info th{*/
  /*font-size: 16px;*/
  /*color: #aaaaaa;*/
/*}*/
/*.table-info tr,.table-info td,.table-info th{*/
  /*border: 1px dashed #444444;*/
/*}*/
</style>
