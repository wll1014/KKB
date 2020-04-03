<template>
	<div class='theme-dark file-distribution-detail'>
    <div class="button-back" style="">
      <el-button icon="ops-icons-bg icon-arrow-circle-left" @click="back" circle></el-button>
    </div>
    <div class="area-file-distribution-detail">
      <div>文件分发详情</div>
      <div style="margin-top: 35px;">
        <span class="left">任务名称</span>
        <el-tooltip placement="top" :content="detailInfo.task_name">
          <span class="right">{{detailInfo.task_name}}</span>
        </el-tooltip>
        <span class="left">操作时间</span>
        <span class="right">{{new Date(detailInfo.create_time).format('Y m-d H:i')}}</span>
        <span class="left">操作人员</span>
        <span class="right">{{detailInfo.operator}}</span>
      </div>
      <div style="margin-top: 25px;margin-bottom: 35px;">
        <span class="left">源文件和大小</span>
        <el-tooltip placement="top" v-if="detailInfo.file">
          <div slot="content" >
            <div v-for="i in transFileInfo(detailInfo.file)" style="text-align: right;">
              <span style="text-align: right;display: inline-block;">{{i[0]}}</span>
              <span style="width: 80px;text-align: left;display: inline-block;"> : {{i[1]}}</span>
            </div>
          </div>
          <span class="right" style="cursor: pointer;">{{transFileInfo(detailInfo.file,0)}}{{transFileInfo(detailInfo.file).length > 1 ? ' ...':''}}</span>
        </el-tooltip>
        <span class="left">上传路径</span>
        <span class="right">{{detailInfo.remote_path}}</span>
      </div>
    </div>
    <!-- 表格展示 -->
    <div style="margin: 0px 40px;padding-top:20px;border-top: #3d4046 1px dashed">
      <el-table
        tooltip-effect="dark"
        stripe
        border
        style="width: 100%;"
        :data='tableDataDetail'>
        <el-table-column style='text-align: center;' min-width="53px" type='index' label="序号"></el-table-column>
        <el-table-column prop='name' min-width='171px' label="服务器名称" show-overflow-tooltip></el-table-column>
        <el-table-column prop='domain_name' min-width='171px' label="所属平台域" show-overflow-tooltip></el-table-column>
        <el-table-column prop='room_name' min-width='171px' label="所属机房" show-overflow-tooltip></el-table-column>
        <el-table-column  min-width='171px' label="发送状态" show-overflow-tooltip>
          <template slot-scope="scope">
            <span>{{objTaskStatu[scope.row.status]}}</span>
          </template>
        </el-table-column>
      </el-table>
    </div>

	</div>
</template>

<script>
	export default {
    components:{

    },
    props:{
      taskID:null,
    },
		data() {
			return {
			  detailInfo:{},
        tableDataDetail:[],

        objTaskStatu:{
          1:'正在执行',
          2:'执行成功',
          3:'执行失败',
        },
      }
		},
		methods:{
      // 其他函数
      // 转换fileinfo
      transFileInfo(l,index){
        if(l){
          let newl = l.map(item=>[item.filename,Math.ceil(item.size/1024) + 'kb'])
          if(index+1){
            // console.log(newl[index])
            return newl[index][0] + " : " + newl[index][1]
          }
          return newl
        }
      },
      // 其他函数end

      back(){
        this.$emit('back',true);
      },

      async init(){
        // console.log(this.taskID)
        if(this.taskID){
          let res = await this.$api.fileDistribution.getFileDistributionTaskInfo(this.taskID)
          // console.log(res.file)
          this.detailInfo = res
          this.tableDataDetail=res.machines
        }
      }
    },
    mounted(){
      this.init()
    },
	}
</script>

<style>
  .file-distribution-detail{
    position: relative;
    font-size: 14px;
  }
  .file-distribution-detail .button-back{
    position:absolute;
    top: -5px;
    left:0px;
    z-index: 99;
  }
  .area-file-distribution-detail{
    padding: 0px 40px;
    color: #9ca9b1;
  }
  .area-file-distribution-detail .left{
    display: inline-block;
    width: 90px;
    color: #5d6266;
    white-space: nowrap;/*不换行*/
    overflow: hidden;/*超出部分隐藏*/
    text-overflow:ellipsis;
  }
  .area-file-distribution-detail .right{
    display: inline-block;
    width: 254px;
    /*overflow: hidden;*/
    white-space: nowrap;/*不换行*/
    overflow: hidden;/*超出部分隐藏*/
    margin-right: 10px;
    text-overflow:ellipsis;
  }
</style>
