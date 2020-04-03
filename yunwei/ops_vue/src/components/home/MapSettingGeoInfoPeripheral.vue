<template>
  <div class="area-geoinfo-machineroom" style="position: relative">
    <div style="position: absolute;top:-40px;right:0px;z-index: 100">
      <el-button @click="maintenanceBatch">添加服务器</el-button>
    </div>

    <!--蒙版区域start-->
    <el-dialog
      title="添加服务器"
      :visible.sync="dialogVisibleEditGeoInfo"
      width="1020px"
      append-to-body
      custom-class="theme-dark"
      @closed="beforeCloseClearNode"
    >
      <div style="margin-top: 20px;" v-if="!clearNode">
        <!--<kdDialogSingleTree :defaultExpandList="nodeExpend" :loadNode="loadNode" :treeProps="treeProps" :treeData="allRoomInfo" @data-change="treeDataChange" @search="treeFilterSearch"></kdDialogSingleTree>-->
        <TheOrganizationPeripheral  ref="geoInfoTheOP"></TheOrganizationPeripheral>
      </div>
      <div style="padding: 30px;text-align: center;box-sizing: border-box;">
          <span style="text-align: center;" >
            <el-button @click="addGeoItem()">保 存</el-button>
            <el-button @click="dialogVisibleEditGeoInfo = false">取 消</el-button>
          </span>
      </div>
    </el-dialog>
    <!--蒙版区域end-->
    <!-- 表格区域 -->
    <div class="area-table" style="">
      <el-table ref="hostinfoMultipleTable" tooltip-effect="dark"
                stripe
                max-height="430"
                border
                style="width: 100%;"
                :data="tableDataGeoinfo"
                :cell-style="setCellStyle"
                v-loading="loadingTableData"
                element-loading-background="rgba(0, 0, 0, 0.5)"
      >
        <el-table-column show-overflow-tooltip type="index" label="序号" width="48">
        </el-table-column>
        <!--<el-table-column :reserve-selection="true" type="selection" width="30">-->
        <!--</el-table-column>-->
        <el-table-column show-overflow-tooltip prop="name" label="服务器名称" width="300">
        </el-table-column>

        <el-table-column label="坐标" width="180">
          <template slot-scope="scope">
            <el-input
              v-model="_inputEditCoordinate"
              style="text-align: center;"
              @blur="editCoordinate(scope.row,true)"
              v-if="editStatuCoordinate===scope.row.moid"
              maxlength="20"
              v-geoFocus></el-input>
            <span style="" @click="editCoordinate(scope.row,false)" v-else>{{scope.row.coordinate_str}}</span>
          </template>
        </el-table-column>
        <el-table-column label="操作">
          <template slot-scope="scope">
            <button type="button" class="button-host-info" @click="delGeoItem(scope.row)">
              <span style="text-decoration: underline;">删除</span>
            </button>
          </template>
        </el-table-column>
      </el-table>
    </div>
    <!-- 表格区域end -->

    <!-- 分页区start -->
    <!-- 		<div class="pagination-class theme-dark">
                <el-pagination @size-change="pageHandleSizeChange" @current-change="pageHandleCurrentChange" :current-page="currentPage"
                 :page-sizes="[10, 20, 30, 40]" :page-size="pageSize" layout="total, sizes, prev, pager, next, jumper" :total="hostInfoTableData.length">
                </el-pagination>
            </div> -->
    <div style="margin-top: 20px;">
      <KdPagination
        @current-change="pageHandleCurrentChange"
        :page-size="pageSize"
        :current-page.sync="currentPage"
        :total="pageTotal"></KdPagination>
    </div>
    <!-- 分页区end -->
  </div>
</template>

<script>
  export default {
    name: "MapSettingGeoInfoMachineRoom",
    components:{
      KdPagination: () => import('@/components/common/KdPagination.vue'),
      TheOrganizationPeripheral: () => import('@/components/home/TheOrganizationPeripheral.vue'),
    },
    directives: {
      // 注册一个局部的自定义指令 v-geoFocus
      geoFocus: {
        // 指令的定义
        inserted: function (el) {
          // 聚焦元素
          el.querySelector('input').focus()
        }
      }
    },
    data(){
      return{
        // 树结构是否展开
        nodeExpend:[],
        // 域列表
        platformDomainList:'',
        // 机房信息
        allRoomInfo:[],

        // tree的节点定义
        treeProps:{},
        // 选中的数据
        treeDataSelected:[],
        // 蒙版数据
        dialogVisibleEditGeoInfo:false,

        selectedProvince:'',
        selectedCity:'',

        // 省市列表
        peripheralInfo:{},

        // 分页数据
        currentPage: 1,
        pageSize: 9,
        pageTotal:0,

        // 表格数据
        loadingTableData:false,
        tableDataGeoinfo:[],

        // 表格 行选中记录数据
        rowSelectedChange:{},
        rowMultipleSelection:[],

        // 当前编辑的数据的记录
        // editInfo:[],

        // 坐标编辑的状态
        editStatuCoordinate:false,
        // 坐标编辑输入框
        inputEditCoordinate:'',

        //  清除蒙版内节点
        clearNode:false,
      }
    },
    computed: {
      selectperipheralInfoProvince() {
        // console.log(Object.keys(this.peripheralInfo))
        return Object.keys(this.peripheralInfo)
      },
      selectperipheralInfoCity() {
        // console.log(this.peripheralInfo[this.selectedProvince])
        return this.peripheralInfo[this.selectedProvince]
      },
      _inputEditCoordinate: {
        set: function(value) {
          this.inputEditCoordinate = value;
        },
        get: function() {
          return this.inputEditCoordinate.replace(/[^0-9,.]+/g,'')
          // return temp.split(',').filter(i=>i).join(',')
        }
      },
    },
    methods:{
      // 表格相关函数start
      // 改变表头样式
      setHeaderCellStyle({row, column, rowIndex, columnIndex}){
        let headerCellStyle = {
          'border-right': 'none',
        }
        if(columnIndex===0||columnIndex===1){
          return headerCellStyle
        }
      },
      // 改变单元格样式
      setCellStyle({row, column, rowIndex, columnIndex}) {
        // console.log(row, column, rowIndex, columnIndex)
        let cellStyle = {
          'color': 'red',
        }
        // if (row.uptime === '异常' && columnIndex === 11) {
        //   // this.$set(cellStyle,'background-color','red')
        //   return cellStyle
        // }
      },
      // 单行选中变化函数
      handleSelectionChange(val) {
        this.rowSelectedChange={}
        val.forEach(row => {
          this.$set(this.rowSelectedChange,row.moid,true)
        });
        this.rowMultipleSelection = val;
      },
      // 选中行选中后变色
      classRowSelectChange({row, rowIndex}){
        if(this.rowSelectedChange[row.moid]){
          // console.log(this.hostInfoSelectedChange[row.moid])
          return "row-selected"
        }
      },

      // 表格删除按钮函数
      delGeoItem(val){
        this.loadingTableData=true
        let delList = [val.id]
        // console.log(val.id)
        let params={
          ids:delList,
        }
        this.$api.homePage.delGeoPeripheralInfo(params)
          .then(res=>{
            this.getGeoPeripheralInfo()
          })
        // this.dialogVisibleEditGeoInfo=true
      },
      // 表格相关函数end

      // 分页相关函数start
      pageHandleSizeChange(val) {
        this.pageSize = val
      },
      pageHandleCurrentChange(val) {
        this.currentPage = val
        this.getGeoPeripheralInfo()
      },
      // 分页相关函数end

      // 页面内触发事件相关函数start
      //蒙版内保存按钮点击函数
      addGeoItem(){
        this.treeDataSelected = this.$refs.geoInfoTheOP.getSelectedData()
        let params = this.treeDataSelected.map((item) =>{
          let info={}
          info["moid"] = item.moid
          info["name"] = item.name
          return info
        })
        this.$api.homePage.postGeoPeripheralInfo(params)
          .then(res=>{
            // console.log("add PeripheralInfo ")
            this.getGeoPeripheralInfo()
          })
        this.dialogVisibleEditGeoInfo=false

      },

      // 添加按钮函数
      async maintenanceBatch(){
        // this.allRoomInfo=await this.$api.homePage.getAllRoomInfo()
        this.clearNode=false
        this.allRoomInfo=await this.$api.homePage.getPeripheralMachineRoomInfo()
        this.dialogVisibleEditGeoInfo=true
      },

      // dialog对于动态变化的数据需要在关闭前清除内容节点
      beforeCloseClearNode(){
        // console.log("close")
        this.clearNode=true
      },

      // 地理坐标点击编辑事件
      editCoordinate(row,isEdit){
        if(isEdit){
          this.editStatuCoordinate=''
          let coordinate = this._inputEditCoordinate.split(",")
          if(coordinate.length<2){
            coordinate=[]
          }
          let params = {
            name:row.name,
            moid:row.moid,
            coordinate:coordinate,
          }
          this.$api.homePage.putGeoPeripheralInfo(row.id,params)
            .then(res=>{
              this.getGeoPeripheralInfo()
            })
        }else{
          this.editStatuCoordinate=row.moid
          this._inputEditCoordinate=row.coordinate_str
        }
      },
      // 页面内触发事件相关函数end

      // API接口start

      // 获取外设服务器列表
      async getGeoPeripheralInfo(){
        this.loadingTableData=true
        let pstart=(this.currentPage-1)*this.pageSize
        let pcount=this.pageSize
        let params={
          start:pstart,
          count:pcount
        }
        let backData=await this.$api.homePage.getGeoPeripheralInfo(params)
        this.pageTotal=backData.total
        this.tableDataGeoinfo = backData.info
        // console.log(this.peripheralInfo)
        this.loadingTableData=false
      },

      //API接口end
    },

    mounted(){
      this.getGeoPeripheralInfo()
    },
  }
</script>

<style>

</style>
