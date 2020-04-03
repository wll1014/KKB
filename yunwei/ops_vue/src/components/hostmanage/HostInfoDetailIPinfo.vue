<template>
  <div class="table-ip" style="padding-top: 10px;">
  <el-table ref="hostDetailIPinfoTable" tooltip-effect="dark" 
   stripe
   border
   style="width: 100%;" 
   :data="hostDetailIPinfo">
    <el-table-column show-overflow-tooltip type="index" label="序号" width="48">
    </el-table-column>
    <el-table-column show-overflow-tooltip prop="ip" label="IP地址">
    </el-table-column>
  	<el-table-column show-overflow-tooltip prop="subnet_mask" label="子网掩码" >
  	</el-table-column>
  	<el-table-column show-overflow-tooltip prop="gateway" label="网关" >
  	</el-table-column>
  </el-table>
  </div>
</template>

<script>
  export default { 
    props:{
      host_moid:String,
    },
    data() {
    	return {
        hostDetailIPinfo:[],
      };
      },
    methods: {
      getSingleHostInfo(id){
        this.$api.hostManageApi.getSingleHostInfo(id)
        	.then(res => {
        		// this.hostDetailinfo = res.data.data
            if(res.data.data){
              this.hostDetailIPinfo=res.data.data.ip_list
            }else{
              this.hostDetailIPinfo={}
            }
        	})
      },
    },
    mounted() {
      this.getSingleHostInfo(this.host_moid);
    	// this.getHostInfoList();
    }
  }
</script>

<style>
</style>
