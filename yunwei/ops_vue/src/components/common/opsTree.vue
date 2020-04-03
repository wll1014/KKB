<template>
  <div class="ops-tree-root">
    <opsTreeNode :data="data" :dataKey="dataKey" :load="load" :selectedNode="selectedNode"
                 :expandAll="expandAll"></opsTreeNode>
  </div>
</template>

<script>
  import {opsTreeStore} from '@/components/common/opsTreeStore'

  export default {
    name: "opsTree",
    components: {
      opsTreeNode: () => import('@/components/common/opsTreeNode.vue'),
    },
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
      expandAll: {
        type: Boolean,
        default: false,
      },
    },
    computed: {},
    data() {
      return {
        selectedNode: [],
        lastClickItem: null,
      }
    },
    methods: {
      handleNodeClick(item, index, parentItem, e) {
        this.selectedNode = [item]
        this.lastClickItem = {item, index, parentItem, e}
      },
      handleNodeDblClick(item, index, parentItem, e) {
        this.$emit('node-dblclick', item, index, parentItem, e)
      },
      handleNodeCtrlClick(item, index, parentItem, e) {
        this.lastClickItem = {item, index, parentItem, e}
        let sIndex = this.selectedNode.indexOf(item)
        if (sIndex !== -1) {
          this.selectedNode.splice(sIndex, 1)
        } else {
          this.selectedNode.push(item)
        }
      },
      handleNodeShiftClick(item, index, parentItem, e) {
        if (this.lastClickItem && this.lastClickItem.parentItem === parentItem) {
          let sliceIndex = this.lastClickItem.index >= index ? [index, this.lastClickItem.index] : [this.lastClickItem.index, index]
          this.selectedNode = parentItem.slice(sliceIndex[0], sliceIndex[1] + 1)
        } else {
          this.handleNodeClick(item, index, parentItem, e)
        }
      },

      // 对外提供的方法
      getSelectedNode() {
        return this.selectedNode
      },
    },
    created() {
      opsTreeStore.$on('node-click', (item, index, parentItem, e) => {
        this.handleNodeClick(item, index, parentItem, e)
      })
      opsTreeStore.$on('node-dblclick', (item, index, parentItem, e) => {
        this.handleNodeDblClick(item, index, parentItem, e)
      })
      opsTreeStore.$on('node-ctrlclick', (item, index, parentItem, e) => {
        this.handleNodeCtrlClick(item, index, parentItem, e)
      })
      opsTreeStore.$on('node-shiftclick', (item, index, parentItem, e) => {
        this.handleNodeShiftClick(item, index, parentItem, e)
      })
    }
  }
</script>

<style>

</style>
