<template>
  <div class="component-select-time-range">
    <el-select @change="selectDataChange"
               popper-class="theme-dark"
               v-model="optionSelectedTimeRange"
               placeholder="请选择"
               style="width: 120px;margin-right: 7px;">
      <el-option
        v-for="item in optionsTimeRange" :key="item.label" :label="item.label" :value="item.value">
      </el-option>
    </el-select>
    <el-date-picker
      style="width: 322px;margin-right: 7px;vertical-align: top;"
      v-model="datePickerTimeRange"
      type="datetimerange"
      start-placeholder="开始日期"
      end-placeholder="结束日期"
      popper-class="theme-dark"
      value-format="timestamp"
      @focus="recoderDatePicker(datePickerTimeRange)"
      @blur="judgeDatePickerChange(datePickerTimeRange)"
      format="yyyy-MM-dd HH:mm"
      :default-time="['00:00:00', '23:59:00']"
      range-separator=""
      class="clear-close-icon"
      prefix-icon="ops-icons-bg icon-calendar"
      :clearable=false
    >
    </el-date-picker>
  </div>
</template>

<script>
  export default {
    props: {
      defaultSelect: {
        type: [String, Number],
        default: 3600000
      },
      timeRangeList: {
        type: Array,
        default: [
          {label: "最近 30分钟", value: 1800000, timerInterver: 30},
          {label: "最近 1小时", value: 3600000, timerInterver: 30},
          {label: "最近 5小时", value: 18000000, timerInterver: 30},
          {label: "最近 一天", value: 86400000, timerInterver: 30},
          {label: "最近 一周", value: 604800000, timerInterver: 30},
          {label: "最近 30天", value: 2592000000, timerInterver: 30},
        ]
      },
      hasTimer: {
        type: Boolean,
        default: true
      },
    },
    data() {
      return {
        timer: null,

        optionsTimeRange: [],
        optionSelectedTimeRange: '',

        datePickerTimeRange: null,

        // 记录上一次时间的选择
        frontDatePickerTimeRange: null,
      };
    },
    methods: {
      // emit
      change(timrRange = null) {
        console.log(this.datePickerTimeRange)
        let ev = {
          select: this.optionSelectedTimeRange,
          dateRange: timrRange || this.datePickerTimeRange,
        }
        this.$emit("change", ev)
      },

      // 对外提供的方法
      // 回到默认配置（不触发emit）
      defaultReset() {
        this.optionSelectedTimeRange = this.defaultSelect
        this.triggerDataChange(this.optionSelectedTimeRange, false)
      },
      // 对外提供的方法 end
      // 加载成功时的默认选择
      loadSelectedOption() {
        let ev = {
          select: this.optionSelectedTimeRange,
          dateRange: this.datePickerTimeRange,
        }
        this.$emit("loadSelectedOption", ev)
      },
      // emit end

      // 选择器函数
      selectDataChange(val) {
        this.triggerDataChange(val)
      },

      //当左侧选择时间变化，触发相关定时器和右侧时间的变化
      triggerDataChange(val, isEmit = true) {
        let vfind = this.optionsTimeRange.find(i => i.value === val)
        let timestamp = new Date().setSeconds(0,0);
        this.datePickerTimeRange = val === "custom" ? null : [timestamp - val, timestamp]

        if (this.hasTimer && vfind.timerInterver) {
          this.setTimer(val, vfind.timerInterver)
        } else {
          this.clearTimer()
        }
        if (isEmit) this.change()
      },

      // 选中时间组件时判断时间是否有改变，若改变下拉框改为“自定义”
      recoderDatePicker(val) {
        this.frontDatePickerTimeRange = val
      },
      judgeDatePickerChange(val) {
        if (this.frontDatePickerTimeRange !== this.datePickerTimeRange) {
          this.optionSelectedTimeRange = "custom"
          this.change()
          this.clearTimer()
        }
      },

      // 定时器
      setTimer(range = 3600000, iTime) {
        this.clearTimer();
        this.timer = setInterval(() => {
          let timestamp = new Date().setSeconds(0,0);
          this.change([timestamp - range, timestamp])
        }, Number(iTime) * 1000)
      },
      // 清楚定时器
      clearTimer() {
        clearInterval(this.timer);
        this.timer = null;
      },

      init() {
        this.optionsTimeRange = [{label: "自定义", value: 'custom'}]
        this.optionsTimeRange = this.optionsTimeRange.concat(this.timeRangeList)
        this.optionSelectedTimeRange = this.defaultSelect
        this.triggerDataChange(this.optionSelectedTimeRange)
        this.loadSelectedOption()
      },
    },
    mounted() {
      this.init()
    },
    beforeDestroy() {
      this.clearTimer()
    },
  }
</script>

<style>
  .component-select-time-range {
    display: inline-block;
  }
</style>
