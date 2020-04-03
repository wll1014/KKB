<template>
    <div style="position: relative;">
      <!--添加按钮-->
      <el-button @click="addFromOrganize" :class="buttonClass">服务器选择</el-button>
      <!-- 表格区域 -->
      <div class="area-table" >
        <el-table ref="tableCrontabTimingDev" tooltip-effect="dark"
                  stripe
                  :max-height="tableHeight"
                  border
                  style="width: 100%;"
                  :data="tableData"
        >
          <el-table-column show-overflow-tooltip type="index" label="序号" width="48">
          </el-table-column>
          <!--<el-table-column :reserve-selection="true" type="selection" width="30">-->
          <!--</el-table-column>-->
          <el-table-column show-overflow-tooltip prop="name" label="服务器" width="170">
          </el-table-column>
          <el-table-column show-overflow-tooltip prop="machine_room_name" label="所属平台域" width="170">
          </el-table-column>
          <el-table-column label="操作">
            <template slot-scope="scope">
              <button type="button" class="button-host-info" @click="delDev(scope.row)">
                <span style="text-decoration: underline;">删除</span>
              </button>
            </template>
          </el-table-column>
        </el-table>
      </div>
      <!-- 表格区域end -->

      <!--蒙版区域start-->
      <!--添加终端-->
      <el-dialog
        title="添加服务器"
        :visible.sync="dialogVisibleAddItem"
        width="1020px"
        append-to-body
        custom-class="theme-dark"
        @closed="beforeCloseClearNode">
        <div style="margin-top: 20px;" v-if="!clearNode">
          <TheOrganizationDevice ref="alarmNotificationTheOD" :customParams="customParams"></TheOrganizationDevice>
        </div>
        <div style="padding: 30px;text-align: center;box-sizing: border-box;">
          <span style="text-align: center;" >
            <el-button @click="addDev()">保 存</el-button>
            <el-button @click="dialogVisibleAddItem = false">取 消</el-button>
          </span>
        </div>
      </el-dialog>
      <!--蒙版区域end-->
    </div>
</template>

<script>
export default {
  name: "TheTableDevAddFromOrganization",
  components:{
    TheOrganizationDevice: () => import('@/components/home/TheOrganizationDevice.vue'),
  },
  props:{
    devList:{
      type: Array,
      default: null,
    },
    buttonClass:{
      type: String,
      default: 'default-button-addfrom-organization',
    },
    tableHeight:{
      type:Number,
      default: 350,
    },
    customParams:{
      type:Object,
      default:null,
    },
  },
  data(){
    return {
      tableData:[],

      dialogVisibleAddItem:false,
      //  清除蒙版内节点
      clearNode:false,
    }
  },
  methods:{

    getTableData(){
      return this.tableData
    },

    addFromOrganize(){
      this.clearNode=false
      this.dialogVisibleAddItem=true
    },

    //蒙版内保存按钮点击函数
    addDev(){
      let tableDataList = this.tableData.map(item => item.moid).filter(item => item)
      // console.log(tableDataList)
      this.treeDataSelected=this.$refs.alarmNotificationTheOD.getSelectedData()
      let newData=this.treeDataSelected.filter(item => tableDataList.indexOf(item.moid) === -1)
      this.dialogVisibleAddItem=false
      this.tableData.push(...newData)
      this.cbData()
    },

    delDev(row){
      const newItems = [...this.tableData]
      // console.log(newItems)
      const index = newItems.indexOf(row)
      newItems.splice(index, 1)
      this.tableData = newItems
      this.cbData()
    },

    // dialog对于动态变化的数据需要在关闭前清除内容节点
    beforeCloseClearNode(){
      // console.log("close")
      this.clearNode=true
    },

    // 当值变化时emit传递
    cbData(){
      this.$emit('data-change',this.tableData);
    },

    init(){
      if(this.devList){
        this.tableData = [...this.devList]
      }
    },
  },
  mounted() {
    this.init()
  }
}
</script>

<style>
.default-button-addfrom-organization{
  position: absolute;
  z-index: 99;
  right: 0;
  top:-49px;
}
</style>
