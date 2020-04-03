<template>
  <div style="width: 100%;height: 100%;margin-top: 10px;">
    <ChartExtendLargeModel :ChartID="ChartID" :chartConf="activeChartConf" :chartChange="chartChange">
      <template #emptyData>
        <p class="reportday__empty">当日无数据</p>
      </template>
    </ChartExtendLargeModel>
  </div>
</template>

<script>
  export default {
    name: "ReporterDayChart",
    components: {
      KdTabCommon: () => import('@/components/common/KdTabCommon.vue'),
      ChartExtendLargeModel: () => import('@/components/monitor/ChartExtendLargeModel.vue'),
    },
    props: {
      ChartName: String,
      ChartID: String,
      params: Object,
    },
    watch: {
      params: {
        deep: true,
        handler: function (newVal, oldVal) {
          this.renderChart()
        }
      },
    },
    data() {
      return {
        chartChange: '',
        activeChartConf: {},
        // start 此组件支持的chartConf
        chartConfSupport: {
          reportDayServerDev: {
            name: "服务器类型概况",
            chartRenderMethod: "reportDay",
            dataRenderMethon: "reportDayServerDev",
            url: ['api', 'getReporterDayCommon'],
            urlParams: 'nextReFresh',
            staticParams: {
              type: 'machine_type'
            },
            options: {
              titleText: '服务器总数',
              titleSubtext: ' 台',
              seriseLabel: {
                formatter: function (params, ticket, callback) {
                  return '{grey|' + params.name + '}{grey| ：' + params.value + ' 台}';
                },
                rich: {
                  grey: {
                    color: "#9ca9b1",
                    fontSize: 14,
                    padding: [4, 0],
                    align: 'center',
                  },
                },
              },
            },
          },
          reportDayConfType: {
            name: "会议类型概况",
            chartRenderMethod: "reportDay",
            dataRenderMethon: "reportDayServerDev",
            url: ['api', 'getReporterDayCommon'],
            urlParams: 'nextReFresh',
            staticParams: {
              type: 'conf_resolution'
            },
            options: {
              titleText: '会议总数',
            },
          },
          reportDayConfQuality: {
            name: "会议质量概况",
            chartRenderMethod: "reportDay",
            dataRenderMethon: "reportDayConfTime",
            url: ['api', 'getReporterDayConfQuality'],
            urlParams: 'nextReFresh',
            staticParams: {
              type: 'conf_quality'
            },
            options: {
              customerColor: ['#247aac', '#288fcb', '#4face3', '#71c6f9'],
              seriseLabel: {
                show: true,
                position: 'outside',
                textStyle: {
                  rich: {
                    left: {
                      fontSize: 14,
                      height: 20,
                      width: 50,
                      align: 'left',
                      padding: [0, 10],
                    },
                    right: {
                      fontSize: 14,
                      height: 20,
                      align: 'left',
                    },
                  }
                },
                formatter: (params) => {
                  return "{left|" + params.data.name + "}{right| : " + params.data.value + " 个}\n{left|占比}" +
                    "{right| : " + params.percent + " %}"
                },
              },
            },
          },
          reportDayConfTime: {
            name: "会议时长概况",
            chartRenderMethod: "reportDay",
            dataRenderMethon: "reportDayConfTime",
            url: ['api', 'getReporterDayCommon'],
            urlParams: 'nextReFresh',
            staticParams: {
              type: 'conf_time'
            },
            options: {
              customerColor: ['#1dd796', '#68e7bb', '#006f48', '#20805e', '#00ab6f'],
              titleText: '会议总数',
            },
          },
          reportDayTransmitResource: {
            name: "转发资源统计",
            chartRenderMethod: "timeline",
            dataRenderMethon: "timeline",
            url: ['api', 'getReporterDayTransmitResource'],
            urlParams: 'nextReFresh',
            staticParams: {
              type: 'transmit_resource'
            },
            options: {
              isArea: true,
              echartsCustom: {
                grid: {
                  bottom: 45
                },
                yAxis: {
                  name: "%",
                  nameTextStyle: {
                    color: '#9ca9b1',
                    fontSize: 12,
                  }
                },
                tooltip: {
                  formatter: (params,) => {
                    let time = this.$echarts.format.formatTime('yyyy-MM-dd', params[0].value[0])
                      + ' ' + this.$echarts.format.formatTime('hh:mm:ss', params[0].value[0]);
                    let usedFormatter = []
                    for (let item of params) {
                      let showValue = item.value[1].toFixed(2) + " %"
                      let avaliable = (item.value[2] / 1024).toFixed(2) + "Mbps"
                      if (item.value[1] === null || item.value[1] === undefined) {
                        showValue = null
                        avaliable = null
                      }
                      // usedFormatter.push(showValue,avaliable)
                      let htmlContent =
                        '<div class="lchart-tootip-content--block">' +
                        '<div class="lchart-tootip-content-left">' + '使用率' + '</div>' +
                        '<div class="lchart-tootip-content-right">' + ':&nbsp' + showValue + '</div>' +
                        '</div>'
                      // +
                      // '<div class="lchart-tootip-content--block">' +
                      // '<div class="lchart-tootip-content-left">'+ '已用带宽'+'</div>' +
                      // '<div class="lchart-tootip-content-right">'+':&nbsp' + avaliable + '</div>' +
                      // '</div>'
                      // usedFormatter.push(item.seriesName + ': ' + showValue)
                      usedFormatter.push(htmlContent)
                    }
                    // console.log(freeFormatter)
                    let header = '<div style="font-size: 16px;margin-bottom: 12px;">' + time + '</div>'
                    let content = [...usedFormatter].join('\n')
                    return header + content;
                  }
                },
              },
            }
          },
          reportDayCompaniesEnablePercent: {
            name: "企业启用停用占比",
            chartRenderMethod: "reportDay",
            dataRenderMethon: "reportDayEnablePercent",
            url: ['api', 'getReporterDayCommon'],
            urlParams: 'nextReFresh',
            staticParams: {
              type: 'enable_disable_companies'
            },
            customParams: {
              dataUri: 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAFoAAABaCAYAAAA4qEECAAAAGXRFWHRTb2Z0d2FyZQBBZG9iZSBJbWFnZVJlYWR5ccllPAAAA4RpVFh0WE1MOmNvbS5hZG9iZS54bXAAAAAAADw/eHBhY2tldCBiZWdpbj0i77u/IiBpZD0iVzVNME1wQ2VoaUh6cmVTek5UY3prYzlkIj8+IDx4OnhtcG1ldGEgeG1sbnM6eD0iYWRvYmU6bnM6bWV0YS8iIHg6eG1wdGs9IkFkb2JlIFhNUCBDb3JlIDUuNi1jMTM4IDc5LjE1OTgyNCwgMjAxNi8wOS8xNC0wMTowOTowMSAgICAgICAgIj4gPHJkZjpSREYgeG1sbnM6cmRmPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5LzAyLzIyLXJkZi1zeW50YXgtbnMjIj4gPHJkZjpEZXNjcmlwdGlvbiByZGY6YWJvdXQ9IiIgeG1sbnM6eG1wTU09Imh0dHA6Ly9ucy5hZG9iZS5jb20veGFwLzEuMC9tbS8iIHhtbG5zOnN0UmVmPSJodHRwOi8vbnMuYWRvYmUuY29tL3hhcC8xLjAvc1R5cGUvUmVzb3VyY2VSZWYjIiB4bWxuczp4bXA9Imh0dHA6Ly9ucy5hZG9iZS5jb20veGFwLzEuMC8iIHhtcE1NOk9yaWdpbmFsRG9jdW1lbnRJRD0ieG1wLmRpZDo0ZmI3ZDY0Zi1jMzMwLTNhNGYtODllOS01MmUxZjE2MzlhZWYiIHhtcE1NOkRvY3VtZW50SUQ9InhtcC5kaWQ6MzgwQjMyRjEwQTczMTFFQUI4MUJBRjg5NUIyQUU4REMiIHhtcE1NOkluc3RhbmNlSUQ9InhtcC5paWQ6MzgwQjMyRjAwQTczMTFFQUI4MUJBRjg5NUIyQUU4REMiIHhtcDpDcmVhdG9yVG9vbD0iQWRvYmUgUGhvdG9zaG9wIENDIDIwMTcgKFdpbmRvd3MpIj4gPHhtcE1NOkRlcml2ZWRGcm9tIHN0UmVmOmluc3RhbmNlSUQ9InhtcC5paWQ6OTM5MDViNzItODFjZC1mZTQzLTg1YWEtOWUxNjMxMjI3YzM0IiBzdFJlZjpkb2N1bWVudElEPSJhZG9iZTpkb2NpZDpwaG90b3Nob3A6OTQ1MjA4NjgtZmEzYy0xMWU5LWE0ZGUtZTZjZDllMTU5NGZkIi8+IDwvcmRmOkRlc2NyaXB0aW9uPiA8L3JkZjpSREY+IDwveDp4bXBtZXRhPiA8P3hwYWNrZXQgZW5kPSJyIj8+KbQKtwAAAdxJREFUeNrsnT9OwzAUhx2oysIFcg4Gph6g52BnQmLIEGVgQGJi7zk4QLJkyDXoARBDi1B4FiniT1NZVZ5x4u+TnlLFdZp8SuLm5yFJ27YG9DlBAaIRDYhGNKIB0YgGRCM6cmYuXyqK4utzWTd2sZRaSaWBHc9a6krqSesHFpcXf9blea52Roco2XT7tJrSrSMN+CpNpyT6x9UklfxzLWIYDKsAjqOKQTQgGtGIBkQjGhCNaEQPw53URqrdU5uuXaNvdKJvpOY9bXb9tVLf6EQ/SG172t6kHpX6Ric6kzoz+wOgedeu0XdHq1TPZd0sGQz1OTrvRvRxshHdEVzezRntRoVongwB0YhGNCAa0aFjU8AX4ykNjDkmvZU6N59p4WhFjyEmPf22zdGKJib9xUxpu5lxizOH7stgyL8OQLQy791yi2hd7qVeu8F3tIPhGPA66HKPRjSiAdGIRnTEx05MaohJnSEm9SSamNTTkyExKYMhohE9UYhJPUFM6gliUu7RgGhEA6IRjWhANKIB0YhGNCA6bJzSu7Ju7Mxz36RpiC/bUt0n8bHbvs2ybcyaDXVGH5qZjhnnWXlX0YdmpmPGeVY+4TV7DIaIBkQjGtGAaEQDohGNaPDBhwADAGVFmx91yVWcAAAAAElFTkSuQmCC',
              enable: {
                key: 'company_enable',
                name: '在用'
              },
              disable: {
                key: 'company_disable',
                name: '停用'
              }
            },
            options: {
              customerColor: ['#e45959', '#299dff']
            },
          },
          reportDayTerminalsEnablePercent: {
            name: "账号启用停用占比",
            chartRenderMethod: "reportDay",
            dataRenderMethon: "reportDayEnablePercent",
            url: ['api', 'getReporterDayCommon'],
            urlParams: 'nextReFresh',
            staticParams: {
              type: 'enable_disable_terminals'
            },
            customParams: {
              dataUri: 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAFoAAABaCAYAAAA4qEECAAAAGXRFWHRTb2Z0d2FyZQBBZG9iZSBJbWFnZVJlYWR5ccllPAAAA4RpVFh0WE1MOmNvbS5hZG9iZS54bXAAAAAAADw/eHBhY2tldCBiZWdpbj0i77u/IiBpZD0iVzVNME1wQ2VoaUh6cmVTek5UY3prYzlkIj8+IDx4OnhtcG1ldGEgeG1sbnM6eD0iYWRvYmU6bnM6bWV0YS8iIHg6eG1wdGs9IkFkb2JlIFhNUCBDb3JlIDUuNi1jMTM4IDc5LjE1OTgyNCwgMjAxNi8wOS8xNC0wMTowOTowMSAgICAgICAgIj4gPHJkZjpSREYgeG1sbnM6cmRmPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5LzAyLzIyLXJkZi1zeW50YXgtbnMjIj4gPHJkZjpEZXNjcmlwdGlvbiByZGY6YWJvdXQ9IiIgeG1sbnM6eG1wTU09Imh0dHA6Ly9ucy5hZG9iZS5jb20veGFwLzEuMC9tbS8iIHhtbG5zOnN0UmVmPSJodHRwOi8vbnMuYWRvYmUuY29tL3hhcC8xLjAvc1R5cGUvUmVzb3VyY2VSZWYjIiB4bWxuczp4bXA9Imh0dHA6Ly9ucy5hZG9iZS5jb20veGFwLzEuMC8iIHhtcE1NOk9yaWdpbmFsRG9jdW1lbnRJRD0ieG1wLmRpZDo0ZmI3ZDY0Zi1jMzMwLTNhNGYtODllOS01MmUxZjE2MzlhZWYiIHhtcE1NOkRvY3VtZW50SUQ9InhtcC5kaWQ6MzgwQjMyRjUwQTczMTFFQUI4MUJBRjg5NUIyQUU4REMiIHhtcE1NOkluc3RhbmNlSUQ9InhtcC5paWQ6MzgwQjMyRjQwQTczMTFFQUI4MUJBRjg5NUIyQUU4REMiIHhtcDpDcmVhdG9yVG9vbD0iQWRvYmUgUGhvdG9zaG9wIENDIDIwMTcgKFdpbmRvd3MpIj4gPHhtcE1NOkRlcml2ZWRGcm9tIHN0UmVmOmluc3RhbmNlSUQ9InhtcC5paWQ6OTM5MDViNzItODFjZC1mZTQzLTg1YWEtOWUxNjMxMjI3YzM0IiBzdFJlZjpkb2N1bWVudElEPSJhZG9iZTpkb2NpZDpwaG90b3Nob3A6OTQ1MjA4NjgtZmEzYy0xMWU5LWE0ZGUt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',
              enable: {
                key: 'terminal_enable',
                name: '在用'
              },
              disable: {
                key: 'terminal_disable',
                name: '停用'
              }
            },
            options: {
              customerColor: ['#e45959', '#299dff']
            },
          },
          reportDayAlarmStatisticsDev: {
            name: "服务器告警统计",
            chartRenderMethod: "reportDay",
            dataRenderMethon: "reportDayAlarmStatistics",
            url: ['api', 'getReporterDayCommon'],
            urlParams: 'nextReFresh',
            staticParams: {
              type: 'server_warning'
            },
            options: {},
          },
          reportDayAlarmStatisticsMt: {
            name: "服务器告警统计",
            chartRenderMethod: "reportDay",
            dataRenderMethon: "reportDayAlarmStatistics",
            url: ['api', 'getReporterDayCommon'],
            urlParams: 'nextReFresh',
            staticParams: {
              type: 'terminal_warning'
            },
            options: {},
          },
        },
        // end 此组件支持的chartConf
      }
    },
    methods: {
      renderChart() {
        // this.chartChange = this.ChartID + this.params.date
        // console.log( this.chartChange)
        let p = {...this.activeChartConf.staticParams}
        p.date = this.params.date
        this.$set(this.activeChartConf, 'urlParams', p)
      },
    },
    mounted() {
      setTimeout(() => this.renderChart(), 200)
    },
    created() {
      this.activeChartConf = {...this.chartConfSupport[this.ChartName]}
    }
  }
</script>

<style scoped>
  .reportday__empty {
    color: #909399;
    font-size: 14px;
    position: absolute;
    top: calc(50% - 7px);
    left: calc(50% - 35px);
  }
</style>
