<template>
  <div class="theme-dark" style="position: relative">
    <!--<div class="button-back" style="">-->
      <!--<el-button icon="ops-icons-bg icon-arrow-circle-left" @click="back" circle></el-button>-->
    <!--</div>-->
    <!--tootip提示-->
    <div style="position: absolute;top:-45px;right:15px;z-index: 100">
      <el-tooltip effect="dark" placement="bottom">
        <div slot="content">坐标：经度,纬度值，如：116.232922,39.542637
          <br/>
          <br/>
          坐标可通过链接：<a href="https://api.map.baidu.com/lbsapi/getpoint/index.html" target="_blank" style="color: #299dff;">https://api.map.baidu.com/lbsapi/getpoint/index.html</a> 查询
          <br/>
          <br/>
          合并组名称：当多个终端所处相同地理坐标时，
          通过此标识将多个终端合并到一起展示。
        </div>
        <i class="ops-icons-bg icon-info" ></i>
      </el-tooltip>
    </div>
    <div style="padding: 0px 15px;min-height: 520px;">
      <KdTabCommon :tab-list="tabList" :active-tab="activeTab" class-name="tab-alarm" @tab-change="tabChange" :width=18></KdTabCommon>
      <div class="area-tab-content">
        <component :is="activeTab"></component>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "GeoInfoMaintenance",
  components: {
    KdTabCommon: () => import('@/components/common/KdTabCommon.vue'),
    MapSettingGeoInfoGlobal: () => import('@/components/home/MapSettingGeoInfoGlobal.vue'),
    MapSettingGeoInfoMachineRoom: () => import('@/components/home/MapSettingGeoInfoMachineRoom.vue'),
    MapSettingGeoInfoPeripheral: () => import('@/components/home/MapSettingGeoInfoPeripheral.vue'),
    MapSettingGeoInfoTerminal: () => import('@/components/home/MapSettingGeoInfoTerminal.vue'),
  },
  data(){
    return{
      // tab信息
      activeTab:'MapSettingGeoInfoGlobal',
      tabList:[
        ['MapSettingGeoInfoGlobal','地图配置'],
        ['MapSettingGeoInfoMachineRoom','机房设置'],
        ['MapSettingGeoInfoTerminal','终端设置'],
        ['MapSettingGeoInfoPeripheral','外设服务器设置'],],


    }
  },
  methods: {
    tabChange(val){
      // console.log(val)
      this.activeTab=val
    },

    back(){
      this.$emit('back',true);
    },

  },
  mounted(){

  },
}
</script>

<style >
.tab-alarm{
  margin-bottom: 20px;
}
.button-back{
  position:absolute;
  top:11px;
  left:8px;
  z-index: 100;
}
</style>
