<template>
	<div class='theme-dark' style="padding: 0px 25px;">
    <div style="margin-bottom: 20px;">
      <span style="width: 100px;display: inline-block;font-size: 12px;">告警通知名称</span>
      <div style="display: inline-block;">
        <el-input clearable v-model='inputNotificationRulesName' maxlength="40" style="margin-right: 10px;width: 590px;"  v-if="!isDetail"></el-input>
        <span v-if="isDetail" style="font-size: 12px;">{{inputNotificationRulesName}}</span>
      </div>
    </div>
    <div style="margin-bottom: 20px;">
      <span style="width: 100px;display: inline-block;font-size: 12px;">告警通知方式</span>
      <div style="display: inline-block;">
        <el-checkbox-group v-model="checkedItems" @change="handleCheckedItemsChange">
          <el-checkbox style="margin-right: 60px;" :disabled="isDetail" v-for="item in checkboxNotificationRulesMethod" :label="item.value" :key="item.value">{{item.label}}</el-checkbox>
        </el-checkbox-group>
      </div>
    </div>
    <div style="height: 26px;">
      <span style="width: 140px;display: inline-block;font-size: 12px;line-height: 26px;">告警通知人员（{{tableData.length}}）</span>
      <div style="display: inline-block;float: right;"  v-if="!isDetail">
        <div style="display: inline-block;">
            <el-autocomplete
            popper-class="theme-dark"
            v-model="inputSearch"
            :fetch-suggestions="querySearch"
            placeholder="请输入账号名"
            :trigger-on-focus="false"
            @select="inputSearchSelect"
            style="margin-right: 7px;width: 300px;"
            :debounce=1000
            value-key="account"
          ></el-autocomplete>
        </div>
        <el-button @click="addFromSearch" >添加</el-button>
        <el-button @click="addFromOrganize" style="margin-left: 2px;">从组织架构添加</el-button>
      </div>
    </div>
    <!-- 表格区域 -->
    <div class="area-table" style="margin-top: 17px;">
      <el-table ref="tableMonitorAlarmNotificationSettings" tooltip-effect="dark"
                max-height="430"
                stripe
                border
                style="width: 100%;"
                :data="tableData"

      >
        <el-table-column show-overflow-tooltip type="index" label="序号" width="57">
        </el-table-column>
        <!--<el-table-column :reserve-selection="true" type="selection" width="30">-->
        <!--</el-table-column>-->
        <el-table-column show-overflow-tooltip prop="name" label="账号" width="140">
        </el-table-column>
        <el-table-column show-overflow-tooltip prop="email" label="邮箱" width="200">
        </el-table-column>
        <el-table-column show-overflow-tooltip prop="mobile" label="手机" width="112">
      </el-table-column>
        <el-table-column show-overflow-tooltip prop="moid" label="微信">
      </el-table-column >
        <el-table-column label="操作" v-if="!isDetail" width="53">
          <template slot-scope="scope">
            <button type="button" class="button-host-info" @click="delUser(scope.row)">
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
      title="添加终端"
      :visible.sync="dialogVisibleAddItem"
      width="1020px"
      append-to-body
      custom-class="notification-settings-dialog-child theme-dark"
      @closed="beforeCloseClearNode">
      <div style="margin-top: 20px;" v-if="!clearNode">
        <TheOrganizationTerminal ref="alarmNotificationTheOT"></TheOrganizationTerminal>
      </div>
      <div style="padding: 30px;text-align: center;box-sizing: border-box;">
          <span style="text-align: center;" >
            <el-button @click="addUser()">保 存</el-button>
            <el-button @click="dialogVisibleAddItem = false">取 消</el-button>
          </span>
      </div>
    </el-dialog>
    <!--蒙版区域end-->
	</div>
</template>

<script>
    export default {
      name: "MonitorAlarmNotificationSettings",
      components:{
        TheOrganizationTerminal: () => import('@/components/home/TheOrganizationTerminal.vue'),
      },
      props:{
        ruleData:null,
        isDetail:{
          type:Boolean,
          default:false,
        }
      },
			data(){
				return{
          dialogVisibleAddItem:false,

          // 选中的数据
          treeDataSelected:[],


          inputNotificationRulesName:'',
          checkedItems:[],

          checkboxNotificationRulesMethod:[
            {value:'email',
              label:'邮件通知'},
            {value:'sms',
              label:'短信通知'},
            {value:'wechat',
              label:'微信通知'},
          ],

          inputSearch:'',
          searchSelected:'',

          tableData:[],
          notificationRulesID:'',
          //  清除蒙版内节点
          clearNode:false,
				}
			},
      computed:{

      },
			methods:{
        handleCheckedItemsChange(value) {
          // console.log(value)
        },


        //蒙版内保存按钮点击函数
        addUser(){
          let tableDataList = this.tableData.map(item => item.moid).filter(item => item)
          // console.log(tableDataList)
          this.treeDataSelected=this.$refs.alarmNotificationTheOT.getSelectedData()
          let newData=this.treeDataSelected.filter(item => tableDataList.indexOf(item.moid) === -1  )
          // console.log(newData)
          this.dialogVisibleAddItem=false
          this.tableData.push(...newData)
        },
        delUser(rowData){

          const newItems = [...this.tableData]
          // console.log(newItems)
          const index = newItems.indexOf(rowData)
           newItems.splice(index, 1)
          this.tableData = newItems
        },
        // 从组织架构中添加按钮
        async addFromOrganize(){
          // this.allUserDomainInfo=await this.$api.homePage.getallUserDomainInfo()
          this.dialogVisibleAddItem=true
          this.clearNode=false

        },

        addFromSearch(){
          let tableDataList = this.tableData.map(item => item.moid).filter(item => item)
          if (this.searchSelected && tableDataList.indexOf(this.searchSelected.moid) === -1){
            this.searchSelected["name"]=this.searchSelected.account
            this.tableData.push(this.searchSelected)
          }
          // this.tableData.push(...newData)
        },
        inputSearchSelect(val){
          // console.log(val)
          this.searchSelected=val
        },

        async querySearch(queryString, cb){
          // console.log(queryString)
          let params = {
            key : queryString
          }
          let queryData = await this.$api.monitor.getSearchUserInfo(params)
          let showData = (queryData.map(item => item.info)).flat(1)
          cb(showData)
        },

        // API start
        async getAlarmNotificationRulesSingle(id){
          let rules = await this.$api.monitor.getAlarmNotificationRules(id)
          this.inputNotificationRulesName=rules.name
          this.checkedItems=rules.notice_method
          rules.persons.forEach(item => {
            item["mobile"]=item.phone
            item["moid"]=item.user_id
            item["name"]=item.user_name
          })
          this.tableData=rules.persons
        },
        // API end

        // dialog对于动态变化的数据需要在关闭前清除内容节点
        beforeCloseClearNode(){
          // console.log("close")
          this.clearNode=true
        },

        // 组件返回数据方法
        getBackData(){
          let backData = {
            name:this.inputNotificationRulesName,
            userList:this.tableData,
            noticeMethod:this.checkedItems,
          }
          if(this.ruleData && this.ruleData.id){
            backData["ruleID"]=this.ruleData.id
          }
          return backData
        },

        async init(){
          // console.log(this.ruleData)
          if(this.ruleData){

            this.getAlarmNotificationRulesSingle(this.ruleData.id)
          }
        },
			},
			mounted() {
        this.init()
			},

    }
</script>

<style >

</style>
