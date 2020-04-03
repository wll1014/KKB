<template>
  <div class="area-geoinfo-machineroom" style="position: relative;">
    <div style="position: absolute;top:-40px;right:0px;z-index: 100">
      <!--<el-dropdown placement="bottom-start" trigger="click" @command="groupSetting">
        <el-button style="height: 24px;margin-right: 7px">
          合并组设置<i class="el-icon-arrow-down el-icon&#45;&#45;right"></i>
        </el-button>
        <el-dropdown-menu slot="dropdown" class="theme-dark" style="width: 150px">
          <el-dropdown-item v-for="item in dropdownGroupSetting" :command="item.command" :key="item.label" >
            {{item.label}}
          </el-dropdown-item>
        </el-dropdown-menu>
      </el-dropdown>-->
      <el-button @click="maintenanceBatch">添加终端</el-button>
    </div>

    <!--蒙版区域start-->
    <!--添加终端-->
    <el-dialog
      title="添加终端"
      :visible.sync="dialogVisibleAddItem"
      width="1020px"
      append-to-body
      custom-class="theme-dark"
      @closed="beforeCloseClearNode">
      <div style="margin-top: 20px;" v-if="!clearNode">
        <!--<kdDialogSingleTree :defaultExpandList="nodeExpend" :loadNode="loadNode" :treeProps="treeProps" :treeData="allUserDomainInfo" @data-change="treeDataChange" @search="treeFilterSearch"></kdDialogSingleTree>-->
        <TheOrganizationTerminal ref="geoInfoTheOT"></TheOrganizationTerminal>
      </div>
      <div style="padding: 30px;text-align: center;box-sizing: border-box;">
          <span style="text-align: center;" >
            <el-button @click="addGeoItem()">保 存</el-button>
            <el-button @click="dialogVisibleAddItem = false">取 消</el-button>
          </span>
      </div>
    </el-dialog>
    <!--添加分组-->
    <el-dialog
      :title="groupSettingTitle"
      :visible.sync="dialogVisibleGroupSetting"
      width="500px"
      append-to-body
      custom-class="theme-dark"
    >
      <div class="geoinfo-dialog-group">
      <div style="margin-top: 20px;">
        <div v-if="groupSettingStatu==='add'">
          <div class="geoinfo-group">
            <span>合并组名称</span>
            <el-input style="width: 260px;" v-model="inputGroupName" placeholder="请输入合并组名称" maxlength="100"></el-input>
          </div>
          <div class="geoinfo-group">
            <span>合并组坐标</span>
            <el-input style="width: 260px;" v-model="inputGroupGeoInfo" placeholder="请输入合并组坐标" maxlength="100"></el-input>
          </div>
        </div>
      </div>
        <div v-if="groupSettingStatu==='edit'">
          <div class="geoinfo-group">
            <span >请选择合并组</span>
            <el-select popper-class="theme-dark" v-model="SelectedOptionGroup" placeholder="请选择平台域" style="width: 260px;margin-left: 14px;">
              <el-option
                v-for="item in SelectOptionsGroupList" :key="item.id" :label="item.name" :value="item.id">
              </el-option>
            </el-select>
          </div>
          <div class="geoinfo-group">
            <span >修改合并组名称</span>
            <el-input style="width: 260px;" v-model="inputGroupName" placeholder="请输入合并组名称" maxlength="100"></el-input>
          </div>
          <div class="geoinfo-group">
            <span>修改合并组坐标</span>
            <el-input style="width: 260px;" v-model="inputGroupGeoInfo" placeholder="请输入合并组坐标" maxlength="100"></el-input>
          </div>
      </div>
      <div v-if="groupSettingStatu==='del'">
        <div class="geoinfo-group">
          <span>请选择合并组</span>
          <el-select popper-class="theme-dark" v-model="SelectedOptionGroup" placeholder="请选择平台域" style="width: 260px;margin-left: 14px;">
            <el-option
              v-for="item in SelectOptionsGroupList" :key="item.id" :label="item.name" :value="item.id">
            </el-option>
          </el-select>
        </div>
      </div>
      <div style="padding: 10px 20px 20px;text-align: center;box-sizing: border-box;">
          <span style="text-align: center;" >
            <el-button @click="groupSave(groupSettingStatu)">保 存</el-button>
            <el-button @click="dialogVisibleGroupSetting = false">取 消</el-button>
          </span>
      </div>
      </div>
    </el-dialog>
    <!--蒙版区域end-->
    <!-- 表格区域 -->
    <div class="area-table" style="">
      <el-table ref="hostinfoMultipleTable" tooltip-effect="dark"
                max-height="430"
                stripe
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
        <el-table-column show-overflow-tooltip prop="name" label="终端名称" >
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
      TheOrganizationTerminal: () => import('@/components/home/TheOrganizationTerminal.vue'),
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
        allUserDomainInfo:[],

        // tree的节点定义
        treeProps:{},
        // 选中的数据
        treeDataSelected:[],
        // 蒙版数据
        dialogVisibleAddItem:false,
        dialogVisibleGroupSetting:false,
        groupSettingStatu:'',
        groupSettingTitle:'',

        selectedProvince:'',
        selectedCity:'',

        // 省市列表
        boroughInfo:{},

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

        // 列表坐标编辑的状态
        editStatuCoordinate:false,
        editStatuGroup:false,

        // 列表坐标编辑输入框
        inputEditCoordinate:'',
        inputEditGroup:'',
        // 蒙版内合并组编辑输入框
        inputGroupGeoInfo:'',
        inputGroupName:'',
        // 合并组列表和选中值
        SelectedOptionGroup:'',
        SelectOptionsGroupList:[],

        // 合作组设置
        dropdownGroupSetting:[
          {
            label:"添加分组",
            command:"add"
          },{
            label:"编辑分组",
            command:"edit"
          },{
            label:"删除分组",
            command:"del"
          },
        ],

        //  清除蒙版内节点
        clearNode:false,
      }
    },
    computed: {
      selectBoroughInfoProvince() {
        // console.log(Object.keys(this.boroughInfo))
        return Object.keys(this.boroughInfo)
      },
      selectBoroughInfoCity() {
        // console.log(this.boroughInfo[this.selectedProvince])
        return this.boroughInfo[this.selectedProvince]
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
        this.$api.homePage.delGeoTerminalsInfo(params)
          .then(res=>{
            this.getGeoUserInfo()
          })
      },
      // 表格相关函数end

      // 分页相关函数start
      pageHandleSizeChange(val) {
        this.pageSize = val
      },
      pageHandleCurrentChange(val) {
        this.currentPage = val
        this.getGeoUserInfo()
      },
      // 分页相关函数end

      // 页面内触发事件相关函数start

      //蒙版内保存按钮点击函数
      addGeoItem(){
        this.treeDataSelected = this.$refs.geoInfoTheOT.getSelectedData()
        let params = this.treeDataSelected.map((item) =>{
          // console.log(item)
          let info={}
          info["moid"] = item.moid
          info["name"] = item.name
          return info
        })
        this.$api.homePage.postGeoTerminalsInfo(params)
          .then(res=>{
            this.getGeoUserInfo()
          })
        this.dialogVisibleAddItem=false
      },

      // 合并组设置按钮函数
      groupSetting(command){
        switch (command) {
          case "add":
            this.groupSettingTitle="添加分组"
            this.dialogVisibleGroupSetting=true
            this.groupSettingStatu=command
            break;
          case 'edit':
            this.groupSettingTitle="编辑分组"
            this.dialogVisibleGroupSetting=true
            this.groupSettingStatu=command
            break;
          case 'del':
            this.groupSettingTitle="删除分组"
            this.dialogVisibleGroupSetting=true
            this.groupSettingStatu=command
            break;
        }
      },
      // 合并组设置保存按钮函数
      groupSave(command){
        console.log(command)
      },
      // 添加按钮函数
      async maintenanceBatch(){
        this.clearNode=false
        this.allUserDomainInfo=await this.$api.homePage.getAllUserDomainInfo()
        this.dialogVisibleAddItem=true
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
          this.$api.homePage.putGeoTerminalsInfo(row.id,params)
            .then(res=>{
              this.getGeoUserInfo()
            })
        }else{
          this.editStatuCoordinate=row.moid
          this._inputEditCoordinate=row.coordinate_str
        }
      },

      // 合并组点击事件
      groupChange(row,isEdit){
        if(isEdit){
          this.editStatuGroup=''
          console.log(this.editStatuGroup,row.room_moid)
        }else{
          this.editStatuGroup=row.room_moid
          this.inputEditGroup=row.group
        }
      },
      // 页面内触发事件相关函数end

      // API接口start
      // 获取省市列表
      async getGeoUserInfo(){
        this.loadingTableData=true
        let pstart=(this.currentPage-1)*this.pageSize
        let pcount=this.pageSize
        let params={
          start:pstart,
          count:pcount
        }
        let backData=await this.$api.homePage.getGeoTerminalsInfo(params)
        this.pageTotal=backData.total
        this.tableDataGeoinfo = backData.info
        this.loadingTableData=false
        // console.log(this.boroughInfo)
      },

      //API接口end
    },

    mounted(){
      this.getGeoUserInfo()
    },
  }
</script>

<style>
  .geoinfo-dialog-group{
    text-align: center;
  }
  .geoinfo-group{
    margin-bottom: 10px;
  }
  .geoinfo-group>span{
    font-size: 14px;
    color: #9ca9b1;
    margin-right: 30px;
  }
</style>
