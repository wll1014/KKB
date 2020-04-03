<template>
  <div class="host-info-sidebar">
    <div class="group-tree">
      <!-- 搜索栏 -->
      <el-select @change="platformChange"
                 v-model="selectedPlatformDomain"
                 popper-class="theme-dark"
                 placeholder="请选择平台域"
                 style="width: 100%;margin-bottom: 13px;">
        <el-option
          v-for="item in selectOptionPlatformDomain" :key="item.domain_moid" :label="item.domain_name"
          :value="item.domain_moid">
        </el-option>
      </el-select>
      <div class="el-tree-node is-focusable" v-for="roomitem in groupData" :key="roomitem.room_name">
        <div :class="['el-tree-node__content',{'is-active':selectedNode === roomitem}]"
             style="padding-left: 0px;position: relative;">
            <span
              :class="['el-tree-node__expand-icon','el-icon-caret-right',{'expanded':expandList.includes(roomitem.room_moid)}] "
              @click="treeNodeExpandClick(roomitem.room_moid)"></span>
          <div style="width: 100%;line-height:36px;" @click="treeNodeClick(roomitem,roomitem)">
            <span class="el-tree-node__label">{{roomitem.room_name}}</span>
            <span class="el-tree-node__label">({{roomitem.count}})</span>
          </div>
          <div style="position: absolute;right: 8px;" @click="dropdownSetGroup('groupAdd',roomitem)">
            <i class="ops-icons-bg icon-faq-group-add"></i>
          </div>
        </div>
        <el-collapse-transition>
          <div class="el-tree-node__children" v-show="expandList.includes(roomitem.room_moid)">
            <div :class="['el-tree-node__content',{'is-active':selectedNode === groupitem}]"
                 style="padding-left: 24px;" v-for="groupitem in roomitem.group">
              <div style="width: 100%;line-height:36px;"
                   @click="treeNodeClick(groupitem,roomitem)">
                <el-tooltip class="item" effect="dark" :content="groupitem.name" placement="top-start">
                  <span class="el-tree-node__label">{{groupitem.name}}</span>
                </el-tooltip>
                <span class="el-tree-node__label">({{groupitem.count}})</span>
              </div>
              <div style="position: absolute;right: 10px;" v-show="selectedNode === groupitem">
                <el-dropdown trigger="click" @command="dropdownSetGroup">
                        <span class="el-dropdown-link">
                          <i class="el-icon-arrow-down el-icon--right"></i>
                        </span>
                  <el-dropdown-menu class="theme-dark" slot="dropdown">
                    <el-dropdown-item command="groupEdit">重命名组</el-dropdown-item>
                    <el-dropdown-item command="groupDel">删除分组</el-dropdown-item>
                  </el-dropdown-menu>
                </el-dropdown>
              </div>
            </div>
          </div>
        </el-collapse-transition>
      </div>
    </div>

    <!-- 蒙版区域开始 -->
    <!-- 分组编辑蒙版 -->
    <el-dialog
      :title="groupDialogTitle[groupDialogstatus]"
      :visible.sync="groupDialogstatus"
      :modal-append-to-body=false
      width="400px"
      top="15%"
    >
      <div style="height: 90px;margin-top: 63px;text-align: center;">
        <span style="color: #9ca9b1;font-size: 14px;">{{groupDialogSpan[groupDialogstatus]}}</span>
        <el-input v-if="groupDialogstatus==='groupAdd' || groupDialogstatus==='groupEdit'"
                  style="width: 240px;margin-left: 20px;"
                  v-model="inputGroupName"
                  placeholder="请输入分组名称"
                  maxlength="20"></el-input>
      </div>
      <div style="padding: 10px 20px 20px;text-align: center;box-sizing: border-box;">
        <span style="text-align: center;">
          <el-button @click="handleGroup">确 定</el-button>
          <el-button @click="groupDialogstatus = false">取 消</el-button>
        </span>
      </div>
    </el-dialog>
    <!-- 蒙版区域结束 -->
  </div>
</template>

<script>
  export default {
    name: "TheHostInfoSidebar",
    components: {
      // SpanOverflowEllipsis: () => import('@/components/common/SpanOverflowEllipsis.vue'),
    },
    props: {
      domainMoid: String,
      roomMoid: String,
    },
    data() {
      return {
        // 域选择
        selectedPlatformDomain: '',
        selectOptionPlatformDomain: [],

        groupData: [],

        selectedNode: null,  // 侧边栏选中的项
        expandList: [],  // 侧边栏展开的项

        activeRoomData: null,  //当前选中节点所在的机房的数据

        groupDialogstatus: false,
        groupDialogTitle: {
          groupAdd: '添加分组',
          groupEdit: '重命名组',
          groupDel: '删除分组',
        },
        groupDialogSpan: {
          groupAdd: '分组名称',
          groupEdit: '新组名',
          groupDel: '删除所选分组，分组内所有服务器自动归入机房根目录',
        },
        groupAddRoomData: null,  // 添加分组所属的机房
        inputGroupName: null,
      }
    },
    methods: {
      // 侧边栏filter相关函数
      // 域下拉框选择
      async platformChange(val) {
        await this.setRoomAndGroup(val)
        this.emitFilterChange()
      },
      // 侧边栏expand图标点击  通过room_moid去设置
      treeNodeExpandClick(v) {
        let index = this.expandList.indexOf(v)
        if (index > -1) {
          this.expandList.splice(index, 1);
        } else {
          this.expandList.push(v)
        }
      },
      // 侧边栏 每一项单击 事件
      treeNodeClick(activeNode, activeFatherNode) {
        this.selectedNode = activeNode
        this.activeRoomData = activeFatherNode
        this.emitFilterChange()
      },

      // 分组相关函数
      // 分组蒙版操作函数
      dropdownSetGroup(command, extraInfo = null) {
        this.groupDialogstatus = command
        this.groupAddRoomData = extraInfo
      },
      // 分组增删改操作函数
      async handleGroup() {
        let recordeSelected = {...this.selectedNode}
        let recordeActiveRoomData = {...this.activeRoomData}
        let room_moid = null
        let group_id = null
        if (this.groupDialogstatus === 'groupAdd') {
          await this.addGroup(this.inputGroupName, this.groupAddRoomData.room_moid)
          if (recordeSelected.hasOwnProperty('room_moid')) {
            room_moid = recordeSelected.room_moid
          } else {
            room_moid = recordeActiveRoomData.room_moid
            group_id = recordeSelected.id
          }
        } else if (this.groupDialogstatus === 'groupEdit') {
          await this.editGroup(this.inputGroupName, this.selectedNode.id)
          room_moid = recordeActiveRoomData.room_moid
          group_id = recordeSelected.id
        } else if (this.groupDialogstatus === 'groupDel') {
          await this.delGroup(this.selectedNode.id)
          room_moid = recordeActiveRoomData.room_moid
        }
        this.groupDialogstatus = false
        await this.setRoomAndGroup(this.selectedPlatformDomain, room_moid, group_id)
        this.emitFilterChange()
      },
      async addGroup(name, id) {
        let params = {
          name: name,
          room_moid: id,
        }
        if (!id) this.$message.error('添加失败，未获取到机房moid')
        await this.$api.hostManageApi.addHostGroups(params)
          .then(res => {
            if (res.data.success) {
              this.$message.success('添加成功')
            }
            else {
              let errInfo = '添加失败，' + res.data.msg
              this.$message.error(errInfo)
            }
          })
      },
      async editGroup(name, id) {
        let params = {
          name: name,
        }
        this.$api.hostManageApi.editHostGroups(id, params)
          .then(res => {
            // console.log(res)
            if (res.data.success) {
              this.$message.success('重命名成功')
            } else {
              let errInfo = '重命名失败，' + res.data.msg
              this.$message.error(errInfo)
            }
          })
      },
      async delGroup(ids) {
        let params = {
          ids: [ids],
        }
        this.$api.hostManageApi.delHostGroups(params)
          .then(res => {
            if (res.data.success) {
              this.$message.success('删除成功')
            } else {
              let errInfo = '删除失败，' + res.data.msg
              this.$message.error(errInfo)
            }
          })
      },
      // 分组相关函数 end

      // 设置平台域
      async setPlatformDomain(defautDomain) {
        this.selectOptionPlatformDomain = await this.$api.hostManageApi.hostDomains()
        if (this.selectOptionPlatformDomain.length) {
          this.selectedPlatformDomain = defautDomain || this.selectOptionPlatformDomain[0].domain_moid
        }
      },
      // 设置机房和分组
      // params:域moid, 默认选中的机房, 默认选中的组
      async setRoomAndGroup(moid, defaultRoom, defaultGroup) {
        let params = {domain_moid: moid}
        let res = await this.$api.hostManageApi.hostGroups(params)
        this.groupData = res.info
        let defautSelect = defaultRoom && this.groupData.find(i => i.room_moid === defaultRoom)
        this.selectedNode = defautSelect || this.groupData[0]
        this.activeRoomData = defautSelect || this.groupData[0]
        if (defaultRoom && defaultGroup) {  // 如果有默认的机房和组，默认选中当前机房下的组
          this.selectedNode = this.activeRoomData.group.find(i => i.id === defaultGroup)
        }
      },
      async init() {
        await this.setPlatformDomain(this.domainMoid)
        await this.setRoomAndGroup(this.selectedPlatformDomain, this.roomMoid)
        this.emitFilterChange()
      },

      // 其他函数
      // emit 不同值
      emitFilterChange() {
        let ev = {
          domain_moid: this.selectedPlatformDomain || '',
          room_moid: this.activeRoomData ? this.activeRoomData.room_moid : '',
          group_id: this.selectedNode && this.selectedNode.hasOwnProperty('id') ? this.selectedNode.id : '',
          activeGroup: this.activeRoomData ? this.activeRoomData.group : []
        }
        this.$emit('change', ev)
      },

      // 对外提供的方法：刷新侧边栏
      async refresh(domain_moid, roomMoid, group_id) {
        await this.setPlatformDomain(domain_moid)
        await this.setRoomAndGroup(domain_moid, roomMoid, group_id)
      },
    },
    mounted() {
      this.init()
    },
  }
</script>

<style>

</style>
