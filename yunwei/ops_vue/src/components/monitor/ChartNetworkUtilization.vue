<template>
  <div style="width: 100%;height:100%;">
  <SelectDataRange @dataChange="dataChange" :firstLoad=false></SelectDataRange>
  <div class="area-cores" style="width: 100%;margin-top:10px;height: 300px;" v-for="item in networkCardList">
    <ChartExtendLargeModel :ChartID="item.chartID" :chartConf="item" :extraPlugin="extraPlugin" extraPluginClass="area-chart-plugin--cpu"></ChartExtendLargeModel>
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
    let echartsTimeFormat = this.$echarts.format.formatTime;
    return{

      // new start

      // chart封装组件的传参
      baseChartConf:{
        name: "Network",
        chartRenderMethod: "timeline",
        dataRenderMethon:"timeline",
        // dataKey:['data','info'],
        url: ['api','getSingleHostNetworkCardData'],
        urlParams:'nextReFresh',
        // url:"cpu",
        routerPush: '跳转cpu',
        timerInterver: 300,
        options: {
          isArea:true,
          title:{},
          echartsCustom: {
            legend:{
              top:32,
              right:162,
              textStyle:{
                color:'#9ca9b1',
                padding:[1,0,0,5],
                fontSize:14
              },
            },
            grid: {
              left: 73,
              right: 58,
              bottom: 80,
              top:76,
              containLabel: false
            },
            yAxis:{
              name:"MB/s",
              nameTextStyle:{
                color:'#9ca9b1',
                fontSize:12,
              }
            },
            tooltip:{
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
                    '<div class="lchart-tootip-content-left">'+item.seriesName + '</div>' +
                    '</div>'
                  // usedFormatter.push(item.seriesName + ': ' + showValue)
                  leftHtml+=lhtmlContent

                  let showValue= null
                  if(item.value[1]!==null && item.value[1]!==undefined) showValue = item.value[1].toFixed(2) + " MB/s"
                  let rhtmlContent = '<div class="lchart-tootip-content--block">' +
                    '<div class="lchart-tootip-content-right">'+':&nbsp' + showValue + '</div>'+
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

      networkCardList:[],

      // new end


    }
  },
  methods: {

    
    // 日期变化
    dataChange(val){
      if(!val){
        val=[undefined,undefined]
      }
      let params={
        moid:this.host_moid,
        start_time: val[0],
        end_time: val[1],
      }

      this.networkCardList.forEach(item => {
        let cardParams = {...params}
        cardParams.card=item.cardID
        this.$set(item,'urlParams',cardParams)
      })
    },
    async getNetworkData(){
      let res = await this.$api.getChartData.getNetworkCards(this.host_moid)
      let cardList = res.cards


      for(let card of cardList){
        let chartConf = {...this.baseChartConf}
        this.$set(chartConf,'chartID','netWork'+card)

        this.$set(chartConf,'cardID',card)

        let options = {...this.baseChartConf.options}
        options.title={
          text:card,
          top:17,
          left:14,
          textStyle:{
            color:'#9ca9b1',
            fontSize:14,
          },
        }
        this.$set(chartConf,'options',options)
        this.networkCardList.push(chartConf)
      }
      let defaultTimeRange=[(new Date()).getTime()-3600000,(new Date()).getTime()]
      this.dataChange(defaultTimeRange)
    },

    init(){
      this.getNetworkData()
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
