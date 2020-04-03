<template>
	<div style='padding:20px 20px 0 26px;' class='theme-dark keda-records '>
		<!-- 表单 -->
				<el-select popper-class="theme-dark" filterable placeholder='请选择平台' v-model='formInLine.platform' style='width:150px;padding-right: 7px' clearable>
					<el-option v-for="item in options1"
						:key="item.domain_name"
						:label="item.domain_name"
						:value="item.domain_name">
					</el-option>
				</el-select>
				<el-input clearable v-model="formInLine.operating_models" placeholder="请输入业务" style='width:230px;padding-right: 7px' maxlength="100" @keydown.enter.native='searchEnterFun'></el-input>
        <el-date-picker
          v-model="formInLine.formtime"
          style="width: 320px;vertical-align: top;margin-right: 7px"
          type="datetimerange"
          range-separator=""
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          popper-class="theme-dark"
          format="yyyy-MM-dd HH:mm"
          class="clear-close-icon"
          prefix-icon="ops-icons-bg icon-calendar"
          :clearable="false">
        </el-date-picker>
				<el-button @click="onSubmit('formInLine')" :disabled="onSubmitDisabled">搜索</el-button>
				<el-button @click="delAll()" style='float: right;' :disabled="delDisabled">删除</el-button>
				<el-button @click="addRecord()" style='float: right;' :disabled="addDisabled">新增</el-button>
	<!-- </el-row> -->
	  <!-- 表格 -->
		<div>
		<el-table
			:data="tableData"
			style="margin-top: 18px;"
			@selection-change="handleSelectionChange"
      :header-cell-class-name="setHeaderCellStyle"
			stripe
			class='rectable'
      v-loading="loadingTableData"
      element-loading-background="rgba(0, 0, 0, 0.5)">
			<template>
				<el-table-column
					prop="record_id"
					type="index"
					label='序号'
          min-width="45px">
				</el-table-column>
				<el-table-column
				type="selection"
        min-width="20px"
				>
				</el-table-column>
				<el-table-column
					label="维护时间"
					min-width="193px"
          show-overflow-tooltip>
          <template slot-scope="scope">
            <span>{{new Date(scope.row.maintenance_time).format('Y-m-d H:i')}}</span>
          </template>
				</el-table-column>
				<el-table-column
					prop="maintainers"
					label="维护人"
					min-width="160px"
          show-overflow-tooltip>
				</el-table-column>
				<el-table-column
					prop="platform"
					label="所属平台"
          min-width="190px"
          show-overflow-tooltip>
				</el-table-column>
				<el-table-column
					prop="operating_models"
					label="所属业务"
          min-width="180px"
					show-overflow-tooltip >
				</el-table-column>
				<el-table-column
					prop="operations"
					label="维护明细"
          min-width="230px"
					show-overflow-tooltip >
				</el-table-column>
				<el-table-column
					prop="postscript"
					label="备注"
          min-width="211px"
					show-overflow-tooltip >
				</el-table-column>
				<el-table-column
					prop="options"
					label='操作'
          min-width="105px"
					class='kd-script'>
					<template slot-scope="scope">
						<button type="button" class="button-host-info" @click="dialogEdit(scope.$index,tableData)">
							<span style="text-decoration: underline;">修改</span>
						</button>
					</template>
				</el-table-column>
			</template>
		</el-table>
		</div>
		<!-- 增加按钮填写 -->
		<el-dialog 
			title="新增"
			:visible.sync="dialogVisible" 
			width="500px"
			:close-on-click-modal="false"
			class='kd-rec formrec'
      style="color: #9ca9b1">
        <div style="margin-top: 20px;color: #9ca9b1;font-size: 12px;">
          <span style="margin-right:37px">维护人</span>
          <el-input v-model='ruleForm.maintainers' maxlength="32" style="width: 340px" placeholder='请输入维护人'></el-input>
					<span style="color:#f56c6c;display: inline;margin-left:3px;">*</span>
        </div>
        <div style="margin-top: 20px;color: #9ca9b1;font-size: 12px;">
          <span style="margin-right:25px">维护时间</span>
          <el-date-picker
            v-model="ruleForm.maintenance_time"
            type="datetime"
            range-separator=""
            placeholder="请选择时间"
            popper-class="theme-dark"
            format="yyyy-MM-dd HH:mm"
            class="clear-close-icon"
            prefix-icon="ops-icons-bg icon-calendar"
            :clearable=false
            style="width: 340px"
            :picker-options="disabledDate">
          </el-date-picker>
					<span style="color:#f56c6c;display: inline;margin-left:3px;">*</span>
        </div>
        <div style="margin-top: 20px;color: #9ca9b1;font-size: 12px;">
          <span style="margin-right:25px">所属平台</span>
          <el-select popper-class="theme-dark" filterable placeholder='请选择平台' v-model='ruleForm.platform' style="width: 340px">
            <el-option v-for="item in options1"
                       :key="item.domain_name"
                       :label="item.domain_name"
                       :value="item.domain_name">
            </el-option>
          </el-select>
					<span style="color:#f56c6c;display: inline;margin-left:3px;">*</span>
        </div>
        <div style="margin-top: 20px;color: #9ca9b1;font-size: 12px;">
          <span style="margin-right:25px">所属业务</span>
          <el-input v-model='ruleForm.operating_models' maxlength="32" style="width: 340px;" placeholder='请输入业务'></el-input>
					<span style="color:#f56c6c;display: inline;margin-left:3px;">*</span>
				</div>
        <div style="margin-top: 20px;color: #9ca9b1;font-size: 12px;">
          <span style="margin-right:25px;float: left" >维护明细</span>
          <el-input v-model='ruleForm.operations' type="textarea" maxlength="100" style="width: 340px;margin-left: 3.5px"></el-input>
					<span style="color:#f56c6c;display: inline;float: right;margin-right: 1px;">*</span>
				</div>
        <div style="margin-top: 20px;color: #9ca9b1;font-size: 12px;">
          <span style="margin-right:37px;float: left">备注</span>
          <el-input v-model='ruleForm.postscript'  maxlength="100" style="width: 340px;margin-left: 15.5px"></el-input>
        </div>
			<div align='center' slot='footer' class='theme-dark' style='margin-top:30px;padding-bottom: 10px'>
        <el-button type="info" @click="dialogVisibleAdd('ruleForm')">确 定</el-button>
				<el-button @click="dialogVisible = false">取 消</el-button>
			</div>
		</el-dialog>
		
		<!-- 修改页面 -->
		<el-dialog	
				title="修改"
				:visible.sync="dialogVisibleDetail"
				width="500px"
				:close-on-click-modal="false"  
				class='kd-rec formrec'
        style="color: #9ca9b1">
      <div style="margin-top: 20px;color: #9ca9b1;font-size: 12px;">
        <span style="margin-right:37px">维护人</span>
        <el-input v-model='ruleFormd.maintainers' maxlength="100" style="width: 340px" placeholder='请输入维护人'></el-input>
				<span style="color:#f56c6c;display: inline;margin-left:3px;">*</span>
      </div>
      <div style="margin-top: 20px;color: #9ca9b1;font-size: 12px;">
        <span style="margin-right:25px">维护时间</span>
        <el-date-picker
          v-model="ruleFormd.maintenance_time"
          type="datetime"
          range-separator=""
          placeholder="请选择时间"
          popper-class="theme-dark"
          format="yyyy-MM-dd HH:mm"
          class="clear-close-icon"
          prefix-icon="ops-icons-bg icon-calendar"
          :clearable=false
          style="width: 340px"
          :picker-options="disabledDate">
        </el-date-picker>
				<span style="color:#f56c6c;display: inline;margin-left:3px;">*</span>
      </div>
      <div style="margin-top: 20px;color: #9ca9b1;font-size: 12px;">
        <span style="margin-right:25px">所属平台</span>
        <el-select popper-class="theme-dark" filterable placeholder='请选择平台' v-model='ruleFormd.platform' style="width: 340px">
          <el-option v-for="item in options1"
                     :key="item.domain_name"
                     :label="item.domain_name"
                     :value="item.domain_name">
          </el-option>
        </el-select>
				<span style="color:#f56c6c;display: inline;margin-left:3px;">*</span>
      </div>
      <div style="margin-top: 20px;color: #9ca9b1;font-size: 12px;">
        <span style="margin-right:25px">所属业务</span>
        <el-input v-model='ruleFormd.operating_models' maxlength="100" style="width: 340px" placeholder='请输入业务'></el-input>
				<span style="color:#f56c6c;display: inline;margin-left:3px;">*</span>
      </div>
      <div style="margin-top: 20px;color: #9ca9b1;font-size: 12px;">
        <span style="margin-right:25px;float: left">维护明细</span>
        <el-input v-model='ruleFormd.operations' type="textarea" maxlength="100" style="width: 340px;margin-left: 3.5px"></el-input>
				<span style="color:#f56c6c;display: inline;float: right;margin-right: 1px;">*</span>
			</div>
      <div style="margin-top: 20px;color: #9ca9b1;font-size: 12px;">
        <span style="margin-right:37px;float: left">备注</span>
        <el-input v-model='ruleFormd.postscript'  maxlength="100" style="width: 340px;margin-left: 15.5px"></el-input>
      </div>
			<div align='center' slot='footer' class='theme-dark' style='margin-top:30px;padding-bottom: 10px'>
        <el-button type="info" @click="dialogVisibleEdit('ruleFormd')">确 定</el-button>
				<el-button @click="dialogVisibleDetail = false">取 消</el-button>
			</div>
		</el-dialog>

		<!-- 页码 -->
		<div style="margin-top: 20px;">
        <KdPagination  
        @current-change="handleCurrentChange" 
        :pageSize="pageSize"
        :currentPage="currentPage"
        :total="count">
				</KdPagination>
    </div>
		
		<!-- 删除提示框 -->

    <el-dialog title="提示" :visible.sync="delVisible" width="300px" top="15%" :close-on-click-modal="false">
      <div style="margin-top: 40px;margin-bottom: 20px;margin-left: 20px  ">
        <span style="margin-right: 7px;font-size: 14px;">
          <i class="ops-icons-bg icon-notice" style="vertical-align: bottom;"></i>
        </span>
        <span>删除不可恢复，是否确定删除？</span>
      </div>
      <div align='center' slot='footer' class='theme-dark' style='margin-top:10px;padding-bottom: 10px'>
        <el-button type="info" @click="deleteRowAll()">确 定</el-button>
        <el-button @click="delVisible = false">取 消</el-button>
      </div>
    </el-dialog>


	
	</div>	
</template>



<script>
	export default {
    components:{
      KdPagination: () => import('@/components/common/KdPagination.vue'),
    },
    data() {
      return {
        loadingTableData:false,   //列表加载
        delDisabled:true,        //删除键是否可点击
        addDisabled:false,     //增加键是否可点击
        onSubmitDisabled:false,    //查询键是否可点击
				options1:[],
				start:0,
				count:0,
        pageSize:15,
				currentPage:1,        //初始页
				formInLine: {              //搜索框的各项
				  formtime: [],
				  platform: '',
					operating_models:'',
				},			 
        tableData: [],						 //数据接收传递
				dialogVisible: false,			 //增加按钮的弹框控制					
				dialogVisibleDetail:false, //详情按钮的弹框控制			
				delVisible:false,          // 删除按钮的弹框控制
        disabledDate: {
          disabledDate:time=>{
            return time.getTime() > Date.now();
          }
        },
				ruleForm:{								 //增加按钮模块数据
					maintenance_time:'',
          maintainers:'',
          platform:'',
          operating_models:'',
          operations:'',
          postscript:'',
				},
				//详情按钮模块数据
				ruleFormd:{},
				rules:{
					maintainers:[
						{required:true,message: '维护人需要被填写',trigger: 'blur'}
					],
					maintenance_time:[
						{required:true,message: '维护时间需要被选择',trigger: 'blur'}
					],
					platform:[
						{required:true,message: '所属平台需要被填写',trigger: 'blur'}
					],
					operating_models:[
						{required:true,message: '操作模块需要被填写',trigger: 'blur'}
					],
					operations:[
						{required:true,message: '维护明细需要被填写',trigger: 'blur'}
					],
				},									//增加按钮的规则
				delArr:[],								//存放删除的数据
				multipleSelection:[],			//多选的数据
				startTime:"",
				endTime:"",
				
		}},
    methods: {
      // disabledDate(time){
      //   return time.getTime() > Date.now();
      // },
      addRecord(){
        this.ruleForm={
            maintenance_time:'',
            maintainers:'',
            platform:'',
            operating_models:'',
            operations:'',
            postscript:'',
        };
        this.dialogVisible = true
      },
			//以下为时间戳转换为时间
      timestampToTime(timestamp) {
        var date = new Date(timestamp);//时间戳为10位需*1000，时间戳为13位的话不需乘1000
        var Y = date.getFullYear() + '-';
        var M = (date.getMonth()+1 < 10 ? '0'+(date.getMonth()+1) : date.getMonth()+1) + '-';
        var D = (date.getDate()<10 ? '0'+date.getDate() : date.getDate()) + ' ';
        var h = (date.getHours()<10 ? '0'+date.getHours():date.getHours())  + ':';
        var m = (date.getMinutes()<10 ? '0'+date.getMinutes():date.getMinutes() ) + ':';
        var s = (date.getSeconds()<10 ? '0'+date.getSeconds():date.getSeconds()) ;
        return Y+M+D+h+m+s;
      },
			getRecords(){   						//接收后端传来的数据
        this.loadingTableData = true
        this.onSubmitDisabled=true
        this.addDisabled=true
        this.delDisabled=true
        this.$api.rec.platformget().then(res=>{
            this.options1 = res.data.info
        }).catch(err=>{})
        var params={
          "start":this.start,
          "count":this.pageSize
        }
				this.$api.rec.records(params).then(res=>{
					if (res.data.success === 1){
            this.loadingTableData = false
            this.onSubmitDisabled=false
            this.addDisabled=false
						this.count = res.data.data.total
						this.tableData=res.data.data.info;
					}	
					else if (res.data.success === 0){
            this.loadingTableData = false
            this.onSubmitDisabled=false
            this.addDisabled=false
					}
				}).catch(err=>{
          this.loadingTableData = false
          this.onSubmitDisabled=false
          this.addDisabled=false
        })
			},
			searchEnterFun(e){									//enter搜索函数
				// console.log(e)
				var keyCode = window.event?e.keyCode:e.which;
				if(keyCode===13){
					this.onSubmit()
				}
			},
			onSubmit() {  							//查询按钮
        this.loadingTableData = true
        this.onSubmitDisabled=true
        this.addDisabled=true
        this.delDisabled=true
				if (!this.formInLine.formtime){   //处理当formInline为空的时候报错问题
					this.startTime= ''
					this.endTime =  ''
				}
				else if (this.formInLine.formtime.length === 2){
					//以下处理为后端时间未改时使用
					this.startTime=this.formInLine.formtime[0]
					this.endTime = this.formInLine.formtime[1]
				}
        this.currentPage = 1
        this.start = 0
				var params={ 							//降低传入后端参数
					"starttime":this.startTime,
					"endtime":this.endTime,
					"platform" :this.formInLine.platform,
					"operating_models":this.formInLine.operating_models,
          "start":this.start,
          "count":this.pageSize
				}
				this.$api.rec.records(params)
				.then(res=>{
					if (res.data.success === 1){
            this.loadingTableData = false
            this.onSubmitDisabled=false
            this.addDisabled=false
						this.count = res.data.data.total;
						this.tableData=res.data.data.info;
					}
					else if (res.data.success === 0){
						console.log(res.data.msg);
            this.loadingTableData = false
            this.onSubmitDisabled=false
            this.addDisabled=false
					}
				}).catch(err=>{
          this.loadingTableData = false
          this.onSubmitDisabled=false
          this.addDisabled=false
        })
			},
			dialogVisibleAdd(formName){					//增加传输数据
        this.$api.rec.recordsPost(this.ruleForm).then(res => {
          if (res.data.success === 1) {
            this.dialogVisible = false;
            this.$message.success('添加成功')
            this.getRecords()
          }
          else if (res.data.success === 0) {
            this.$message.error('添加失败')
            console.log(res.data.msg);
          }
        }).catch(err => {
          this.$message.error('添加失败')
        })
      },
			dialogVisibleEdit(formName){			 //编辑传输数据
        this.$api.rec.recordsPut(this.ruleFormd).then(res =>{
          if (res.data.success === 1){
            this.dialogVisibleDetail = false;
            this.$message.success('修改成功')
            this.getRecords()
          }
          else if (res.data.success === 0){
            this.$message.error('修改失败')
          }
        }).catch(err=>{
          this.$message.error('修改失败')
        })
			},	
			deleteRow(index, row){
				this.delVisible = true;			//删除单条
				this.delArr.push(row.record_id)			
			},
			handleSelectionChange(val){		//操作多选
				this.multipleSelection = val;
				if(this.multipleSelection.length===0){
				  this.delDisabled=true
        }else{
				  this.delDisabled=false
        }
			},
			delAll(){ 										//批量删除
				const length = this.multipleSelection.length;
        this.delVisible = true;   	//显示删除弹框
        for (let i = 0; i < length; i++){
          this.delArr.push(this.multipleSelection[i].record_id)
        }

			},
			deleteRowAll(){
				var param = {"ids":this.delArr}
				this.$api.rec.recordsDelete(param).then(res =>{
					this.multipleSelection = []
					this.delArr=[]
					if (res.data.success === 1){
						this.$message.success('删除成功')
						this.getRecords()
					}	
					else if (res.data.success === 0){
						this.$message.error('删除失败')
					}
				}).catch(err=>{})
				this.delVisible = false; //关闭提示框
			},
			dialogEdit(row,tableData){            //获取单条维护记录
				this.dialogVisibleDetail=true
				this.$api.rec.recordsGet(tableData[row]).then(res=>{
					if (res.data.success === 1){
						this.ruleFormd = res.data.data.info[0];
            this.onSubmitDisabled=false
					}	
					else if (res.data.success === 0){
						this.$message.error('获取详情失败')
            this.onSubmitDisabled=false
					}
				}).catch(err=>{
          this.onSubmitDisabled=false
        })
				this.dialogVisibleDetail=true
			},

			handleCurrentChange(currentPage){   //点击第几页
        this.currentPage = currentPage
        this.loadingTableData = true
        this.onSubmitDisabled=true
        this.addDisabled=true
        this.delDisabled=true
				this.start = (currentPage-1) * this.pageSize;  //为了规避同名导致点击页数跳转
				if (currentPage >0){
					var params = {
						"count":this.pageSize,
						"start": this.start,
						"starttime":this.startTime,
						"endtime":this.endTime,
						"platform" :this.formInLine.platform,
						"operating_models":this.formInLine.operating_models,
					}
					this.$api.rec.records(params).then(res =>{
						if (res.data.success === 1){
							this.tableData=res.data.data.info;
              this.loadingTableData = false
              this.onSubmitDisabled=false
              this.addDisabled=false
              this.delDisabled=false
						}	
						else if (res.data.success === 0){
							console.log(res.data.msg);
              this.loadingTableData = false
              this.onSubmitDisabled=false
              this.addDisabled=false
              this.delDisabled=false
						}
					}).catch(err=>{
            this.loadingTableData = false
            this.onSubmitDisabled=false
            this.addDisabled=false
            this.delDisabled=false
          })
				}
				
			},
      setHeaderCellStyle({row, column, rowIndex, columnIndex}){		//去掉表格前两项的竖杠
        if(columnIndex===0||columnIndex===1){
          return "el-table-th-noborder"
        }
      },
    },
		mounted(){ 
			this.getRecords();  //初始化加载
		},

};
</script>


<style>
  .keda-records .el-tooltip__popper{     /* 鼠标触碰时所展示出来的宽度以及高度 */
    max-width: 400px;
    line-height: 180%;
  }
	.keda-records .el-form-item{
		margin: 0;
	}
	.kd-rec .el-dialog{
		padding: auto 20px;
	}
	.kd-rec .el-dialog__body{
		padding: 5px 35px;
	}
  .kd-rec .el-textarea__inner::-webkit-input-placeholder {
    color:#9ca9b1;
    font-size: 12px;
  }
  .kd-rec .el-textarea__inner{
      background-color: #1f2122;
      border-radius: 0;
      border: 1px solid #383b3c;
      height: 80px !important;
      color:#9ca9b1;
      padding:5px 10px;
      font: 12px"微软雅黑";
    }
  .postRemark .el-textarea__inner::-webkit-input-placeholder {
    color:#9ca9b1;
    font-size: 12px;
  }
  .postRemark .el-textarea__inner{
    color:#9ca9b1;
    background-color: #1f2122;
    border-radius: 0;
    border: 1px solid #383b3c;
    height: 40px;
    margin-bottom: 5px;
  }
  .postRemark .el-form-item.is-success .el-input__inner,
  .postRemark .el-form-item.is-success .el-input__inner:focus,
  .postRemark .el-form-item.is-success .el-textarea__inner,
  .postRemark .el-form-item.is-success .el-textarea__inner:focus{
    border-color:#383b3c
  }
  .kd-rec .el-form-item.is-success .el-input__inner,
  .kd-rec .el-form-item.is-success .el-input__inner:focus,
  .kd-rec .el-form-item.is-success .el-textarea__inner,
  .kd-rec .el-form-item.is-success .el-textarea__inner:focus{
    border-color:#383b3c
  }

</style>
