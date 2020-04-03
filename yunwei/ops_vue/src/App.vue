<template>
  <div id="app" class="theme-dark">
			<!-- <layout-ham></layout-ham> -->
			<router-view v-if="isLogin"/>
  </div>
</template>

<script>
export default {
  name: 'App',
  data() {
    return {
      isLogin:false
    }
  },
  methods:{
    // 登录校验
    login(){
      this.$api.sidebarapi.islogin().then(res=>{
        this.isLogin = true
        if(res.data.success){
          this.$store.dispatch('login',res.data.data)
        }
      }).catch(err=>{})
    },
  },
  mounted(){
    this.login()
  }
}
</script>

<style>
</style>
