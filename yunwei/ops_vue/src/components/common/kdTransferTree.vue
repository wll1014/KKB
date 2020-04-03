<template>
	<div class="kd-singletree" style="width:100%;text-align: center;">
		<div class='theme-dark el-transfer-panel ' style='background: #232629;width:388px;border-radius:0px;'>
			<div class="transfer--header" style="" >
				待选列表
			</div>
			<div class="transfer--body" style=''>
        <div>
          <el-input clearable v-model='leftFilterText' style="margin-right: 10px;width: 290px;" @keyup.enter.native="buttonSearch" maxlength="100">
          </el-input>
          <el-button @click="buttonSearch">搜索</el-button>
        </div>
        <div class="transfer-tree--border" style="">
				<opsTree  ref="singleTree"
                 :dataKey="treeProps"
                 :load="loadNode"
                 :data="treeData"
                 :expandAll="expandAll"
                  @node-dblclick="handleDblClick"
                  ></opsTree>
        </div>
			</div>
		</div>

		<div class="el-transfer__buttons theme-dark">
			<el-button circle @click='rightAll' icon="ops-icons-bg icon-arrow-circle-rightall"></el-button>
			<el-button circle @click='rightOne' icon="ops-icons-bg icon-arrow-circle-right" ></el-button>
			<el-button circle @click='leftOne' icon="ops-icons-bg icon-arrow-circle-left" ></el-button>
			<el-button circle @click='leftAll' icon="ops-icons-bg icon-arrow-circle-leftall"></el-button>
		</div>
		<div class='theme-dark el-transfer-panel ' style='background: #232629;width:388px;border-radius:0px;'>
			<div  class="transfer--header" >
				已选列表&nbsp;&nbsp;{{  this.rightTreeData.length }}
			</div>
			<div class="transfer--body" style=''>
        <div>
          <el-input clearable v-model='rightFilterText' style='margin-right: 10px;width: 290px;' maxlength="100">
            <!-- <el-button icon="el-icon-search"></el-button> -->
          </el-input>
          <el-button @click="buttonSearchRightTreeData">搜索</el-button>
        </div>
        <div class="transfer-tree--border" style="">
        <!--<el-tree style='color:#9ca9b1;' ref="singleTreeRight"-->
                 <!--:data="rightTreeData"-->
                 <!--:props="treeProps"-->
                 <!--:highlight-current="true"-->
                 <!--:filter-node-method="filterNode"-->
                 <!--:node-key="treeProps.nodeKey"></el-tree>-->
          <opsOrganizationRightList  ref="singleTreeRight"
                                    :dataKey="treeProps"
                                    :data="rightTreeData"
                                     :filterNodeMethod="filterNode"
                                     @node-dblclick="handleDblClickRight"
          ></opsOrganizationRightList>
        </div>
			</div>
		</div>
	</div>
</template>

<script>
export default {
  components: {
    opsTree: () => import('@/components/common/opsTree.vue'),
    opsOrganizationRightList: () => import('@/components/common/opsOrganizationRightList.vue'),
  },
  props:{
    treeData:{
      type: Array,
      default: [],
    },
    treeProps:{
      type: Object,
      default: {
        children: 'children',
        label: 'label',
        isLeaf: 'leaf',
        nodeKey:'key'
      }
    },
    loadNode:{
      type:Function,
    },
    buttonRAll:{
      type:Function,
      default:function () {
        return null
      }
    },
    defaultExpandList:{
      type:Array,
      default:[]
    },
    selectLengthLimit:{
      type:Number,
      default:0,
    },
    expandAll:{
      type: Boolean,
      default: false,
    },
  },
  watch: {
    rightFilterText(val) {
      this.$refs.singleTreeRight.filterNode(val);
    },
    // treeProps(val){
    //   console.log(val)
    // }
  },
  computed:{
    expandList(){
      return this.defaultExpandList
    },
  },
  data(){
    return {
      // 左侧选中的节点
      elLeftSelectedNode:null,

      // 右侧内容
      rightTreeData:[],
      leftFilterText:'',
      rightFilterText:'',

      keepaliveLeftFilterText:'',
    };
  },
  methods: {
    // 判断一个元素是否包含一个指定节点
    isDOMContains(parentEle,ele) {
      //parentEle: 要判断节点的父级节点
      //ele:要判断的子节点
      //container : 二者的父级节点

      //如果parentEle h和ele传的值一样，那么两个节点相同
      if (parentEle == ele) {
        return true
      }
      if (!ele || !ele.nodeType || ele.nodeType != 1) {
        return false;
      }
      //如果浏览器支持contains
      if (parentEle.contains) {
        return parentEle.contains(ele)
      }
      //火狐支持
      if (parentEle.compareDocumentPosition) {
        return !!(parentEle.compareDocumentPosition(ele) & 16);
      }
    },

    // 过滤函数
    filterNode(value,data) {
      if (!value) return data;
      let filterData = data.map(item => {
          if(item[this.treeProps.label].indexOf(value) !== -1) return item
        }).filter(i=>i)
      return filterData
    },
    // 记录当前选中的文档(element)节点
    handleClick(data,node,e){
      // console.log(e.$el)
      this.elLeftSelectedNode=e.$el
    },
    // 将双击节点与当前选中的文档(element)节点比较，若是子节点则添加
    handleDblClick(item,index,parentItem,e){
      this.rightOne()
    },
    // 右侧将双击节点与当前选中的文档(element)节点比较，若是子节点则添加
    handleDblClickRight(item,index,e){
      // console.log(newItems)
      const sIndex = this.rightTreeData.indexOf(item)
      if(sIndex !== -1) this.rightTreeData.splice(sIndex, 1)
      if(this.rightFilterText.length > 0) this.$refs.singleTreeRight.filterNode(this.rightFilterText)
    },
    // 按钮函数
    async rightAll(){
      let selectedNode=this.$refs.singleTree.getSelectedNode()

      let fItem = await this.buttonRAll(selectedNode,this.keepaliveLeftFilterText)
      if(fItem && fItem.length > 0){
        // let selectedData = singleNode.moid
        // 传参：（过滤列表，嵌套层的Key，过滤匹配的key，过滤文本）
        // let filterItem = this.factorialFindKey([singleNode],
        //                                        this.treeProps.children,
        //                                        this.treeProps.label,
        //                                        false)
        // if(this.rightTreeData.length){
        let arrFilter = [...fItem].filter(
          x => this.rightTreeData.every(
            y => y[this.treeProps.nodeKey] !== x[this.treeProps.nodeKey]));
          // console.log(arrFilter)

        this.rightTreeData=[...this.rightTreeData,...arrFilter]
        this.callbackData()
      }
    },
    rightOne(){
      let selectedNode=this.$refs.singleTree.getSelectedNode()
      if(selectedNode.length > 0){
        let filterItem = selectedNode.map(item=>{
          if(item.hasOwnProperty(this.treeProps.children)){
            return null
          }else {
            return item
          }
        }).filter(item => item)

        if(filterItem.length > 0){
          let arrFilter = [...filterItem].filter(
            x => this.rightTreeData.every(
              y => y[this.treeProps.nodeKey] !== x[this.treeProps.nodeKey]));

          this.rightTreeData=[...this.rightTreeData,...arrFilter]
          this.callbackData()
        }
      }
    },
    leftOne(){
      // console.log(this.$refs.singleTreeRight.getCurrentNode().name,this.$refs.singleTreeRight.getCurrentNode().moid)
      let selectedNode=this.$refs.singleTreeRight.getSelectedNode()
      if(selectedNode && selectedNode.length > 0){
        selectedNode.forEach(item=>{
          let sIndex = this.rightTreeData.findIndex(i=>i[this.treeProps.nodeKey] === item[this.treeProps.nodeKey])
          this.rightTreeData.splice(sIndex,1)
        })
        this.callbackData()
      }
    },
    leftAll(){
      this.rightTreeData=[]
      this.callbackData()
    },

    // 功能函数start
    // 递归查找符合最里面一层的对象，传参：（过滤列表，嵌套层的Key，过滤匹配的key，过滤文本）
    factorialFindKey(i,deepKey,filterKey,filterText){
      let temList=i.flatMap((item)=>{
        if(item.hasOwnProperty(deepKey)){
          return this.factorialFindKey(item[deepKey],deepKey,filterKey,filterText)
        }else{
          if(filterText && item[filterKey].indexOf(filterText) !== -1){
            return item
          }else{
            return item
          }
        }
      }).filter(item => item)
      return temList
    },

    // 功能函数end

    // 当值变化时emit传递
    callbackData(){
      this.$emit('data-change',this.rightTreeData);
    },

    //获取目前选择的数据
    getSelectedData(){
      return this.rightTreeData
    },
    // 传递过滤项
    buttonSearch(){
      this.keepaliveLeftFilterText=this.leftFilterText
      this.$emit('search',this.keepaliveLeftFilterText);
    },
    buttonSearchRightTreeData(){
      this.$refs.singleTreeRight.filterNode(this.rightFilterText);
    },
  },
  mounted(){
    // console.log(this.treeData)
  },
};
</script>

<style>
  .transfer--header{
    background: #292e30;
    color:#9ca9b1;
    padding-left: 10px;
    height: 40px;
    vertical-align: middle;
    text-align: left;
    line-height: 40px;
  }
  .transfer--body{
    height: 400px;
    background: #232629;border: 1px solid #292e30;
    padding: 10px;
  }
  .transfer-tree--border{
    margin-top: 14px;
    height: 350px;
  }
  .kd-singletree .el-transfer-panel{
    border: none;
  }
  .kd-singletree .ops-tree-root {			/* 设置el-tree达到父组件高度时出现滚动条 */
	  width: 100%;
		height: 100%;
	  overflow: auto;
		overflow-x:hidden;
		background: #232629;
	}
  .kd-singletree .ops-organization-rightlist {			/* 设置el-tree达到父组件高度时出现滚动条 */
    width: 100%;
    height: 100%;
    overflow: auto;
    overflow-x:hidden;
    background: #232629;
  }
  .kd-singletree .el-transfer-panel .el-input-group__append,
  .kd-singletree .el-transfer-panel .el-input-group__prepend{
			background: #69808d;
			border: none;
			border-radius: 0px;
			color:white;
		}
  .kd-singletree .el-transfer__buttons {
			width:30px;
			margin: 0;
			padding: 0 42px;
		}
  .kd-singletree .el-transfer__buttons .el-button+.el-button{
			margin-left:0;
		}
  .kd-singletree .el-transfer__buttons .el-button {
			margin-bottom: 20px;
		}
  .kd-singletree .el-transfer-panel .el-tree-node > .el-tree-node__content:hover   {
			background-color: #00a0e9;
      color:#fff;
		}
		/*.el-transfer-panel .el-tree-node:focus > .el-tree-node__content{*/
			/*background-color: #00a0e9 ;*/
		/*}*/

  .kd-singletree .el-transfer-panel .el-tree--highlight-current .el-tree-node.is-current > .el-tree-node__content{
    background-color: #485a6b;
    color:#fff;
  }
  .kd-singletree .el-transfer-panel .el-tree-node:focus > .el-tree-node__content{
    background-color: #485a6b;
    color:#fff;
  }
  .kd-singletree .el-tree-node__label {
    margin-left: 3px;
  }
  .kd-singletree .el-tree-node__content{
    height: 30px;
    margin: 5px 0px;
  }
</style>
