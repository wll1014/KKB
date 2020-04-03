<template>
  <div class="area-kd-tab">
    <div v-for="(item,index) in tabList" :class="['kd-tab--border',className]">
      <span @click="tabChange(item[0])" :class="['kd-tab',{'active':activeTabVal === item[0]}]" >{{item[1]}}</span>
      <div class="tab-divider--vertical" v-if="index !== tabList.length-1" :style="tabStyle"></div>
    </div>
  </div>
</template>

<script>
  export default{
    props:{
      tabList:Array,
      className:String,
      activeTab:{
        type: [Number, String],
        default: '',
      },
      width:{
        type: [Number],
        default: 16,
      },
    },
    data() {
    	return {
        activeTabVal:this.activeTab,
      }
    },
    watch: {
      activeTab: function (newVal,oldVal) {
        this.activeTabVal = newVal
      },
      // currentPageNumber: function (newVal,oldVal) {
      //   this.$emit("update:currentPage",parseInt(newVal))
      // },
    },
    computed: {
    // 计算属性的 getter
      tabStyle: function () {
        // console.log({margin: '0 ' + this.width + 'px ' + '0px ' + this.width-3 +'px'})
        let leftWidth=this.width-3
        return {margin: '0px ' + this.width + 'px ' + '0px ' + leftWidth + 'px'}
      },
      // currentPageNumber: function () {
      //   return this.currentPage
      // },
    },
    methods: {
      tabChange(val){
        this.activeTabVal=val
        this.$emit('tab-change',val);
      },
    },
    mounted(){
      // this.activeTabVal=this.activeTab

    },
  }
</script>

<style>
  .kd-tab--border{
    display: inline-block;
  }
  .kd-tab{
    color: #9ca9b1;
    font-size: 12px;
    cursor:pointer;
    text-align: center;
  }
  .kd-tab:hover{
    color:#00a2ff;
  }
  .kd-tab.active{
    font-size: 14px;
    font-weight: 700;
    color:#00a2ff;
  }
  .tab-divider--vertical{
    display: inline-block;
    width: 2px;
    height: 17px;
    margin: 0px 16px 0px 13px;
    vertical-align: middle;
    position: relative;
    background-color: #3d4046;
  }
</style>
