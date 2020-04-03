const extendReporterDay = {
  methods: {
    async renderChartAppRequestInit(defaultConf, chartConf, renderChartDataMethod, isNewChart) {
      let renderChartTypeMethod = {
        'appRequestWebEngine': this.renderChartTypeAppRequestWebEngine, //客户端统计图表
      }
      await renderChartTypeMethod[chartConf.dataRenderMethon](defaultConf, chartConf, renderChartDataMethod, isNewChart)
    },
    // chart渲染start：客户端统计统计chart
    async renderChartTypeAppRequestWebEngine(defaultConf, chartConf, renderChartDataMethod, isNewChart) {
      let chartBaseOptionPie = {
        backgroundColor: defaultConf.echartsBackgroudColor,
        color:defaultConf.colorCustomer,
        grid: {
          left: '7%',
          right: '9%',
          bottom: 15,
          top:45,
          containLabel: true
        },
        tooltip: {
          trigger: 'item',
          padding: [18,14],
          backgroundColor:'#141414',
          borderColor:'#383b3c',
          borderWidth:1,
          textStyle:{
            color:'#9ca9b1',
          },
          formatter: '{b} : {d} %'
        },
        series: {
          type:'pie',
          name:chartConf.name,
          // selectedMode:'single',
          minAngle:10,
          radius:chartConf.options.radius || '55%',
          center:chartConf.options.center || ['50%', '20%'],
          label:chartConf.options.label||{
            color:'#9ca9b1',
            formatter:'{b}： {d} %'
          },
          labelLine:chartConf.options.labelLine || {lineStyle:{width:2}}
        }
      };

      if(isNewChart){
        this.chartBaseInstance.setOption(chartBaseOptionPie,true)
        this.chartBaseInstance.on('pieselectchanged' ,(params) => {
          // console.log(params)
        })
      }
      // 用于后续增加的整体样式调整 options
      let optionsAppend={}
      // 对于自定义项目的修改
      if(chartConf.options && chartConf.options.echartsCustom){
        for(let key in chartConf.options.echartsCustom){
          key ? optionsAppend[key]=chartConf.options.echartsCustom[key] : ''
        }
      }
      this.chartBaseInstance.setOption(optionsAppend)

      // end判断是否是新的一张表，若是，则重新渲染整张表，否，则只渲染数据
      let getData = await this.getApiData(defaultConf, chartConf)
      if (!getData) {
        return false
      }

      let seriesData = getData.map((item,index)=>{
        // 对有数据处理的数据做处理后返回
        if(item.data === 0) return null
        let dataFront={
          value:item.data,
          name:item.description,
          itemStyle:{
            color:defaultConf.colorCustomer[index],
          }
        };
        return dataFront
      }).filter(i=>i)

      if(!seriesData || !seriesData.length) this.showDialog = true

      this.chartBaseInstance.setOption({
        series:{data:seriesData}
      })
    },
    // chart渲染end：客户端统计统计chart

  }
};

export default extendReporterDay;
