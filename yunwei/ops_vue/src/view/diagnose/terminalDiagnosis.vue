<template >
    <div class="terminalDiagnosis theme-dark"  v-loading='diagnoing' element-loading-background="rgba(0, 0, 0, 0.5)" element-loading-text="诊断中...请稍候" element-loading-spinner="el-icon-loading">
      <!--终端诊断上方-->
      <div class="terminalDiagnosisTop">
        <div class="terminalDiagnosisFont">终端诊断</div>
        <div>
          <span class="terminalDiagnosisObj">诊断对象</span>
          <el-input @input="inputChange" maxlength="100" class="terminalDiagnosisInput" @keydown.enter.native='searchResult' v-model="inputCondition" clearable placeholder="请输入终端名称、E164号、IP" style='font-size:14px ;width: 230px;'></el-input>
          <el-button  @click="searchResult" :disabled="searchDisabled">诊断</el-button>
          <div  style="padding-top: 20px;font-size: 14px;padding-left: 25px;">
            <span style="padding-right: 10px;color: #5d6266;">诊断时间</span>
            <span>{{ diagnosisTime }}</span>
          </div>
        </div>
      </div>
      <!--终端诊断下方-->
      <!--无数据时显示-->
      <div style="position: relative;  margin-top:280px;text-align: center;min-height: 320px" v-if="withoutData===true">
        <span v-if="!withoutInfo">尚无诊断内容，请填写设备进行诊断</span>
				<span v-if="withoutInfo">该终端尚无诊断内容</span>
      </div>
      <!--有数据时显示数据-->
      <div style="min-height: 600px;" v-if="withoutData===false">
        <!--基础信息-->
        <div>
          <div class="peripheralInfo">账号信息</div>
          <div style="margin-left: 25px;font-size: 14px">
						<span style="width: 335px;display: inline-block">
              <span style="width: 110px;display:inline-block;color: #5d6266;font-size: 14px">账号名称</span><span>{{ baseInfo.name }}</span>
            </span>
            <span style="width: 335px;display: inline-block">
              <span style="width: 110px;display:inline-block;color: #5d6266;font-size: 14px">E164号</span><span>{{ baseInfo.e164 }}</span>
            </span>
            <span style="width: 335px;display: inline-block">
              <span style="width: 110px;display:inline-block;color: #5d6266;font-size: 14px">所属用户域</span><span>{{ baseInfo.user_domain_name }}</span>
            </span>
          </div>
          <div style="margin: 25px;">
           <div style="margin-top: 20px;min-height: 40px;margin-bottom: 10px;">
            <span style="width: 110px;display:inline-block;color: #5d6266;font-size: 14px;float: left;height: 40px;">角色信息</span>
             <span v-if="role.length===0">{{ " ----" }}</span>
            <span v-for="(roleInfo,index) in role" :key="index" v-if="role.length!==0">
							<span style="border: 1px solid #3D4046;padding: 4px;margin-right: 4px;color: #9ca9b1;display:inline-block;" v-if="roleInfo.status===1">{{ roleInfo.desc }}</span>
						</span>
          </div>
          <div style="margin-top: 20px;min-height: 40px;margin-bottom: 10px;">
            <span style="width: 110px;display:inline-block;color: #5d6266;font-size: 14px;float: left;height: 40px;">已开启权限</span>
            <span v-for="(privilegeInfo,index) in privilege" :key="index" >
							<span v-if='privilegeInfo.status===1' style="border: 1px solid #3D4046;padding: 4px;margin-right: 4px;color: #9ca9b1;margin-bottom: 4px;display:inline-block;">{{ privilegeInfo.desc }}</span>
						</span>
          </div>
					<div style="height: 2px;"> </div>
          <div  style="margin-top: 20px;min-height: 40px;margin-bottom: 10px;">
            <span style="width: 110px;display:inline-block;color: #5d6266;font-size: 14px;float: left;height: 40px;">未开启权限</span>
            <span v-for="(privilegeInfo,index) in privilege" :key="index" style="">
							<span v-if='privilegeInfo.status===0'  style="border: 1px solid #3D4046;padding: 4px;margin-right: 4px;margin-bottom: 4px;color: #9ca9b1;display:inline-block;">
								{{ privilegeInfo.desc }}
							</span>
						</span>
          </div>
					<div style="height: 2px;"> </div>
          <div style="margin-top: 20px;min-height: 30px;">
						<span style="width: 110px;display:inline-block;color: #5d6266;font-size: 14px;height: 60px;float: left;" v-if="enable_device.length<50&&enable_device.length>30">可登录设备</span>
            <span style="width: 110px;display:inline-block;color: #5d6266;font-size: 14px;height: 40px;float: left;" v-if="enable_device.length<=30">可登录设备</span>	
						<span style="width: 110px;display:inline-block;color: #5d6266;font-size: 14px;height: 100px;float: left;" v-if="enable_device.length>=50">可登录设备</span>				
						<span v-for="(deviceInfo,index) in enable_device" :key="index" >
							<span style="border: 1px solid #3D4046;padding: 4px;margin-right: 4px;color: #9ca9b1;display:inline-block;margin-bottom: 4px;">{{ deviceInfo }}</span>
						</span>
          </div>
        </div>
        </div>
        <!-- 选择设备界面 -->

        <!--tab以下展示信息-->
        <div v-if="!withoutTab">
          <div style="margin-left: 25px;margin-bottom: 20px;font-size: 16px;color: #299dFF;">
            <el-select
              v-model="loginDevice"
              placeholder="尚无在线终端"
              style='width:180px;margin-right: 7px'
              popper-class="theme-dark"
              @change='changeSearch(loginDevice)'>
              <el-option
                v-for='item in loginDeviceList'
                :key='item.value'
                :label='item.value'
                :value='item.value'></el-option>
            </el-select>
          </div>
          <!--tab界面-->
          <div style="margin-left: 25px;margin-bottom: 20px;font-size: 16px;color: #299dFF;">
            <KdTabCommon :tab-list="tabList" :active-tab="activeTab"  class-name="tab-alarm" @tab-change="tabChange"></KdTabCommon>
          </div>
          <!--基本信息-->
          <div v-if="activeTab==='resgiInfo'">
            <div style="margin-left: 25px;font-size: 14px">
						<span style="width: 335px;display: inline-block">
              <span style="width: 110px;display:inline-block;color: #5d6266;font-size: 14px">终端版本</span>
							<span>{{ registrationInfo.version}}</span>
            </span>
              <span style="width: 335px;display: inline-block">
						    <span style="width: 110px;display:inline-block;color: #5d6266;font-size: 14px">终端序列号</span>
								<span>{{registrationInfo.SN }}</span>
						</span>
              <span style="width: 335px;display: inline-block">
						    <span style="width: 110px;display:inline-block;color: #5d6266;font-size: 14px">注册状态</span>
								<span v-if="registrationInfo.register_status===1">成功</span>
                <span v-if="registrationInfo.register_status===0">失败</span>
                <span v-if='registrationInfo.register_status===" ----"'>{{registrationInfo.register_status}}</span>
						</span>
              <span style="display: inline-block">
						  <span style="width: 110px;display:inline-block;color: #5d6266;font-size: 14px">协议类型</span>
							<span>{{ registrationInfo.register_protocol }}</span>
						</span>
            </div>
            <div style="margin: 25px;font-size: 14px">
            <span style="width:335px;display: inline-block">
              <span style="width: 110px;display:inline-block;color: #5d6266;font-size: 14px">注册服务器地址</span>
							<span>{{ registrationInfo.pas_ip }}</span>
            </span>
              <span style="width: 335px;display: inline-block;">
						  <span style="width: 110px;display:inline-block;color: #5d6266;font-size: 14px">NAT状态</span>
							<span >{{ registrationInfo.nat_status }}</span>
						</span>
              <span style="width: 335px;display: inline-block;">
						  <span style="width: 110px;display:inline-block;color: #5d6266;font-size: 14px">DMZ状态</span>
							<span>{{registrationInfo.dmz}}</span>
						</span>
              <span style="display: inline-block">
						  <span style="width: 110px;display:inline-block;color: #5d6266;font-size: 14px">呼叫协议</span>
              <span v-if="registrationInfo.call_protocol===1">标准</span>
              <span v-if="registrationInfo.call_protocol===0">非标</span>
              <span v-if='registrationInfo.call_protocol===" ----"'>{{registrationInfo.call_protocol}}</span>
						</span>
            </div>
            <div style="display: inline-block;margin-left: 25px;margin-bottom: 25px;font-size: 14px">
						<span style="width: 335px;display: inline-block">
							<span style="width: 110px;display:inline-block;color: #5d6266;font-size: 14px">代理服务器状态</span>
              <span v-if="registrationInfo.proxy_status===1">正常</span>
              <span v-if="registrationInfo.proxy_status===0">异常</span>
              <span v-if='registrationInfo.proxy_status===" ----"'>{{registrationInfo.proxy_status}}</span>
						</span>
              <span style="width: 335px;display: inline-block">
							<span style="width: 110px;display:inline-block;color: #5d6266;font-size: 14px">代理服务器IP</span>
							<span>{{ registrationInfo.proxy_ip }}</span>
						</span>
              <span style="width: 335px;display: inline-block">
							<span style="width: 110px;display:inline-block;color: #5d6266;font-size: 14px">H323监听端口</span>
							<span>{{ registrationInfo.h323_port }}</span>
						</span>
            </div>
            <div style="height: 600px;" v-show="activeTab==='resgiInfo'">
              <div style="float: right;margin: 30px 0 0 0;" v-if="terminalPicInfo">
                <span style="color: #9ca9b1;float: right;margin-right: 39px;font-size: 14px;">未连接</span>
                <i class="ops-icons-bg icon-legend-orange" style="float: right;margin-right: 7px;margin-top: 8px"></i>
                <span style="color: #9ca9b1;float: right;margin-right: 35px;font-size: 14px;">已连接</span>
                <i class="ops-icons-bg icon-legend-blue" style="float: right;margin-right: 7px;margin-top: 8px"></i>
              </div>
              <div id="termianlDiaChartID" style="height: 100%; width: 100%;padding-top: 20px"></div>
              <!--<terminalDiagnosisPic :terminalPicInfo="terminalPicInfo" style="height: 600px"></terminalDiagnosisPic>-->
            </div>
          </div>
          <!-- 状态信息 -->
          <div v-if="activeTab==='statusInfo'" style="font-size: 14px">
            <!-- <div class="peripheralInfo" style="border-top: #3d4046 1px dashed ;">状态信息</div> -->
            <div style="display: inline-block;margin-left: 25px;margin-bottom: 25px;font-size: 14px">
						<span style="width: 335px;display: inline-block;">
						  <span style="width: 110px;display:inline-block;color: #5d6266;font-size: 14px">终端系统时间</span>
							<span>{{ statusInfoObj.os_time }}</span>
						</span>
              <span style="width: 335px;display: inline-block;">
						  <span style="width: 110px;display:inline-block;color: #5d6266;font-size: 14px">CPU使用率</span>
              <span v-if="statusInfoObj.cpu_userate !==' ----'">{{ statusInfoObj.cpu_userate  }}%</span>
              <span v-if="statusInfoObj.cpu_userate ===' ----'">{{ statusInfoObj.cpu_userate  }}</span>
						</span>
              <span style="width: 335px;display: inline-block;">
						  <span style="width: 110px;display:inline-block;color: #5d6266;font-size: 14px">内存总量</span>
              <span v-if="statusInfoObj.mem_total !==' ----'">{{ statusInfoObj.mem_total  }}M</span>
              <span v-if="statusInfoObj.mem_total ===' ----'">{{ statusInfoObj.mem_total  }}</span>
						</span>
              <span style="display: inline-block;">
						  <span style="width: 110px;display:inline-block;color: #5d6266;font-size: 14px">已用内存</span>
							<span v-if="statusInfoObj.mem_use !==' ----'">{{ statusInfoObj.mem_use  }}M</span>
              <span v-if="statusInfoObj.mem_use ===' ----'">{{ statusInfoObj.mem_use  }}</span>
						</span>
            </div>
            <div style="display: inline-block;margin-left: 25px;margin-bottom: 25px;font-size: 14px">
						<span style="width: 335px;display: inline-block;">
						  <span style="width: 110px;display:inline-block;color: #5d6266;font-size: 14px">可用内存</span>
							<span v-if="statusInfoObj.mem_total!==' ----'&&statusInfoObj.mem_use!==' ----'">{{  statusInfoObj.mem_total-statusInfoObj.mem_use }}M</span>
              <span v-if="statusInfoObj.mem_total===' ----'||statusInfoObj.mem_use ===' ----'"> ----</span>
						</span>
              <span style="width:335px;display: inline-block;">
						   <span style="width: 110px;display:inline-block;color: #5d6266;font-size: 14px">告警状态</span>
							 <span v-if='statusInfoObj.alarm===0'>有</span>
							 <span v-if='statusInfoObj.alarm===1'>无</span>
              <span v-if='statusInfoObj.alarm===" ----"'>{{ statusInfoObj.alarm }}</span>
						</span>
              <span style="width:335px;display: inline-block;">
						   <span style="width: 110px;display:inline-block;color: #5d6266;font-size: 14px">终端状态</span>
							 <span v-if='statusInfoObj.online===0'>离线</span>
							 <span v-if='statusInfoObj.online===1'>在线</span>
              <span v-if='statusInfoObj.online===" ----"'>{{ statusInfoObj.online }}</span>
						</span>
              <span style="display: inline-block;">
						   <span style="width: 110px;display:inline-block;color: #5d6266;font-size: 14px">与会详情</span>
							 <span v-if='statusInfoObj.meeting === 0'>
								 <span>无</span>
							 </span>
							 <span v-if='statusInfoObj.meeting === 1'>
									<button type="button" class="button-host-info" @click="detailTurnRoute(statusInfoObj.confid)" >
										<span style="text-decoration: underline;">详情</span>
									</button>
							 </span>
						</span>
            </div>
            <div style="margin-left: 25px;margin-bottom: 25px;font-size: 14px">
            <span style="width: 335px;display: inline-block;">
						  <span style="width: 110px;display:inline-block;color: #5d6266;font-size: 14px">OSD显示状态</span>
              <span v-if='statusInfoObj.osd===0'>异常</span>
							 <span v-if='statusInfoObj.osd===1'>正常</span>
              <span v-if='statusInfoObj.osd===" ----"'>{{ statusInfoObj.osd }}</span>
						</span>
            </div>
            <div style="margin-left: 25px;margin-right:25px;font-size: 14px;margin-bottom:30px;">
              <span >终端时长</span>
              <el-table tooltip-effect="dark"
                        stripe
                        border
                        style="width: 100%;min-height: 80px;margin-top:25px ;"
                        :data="terminalTime"
              >
                <el-table-column show-overflow-tooltip type="index" label="序号" width="50">
                </el-table-column>
                <el-table-column show-overflow-tooltip  prop="long" label="时间段" >
                </el-table-column>
                <el-table-column show-overflow-tooltip  prop="online" label="运行时长" >
                </el-table-column>
                <el-table-column show-overflow-tooltip  prop="onconf" label="参会时长">
                </el-table-column>
              </el-table>
            </div>
          </div>
          <!--外设信息-->
          <div v-show="activeTab==='peripheral'">
            <!--无数据时显示-->
            <div style="font-size: 16px;color:#9ca9b1;padding-top: 50px;padding-left: 520px;padding-bottom: 50px;margin: 20px;height: 50px" v-show="peripheralWithoutData">
              <span style="margin-right: 10px;"><i class="el-icon-info"></i></span>
              <span >
                尚 无 外 设 相 关 数 据
              </span>
            </div>
            <!-- 表格区域 -->
            <el-table tooltip-effect="dark"
                      stripe
                      border
                      style="width: 100%;min-height: 80px"
                      :data="peripheralList"
                      class="perInfo"
                      :cell-style="changeCellStyle"
                      v-if="!peripheralWithoutData"

            >
              <el-table-column show-overflow-tooltip type="index" label="序号" width="50"></el-table-column>
              <el-table-column show-overflow-tooltip  prop="name" label="外设名称" ></el-table-column>
              <el-table-column show-overflow-tooltip  prop="type" label="外设类型" ></el-table-column>
              <el-table-column show-overflow-tooltip  prop="status" label="状态"></el-table-column>
              <el-table-column show-overflow-tooltip  prop="id" label="产品型号">
                <template slot-scope="scope" >
                  <span >{{ peripheralList[scope.$index].id }}</span>
                </template>
              </el-table-column>
              <el-table-column show-overflow-tooltip  prop="soft_version" label="软件版本信息"></el-table-column>
              <el-table-column show-overflow-tooltip  prop="hard_version" label="硬件版本信息" ></el-table-column>
            </el-table>
          </div>
          <!-- 关键进程信息 -->
          <div v-show="activeTab==='crucial'">
            <div style="font-size: 16px;color:#9ca9b1;padding-top: 50px;padding-left: 520px;padding-bottom: 50px;margin: 20px;height: 50px" v-show="crucialWithoutData">
              <span style="margin-right: 10px;"><i class="el-icon-info"></i></span>
              <span >
                尚 无 进 程 相 关 数 据
              </span>
            </div>
            <el-table tooltip-effect="dark"
                      class="perInfo"
                      stripe
                      border
                      style="width: 100%;min-height: 80px"
                      :data="keyOutList"
                      v-if="!crucialWithoutData">
              <el-table-column show-overflow-tooltip type="index" label="序号" width="50">
              </el-table-column>
              <el-table-column show-overflow-tooltip  prop="process" label="进程名称" >
              </el-table-column>
              <el-table-column show-overflow-tooltip  prop="runtime" label="运行时间" ></el-table-column>
              <el-table-column show-overflow-tooltip  prop="restart" label="重启次数"></el-table-column>
              <el-table-column show-overflow-tooltip  label="操作" >
                <template slot-scope="scope" >
                  <button type="button" class="button-host-info" @click="keyDetailButton(keyOutList[scope.$index])" >
                    <span style="text-decoration: underline;">详情</span>
                  </button>
                </template>
              </el-table-column>
            </el-table>

          </div>
          <!--呼叫-->
          <div v-if="activeTab==='callRecord'">
            <div style="font-size: 16px;color:#9ca9b1;padding-top: 50px;padding-left: 520px;padding-bottom: 50px;margin: 20px;height: 50px" v-show="callRecordWithoutData">
              <span style="margin-right: 10px;"><i class="el-icon-info"></i></span>
              <span >
                尚 无 呼 叫 相 关 数 据
              </span>
            </div>
            <!-- 表格区域 -->
            <el-table tooltip-effect="dark"
                      stripe
                      border
                      style="width: 100%;min-height: 80px"
                      :data="callRecordList"
                      class="perInfo"
                      v-if="!callRecordWithoutData"
                      v-loading='callRecording'
                      element-loading-background="rgba(0, 0, 0, 0.5)"
                      element-loading-text="加载中...请稍候"
                      element-loading-spinner="el-icon-loading"
            >
              <el-table-column show-overflow-tooltip type="index" label="序号" width="50">
              </el-table-column>
              <el-table-column show-overflow-tooltip  prop="time" label="呼叫时间" >
              </el-table-column>
              <el-table-column show-overflow-tooltip  prop="result" label="结果" >
              </el-table-column>
              <el-table-column show-overflow-tooltip  prop="err_msg" label="失败原因">
              </el-table-column>
            </el-table>
            <div style="margin-top: 20px;margin-right: 25px;margin-bottom: 10px;" v-if="!callRecordWithoutData">
              <KdPagination
                @current-change="currentChange"
                :pageSize="this.count"
                :currentPage="currentPage"
                :total="this.total"
                :disabled="pageDisabled">
              </KdPagination>
            </div>
          </div>
        </div>
			</div>
			<el-dialog title='提示' :visible.sync='dialogTerminal' :close-on-click-modal='false' width="800px">
        <div v-if="dialogTerminalList.length!==0">
          <div style='margin-top: 20px;margin-bottom: 10px;'>请选择一个进行诊断</div>
          <el-table stripe  :data='dialogTerminalList' height='400px' style='padding-top: 6px;background: none'>
            <el-table-column prop='account' show-overflow-tooltip label='账号' ></el-table-column>
            <el-table-column prop='e164' label='e164号' show-overflow-tooltip></el-table-column>
            <el-table-column prop='user_domain_name' label='用户域' show-overflow-tooltip></el-table-column>
            <el-table-column prop='status' label='状态' show-overflow-tooltip>
              <template  slot-scope="scope">
                <span v-if="scope.row.status===0">离线</span>
                <span v-if="scope.row.status===1">在线</span>
              </template>
            </el-table-column>
            <el-table-column label='操作' show-overflow-tooltip>
              <template slot-scope="scope">
                <button type="button" class="button-host-info" @click="diagnoseItem(scope.row)">
                  <span>诊断</span>
                </button>
              </template>
            </el-table-column>
          </el-table>
        </div>
				<div v-if="dialogTerminalList.length===0" style="height:400px">
          <span>没有此诊断对象</span>
        </div>
			</el-dialog>
			<el-dialog title='详情' :visible.sync='keyDetail' :close-on-click-modal='false' width="600px">
				<div style="min-height: 300px;">
					<div style="padding-bottom: 20px;padding-top: 20px;">
							<span style="color: #5d6266">进程名称  </span>
							<span style="padding-left: 30px"> {{  keyName  }}</span>
						</div>
						<el-table tooltip-effect="dark"
						          stripe
						          border
						          style=""
						          :data="keyDetailList"
						          :cell-style='changeCellStyle'
						>
						  <el-table-column show-overflow-tooltip type="index" label="序号" width="50">
						  </el-table-column>
						  <el-table-column show-overflow-tooltip  prop="time" label="重启时间" >
						  </el-table-column>
							<el-table-column show-overflow-tooltip  prop="reason" label="重启原因" >
							</el-table-column>
						</el-table>
				</div>
				<div align="center" slot='footer' style="padding-bottom: 10px">
				  <el-button @click='keyDetail=false'>关闭</el-button>
				</div>
			</el-dialog>	
		</div>
</template>

<script>
    export default {
      name: "terminalDiagnosis",
      components: {
        KdTabCommon: () => import('@/components/common/KdTabCommon.vue'),
				ChartExtendLargeModel: ()=> import('@/components/monitor/ChartExtendLargeModel.vue'),
				KdPagination: () => import('@/components/common/KdPagination.vue'),
				terminalDiagnosisPic: () => import('@/view/diagnose/terminalDiagnosisPic.vue'),
      },
      data (){
          return {
            //一级界面
            allData:[],																						//总数据
            searchDisabled:true,																	//诊断按钮是否可点
            diagnoing:false,																			//诊断时蒙版
            diagnosisTime:'',                                     //诊断时间
            inputCondition:'',                                    //输入诊断条件
            withoutData:true,
            withoutInfo:false,
            activeTab:'resgiInfo',
            e164:'',
            //列表数据
            tabList:[
              ['resgiInfo','基本信息'],
              ['statusInfo','状态信息'],
              ['peripheral','外设信息'],
              ['crucial','关键进程'],
              ['callRecord','呼叫记录'],
            ],
            dialogTerminalList:[],																								//点击诊断弹出框列表
            dialogTerminal:false,																									//点击诊断弹出框


            //二级界面

            //账号信息
            baseInfo:{},                                          //账号信息
            role:[],                                              //角色权限列表
            loginDevice:'',																				//多登设备
            loginDeviceList:[],																		//多登设备列表
            enable_device:[],                                      //可登录设备列表
            privilege:[],                                     			//开启与未开启权限列表
            withoutTab:true,
            // 基本信息
            registrationInfos:[],                                  //所有注册信息
            registrationInfo:{},                                   //注册信息
            terminalPicInfo:{0:{}},                                //传入图形界面数据
            option : {},
            // 外设信息
            peripheralWithoutData:true,                            //外设有无信息时展示
            peripheralList:[],                                      //外设信息列表
            // 状态信息
            statusInfoObj:{},
            terminalTime:[],																			//终端时长列表
            // 关键进程
            crucialWithoutData:true,
            keyOutList:[],																				//关键进程列表
            keyDetail:false,																			//进程详情弹出框
            keyDetailList:[],																			//进程列表弹出框
            keyName:'',                                           //进程弹出框显示名称
            // 呼叫记录
            callRecordList:[],                                    //呼叫记录
            callRecording:false,                                  //加载
            callRecordWithoutData:true,
						count:12,                                             //分页组件需要数据
						start:0,
						currentPage:1,
						total:0,

				}
      },
      methods:{
        //tip样式修改
        tooltipList(textList){
          let htmlContent = textList.map((item) => {
            return '<div class="terminalDiagnosisPicTip">' +
              '<div style="width:100px;text-align: right;display:inline-block;">' + item.left + '</div>' +
              '<div style="text-align:left;display:inline-block;padding-left:10px;">' + ':&nbsp&nbsp&nbsp'  + item.right +
              '</div></div>'
          });
          return htmlContent.join('\n')
        },
        //渲染eCharts图形
        chartsInfo(){
          this.option = {
            tooltip: {
              // hideDelay : 100,
              // triggerOn:"mousemove",
              enterable:true,
              padding: [18, 14],
              backgroundColor: '#141414',
              borderColor: '#383b3c',
              borderWidth: 1,
              textStyle: {
                color: '#9ca9b1',
              },
              formatter: (params) =>{
                //根据值是否为空判断是点还是线段
                if(params.data.name){//如果鼠标移动到线条
                  if(params.data.name === "PAS"&&params.data.itemStyle!==undefined){
                    let textList = [
                      {left:"PAS IP " ,right:params.data.info.ip || '----'},
                      {left:"最后注册时间 " ,right:params.data.info.last_register || '----'},
                      {left:"注册机房 " ,right:params.data.info.machineroom || '----'},
                      {left:"最后过NAT IP " ,right:params.data.info.last_nat_ip || '----'},
                      {left:"终端地址+端口 " ,right:params.data.info.dev_ip_port || '----'},
                      {left:"h460状态 " ,right:params.data.info.h460 || '----'},
                      {left:"Moid " ,right:params.data.info.moid || '----'},
                      {left:"产品ID " ,right:params.data.info.product_id || '----'},
                      {left:"设备号 " ,right:params.data.info.dev_id || '----'},
                      {left:"端口复用 " ,right:params.data.info.portreuse || '----'},
                      {left:"传输类型 " ,right:params.data.info.transport_type || '----'},
                      {left:"机房Moid " ,right:params.data.info.machineroom_moid || '----'},
                      {left:"APS登录 " ,right:params.data.info.aps_login || '----'},
                      {left:"网呈终端 " ,right:params.data.info.stp || '----'},
                      {left:"私网终端状态 " ,right:params.data.info.privatenet || '----'},
                      {left:"注册阶段 " ,right:params.data.info.reg || '----'},
                    ];
                    return  this.tooltipList(textList)
                  }else if(params.data.name === "PAS"&&params.data.itemStyle===undefined){
                    let textList = [
                      {left:"PAS IP " ,right:params.data.info.ip || '----'},
                      {left:"最后注册时间 " ,right:params.data.info.last_register || '----'},
                      {left:"未连接原因 " ,right:params.data.info.err_msg || '----'},
                      {left:"ErrCode " ,right:params.data.info.errcode || '----'},
                    ]
                    return  this.tooltipList(textList)
                  }else if(params.data.category === 4){
                  }else{
                    if(params.data.itemStyle!==undefined){
                      return  params.data.name  +" IP ：" + params.data.info.ip
                    }
                  }
                }}
            },
            animationDurationUpdate: 1500,
            animationEasingUpdate: 'quinticInOut',
            // animation : false,
            series: [
              {
                type: 'graph',
                layout: 'force',
                roam: false,
                label: {
                  show: true
                },
                edgeSymbol: ['circle', 'arrow'],
                edgeSymbolSize: [0, 0],  //设置箭头大小
                edgeLabel: {
                  fontSize: 20
                },
                itemStyle : {
                  normal: {
                    borderWidth:1,
                    lineStyle: {
                      width:1.5,
                      type: 'dotted',
                      color:"#5d6266",
                    },
                    color: '#e45959',
                  }
                },
                symbolSize: (value, params) => {
                  //根据数据params中的data来判定数据大小
                  switch (params.data.category) {
                    case 4:return 120;break;
                    default:return 60;
                  }
                },
                data: [],
                // links: [],
                links: [],
                lineStyle: {
                  width: 2,
                  curveness: 0,
                },
                force: {
                  edgeLength:200 ,             //200
                  nodeScaleRatio:0,
                  repulsion: 1000,
                  layoutAnimation: false,//去除echarts动画
                  initLayout:'circular',
                },

              }
            ]
          }
        },
        //诊断输入时判断按钮disabled
        inputChange(){
					if(this.inputCondition){
						this.searchDisabled = false
					}else{
						this.searchDisabled = true
					}
				},
        //tab请求
        tabChange(val){
          this.activeTab=val;
          let params = {
            e164:this.e164,
            terminal:this.loginDevice
          };
          this.terminalTime=[];
          this.peripheralList=[];
          this.keyOutList=[];
          if(val==='resgiInfo'){
            this.changeSearch()
            // this.baseInfoRequest(params)
          }else if(val==='statusInfo'){
            this.terminalStatistic(params);
            this.statusInfoRequest(params)
          }else if(val==='peripheral'){
            this.peripheralInfoRequest(params)
          }else if(val==="crucial"){
            this.crucialInfoRequest(params)
          }else if(val==='callRecord'){
            this.start = 0;
            this.currentPage = 1;
            this.total = 0;
            this.callInfoRequest()
          }
        },
        //终端个数请求
        searchResult(){
						this.diagnoing = true;
						let params = {
						  keyword :this.inputCondition,
						};
						this.$api.terminalDiagnosis.getTerminalAccountInfo(params).then(res=>{
							if(res.data.success===1){
								if(res.data.data.info.length===1){
									this.diagnoseItem(res.data.data.info[0])
								}else if(res.data.data.info.length===0){
									this.$message('未查询到此诊断对象');
									this.withoutData = true;
									this.diagnosisTime='';
									this.diagnoing = false;
                  this.dialogTerminalList=[]
								}else{
									this.dialogTerminal = true;
									this.dialogTerminalList=res.data.data.info;
									this.diagnoing = false
								}
								
							}else{
								this.$message('请求失败');
								this.diagnoing = false
							}
						}).catch(err=>{
							this.diagnoing = false
						})
        },
        //点击诊断按钮
        diagnoseItem(value){
          this.diagnoing = true;
          this.dialogTerminal=false;
          this.e164 = value.e164;
          this.baseInfoRequest({"e164":value.e164});
				  this.accountTerminal({"e164":value.e164})
        },
        //请求终端账号信息
				accountTerminal(params){
					this.$api.terminalDiagnosis.getTerminalDeviceInfo(params).then(res=>{
						if(res.data.success===1){
							if(res.data.data.info){
								this.diagnosisTime=this.timestampToTimes(res.data.data.info.timestamp);
								this.withoutData=false;
								for(let value in res.data.data.info.account){
								  if(res.data.data.info.account[value]===''){
								    res.data.data.info.account[value] = ' ----'
                  }
                }
								this.baseInfo = res.data.data.info.account;
								let rowStatus = true
								for(let i in res.data.data.info.role){
								  if(res.data.data.info.role[i].status===1){
                    rowStatus = false
                  }
                }
                if(rowStatus === true){
                  this.role=""
                }else{
                  this.role = res.data.data.info.role;
                }

								this.enable_device = res.data.data.info.enable_device;
								this.privilege = res.data.data.info.privilege;
							}else{
								this.withoutData = true;
								this.withoutInfo = true
							}
							this.diagnoing = false
						}else {
							this.$message('请求失败');
							this.diagnoing = false
						}
					}).catch(err=>{
            this.$message('请求失败');
						this.diagnoing = false
					})
				},
        //选择设备后取值
        changeSearch(){
				  this.activeTab = "resgiInfo";
          let params={
            e164:this.e164,
            terminal:this.loginDevice
          };
          for(let value in this.registrationInfos){
            if(this.registrationInfos[value].type===this.loginDevice){
              this.registrationInfo = this.registrationInfos[value];
              this.connectInfoRequest(params,this.registrationInfos[value].ip)
            }
          }
        },
        //基本信息请求
        baseInfoRequest(params){
          this.$api.terminalDiagnosis.getTerminalBaseInfo(params).then(res=>{
            // console.log(res.data)
            if(res.data.success===1){
              this.loginDeviceList = [];
              for(let i in res.data.data.info){
                for(let r in res.data.data.info[i]){
                  if(res.data.data.info[i][r]===""){
                    res.data.data.info[i][r]= ' ----'
                  }
                }
                this.loginDeviceList.push({
                  "value":res.data.data.info[i].type
                })
              }
              this.registrationInfos = res.data.data.info;
              if(this.loginDeviceList[0]){
                this.withoutTab = false;
                this.loginDevice = this.loginDeviceList[0].value;
                this.changeSearch()
              }else{
                this.loginDeviceList = [];
                this.loginDevice='';
                this.withoutTab = true;
                this.$message("该诊断对象尚无在线终端")
              }
            }else{
              this.$message("请求失败")

            }
          }).catch(err=>{this.$message("请求失败")})
        },
				//连接信息请求
        connectInfoRequest(params,ip){
          this.$api.terminalDiagnosis.getTerminalConnectInfo(params).then(res=>{
            console.log(res.data.success)
            if(res.data.success===1){
              let listInfo = [];
              let link = [];
              for(let value in res.data.data.info.should_connect){
                listInfo.push({"name":res.data.data.info.should_connect[value]})
              }
              for(let value1 in listInfo){
                if(res.data.data.info.connect.length!==0){
                  for(let value2 in res.data.data.info.connect){
                    if(listInfo[value1].name === res.data.data.info.connect[value2].type){
                      listInfo[value1]["info"] = res.data.data.info.connect[value2].data;
                      listInfo[value1]['itemStyle'] = {color:'#5eb9ef'}
                    }
                  }
                }
                link.push({source:'终端IP' + '\n\n'+ip,target:listInfo[value1].name})
              }
              if(res.data.data.info.should_connect.length!==0){
                listInfo.push({"name":'终端IP' + '\n\n'+ip,category:4,'itemStyle':{color:'#5eb9ef'}})
              }
              let data = {
                data:listInfo,
                link:link
              };
              this.terminalPicInfo = data;
              this.chartsInfo();
              this.option.series[0].data = this.terminalPicInfo.data;
              this.option.series[0].links = this.terminalPicInfo.link;
              let myChart = echarts.init(document.getElementById('termianlDiaChartID'));
              myChart.clear();
              myChart.setOption(this.option,true);
            }else{
              this.$message("请求失败")
            }
          }).catch(err=>{
            this.$message("请求失败");
            console.log(err)
          })
        },
        //状态信息请求
        statusInfoRequest(params){
				  this.$api.terminalDiagnosis.getTerminalStatusInfo(params).then(res=>{
            if(res.data.success===1){
              if(res.data.data.info.length!==0){
                for(let value in res.data.data.info){
                  if(res.data.data.info[value]===""){
                    res.data.data.info[value]=' ----'
                  }else if(value==='os_time'){
                    res.data.data.info[value] = this.timestampToTimes(res.data.data.info[value])
                  }
                }
                this.statusInfoObj = res.data.data.info
              }
            }else{
              this.$message("请求失败")
            }
          }).catch(err=>{this.$message("请求失败")})
        },
        //在线时长请求
        terminalStatistic(params){
          this.$api.terminalDiagnosis.getTerminalStatistic(params).then(res=>{
            if(res.data.success===1){
              if(res.data.data.info.length!==0){
                let terminalTimeInfo = [{},{},{}];
                if(res.data.data.info[0].name==='online_time'){
                  terminalTimeInfo[0]['long'] = "最近一周";
                  terminalTimeInfo[1]['long'] = "最近一个月";
                  terminalTimeInfo[2]['long'] = "最近一年";
                  terminalTimeInfo[0]['online'] = this.timestampToTime(res.data.data.info[0].last_week);
                  terminalTimeInfo[0]['onconf'] = this.timestampToTime(res.data.data.info[1].last_week);
                  terminalTimeInfo[1]['online'] = this.timestampToTime(res.data.data.info[0].last_month);
                  terminalTimeInfo[1]['onconf'] = this.timestampToTime(res.data.data.info[1].last_month);
                  terminalTimeInfo[2]['online'] = this.timestampToTime(res.data.data.info[0].last_year);
                  terminalTimeInfo[2]['onconf'] = this.timestampToTime(res.data.data.info[1].last_year)
                }else{
                  terminalTimeInfo[0]['long'] = "最近一周";
                  terminalTimeInfo[1]['long'] = "最近一个月";
                  terminalTimeInfo[2]['long'] = "最近一年";
                  terminalTimeInfo[0]['online'] = this.timestampToTime(res.data.data.info[1].last_week);
                  terminalTimeInfo[0]['onconf'] = this.timestampToTime(res.data.data.info[0].last_week);
                  terminalTimeInfo[1]['online'] = this.timestampToTime(res.data.data.info[1].last_month);
                  terminalTimeInfo[1]['onconf'] = this.timestampToTime(res.data.data.info[0].last_month);
                  terminalTimeInfo[2]['online'] = this.timestampToTime(res.data.data.info[1].last_year);
                  terminalTimeInfo[2]['onconf'] = this.timestampToTime(res.data.data.info[0].last_year)
                }
                this.terminalTime = terminalTimeInfo
                // console.log(this.terminalTime)
              }
            }else{
              this.$message("请求失败")
            }
          }).catch(err=>{this.$message("请求失败")})
        },
        //外设请求
        peripheralInfoRequest(params){
          this.$api.terminalDiagnosis.getTerminalPeripheralInfo(params).then(res=>{
            if(res.data.success===1){
              if(res.data.data.info.length!==0){
                this.peripheralWithoutData = false;
                for(let value in res.data.data.info){
                  for(let value1 in res.data.data.info[value]){
                    if(res.data.data.info[value][value1] === ""){
                      res.data.data.info[value][value1] = ' ----'
                    }
                    if(value1==="type"){
                      if(res.data.data.info[value][value1]===1){
                        res.data.data.info[value][value1] = "摄像机"
                      }else if(res.data.data.info[value][value1]===2){
                        res.data.data.info[value][value1] = "麦克风"
                      }else if(res.data.data.info[value][value1]===3){
                        res.data.data.info[value][value1] = "扬声器"
                      }else if(res.data.data.info[value][value1]===4){
                        res.data.data.info[value][value1] = "投屏器"
                      }
                    }
                    if(value1==="status"){
                      if(res.data.data.info[value][value1]===1){
                        res.data.data.info[value][value1] = "正常"
                      }else if(res.data.data.info[value][value1]===0){
                        res.data.data.info[value][value1] = "异常"
                      }
                    }
                  }

                }
                console.log(res.data.data.info)
                this.peripheralList=res.data.data.info
              }else{
                this.peripheralWithoutData = true
              }
            }else{
              this.$message("请求失败")
            }
          }).catch(err=>{
            this.$message("请求失败");
            console.log(err)
          })
        },
        //关键进程请求
        crucialInfoRequest(params){
          this.$api.terminalDiagnosis.getTerminalCrucialInfo(params).then(res=>{
            if(res.data.success===1){
              if(res.data.data.info.length!==0){
                this.crucialWithoutData=false;
                for(let value in res.data.data.info){
                  for(let value1 in res.data.data.info[value]){
                    if(res.data.data.info[value][value1] === ""){
                      res.data.data.info[value][value1] = ' ----'
                    }else if(value1==='runtime'){
                      res.data.data.info[value][value1] = this.timestampToTime(res.data.data.info[value][value1])
                    }else if(value1==='restart'){
                      res.data.data.info[value][value1] = res.data.data.info[value][value1] + "次"
                    }
                  }
                }
                this.keyOutList=res.data.data.info
              }else{
                this.crucialWithoutData=true
              }
            }else{
              this.$message("请求失败")
            }
          }).catch(err=>{
            this.$message("请求失败");
            console.log(err)
          })
        },
        //进程详情
        keyDetailButton(row){
          this.keyName = row.process;

            for (let i in row.data){
              console.log(row.data)
              if(row.data[i]["time"]){
                row.data[i]["time"] = this.timestampToTimes(row.data[i]["time"])
              }else{
                row.data[i]["time"] = " ----"
              }
              if(!row.data[i]["reason"]){
                row.data[i]["reason"] = ' ----'
              }
            }

          this.keyDetailList = row.data;
          this.keyDetail = true
        },
        //呼叫请求
        callInfoRequest(){
				  let param = {
				    "start":this.start,
            "count":this.count,
            "e164":this.e164,
            "terminal":this.loginDevice
          };
          this.callRecording = true
          this.$api.terminalDiagnosis.getTerminalCallInfo(param).then(res=>{
            if(res.data.success===1){
              if(res.data.data.info.length!==0){
                this.callRecordWithoutData=false;
                this.total = res.data.data.total;
                for(let value in res.data.data.info){
                  for(let value1 in res.data.data.info[value]){
                    if(res.data.data.info[value][value1] === ""){
                      res.data.data.info[value][value1] = ' ----'
                    }else if(value1==="time"){
                      res.data.data.info[value][value1] = this.timestampToTimes(res.data.data.info[value][value1])
                    }else if(value1==='result'){
                      if(res.data.data.info[value][value1]===1){
                        res.data.data.info[value][value1] = "成功"
                      }else if(res.data.data.info[value][value1]===0){
                        res.data.data.info[value][value1] = "失败"
                      }
                    }
                  }
                }
                this.callRecordList=res.data.data.info
              }else{
                this.callRecordWithoutData=true
              }
              this.callRecording = false
            }else{
              this.$message("请求失败")
              this.callRecording = false
            }
          }).catch(err=>{
            this.$message("请求失败");
            this.callRecording = false
            console.log(err)
          })
        },
        //时间长度转换
        timestampToTime(total_time) {
          if(total_time !==""){
            if (total_time<60){
              total_time = total_time+'秒'
            }else if (total_time<60*60){
              total_time = parseInt(total_time/60)+'分钟'+parseInt((total_time-parseInt(total_time/60)*60))+'秒'
            }else{
              let second = total_time-parseInt(total_time/60/60)*60*60-parseInt((total_time-parseInt(total_time/60/60)*60*60)/60)*60;
              total_time = parseInt(total_time/60/60)+'小时'+parseInt((total_time-parseInt(total_time/60/60)*60*60)/60)+'分钟'+parseInt(second)+'秒'
            }
          }
					return total_time
				},
				//时间戳转换
        timestampToTimes(timestamp){
          let date = new Date(timestamp);//时间戳为10位需*1000，时间戳为13位的话不需乘1000
          let Y = date.getFullYear() + '-';
          let M = (date.getMonth()+1 < 10 ? '0'+(date.getMonth()+1) : date.getMonth()+1) + '-';
          let D = (date.getDate()<10 ? '0'+date.getDate() : date.getDate()) + ' ';
          let h = (date.getHours()<10 ? '0'+date.getHours():date.getHours())  + ':';
          let m = (date.getMinutes()<10 ? '0'+date.getMinutes():date.getMinutes()) + ':';
					let s = (date.getSeconds()<10 ? '0'+date.getSeconds():date.getSeconds()) ;
					return Y+M+D+h+m+s;
				},
        //详情跳转终端详情按钮
        detailTurnRoute(val){
          this.$router.push({
            name: 'monitor-meetinginfo',
            params: {
              module: 'mtInfo',
              params: {
                conf_id: val,
                mt_id: this.e164,
                conf_type: 3,
                conf_status: 1,
              }
            },
          });
        },
        //设置外设表格异常红色显示
        changeCellStyle(object){
          let cellStyle = {
            color:'red'
          };
          if (object.row.status === '异常' && object.columnIndex === 3){
            return cellStyle
          }
        },
        //呼叫记录分页
        currentChange(val){
					if(this.total!==0){
						this.currentPage = val;
						if (val>0){
							this.start = (val-1)*this.count;
              this.callInfoRequest()
						}
					}
				},
      },
      mounted() {
				//终端详情跳转到此界面
				let activeRouteList=["/ops/diagnose/terminal", "/ops/diagnose"];
				this.$store.dispatch('activeRouteChange',activeRouteList);
				if(Object.keys(this.$route.params).length !==0&&this.$route.params.params!==null){
					this.inputCondition=this.$route.params.params.mt_id;
					this.searchResult();
					Object.keys(this.$route.params).forEach(i=>this.$route.params[i]=null)
				}
      },
    }
</script>

<style scoped>
 .terminalDiagnosis{
   position: relative;
   background-color: #232629;
   height: 100%;
   margin-top: 20px;
   margin-right: 20px;
   margin-left: 20px;
 }
  .terminalDiagnosisTop{
    padding-bottom: 30px;
    border-bottom: #3d4046 1px dashed ;
  }
  .terminalDiagnosisFont{
    font-size: 14px;
    padding:20px 20px 30px 25px;
    font-weight: bold;
  }
  .terminalDiagnosisObj{
    color: #5d6266;
    font-size: 14px;
    padding-left: 25px;
    padding-right: 10px;
  }
  .terminalDiagnosisInput{
    width: 200px;
    padding-right: 7px;
		font-size: 14px;
  }
  .peripheralInfo{
    padding-bottom: 30px;
    padding-left: 25px;
    font-size: 14px;
    padding-top :25px;
  }
  .perInfo{
    padding-left: 25px;
    padding-right: 25px;
    padding-bottom: 25px;
  }
 .terminalDiagnosisPicTip {
   font-size: 14px;
   width: 100%;
   box-sizing: border-box;
   text-align: left;
 }

</style>
