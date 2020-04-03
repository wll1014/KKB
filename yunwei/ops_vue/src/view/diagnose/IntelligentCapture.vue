<template>
	<div class='theme-dark'>

		<div style="background: #232629; height: 800px;margin: 20px 20px;padding: 20px 20px;font-size: 14px;" class='theme-dark capture'>
			<!-- 一键抓包 -->
			<div style="color: #fff;margin-bottom: 30px;font-size: 14px;" >一键抓包</div>
			<span style="margin-right: 10px;">抓包对象</span>
			<el-input v-model='oneClickCaptureMeetingPhone' @change="oneClickCaptureYN" placeholder="请输入会议号" style='width: 150px;'></el-input>
			<el-input v-model='oneClickCaptureTerminalE164' @change="oneClickCaptureYN" placeholder="请输入终端E164号" style='width: 150px;margin-right: 20px;'></el-input>
			<el-button @click='oneClickCapture' :disabled="oneClickCaptureDisabled" v-if='beginCapture'>一键抓包</el-button>
			<el-button @click='oneClickCaptureEnd' v-if='endCapture'>结束抓包</el-button>
			<!-- 自定义抓包 -->
			<div style="border:#383838 dashed 1px;margin-top: 40px;"></div>
			<div style="color: #fff;margin-bottom: 30px;font-size: 14px;margin-top: 40px;" >自定义抓包</div>
			<span style="margin-right: 10px;">抓包对象</span>
      <el-select
        v-model="captureObjType"
        placeholder="服务器"
        style='width:100px;'
        popper-class="theme-dark">
        <el-option
          v-for='item in objType'
          :key='item.label'
          :label='item.label'
          :value='item.label'></el-option>
      </el-select>
			<el-input v-model="IPAddress" placeholder="请输入IP地址" style='width: 230px;' @change='IpCheck'></el-input>
			<el-select
				v-model="internet"
				placeholder="全部网口"
				style='width:100px;'
				popper-class="theme-dark">
				<el-option
					v-for='item in ipPort'
					:key='item.label'
					:label='item.label'
					:value='item.label'></el-option>
			</el-select>
			<el-select
				v-model="protocol"
				placeholder="全部协议"
				style='width:100px;'
				popper-class="theme-dark"
        v-if="captureObjType==='服务器'">
				<el-option
					v-for='item in protocols'
					:key='item.label'
					:label='item.label'
					:value='item.label'></el-option>
			</el-select>
			<el-input v-model='selfCapturePort' placeholder="请输入端口,多个端口请用'、'分隔" style='width: 250px;' v-if="captureObjType==='服务器'"></el-input>
			<!--<el-button icon="el-icon-circle-plus-outline" circle style='margin-left: 20px;' @click='addToCaptureList'></el-button>-->
      <!--<div class="theme-dark" style="padding: 0px;width: 26px">-->
        <!--<button icon="el-icon-plus" style='width: 26px' @click="addToCaptureList" :disabled="addSelfCaptureDisabled" circle ></button>-->
        <el-button icon="ops-icons-bg icon-arrow-circle-add" @click="addToCaptureList"  :disabled="addSelfCaptureDisabled" circle style="padding: 0;border: none;position: absolute"></el-button>
      <!--</div>-->
      <br>
			<span style="margin-right: 10px;margin-top: 30px;">时长设置</span>
			<el-input v-model='inputTime' placeholder="时间限制60秒" style='width: 150px;margin-top: 30px;' @keyup.native="inputRules(inputTime)"></el-input>
			<span>&nbsp;秒</span>
			<el-form  class='theme-dark' :inline="true" :model="captureForm" style='margin-top: 20px;'>
				<el-form-item>
					<span>抓包列表</span>
					<span v-if='alreadyBeginCapture'>
						<span>开始时间</span>
						<span >已抓时间</span>
            <span>{{timeAlreadyUse}}</span>
					</span>

				</el-form-item>
				<el-form-item style="float: right;">
					<el-button @click='BeginCapture' v-if='selfBeginCapture' :disabled="beginCaptureDisabled">开始抓包</el-button>
					<el-button @click='overCapture' v-if='selfOverCapture'>结束抓包</el-button>
					<el-button @click='DownCapture' :disabled='downFiles'>下载抓包文件</el-button>
					<el-button @click='EndCapture' :disabled='clearAll'>清空</el-button>
				</el-form-item>
			</el-form>
			<el-table :data="captureSetting" style='height: 400px;background: none;' stripe>
				<el-table-column type='index' label='序号' width="50px"></el-table-column>
				<!-- <el-table-column label='抓包对象' prop='object'></el-table-column> -->
				<el-table-column label='ip' prop='ip'></el-table-column>
				<el-table-column label='网口' prop='internet'></el-table-column>
				<el-table-column label='协议' prop='protocol'></el-table-column>
				<el-table-column label='端口' prop='selfCapturePort'></el-table-column>
				<el-table-column label='操作'>
					<template slot-scope="scope">
						<button type="button" class="button-host-info" @click="editCapture(scope.$index,captureSetting)">
							<span style="text-decoration: underline;">编辑</span>
						</button>
						<button type="button" class="button-host-info" @click="delCapture(scope.$index,captureSetting)">
							<span style="text-decoration: underline;">删除</span>
						</button>
					</template>
				</el-table-column>
			</el-table>
		</div>

		<!-- 各种弹出框 -->
		<!-- 编辑按钮弹出框 -->
		<el-dialog title="编辑" center :close-on-click-model='false' width="300px" :visible.sync="addCaptureObjectEdit" >
			<div style="height: 150px;">
			<el-input v-model="edit.ip" placeholder="请输入IP地址" style='padding-bottom: 10px;' @change='IpCheck'></el-input><br>
			<el-select
				v-model="edit.internet"
				placeholder="全部网口"
				style='padding-bottom: 10px;'
				popper-class="theme-dark">
				<el-option
					v-for='item in ipPort'
					:key='item.label'
					:label='item.label'
					:value='item.label'></el-option>
			</el-select><br>
			<el-select
				v-model="edit.protocol"
				placeholder="全部协议"
				style='padding-bottom: 10px;'
				popper-class="theme-dark"
        v-if="captureObjType==='服务器'">
				<el-option
					v-for='item in protocols'
					:key='item.label'
					:label='item.label'
					:value='item.label'></el-option>
			</el-select><br>
			<el-input v-model='edit.selfCapturePort' placeholder="请输入端口,多个端口请用'、'分隔" style='padding-bottom: 10px;' v-if="captureObjType==='服务器'"></el-input>
			</div>
			<div align='center' slot='footer' class='theme-dark' style='margin-top:30px;'>
				<el-button @click='dialogSaveEdit(edit)'>保存</el-button>
				<el-button @click='addCaptureObjectEdit = false'>取消</el-button>
			</div>
		</el-dialog>
		<!-- 文件生成中提示框 -->
		<el-dialog title="提示" center :close-on-click-modal="false" width="20%" :visible.sync="captureFileing">
			<div style="color: #fff;">文件已生成中，请稍后......</div>
			<span slot="footer" class="dialog-footer">
				<el-button @click="captureFileing = false">取 消</el-button>
			</span>
		</el-dialog>

		<!-- 文件生成后提示框 -->
		<el-dialog title="提示" center :close-on-click-modal="false" width="20%" :visible.sync="captureFileDown">
			<div style="color: #fff;">文件完成生成，请下载抓包文件</div>
			<span slot="footer" class="dialog-footer">
				<el-button >
					<a :href="oneClickUrl" style='padding-right: 10px;' @click="updown" :download='downname'></a></el-button>
			</span>
		</el-dialog>

		<!-- 二次抓包提示框 -->
		<el-dialog title="提示" center :close-on-click-modal="false" width="20%" :visible.sync="captureBeginAgain">
			<div style="color: #fff;">已存在抓包文件，继续抓包将进行覆盖。<br>是否进行继续抓包？</div>
			<span slot="footer" class="dialog-footer">
				<el-button  @click="BeginCapture">确 定</el-button>
				<el-button @click="captureBeginAgain = false">取 消</el-button>
			</span>
		</el-dialog>

		<!-- 清空提示框 -->
		<div class='clearCapture'>
			<el-dialog title="提示" :visible.sync="clearVisible" center :close-on-click-modal="false" width="20%" >
				<div style="color: #fff;">确定清空所有对象及抓包文件？</div>
				<span slot="footer" class="dialog-footer">
					<el-button  @click="clearRowAll">确 定</el-button>
					<el-button @click="clearVisible = false">取 消</el-button>
				</span>
			</el-dialog>
		</div>

		
		</div>

</template>

<script>
	export default{
    components:{
      KdTabCommon: () => import('@/components/common/KdTabCommon.vue'),
    },
		data() {
			return {
				captureBeginAgain:false,
				selfBeginCapture:true,				//自定义抓包开始按钮
				selfOverCapture:false,				//自定义抓包结束按钮
				downFiles:true,
				clearAll:true,
				alreadyBeginCapture:false,		//开始抓包后显示
				oneClickCaptureDisabled:true, //设置一键抓包键是否可点
        beginCaptureDisabled:true,   //设置开始抓包按钮是否可点
        addSelfCaptureDisabled:true,        //设置自定义抓包添加按钮是否可点
				oneClickCaptureMeetingPhone:'',//一键抓包会议号码
				oneClickCaptureTerminalE164:'',//一键抓包e164号
				endCapture:false,//一键抓包结束按钮是否显示
				beginCapture:true,//一键抓包按钮是否显示
				oneClickUrl:'',
				captureFileDown:false,	//下载抓包文件
				captureFileing:false,		//抓包未完成提示
				clearVisible:false,
				task_id:'',
				IPAddress:'',
				protocol:'全部协议', 				//协议
				protocols:[
					{	label:'全部协议',
						value:0
					},{
						label:'TCP协议',
						value:1
					},{
						label:'UDP协议',
						value:2
					}
				],
				internet:'全部网口',					//网口
        captureObjType:"服务器",            //抓包对象类型选择
        objType:[
          {
            label:'服务器',
            value:1
          },{
				    label:'终端',
            value:2
          }
        ],
				ipPort:[],				//网口下拉框列表
				addCaptureObjectEdit:false, //列表编辑
				edit:{},										//编辑详情
				selfCapturePort:'',
				inputTime:'',
				captureForm:{},
				captureSetting:[],
				downname:'',
				index:'',
        timeAlreadyUse:'',        //抓包已进行时长
			}
		},
		methods:{
      //输入框限制规则
      inputRules(val){
        if(!Number(val)||Number(val)>60){
          this.inputTime = ''
        }
      },
			//判断是否将一键抓包按钮设置为可点击
			oneClickCaptureYN(){
				if(this.oneClickCaptureMeetingPhone && this.oneClickCaptureTerminalE164){
					this.oneClickCaptureDisabled = false
				}else{
					this.oneClickCaptureDisabled = true
				}
			},
			//点击一键抓包进行抓包
			oneClickCapture(){
				var params = {
					'conf_id':this.oneClickCaptureMeetingPhone,
					"device_id":this.oneClickCaptureTerminalE164
				}
				this.$api.intelligentCapture.oneClickCapture(params).then(res=>{
					if (res.data.success === '1'){
						this.beginCapture = false
						this.endCapture = true
						this.task_id = res.data.task_id
					}else{
						// console.log(res.data.msg)
					}
				})
			},
			oneClickCaptureEnd(){
				//判断是否结束抓包
				this.$api.intelligentCapture.endOneClickCapture().then(res=>{
					if (res.data.success === 1){
						if (res.data.data.info[0].status ===1 ){
							//状态为1时
							this.task_id = res.data.data.info[0].task_id
							this.captureFileDown = true
							this.$api.intelligentCapture.downOneClickCaptureFile(this.task_id).then(rest=>{
								if(rest.data.success === 1){
									this.oneClickUrl = rest.data.url
								}
							})
						}else if (res.data.data.info[0].status === 0){
							this.captureFileing = true
						}
					}else if (res.data.success === 0){
						// console.log(msg)
					}
				})
			},
			// 检验ip是否合法
			IpCheck(){
				//检验ip是否合法
        var ip = this.IPAddress
        var re=/^(\d+)\.(\d+)\.(\d+)\.(\d+)$/;//正则表达式
        if(re.test(ip)){
          if( RegExp.$1<256 && RegExp.$2<256 && RegExp.$3<256 && RegExp.$4<256){
            this.getIpIntPort()
            this.addSelfCaptureDisabled = false
            return true
          }else{
            this.$message("IP有误！");
            this.addSelfCaptureDisabled = true
            return false
          }
        }else{
          this.$message("IP有误！");
          this.addSelfCaptureDisabled = true
          return false
        }
			},
      //发送获取网口请求
      getIpIntPort(){
			  var params = {
			    "ip":this.IPAddress
        }
        this.$api.intelligentCapture.getOneIpNetPort(params).then(res=>{
          //将网口信息输入到下拉框中
        })
      },
			//自定义抓包添加对象到列表
			addToCaptureList(){
			  if (this.IpCheck()){
          var params = {
            "type":this.captureObjType,
            "ip":this.IPAddress,
            "internet":this.internet,
            "protocol":this.protocol,
            "selfCapturePort":this.selfCapturePort
          }
          this.captureSetting.push(params)
          this.IPAddress = ''
          this.addSelfCaptureDisabled = true
          this.selfCapturePort=''
        }

			},
			editCapture(index,captureSetting){									//编辑列表元素
				this.index = index
				this.addCaptureObjectEdit = true
				// console.log(value[index])
				this.edit = captureSetting[index]
			},
			dialogSaveEdit(edit){													//报存编辑信息
				this.captureSetting[this.index] = edit
				this.addCaptureObjectEdit = false
			},
			delCapture(index,captureSetting){															//删除元素
				captureSetting.splice(index,1)
			},
			BeginCapture(){									//开始抓包
				//整合所需列表内容，发送请求,将开始抓包按钮变为结束抓包按钮
				//时间未放到params中
				// console.log(this.captureSetting)
				//发请求判断是否存在文件，若存在则
				
				if (this.captureSetting.length !== 0){
					var params = {
						"data":this.captureSetting
					}
					this.$api.intelligentCapture.selfBeginCapture(params).then(res=>{
						if(res.data.success === 1){
							this.task_id = res.data.task_id
							this.selfOverCapture = true
							this.selfBeginCapture = false
						}
					}).catch(
					  err=>{}
          )
				}else{
					this.$message('请自定义抓包')
				}
			},
			DownCapture(){
				//发送请求看抓包是否完成，完成按钮可用，发送请求进行抓包下载
				this.$api.intelligentCapture.downCaptureFiles().then(res=>{
					if(res.data.success === 1){
						
					}
				})
			},
			overCapture(){		//自定义抓包结束按钮
				// 点击结束抓包按钮提示未结束抓包，若结束成功 失败均有提示
				this.$api.intelligentCapture.endCapture(this.task_id).then(res=>{
					//未结束抓包
					if(1){
						this.captureFileing = true
					}else{
						//结束抓包
						this.downFiles = true
						this.clearAll = true
						this.selfOverCapture = false
						this.selfBeginCapture = true
						this.$message('抓包结束')
						this.captureFileing = false
					}
					
					
					//未成功提示框
				})
			},
			EndCapture(){			//清空按钮
				this.clearVisible = true
			},
			updown(){														//点击下载文件
				//请求抓包文件url
			},
			clearRowAll(){											//清空已下载文件
				// 发送请求进行已下载文件清空处理
				this.$api.intelligentCapture.clearFiles().then(res=>{
					
				})
			},
		},

	}
</script>

<style>
	
</style>
