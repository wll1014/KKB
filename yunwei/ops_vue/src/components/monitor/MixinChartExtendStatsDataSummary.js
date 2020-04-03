const extendStatsDataSummary = {
  methods: {
    async renderChartStatsDataSummary(defaultConf, chartConf, renderChartDataMethod, isNewChart) {
      let renderChartTypeMethod = {
        'equipmentUsage': this.renderChartTypeEquipmentUsage, // 设备使用率统计图表
      }
      await renderChartTypeMethod[chartConf.dataRenderMethon](defaultConf, chartConf, renderChartDataMethod, isNewChart)
    },
    // chart渲染start：设备使用率统计chart
    async renderChartTypeEquipmentUsage(defaultConf, chartConf, renderChartDataMethod, isNewChart) {
      let chartBaseOptionPie = {
        backgroundColor: defaultConf.echartsBackgroudColor,
        color: defaultConf.colorCustomer,
        grid: {
          left: '7%',
          right: '9%',
          bottom: 15,
          top: 45,
          containLabel: true
        },
        legend: {
          itemWidth: 10,
          itemHeight: 5,
          width: '70%',
          icon: 'roundRect',
          itemGap: 22,
          right: 53,
          // left:100,
          textStyle: {
            color: '#9ca9b1',
            padding: [1, 0, 0, 5]
          },
          top: 20,
        },
        tooltip: {
          trigger: 'item',
          padding: [18, 14],
          backgroundColor: '#141414',
          borderColor: '#383b3c',
          borderWidth: 1,
          textStyle: {
            color: '#9ca9b1',
          },
          formatter: '{b} : {d} %'
        },
        series: [{
          type: 'pie',
          name: '服务器设备统计',
          radius: chartConf.options.radius || '35%',
          center: chartConf.options.center || ['25%', '50%'],
          label: chartConf.options.label || {
            show: false,
          },
          labelLine: chartConf.options.labelLine || {show: false,}
        }, {
          type: 'pie',
          name: '终端设备统计',
          radius: chartConf.options.radius || '35%',
          center: chartConf.options.center || ['75%', '50%'],
          label: chartConf.options.label || {
            show: false,
          },
          labelLine: chartConf.options.labelLine || {show: false,}
        }]
      };

      if (isNewChart) {
        this.chartBaseInstance.setOption(chartBaseOptionPie, true)
      }
      // 用于后续增加的整体样式调整 options
      let optionsAppend = {}
      // 对于自定义项目的修改
      if (chartConf.options && chartConf.options.echartsCustom) {
        for (let key in chartConf.options.echartsCustom) {
          key ? optionsAppend[key] = chartConf.options.echartsCustom[key] : ''
        }
      }
      this.chartBaseInstance.setOption(optionsAppend)

      // end判断是否是新的一张表，若是，则重新渲染整张表，否，则只渲染数据
      let getData = await this.getApiData(defaultConf, chartConf)
      if (!getData) {
        return false
      }

      let devData = getData[0].data
      let mtData = getData[1].data
      let series = getData.map((item, index) => {
        // 对数据做处理后返回
        let total = item.data[0]
        let use = item.data[1]
        let free = parseInt(total - use)

        let data = [{
          name: '运行设备',
          value: use
        }, {
          name: '未运行设备',
          value: free
        }]

        return {
          data: data,
          name: item.description,
        }
      })

      let title = [{
        subtext: '服务器设备',
        left: '25%',
        top: '67%',
        textAlign: 'center'
      }, {
        subtext: '设备总数：' + (devData[0] || 0),
        left: '25%',
        top: '75%',
        textAlign: 'center'
      }, {
        subtext: '运行数量：' + (devData[1] || 0),
        left: '25%',
        top: '82%',
        textAlign: 'center'
      }, {
        subtext: '终端设备',
        left: '75%',
        top: '67%',
        textAlign: 'center'
      }, {
        subtext: '设备总数：' + (mtData[0] || 0),
        left: '75%',
        top: '75%',
        textAlign: 'center'
      }, {
        subtext: '运行数量：' + (mtData[1] || 0),
        left: '75%',
        top: '82%',
        textAlign: 'center'
      },]
      this.chartBaseInstance.setOption({
        title: title,
        series: series
      })
    },
    // chart渲染end：客户端统计统计chart

  }
};

export default extendStatsDataSummary;
