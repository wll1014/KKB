<template>
    <div class="theme-dark intelligent-wireshark">
      <div class="auto-tcpdump">
        <IntelligentWiresharkAutoTcpdump></IntelligentWiresharkAutoTcpdump>
      </div>
      <div style="margin-top: 30px;">
        <IntelligentWiresharkCustom></IntelligentWiresharkCustom>
      </div>
    </div>
</template>

<script>
export default {
  name: "IntelligentWireshark",
  components:{
    // TheMainLayoutHeader,
    // TheMainLayoutLeft,
    IntelligentWiresharkAutoTcpdump: () => import('@/components/diagnose/IntelligentWiresharkAutoTcpdump.vue'),
    IntelligentWiresharkCustom: () => import('@/components/diagnose/IntelligentWiresharkCustom.vue'),
  },
}
</script>

<style>
.intelligent-wireshark{
  box-sizing: border-box;
  padding: 20px 25px;
}
.intelligent-wireshark .auto-tcpdump{
  padding-bottom: 30px;
  border-bottom: #3d4046 1px dashed ;
}
</style>
