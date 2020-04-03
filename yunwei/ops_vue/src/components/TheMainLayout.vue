<template>
  <div>
    <header class="keda-main-header" style="z-index:2000;">
      <TheMainLayoutHeader></TheMainLayoutHeader>
    </header>
    <div class="keda-layout6-main">
      <!-- left  -->
      <div class="keda-layout6-sidebar">
        <TheMainLayoutLeft></TheMainLayoutLeft>
      </div>
      <!-- right -->
      <div class="keda-layout6-content" :style="{'margin-left':isCollapse?'62px':'180px'}">
        <router-view v-if="isRouterAlive"></router-view>
      </div>
    </div>
    <!--test DIV 用于模拟鼠标点击事件，防止休眠引起的异常 --20200319 -->
    <!--<div id="test"></div>-->
  </div>
</template>

<script>
  // import TheMainLayoutHeader from "@/components/TheMainLayoutHeader.vue"
  // import TheMainLayoutLeft from "@/components/TheMainLayoutLeft.vue"
  export default {
    name: 'TheMainLayout',
    // 点击页面侧边栏重载功能的实现（该处提供了提供给后代组件的数据/方法）
    provide() {
      return {
        contentPageReload: this.contentPageReload
      }
    },
    components: {
      // TheMainLayoutHeader,
      // TheMainLayoutLeft,
      TheMainLayoutHeader: () => import('@/components/TheMainLayoutHeader.vue'),
      TheMainLayoutLeft: () => import('@/components/TheMainLayoutLeft.vue'),
    },
    data() {
      return {
        isRouterAlive: true,
      }
    },
    computed: {
      isCollapse() {
        return this.$store.getters.getsiderbarCollapseStatu
      },
    },
    methods: {
      //content区域页面重新载入函数
      contentPageReload() {
        this.isRouterAlive = false;
        this.$nextTick(function () {
          this.isRouterAlive = true
        })
      }
    },
    mounted() {
    },
  }
</script>

<style>
  .keda-main-header {
    height: 54px;
    z-index: 1030;
    background: #373d41;
    /*border-bottom: 1px solid #303030;*/
    position: fixed;
    width: 100%;
    min-width: 540px;
  }

  .keda-layout6-sidebar {
    position: fixed;
    top: 0;
    left: 0;
    margin-top: 54px;
    min-height: 100%;
    /* width: 230px; */
    z-index: 101;
    bottom: 0;
  }

  .keda-layout6-content {
    /* min-height: 768px; */
    /* padding-bottom: 15px; */
    /*z-index: 800;*/
    padding-top: 54px;
  }

</style>
