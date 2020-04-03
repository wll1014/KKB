<template>
  <div style="width: 100%;height:100%;">
    <SelectDataRange @dataChange="dataChange"></SelectDataRange>
    <div style="width: 100%;height: 462px;margin-top: 10px;">
      <ChartExtendLargeModel ChartID="IDMemUtilization" :chartConf="activeChartConf" :extraPlugin="extraPlugin" extraPluginClass="area-chart-plugin--cpu"></ChartExtendLargeModel>
    </div>
  </div>
</template>

<script>
// import SelectDataRange from "@/components/monitor/SelectDataRange.vue"
export default {
  components: {
    SelectDataRange: ()=> import('@/components/monitor/SelectDataRange.vue'),
    ChartExtendLargeModel: ()=> import('@/components/monitor/ChartExtendLargeModel.vue'),
  },
  props:{
    host_moid:String,
  },
  data(){
    return{
      // new start

      // chart封装组件的传参
      activeChartConf:{
        name: "MEM",
        chartRenderMethod: "timeline",
        dataRenderMethon:"timeline",
        // dataKey:['data','info'],
        url: ['api','getSingleHostMemData'],
        urlParams:'nextReFresh',
        // url:"cpu",
        routerPush: '跳转cpu',
        timerInterver: 300,
        options: {
          isArea:true,
          // dataFormat:["percent"],
          echartsCustom:{
            grid: {
              left: 73,
              right: 58,
              bottom: 80,
              top:76,
              containLabel: false
            },
            legend:{
              top:32,
              right:162,
              textStyle:{
                color:'#9ca9b1',
                padding:[1,0,0,5],
                fontSize:14
              },
            },
            yAxis: {
              // name:'使用率%',
              nameTextStyle:{
                fontSize:12,
              },
              axisLabel:{
                fontSize:10,
                color:'#9ca9b1',
                margin:10,
                formatter: '{value}%'
              },
              axisLine: {
                lineStyle: {
                  color: '#5f656a'
                },
              },
              axisTick:{
                show:false,
              },
              splitLine: {
                lineStyle:{
                  color: ['#5f656a'],
                  type:'dotted'
                },
              },
            },
            tooltip: {
              formatter:  (params,) => {
                let time = this.$echarts.format.formatTime('yyyy-MM-dd', params[0].value[0])
                  + ' ' + this.$echarts.format.formatTime('hh:mm:ss', params[0].value[0]);
                let usedFormatter=[]
                let leftHtml='<div class="lchart-tootip-block__left">'
                let rightHtml='<div class="lchart-tootip-block__right">'

                for(let item of params){

                  let lstyle = 'style="background: ' + item.color + ';"'
                  let lhtmlContent = '<div class="lchart-tootip-content--block">' +
                    '<div class="lchart-tootip-content-legendicon"' + lstyle + '></div>' +
                    '<div class="lchart-tootip-content-left">'+ "使用率" + '</div>' +
                    '</div>'+'<div class="lchart-tootip-content--block">' +
                    '<div class="lchart-tootip-content-legendicon"' + lstyle + '></div>' +
                    '<div class="lchart-tootip-content-left">'+ "内存总大小" + '</div>' +
                    '</div>'
                  leftHtml+=lhtmlContent

                  let showValue= null
                  if(item.value[1]!==null && item.value[1]!==undefined) showValue = Math.round(item.value[1]*100)/100 + " %"
                  let totalMemSize = item.value[2] ? parseInt(item.value[2]/1073741824) + " GB" : item.value[2]
                  let rhtmlContent = '<div class="lchart-tootip-content--block">' +
                    '<div class="lchart-tootip-content-right">'+':&nbsp' + showValue + '</div>'+
                    '</div>' + '<div class="lchart-tootip-content--block">' +
                    '<div class="lchart-tootip-content-right">'+':&nbsp' + totalMemSize + '</div>'+
                    '</div>'
                  rightHtml+=rhtmlContent
                }

                leftHtml+='</div>'
                rightHtml+='</div>'

                usedFormatter=[leftHtml,rightHtml]
                // console.log(freeFormatter)
                let header='<div style="font-size: 16px;margin-bottom: 12px;">'+time+'</div>'
                let content=[...usedFormatter].join('\n')
                return header+content;
              }
            },
          },

        }
      },

      extraPlugin:{
        imgExport:true,
      },

    }
  },
  methods: {

    dataChange(val){
      if(!val){
        val=[undefined,undefined]
      }
      let params={
        moid:this.host_moid,
        start_time: val[0],
        end_time: val[1],
      }

      this.$nextTick(()=>this.$set(this.activeChartConf,'urlParams',params))
      // console.log("mem i am mounted",this.activeChartConf.urlParams)
    },

    async getMemData(){
      let params={
        moid:this.host_moid
      }
      this.$set(this.activeChartConf,'urlParams',params)
      // let backData = await this.$api.getChartData.getSingleHostMemData(params)
      //
      // console.log(backData)
    },
    init(){
      // this.getMemData()
    },
  },
  mounted(){
   this.init()

  },
 
  beforeDestroy () {

  },

}
</script>

<style>
  .area-chart-plugin--cpu{
    top:20px;
    right: 38px;
  }
</style>
