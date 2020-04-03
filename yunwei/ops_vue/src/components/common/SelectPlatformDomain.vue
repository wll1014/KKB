<template>
  <div class="component-select-platform-domain">
    <el-select popper-class="theme-dark"
               v-model="optionSelectedPlatformDomain"
               @change="handleChangePlatform"
               placeholder="请选择平台域">
      <el-option
        v-for="item in optionsPlatformDomain"
        :key="item.moid"
        :label="item.name"
        :value="item.moid"
      >
      </el-option>
    </el-select>
    <el-select popper-class="theme-dark"
               v-model="optionSelectedMachineRoom"
               @change="handleChangeMachineRoom"
               v-if="showSelectMachineRoom"
               placeholder="请选择机房">
      <el-option
        v-for="item in optionsMachineRoom"
        :key="item.moid"
        :label="item.name"
        :value="item.moid"
      >
      </el-option>
    </el-select>
  </div>
</template>

<script>
  export default {
    name: "SelectPlatformDomain",
    props: {
      hasOptionAll: {   //是否有全部平台域的选项
        type: Boolean,
        default: false,
      },
      selectedMoidPlatform: {  //默认选中的选项，默认：当hasOptionAll为true时，默认为all；其余的为第一个域的moid
        type: String,
        default: null,
      },
      filterDomainType: {  //对下拉选项做domain_type
        type: [String, Number],
        default: null,
      },

      showSelectMachineRoom: {  //是否显示机房的select
        type: Boolean,
        default: false,
      },
      selectedMoidMachineRoom: {
        type: String,
        default: null,
      },
    },
    data() {
      return {
        optionsPlatformDomain: [],
        optionSelectedPlatformDomain: '',

        optionsMachineRoom: [],
        optionSelectedMachineRoom: '',
      };
    },
    methods: {
      // emit
      change() {
        let ev = {
          domainMoid: this.optionSelectedPlatformDomain,
          roomMoid: this.optionSelectedMachineRoom,
          domainList: this.optionsPlatformDomain,
          roomList: this.optionsMachineRoom
        }
        this.$emit("change", ev)
      },
      loadSelectedOption() {
        let ev = {
          domainMoid: this.optionSelectedPlatformDomain,
          roomMoid: this.optionSelectedMachineRoom,
          domainList: this.optionsPlatformDomain,
          roomList: this.optionsMachineRoom
        }
        this.$emit("loadSelectedOption", ev)
      },
      // emit end

      // 下拉选择函数
      async handleChangePlatform(val) {
        if (this.showSelectMachineRoom) {
          await this.setOptionsMachineRoom(val)
        }
        this.change()
      },

      handleChangeMachineRoom(val) {
        this.change()
      },
      // 下拉选择函数 end

      //重新初始化
      reload() {
        this.setOptionsPlatform()
      },

      async setOptionsPlatform(defaultDomainMoid = null,defaultMachineRoom = null) {
        this.optionsPlatformDomain = []
        if (this.hasOptionAll) {
          let optionAll = {
            name: '全部平台域',
            moid: 'all'
          }
          this.optionsPlatformDomain.push(optionAll)
        }

        let platformDomainList = await this.$api.globalData.allPlatformDomain()

        if (this.filterDomainType || this.filterDomainType === 0) {
          platformDomainList = platformDomainList.filter(i => i.domain_type === this.filterDomainType)
        }

        this.optionSelectedPlatformDomain = defaultDomainMoid ? defaultDomainMoid :
          this.hasOptionAll ? 'all' : platformDomainList[0].moid

        this.optionsPlatformDomain = this.optionsPlatformDomain.concat(platformDomainList)

        if (this.showSelectMachineRoom) {
          await this.setOptionsMachineRoom(this.optionSelectedPlatformDomain,defaultMachineRoom)
        }
        this.loadSelectedOption()
      },

      async setOptionsMachineRoom(domainMoid,defaultMachineRoom = null) {

        this.optionsMachineRoom = []
        let machineRoomList = [{
          name: '全部机房',
          moid: 'all'
        }]
        if (domainMoid !== 'all') machineRoomList = await this.$api.homePage.getMachineRoomInfo(domainMoid)

        this.optionsMachineRoom = machineRoomList

        this.optionSelectedMachineRoom = defaultMachineRoom ?  defaultMachineRoom : this.optionsMachineRoom[0] ? this.optionsMachineRoom[0].moid : ''
      },
    },
    mounted() {
      this.setOptionsPlatform(this.selectedMoidPlatform,this.selectedMoidMachineRoom)
    },
  }
</script>

<style scoped>
  .component-select-platform-domain {
    display: inline-block;
  }

  .component-select-platform-domain > .el-select:nth-child(2) {
    margin-left: 7px;
  }
</style>
