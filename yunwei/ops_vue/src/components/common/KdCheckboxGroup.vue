<template>
  <div class="kd-checkbox-group--frame theme-dark">
    <el-checkbox class="kd-checkbox-group--title" :indeterminate="isIndeterminate" v-model="checkAll" @change="handleCheckAllChange">{{title}}</el-checkbox>
    <span style="float: right;font-size: 12px;color: #5d6266;margin-top: 5px;">已选：{{checkedItems.length}}</span>
    <div class="kd-checkbox-group--border">
      <el-checkbox-group v-model="checkedItems" @change="handleCheckedItemsChange">
        <el-checkbox class="kd-checkbox-group--item" v-for="item in checkboxData" :label="item[checkboxProps.id]" :key="item[checkboxProps.id]">{{item[checkboxProps.label]}}</el-checkbox>
      </el-checkbox-group>
    </div>
  </div>
</template>

<script>
export default {
  name: "KdCheckboxGroup",
  props:{
    title:{
      type: String,
      default: 'title',
    },
    checkboxProps:{
      type: Object,
      default: {
        id: 'id',
        label: 'label',
        isChecked:'isChecked',
      }
    },
    checkboxData:Array,
    // checkedList:Array,
  },
  data() {
    return {
      checkAll: false,
      checkedItems: [],
      isIndeterminate: true,
    };
  },
  watch: {
    checkboxData:{
      deep:true,
      handler:function(newVal,oldVal){
        // this.checkData=newVal
        // console.log("监听变化：" + newVal)
        this.checkedItems=this.checkboxData.filter(item => item[this.checkboxProps.isChecked]).map(item => item[this.checkboxProps.id])
        this.checkedChange()
      }
    },
  },
  methods: {
    handleCheckAllChange(val) {
      // console.log(val)
      this.checkedItems = val ? this.checkboxData.map(item => item[this.checkboxProps.id]) : [];
      this.checkedChange()
    },
    handleCheckedItemsChange(value) {
      this.checkedItems=value
      this.checkedChange()
    },
    checkedChange(){
      let checkedCount = this.checkedItems.length;
      this.checkAll = checkedCount === this.checkboxData.length;
      this.isIndeterminate = checkedCount > 0 && checkedCount < this.checkboxData.length;
      this.$emit('checked-change',this.title,this.checkedItems);
    },
    init(){
      this.checkedItems=this.checkboxData.filter(item => item[this.checkboxProps.isChecked]).map(item => item[this.checkboxProps.id])
      // console.log("初始化：" + this.checkedItems)
      this.checkedChange()
    },
  },
  mounted(){
    this.init()
  },
}
</script>

<style>
.kd-checkbox-group--frame{
  background-color: #222526;
  width: 100%;
  box-sizing: border-box;
  padding: 8px 25px;

}
.kd-checkbox-group--title{
  color: #9ca9b1;
  margin-bottom: 8px;
}
.kd-checkbox-group--border{
  border: 1px solid #383b3c;
  background-color: #272c2e;
  box-sizing: border-box;
  padding: 11px 38px;
  max-height: 90px;
  overflow: auto;
}
.kd-checkbox-group--item{
  width: 50%;
  color: #9ca9b1;
  line-height: 24px;
}
</style>
