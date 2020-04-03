<template>
  <div class='page-monitor-alarm-notification  theme-dark'>
    <div style="position: absolute;  top:-35px;  right: 20px;">
      <el-button @click="addNotificationRules">新增</el-button>
    </div>
    <div v-if="!hasRules">
      <div style="position: absolute;  top:280px;width: 100%;text-align: center;">
        <span style="margin-right: 7px;font-size: 14px;">
          <i class="ops-icons-bg icon-notice" style="vertical-align: bottom;"></i>
        </span>
        <span>尚无告警通知规则，请先</span>
        <span style="color: #299dff;text-decoration:underline;cursor: pointer;"
              @click="addNotificationRules">新增告警通知规则</span>
      </div>
    </div>
    <div v-if="hasRules">
      <div class="monitor-alarm-notification-content" style="box-sizing: border-box;">
        <el-row style="margin-bottom: 20px;" :gutter="20" v-for="item in rowNumber" :key="item">
          <el-col :span="8" v-for="i,index in listRules[item-1]" :key="i.id">
            <div class="block-notification" style="">
              <div class="area-notification--button">
                <button style="margin-left: 7px;" type="button" class="ops-button-text"
                        @click="handleNotificationRules('edit',i)">
                  <span style="">编辑</span>
                </button>
                <button style="margin-left: 7px;" type="button" class="ops-button-text"
                        @click="handleNotificationRules('detail',i)">
                  <span style="">详情</span>
                </button>
                <button style="margin-left: 7px;" type="button" class="ops-button-text"
                        @click="handleNotificationRules('del',i)">
                  <span style="">删除</span>
                </button>
              </div>
              <div class="area-notification--title">{{i.name}}</div>
              <div class="area-notification--content">
                <div class="area-notification--item">通知人员</div>
                <el-tooltip :content="i.persons.join(' , ')" placement="bottom-start" effect="dark">
                  <div class="area-notification--item-right">{{i.persons.join(" , ")}}</div>
                </el-tooltip>
              </div>
              <div class="area-notification--content" style="height: 24px;">
                <div class="area-notification--item">通知方式</div>
                <div class="area-notification--item-right" style="height: 24px;">{{i.cn_notice_method.join(" , ")}}
                </div>
              </div>
              <div class="area-notification--content">
                <div class="area-notification--item">告警项</div>
                <div class="area-notification--item-right" style="height:90px;">
                  <!-- 去掉其他选项
                                  *  <div>
                      <span>其他</span>
                      <span>已选  {{i.sub_codes.other.length}}</span>
                    </div>
                                  *  -->

                  <div>
                    <span>MCU告警</span>
                    <span>已选  {{i.sub_codes.mcu.length}}</span>
                  </div>
                  <div>
                    <span>服务器设备告警</span>
                    <span>已选  {{i.sub_codes.server.length}}</span>
                  </div>
                  <div>
                    <span>终端设备告警</span>
                    <span>已选  {{i.sub_codes.terminal.length}}</span>
                  </div>
                </div>
              </div>
            </div>
          </el-col>
        </el-row>

      </div>
    </div>
    <!--蒙版区域start-->
    <!--添加规则-->
    <el-dialog
      title="告警通知规则"
      :visible.sync="dialogVisibleAddRule"
      width="800px"
      @closed="beforeCloseClearNode()">
      <div style="margin-top: 10px;font-size: 14px;color: #9ca9b1;">
        <KdTabCommon :tab-list="tabList" :active-tab="activeTab" class-name="tab-alarm" @tab-change="tabChange"
                     style="margin-left: 25px;"></KdTabCommon>
        <div style="" v-if="!clearNode">
          <MonitorAlarmNotificationSettings v-show="activeTab === 'NotificationPeople'" ref="alarmNotificationSetting"
                                            :ruleData="activeRuleData"
                                            :isDetail="isDetail"></MonitorAlarmNotificationSettings>
          <MonitorAlarmSubscriptionSettings v-show="activeTab === 'NotificationNode'" ref="alarmNotification"
                                            :isSubSetting=false :checkedCodes="checkedCodes"
                                            :isDetail="isDetail"></MonitorAlarmSubscriptionSettings>
        </div>
        <div style="padding: 30px;text-align: center;box-sizing: border-box;">
            <span style="text-align: center;">
              <el-button @click="saveNotificationRules">保 存</el-button>
              <el-button @click="dialogVisibleAddRule = false">取 消</el-button>
            </span>
        </div>
      </div>
    </el-dialog>

    <!--删除二次确认-->
    <el-dialog title="提示" :visible.sync="delVisible" width="300px" top="15%">
      <div style="margin-top: 40px;margin-bottom: 20px;margin-left: 20px">
        <span style="margin-right: 7px;font-size: 14px;">
          <i class="ops-icons-bg icon-notice" style="vertical-align: bottom;"></i>
        </span>
        <span>确定删除所选告警通知规则吗？</span>
      </div>
      <div align='center' slot='footer' class='theme-dark' style='margin-top:10px;padding-bottom: 10px'>
        <el-button type="info" @click="handleNotificationRules('delConfirm',delConfirmRule)">确 定</el-button>
        <el-button @click="delVisible = false">取 消</el-button>
      </div>
    </el-dialog>
    <!--蒙版区域end-->
  </div>
</template>

<script>
  export default {
    name: "MonitorAlarmNotification",
    components: {
      KdTabCommon: () => import('@/components/common/KdTabCommon.vue'),

      // MonitorAlarmNotificationor: () => import('@/view/monitor/MonitorAlarmNotification/MonitorAlarmNotificationor.vue'),
      // MonitorAlarmNotificationProject: () => import('@/view/monitor/MonitorAlarmNotification/MonitorAlarmNotificationProject.vue'),
      MonitorAlarmNotificationSettings: () => import('@/view/monitor/MonitorAlarmNotificationSettings.vue'),
      MonitorAlarmSubscriptionSettings: () => import('@/view/monitor/MonitorAlarmSubscriptionSettings.vue'),
    },
    data() {
      return {
        hasRules: true,
        clearNode: false,
        isDetail: false,
        handleRulesMethod: '',

        activeTab: 'NotificationPeople',
        tabList: [['NotificationPeople', '通知人员'],
          ['NotificationNode', '告警项'],],

        rowNumber: '',
        listRules: [],
        checkedCodes: [],
        activeRuleData: '',

        dialogVisibleAddRule: false,
        delVisible: false,
        delConfirmRule: null,
      }
    },
    computed: {},
    methods: {
      tabChange(val) {
        this.activeTab = val
      },

      // 新增规则按钮
      addNotificationRules() {
        this.checkedCodes = []
        this.activeRuleData = ''
        this.dialogVisibleAddRule = true
        this.clearNode = false

      },
      // dialog对于动态变化的数据需要在关闭前清除内容节点
      beforeCloseClearNode() {
        // console.log("close")
        this.isDetail = false
        this.clearNode = true
      },

      saveNotificationRules() {
        if (!this.isDetail) {
          let codes = this.$refs.alarmNotification.getCheckedAlarmCodes()
          let settings = this.$refs.alarmNotificationSetting.getBackData()
          let subCodes = []
          for (let key in codes) {
            subCodes.push(codes[key])
          }
          subCodes = subCodes.flat(1)
          let params = {
            name: settings.name,
            persons: settings.userList.map(item => item.moid),
            sub_codes: subCodes,
            notice_method: settings.noticeMethod
          }
          if (params.name.length === 0) {
            this.$msgbox({
              title: '添加失败',
              message: '“告警通知名称”不能为空',
              type: 'error',
              customClass: 'temp',
              showConfirmButton: false
            })
            return false
          }
          if (params.persons.length === 0) {
            this.$msgbox({
              title: '添加失败',
              message: '“告警通知人员”不能为空',
              type: 'error',
              customClass: 'temp',
              showConfirmButton: false
            })
            return false
          }
          if (settings.ruleID) { //如果是编辑页面
            this.$api.monitor.putEditAlarmNotificationRules(settings.ruleID, params)
              .then(res => {
                if (res.data.success) {
                  this.getAlarmNotificationRules()
                }
              })
          } else {
            this.$api.monitor.postAddAlarmNotificationRules(params)
              .then(res => {
                if (res.data.success) {
                  this.getAlarmNotificationRules()
                }
              })
              .catch(err => {
                // console.log(err)
                let errInfo = err.data.non_field_errors.join(',')
                this.$msgbox({
                  title: '添加失败',
                  message: errInfo,
                  type: 'error',
                  customClass: 'temp',
                  showConfirmButton: false
                })
              })
          }
        }
        this.dialogVisibleAddRule = false
      },

      handleNotificationRules(method, item) {
        let params = {}
        let subCodes = Object.values(item.sub_codes).flat(1)
        // console.log(subCodes)
        if (method === 'edit') {
          this.checkedCodes = subCodes
          this.activeRuleData = item
          this.clearNode = false
          this.dialogVisibleAddRule = true
        }
        else if (method === 'detail') {
          this.checkedCodes = subCodes
          this.activeRuleData = item
          this.isDetail = true
          this.clearNode = false
          this.dialogVisibleAddRule = true
        }
        else if (method === 'del') {
          this.delVisible = true
          this.delConfirmRule = item
        }
        else if (method === "delConfirm") {
          params['ids'] = [item.id]
          this.$api.monitor.delAlarmNotificationRules(params)
            .then(res => {
              if (res.data.success) {
                this.$message.success("删除成功")
                this.getAlarmNotificationRules()
              }
            })
          this.delVisible = false
        }
      },
      // api start
      async getAlarmNotificationRules() {
        let rules = await this.$api.monitor.getAlarmNotificationRules()
        // console.log(rules)
        if (rules && rules.length !== 0) {
          let mapNotificationMethod = {
            "email": "邮件通知",
            "sms": "短信通知",
            "wechat": "微信通知",
          }
          rules.forEach((item) => {
            item["cn_notice_method"] = item.notice_method.map((item) => mapNotificationMethod[item])
            // console.log(item["cn_notice_method"])
          })
          // console.log(rules[0].cn_notice_method)
          this.hasRules = true

          let row = Math.ceil(rules.length / 3)
          this.rowNumber = row
          // let remainder = rules.length%3
          // console.log(row,remainder)
          this.listRules = []
          for (let i = 0; i < row; i++) {
            let start = i * 3
            let end = start + 3
            this.listRules.push(rules.slice(start, end))
          }
          // console.log(this.listRules)
        } else {
          this.hasRules = false
        }
      },
      // api end
      async init() {
        this.getAlarmNotificationRules()
      },
    },
    mounted() {
      this.init()
    },

  }
</script>

<style>
  .page-monitor-alarm-notification {
    position: relative;
  }

  .block-notification {
    height: 240px;
    background-color: #232629;
    position: relative;
    width: 100%;
    padding: 11px 20px;
    box-sizing: border-box;
    font-size: 12px;
    color: #9ca9b1;
  }

  .area-notification--title {
    font-size: 14px;
    color: #9ca9b1;
    margin-bottom: 4px;

  }

  .area-notification--button {
    position: absolute;
    top: 11px;
    right: 20px;
  }

  .area-notification--button .ops-button-text {
    font-size: 12px;
  }

  .area-notification--content {
    width: 100%;
    height: 42px;
    /*overflow: hidden;*/
    padding-top: 14px;
  }

  .area-notification--item {
    display: inline-block;
    vertical-align: top;
    cursor: pointer;
    text-overflow: ellipsis;
    overflow: hidden;
    line-height: 22px;
    color: #5d6266;
  }

  .area-notification--content .area-notification--item:first-child {
    width: 90px;
  }

  .area-notification--item-right {
    display: inline-block;
    width: calc(100% - 100px);
    height: 42px;
    vertical-align: top;
    text-overflow: ellipsis;
    overflow: hidden;
    cursor: pointer;
    line-height: 22px;
  }

  .area-notification--item-right span:first-child {
    display: inline-block;
    width: 120px;
  }

  .area-notification--item-right span:last-child {
    color: #5d6266;
  }
</style>
