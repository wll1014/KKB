<template>
  <div class="theme-dark" style="padding: 20px 20px 20px 27px;">
    <KdTabCommon :tab-list="tabList" :active-tab="activeTab" class-name="tab-alarm" @tab-change="tabChange"></KdTabCommon>
    <div class="area-tab-content">
      <component :is="activeTab"></component>
    </div>
  </div>

</template>

<script>
  export default {
    components: {
      KdTabCommon: () => import('@/components/common/KdTabCommon.vue'),
      VersionMt: () => import('@/view/version/VersionMt.vue'),
      VersionPlatform: () => import('@/view/version/VersionPlatform.vue'),
      VersionOperatingSystem: () => import('@/view/version/VersionOperatingSystem.vue'),
    },
    data(){
      return{
        activeTab:'VersionPlatform',
        tabList:[['VersionPlatform','平台版本'],
          ['VersionMt','终端版本'],
          ['VersionOperatingSystem','操作系统版本'],],
      }
    },
    methods: {
      tabChange(val){
        this.activeTab=val
      },
    },
    mounted(){

    },

  }
</script>

<style>
  .tab-alarm{
    margin-bottom: 20px;
  }
</style>
