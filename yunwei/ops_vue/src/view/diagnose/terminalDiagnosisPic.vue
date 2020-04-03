<template>
	<div class="area-chart-base theme-dark" style="height: 100%; width: 100%">
    <div style="float: right;margin: 30px 0 0 0;" v-if="terminalPicInfo">
      <span style="color: #9ca9b1;float: right;margin-right: 39px;font-size: 14px;">未连接</span>
      <i class="ops-icons-bg icon-legend-orange" style="float: right;margin-right: 7px;margin-top: 8px"></i>
      <span style="color: #9ca9b1;float: right;margin-right: 35px;font-size: 14px;">已连接</span>
      <i class="ops-icons-bg icon-legend-blue" style="float: right;margin-right: 7px;margin-top: 8px"></i>
    </div>
	  <div id="TermianlDiaChartID" style="height: 100%; width: 100%;padding-top: 20px"></div>
	</div>
</template>

<script>
	export default {
	  props:{
      terminalPicInfo:{
        type:Object,
        default:{}
      }
    },
		data() {
			return {
				option : {
					tooltip: {
            extraCssText:"background:black;color:#9ca9b1;margin:5px",
            formatter: function(params) {
              //根据值是否为空判断是点还是线段
              if(params.data.name){//如果鼠标移动到线条
                if(params.data.name === "PAS"&&params.data.itemStyle!==undefined){
                  // if(连接成功){}
                  return  "PAS IP ：" + params.data.info.ip +"<br>" +
                          "最后注册时间 ：" + params.data.info.last_register + "<br>" +
                          "注册机房 ：" + params.data.info.machineroom + "<br>" +
                          "最后过NAT IP ：" + params.data.info.last_nat_ip + "<br>" +
                          "终端地址+端口 ：" + params.data.info.dev_ip_port + "<br>" +
                          "h460状态 ：" + params.data.info.h460 + "<br>" +
                          "Moid ：" + params.data.info.moid + "<br>" +
                          "产品ID ：" + params.data.info.product_id + "<br>" +
                          "设备号 ：" + params.data.info.dev_id + "<br>" +
                          "端口复用 ：" + params.data.info.portreuse + "<br>" +
                          "传输类型 ：" + params.data.info.transport_type + "<br>" +
                          "机房Moid ：" + params.data.info.machineroom_moid + "<br>" +
                          "APS登录 ：" + params.data.info.aps_login + "<br>" +
                          "网呈终端 ：" + params.data.info.stp + "<br>" +
                          "私网终端状态 ：" + params.data.info.privatenet + "<br>" +
                          "注册阶段 ：" + params.data.info.reg
                  // else if(连接失败){}
                  // return "PAS IP ：" + params.data.pas_ip +"：<br>" +
                  //         "最后注册时间 ：" + params.data.time + "：<br>" +
                  //         "未连接原因 ：" + params.data.result
                }else if(params.data.name === "PAS"&&params.data.itemStyle===undefined){
                  return "PAS IP ：" + params.data.info.ip +"<br>" +
                          "最后注册时间 ：" + params.data.info.last_register + "<br>" +
                          "未连接原因 ：" + params.data.info.err_msg + "<br>" +
                           "ErrCode ：" + params.data.info.errcode;
                }else if(params.data.category === 4){

                }else{
                  if(params.data.itemStyle!==undefined){
                    return  params.data.name  +" IP ：" + params.data.info.ip
                  }else{

                  }
                }
            }}
          },
					animationDurationUpdate: 1500,
					animationEasingUpdate: 'quinticInOut',
          // animation : false,
					series: [
							{
							    type: 'graph',
									layout: 'force',
									roam: false,
									label: {
											show: true
									},
									edgeSymbol: ['circle', 'arrow'],
									edgeSymbolSize: [0, 0],  //设置箭头大小
									edgeLabel: {
											fontSize: 20
									},
									itemStyle : {
													normal: {
															borderWidth:1,
															lineStyle: {
																	type: 'dashed',
															},
                            color: '#e45959',
													}
											},
									 symbolSize: (value, params) => {
											//根据数据params中的data来判定数据大小
											switch (params.data.category) {
													case 4:return 120;break;
													default:return 60;
													};
									},
									data: [],
									// links: [],
									links: [],
									lineStyle: {
											opacity: 0.9,
											width: 2,
											curveness: 0,
									},
                force: {
                  edgeLength: 185,
                  repulsion: 1000,
                  layoutAnimation: false,//去除echarts动画
                  initLayout:'circular',
                },

							}
					]
				},
			}
		},
		methods: {
	    getData(){
        this.option.series[0].data = this.terminalPicInfo.data
        this.option.series[0].links = this.terminalPicInfo.link
        this.init()

      },
			init() {
				var myChart = echarts.init(document.getElementById('TermianlDiaChartID'));
				myChart.setOption(this.option);
			}
		},
    watch:{
      terminalPicInfo(newV,oldV){
        // console.log(newV)
        // for(var i in newV){
        //   // console.log(newV[i])
        //   this.terminalPicInfo=newV[i]
        // }

        this.getData()

      },
      deep:true
    },
	}
</script>

<style>
</style>
