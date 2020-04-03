<template>
  <div class="pagination-class">
    <p class="pagination--total" style="">当前共有  {{total}}  条记录</p>
    <el-input
    :disabled="disabled"
    v-model="currentPageNumber" 
    style="width:40px;text-align: center;"
    @blur="currentChange(currentPageNumber)"
    @keyup.enter.native="currentChange(currentPageNumber)"></el-input>
    <p class="pagination--numbersplit" style="">/</p>
    <p style="display: inline;margin-right: 10px;">{{ totalPageNumber }}</p>
    <el-button :disabled="disabled" icon="el-icon-arrow-left" @click="currentChange(currentPageNumber-1)" style="padding: 6px;margin-right: -3px;"></el-button>
    <el-button :disabled="disabled" icon="el-icon-arrow-right" @click="currentChange(currentPageNumber+1)" style="padding: 6px;margin-left: 1px;"></el-button>
  </div>
</template>

<script>
  export default{
    props:{
      currentPage:Number,
      total:Number,
      pageSize:Number,
      disabled:Boolean,
    },
    data() {
    	return {
        currentPageNumber:this.currentPage,

        timeOutTimer:null, //防止连续触发
      }
    },
    watch: {
      currentPage: function (newVal,oldVal) {
        // console.log("分页变化："+ newVal)
        this.currentPageNumber = newVal
      },
      // currentPageNumber: function (newVal,oldVal) {
      //   this.$emit("update:currentPage",parseInt(newVal))
      // },
    },
    computed: {
    // 计算属性的 getter
      totalPageNumber: function () {
        return Math.ceil(this.total/this.pageSize) > 0 ? Math.ceil(this.total/this.pageSize) : 1
      },
      // currentPageNumber: function () {
      //   return this.currentPage
      // },
    },
    methods: {
      currentChange(pageNumber){
        pageNumber=parseInt(pageNumber)
        if(pageNumber){
          if(pageNumber<0){
            this.currentPageNumber=1
          }
          else if(pageNumber>this.totalPageNumber && this.totalPageNumber!==0){
            this.currentPageNumber=this.totalPageNumber
          }
          else{
            this.currentPageNumber=pageNumber
          }
          // if(this.currentPageNumber!=this.currentPage){
          // }
          // console.log(this.currentPageNumber)
        }
        else{
          this.currentPageNumber=1
        }

        if(this.timeOutTimer){
          clearTimeout(this.timeOutTimer);
        }
        this.timeOutTimer = setTimeout(()=>{
          this.$emit('current-change',this.currentPageNumber);
        }, 300);
      }
    },
      
  }
</script>

<style>
.pagination-class{
   /*height: 39px;*/
  position: relative;
  text-align: right;
  vertical-align: top;
  font-size: 12px;
  color: #9ca9b1;
}
.pagination-class .el-input__inner{
  text-align: center;
  padding: 0 10px;
}
.pagination--total{
  display: inline;
  margin-right: 20px;
  font-size: 12px;
  color: #9ca9b1;
}
.pagination--numbersplit{
  display: inline;
  margin:0px 3px 0px 7px;
  font-size: 12px;
  color: #9ca9b1;
}
</style>
