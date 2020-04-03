<template>
  <div v-loading="wiresharkLoading"
       element-loading-text="正在结束抓包任务，生成文件中..."
       element-loading-spinner="el-icon-loading"
       element-loading-background="rgba(0, 0, 0, 0.5)">
    <div style="font-size: 14px;">自定义抓包</div>
    <div style="margin-top: 40px;">
      <span style="font-size: 12px;display: inline-block;width: 78px;">抓包对象</span>

      <el-select popper-class="theme-dark" v-model="optionSelectedWiresharkType" @change="selectWiresharkTypeChange"
                 style="width: 140px;">
        <el-option
          v-for="item in optionsWiresharkType" :key="item.value" :label="item.label" :value="item.value">
        </el-option>
      </el-select>

      <!--<el-button @click="dialogShowAddItem">{{ObjWiresharkType[optionSelectedWiresharkType].buttonLabel}}</el-button>-->
      <div class="selected-wireshark-object" @click="dialogShowAddItem">
        {{WiresharkObject?WiresharkObject.name:'请选择服务器或终端'}}
      </div>

      <div style="display: inline-block;" v-if="optionSelectedWiresharkType === 1">


        <el-select popper-class="theme-dark" v-model=" optionSelectedWiresharkNetwork"
                   :loading="loadingWiresharkNetwork" placeholder="请选择网口" style="width: 140px;margin-right: 7px;">
          <el-option
            v-for="item in optionsWiresharkNetwork" :key="item" :label="item" :value="item">
          </el-option>
        </el-select>

        <el-select popper-class="theme-dark" v-model=" optionSelectedWiresharkProtocol" placeholder="请选择协议"
                   style="width: 140px;margin-right: 7px;">
          <el-option
            v-for="item in optionsWiresharkProtocol" :key="item.value" :label="item.label" :value="item.value">
          </el-option>
        </el-select>

        <el-input style="width: 300px;margin-right: 17px;" v-model="_inputPort" @blur="blurInputPort"
                  placeholder="请输入端口，多个端口用英文逗号 ',' 分隔" maxlength="100" clearable></el-input>
      </div>
      <el-button circle @click='addToTask' icon="ops-icons-bg icon-circle-plus"
                 style="vertical-align: bottom;"></el-button>

      <div style="color: #ff6666;margin-top: 10px;font-size: 12px;" v-if="errorInfo">{{errorInfo}}</div>
    </div>

    <div style="margin-top: 20px;">
      <span style="font-size: 12px;display: inline-block;width: 78px;">时间</span>
      <el-input style="width: 140px;margin-right: 7px;" v-model="_inputTimeOut" placeholder="时间限制最大900秒"
                @blur="blurInputTimeOut"></el-input>
      <span style="font-size: 12px;display: inline-block;">秒</span>
    </div>

    <div style="margin-top: 20px;width: 100%;font-size: 0px;">
      <span style="font-size: 12px;display: inline-block;width: 20%;">抓包列表</span>
      <span style="font-size: 12px;display: inline-block;width: 20%;">{{WiresharkStartTime}}</span>
      <span style="font-size: 12px;display: inline-block;width: 20%;">{{WiresharkDuration}}</span>
      <div style="display: inline-block;width: 40%;text-align: right;">
        <el-button @click="startOrEndTask" :disabled="buttonDisabledStartOrEndTask">{{lastTask.is_complete === 0 ?
          '结束抓包' : '开始抓包'}}
        </el-button>
        <el-button @click="downloadTcpdumpFile" :disabled="lastTask.is_complete !== 1">下载抓包文件</el-button>
        <el-button @click="dialogStartOrEmptyTaskItem('empty')" :disabled="lastTask.is_complete === 0">清空</el-button>
      </div>
    </div>

    <!-- 表格区域 -->
    <div class="area-table" style="margin-top: 20px;">
      <el-table tooltip-effect="dark"
                stripe
                :max-height="tableHeight"
                border
                empty-text="尚无抓包对象，请先添加抓包对象在进行抓包"
                style="width: 100%;"
                :data="tableData"
      >
        <el-table-column show-overflow-tooltip type="index" label="序号" width="48">
        </el-table-column>
        <el-table-column show-overflow-tooltip prop="name" label="抓包对象" width="393">
        </el-table-column>
        <el-table-column show-overflow-tooltip label="类型" width="170">
          <template slot-scope="scope">
            <span>{{ObjWiresharkType[scope.row.item_type].label}}</span>
          </template>
        </el-table-column>
        <el-table-column show-overflow-tooltip prop="card" label="网口" width="200">
          <template slot-scope="scope">
            <span>{{scope.row.card ? scope.row.card : '----'}}</span>
          </template>
        </el-table-column>
        <el-table-column show-overflow-tooltip prop="protocol" label="协议" width="164">
          <template slot-scope="scope">
            <span>{{scope.row.protocol ? scope.row.protocol : '----'}}</span>
          </template>
        </el-table-column>
        <el-table-column show-overflow-tooltip prop="ports" label="端口">
          <template slot-scope="scope">
            <span>{{scope.row.ports ? scope.row.ports : '----'}}</span>
          </template>
        </el-table-column>
        <el-table-column label="操作">
          <template slot-scope="scope">
            <button type="button" class="button-host-info" @click="editTaskItem(scope.row)"
                    v-if="scope.row.item_type === 1">
              <span style="text-decoration: underline;">编辑</span>
            </button>
            <button type="button" class="button-host-info" @click="delCustomCaptureTaskItem(scope.row.id)">
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
      :title="ObjWiresharkType[optionSelectedWiresharkType].dialogLabel"
      :visible.sync="dialogVisibleAddItem"
      width="1020px"
      append-to-body
      custom-class="theme-dark"
      @closed="dialogCloseClearAddItem">
      <div style="position: absolute;top:15px;right: 60px;z-index: 100;">
          <span style="margin-right: 7px;font-size: 14px;">
            <i class="ops-icons-bg icon-notice" style="vertical-align: bottom;"></i>
          </span>
        <span style="font-size: 12px;color: #5d6266;">只能选择一个，已选列表第一个为抓包对象</span>
      </div>
      <div style="margin-top: 20px;" v-if="!dialogClearNodeAddItem">
        <!--<kdDialogSingleTree :defaultExpandList="nodeExpend" :loadNode="loadNode" :treeProps="treeProps" :treeData="allUserDomainInfo" @data-change="treeDataChange" @search="treeFilterSearch"></kdDialogSingleTree>-->
        <TheOrganizationTerminal ref="IntelligentWiresharkTheOT"
                                 v-if="optionSelectedWiresharkType === 2"></TheOrganizationTerminal>
        <TheOrganizationDevice ref="IntelligentWiresharkTheOD" :customParams="{device_type:0}"
                               v-if="optionSelectedWiresharkType === 1"></TheOrganizationDevice>
      </div>
      <div style="padding: 30px;text-align: center;box-sizing: border-box;">
          <span style="text-align: center;">
            <el-button @click="addFromOrganization()">保 存</el-button>
            <el-button @click="dialogVisibleAddItem = false">取 消</el-button>
          </span>
      </div>
    </el-dialog>
    <!--添加终端end-->

    <!--编辑提示类蒙版-->
    <el-dialog
      title="提示"
      :visible.sync="dialogVisibleTaskItem"
      width="500px"
      append-to-body
      custom-class="theme-dark"
      @closed="closeDialogTaskItem"
    >
      <div v-if="dialogShowContent==='edit'" style="width: 100%;text-align: center;margin-top: 15px;"
           class="dialog-wireshark-edit">
        <div>
          <span>抓包对象</span>
          <span style="display: inline-block;width: 300px;text-align: left;">{{dialogEditItem.name}}</span>
        </div>
        <div>
          <span>网口</span>
          <el-select popper-class="theme-dark" v-model="dialogOptionSelectedWiresharkNetwork"
                     :loading="loadingWiresharkNetwork" placeholder="请选择网口" style="width: 300px;">
            <el-option
              v-for="item in dialogOptionsWiresharkNetwork" :key="item" :label="item" :value="item">
            </el-option>
          </el-select>
        </div>
        <div>
          <span>协议</span>
          <el-select popper-class="theme-dark" v-model=" optionSelectedWiresharkProtocol" placeholder="请选择协议"
                     style="width: 300px;">
            <el-option
              v-for="item in optionsWiresharkProtocol" :key="item.value" :label="item.label" :value="item.value">
            </el-option>
          </el-select>
        </div>
        <div>
          <span>端口</span>
          <el-input style="width: 300px;" v-model="_inputPort" @blur="blurInputPort"
                    placeholder="请输入端口，多个端口用英文逗号 ',' 分隔" maxlength="100" clearable></el-input>
        </div>
      </div>
      <div v-if="dialogShowContent==='start'" style="width: 100%;text-align: center;margin-top: 15px;"
           class="dialog-wireshark-start">
          <span style="margin-right: 7px;font-size: 14px;">
            <i class="ops-icons-bg icon-notice" style="vertical-align: bottom;"></i>
          </span>
        <span>已存在抓包文件，继续抓包将进行覆盖，是否继续进行抓包？</span>
      </div>
      <div v-if="dialogShowContent==='empty'" style="width: 100%;text-align: center;margin-top: 15px;"
           class="dialog-wireshark-empty">
          <span style="margin-right: 7px;font-size: 14px;">
            <i class="ops-icons-bg icon-notice" style="vertical-align: bottom;"></i>
          </span>
        <span>确定清空列表及抓包文件？</span>
      </div>
      <div style="padding: 30px;text-align: center;box-sizing: border-box;">
          <span style="text-align: center;">
            <el-button @click="dialogDeterminebutton" v-if="dialogShowContent==='start' || dialogShowContent==='empty'">确 定</el-button>
            <el-button @click="editCustomCaptureTaskItem" v-if="dialogShowContent==='edit'">确 定</el-button>
            <el-button @click="closeDialogTaskItem">取 消</el-button>
          </span>
      </div>
    </el-dialog>
    <!--蒙版区域end-->
  </div>
</template>

<script>
  export default {
    name: "IntelligentWiresharkCustom",
    components: {
      KdPagination: () => import('@/components/common/KdPagination.vue'),
      TheOrganizationTerminal: () => import('@/components/home/TheOrganizationTerminal.vue'),
      TheOrganizationDevice: () => import('@/components/home/TheOrganizationDevice.vue'),

    },
    data() {
      return {
        wiresharkLoading: false,  // 主要用于结束抓包后的延迟
        optionSelectedWiresharkType: 1,
        optionsWiresharkType: [
          {
            label: '服务器',
            value: 1
          }, {
            label: '终端',
            value: 2
          }
        ],
        ObjWiresharkType: {
          1: {
            buttonLabel: '选择服务器',
            dialogLabel: '添加服务器',
            label: '服务器'
          },
          2: {
            buttonLabel: '选择终端',
            dialogLabel: '添加终端',
            label: '终端'
          }
        },

        optionSelectedWiresharkNetwork: null,
        optionsWiresharkNetwork: [],
        loadingWiresharkNetwork: false,

        optionSelectedWiresharkProtocol: 'all',
        optionsWiresharkProtocol: [{
          label: '全部',
          value: 'all'
        }, {
          label: 'tcp协议',
          value: 'tcp'
        }, {
          label: 'udp协议',
          value: 'udp'
        }
        ],

        inputPort: '',
        inputTimeOut: '60',

        taskID: null,
        taskComplete: null,

        buttonDisabledStartOrEndTask: false, // 开始或结束按钮的disabled状态
        // 当前选中的数据(抓包对象)
        WiresharkObject: null,
        // 添加对象时的错误提示
        errorInfo: null,

        lastTask: {},
        // 表格数据
        tableData: [],

        // 蒙版数据 start
        // 添加终端或服务器的蒙版数据 start
        dialogVisibleAddItem: false,
        dialogClearNodeAddItem: true,
        // 添加终端或服务器的蒙版数据 end

        // 编辑提示类蒙版
        dialogShowContent: null,
        dialogVisibleTaskItem: false,
        dialogEditItem: {},
        dialogOptionSelectedWiresharkNetwork: null,
        dialogOptionsWiresharkNetwork: [],
        // 蒙版数据 end
      }
    },
    computed: {
      _inputPort: {
        set: function (value) {
          this.inputPort = value;
        },
        get: function () {
          return this.inputPort.replace(/[^0-9,]+/g, '')
          // return temp.split(',').filter(i=>i).join(',')
        }
      },
      _inputTimeOut: {
        set: function (value) {
          this.inputTimeOut = value;
        },
        get: function () {
          let temp = this.inputTimeOut.replace(/[^0-9]+/g, '')
          // if(!temp) temp = '60'
          return parseInt(temp) > 900 ? '900' : parseInt(temp) <= 1 ? '1' : temp
        }
      },
      WiresharkStartTime() {
        if (this.lastTask.start_time && this.lastTask.is_complete !== 3) return '开始时间：    ' + new Date(parseInt(this.lastTask.start_time)).format('Y-m-d H:i:s')
      },
      WiresharkDuration() {
        if (this.lastTask.is_complete === 0) {
          let time = parseInt((parseInt((new Date()).getTime()) - parseInt(this.lastTask.start_time)) / 1000)
          return '抓包中...'
        }
        else if (this.lastTask.is_complete === 1) {
          return '抓包文件已生成'
        }
        else {
          return ''
        }
      },
    },
    methods: {
      // 蒙版相关start
      // 添加终端或服务器的蒙版start
      // 显示蒙版
      dialogShowAddItem() {
        this.dialogClearNodeAddItem = false
        this.dialogVisibleAddItem = true
      },
      // 关闭回调
      dialogCloseClearAddItem() {
        this.dialogVisibleAddItem = false
        this.dialogClearNodeAddItem = true
      },
      // 点击保存
      addFromOrganization() {
        let treeDataSelected = this.optionSelectedWiresharkType === 1 ? this.$refs.IntelligentWiresharkTheOD.getSelectedData() : this.$refs.IntelligentWiresharkTheOT.getSelectedData()
        // console.log(treeDataSelected)
        this.WiresharkObject = treeDataSelected[0]
        this.dialogCloseClearAddItem()
        this.getDevNetworkCards(this.WiresharkObject.moid)
      },

      // 编辑的蒙版
      // 显示蒙版
      dialogStartOrEmptyTaskItem(act) {
        if (act == 'start') {
          this.dialogShowContent = "start"
        } else if (act == 'empty') {
          this.dialogShowContent = "empty"
        }
        this.dialogVisibleTaskItem = true
      },
      editTaskItem(row) {
        this.dialogEditItem = row
        this.dialogShowContent = "edit"
        this.dialogVisibleTaskItem = true

        this.getDevNetworkCards(row.moid)
        this.inputPort = this.dialogEditItem.ports
        this.optionSelectedWiresharkProtocol = this.dialogEditItem.protocol ? this.dialogEditItem.protocol : 'all'
      },
      // 关闭回调
      closeDialogTaskItem() {
        this.dialogVisibleTaskItem = false
        this.dialogShowContent = null
        this.dialogOptionSelectedWiresharkNetwork = null
        this.dialogOptionsWiresharkNetwork = []
        this.inputPort = ''
        this.optionSelectedWiresharkProtocol = 'all'
        this.dialogEditItem = {}
      },
      // 确定按钮
      dialogDeterminebutton() {
        if (this.dialogShowContent === "start") {
          this.startCustomCaptureTask()
        } else if (this.dialogShowContent === "empty") {
          this.emptyeCustomCaptureTask()
        }
        this.dialogVisibleTaskItem = false
      },
      // 添加终端或服务器的蒙版end
      // 蒙版相关end

      // 页面函数
      selectWiresharkTypeChange(val) {
        this.WiresharkObject = null
      },
      blurInputTimeOut() {
        if (!this._inputTimeOut) this._inputTimeOut = '60'
      },
      blurInputPort() {
        if (this._inputPort) this._inputPort = this._inputPort.split(',').filter(i => i).join(',')
      },
      async addToTask() {
        this.errorInfo = this.WiresharkObject ? null : '请先选择服务器或者终端'
        if (!this.errorInfo) {
          let params = {
            "moid": this.WiresharkObject.moid,
            "item_type": this.optionSelectedWiresharkType,
            "card": this.optionSelectedWiresharkNetwork && this.optionSelectedWiresharkNetwork !== '全部' ? this.optionSelectedWiresharkNetwork : '',
            "ports": this.inputPort,
            "protocol": this.optionSelectedWiresharkProtocol === 'all' ? '' : this.optionSelectedWiresharkProtocol
          }
          this.addCustomCaptureTaskItem(params)
        }
      },

      startOrEndTask() {
        if (this.lastTask.is_complete === 0) {
          this.wiresharkLoading = true
          this.endCustomCaptureTask()
        } else {
          if (this.tableData.length > 0) {
            if (this.lastTask.is_complete === 3) {
              this.startCustomCaptureTask()
            } else {
              this.dialogStartOrEmptyTaskItem('start')
            }
          } else {
            this.errorInfo = '请先添加服务器或者终端';
            return false
          }
        }
      },


      // 页面函数 end


      // api start
      // 首次进入页面请求最后一次任务
      async getCustomCaptureTask() {
        let params = {
          start: 0,
          count: 1,
        }
        let res = await this.$api.intelligentWireshark.getCustomCaptureTask(params)
        if (res.data.success) {
          let lastTask = res.data.data.info[0]
          // lastTask.length > 0 ?
          this.getCustomCaptureTaskInfo(lastTask.id)
        }
      },

      async getCustomCaptureTaskInfo(id) {
        let res = await this.$api.intelligentWireshark.getCustomCaptureTaskInfo(id)
        // console.log(res)
        this.lastTask = res.data.data
        this.tableData = this.lastTask.items
        if (this.lastTask.is_complete === 0) { // 未完成状态继续请求
          setTimeout(() => {
            this.getCustomCaptureTaskInfo(id)
          }, 2000)
        } else {
          this.wiresharkLoading = false
        }
      },

      getDevNetworkCards(moid) {
        this.loadingWiresharkNetwork = true
        this.$api.intelligentWireshark.getCaptureDevCards(moid)
          .then(res => {
            if (res.data.success) {
              let cards = res.data.data.cards
              cards.unshift('全部')
              if (this.dialogVisibleTaskItem) {
                this.dialogOptionsWiresharkNetwork = cards
                this.dialogOptionSelectedWiresharkNetwork = this.dialogEditItem.card ? this.dialogEditItem.card : '全部'
              } else {
                this.optionsWiresharkNetwork = cards
                this.optionSelectedWiresharkNetwork = '全部'
              }
            }
            this.loadingWiresharkNetwork = false
          })
      },

      addCustomCaptureTaskItem(params) {
        this.$api.intelligentWireshark.addCustomCaptureTaskItem(params)
          .then(res => {
            if (res.data.success) {
              this.getCustomCaptureTaskInfo(this.lastTask.id)
            } else {
              let errInfo = '操作失败，' + res.data.msg
              this.$message.error(errInfo)
            }
          });
      },

      editCustomCaptureTaskItem() {
        let id = this.dialogEditItem.id
        let params = {
          "moid": this.dialogEditItem.moid,
          "item_type": this.dialogEditItem.item_type,
          "card": this.dialogOptionSelectedWiresharkNetwork === '全部' ? '' : this.dialogOptionSelectedWiresharkNetwork,
          "ports": this.inputPort,
          "protocol": this.optionSelectedWiresharkProtocol === 'all' ? '' : this.optionSelectedWiresharkProtocol
        }
        this.$api.intelligentWireshark.editCustomCaptureTaskItem(id, params)
          .then(res => {
            if (res.data.success) {
              this.getCustomCaptureTaskInfo(this.lastTask.id)
              this.closeDialogTaskItem()
            }
          })
      },

      delCustomCaptureTaskItem(id) {
        this.$api.intelligentWireshark.deleteCustomCaptureTaskItem(id)
          .then(res => {
            this.getCustomCaptureTaskInfo(this.lastTask.id)
          })
      },

      // 清空抓包对象和文件
      emptyeCustomCaptureTask() {
        this.$api.intelligentWireshark.emptyeCustomCaptureTask()
          .then(res => {
            this.getCustomCaptureTaskInfo(this.lastTask.id)
          })
      },

      startCustomCaptureTask() {
        this.buttonDisabledStartOrEndTask = true
        let params = {
          start_time: new Date().getTime(),
          timeout: this.inputTimeOut ? this.inputTimeOut : '60'
        }
        this.$api.intelligentWireshark.putCustomCaptureTask(this.lastTask.id, params).then(res => {
          this.$api.intelligentWireshark.startCustomCaptureTask()
            .then(res => {
              this.buttonDisabledStartOrEndTask = false
              this.getCustomCaptureTaskInfo(this.lastTask.id)
            })
        })
      },

      endCustomCaptureTask() {
        this.$api.intelligentWireshark.endCustomCaptureTask()
          .then(res => {
            this.getCustomCaptureTaskInfo(this.lastTask.id)
          })
      },

      downloadTcpdumpFile() {
        // console.log(params)
        let id = this.lastTask.id
        const elink = document.createElement('a')
        // elink.download = "0512110000602.tar.gz"
        elink.style.display = 'none'
        elink.href = `/api/v1/ops/diagnose/download/?type=custom_capture&task_id=${id}`
        // elink.href = "/api/v1/ops/media/snapshot/0512110000602.tar.gz"
        document.body.appendChild(elink)
        elink.click()
        URL.revokeObjectURL(elink.href) // 释放URL 对象
        document.body.removeChild(elink)
      },
      // api end

      // 其他功能函数
      checkIdIsLegal(confID, mtID) {
        return true
      },
      // 其他功能函数 end

      init() {
        this.getCustomCaptureTask()
      },

    },
    mounted() {
      this.init()
    }
  }
</script>

<style scoped>
  .ani_dot {
    font-family: simsun;
  }

  :root .ani_dot { /* 这里使用Hack是因为IE6~IE8浏览器下， vertical-align解析不规范，值为bottom或其他会改变按钮的实际高度*/
    display: inline-block;
    width: 1.5em;
    vertical-align: bottom;
    overflow: hidden;
  }

  @-webkit-keyframes dot {
    0% {
      width: 0;
      margin-right: 1.5em;
    }
    33% {
      width: .5em;
      margin-right: 1em;
    }
    66% {
      width: 1em;
      margin-right: .5em;
    }
    100% {
      width: 1.5em;
      margin-right: 0;
    }
  }

  .ani_dot {
    -webkit-animation: dot 2s infinite step-start;
  }

  @keyframes dot {
    0% {
      width: 0;
      margin-right: 1.5em;
    }
    33% {
      width: .5em;
      margin-right: 1em;
    }
    66% {
      width: 1em;
      margin-right: .5em;
    }
    100% {
      width: 1.5em;
      margin-right: 0;
    }
  }

  .ani_dot {
    animation: dot 2s infinite step-start;
  }

  .selected-wireshark-object {
    width: 160px;
    display: inline-block;
    height: 24px;
    line-height: 24px;
    overflow: hidden;
    font-size: 12px;
    border: 1px solid #383b3c;
    vertical-align: bottom;
    padding: 0px 10px;
    margin-right: 7px;
    cursor: pointer;
  }

  .dialog-wireshark-edit > div {
    margin-bottom: 30px;
  }

  .dialog-wireshark-edit div span:first-child {
    width: 80px;
    display: inline-block;
    text-align: left;
  }
</style>
