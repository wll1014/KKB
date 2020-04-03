<template>
  <!--<kdDialogSingleTree :defaultExpandList="nodeExpend"-->
                      <!--:loadNode="loadNode"-->
                      <!--:buttonRAll="loadSelectedNode"-->
                      <!--:treeProps="treeProps"-->
                      <!--:treeData="allRoomInfo"-->
                      <!--@search="treeFilterSearch"-->
                      <!--ref="theOP"-->
  <!--&gt;</kdDialogSingleTree>-->
  <kdTransferTree :defaultExpandList="nodeExpend"
                  :expandAll="expandAll"
                  :loadNode="loadNode"
                  :buttonRAll="loadSelectedNode"
                  :treeProps="treeProps"
                  :treeData="allRoomInfo"
                  @search="treeFilterSearch"
                  ref="theOP"
  ></kdTransferTree>
</template>

<script>
  export default {
    name: "TheOrganizationPeripheral",
    components:{
      kdTransferTree: () => import('@/components/common/kdTransferTree.vue'),

    },
    data(){
      return {
        // 树结构是否展开
        nodeExpend: [],
        expandAll:false,
        // tree的节点定义
        treeProps:{
          children: 'info',
          label: 'name',
          nodeKey:'moid',
          isLeaf: 'leaf'
        },
        // 机房信息
        allRoomInfo:[],

        //缓存过滤的信息
        dataByFilterSearch:[],

      }
    },
    methods:{
      //获取目前选择的数据
      getSelectedData(){
        return this.$refs.theOP.getSelectedData()
      },

      // tree懒加载函数
      async loadNode(node,isNew=false){
        let data = node

        if(data[this.treeProps.children] && data[this.treeProps.children].length > 0){
          return data[this.treeProps.children]
        }else{
          // 懒加载数据
          let roomInfo=await this.getPeripheralInfo(data.moid)
          return roomInfo;
        }
      },

      // tree过滤搜索事件
      async treeFilterSearch(val){
        if(val){
          let params={
            key:val
          }
          let roomInfo = await this.$api.homePage.getPeripheralInfoBySearch(params)
          this.allRoomInfo=roomInfo
          this.expandAll=true
          this.dataByFilterSearch=roomInfo //缓存过滤后的数据
        }else{
          this.dataByFilterSearch=[] //清空过滤后的数据
          this.expandAll=false
          this.allRoomInfo=await this.$api.homePage.getPeripheralMachineRoomInfo()
        }
      },

      // tree点击全部右移的按钮触发返回的数据
      async loadSelectedNode(v,filter){
        if(v && v.length > 0){
          let callbackData = []
          for(let item of v){
            if(item.hasOwnProperty(this.treeProps.children)){
              let roomInfo=[]
              if(filter){ //如果有过滤条件
                roomInfo = this.dataByFilterSearch.find(i=> i.moid === item.moid).info
              }else{
                roomInfo=await this.getPeripheralInfo(item.moid)
              }
              if(roomInfo && roomInfo.length>0){
                callbackData = callbackData.concat(roomInfo)
              }
            }else{
              callbackData.push(item)
            }
          }
          callbackData=this.Es6duplicate(callbackData,'moid')
          return callbackData
        }else{
          return null
        }
      },

      // 获取所有机房
      async getPeripheralMachineRoomInfo(){
        this.allRoomInfo=await this.$api.homePage.getPeripheralMachineRoomInfo()
      },

      //获取外设服务器
      async getPeripheralInfo(moid){
        let start=0
        let count=50
        let temCacheLength=50
        let temCache=[]
        while (temCacheLength>=count){
          let params={
            start:start,
            count:count
          }
          let data=await this.$api.homePage.getPeripheralInfo(moid,params)
          temCacheLength=data.length
          start=start+temCacheLength
          temCache=temCache.concat(data)
        }
        return temCache
      },
      // 常用方法
      //Es6 + ES5去重办法
      Es6duplicate(arr,type){
        if(arr.length == 0){
          return arr;
        }else{
          if(type){
            var obj = {}
            var newArr = arr.reduce((cur,next) => {
              obj[next[type]] ? "" : obj[next[type]] = true && cur.push(next);
              return cur;
            },[])
            return newArr;
          }else{
            return Array.from(new Set(arr));
          }
        }
      },
    },
    mounted(){

      this.getPeripheralMachineRoomInfo()
    },

  }
</script>

<style scoped>

</style>
