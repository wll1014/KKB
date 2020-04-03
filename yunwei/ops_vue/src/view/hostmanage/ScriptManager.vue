
<template>
<div class="theme-dark" style="margin:20px 20px 20px 28px;">
  <KdTabCommon :tab-list="tabList" :active-tab="activeTab" class-name="tab-alarm-yp" @tab-change="tabChange"></KdTabCommon>
  <div class="area-tab-content">
      <component :is="activeTab"></component>
  </div>
</div>

</template>

<script>
export default {
  components: {
    KdTabCommon: () => import('@/components/common/KdTabCommon.vue'),
    ScriptList: () => import('@/view/hostmanage/ScriptList.vue'),
    ScriptInstantTask: () => import('@/view/hostmanage/ScriptInstantTask.vue'),
    ScriptTimeTask: () => import('@/view/hostmanage/ScriptTimeTask.vue'),
  },
	data(){
		return{
		  activeTab:'ScriptList',
      tabList:[['ScriptList','脚本列表'],
               ['ScriptInstantTask','即时任务'],
               ['ScriptTimeTask','定时任务'],],
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
.tab-alarm-yp{
  margin-bottom: 30px;
}
</style>
