<template>
  <div class="ops-tree">
    <div v-for="(item,index) in data" :key="index" class="ops-tree-node">
      <div :class="['ops-tree-node__content',{'selected':selectedNode.indexOf(item) !== -1}]"
           @click.stop="!$event.ctrlKey && !$event.shiftKey && handleContentClick(item,index,$event)"
           @dblclick.stop="handleContentDblClick(item,index,$event)"
           @click.ctrl.stop="handleContentCtrlClick(item,index,$event)"
           @click.shift.stop="handleContentShiftClick(item,index,$event)">
        <div class="ops-tree-node__expand-icon"
             v-if="item[dataKey.children]"
             @click.stop="handleExpandIconClick(item,index)">
          <span :class="['el-tree-node__expand-icon el-icon-caret-right',{'expanded':expandList[index]}]"></span>
        </div>
        <span class="el-tree-node__none" v-else></span>
        <span>{{item[dataKey.label]}}</span>
      </div>
      <div v-if="expandList[index] && item[dataKey.children]" class="ops-tree-node__children">
        <opsTreeNode :data="item[dataKey.children]"
                     :dataKey="dataKey"
                     :load="load"
                     :selectedNode="selectedNode"
        ></opsTreeNode>
      </div>
    </div>
  </div>
</template>

<script>
  import {opsTreeStore} from '@/components/common/opsTreeStore'

  export default {
    name: "opsTreeNode",
    props: {
      data: {
        type: Array,
        default: [],
      },
      dataKey: {
        type: Object,
        default: {
          children: 'children',
          label: 'label',
          isLeaf: 'leaf'
        }
      },
      load: {
        type: Function,
      },
      selectedNode: {
        type: Array,
        default: [],
      },
      expandAll: {
        type: Boolean,
        default: false,
      },
    },
    computed: {},
    watch: {
      expandAll(val) {
        this.handleExpandAll()
      },
    },
    data() {
      return {
        expandList: [],
        selectList: [],
      }
    },
    methods: {
      handleExpandAll() {
        if (this.expandAll) {
          for (let index in this.data) {
            if (this.data[index] && this.data[index][this.dataKey.children]) this.handleExpandIconClick(this.data[index], index)
          }
        }
      },
      async handleExpandIconClick(item, index) {
        this.$set(this.expandList, index, !this.expandList[index])
        let res = await this.load(item)
        this.$set(item, this.dataKey.children, res)
      },
      handleContentClick(item, index, e) {
        // this.selectList=[item]
        // this.$emit('node-click',item,index,e.target.parentNode)
        opsTreeStore.$emit('node-click', item, index, this.data, e.target.parentNode)
      },
      handleContentDblClick(item, index, e) {
        // this.selectList=[item]
        // this.$emit('node-click',item,index,e.target.parentNode)
        opsTreeStore.$emit('node-dblclick', item, index, this.data, e.target.parentNode)
      },
      handleContentCtrlClick(item, index, e) {
        // this.selectList.push(item)
        // console.log(item)
        // this.$emit('node-click',item,index,e.target.parentNode)
        opsTreeStore.$emit('node-ctrlclick', item, index, this.data, e.target.parentNode)
      },
      handleContentShiftClick(item, index, e) {
        // this.selectList.push(item)
        // console.log(item)
        // this.$emit('node-click',item,index,e.target.parentNode)
        opsTreeStore.$emit('node-shiftclick', item, index, this.data, e.target.parentNode)
      },
    },
    created() {
      this.handleExpandAll()
    }
  }
</script>

<style>
  .ops-tree {
    color: #9ca9b1;
    font-size: 14px;
    text-align: left;
    -webkit-user-select: none;
    -moz-user-select: none;
    -ms-user-select: none;
    user-select: none;
  }

  .ops-tree-node {
    white-space: nowrap;
    outline: 0;
  }

  .el-tree-node__none {
    display: inline-block;
    width: 14px;
  }

  .ops-tree-node__expand-icon {
    display: inline-block;
    height: 30px;
    line-height: 30px;
    width: 20px;
    text-align: center;
  }

  .ops-tree-node__children {
    padding-left: 28px;
  }

  .ops-tree-node__content {
    height: 30px;
    line-height: 30px;
    margin: 5px 0;
    cursor: pointer;
    align-items: center;
    -webkit-box-align: center;

  }

  .ops-tree-node__content:hover {
    background-color: #00a0e9;
    color: #fff;
  }

  .ops-tree-node__content.selected {
    background-color: #485a6b;
    color: #fff;
  }
</style>
