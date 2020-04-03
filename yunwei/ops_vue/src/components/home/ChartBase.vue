<template>
    <div class="area-chart-base" style="height: 100%; width: 100%">
      <div :id="chartID" style="height: 100%; width: 100%"></div>
    </div>
</template>

<script>
export default {
  name: "ChartBase",
  props:{
    chartID:String,
  },
  data(){
    return {
      // props
      // chartID:"temp1",

      // 定时器
      timer:null,
      // 表的实例化
      chartInstance:'',
    }
  },

  computed: {
    // 监听左侧导航栏变化
    isCollapse() {
      return this.$store.getters.getsiderbarCollapseStatu
    },
  },
  watch:{
    // 当左侧导航栏变化时echart resize
    // 写法一：不需要computed
    // "$store.getters.getsiderbarCollapseStatu":(newStatu,oldStatu)=>{
    //   // this.chartsResize()
    //   console.log("asdsd")
    // }
    // 写法二：配合computed实现监听
    isCollapse(newStatu,oldStatu) {
      this.chartsResize()
    },
  },

  methods:{
    getChartInstance(){
      return this.chartInstance
    },
    setOption(option){
      this.chartInstance.setOption(option)
    },
    // resize函数
    chartsResize(){
      this.chartInstance.resize()
    },

    // 图表销毁
    chartDispose(){
      this.chartInstance.dispose()
    },

    // 定时器
    setTimer(time=60){
      const timer = setInterval(()=>{
        // console.log(time)
      },time*1000)
      this.$once('hook:beforeDestroy',()=>{
        clearInterval(timer)
      })
    },


    init(){
      this.chartInstance = this.$echarts.init(document.getElementById(this.chartID));
      // this.chartInstance.setOption(this.chartOption)
      window.addEventListener("resize",this.chartsResize)
      // 若是异步调用此组件，需调用此方法返回chart实例,（暂时取消不用）
      // this.$emit('chartInstanceOver',this.chartInstance)
      // this.$once('hook:beforeDestroy',()=>{
      //   window.removeEventListener("resize",this.chartsResize)
      //   if(this.chartInstance){
      //     this.chartDispose()
      //   }
      // })
    },

  },
  mounted(){
    this.init()

    // 新的监听当前el的style变化的方法；未做测试波及较大暂不用
    // let conf = {
    //   attributes: true, // 属性的变动
    //   attributeFilter: ['style'], // 观察特定属性
    //   // subtree: true, // 是否将观察器应用于该节点的所有后代节点
    // }
    // let observer = new MutationObserver(function (mutations, observer){
    //   console.log(mutations);
    //   if(mutations[0]){
    //     console.log(mutations[0].target.offsetWidth)
    //   }
    // })
    // observer.observe(this.$el.firstChild,conf)  //开始观测
    // observer.disconnect();  // 停止观测
    // 新的监听当前el的style变化的方法；未做测试波及较大暂不用 end
  },

  beforeDestroy () {
    window.removeEventListener("resize",this.chartsResize)
    if(this.chartInstance){
      this.chartDispose()
    }
  },
}
</script>

<style scoped>

</style>
