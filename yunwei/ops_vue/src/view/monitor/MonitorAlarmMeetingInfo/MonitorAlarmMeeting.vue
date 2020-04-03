	<template >
		<!-- 主页面，接收各个模块的数据，进行数据处理以及发送 -->
		<div  class='settings meetingAll theme-dark'>
			
			<div class='meetingAll theme-dark' v-show='defaultall'>
				<!-- 侧边栏 -->
				<div v-show="sidebarShow" :class="['meetingInfo',{'unfold':!unfold}]" :style="{'width':unfold? '0':'260px'} ">
					<div class="meetingInfo-group-collapse" :style="{'left':unfold?'0px':'260px'}"
							 @click="sidebarTelescopic">
						<i :class="['icon-group-collapse','el-icon-arrow-right',{'active':!unfold}]"></i>
					</div>
					<el-scrollbar class="meetingInfo-siderbar-scrollbar" :noresize="false" >
					<div class="siderbar-tree">
						<div style="width: 100%" >
							<el-input placeholder="请输入域" v-model='searchUser' style="display:inline-block;width: 160px" maxlength="100" @keydown.enter.native='searchEnterFun'></el-input>
							<el-button @click='searchForm()'>搜索</el-button>
						</div>
						<div class="el-tree-node is-focusable" v-for="roomitem in platform" :key="roomitem.moid">
							<div :class="['el-tree-node__content',{'is-active':groupIsActived === roomitem.moid}]"
									 style="padding-left: 0;position: relative;margin-top: 20px"
									 @click="treeNodeContenthover(roomitem.moid,'room_moid')">
								<span :class="['el-tree-node__expand-icon','el-icon-caret-right',{'expanded':groupIsOpened[roomitem.moid]}] "
											@click="treeNodeContentCaretClick(roomitem.moid)">
								</span>
								<span style="width: 100%;line-height:36px;" @click="treeNodeContentItemClick(roomitem.moid,'room_moid',roomitem)">
                  <el-tooltip class="item" effect="dark" :content="roomitem.name" placement="top-start" v-if="roomitem.name.length> 16">
									  <span class="el-tree-node__label">{{roomitem.name}}</span>
                  </el-tooltip>
                  <span class="el-tree-node__label" v-if="roomitem.name.length<=16">{{roomitem.name}}</span>
								</span>
							</div>
							<div class="el-tree-node is-focusable"
									 v-for="userformitem in roomitem.info"
									 :key="userformitem.moid"
									 :class="['el-tree-node__content',{'is-active':groupIsActivedUser === userformitem.moid}]"
									 v-if="groupIsOpened[roomitem.moid]"
									 style="padding-left: 0;position: relative;"
									 @click="treeNodeContenthoverU(userformitem)">
                <el-tooltip  :content="userformitem.name" placement="top-start" v-if="userformitem.name.length>= 14">
                  <span class="el-tree-node__label" style="margin-left: 40px;font: 14px '微软雅黑';margin-top: 10px;display: inline-block;overflow: hidden; max-width:170px;text-overflow:ellipsis;">{{userformitem.name}}</span>
                </el-tooltip>
								<div  style="margin-left: 40px;font: 14px '微软雅黑';margin-top: 10px" class="el-tree-node__label" v-if="userformitem.name.length<14">{{userformitem.name}}</div>
							</div>
						</div>
						</div>
					</el-scrollbar>
				</div>
				<div class="theme-dark meetingInfo-column" :style="{'margin-left':unfold?'26px':'286px'}" >
					<!-- tab页面两个 -->
					<KdTabCommon :tab-list="tabList" :active-tab="activeTab"  class-name="tab-alarm" @tab-change="tabChange"></KdTabCommon>
					<div class="area-tab-content">
							<component :is="activeTab" @detailit='detailit' @conferenceTopologyChange="conferenceTopologyChange" :moid='moids' @realTime = 'realTime' :realList='realList'></component>
					</div>
				</div>
			</div>
			<!-- 详细信息 -->
			<div v-if="detailInfo" class='meetingAll theme-dark kd-alarm-no' >
				<!-- 与会终端列表 -->
				<div class='theme-dark' style="padding: 13px 20px;" v-if='terminalInfoList'>
					<div class="" style="display:flex;align-items: center; ">
						<el-button icon="ops-icons-bg icon-arrow-circle-left" @click="returnit" circle></el-button>
						<span style="margin-left: 14px;font-size: 14px;color: #9ca9b1;">{{terminalFormInfos.conf_name}}</span>
					</div>
					<div style="padding-left: 40px;padding-top: 34px;color: #9ca9b1;font-size: 14px;position: relative">
						<!--实时会议-->
						<div style="margin-bottom: 25px"  v-if="this.status===1">
							<span style="width: 335px;display: inline-block">
								<span style="width: 110px;display:inline-block;color: #5d6266;font-size: 14px">发言方</span><span>{{ terminalFormInfos.speaker}}</span>
							</span>
							<span style="width: 335px;display: inline-block">
								<span style="width: 110px;display:inline-block;color: #5d6266;font-size: 14px">管理方</span><span>{{ terminalFormInfos.chairman}}</span>
							</span>
							<span style="width: 335px;display: inline-block">
								<span style="width: 110px;display:inline-block;color: #5d6266;font-size: 14px">双流源</span><span>{{ terminalFormInfos.dualstream}}</span>
							</span>
							<span style="display: inline-block">
								<span style="width: 110px;display:inline-block;color: #5d6266;font-size: 14px">直播状态</span><span>{{ terminalFormInfos.live_stat}}</span>
							</span>
						</div>
						<div style="margin-bottom: 25px"  v-if="this.status===1">
							<span style="width: 335px;display: inline-block">
								<span style="width: 110px;display:inline-block;color: #5d6266;font-size: 14px">录像状态</span><span>{{ terminalFormInfos.rec_stat}}</span>
							</span>
							<span style="width: 335px;display: inline-block">
								<span style="width: 110px;display:inline-block;color: #5d6266;font-size: 14px">协作状态</span><span>{{ terminalFormInfos.dcs_stat}}</span>
							</span>
							<span style="width: 335px;display: inline-block">
								<span style="width: 110px;display:inline-block;color: #5d6266;font-size: 14px">加密方式</span><span>{{ terminalFormInfos.encryption}}</span>
							</span>
							<span style="display: inline-block">
								<span style="width: 110px;display:inline-block;color: #5d6266;font-size: 14px">媒体能力</span><span>{{ terminalFormInfos.media}}</span>
							</span>
						</div>
						<div style="margin-bottom: 25px"  v-if="this.status===1">
							<span style="width: 335px;display: inline-block">
								<span style="width: 110px;display:inline-block;color: #5d6266;font-size: 14px">视频格式</span><span>{{ terminalFormInfos.format}}</span>
							</span>
							<span style="width: 335px;display: inline-block">
								<span style="width: 110px;display:inline-block;color: #5d6266;font-size: 14px">混音</span><span v-if="terminalFormInfos.mix">
										<span>{{ terminalFormInfos.mix.mode}}</span>
								<!--<span>定制混音</span>-->
                <el-popover
                    placement="bottom"
                    title=""
                    width="200"
                    trigger="click"
                    popper-class="theme-dark"
                    v-if="terminalFormInfos.mix.mode === '定制混音'">
                    <div  style="float: left;color: #5d6266;font-size: 12px"> 终端名称</div>
                    <div style="height: 204px;padding-left: 20px;margin-top: 22px;overflow:auto;overflow-x:hidden;" >
                      <div v-for="mixListOne in mixList" :key="o" class="text item" style="padding-bottom: 14px;color: #9ca9b1;font-size: 12px" >
                        {{ mixListOne }}
                      </div>
                    </div>
                    <button type="button" class="button-host-info" slot='reference' @click="mixDialog(terminalFormInfos.mix)">
                      <span style="text-decoration: underline;">详情</span>
                    </button>
                  </el-popover>
										<!-- <button type="button" class="button-host-info" v-if="terminalFormInfos.mix.mode === '定制混音'" @click="mixDialog(terminalFormInfos.mix)"> -->
										<!--<button type="button" class="button-host-info" @click="mix=true">-->
											<!-- <span style="text-decoration: underline;">详情</span> -->
										<!-- </button> -->
									</span>
							</span>
							<span style="width: 335px;display: inline-block">
								<span style="width: 110px;display:inline-block;color: #5d6266;font-size: 14px">画面合成</span>
                  <span v-if="terminalFormInfos.vmp">
										<span>{{ terminalFormInfos.vmp.stat}}</span>
                  <!--<span>开启</span>-->
                    <el-popover
                        placement="bottom"
                        title=""
                        width="200"
                        trigger="click"
                        popper-class="theme-dark"
                        v-if="terminalFormInfos.vmp.stat === '开启'">
                        <div  style="float: left;color: #5d6266;font-size: 12px"> 终端名称</div>
                        <div style="height: 204px;padding-left: 20px;margin-top: 22px;overflow:auto;overflow-x:hidden;" >
                          <div v-for="mixListOne in mixList" :key="o" class="text item" style="padding-bottom: 14px;color: #9ca9b1;font-size: 12px" >
                            {{ mixListOne }}
                          </div>
                      </div>
                      <button type="button" class="button-host-info" slot='reference' @click="mixDialog(terminalFormInfos.vmp)">
                        <span style="text-decoration: underline;">详情</span>
                      </button>
                    </el-popover>
										<!-- <button type="button" class="button-host-info" v-if="terminalFormInfos.vmp.stat === '开启'" @click="mixDialog(terminalFormInfos.vmp)"> -->
											<!--<button type="button" class="button-host-info" @click="mix=true">-->
											<!-- <span style="text-decoration: underline;">详情</span> -->
										<!-- </button> -->
									</span>
							</span>
							<span style="width: 335px;display: inline-block">
								<span style="width: 110px;display:inline-block;color: #5d6266;font-size: 14px">会议服务器IP</span><span>{{ terminalFormInfos.cmu_ip}}</span>
							</span>
						</div>
						<div style="margin-bottom: 25px"  v-if="this.status===1">
							<span style="width: 335px;display: inline-block">
								<span style="width: 110px;display:inline-block;color: #5d6266;font-size: 14px">媒体服务器IP</span><span>{{ terminalFormInfos.media_ip}}</span>
							</span>
						</div>
						<!--历史会议-->
						<div style="margin-bottom: 25px" v-if="this.status===0">
							<span style="width: 335px;display: inline-block">
								<span style="width: 110px;display:inline-block;color: #5d6266;font-size: 14px">加密方式</span><span>{{ terminalFormInfos.encryption}}</span>
							</span>
							<span style="width: 335px;display: inline-block">
								<span style="width: 110px;display:inline-block;color: #5d6266;font-size: 14px">媒体能力</span><span>{{ terminalFormInfos.media}}</span>
							</span>
							<span style="display: inline-block">
								<span style="width: 110px;display:inline-block;color: #5d6266;font-size: 14px">视频格式</span><span>{{ terminalFormInfos.format}}</span>
							</span>
						</div>
						<MonitorMeetingInfoConfEventSurvey :apiParams="mtParams"></MonitorMeetingInfoConfEventSurvey>
						<!-- 下方表格 -->
						<div style="background: #232629;margin-top: 10px;min-height:200px ;">
							<div style="color: #9ca9b1;margin: 20px;padding-top: 20px;">
								<el-input
									clearable
									v-model="condition"
									placeholder="请输入与会终端名称或E164号"
									style='width:230px;padding-right: 7px'
									maxlength="100"
									@keydown.enter.native='searchEnterFunTerminal'></el-input>
								<el-button @click="searchTerminal()">
									搜索
								</el-button>
							</div>
							<template>
								<el-table
									stripe
									:data='terminalList'
									style='margin-top: 5px;padding-left: 20px;padding-right: 20px;padding-bottom: 20px;'
									v-loading="loadingTableData"
							    @row-dblclick="tableRowDblClick"
									element-loading-background="rgba(0, 0, 0, 0.5)"
									:cell-style='changeCellStyle'>
									<el-table-column label="序号" type='index' width="57px"></el-table-column>
									<el-table-column prop='mt_name' label="终端名称" show-overflow-tooltip min-width="371px"></el-table-column>
									<el-table-column label="在线状态" show-overflow-tooltip v-if="this.status===1">
										<template slot-scope="scope">
											<span v-if="terminalList[scope.$index].is_online === 1" style="color: #63cd81">在线</span>
											<span v-if="terminalList[scope.$index].is_online === 0">离线</span>
										</template>
									</el-table-column>
									<!-- <el-table-column prop='mt_status' label="状态" show-overflow-tooltip v-if="this.status===1" min-width="80px"></el-table-column> -->
									<el-table-column prop='mt_addr' label="设备IP" show-overflow-tooltip min-width="130px"></el-table-column>
									<el-table-column prop='mt_type' label="设备型号" show-overflow-tooltip min-width="105px"></el-table-column>
									<el-table-column prop='mt_e164' label="E164号" show-overflow-tooltip min-width="110px"></el-table-column>
									<el-table-column prop='mt_expe' label="会议体验" show-overflow-tooltip min-width="80px"></el-table-column>
									<el-table-column prop='bitrate' label="呼叫码率" show-overflow-tooltip min-width="89px"></el-table-column>
									<el-table-column prop='mt_soft' label="软件版本" show-overflow-tooltip min-width="100px"></el-table-column>
									<el-table-column label="操作" min-width="125px" v-if="this.status===1">
										<template slot-scope="scope">
											<span>
												<button type="button" class="button-host-info" @click="terminalDetail(scope.$index, terminalList)" v-if="terminalList[scope.$index].mt_e164!=='   ----'&&(terminalList[scope.$index].add_type===3||terminalList[scope.$index].add_type===2||terminalList[scope.$index].add_type===4||terminalList[scope.$index].add_type===5)">
													<span style="text-decoration: underline;">详情</span>
												</button>
												<!--{{ terminalList[scope.$index].mt_e164 }}-->
												<button disabled type="button" class="button-host-info" @click="terminalDetail(scope.$index, terminalList)" v-if="terminalList[scope.$index].mt_e164==='   ----'||(terminalList[scope.$index].add_type!==3&&terminalList[scope.$index].add_type!==2&&terminalList[scope.$index].add_type!==4&&terminalList[scope.$index].add_type!==5)">
													<span style="text-decoration: underline;color: gray;" >详情</span>
												</button>
											</span>
											
											<!-- <button type="button" class="button-host-info" @click="terminalDetail(scope.$index, terminalList)" v-if="terminalList[scope.$index].add_type===3">
												<span style="text-decoration: underline;">详情</span>
											</button>
											<button disabled type="button" class="button-host-info" @click="terminalDetail(scope.$index, terminalList)" v-if="terminalList[scope.$index].add_type!==3">
												<span style="text-decoration: underline;color: gray;" >详情</span>
											</button> -->
											<button type="button" class="button-host-info" @click="snapShot(scope.$index, terminalList)" v-if="terminalList[scope.$index].mt_e164!=='   ----'&&terminalList[scope.$index].add_type!==2&&terminalList[scope.$index].add_type!==4&&terminalList[scope.$index].add_type!==5">
												<span style="text-decoration: underline;">终端快照</span>
											</button>
											<button disabled type="button" class="button-host-info" @click="snapShot(scope.$index, terminalList)" v-if="terminalList[scope.$index].mt_e164==='   ----'&&terminalList[scope.$index].add_type!==2&&terminalList[scope.$index].add_type!==4&&terminalList[scope.$index].add_type!==5">
												<span style="text-decoration: underline;color: gray;">终端快照</span>
											</button>
										</template>
									</el-table-column>
									<el-table-column label="操作" min-width="125px" v-if="this.status===0">
										<template slot-scope="scope">
											
											<button type="button" class="button-host-info" @click="terminalDetail(scope.$index, terminalList)" v-if="terminalList[scope.$index].mt_e164!=='   ----'&&(terminalList[scope.$index].add_type===3||terminalList[scope.$index].add_type===2||terminalList[scope.$index].add_type===4||terminalList[scope.$index].add_type===5)">
												<span style="text-decoration: underline;">详情</span>
											</button>
											<button disabled type="button" class="button-host-info" @click="terminalDetail(scope.$index, terminalList)" v-if="terminalList[scope.$index].mt_e164==='   ----'||(terminalList[scope.$index].add_type!==3&&terminalList[scope.$index].add_type!==2&&terminalList[scope.$index].add_type!==4&&terminalList[scope.$index].add_type!==5)">
												<span style="text-decoration: underline;color: gray;" >详情</span>
											</button>
											<button type="button" class="button-host-info" @click="snapShot(scope.$index, terminalList)" v-if="terminalList[scope.$index].mt_e164!=='   ----'&&terminalList[scope.$index].add_type!==2&&terminalList[scope.$index].add_type!==4&&terminalList[scope.$index].add_type!==5">
												<span style="text-decoration: underline;">终端快照</span>
											</button>
											<button disabled type="button" class="button-host-info" @click="snapShot(scope.$index, terminalList)" v-if="terminalList[scope.$index].mt_e164==='   ----'&&terminalList[scope.$index].add_type!==2&&terminalList[scope.$index].add_type!==4&&terminalList[scope.$index].add_type!==5">
												<span style="text-decoration: underline;color: gray;">终端快照</span>
											</button>
										</template>
									</el-table-column>
								</el-table>
							</template>
							</div>
							<div style="right: 0;bottom: 10px;padding-top: 10px;background: #232629;padding-right: 20px;padding-bottom: 20px;" class='theme-dark'>
									<KdPagination
									@current-change="currentChange"
									:pageSize="this.count"
									:currentPage="currentPage"
									:total="this.total"
									:disabled="pageDisabled">
									</KdPagination>
							</div>
						</div>
					<!--终端快照-->
					<el-dialog
						title="终端快照"
						:visible.sync="terminalSnapShot"
						width="500px"
						:close-on-click-modal="false"
						@close="meetingSnapShotclose">
						<div style="padding:100px 50px;width: 100%;height: 100%" v-if="showSnapShot">
							<TheConferenceSnapshot :tiemRange = 'timeRange' @snapshotsStatu="snapshotsStatu" ref="timeRange"></TheConferenceSnapshot>
						</div>
						<div align="center" slot='footer' class='theme-dark' style='margin-bottom:10px;' v-if="snapShotStatu === null">
							<el-button @click='giveTimeSpanShot'>确定</el-button>
							<el-button @click='terminalSnapShot=false'>取消</el-button>
						</div>
						<div align="center" slot='footer' class='theme-dark' style='margin-bottom:10px;' v-if="snapShotStatu === 'creating'">
							<el-button @click='terminalSnapShotclose'>取消</el-button>
						</div>
						<div align="center" slot='footer' class='theme-dark' style='margin-bottom:10px;' v-if="snapShotStatu === 'created'">
							<el-button @click='downSnapShot()'>下载文件</el-button>
						</div>
						<div align="center" slot='footer' class='theme-dark' style='margin-bottom:10px;' v-if="snapShotStatu === 'failed'">
							<el-button @click='terminalSnapShotclose'>确定</el-button>
						</div>
					</el-dialog>
					<!--合成和混音弹出框-->
				<!-- 	<el-dialog
						title=""
						:visible.sync="mixing"
						width="260px"
						close-on-click-modal="false"
						:modal="false"
						class="mixSyn"
						style="
						position: fixed;
						top: 100px;
						left: 3px;
						transform-origin: center top;
						z-index: 1000;"
						>
						<div  style="float: left;color: #5d6266;font-size: 12px"> 终端名称</div>
						<div style="height: 204px;padding-left: 20px;margin-top: 22px;overflow:auto;overflow-x:hidden;" >
							<div v-for="mixListOne in mixList" :key="o" class="text item" style="padding-bottom: 14px;color: #9ca9b1;font-size: 12px" >
								{{ mixListOne }}
							</div>
						</div>
						<div style="height: 33px;"></div>
					</el-dialog> -->
				</div>
				<!-- 每个终端详情(多点会议) -->
				<div class='theme-dark' style="margin: 13px 20px;" v-if='terminalInfoChart'>
					<el-button @click='routeTerminalDiagnose()' style='float: right;'>诊断</el-button>
					<div class="" style="display:flex;align-items: center; ">
						<el-button icon="ops-icons-bg icon-arrow-circle-left" @click="returnOne" circle></el-button>
						<span style="margin-left: 14px;font-size: 14px;color: #9ca9b1;">终端详情</span>
					</div>

					
					<div style="padding-left: 40px;padding-top: 34px;color: #9ca9b1;font-size: 14px;position: relative">
						<div style="margin-bottom: 25px">
							<span style="width: 335px;display: inline-block">
								<span style="width: 110px;display:inline-block;color: #5d6266;font-size: 14px">终端名称</span><span>{{ terminalFormInfo.mt_name}}</span>
							</span>
							<span style="width: 335px;display: inline-block">
								<span style="width: 110px;display:inline-block;color: #5d6266;font-size: 14px">IPv6地址</span><span> ----</span>
							</span>
							<span style="width: 335px;display: inline-block">
								<span style="width: 110px;display:inline-block;color: #5d6266;font-size: 14px">IPv4地址</span><span>{{ terminalFormInfo.mt_addr}}</span>
							</span>
							<span style="	display: inline-block">
								<span style="width: 110px;display:inline-block;color: #5d6266;font-size: 14px">E164号</span><span>{{ terminalFormInfo.mt_e164}}</span>
							</span>
							
						</div>
						<div style="margin-bottom: 25px">
							<span style="width: 335px;display: inline-block">
								<span style="width: 110px;display:inline-block;color: #5d6266;font-size: 14px">DNS IP</span><span> ----</span>
							</span>
							<span style="width: 335px;display: inline-block">
								<span style="width: 110px;display:inline-block;color: #5d6266;font-size: 14px">APS IP</span><span> ----</span>
							</span>
							<span style="width: 335px;display: inline-block">
								<span style="width: 110px;display:inline-block;color: #5d6266;font-size: 14px">网关</span><span> ----</span>
							</span>
							<span style="width: 335px;display: inline-block">
								<span style="width: 110px;display:inline-block;color: #5d6266;font-size: 14px">端口</span><span> ----</span>
							</span>
						</div>
						<div style="margin-bottom: 25px">
							<span style="width: 335px;display: inline-block">
								<span style="width: 110px;display:inline-block;color: #5d6266;font-size: 14px">协议类型</span><span>{{ terminalFormInfo.mt_prot}}</span>
							</span>
							<span style="width: 335px;display: inline-block">
								<span style="width: 110px;display:inline-block;color: #5d6266;font-size: 14px">设备型号</span><span>{{ terminalFormInfo.mt_type}}</span>
							</span>
							<span style="width: 335px;display: inline-block">
								<span style="width: 110px;display:inline-block;color: #5d6266;font-size: 14px">软件版本</span><span>{{ terminalFormInfo.mt_soft}}</span>
							</span>
							<span style="display: inline-block">
								<span style="width: 110px;display:inline-block;color: #5d6266;font-size: 14px">会议体验</span><span>{{ terminalFormInfo.mt_expe}}</span>
							</span>
						</div>
						<div style="margin-bottom: 30px">
							<span style="width: 335px;display: inline-block">
								<span style="width: 110px;display:inline-block;color: #5d6266;font-size: 14px">呼叫码率</span><span>{{ terminalFormInfo.bitrate}}</span>
							</span>
							<span style="width: 335px;display: inline-block">
								<span style="width: 110px;display:inline-block;color: #5d6266;font-size: 14px">接入服务器IP</span><span>{{ terminalFormInfo.gk_ip}}</span>
							</span>
						</div>
					</div>
					<div style="border-top:1px #5d6266 dashed ;margin-left: 42px;margin-top: 12px"></div>
					<span style="float: right;padding: 40px 0 0 42px;font-size: 0" v-if="this.activeTabTerminalDetail==='terminalCallDetail'" >
						<button  @click='typesChange("pic")' :class="['changeCallTerminal',{'active':media === 'pic'}]">视图</button>
						<button  @click='typesChange("list")' :class="['changeCallTerminal',{'active':media === 'list'}]">列表</button>
					</span>
					<div style="padding: 40px 0 0 42px;">
						<!-- <MonitorMeetingInfoTerminalSummary></MonitorMeetingInfoTerminalSummary> -->
						<KdTabCommon style="height: 100%" :tab-list="tabListTerminalDetail" :active-tab="activeTabTerminalDetail" class-name="tab-alarm" @tab-change="tabChangeTerminalDetail" v-if="this.status===1"></KdTabCommon>
						<KdTabCommon style="height: 100%" :tab-list="tabListTerminalDetailHistory" :active-tab="activeTabTerminalDetail" class-name="tab-alarm" @tab-change="tabChangeTerminalDetail" v-if="this.status===0"></KdTabCommon>
						
						
						<div class="area-tab-content">
							<component :is="activeTabTerminalDetail" :media='media' :callDetailTable='terminalDeraildata' ></component>
						</div>
					</div>
				</div>
				<!-- 每个终端详情(点对点会议) 点对点会议没有终端列表-->
				<div class='theme-dark' style="padding: 10px 20px;" v-if='peerToPeerterminalInfoChart'>
					<div class="" style="float:left">
						<el-button icon="ops-icons-bg icon-arrow-circle-left" @click="returnit" circle></el-button>
					</div>
					<!--<el-button icon='el-icon-back' circle @click='returnit()'></el-button>-->
					<div style="height: 3px"></div>
					<span style="margin-left: 10px;font-size: 14px;color: #9ca9b1;">详情</span>
					<div style="padding: 20px 40px;">
						<el-select
							v-model="callingChange"
							placeholder="主叫终端"
							style='width:110px;'
							popper-class="theme-dark"
							@change="callsChange">
							<el-option
								v-for='item in p2pList'
								:key='item.value'
								:label='item.label'
								:value='item.value'></el-option>
						</el-select>
						<callterminal :peertopeerdata='peertopeerdata' v-if='callValue===0'></callterminal>
						<calledterminal :peertopeerdata='peertopeerdata' v-if='callValue===1'></calledterminal>
					</div>
				</div>
			</div>
		</div>
	</template>

	<script>
		export default {
			components: {
				// ops_vue/src/components/monitor/MonitorMeetingInfoConfEventSurvey.vue
				MonitorMeetingInfoConfEventSurvey: () => import('@/components/monitor/MonitorMeetingInfoConfEventSurvey.vue'),
				terminalCallDetail: () => import('@/view/monitor/MonitorAlarmMeetingInfo/terminalCallDetail.vue'),
				terminalOverView: () => import('@/view/monitor/MonitorAlarmMeetingInfo/terminalOverView.vue'),
				statusInfo: () => import('@/view/monitor/MonitorAlarmMeetingInfo/statusInfo.vue'),
				terminalCallLink: () => import('@/view/monitor/MonitorAlarmMeetingInfo/terminalCallLink.vue'),
				terminalLink: () => import('@/view/monitor/MonitorAlarmMeetingInfo/terminalLink.vue'),
				KdPagination: () => import('@/components/common/KdPagination.vue'),
				KdTabCommon: () => import('@/components/common/KdTabCommon.vue'),
				callterminal: () => import('@/view/monitor/MonitorAlarmMeetingInfo/callterminal.vue'),
				calledterminal: () => import('@/view/monitor/MonitorAlarmMeetingInfo/calledterminal.vue'),
				RealTimeMeeting: () => import('@/view/monitor/MonitorAlarmMeetingInfo/RealTimeMeeting.vue'),
				HistoryMeeting: () => import('@/view/monitor/MonitorAlarmMeetingInfo/HistoryMeeting.vue'),
				videoSource:() => import('@/view/monitor/MonitorAlarmMeetingInfo/videoSource.vue'),
				TheConferenceSnapshot: () => import('@/components/monitor/TheConferenceSnapshot.vue'),
				terminalTopology:() => import("@/view/monitor/MonitorAlarmMeetingInfo/terminalTopology.vue")
			},
			data(){
				return {
					//2.0
					realList:[],
					mtParams:{},
					sidebarShow:false,
					condition:'',								//与会终端搜索条件
					groupIsOpened:{},
					groupIsHovered:'',
					groupIsActived:'',
					groupIsActivedUser:'',
					groupIsOpenedUser:{},
					pageDisabled:false,           //分页按钮是否可点
					disabledTerminalDetail:false, //是否可点击终端列表详情按钮
					treeProps:{
						children: 'children',
						label: 'name',
						nodeKey:'',
						isLeaf: 'leaf'
					},
					unfold:true,															//展开侧边栏所显示的内容
					// pickup:false,													//收起侧边栏时的预留块宽度
					defaultall:true,													//默认界面
					detailInfo:false,													//详细信息界面
					activeTab:'RealTimeMeeting',							//默认tab选项
					tabList:[['RealTimeMeeting','实时会议'],	//tab设置
									['HistoryMeeting','历史会议'],],
					searchUser:'',														//侧边栏搜索内容
					nodeExpend:[],
					platform:[],															//放入平台域信息
					userform:[],															//放入用户域信息
					moids:[],																	//传入子组件的数据
					peertopeerdata:{},												//点对点终端详情数据传递
					activeTab1:'callterminal',								//详情点对点tab页面默认值
					tabList1:[['callterminal','主叫终端'],			//详情点对点tab页面展示
									['calledterminal','被叫终端'],],
					terminalInfoList:false,										//与会终端列表显示
					terminalList: [],													//与会终端列表信息
					terminalInfoChart:false,									//终端详情显示
					terminalFormInfo:{},											//终端详情上方表单
					terminalFormInfos:{},
					peerToPeerterminalInfoChart:false,				//点对点终端详情显示
					sidebarListInfo:[],												//侧边栏选中信息
					terminalListCommonInfo:{},								//与会终端公共信息
					conf_type:0,															//会议类型，默认为传统会议
					userform_id:'',														//userformid
					platform_id:'',														//platformid
					activeTabTerminalDetail:'terminalOverView',		//多点会议终端详情下方图表
					tabListTerminalDetail:[																					//多点会议终端详情tab分页
						['terminalOverView','参会概况'],
						['statusInfo','状态信息'],
						// ['terminalCallLink','呼叫链路'],
            ['terminalLink','码流链路'],
						['terminalCallDetail','呼叫详情'],
						['videoSource','视频源'],
						['terminalTopology','终端拓扑'],
					],
					tabListTerminalDetailHistory:[																					//多点会议终端详情tab分页历史会议
						['terminalOverView','参会概况'],
						['statusInfo','状态信息'],
						// ['terminalCallLink','呼叫链路'],
            ['terminalLink','码流链路'],
						['terminalCallDetail','呼叫详情'],
						['videoSource','视频源'],
					],
					terminalDeraildata:[],										//多点会议传入终端各个图标的数据
					media:'pic',			
					p2pList:[
						{
							label:'主叫终端',
							value:0,
						},
						{
							label:'被叫终端',
							value:1,
						}
					],
					callValue:0,						  //默认点对点终端详情为主叫终端
					callingChange:0,
					start:1,
					count:12,
					total:0,
					currentPage:1,
					terminalDetailOne:{},
					treeData:[],
					status:'',
					loadingTableData:false,  //列表加载
					timeRange:[],            //快照时间范围
					terminalSnapShot:false, //终端快照
					snapShotStatu:null,     //快照状态
					snapShotObj:{},         //所点击的终端列表的值
					showSnapShot:false,    //是否加载快照组件
					mixList:[],            //混音合成详情列表
					mixing:false,
					conf_id:'',
					conf_status:'',
					mt_id:'',
					e164:'',
					
				}
			},
			methods: {
				// 2.0
				typesChange(value){
					if(value==='list'){
						
						this.media = 'list'
					}else if(value==='pic'){
						this.media='pic'
					}
          let storage = window.localStorage;
          if (!storage.getItem("terminalCallDetailChange")){
            storage.setItem("terminalCallDetailChange",this.media);
          }else{
            storage.removeItem('terminalCallDetailChange');
            storage.setItem("terminalCallDetailChange",this.media);
          }
				},
				
				
        // add by ywj
        tableRowDblClick(row, column, event){
          this.clearTimer()
          if(row.add_type===3){
            this.terminalInfoList=false
            this.terminalInfoChart=true
						this.activeTabTerminalDetail='terminalOverView'
            if (!row.mt_name){
              row.mt_name =row.mt_e164
            }
            this.terminalFormInfo = row
            var param=[{
              'conf_id':this.terminalListCommonInfo.conf_id,
              'mt_e164':row.mt_e164,
              'start_time':this.terminalListCommonInfo.start_time,
              'end_time':this.terminalListCommonInfo.end_time,
              'conf_type':this.conf_type,
              "conf_status":this.status,
              "mt_addr":row.mt_addr
            }]
            param.push(row)
            //增加一个属性为视频源信息无需请求
            this.terminalDeraildata = param
          }
        },
        // add by ywj end
        //点击用户域大模块
				treeNodeContenthoverU(userinfo){
					this.groupIsActived = userinfo.platform_moid
					if(userinfo.moid!==this.groupIsActivedUser){
						this.groupIsActivedUser=userinfo.moid
						this.$set(this.groupIsOpenedUser,userinfo.moid,!this.groupIsOpenedUser[userinfo.moid])
					}
					this.user_moid = userinfo.moid
					this.sidebarListInfo[0] = userinfo
					this.sidebarListInfo[1] = {
						"user_moid":this.user_moid
					}
					this.moids=[...this.sidebarListInfo]
				},
        //点击平台域大模块
				treeNodeContenthover(id,type){
					this.groupIsHovered = id
					this.groupIsActived = id
				},
        //点击平台域名字
				async treeNodeContentItemClick(id,type,roomitem){
					this.sidebarListInfo=[]
					this.userform=''
					this.groupIsActivedUser=''
					this.groupIsActived=id
					this.groupIsHovered=id
					this.groupTypeIsActived=type
					this.sidebarListInfo[0] = {
						"platform_moid":id
					}
					this.moids=[...this.sidebarListInfo]
						let params={
							platform_moid:id
						}
						if(!this.userform){
							this.userform= await  this.$api.monitor.getUserDomains(params)
							for(var i in this.platform){
								if(this.platform[i].moid===roomitem.moid){
									this.platform[i].info=this.userform
								}
							}
						}
				},
        //点击三角按钮
				async treeNodeContentCaretClick(id){
					for(var i in this.platform){
						if(this.platform[i].moid===id){
							if(this.platform[i].info.length===0){
								var res=await this.$api.monitor.getUserDomains({platform_moid:id})
								this.platform[i].info = res
							}
						}
					}
					this.groupIsActivedUser=''
					this.user_moid = ''
					this.sidebarListInfo[1] = {
						"user_moid":""
					}
					this.moids=[...this.sidebarListInfo]
					this.groupIsActived=id
					this.$set(this.groupIsOpened,id,!this.groupIsOpened[id])

				},
        //混音 合成弹出框详情
				mixDialog(val){
					this.mixing = true
					this.mixList=[]
					for(var member in val.members){
						if(val.members[member].mt_name){
							this.mixList.push(val.members[member].mt_name)
						}else if (val.members[member].mt_id){
							this.mixList.push(val.members[member].mt_id)
						}
					}
				},
        //终端列表是否进行点击详情控制
				changeCellStyle(object){
					let cellStyle = {
						disabledTerminalDetail:true
					}
					if (object.row.add_type !== 3 && object.columnIndex === 9){
						return this.disabledTerminalDetail=true
					}
				},
        //关闭终端快照弹出框
				terminalSnapShotclose(){
					this.terminalSnapShot = false
					this.showSnapShot = false
					this.snapShotStatu=null
				},
        //传给组件创建任务值
				giveTimeSpanShot(){
					if(this.snapShotObj.mt_e164){
						var params = {
							"key":this.snapShotObj.mt_e164}
					}else{
						var params ={
							"key":this.snapShotObj.mt_addr
						}
					}
					this.$refs.timeRange.createSnapshots(params)
				},
        //下载快照
				downSnapShot(){
					this.$refs.timeRange.downloadSnapshots()
					this.terminalSnapShot=false
					this.showSnapShot = false
					this.snapShotStatu=null
				},
        //获取组件传来的数据
				snapshotsStatu(val){
					this.snapShotStatu = val
				},
        //点击列表终端快照
				snapShot(index,data){
					this.terminalSnapShot = true
					this.showSnapShot = true
					this.snapShotObj = data[index]
					if(this.terminalListCommonInfo.conf_status === 1){
						this.timeRange = [this.terminalListCommonInfo.start_time-60000,(new Date()).valueOf()]
					}else if(this.terminalListCommonInfo.conf_status ===0){
						this.timeRange = [this.terminalListCommonInfo.start_time-60000,this.terminalListCommonInfo.end_time]
					}
				},
        //enter搜索函数
				searchEnterFun(e){
					var keyCode = window.event?e.keyCode:e.which;
					if(keyCode===13){
						this.searchForm()
					}
				},
        //搜索域
				async searchForm(){
					for(var plat in this.platform){
						this.$set(this.groupIsOpened,this.platform[plat]['moid'],this.groupIsOpened[this.platform[plat]['moid']]= false)
					}
					if(this.searchUser){
						let params={
							"key":this.searchUser
						}
						let userInfo=await this.$api.monitor.getUserSearchDomains(params)
						this.platform=await this.$api.monitor.getPlatformDomains()
						let platList = []
						for(var plat in this.platform){
							if(this.platform[plat]['name']===this.searchUser){
								platList.push(this.platform[plat])
							}
						}
						if(userInfo.length!==0){
							this.platform.forEach((item)=>{
								if(item.moid===userInfo[0].platform_moid){
									this.$set(item,'info',userInfo)
								}
							})
							for(var i in userInfo){
								userInfo[i]["moid"] = userInfo[i].platform_moid
								userInfo[i]['name'] = userInfo[i].platform_name
								var dict = {
									"moid":userInfo[i].user_domain_moid,
									"name":userInfo[i].user_domain_name,
									"platform_moid":userInfo[i].platform_moid,
									"platform_name":userInfo[i].platform_name,
									"info":[],
								}
								userInfo[i]['info'].push(dict)
								this.$set(this.groupIsOpened,userInfo[i].platform_moid,this.groupIsOpened[userInfo[i].platform_moid]= true)
								platList.push(userInfo[i])
							}
							var list = []
							var value = 0
							for (var i in platList){
								list.push({"moid":platList[i].platform_moid,"name":platList[i].platform_name,"info":[]})
							}
							var a = this.uniqueList(list)
							for(var j in a){
								for(var i in platList){
									if(a[j].moid===platList[i].platform_moid){
										var dict = {
											"moid":platList[i].user_domain_moid,
											"name":platList[i].user_domain_name,
											"platform_moid":platList[i].platform_moid,
											"platform_name":platList[i].platform_name,
											"info":[],
										}
										a[j]['info'].push(dict)
									}
								}
							}
							this.platform = a
						}else if(userInfo.length===0){
              let platList = []
              for(var plat in this.platform){
                if(this.platform[plat]['name']===this.searchUser){
                  platList.push(this.platform[plat])
                }
              }
              var list = []
              var value = 0
              for (var i in platList){
                list.push({"moid":platList[i].moid,"name":platList[i].name,"info":[]})
              }
              var a = this.uniqueList(list)
              this.platform = a
						}
					}else{
						this.nodeExpend=[]
						this.platform=await this.$api.monitor.getPlatformDomains()
					}
				},
				//数组去重
				uniqueList(array){
					var r = [];
					for(var i = 0, l = array.length; i < l; i++) {
						for(var j = i + 1; j < l; j++)
							//关键在这里
							if (JSON.stringify(array[i]) == JSON.stringify(array[j])) j = ++i;
						r.push(array[i]);
					}
					return r;
				},
        //侧边栏的展开收起
				async sidebarTelescopic(){
					if(this.platform.length===0){
						this.platform =await this.$api.monitor.getPlatformDomains()
					}
					this.unfold = !this.unfold
				},
				tabChange(val){																								//tab传递数据给子组件
					this.activeTab=val
					this.sidebarShow = true
				},
				tabChangeTerminalDetail(val){
					if(val==='terminalCallDetail'){
						// this.media='pic'
            if(window.localStorage.getItem("terminalCallDetailChange")){
              this.typesChange(window.localStorage.getItem("terminalCallDetailChange"))
            }
					}
					this.activeTabTerminalDetail=val
				},
				realTime(value){																								//接收realTime会议传来是列表还是图表判断
					if(value==='list'){
						this.sidebarShow = true
					}else if(value==='pic'){
						this.sidebarShow = false
					}
					this.unfold = true
				},
        //会议详情，获取会议组件传值
				detailit(val){
					// console.log(val)
					//2.0加入
					this.conf_status = val.conf_status
					if(val.conf_status===1){
						var end_time = 'now'
					}else{
						var end_time = val.end_time
					}
					this.mtParams={
						confID: val.conf_id,
						startTime:val.start_time,
						endTime: end_time,
						confStatus:val.conf_status,
						confType:val.conf_type,
					}
					
					
					
					this.mixing=false
					//会议名称为空则传递id给三级界面
					if (val.conf_name===''){
						val.conf_name = val.conf_id
					}
					// console.log(val)
					this.terminalFormInfos=val
					// 码率等添加单位，及转换混音与合成
					
					// console.log(Type(val.bitrate))
					var strbit = String(val.bitrate).substr(val.bitrate.length-4)
					var strfra = String(val.frame).substr(val.frame.length-3)
					// console.log(strbit)
					if(val.bitrate&&strbit!=='kbps'){
						this.terminalFormInfos.bitrate = val.bitrate+"kbps"
					}
					if(val.frame&&strfra!=='fps'){
						this.terminalFormInfos.frame=val.frame+"fps"
					}
					if(val.resolution&&val.frame&&val.bitrate){
						this.terminalFormInfos.media  = val.resolution+"@"+this.terminalFormInfos.frame +" "+this.terminalFormInfos.bitrate}
					if (val.conf_status===1){
						if(val.conf_type!==2){
							this.extendRequest(val)
							this.setTimer(20)
						}else{
							this.clearTimer()
						}
					}
					this.terminalList=[]
					this.status = val.conf_status
					this.conf_type = val.conf_type
					if(this.conf_type === 2){
						this.defaultall=false
						this.detailInfo=true
						this.terminalInfoList=false
						this.peerToPeerterminalInfoChart=true
						this.peertopeerdata = val
						this.clearTimer()
					}else{
						this.pageDisabled = true
						this.defaultall=false
						this.detailInfo=true
						this.terminalInfoList=true
						this.terminalDetailOne = val
						this.loadingTableData = true
						//降低传入后端参数
						val["start"]=0
						val["count"]=this.count
						this.requestTerminalList(val)
						this.setTimer(20)
					}
				},
				//请求额外参数
				extendRequest(val){
					this.$api.monitor.getExtend(val).then(res=>{
						if(res.data.success===1){
							this.terminalFormInfos.vmp = res.data.data.info[0].vmp
							if(res.data.data.info[0].vmp.stat===0){
								this.terminalFormInfos.vmp.stat = "关闭"
							}else if (res.data.data.info[0].vmp.stat===1){
								this.terminalFormInfos.vmp.stat = "开启"
							}
							this.terminalFormInfos.mix = res.data.data.info[0].mix
							if(res.data.data.info[0].mix.stat === 0){
								this.terminalFormInfos.mix.mode = "关闭"
							}else if(res.data.data.info[0].mix.stat === 1){
								if(res.data.data.info[0].mix.mode===1){
									this.terminalFormInfos.mix.mode= "智能混音"
								}else if (res.data.data.info[0].mix.mode===2){
									this.terminalFormInfos.mix.mode = "定制混音"
								}
							}
							this.terminalFormInfos.speaker =res.data.data.info[0].speaker
							this.terminalFormInfos.chairman = res.data.data.info[0].chairman
							this.terminalFormInfos.dualstream = res.data.data.info[0].dualstream
							this.terminalFormInfos.media_ip = res.data.data.info[0].media_ip
							this.terminalFormInfos.cmu_ip = res.data.data.info[0].cmu_ip
							if(res.data.data.info[0].live_stat ===0){
								this.$set(this.terminalFormInfos,"live_stat","关闭")
							}else if (res.data.data.info[0].live_stat ===1){
								this.$set(this.terminalFormInfos,"live_stat","开启")
							}
							if(res.data.data.info[0].rec_stat ===0){
								this.$set(this.terminalFormInfos,"rec_stat","关闭")
							}else if (res.data.data.info[0].rec_stat ===1){
								this.$set(this.terminalFormInfos,"rec_stat","开启")
							}
							if(res.data.data.info[0].dcs_stat ===0){
								this.$set(this.terminalFormInfos,"dcs_stat","关闭")
							}else if (res.data.data.info[0].dcs_stat ===1){
								this.$set(this.terminalFormInfos,"dcs_stat","开启")
							}
							for(var item in this.terminalFormInfos) {
								if(this.terminalFormInfos[item]===''){
									this.terminalFormInfos[item]='   ----'
								}
							}
						}else if(res.data.success===0) {
							console.log(res.data.msg)
						}
					}).catch(err=>{})
				},
        //回车键搜索表格
				searchEnterFunTerminal(e){
					var keyCode = window.event?e.keyCode:e.which;
					if(keyCode===13){
						this.searchTerminal()
					}
				},
				//终端列表search
				searchTerminal(){
					this.currentPage = 1
					this.start = 0
					var params={
						"conf_type":this.conf_type,
						'conf_id':this.terminalDetailOne.conf_id,
						'start_time':this.terminalDetailOne.start_time,
						'end_time':this.terminalDetailOne.end_time,
						"conf_status":this.terminalDetailOne.conf_status,
						"condition":this.condition,
						"start":0,
						"count":this.count,
					}
					this.requestTerminalList(params)
				},
				//终端请求列表
				requestTerminalList(val){
					if(!this.detailInfo){
						this.clearTimer()
					}
					this.$api.monitor.meetingDevice(val).then(res=>{
						if (res.data.success===1){
							this.total = res.data.data.total
							this.start = res.data.data.start
							for(var i in res.data.data.info){
								if(res.data.data.info[i].mt_expe||res.data.data.info[i].mt_expe===0){
									res.data.data.info[i].mt_expe = res.data.data.info[i].mt_expe +'分'
								}
								if(res.data.data.info[i].bitrate||res.data.data.info[i].bitrate===0){
									res.data.data.info[i].bitrate = res.data.data.info[i].bitrate +'kbps'
								}
								if (!res.data.data.info[i].mt_name && res.data.data.info[i].mt_e164){
									res.data.data.info[i].mt_name = res.data.data.info[i].mt_e164
								}else if(!res.data.data.info[i].mt_name && !res.data.data.info[i].mt_e164){
									res.data.data.info[i].mt_name =res.data.data.info[i].mt_addr
								}
								if(res.data.data.info[i].add_type!==3){
									res.data.data.info[i].mt_type = res.data.data.info[i].add_desc
								}
								if(res.data.data.info[i].add_type===2||res.data.data.info[i].add_type===4||res.data.data.info[i].add_type===5){
                  res.data.data.info[i].mt_addr = '   ----'
                }
							}
							this.terminalList = res.data.data.info
							for(let item of this.terminalList) {
								for(let key in item){
									if(item[key]===''){
										item[key]='   ----'
									}
								}
								if(item.mt_status===0){
									item.mt_status = "正常"
								}else if(item.mt_status===1){
									item.mt_status = "异常"
								}
							}
							this.terminalListCommonInfo = res.data.data
						}
						this.loadingTableData = false
						this.pageDisabled = false
					}).catch(err =>{
						this.loadingTableData = false
						this.pageDisabled = false
					})
				},
        //返回上一级
				returnit(){
					this.condition=''
					this.mixing=false
					var listValue = ['list']
					this.realList = [...listValue]
					this.sidebarShow = true
					if(this.conf_type === 2){
						this.defaultall=true
						this.detailInfo=false
						this.terminalInfoList=false
						this.peerToPeerterminalInfoChart=false
						this.terminalInfoChart=false
					}else{
						this.peerToPeerterminalInfoChart=false
						this.detailInfo=false
						this.defaultall=true
						this.clearTimer()
					}
					
				},
        //返回上一级
				returnOne(){
					this.mixing=false
					this.terminalInfoList=true
					this.terminalInfoChart=false
					this.condition=''
					if(this.conf_type !== 2){
						var params = {
							"start_time":this.terminalDetailOne.start_time,
							"conf_id":this.terminalDetailOne.conf_id,
						}
						this.extendRequest(params)
						this.detailit(this.terminalFormInfos)
						this.searchTerminal()
						if(this.status===1){
							this.setTimer(20)
						}
					}
				},
        //终端详情信息
				terminalDetail(index,data){
					
					this.clearTimer()
					if(data[index].add_type===3){
						this.terminalInfoList=false
						this.terminalInfoChart=true
						this.activeTabTerminalDetail='terminalOverView'
						if (!data[index].mt_name){
							data[index].mt_name = data[index].mt_e164
						}
						this.terminalFormInfo = data[index]
						var param=[{
							'conf_id':this.terminalListCommonInfo.conf_id,
							'mt_e164':data[index].mt_e164,
							'start_time':this.terminalListCommonInfo.start_time,
							'end_time':this.terminalListCommonInfo.end_time,
							'conf_type':this.conf_type,
							"conf_status":this.status,
							"mt_addr":data[index].mt_addr
						}]
						param.push(data[index])
						this.e164 = data[index].mt_e164
						//增加一个属性为视频源信息无需请求
						this.terminalDeraildata = param
					}else if((data[index].add_type===2||data[index].add_type===4||data[index].add_type===5)){
						var params={
							'keywords':data[index].mt_e164,
							'conf_type':'3',
							'conf_status':this.status,
						}
						this.$api.monitor.meetingGet(params).then(res=>{
						  if (res.data.success === 1){
								for(var i in res.data.data.info){
									if(res.data.data.info[i].conf_id===data[index].mt_e164){
										this.detailit(res.data.data.info[i])
									}
								}
								
							}
						})
						// this.detailit()
					}
				},
				//跳转终端诊断界面
				routeTerminalDiagnose(){
					// console.log(this.terminalFormInfo)
					this.$router.push({
					  name: 'terminal_diagnose',
					  params: {
					    module: 'diaMt',
					    params: {
					      mt_id: this.terminalFormInfo.mt_e164,
					    }
					  },
					});
				},
        //终端列表分页请求
				currentChange(val){
					if(this.total!==0){
						this.currentPage =val
						var params ={
							"conf_type":this.conf_type,
							'count':this.count,
							'start':(val-1)*12,
							'conf_id':this.terminalDetailOne.conf_id,
							'start_time':this.terminalDetailOne.start_time,
							'end_time':this.terminalDetailOne.end_time,
							"conf_status":this.terminalDetailOne.conf_status,
							"condition":this.condition,
						}
						this.loadingTableData = true
						this.$api.monitor.meetingDevice(params).then(res=>{
							if (res.data.success===1){
								this.total = res.data.data.total
								this.start = res.data.data.start
								for(var i in res.data.data.info){
									if(res.data.data.info[i].mt_expe||res.data.data.info[i].mt_expe===0){
										res.data.data.info[i].mt_expe = res.data.data.info[i].mt_expe +'分'
									}
									if(res.data.data.info[i].bitrate||res.data.data.info[i].bitrate===0){
										res.data.data.info[i].bitrate = res.data.data.info[i].bitrate +'kbps'
									}
									if (!res.data.data.info[i].mt_name && res.data.data.info[i].mt_e164){
										res.data.data.info[i].mt_name = res.data.data.info[i].mt_e164
									}else if(!res.data.data.info[i].mt_name && !res.data.data.info[i].mt_e164){
										res.data.data.info[i].mt_name =res.data.data.info[i].mt_addr
									}
									if(res.data.data.info[i].add_type!==3){
										res.data.data.info[i].mt_type = res.data.data.info[i].add_desc
									}
								}
								this.terminalList = res.data.data.info
								for(let item of this.terminalList) {
									for(let key in item){
										if(item[key]===''){
											item[key]='   ----'
										}
									}
									if(item.mt_status===0){
										item.mt_status = "正常"
									}else if(item.mt_status===1){
										item.mt_status = "异常"
									}
								}
								this.terminalListCommonInfo = res.data.data
							}
							this.loadingTableData = false
						}).catch(err=>{
							this.loadingTableData = false
						})
					}
				},
        conferenceTopologyChange(params){
          this.conf_status=params.conf_status
          this.conf_type=params.conf_type
          this.conf_id=params.conf_id
          this.mt_id=params.mt_id
          this.routeTerminal()
        },
        //其他界面跳转终端详情
				routeTerminal(){
				    this.terminalInfoList = false
					  this.defaultall=false
						this.detailInfo=true
						this.terminalInfoChart=true
						this.activeTabTerminalDetail='terminalOverView'
						var params={
							"conf_status":this.conf_status,
							"conf_type":this.conf_type,
							"keywords":this.conf_id
						}
						// console.log(this.$route.params.params.conf_status)
						this.status=this.conf_status
						this.$api.monitor.meetingGet(params).then(res=>{
							if(res.data.success===1){
								if(res.data.data.length!==0){
									// console.log(res.data.data.info[0])
									var routeInfo = [res.data.data.info[0]]
									this.terminalDetailOne=res.data.data.info[0]
									this.terminalFormInfos = res.data.data.info[0]
									var params = {
										start_time:res.data.data.info[0].start_time,
										end_time :res.data.data.info[0].end_time,
										conf_status :res.data.data.info[0].conf_status,
										conf_type : res.data.data.info[0].conf_type,
										conf_id : res.data.data.info[0].conf_id,
										condition:this.mt_id
									}
									this.start_time=res.data.data.info[0].start_time
									this.end_time=res.data.data.info[0].end_time
									this.$api.monitor.meetingDevice(params).then(res=>{
										if(res.data.success===1){
											// console.log(res.data.data.info[0])
											if(res.data.data.info.length!==0){
												this.terminalListCommonInfo = res.data.data
												for(var i in res.data.data.info){
													if(res.data.data.info[i].mt_expe||res.data.data.info[i].mt_expe===0){
														res.data.data.info[i].mt_expe = res.data.data.info[i].mt_expe +'分'
													}
													if(res.data.data.info[i].bitrate||res.data.data.info[i].bitrate===0){
														res.data.data.info[i].bitrate = res.data.data.info[i].bitrate +'kbps'
													}
												}
												this.terminalFormInfo = res.data.data.info[0]
												// console.log(this.terminalFormInfo)
												// this.terminalFormInfo = routeInfo[0]
												// this.conf_type=this.$route.params.params.conf_type
												
												var param=[{
													'conf_id':this.terminalListCommonInfo.conf_id,
													'mt_e164':this.terminalFormInfo.mt_e164,
													'start_time':this.terminalListCommonInfo.start_time,
													'end_time':this.terminalListCommonInfo.end_time,
													'conf_type':this.conf_type,
													"conf_status":this.status,
													"mt_addr":this.terminalFormInfo.mt_addr
												}]
												routeInfo['mt_prot']=this.terminalFormInfo.mt_prot
												param.push(routeInfo)
												//增加一个属性为视频源信息无需请求
												// console.log(param)
												this.terminalDeraildata = param
											}else{
												this.$message('未查到该终端信息')
											}
										}
									})
								}else{
									this.$message('未查到该会议信息')
								}
							}
						})
						
				},
				//点对点会议选择主叫被叫终端
				callsChange(val){
					if (val ===0 ){
						this.callValue = 0
					}else if (val ===1 ){
						this.callValue = 1
					}
				},
        //定时发送请求
				timeParams(){
					if(this.terminalInfoList){
						var params ={
							"conf_type":this.conf_type,
							'count':this.count,
							'start':(this.currentPage-1)*12,
							'conf_id':this.terminalDetailOne.conf_id,
							'start_time':this.terminalDetailOne.start_time,
							'end_time':this.terminalDetailOne.end_time,
							"conf_status":this.terminalDetailOne.conf_status,
							"condition":this.condition,
						}
						this.requestTerminalList(params)
						this.extendRequest(params)
					}
				},
        // 定时器
				setTimer(interver=60,range=3600000){
					this.clearTimer();
						this.timer = setInterval(() => {
							if(this.status===1){
								this.timeParams()
							}

						},interver*1000)
				},
				// 清除定时器
				clearTimer(){
					clearInterval(this.timer);
					this.timer = null;
				},
			},
			mounted(){
				// 调整当前route，变化侧边栏高亮
				let activeRouteList=["/ops/monitor/meetinginfo", "/ops/monitor"]
				this.$store.dispatch('activeRouteChange',activeRouteList)
				// console.log("1111")
				if(Object.keys(this.$route.params).length !==0&&this.$route.params.params!==null){
					// console.log(this.$route.params)
					this.conf_status=this.$route.params.params.conf_status
					this.conf_type=this.$route.params.params.conf_type
					this.conf_id=this.$route.params.params.conf_id
					this.mt_id=this.$route.params.params.mt_id
					this.routeTerminal()
					Object.keys(this.$route.params).forEach(i=>this.$route.params[i]=null)
					}
        // storage.pageLoadCount = parseInt(storage.getItem("pageLoadCount")) + 1;//必须格式转换
        // console.log(storage.getItem("pageLoadCount"))
        // document.getElementById("test").innerHTML = storage.pageLoadCount;


			},
			computed: {
			// 计算属性的 getter
			  tabStyle: function () {
			    // console.log({margin: '0 ' + this.width + 'px ' + '0px ' + this.width-3 +'px'})
			    let leftWidth=0
			    return {margin: '0px ' + 0+ 'px ' + '0px ' + leftWidth + 'px'}
			  },
			  // currentPageNumber: function () {
			  //   return this.currentPage
			  // },
			},
			watch: {
        //侧边栏
				searchUser(val) {
					// this.$refs.singleTreeRight.filter(val);
				},
				detailInfo(val,old){
					if(val===false){
						this.clearTimer()
					}
				},

			},
      //离开界面前清除
			beforeDestroy () {
				this.clearTimer()
			},
		}

	</script>

	<style>

		/* 设置除侧边栏外的部分样式 */
	.meetingInfo{
		position: fixed;
		height:calc(100vh - 61px);
		background-color: #232629;
		z-index: 1020;
		}
		.meetingInfo .el-tree-node__content.is-active{
			color: #299dff;
		}
		.meetingInfo .el-tree-node__content{
			height: 14px;
			color: #9ca9b1;
			margin-bottom: 10px;
		}
		.meetingInfo .el-tree-node:focus > .el-tree-node__content{
			color: #299dff;
			background-color: transparent;
		}
		.meetingInfo .el-tree-node__content:hover {
			color: #299dff;
			background-color: transparent;
		}
		.meetingInfo .el-tree-node__content:focus{
			background-color: transparent;
			color: #299dff;
		}
		.meetingAll .el-tree-node__content.is-active{
			color: #299dff;
		}
		.meetingAll .el-tree-node__content{
			height: 14px;
			color: #9ca9b1;
			font-size: 14px;
			margin-bottom: 15px;
		}
		.meetingAll .el-tree-node__content:hover {
			color: #299dff;
			background-color: transparent;
		}
	.meetingInfo-group-collapse{
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
	.icon-group-collapse{
		color: #c0c4cc;
		font-size: 12px;
		transform: rotate(0deg);
		transition: transform .3s ease-in-out;
	}
	.icon-group-collapse.active{
		transform: rotate(-180deg);
	}
	.meetingInfo-siderbar-scrollbar{
		height: 100%;
	}

	.meetingAll .el-scrollbar .el-scrollbar__wrap {
		overflow-x: hidden;overflow-y: auto;
	}

	.meetingInfo-column{
			padding-top: 16px;
			padding-right: 20px;
	}
	.meetingAll .siderbar-tree{
		box-sizing: border-box;
		padding: 16px 24px 16px 10px;
	}
	.meetingAll{
		position: relative;
	}

	.meetingAll .el-form-item__label{
		color:#5d6266;
	}
	.meetingAll .el-form-item__content{
		line-height:18.5px;
		position: relative;
	}
	.meetingAll .el-form-item{
		margin-right: 0px;
		margin-bottom: 25px;
		line-height: 18.5px;
	}
	.tab-alarm{
		margin-bottom: 20px;
	}
	.mixSyn .el-dialog{
		background: #141414;
		border:1px solid #383b3c;
	}
	.mixSyn .el-dialog__body{
		padding-right: 15px;
		padding-left: 14px;
	}
  .meetingAll {
    min-width: 1400px;
    /*width:expression(document.body.clientWidth < 1000 ? "1000px": "auto" );*/
  }
	.changeCallTerminal.active {
		background-color: #485a6b;
		color: #fff;
		width: 60px;
		height: 24px;
		border: 0;
	}
	.changeCallTerminal:hover{
		color:#00a2ff;
	}
	.changeCallTerminal{
		background-color: #232629;
		color: #fff;
		width: 60px;
		height: 24px;
		border: 1px solid #485a6b;
		font-size: 12px;
		cursor:pointer;
	}
	</style>
