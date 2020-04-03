<template>
    <div class="ops-organization-rightlist">
      <div v-for="(item,index) in dataList" :key="index" class="ops-tree-node">
        <div :class="['ops-tree-node__content',{'selected':selectedNode.indexOf(item) !== -1}]"
             @click.stop="!$event.ctrlKey && !$event.shiftKey && handleContentClick(item,index,$event)"
             @dblclick.stop="handleContentDblClick(item,index,$event)"
             @click.ctrl.stop="handleContentCtrlClick(item,index,$event)"
             @click.shift.stop="handleContentShiftClick(item,index,$event)">
          <span class="el-tree-node__none"></span>
          <span >{{item[dataKey.label]}}</span>
        </div>
      </div>
    </div>
</template>

<script>
export default {
  name: "opsOrganizationRightList",
  props:{
    data:{
      type: Array,
      default: [],
    },
    dataKey:{
      type: Object,
      default: {
        children: 'children',
        label: 'label',
        isLeaf: 'leaf'
      }
    },
    load:{
      type:Function,
    },
    filterNodeMethod:{
      type:Function,
    },
    expandAll:{
      type: Boolean,
      default: false,
    },
  },
  watch: {
    data:{
      deep:true,
      handler:function(newVal,oldVal){
        this.dataList = newVal
      }
    },
  },
  data(){
    return{
      dataList:[],
      expandList:[],
      selectList:[],
      selectedNode:[]
    }
  },
  methods: {
    handleContentClick(item,index,e){
      this.selectedNode = [item]
      this.lastClickItem={item,index,e}
    },
    handleContentDblClick(item,index,e){
      this.$emit('node-dblclick',item,index,e)
    },
    handleContentCtrlClick(item,index,e){
      this.lastClickItem={item,index,e}
      let sIndex = this.selectedNode.indexOf(item)
      if(sIndex !== -1){
        this.selectedNode.splice(sIndex,1)
      }else {
        this.selectedNode.push(item)
      }
    },
    handleContentShiftClick(item,index,e){
      let sliceIndex = this.lastClickItem.index >= index ? [index,this.lastClickItem.index] : [this.lastClickItem.index,index]
      this.selectedNode = this.data.slice(sliceIndex[0],sliceIndex[1]+1)
    },

    // 对外提供的方法
    getSelectedNode(){
      return this.selectedNode
    },
    async filterNode(val){
      let fData = [...this.data]
      this.dataList = await this.filterNodeMethod(val,fData)
    },
  },
  mounted(){
    this.dataList=this.data
  },
}
</script>

<style>
.ops-organization-rightlist{
  color: #9ca9b1;
  font-size: 14px;
  text-align: left;
  -webkit-user-select:none;
  -moz-user-select:none;
  -ms-user-select:none;
  user-select:none;
}
</style>
