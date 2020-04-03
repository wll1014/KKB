<template>
  <!--<kdDialogSingleTree :defaultExpandList="nodeExpend"-->
                      <!--:loadNode="loadNode"-->
                      <!--:buttonRAll="loadSelectedNode"-->
                      <!--:treeProps="treeProps"-->
                      <!--:treeData="allUserDomainInfo"-->
                      <!--@search="treeFilterSearch"-->
                      <!--ref="theOT"-->
  <!--&gt;</kdDialogSingleTree>-->
  <kdTransferTree :defaultExpandList="nodeExpend"
                  :expandAll="expandAll"
                  :loadNode="loadNode"
                  :buttonRAll="loadSelectedNode"
                  :treeProps="treeProps"
                  :treeData="allUserDomainInfo"
                  @search="treeFilterSearch"
                  ref="theOT"
  ></kdTransferTree>
</template>

<script>
  export default {
    name: "TheOrganizationTerminal",
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
        // 用户域信息
        allUserDomainInfo:[],

        //缓存过滤的信息
        dataByFilterSearch:[],
      }
    },
    methods:{
      //获取目前选择的数据
      getSelectedData(){
        return this.$refs.theOT.getSelectedData()
      },

      // tree懒加载函数
      async loadNode(node,isNew=false){
        let data = node

        if(data[this.treeProps.children] && data[this.treeProps.children].length > 0){
          return data[this.treeProps.children]
        }else{
          // 懒加载数据
          let roomInfo=await this.getUserDomainUserInfo(data.moid)
          return roomInfo;
        }
      },

      // tree过滤搜索事件
      async treeFilterSearch(val){
        if(val){
          let params={
            key:val
          }
          let userInfo = await this.$api.homePage.getUserInfoBySearch(params)
          this.allUserDomainInfo=userInfo
          this.expandAll=true
          this.dataByFilterSearch=userInfo //缓存过滤后的数据
        }else{
          this.dataByFilterSearch=[] //清空过滤后的数据
          this.expandAll=false
          this.allUserDomainInfo=await this.$api.homePage.getAllUserDomainInfo()
        }
      },

      // tree点击全部右移的按钮触发返回的数据
      async loadSelectedNode(v,filter){
        if(v && v.length > 0){
          let callbackData = []
          for(let item of v){
            if(item.hasOwnProperty(this.treeProps.children)){
              let userInfo=[]
              if(filter){ //如果有过滤条件
                userInfo = this.dataByFilterSearch.find(i=> i.moid === item.moid).info
              }else{
                userInfo=await this.getUserDomainUserInfo(item.moid)
              }
              if(userInfo && userInfo.length>0){
                callbackData = callbackData.concat(userInfo)
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

      // 获取所有平台域
      async getAllUserDomainInfo(){

        this.allUserDomainInfo=await this.$api.homePage.getAllUserDomainInfo()
      },

      //获取用户域下的用户
      async getUserDomainUserInfo(moid){
        let start=0
        let count=50
        let temCacheLength=50
        let temCache=[]
        while (temCacheLength>=count){
          let params={
            start:start,
            count:count
          }
          let data=await this.$api.homePage.getUserDomainUserInfo(moid,params)
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
      this.getAllUserDomainInfo()
    },
  }
</script>

<style scoped>

</style>
