   <template>
    <div class='theme-dark keda-faq'>
      <!--//以下为修改版-->
      <div class='faqAllit theme-dark' v-if='defaultall'>
        <!--左边侧边栏-->
        <div :class="['faqInfo',{'unfold':!unfold}]" :style="{'width':unfold? '0':'260px'} ">
          <div class="faqInfo-group-collapse" :style="{'left':unfold?'0px':'260px'}"
               @click="sidebarTelescopic">
            <i :class="['icon-group-collapse','el-icon-arrow-right',{'active':!unfold}]"></i>
          </div>
          <el-scrollbar class="faqInfo-siderbar-scrollbar" :noresize="false" >
            <div class="faq-siderbar-tree " >
              <div :class="['el-tree-node__content',{'is-active':showAllButton}]" @click="showAllQuestion" style="height: 30px;display: flex;align-items: center;margin-left: 12px;margin-top: 13px;margin-right: 16px" @mouseover="mouseoverTree" @mouseleave="mouseleaveTree"  >
                <span class="el-dropdown-link" style="display: flex;justify-content: center;align-items: center">
                  <i class="ops-icons-bg icon-faq-group-dropdown"></i>
                </span>
                <span style="margin-left: 6px;font-size: 14px">全部</span>
                <span style="margin-left: 160px;" class="addGroupButtonStyle">
                  <el-button @click="addTypesFunction">
                    <i class="ops-icons-bg icon-faq-group-add" ></i>
                  </el-button>
                </span>
              </div>
              <!--分组操作-->
              <div v-for="(everyProject,index) in options" :key="index" style="padding: 10px  16px 0 10px;font-size: 14px;"  >
                <div @click="typesClick(everyProject)" :class=" ['el-tree-node__content',{'is-active':groupIsActived === everyProject.id}]" style="position: relative;">
                  <el-tooltip class="item" effect="dark" :content="everyProject.classification" placement="top-start"  v-if="everyProject.classification.length>10">
                    <span class="el-tree-node__label" style="display: inline-block;position:absolute;left: 15%;white-space: nowrap;overflow: hidden; max-width:170px;text-overflow:ellipsis;">{{everyProject.classification}}</span>
                  </el-tooltip>
                    <span class="el-tree-node__label"  style="left: 15%;margin-left: 35px" v-if="everyProject.classification.length<=10">{{everyProject.classification}}</span>
                  <el-dropdown  trigger="click" style="position: absolute;right: 22px"  v-show="showEditGroup&&selectionGroup===everyProject.id" >
                    <span class="el-dropdown-link">
                      <i class="el-icon-arrow-down el-icon--right"></i>
                    </span>
                    <el-dropdown-menu class="theme-dark" slot="dropdown">
                      <el-dropdown-item @click.native="modifyTypes(everyProject)">重命名组</el-dropdown-item>
                      <el-dropdown-item @click.native="delTypes()">删除分组</el-dropdown-item>
                    </el-dropdown-menu>
                  </el-dropdown>
                </div>
              </div>
            </div>
          </el-scrollbar>
        </div>
        <!--右半部分问题答案-->
        <div class="theme-dark faqInfo-column" :style="{'margin-left':unfold?'37px':'297px'}" >
					<div style="float: left;">
						<el-input
						  placeholder='请输入问题进行搜索'
						  v-model='MeetingSearch'
						  style='width:230px;margin-right: 7px' maxlength="100" clearable
							@keydown.enter.native='searchEnterFun'></el-input>
						<el-button @click="meetingSearch(MeetingSearch)" >搜索</el-button>
					</div>
					<div style="position: fixed;right: 20px;">
						<el-button @click="addQuestion" :disabled="addQuestionDisabled">新增</el-button>
						<el-button @click="dialogVisibleEdit()" :disabled="editQuestionDisabled">编辑</el-button>
						<el-button @click="delAllOne(ruleForm)" :disabled="deleteQuestionDisabled">删除</el-button>
					</div>
          <div style="margin-top: 46px;background-color:transparent;">
              <el-collapse v-model="activeNames"  v-for="(faqQuest,index1) in faqQaList" style="background-color:transparent" :key="index1" @click.native ="itemit(faqQuest)">
                <el-collapse-item :name="faqQuest.record_id" style="background-color: transparent;margin-left: 5px;" id="questionColor">
                  <template slot="title" >
                    <div :class="['el-tree-node__content',{'is-active':collapseId === faqQuest.record_id}]">
                      {{index1+1}}. {{  faqQuest.question}}
                    </div>
                  </template>
                  <div style="height: 9px;background-color: #1e2224" ></div>
                  <div style="background: #272c2e;color: #9ca9b1;padding:18px 10px 18px 18px;min-height: 80px;min-width: 1102px;box-sizing: border-box;overflow:auto;white-space: pre-line;word-break: break-all;word-wrap: break-word;">{{faqQuest.anwserItem}}</div>
                  <div style="height: 10px;background-color: #1e2224 "></div>
                </el-collapse-item>
                <div style="height: 2px;background-color: #1e2224 "></div>
              </el-collapse>
            <!-- </div> -->
          </div>
        </div>
        <!--结束问题答案-->
        <!--无问题分组时显示-->
        <div style="position: relative;  margin-top:280px;text-align: center;" v-if="withoutGroup">
          <span style="margin-right: 7px;font-size: 14px;">
            <i class="ops-icons-bg icon-notice" style="vertical-align: bottom;"></i>
          </span>
          <span>尚无帮助问答，请先</span>
          <span style="color: #299dff;text-decoration:underline;cursor: pointer;" @click="addTypesFunction">新建分组</span>
          <span>再新增问题</span>
        </div>
        <!--分组内无问题时显示-->
        <div style="position: relative;  margin-top:280px;text-align: center;" v-if="withoutQuestion">
          <span style="margin-right: 7px;">
            <i class="ops-icons-bg icon-notice" style="vertical-align: bottom;"></i>
          </span>
          <span style="font-size: 12px;color: #9ca9b1">该分组内尚无帮助问答，请先</span>
          <span style="color: #299dff;text-decoration:underline;cursor: pointer;" @click="addQuestion">新增问题</span>
        </div>

        <!--重命名组-->
        <el-dialog
          title="重命名组"
          :visible.sync="modifyQsTypes"
          width="400px"
          top="15%"
          custom-class="classQuestionTypes"
          :close-on-click-modal="false"
          @close="closeModifyQs"
          class=''>
          <div style="margin-top: 63px;">
            <span style="margin-right:7px;display: inline-block">新组名</span>
            <el-input placeholder="请输入新组名"  v-model="modifyQuestionsTypes.newClassIfiCation" style="width: 260px;" maxlength="32"></el-input>
          </div>
          <div  align='center' slot='footer' class='theme-dark' style='margin-top:82px;margin-bottom: 10px'>
            <el-button type="info" @click="dialogVisibleModifyTypes(modifyQuestionsTypes)">确 定</el-button>
            <el-button @click="modifyQsTypes = false">取 消</el-button>
          </div>
        </el-dialog>
        <!--结束-->

        <!--删除分组-->
        <el-dialog
        title="提示"
        :visible.sync="dialogVisibleDelTypes"
        width="300px"
        top="15%"
        :close-on-click-modal="false">
        <div style="margin-top: 40px;margin-bottom: 40px;margin-left: 15px">
          <span style="margin-right: 7px;font-size: 14px;">
            <i class="ops-icons-bg icon-notice" style="vertical-align: bottom;"></i>
          </span>
          <span>选定的分组内有帮助问答，该分组不能被删除！</span>
        </div>
        <div  align='center' slot='footer' class='theme-dark' style='margin-top:30px;padding-bottom: 10px'>
          <el-button @click="dialogVisibleDelTypes = false">确 定</el-button>
        </div>
        </el-dialog>
        <!--结束-->

        <!--新增问题-->
        <el-dialog
        title="新增"
        :visible.sync="add"
        custom-class="classQuestion"
        :close-on-click-modal="false"
        width="500px">
          <div :model="addForm" ref="addForm" style="margin-top:  30px">
            <div style="margin-bottom: 20px;color: #9ca9b1;font-size: 12px">
              <span style="margin-right:32px" >问题描述</span>
              <el-input v-model="addForm.question" style="width: 340px" type="text" maxlength="128" placeholder="请输入问题描述"></el-input>
            </div>
            <div style="margin-bottom: 20px;color: #9ca9b1;font-size: 12px">
              <span style="margin-right:32px">选择分组</span>
              <el-select v-model='addForm.classificationes' placeholder='请选择分组' popper-class="theme-dark" style="width: 340px">
                <el-option
                  v-for="item in options"
                  :key="item.id"
                  :label="item.classification"
                  :value="item.id">
                </el-option>
              </el-select>
            </div>
            <div style="margin-bottom: 20px;color: #9ca9b1;font-size: 12px;min-height: 80px" class="answerDetail">
              <span style="margin-right:32px;display: inline-block">答案明细</span>
              <el-input v-model="addForm.answer" type="textarea" maxlength="1024"  style="max-width: 340px;float: right;margin-right: 7px" placeholder="请输入答案明细"></el-input>
            </div>

          </div>
          <div  align='center' slot='footer' class='theme-dark' style='margin-top:30px;padding-bottom: 10px'>
            <el-button type="info" @click="dialogVisibleAdd(addForm)">确 定</el-button>
            <el-button @click="add = false">取 消</el-button>
          </div>
        </el-dialog>
        <!--结束-->

        <!--分组增加-->
        <el-dialog
          title="新建分组"
          :visible.sync="addTypes"
          width="400px"
          top="15%"
          custom-class="classQuestionTypes"
          :close-on-click-modal="false"
          class=''>
          <div :model='addQuestionsTypes' ref="addQuestionsTypes" style="margin-top: 63px;">
            <span style="margin-right:7px;display: inline-block">分组名称</span>
            <el-input placeholder="请输入要添加的分组" maxlength="32"  v-model="addQuestionsTypes.classification" style="width: 260px"></el-input>
          </div>
          <div  align='center' slot='footer' class='theme-dark' style='margin-top:82px;margin-bottom: 10px'>
            <el-button type="info" @click="dialogVisibleAddTypes('addQuestionsTypes')">确 定</el-button>
            <el-button @click="addTypes = false">取 消</el-button>
          </div>
        </el-dialog>
        <!--结束-->

        <!--编辑问题-->
        <el-dialog
        title="编辑"
        :visible.sync="editIsShow"
        width="500px"
        custom-class="classQuestion"
        :close-on-click-modal="false"
        class=''>
          <div :model="ruleForm" ref="ruleForm"  style="margin-top:  30px">
            <div style="margin-bottom: 20px;color: #9ca9b1;font-size: 12px">
              <span style="margin-right:32px" >问题描述</span>
              <el-input v-model="ruleForm.question" style="width: 340px" type="text" maxlength="128"></el-input>
            </div>
            <div style="margin-bottom: 20px;color: #9ca9b1;font-size: 12px">
              <span style="margin-right:32px">选择分组</span>
              <el-select v-model='ruleForm.classification' placeholder='请选择分组' popper-class="theme-dark" style="width: 340px">
                <el-option
                  :default='ruleForm.classification'
                  v-for="item in options"
                  :key="item.id"
                  :label="item.classification"
                  :value="item.id">
                </el-option>
              </el-select>
            </div>
            <div style="margin-bottom: 20px;color: #9ca9b1;font-size: 12px;min-height: 80px" class="answerDetail">
              <span style="margin-right:32px;display: inline-block">答案明细</span>
              <el-input v-model="ruleForm.answer" type="textarea" maxlength="1024"  style="max-width: 340px;float: right;margin-right: 7px"></el-input>
            </div>
          </div>
          <div  align='center' slot='footer' class='theme-dark' style='margin-top:30px;padding-bottom: 10px'>
            <el-button type="info" @click="dialogVisibleEditOk(ruleForm)">确 定</el-button>
            <el-button @click="editIsShow = false">取 消</el-button>
          </div>
        </el-dialog>
        <!--结束-->

        <!--删除问题-->
        <el-dialog title="提示" :visible.sync="delVisible" width="300px" top="15%" :close-on-click-modal="false">
          <div style="margin-top: 40px;margin-bottom: 40px;margin-left: 20px">
            <span style="margin-right: 7px;font-size: 14px;">
              <i class="ops-icons-bg icon-notice" style="vertical-align: bottom;"></i>
            </span>
            <span>确定删除该条帮助问答？</span>
          </div>
          <div align='center' slot='footer' class='theme-dark' style='margin-top:30px;padding-bottom: 10px'>
            <el-button type="info" @click="delAll()">确 定</el-button>
            <el-button @click="delVisible = false">取 消</el-button>
          </div>
        </el-dialog>
        <!--结束-->
      </div>
      <!--以上为修改版-->
    </div>
  </template>




  <script>
    export default {
      data() {
        return {
          //以下为修改版
          activeNames:[],                  //默认展开
          defaultall:true,													//默认界面
          unfold:true,															//展开侧边栏所显示的内容
          withoutGroup:false,                        //在没有问题分组时展示
          withoutQuestion:false,                     //在分组内没有问题时展示
          addQuestionDisabled:true,
          deleteQuestionDisabled:true,
          editQuestionDisabled:true,
          showEditGroup:false,            //左边是否展示重命名和删除分组
          selectionGroup:'',                //选中分组信息
          showAllButton:true,
          groupIsActived:"",
          collapseId:'',
          showAllFocus:'',
          //以上为修改版
          options:[],																							//增加问题答案时的分类
          delValue:{},																						//删除分类
          dialogVisibleDelTypes:false,														//控制删除分类
          addQuestionsTypes:{																			//增加分类
            classification:'',
          },
          modifyQuestionsTypes:{},								 								//修改分类
          faqqa:{}, 																							//接收问题类型数据
					faqQaList:[],
          dialogVisible : false,  																//控制详情框
          edit:false,     																				//控制编辑框
          add : false,																						//控制增加框
          addTypes:false,																					//控制增加分类
          modifyQsTypes:false,																		//控制修改分类
          delVisible:false,																				//控制删除提示框
          ruleForm:{},																						//答案详情
          formInLine:{},																					//搜索框
          addForm:{																								//增加框
            "creator":"admin",
            "classificationes":'',
            "question":"",
            "answer":"",
          },
          delArr:[],																							//删除的数据
          editIsShow:false,																				//编辑框隐藏
          record_id:'',                                           //问答id
          id:'',                                                  //分类id
					MeetingSearch:'',                                       //搜索条件
        }
      },
      methods: {
        //enter搜索函数
				searchEnterFun(e){
					// console.log(e)
					var keyCode = window.event?e.keyCode:e.which;
					if(keyCode===13){
						this.meetingSearch()
					}
				},
				//新增搜索功能
				meetingSearch(val){
					var params={
						"id":this.id,
						"question":this.MeetingSearch
					}
					this.faqGet(params)
				},
				// 为了计算距离顶部的高度，当高度大于60显示回顶部图标，小于60则隐藏
        // scrollToTop () {
        //   const that = this
        //   let scrollTop = window.pageYOffset || document.documentElement.scrollTop || document.body.scrollTop
        //   that.scrollTop = scrollTop
        //   if (that.scrollTop > 60) {
        //     that.btnFlag = true
        //   } else {
        //     that.btnFlag = false
        //   }
        // },
        //重命名分组关闭dialog前清除
        closeModifyQs(){
          this.modifyQuestionsTypes.newClassIfiCation=''
        },
        // 以下为修改版
        //侧边栏点击全部时显示
        showAllQuestion(){
          this.collapseId=''
          this.groupIsActived=''
          this.id=''
          this.showAllButton=true
          this.faqGet()
        },
        //侧边栏的展开收起
        sidebarTelescopic(){
          this.unfold = !this.unfold
          // this.pickup = !this.pickup
        },
        // 设置是否隐藏侧边栏添加分组按钮
        mouseoverTree(){
          // this.addGroupButton = true
        },
        // 设置是否隐藏侧边栏添加分组按钮
        mouseleaveTree(){
          // this.addGroupButton = false
        },
        // 点击新增问题按钮后清除之前缓存填入问题
        addQuestion(){
          this.addForm={
            "creator":"admin",
            "classificationes":'',
            "question":"",
            "answer":"",
          }
          this.add=true
        },
       // 点击新建分组按钮后清除之前缓存填入问题
        addTypesFunction(){
          this.addQuestionsTypes.classification=''
          this.addTypes=true
        },
        //选中分类下所有的问题参数
        typesClick(val){
          this.faqSiderbarStyle = {
            "background-color":"#485a6b"
          }
          this.showAllButton=false
          this.groupIsActived = val.id
          this.selectionGroup = val.id
          this.delValue.classificationes = val.id
          this.modifyQuestionsTypes.classification=val.id
          this.showEditGroup = true
          this.id = val.id
          this.MeetingSearch=''
          var params = {
            "id":this.id,
          }
          this.faqGet(params)
        },
        //修改分类
        modifyTypes(raw){
          //保留所修改分类的id以便修改
          this.qsTypes()
          this.modifyQsTypes = true
        },
        //编辑框
        dialogVisibleEdit(){
          this.editIsShow = true;
        },
        //点击删除分组时请求下拉菜单
        delTypes(){
          if(this.withoutQuestion){
            this.delTypes2()
            this.collapseId=''
            this.groupIsActived=''
            this.id=''
            this.showAllButton=true
          }else{
            this.dialogVisibleDelTypes = true;
          }
        },
        //点击删除问题按钮
        delAllOne(question){
          this.delVisible=true;
          this.delArr = []
          this.delArr.push(question.record_id)
        },
        // 以上为修改版

        //发请求获取每个问题的详细答案
        itemit(val){
          if(val){
            this.collapseId = val.record_id
            this.editQuestionDisabled = false
            this.deleteQuestionDisabled = false
          }else{
            this.collapseId=''
          }
          this.record_id = val.record_id
          var params = {
            "record_id":this.record_id
          }
          this.$api.faq.faqGetOne(params).then(res=>{
            if (res.data.success === 1){
              for(var typei in this.faqqa){
                for(var questionj in this.faqqa[typei].questions){
                  if(this.faqqa[typei].questions[questionj].record_id===val.record_id){
                    this.$set(this.faqqa[typei].questions[questionj],"anwserItem",res.data.data[0].answer)
                  }
                }
              }
              this.ruleForm = res.data.data[0]
            }
            else if (res.data.success === 0){
              this.$message.error('显示详情失败')
              console.log(res.data.msg);
            }
          }).catch(err=>{})
        },
        //发请求获取问答记录
        faqGet(params){
          this.activeNames=[]
          this.$api.faq.faqGet(params).then(res=>{
            if(res.data.success === 1){
              if(res.data.data.length !== 0){
                if(res.data.data.length === 1){
                  if(res.data.data[0].questions.length===0){
                    this.withoutQuestion = true
                    this.withoutGroup = false
                    this.editQuestionDisabled = true
                    this.deleteQuestionDisabled = true
                  }else{
                    this.withoutQuestion = false
                    this.editQuestionDisabled = true
                    this.deleteQuestionDisabled = true
                  }
                }else{
                  this.withoutQuestion=false
                  this.editQuestionDisabled = true
                  this.deleteQuestionDisabled = true
                }
                this.faqqa = res.data.data
								this.faqQaList = []
								for(var i in this.faqqa){
										for(var j in this.faqqa[i]['questions']){
											this.faqQaList.push(this.faqqa[i]['questions'][j])
										}
								}
              }else{
                if(!this.withoutGroup){
                  this.withoutQuestion = true
                }
              }
            }else if (res.data.success===0){
              this.$message.error('获取分类失败')
              console.log(res.data.msg)
            }
          }).catch(err=>{})
        },
        //发请求问题类型下拉框的值
        qsTypes(){
          this.$api.faq.faqTypesGet().then(res=>{
            if (res.data.success === 1){
              if(res.data.data.length !== 0){
                this.withoutGroup = false
                this.addQuestionDisabled=false
                this.options = res.data.data
                this.groupIsActived = this.options.id
                this.faqGet()
              }else {
                this.withoutGroup = true
                this.addQuestionDisabled=true
                this.withoutQuestion = false
                this.options=[]
                this.faqGet()
              }
            }
            else if (res.data.success === 0){
              this.$message.error('获取分类失败')
              console.log(res.data.msg);
            }
          }).catch(err=>{})
        },
        //发请求修改问题
        dialogVisibleEditOk(){
          if ( this.ruleForm.classification.constructor===String ){
            var typeId = this.ruleForm.id
          }else{
            var typeId = this.ruleForm.classification
          }
          var params = {
            "classification":typeId,
            "question":this.ruleForm.question,
            "answer":this.ruleForm.answer,
            "record_id":this.ruleForm.record_id
          }
          this.$api.faq.faqPut(params).then(res =>{
            if (res.data.success === 1){
              this.$message.success('修改成功')
              this.groupIsActived=''
              this.showAllButton = true
              this.id=''
              var params = {
                "id":this.id
              }
              this.faqGet(params)
              // this.faqGet() //刷新页面
              this.editIsShow = false;													//关闭提示框
            }
            else if (res.data.success === 0){
              this.$message.error('修改失败')
              console.log(res.data.msg);
            }
          }).catch(err=>{})
        },
        //发请求确认增加问题
        dialogVisibleAdd(){
          var params = {
            "classification":this.addForm.classificationes,
            "question":this.addForm.question,
            "answer":this.addForm.answer,
            'creator':this.addForm.creator,
          }
          this.$api.faq.faqPost(params).then(res =>{
            if (res.data.success === 1){
              this.$message.success('添加成功')
              this.add = false;																	//关闭提示框
              this.groupIsActived=''
              this.showAllButton = true
              this.id=''
							this.MeetingSearch=''
              var params = {
                "id":this.id,
								
              }
              this.faqGet(params)
            }
            else if (res.data.success === 0){
              if(res.data.msg==="non_field_errors\u95ee\u9898\u5df2\u5b58\u5728\uff0c\u8bf7\u4fee\u6539\u540e\u91cd\u8bd5\uff01"){
                this.$message.error("\u95ee\u9898\u5df2\u5b58\u5728\uff0c\u8bf7\u4fee\u6539\u540e\u91cd\u8bd5\uff01")
              }else{
                this.$message.error('添加失败')
              }
              this.add = false;
            }
          }).catch(err=>{
						this.add = false;
					})
        },
        //发请求增加分类
        dialogVisibleAddTypes(){
          this.$api.faq.faqTypesPost(this.addQuestionsTypes).then(res =>{
            if (res.data.success === 1){
              this.$message.success('添加成功')
              this.addTypes = false;
              this.qsTypes()
            }
            else if (res.data.success === 0){
              if(res.data.msg==="classification\u5206\u7c7b\u5df2\u5b58\u5728\uff0c\u8bf7\u4fee\u6539\u540e\u91cd\u8bd5\uff01"){
                this.$message.error('\u5206\u7c7b\u5df2\u5b58\u5728\uff0c\u8bf7\u4fee\u6539\u540e\u91cd\u8bd5\uff01')
              }else{
                this.$message.error('添加失败')
              }
              this.addTypes = false;
            }
          }).catch(err=>{
						this.addTypes = false;
					})
        },
        //发请求修改确认
        dialogVisibleModifyTypes(){
          var params={
            "classification":this.modifyQuestionsTypes.newClassIfiCation,
            'id':this.modifyQuestionsTypes.classification
          }
          // 修改问题类型名称
          this.$api.faq.faqTypesPut(params).then(res =>{
            if (res.data.success === 1){
              this.$message.success('修改成功')
              this.qsTypes()
              this.modifyQsTypes = false;
            }
            else if (res.data.success === 0){
              this.$message.error('修改失败')
              console.log(res.data.msg);
            }
          }).catch(err=>{
					})
        },
        //发请求删除问题分类
        delTypes2(){
					this.delArr = []
          this.delArr.push(this.delValue.classificationes)
          var param = {"ids":this.delArr}
          this.$api.faq.faqTypesDelete(param).then(res =>{
            if (res.data.success === 1){
              this.$message.success('删除成功')
              this.dialogVisibleDelTypes = false;
              this.qsTypes()//刷新页面
            }
            else if (res.data.success === 0){
              this.$message.error('删除失败,请重新选择要删除的数据')
							this.dialogVisibleDelTypes = false;
            }
          }).catch(err=>{
						this.dialogVisibleDelTypes = false;
					})
        },
        //发请求确认删除问题
        delAll(){
          var param = {"ids":this.delArr}
          this.$api.faq.faqDelete(param).then(res =>{
            if (res.data.success === 1){
              this.$message.success('删除成功')
              var params = {
                "id":this.id
              }
              this.faqGet(params)
              this.delVisible = false; //关闭提示框
              this.dialogVisibleDelTypes = false;
            }
            else if (res.data.success === 0){
              this.$message.error('删除失败')
							this.delVisible = false; //关闭提示框
							this.dialogVisibleDelTypes = false;
              console.log(res.data.msg);
            }
          }).catch(err=>{
						this.delVisible = false; //关闭提示框
						this.dialogVisibleDelTypes = false;
					})
        },
      },
      mounted(){																									//初始化加载
        this.qsTypes();
        // window.addEventListener('scroll', this.scrollToTop)
      },

      destroyed () {
        // window.removeEventListener('scroll', this.scrollToTop)
      },
    }
  </script>
  <style>
    #backTop{
      position:relative;
      right:25px;
      bottom:20px;
    }
    /*以下为修改版样式调整*/
    /* 设置除侧边栏外的部分样式 */
    .faqInfo{
      position: fixed;
      height:calc(100vh - 61px);
      background-color: #232629;
      z-index: 1020;
    }
    .faqInfo-group-collapse{
      height: 40px;
      width: 14px;
      border: 1px solid #787c81;
      text-align: center;
      vertical-align: middle;
      line-height:40px;
      cursor: pointer;
      position:absolute;
      top:calc((100vh - 60px) / 2);
      z-index: 1000;
			background: #232629;
    }

    .faqInfo-siderbar-scrollbar{
      height: 100%;
    }

    .faqAllit .el-scrollbar .el-scrollbar__wrap {
      overflow-x: hidden;overflow-y: auto;
    }

    .faqInfo-column{
      padding-top: 16px;
      padding-right: 20px;
    }
    .keda-faq .classQuestion { 																						/* 设置弹出框的长宽高 */
      margin-left: 30%;
      /*height: 500px;*/
      margin-bottom: 0;
      overflow: auto;
    }
    .keda-faq .el-textarea__inner{
      background-color: #1f2122;
      border-radius: 0;
      border: 1px solid #383b3c;
      height: 215px;
    }
    .keda-faq .el-dialog__body{
      padding: 0 35px;
    }
    .keda-faq .el-dialog__footer{
      padding-top: 0px;
    }
    .keda-faq .el-textarea__inner::-webkit-input-placeholder {
      color:#5d6266;
      font-size: 12px;
    }

    .faq-siderbar-tree {
      box-sizing: border-box;
      /*padding: 16px 24px 16px 10px;*/
    }
    .keda-faq .el-tree-node__content.is-active{
      background-color: transparent;
      color: #299dff;
    }
    .keda-faq .el-tree-node__content{
      height: 30px;
      color: #9ca9b1;
      /*margin-bottom: 10px;*/
    }
    .keda-faq .el-tree-node__content:hover {
      color: #299dff;
      background-color: transparent;
    }
    .keda-faq .collapse__title.is-active{
      background-color: transparent;
      color: #299dff;
    }
    .keda-faq .collapse__title:hover{
      background-color: transparent;
      color: #299dff;
    }
    .keda-faq .collapse__title{
      background-color: #1e2224;
      color:#9ca9b1;
      border:0;
      /*margin-bottom: 9px;*/
    }
    .keda-faq .el-collapse-item__header{
      background-color: #1e2224;
      /*color:#9ca9b1;*/
      border:0;
      /*margin-bottom: 9px;*/
    }
    .keda-faq .el-collapse-item__content,
    .keda-faq .el-collapse-item__wrap{
      padding: 0;
      border: 0;
    }

    .keda-faq .el-collapse{
      border: 0px;
    }

  .addGroupButtonStyle .el-button,
  .addGroupButtonStyle .el-button:hover,
  .addGroupButtonStyle .el-button:focus{
    background-color: transparent;
    padding: 0;
  }
    .answerDetail .el-textarea__inner{
      height: 80px !important;
      background-color: #1f2122;
      border-radius: 0;
      border: 1px solid #383b3c;
      color:#9ca9b1;
      padding: 5px 10px;
      font: 12px "微软雅黑";
    }
    .icon-group-collapse{
      color: #c0c4cc;
      font-size: 12px;
      transform: rotate(0deg);
      transition: transform .3s ease-in-out;
    }
    .icon-group-collapse.active{
      transform: rotate(-180deg);
    }
    .answerDetail .el-textarea__inner::-webkit-input-placeholder {
      color:#5d6266;
      font: 12px "微软雅黑";
    }

  </style>
