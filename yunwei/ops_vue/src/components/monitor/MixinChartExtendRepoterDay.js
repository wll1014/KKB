const extendReporterDay = {
  methods: {
    async renderChartDayReportInit(defaultConf,chartConf,renderChartDataMethod,isNewChart){
      let renderChartTypeMethod = {
        'reportDayServerDev':this.renderChartTypeReportDayServerDev, //平台概况图表
        'reportDayEnablePercent':this.renderChartTypeReportDayEnablePercent, //企业或者终端启用停用占比图表
        'reportDayAlarmStatistics':this.renderChartTypeReportDayAlarmStatistics, //告警统计图表
        'reportDayConfQuality':this.renderChartTypereportDayConfQuality, //会议质量图表
        'reportDayConfTime':this.renderChartTypereportDayConfTime, //会议时长图表
      }
      await renderChartTypeMethod[chartConf.dataRenderMethon](defaultConf,chartConf,renderChartDataMethod,isNewChart)
    },
    // chart渲染start：平台概况服务器统计chart
    async renderChartTypeReportDayServerDev(defaultConf,chartConf,renderChartDataMethod,isNewChart){

      // end判断是否是新的一张表，若是，则重新渲染整张表，否，则只渲染数据
      let getData=await this.getApiData(defaultConf,chartConf)
      if(!getData){
        return false
      }
      let reportData = getData.report_data
      let seriseData = []
      let total = 0
      if(Object.keys(reportData).length > 0){
        Object.keys(reportData).forEach((key,index)=>{
          let tempD = {}
          tempD.name = key
          tempD.value = reportData[key]
          // let colorLG = new this.$echarts.graphic.LinearGradient(
          //   0, 0, 0, 1,
          //   [
          //     {offset: 0, color: defaultConf.colorCustomer[index]},
          //     {offset: 1, color: 'transparent'}
          //   ])
          tempD.itemStyle = {
            color:defaultConf.colorCustomer[index],
          }
          total+=reportData[key]
          seriseData.push(tempD)
        });
      };

      if(total == 0){
        this.showDialog = true
        return false
      }
      let titleText = chartConf.options.titleText ? chartConf.options.titleText : "总数"
      let titleSubtext = chartConf.options.titleSubtext ? chartConf.options.titleSubtext : " 个"
      let seriseLabel = {
        formatter: function(params, ticket, callback) {
          return '{grey|' + params.name + '}{grey| ：' + params.value + ' 个}';
        },
        rich: {
          grey: {
            color: "#9ca9b1",
            fontSize: 14,
            padding: [4, 0],
            align: 'center',
            height:18,
          },
        },
      };
      if(chartConf.options.seriseLabel) seriseLabel = chartConf.options.seriseLabel

      // 日报服务器统计chart options
      let chartOpitons={
        backgroundColor: defaultConf.echartsBackgroudColor,
        grid: {
          left: 113,
          right: 0,
          top:80,
          containLabel: true
        },
        title: [{
          text: titleText,
          subtext: total + titleSubtext,
          textStyle: {
            color: '#9ca9b1',
            fontSize: 16,
            align: 'center',
            fontWeight:'normal'
          },
          subtextStyle: {
            fontSize: 18,
            color: ['#ff9d19']
          },
          x: 'center',
          y: '45%',
        }],
        legend: {
          // orient 设置布局方式，默认水平布局，可选值：'horizontal'（水平） | 'vertical'（垂直）
          orient: 'vertical',
          left:0,
          // y 设置垂直安放位置，默认全图顶端，可选值：'top' | 'bottom' | 'center' | {number}（y坐标，单位px）
          y: 'center',
          itemWidth: 3,   // 设置图例图形的宽
          itemHeight: 25,  // 设置图例图形的高
          itemGap: 8,
          textStyle: {
            color: '#9ca9b1',  // 图例文字颜色
            padding:[0,4],
          },
          // itemGap设置各个item之间的间隔，单位px，默认为10，横向布局时为水平间隔，纵向布局时为纵向间隔
        },

        series: [{
          name: chartConf.name,
          type: 'pie',
          minAngle:10,
          itemStyle: {
            normal: {
              borderWidth: 5,
              borderColor: "#232629"
            }
          },
          radius: ['54%', '60%'],
          center: ['50%', '50%'],
          hoverAnimation: false,
          silent:true,
          color: ['#c487ee', '#deb140', '#49dff0', '#034079', '#6f81da', '#00ffb4'],
          label: seriseLabel,
          labelLine: {
            normal: {
              length: 20,
              length2: 10,
              lineStyle: {
                color: '#4796c4'
              }
            }
          },
          data: seriseData
        }]
      }

      // 用于后续增加的整体样式调整 options
      let optionsAppend={}

      // start判断是否是新的一张表，若是，则重新渲染整张表，否，则只渲染数据
      // if(isNewChart){
        this.chartBaseInstance.setOption(chartOpitons,true)
      // }

    },
    // chart渲染end：平台概况服务器统计chart

    // chart渲染start：企业或者终端启用停用占比统计chart
    async renderChartTypeReportDayEnablePercent(defaultConf,chartConf,renderChartDataMethod,isNewChart){
      this.chartBaseInstance.clear() //此步骤防止前一个图表对后一个图的渲染造成渲染位置混乱
      // end判断是否是新的一张表，若是，则重新渲染整张表，否，则只渲染数据
      let getData=await this.getApiData(defaultConf,chartConf)

      if(!getData){
        return false
      }
      let reportData = getData.report_data
      let enableKey = chartConf.customParams.enable.key
      let disableKey = chartConf.customParams.disable.key
      let enableNum = reportData.info.find(i => i.name === enableKey)
      let disableNum = reportData.info.find(i => i.name === disableKey)
      let enablePer = (enableNum.data/(enableNum.data+disableNum.data) * 100).toFixed(0)
      let disablePer = (disableNum.data/(enableNum.data+disableNum.data) * 100).toFixed(0)
      let lengendData = {}
      lengendData[chartConf.customParams.enable.name] = enableNum.data
      lengendData[chartConf.customParams.disable.name] = disableNum.data

      // 日报服务器统计chart options
      let chartOpitons={
        backgroundColor: defaultConf.echartsBackgroudColor,
        grid: {
          left: '20%',
          right: '20%',
          // bottom: 80,
          // top:180,
          containLabel: true
        },
        legend: {
          show: true,
          orient: 'vertical',
          left:'87%',
          y: 'center',
          itemWidth: 3,   // 设置图例图形的宽
          itemHeight: 30,  // 设置图例图形的高
          itemGap: 5,
          width:50,
          formatter: function(params) {
            return "{title|" + params + "}\n{value|" + lengendData[params] + " 个}"
          },
          textStyle: {
            rich: {
              title: {
                fontSize: 14,
                height:20,
                padding: [0, 10],
                color: "#9ca9b1"
              },
              value: {
                fontSize: 16,
                height:20,
                padding: [0, 10],
                color: "#299dff"
              }
            }
          },
        },
        graphic: [
          {
            type: 'image',
            id: 'logo',
            left: '7%',
            top: 10,
            bounding: 'raw',
            silent:true,
            origin: [75, 75],
            style: {
              image: chartConf.customParams.dataUri,
              width: 90,
              height: 90,
            }
          },
        ],
        xAxis: [{
          type :'value',
          axisTick: {
            show: false,
          },
          axisLine: {
            show: false,
          },
          axisLabel: {
            show: false
          },
          splitLine: {
            show: false,
          }
        }],
        yAxis: [{
          //type: 'category',
          data: [''],
          axisTick: {
            show: false,
          },
          axisLine: {
            show: false,
          },
          axisLabel: {
            textStyle: {
              color: '#fff',
            }
          }

        }],
        series: [
          {
            name:chartConf.customParams.disable.name,
            type:'bar',
            silent:true,
            barWidth:16,
            stack: 'enable',
            label: {

                borderWidth: 10,
                distance: 20,
                padding: 3,
                align: 'center',
                fontSize:12,
                verticalAlign: 'middle',
                borderRadius: 1,
                borderColor: defaultConf.colorCustomer[0],
                backgroundColor: defaultConf.colorCustomer[0],
                show: true,
                position: 'top',
                formatter: '停用：{c} %',
                color: '#fff'

            },
            itemStyle: {
              color: defaultConf.colorCustomer[0]
            },
            data:[{
              value:Number(disablePer),
              itemStyle: {
                barBorderRadius:[30,0,0,30],
                color: {
                  colorStops: [{
                    offset: 0,
                    color: 'rgba(228,89,89,0.4)' // 0% 处的颜色
                  }, {
                    offset: 0.5,
                    color: defaultConf.colorCustomer[0] // 100% 处的颜色
                  },{
                    offset: 1,
                    color: 'rgba(228,89,89,0.4)' // 100% 处的颜色
                  }],
                  globalCoord: false, // 缺省为 false
                }
              }
            }],
          },
          {
            name:chartConf.customParams.enable.name,
            type:'bar',
            silent:true,
            barWidth:16,
            stack: 'enable',
            itemStyle: {
              color: defaultConf.colorCustomer[1]
            },
            label: {

                borderWidth: 10,
                distance: 20,
                padding: 3,
                align: 'center',
                fontSize:12,
                verticalAlign: 'middle',
                borderRadius: 1,
                borderColor: defaultConf.colorCustomer[1],
                backgroundColor: defaultConf.colorCustomer[1],
                show: true,
                position: 'top',
                formatter: '启用：{c} %',
                color: '#fff'

            },
            data:[{
              value:Number(enablePer),
              itemStyle: {
                barBorderRadius:[0,30,30,0],
                color: {
                  colorStops: [{
                    offset: 0,
                    color: 'rgba(41,157,255,0.4)' // 0% 处的颜色
                  }, {
                    offset: 0.5,
                    color: defaultConf.colorCustomer[1] // 100% 处的颜色
                  },{
                    offset: 1,
                    color: 'rgba(41,157,255,0.4)' // 100% 处的颜色
                  }],
                  globalCoord: false, // 缺省为 false

                }
              },
            }],
          },
        ]
      }

      // 用于后续增加的整体样式调整 options
      let optionsAppend={}

      // start判断是否是新的一张表，若是，则重新渲染整张表，否，则只渲染数据
      // if(isNewChart){
      // console.log(chartConf.name,chartOpitons)
      this.chartBaseInstance.setOption(chartOpitons,true)
      // }

    },
    // chart渲染end：企业或者终端启用停用占比统计chart

    // chart渲染start：告警统计chart
    async renderChartTypeReportDayAlarmStatistics(defaultConf,chartConf,renderChartDataMethod,isNewChart){
      let getData=await this.getApiData(defaultConf,chartConf)

      if(!getData){
        return false
      }
      // console.log(getData)
      let YAxisData = ['已修复','未修复']
      let LegendData = ['一般','重要','严重']
      let LegendObj = {
        // normal: {label:'一般',color:'#a6c613'},
        // important: {label:'重要',color:'#f19217'},
        // critical: {label:'严重',color:'#c1160e'}
        normal: {label:'一般',color:'#5eb9ef'},
        important: {label:'重要',color:'#f1ac17'},
        critical: {label:'严重',color:'#fb265d'}
      }

      let repairedData = getData.report_data.repaired
      let unrepairedData = getData.report_data.unrepaired
      // let repairedData = { normal: 10, important: 0, critical: 2 }
      // let unrepairedData ={ normal: 5, important: 6, critical: 7 }
      let sumData = {
        '一般' : repairedData.normal + unrepairedData.normal,
        '重要' : repairedData.important + unrepairedData.important,
        '严重' : repairedData.critical + unrepairedData.critical,
      }
      sumData['总数'] = sumData['一般'] + sumData['重要'] +sumData['严重']

      let seriseDataBar = []
      for(let k in LegendObj){
        // 柱状图渐变
        // let linearColor=new this.$echarts.graphic.LinearGradient(
        //   0, 0, 1, 0,
        //   [
        //     {offset: 0, color: LegendObj[k].color},
        //     {offset: 1, color: LegendObj[k].color}
        //   ])

        // 单个bar的配置
        let temp = {
          name: LegendObj[k].label,
          type: 'bar',
          silent:true,
          // stack: '告警数',
          // barWidth:'30%',
          label: {
            show: true,
            color:LegendObj[k].color,
            fontSize:14,
            position:'right',
            formatter:(parmas)=>{
              return parmas.data ? parmas.data : ''
            },
          },
          itemStyle:{
            color:LegendObj[k].color,
            // barBorderRadius:20,
            opacity: 0.8,
          },
          data: [repairedData[k], unrepairedData[k]]
        };
        // 单个bar的配置 end
        seriseDataBar.push(temp)
      }
      let richObj = {
        '一般' : 'normal',
        '重要' : 'important',
        '严重' : 'critical',
      }
      let chartOpitons={
        backgroundColor: defaultConf.echartsBackgroudColor,
        grid: {
          left: '10%',
          right: '30%',
          // bottom: 80,
          // top:180,
          containLabel: false
        },
        legend: {
          show: true,
          orient: 'vertical',
          left:'77%',
          y: 'center',
          itemWidth: 3,   // 设置图例图形的宽
          itemHeight: 30,  // 设置图例图形的高
          itemGap: 5,
          width:50,
          data:LegendData,
          formatter: function(params) {
            return "{" + richObj[params] + "|" + params + '：' + sumData[params] + " 个}"
            // return params
          },
          textStyle: {
            rich: {
              normal: {
                fontSize: 16,
                height:20,
                padding: [0, 10],
                color: LegendObj.normal.color
              },
              important: {
                fontSize: 16,
                height:20,
                padding: [0, 10],
                color: LegendObj.important.color
              },
              critical:{
                fontSize: 16,
                height:20,
                padding: [0, 10],
                color: LegendObj.critical.color
              }
            }
          },
        },
        xAxis:  {
          type: 'value',
          axisLabel:{
            fontSize:12,
            color: '#9ca9b1',
            margin:10,
            // interval:20,
          },
          axisLine: {
            lineStyle: {
              color: '#5f656a'
            },
          },
          splitLine: {
            lineStyle:{
              color: ['#5f656a'],
              type:'dotted'
            },
          },
          axisTick:{
            show:false,
          },
          max:function (v) {
            let  l=v.max.toString().length
            if(l){
              let x = ('1' + new Array(l).join('0'))
              return v.max + parseInt(x)
            }
          },
        },
        yAxis: {
          type:"category",
          data:YAxisData,
          // name:'使用率%',
          nameTextStyle:{
            fontSize:12,
          },
          axisLabel:{
            fontSize:14,
            margin:10,
            color:'#9ca9b1',
          },
          axisLine: {
            lineStyle: {
              color: '#5f656a',
            },
          },
          axisTick:{
            show:true,
            color:'#5f656a',
          },
        },
        series: seriseDataBar
      };

      this.chartBaseInstance.setOption(chartOpitons,true)

    },
    // chart渲染start：告警统计chart end

    // chart渲染start：会议质量图表chart
    async renderChartTypereportDayConfQuality(defaultConf,chartConf,renderChartDataMethod,isNewChart){
      let getData=await this.getApiData(defaultConf,chartConf)
      if(!getData){
        return false
      }
      let reportData = getData.report_data
      // console.log(reportData)

      let seriseData=[]
      reportData.reverse()
      seriseData=reportData.map((item,index)=>{
        let backData={}
        if(item.percent !== 0){
          backData["name"]=item.description

          backData["itemStyle"]={
            // color:linearColor
            color:defaultConf.colorCustomer[index]
          }

          backData["value"]=(item.percent*100)
        }
        return backData
      })
      let chartOpitons={
        backgroundColor: defaultConf.echartsBackgroudColor,
        grid: {
          // left: '3%',
          // right: '3%',
          // bottom: 5,
          // top:35,
          // containLabel: true
        },
        series : [
          {
            name:'辅助',
            type:'pie',
            radius: [0, '11%'],
            center: ['50%', '55%'],
            silent:true,
            label: {
              normal: {
                show: false
              }
            },
            labelLine: {
              normal: {
                show: false
              }
            },
            itemStyle:{
              color:'#fff',
            },

            data:[
              {value:1, name:'fuzhu'},
            ]
          },
          {
            name:'辅助',
            type:'pie',
            radius: ['10%','21%'],
            center: ['50%', '55%'],
            silent:true,
            label: {
              normal: {
                show: false
              }
            },
            labelLine: {
              normal: {
                show: false
              }
            },
            itemStyle:{
              color:'#bfdef0',
            },

            data:[
              {value:1, name:'fuzhu'},
            ]
          },
          {
            name:'辅助',
            type:'pie',
            radius: ['79%','80%'],
            center: ['50%', '55%'],
            silent:true,
            label: {
              normal: {
                show: false
              }
            },
            labelLine: {
              normal: {
                show: false
              }
            },
            itemStyle:{
              color:'#43494d',
            },

            data:[
              {value:1, name:'fuzhu'},
            ]
          },
          {
            name: 'conf_quality',
            type: 'pie',
            radius: ['20%', '70%'],
            center: ['50%', '55%'],
            silent:true,
            roseType: 'radius',
            startAngle:0,
            minAngle:20,
            hoverAnimation:false,
            label: {
              align:'left',
              verticalAlign:'bottom',
              formatter:(params) => {
                // console.log(params.value)
                let content = params.value ? params.name + ": "  + params.value.toFixed(0) + '%' : null
                return content
              },
              textStyle: {
                color: '#9ca9b1',
                fontSize:14,
              }
            },
            labelLine: {
              lineStyle: {
                color: '#4796c4'
              },
              smooth: 0,
              length:3,
              // length2:1,
            },
            data: seriseData,
          }
        ]
      }

      // 用于后续增加的整体样式调整 options
      let optionsAppend={}

      // start判断是否是新的一张表，若是，则重新渲染整张表，否，则只渲染数据
      // if(isNewChart){
      this.chartBaseInstance.setOption(chartOpitons,true)
      // }
    },
    // chart渲染start：会议质量图表chart end

    // chart渲染start：会议时长图表chart
    async renderChartTypereportDayConfTime(defaultConf,chartConf,renderChartDataMethod,isNewChart){
      let getData=await this.getApiData(defaultConf,chartConf)
      if(!getData){
        return false
      }
      let reportData = getData.report_data

      let seriseData = reportData.map(i => {
        return {name:i.description,value:i.data}
      })

      let seriseLabel = {
        show: true,
        position: 'outside',
        textStyle: {
          rich: {
            left: {
              fontSize: 14,
              height:20,
              width:86,
              align:'left',
              padding: [0, 10],
            },
            right: {
              fontSize: 14,
              height:20,
              align:'left',
            },
          }
        },
        formatter: (params)=>{
          return "{left|" + params.data.name + "}{right| : " + params.data.value + " 个}\n{left|占比}" +
            "{right| : " + params.percent + " %}"
        },
      }
      if(chartConf.options.seriseLabel){ seriseLabel = chartConf.options.seriseLabel}

      let chartOpitons={
        backgroundColor: defaultConf.echartsBackgroudColor,
        color:defaultConf.colorCustomer,
        polar: {
          radius:'70%'
        },
        angleAxis: {
          interval: 10,
          type: 'category',
          data: [],
          z: 10,
          axisLine: {
            show: false,
            lineStyle: {
              color: "#43494d",
              width: 1,
              type: "solid"
            },
          },
          axisLabel: {
            interval: 0,
            show: false,
            color: "#43494d",
            margin: 8,
            fontSize: 16
          },
        },
        radiusAxis: {
          min: 40,
          max: 120,
          interval: 20,
          axisLine: {
            show: false,
            lineStyle: {
              color: "#43494d",
              width: 1,
              type: "solid"
            },
          },
          axisLabel: {
            formatter: '{value} %',
            show: false,
            padding: [0, 0, 20, 0],
            color: "#43494d",
            fontSize: 16
          },
          splitLine: {
            show:true,
            lineStyle: {
              color: "#43494d",
              width: 1,
              type: "solid"
            }
          }
        },
        calculable: true,
        series: [{
          type: 'pie',
          silent:true,
          radius: ["5%", "10%"],
          hoverAnimation: false,
          labelLine: {
            normal: {
              show: false,
              length: 30,
              length2: 55
            },
            emphasis: {
              show: false
            }
          },
          data: [{
            name: '',
            value: 0,
            itemStyle: {
              normal: {
                color: "#43494d"
              }
            }
          }]
        },{
          stack: 'a',
          type: 'pie',
          radius: ['18%', '64%'],
          center: ['50%', '50%'],
          roseType: 'area',
          zlevel:10,
          silent:true,
          label: seriseLabel,
          labelLine: {
            normal: {
              show: true,
              length: 20,
              length2: 20
            },
            emphasis: {
              show: false
            }
          },
          data: seriseData,
        }, ]
      }

      // 用于后续增加的整体样式调整 options
      let optionsAppend={}

      // start判断是否是新的一张表，若是，则重新渲染整张表，否，则只渲染数据
      // if(isNewChart){
      this.chartBaseInstance.setOption(chartOpitons,true)
      // }
    },
    // chart渲染start：会议时长图表chart end
  }
};

export default extendReporterDay;
