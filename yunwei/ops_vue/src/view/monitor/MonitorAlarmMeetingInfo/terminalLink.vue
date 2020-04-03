<template class="terminalLink">
	<!-- 码流链路 -->
	<div style="width: 100%;background: #232629;height: 100%">
		<!--时间选择-->
    <div style="display: inline">
      <el-date-picker
        v-model="terminalLinkTime"
        type="datetime"
        range-separator=""
        :placeholder="timeDefault"
        popper-class="theme-dark"
        class="clear-close-icon"
        format="yyyy-MM-dd HH:mm:ss"
        prefix-icon="ops-icons-bg icon-calendar"
        value-format="timestamp"
        :clearable=false
        @change="terminalDateLink"
        :default-value="timeitem"
        style='margin-top: 25px;margin-left: 20px;width: 190px;margin-right: 7px;'
      >
      </el-date-picker>
      <!--类型选择-->
      <el-select
        v-model="terminalLinkTypes"
        placeholder="主流"
        style='width:140px;'
        popper-class="theme-dark"
        @change="terminalLinkTypeChange">
        <el-option
          v-for='item in terminalLinkType'
          :key='item.value'
          :label='item.label'
          :value='item.value'></el-option>
      </el-select>
      <span class="block" style="margin-left: 40px">
        <span style="margin-right: 10px">{{timebefore}}</span>
        <el-slider v-model="timeLine" style="width: 290px; display: inline-block;vertical-align: top;margin-top: 20px" :show-tooltip="false" @input="timeLineChange" :step="5" @change="sendRequest"></el-slider>
        <span style="color: #00a2ff;margin-left: 10px">{{timeItems}}</span>
        <span>/{{timeafter}}</span>
      </span>

    </div>



		<!--图例-->
    <div style="float: right;margin: 30px 0 0 0;" v-if='showAll'>
      <span style="color: #9ca9b1;float: right;margin-right: 39px;font-size: 14px;">异常</span>
      <i class="ops-icons-bg icon-legend-red" style="float: right;margin-right: 7px;margin-top: 8px"></i>
      <span style="color: #9ca9b1;float: right;margin-right: 35px;font-size: 14px;">正常</span>
      <i class="ops-icons-bg icon-legend-grassGreen" style="float: right;margin-right: 7px;margin-top: 8px"></i>
		</div>
    <!--无数据时显示-->
    <div style="font-size: 16px;color:#9ca9b1;padding-top: 150px;padding-left: 520px;padding-bottom: 150px" v-show="withoutData">
      <span style="margin-right: 10px;"><i class="el-icon-info"></i></span>
      <span >
        尚 无 码 流 链 路 数 据
      </span>
    </div>

		<!--上行-->
    <div style="color:#9ca9b1;margin: 28px 50px 0 50px ;font-size: 14px" v-if='showAll'>上行</div>
		<div class='send' style="font-size: 14px;width: 1300px;"  v-if='showAll' >
      <div v-for=" i in forNumbSendFirst" v-if="codeStreamLinkInfo.send[0]">
        <!--小于等于四个时的状态图标以及标志信息-->
        <div style="height: 36px;margin-left: 150px; margin-top: 18px;">
          <span style="float:left;color: #9ca9b1;width: 270px;" v-for='(value1,index1) in codeStreamLinkInfo.send[0].data'   :key='index1'>
            <span v-if="8*(i-1)<=index1&&index1<8*(i-1)+4&&i===1">
              <!--循环判断是否带状态图标-->
              <span style="border:#fb265d solid 4px;float:left;margin: 6px auto;border-radius:2em;" v-if="value1.status===0"></span>
              <span style="border:#63cd81 solid 4px;float:left;margin: 6px auto;border-radius:2em;" v-if="value1.status===1"></span>
              <!--上方ip等信息-->
              <span v-if="value1.ip&&value1.port" style="margin-left: 5px;">{{value1.desc+':'+value1.ip+":"+value1.port}}</span>
              <span v-if="!value1.ip&&(index1===0)" style="padding-left: 10px;margin-left: 5px">{{value1.desc}}</span>
              <span v-if="!value1.ip&&!(index1===0)" style="padding-left: 55px;margin-left: 5px">{{value1.desc}}</span>
              <span v-if="value1.ip&&!value1.port" style="margin-left: 5px;">{{value1.desc+':'+value1.ip}}</span>
							<!-- 2.0 -->
              <button type="button" class="button-host-info" @click="syn(value1)" v-if="(value1.desc==='合成'||value1.desc==='混音')&&value1.status===0">
                <span style="text-decoration: underline;">查看</span>
              </button>
							<!-- 2.0 end -->
            </span>
            <span v-if="8*(i-1)<=index1&&index1<8*(i-1)+4&&i>1" >
              <!--循环判断是否带状态图标-->
              <span style="border:#fb265d solid 4px;float:left;margin: 6px auto;border-radius:2em;" v-if="value1.status===0"></span>
              <span style="border:#63cd81 solid 4px;float:left;margin: 6px auto;border-radius:2em;" v-if="value1.status===1"></span>
              <!--上方ip等信息-->
              <span v-if="value1.ip&&value1.port" style="margin-left: 5px;">{{value1.desc+':'+value1.ip+":"+value1.port}}</span>
              <span v-if="!value1.ip&&(index1===0)" style="padding-left: 10px;margin-left: 5px">{{value1.desc}}</span>
              <span v-if="!value1.ip&&!(index1===0)" style="padding-left: 55px;margin-left: 5px">{{value1.desc}}</span>
              <span v-if="value1.ip&&!value1.port" style="margin-left: 5px;">{{value1.desc+':'+value1.ip}}</span>
							<!-- 2.0 -->
							<button type="button" class="button-host-info" @click="syn(value1)" v-if="(value1.desc==='合成'||value1.desc==='混音')&&value1.status===0">
							  <span style="text-decoration: underline;">查看</span>
							</button>
							<!-- 2.0 end -->
            </span>
          </span>
        </div>
        <!--小于四个时的大图标-->
        <div style="height: 42px;margin-left: 150px;" >
          <!--图标-->
          <span v-for='(value2,index2) in codeStreamLinkInfo.send[0].data' v-if="codeStreamLinkInfo.send[0]" :key='index2'>
            <el-tooltip placement="bottom-start">
              <div slot="content" style="width:300px;height: 20px;" v-for="( toopTip, indexAll) in value2"  v-if="indexAll!=='name'&&indexAll!=='desc'&&indexAll!=='ip'&&indexAll!=='port'&&indexAll!=='status'">
                <span style="display:block; float:left;min-width: 90px;text-align:right;">{{ indexAll }}</span> :  <span>{{ toopTip }}</span>
              </div>
              <i class='ops-icons-bg icon-link-model-meetting' style='float:left;margin-left: 10px;margin-right: 10px' v-if="(index2 !== codeStreamLinkInfo.send[0].data.length)&&8*(i-1)<=index2&&index2<8*(i-1)+4&&i===1"></i>
              <i class='ops-icons-bg icon-link-model-meetting' style='float:left;margin-left: 10px;margin-right: 10px' v-if="(index2 !== codeStreamLinkInfo.send[0].data.length)&&8*(i-1)<=index2&&index2<8*(i-1)+4&&i>1"></i>
            </el-tooltip>
            <!--第一行-->
            <terminalLinkChart style='float:left;' v-if="(index2 !== codeStreamLinkInfo.send[0].data.length-1)&&4*(i-1)<=index2&&index2<4*i-1&&i===1"></terminalLinkChart>
            <!--除第一行外的行数-->
            <terminalLinkChart style='float:left;' v-if="(index2 !== codeStreamLinkInfo.send[0].data.length-1)&&8*(i-1)<=index2&&index2<8 *(i-1)+4-1&&i>1"></terminalLinkChart>
          </span>
          <terminalLinkChartY style='margin-left:897px;margin-right:30px;' v-if="codeStreamLinkInfo.send[0].data.length>3+8*(i-1)&&codeStreamLinkInfo.send[0].data.length-[8 *(i-1)+4]>0"></terminalLinkChartY>
        </div>
        <!--大于四个时的图标以及标志信息-->
        <div style="height: 36px;margin-right:160px; margin-top: 33px">
          <span style="float:right;color: #9ca9b1;margin-left: 90px;width: 160px;margin-right: 20px" v-for='(value1,index1) in codeStreamLinkInfo.send[0].data' :key='index1'>
            <span v-if="index1>=4+8*(i-1)&&index1<4+8*(i-1)+4">
              <!--循环判断是否带图标-->
              <span style="border:#fb265d solid 4px;float:left;margin: 6px 0 0 0;border-radius:2em;" v-if="value1.status===0"></span>
              <span style="border: #63cd81 solid 4px;float:left;margin: 6px 0 0 0;border-radius:2em;" v-if="value1.status===1"></span>
              <!--上方ip等信息-->
              <span v-if="value1.ip&&value1.port" style="margin-left: 5px;float:right">{{ value1.desc + ":" + value1.ip + ":" + value1.port }}</span>
              <span v-if="!value1.ip&&(index1===0)" style="padding-left: 10px;margin-left: 5px">{{ value1.desc }}</span>
              <span v-if="!value1.ip&&!(index1===0)" style="padding-left: 35px;margin-left: 5px">{{ value1.desc }}</span>
              <span v-if="value1.ip&&!value1.port" style="margin-left:5px;">{{ value1.desc +':' +value1.ip }}</span>
							<!-- 2.0 -->
							<button type="button" class="button-host-info" @click="syn(value1)" v-if="(value1.desc==='合成'||value1.desc==='混音')&&value1.status===0">
							  <span style="text-decoration: underline;">查看</span>
							</button>
							<!-- 2.0 end -->
            </span>
          </span>
        </div>
        <!--大于4个时-->
        <div style="height: 42px;margin-right: 214px;" v-if="codeStreamLinkInfo.send[0].data.length>=4*i">
          <!--除第一个外的图标-->
          <span v-for='(value2,index2) in codeStreamLinkInfo.send[0].data' :key='index2'>
            <el-tooltip placement="bottom-start">
              <div slot="content" style="width:300px;height: 20px" v-for="( toopTip, indexAll) in codeStreamLinkInfo.send[0].data[index2+1]" v-if="indexAll!=='name'&&indexAll!=='desc'&&indexAll!=='ip'&&indexAll!=='port'&&indexAll!=='status'">
                <span style="display:block; float:left;min-width: 90px;text-align:right;">{{ indexAll }}</span> :  <span>{{ toopTip }}</span>
              </div>
              <!--<span style="display:block; float:left;min-width: 50px" v-if="indexAll!=='activepayload'&&indexAll!=='视频分辨率格式'">{{ indexAll }}</span> :  <span>{{ toopTip }}</span>-->
              <i class='ops-icons-bg icon-link-model-meetting' style='float:right;margin-left: 10px;margin-right: 10px;position: relative' v-if="(index2 !== this.codeStreamLinkInfo.send[0].data.length-1)&&4+8*(i-1)-1<=index2&&index2<4+8*(i-1)+4-1"></i>
            </el-tooltip>
            <terminalLinkChartsReverse style='position: relative;float: right' v-if="(index2 <= codeStreamLinkInfo.send[0].data.length-3)&&4+8*(i-1)-1<=index2&&index2<4+8*(i-1)+4-2"></terminalLinkChartsReverse>
          </span>
        </div>
        <terminalLinkChartY style='margin-left: 170px'  v-if="codeStreamLinkInfo.send[0].data.length>8*i"></terminalLinkChartY>
      </div>

      <div v-for=" i in forNumbSendSecond" v-if="codeStreamLinkInfo.send[1]">
        <!--小于等于四个时的状态图标以及标志信息-->
        <div style="height: 36px;margin-left: 150px; margin-top: 18px;">
        <span style="float:left;color: #9ca9b1;width: 270px;" v-for='(value1,index1) in codeStreamLinkInfo.send[1].data' v-if="codeStreamLinkInfo.send[1].data" :key='index1'>
        <span v-if="8*(i-1)<=index1&&index1<8*(i-1)+4&&i===1">
        <!--循环判断是否带状态图标-->
        <span style="border:#fb265d solid 4px;float:left;margin: 6px auto;border-radius:2em;" v-if="value1.status===0"></span>
        <span style="border:#63cd81 solid 4px;float:left;margin: 6px auto;border-radius:2em;" v-if="value1.status===1"></span>
        <!--上方ip等信息-->
        <span v-if="value1.ip&&value1.port" style="margin-left: 5px;">{{value1.desc+':'+value1.ip+":"+value1.port}}</span>
        <span v-if="!value1.ip&&(index1===0)" style="padding-left: 10px;margin-left: 5px">{{value1.desc}}</span>
        <span v-if="!value1.ip&&!(index1===0)" style="padding-left: 55px;margin-left: 5px">{{value1.desc}}</span>
        <span v-if="value1.ip&&!value1.port" style="margin-left: 5px;">{{value1.desc+':'+value1.ip}}</span>
				<!-- 2.0 -->
				<button type="button" class="button-host-info" @click="syn(value1)" v-if="(value1.desc==='合成'||value1.desc==='混音')&&value1.status===0">
				  <span style="text-decoration: underline;">查看</span>
				</button>
				<!-- 2.0 end -->
        </span>
        <span v-if="8*(i-1)<=index1&&index1<8*(i-1)+4&&i>1" >
        <!--循环判断是否带状态图标-->
        <span style="border:#fb265d solid 4px;float:left;margin: 6px auto;border-radius:2em;" v-if="value1.status===0"></span>
        <span style="border:#63cd81 solid 4px;float:left;margin: 6px auto;border-radius:2em;" v-if="value1.status===1"></span>
        <!--上方ip等信息-->
        <span v-if="value1.ip&&value1.port" style="margin-left: 5px;">{{value1.desc+':'+value1.ip+":"+value1.port}}</span>
        <span v-if="!value1.ip&&(index1===0)" style="padding-left: 10px;margin-left: 5px">{{value1.desc}}</span>
        <span v-if="!value1.ip&&!(index1===0)" style="padding-left: 55px;margin-left: 5px">{{value1.desc}}</span>
        <span v-if="value1.ip&&!value1.port" style="margin-left: 5px;">{{value1.desc+':'+value1.ip}}</span>
				<!-- 2.0 -->
				<button type="button" class="button-host-info" @click="syn(value1)" v-if="(value1.desc==='合成'||value1.desc==='混音')&&value1.status===0">
				  <span style="text-decoration: underline;">查看</span>
				</button>
				<!-- 2.0 end -->
        </span>
        </span>
        </div>
        <!--小于四个时的大图标-->
        <div style="height: 42px;margin-left: 150px;" >
        <!--图标-->
        <span v-for='(value2,index2) in codeStreamLinkInfo.send[1].data' v-if="codeStreamLinkInfo.send[1].data"  :key='index2'>
        <el-tooltip placement="bottom-start">
        <div slot="content" style="width:300px;height: 20px" v-for="( toopTip, indexAll) in value2"  v-if="indexAll!=='视频分辨率格式'&&indexAll!=='activepayload'&&indexAll!=='name'&&indexAll!=='desc'&&indexAll!=='ip'&&indexAll!=='port'&&indexAll!=='status'">
        <span style="display:block; float:left;min-width: 90px;text-align:right;">{{ indexAll }}</span> :  <span>{{ toopTip }}</span>
        </div>
        <div slot="content" style="width:300px;height: 20px" v-for="( toopTip, indexAll) in value2"  v-if="indexAll==='视频分辨率格式'||indexAll==='activepayload'&&indexAll!=='name'&&indexAll!=='desc'&&indexAll!=='ip'&&indexAll!=='port'&&indexAll!=='status'">
        <span style="display:block; float:left;min-width: 90px;text-align:right;">{{ indexAll }}</span> :  <span>{{ toopTip }}</span>
        </div>

        <i class='ops-icons-bg icon-link-model-meetting' style='float:left;margin-left: 10px;margin-right: 10px' v-if="(index2 !== codeStreamLinkInfo.send[1].data.length)&&8*(i-1)<=index2&&index2<8*(i-1)+4&&i===1"></i>
        <i class='ops-icons-bg icon-link-model-meetting' style='float:left;margin-left: 10px;margin-right: 10px' v-if="(index2 !== codeStreamLinkInfo.send[1].data.length)&&8*(i-1)<=index2&&index2<8*(i-1)+4&&i>1"></i>
        </el-tooltip>
        <!--第一行-->
        <terminalLinkChart style='float:left;' v-if="(index2 !== codeStreamLinkInfo.send[1].data.length-1)&&4*(i-1)<=index2&&index2<4*i-1&&i===1"></terminalLinkChart>
        <!--除第一行外的行数-->
        <terminalLinkChart style='float:left;' v-if="(index2 !== codeStreamLinkInfo.send[1].data.length-1)&&8*(i-1)<=index2&&index2<8 *(i-1)+4-1&&i>1"></terminalLinkChart>
        </span>
        <terminalLinkChartY style='margin-left:897px;margin-right:30px;' v-if="codeStreamLinkInfo.send[1].data.length>3+8*(i-1)&&codeStreamLinkInfo.send[1].data.length-[8 *(i-1)+4]>0"></terminalLinkChartY>
        </div>
        <!--大于四个时的图标以及标志信息-->
        <div style="height: 36px;margin-right:160px; margin-top: 33px">
        <span style="float:right;color: #9ca9b1;margin-left: 90px;width: 160px;margin-right: 20px" v-for='(value1,index1) in codeStreamLinkInfo.send[1].data' :key='index1'>
        <span v-if="index1>=4+8*(i-1)&&index1<4+8*(i-1)+4">
        <!--循环判断是否带图标-->
        <span style="border:#fb265d solid 4px;float:left;margin: 6px 0 0 0;border-radius:2em;" v-if="value1.status===0"></span>
        <span style="border: #63cd81 solid 4px;float:left;margin: 6px 0 0 0;border-radius:2em;" v-if="value1.status===1"></span>
        <!--上方ip等信息-->
        <span v-if="value1.ip&&value1.port" style="margin-left: 5px;float:right">{{ value1.desc + ":" + value1.ip + ":" + value1.port }}</span>
        <span v-if="!value1.ip&&(index1===0)" style="padding-left: 10px;margin-left: 5px">{{ value1.desc }}</span>
        <span v-if="!value1.ip&&!(index1===0)" style="padding-left: 35px;margin-left: 5px">{{ value1.desc }}</span>
        <span v-if="value1.ip&&!value1.port" style="margin-left:5px;">{{ value1.desc +':' +value1.ip }}</span>
				<!-- 2.0 -->
				<button type="button" class="button-host-info" @click="syn(value1)" v-if="(value1.desc==='合成'||value1.desc==='混音')&&value1.status===0">
				  <span style="text-decoration: underline;">查看</span>
				</button>
				<!-- 2.0 end -->
        </span>
        </span>
        </div>
        <!--大于4个时-->
        <div style="height: 42px;margin-right: 214px;" v-if="codeStreamLinkInfo.send[1].data.length>=4*i">
        <!--除第一个外的图标-->
        <span v-for='(value2,index2) in codeStreamLinkInfo.send[1].data' :key='index2'>
        <el-tooltip placement="bottom-start">
        <div slot="content" style="width:300px;height: 20px" v-for="( toopTip, indexAll) in codeStreamLinkInfo.send[1].data[index2+1]" v-if="indexAll!=='name'&&indexAll!=='desc'&&indexAll!=='ip'&&indexAll!=='port'&&indexAll!=='status'">
        <span style="display:block; float:left;min-width: 90px;text-align:right;">{{ indexAll }}</span> :  <span>{{ toopTip }}</span>
        </div>
        <!--<span style="display:block; float:left;min-width: 50px" v-if="indexAll!=='activepayload'&&indexAll!=='视频分辨率格式'">{{ indexAll }}</span> :  <span>{{ toopTip }}</span>-->
        <i class='ops-icons-bg icon-link-model-meetting' style='float:right;margin-left: 10px;margin-right: 10px;position: relative' v-if="(index2 !== codeStreamLinkInfo.send[0].data.length-1)&&4+8*(i-1)-1<=index2&&index2<4+8*(i-1)+4-1"></i>
        </el-tooltip>
        <terminalLinkChartsReverse style='position: relative;float: right' v-if="(index2 <= codeStreamLinkInfo.send[1].data.length-3)&&4+8*(i-1)-1<=index2&&index2<4+8*(i-1)+4-2"></terminalLinkChartsReverse>
        </span>
        </div>
        <terminalLinkChartY style='margin-left: 170px'  v-if="codeStreamLinkInfo.send[1].data.length>8*i"></terminalLinkChartY>
      </div>
		</div>

    <!--下行-->
		<div style="color:#9ca9b1;margin: 40px 50px 15px 50px ;font-size: 14px" v-if='showAll'>下行</div>
		<div class='recv' style="font-size: 14px;margin-bottom: 20px;width: 1300px;" v-for="(value,index) in codeStreamLinkInfo.recv" :key='"recv-"+index' v-if='showAll'>
      <div v-for=" i in forNumbRecvFirst">
        <!--小于等于四个时的状态图标以及标志信息-->
        <div style="height: 36px;margin-left: 150px; margin-top: 18px;">
          <span style="float:left;color: #9ca9b1;width: 270px;" v-for='(value1,index1) in value.data'  :key='index1'>
            <span v-if="8*(i-1)<=index1&&index1<8*(i-1)+4&&i===1">
              <!--循环判断是否带状态图标-->
              <span style="border:#fb265d solid 4px;float:left;margin: 6px auto;border-radius:2em;" v-if="value1.status===0"></span>
              <span style="border:#63cd81 solid 4px;float:left;margin: 6px auto;border-radius:2em;" v-if="value1.status===1"></span>
              <!--上方ip等信息-->
              <span v-if="value1.ip&&value1.port" style="margin-left: 5px;">{{value1.desc+':'+value1.ip+":"+value1.port}}</span>
              <span v-if="!value1.ip&&(index1===0)" style="padding-left: 10px;margin-left: 5px">{{value1.desc}}</span>
              <span v-if="!value1.ip&&!(index1===0)" style="padding-left: 55px;margin-left: 5px">{{value1.desc}}</span>
              <span v-if="value1.ip&&!value1.port" style="margin-left: 5px;">{{value1.desc+':'+value1.ip}}</span>
							<!-- 2.0 -->
							<button type="button" class="button-host-info" @click="syn(value1)" v-if="(value1.desc==='合成'||value1.desc==='混音')&&value1.status===0">
							  <span style="text-decoration: underline;">查看</span>
							</button>
							<!-- 2.0 end -->
            </span>
            <span v-if="8*(i-1)<=index1&&index1<8*(i-1)+4&&i>1">
              <!--循环判断是否带状态图标-->
              <span style="border:#fb265d solid 4px;float:left;margin: 6px auto;border-radius:2em;" v-if="value1.status===0"></span>
              <span style="border:#63cd81 solid 4px;float:left;margin: 6px auto;border-radius:2em;" v-if="value1.status===1"></span>
              <!--上方ip等信息-->
              <span v-if="value1.ip&&value1.port" style="margin-left: 5px;">{{value1.desc+':'+value1.ip+":"+value1.port}}</span>
              <span v-if="!value1.ip&&(index1===0)" style="padding-left: 10px;margin-left: 5px">{{value1.desc}}</span>
              <span v-if="!value1.ip&&!(index1===0)" style="padding-left: 55px;margin-left: 5px">{{value1.desc}}</span>
              <span v-if="value1.ip&&!value1.port" style="margin-left: 5px;">{{value1.desc+':'+value1.ip}}</span>
							<!-- 2.0 -->
							<button type="button" class="button-host-info" @click="syn(value1)" v-if="(value1.desc==='合成'||value1.desc==='混音')&&value1.status===0">
							  <span style="text-decoration: underline;">查看</span>
							</button>
							<!-- 2.0 end -->
            </span>
          </span>
        </div>
        <!--小于四个时的大图标-->
        <div style="height: 42px;margin-left: 150px;" >
          <!--图标-->
          <span v-for='(value2,index2) in value.data' :key='index2'>
            <el-tooltip placement="bottom-start">
              <div slot="content" style="width:300px;height: 20px" v-for="( toopTip, indexAll) in value2"  v-if="indexAll!=='name'&&indexAll!=='desc'&&indexAll!=='ip'&&indexAll!=='port'&&indexAll!=='status'">
                <span style="display:block; float:left;min-width: 90px;text-align:right;">{{ indexAll }}</span> :  <span>{{ toopTip }}</span>
              </div>
              <i class='ops-icons-bg icon-link-model-meetting' style='float:left;margin-left: 10px;margin-right: 10px' v-if="(index2 !== value.data.length)&&8*(i-1)<=index2&&index2<8*(i-1)+4&&i===1"></i>
              <i class='ops-icons-bg icon-link-model-meetting' style='float:left;margin-left: 10px;margin-right: 10px' v-if="(index2 !== value.data.length)&&8*(i-1)<=index2&&index2<8*(i-1)+4&&i>1"></i>
            </el-tooltip>
            <!--第一行-->
            <terminalLinkChart style='float:left;' v-if="(index2 !== value.data.length-1)&&4*(i-1)<=index2&&index2<4*i-1&&i===1"></terminalLinkChart>
            <!--除第一行外的行数-->
            <terminalLinkChart style='float:left;' v-if="(index2 !== value.data.length-1)&&8*(i-1)<=index2&&index2<8 *(i-1)+4-1&&i>1"></terminalLinkChart>
          </span>
          <terminalLinkChartY style='margin-left:897px;margin-right:30px;' v-if="value.data.length>3+8*(i-1)&&value.data.length-[8 *(i-1)+4]>0"></terminalLinkChartY>
        </div>
        <!--大于四个时的图标以及标志信息-->
        <div style="height: 36px;margin-right: 160px; margin-top: 33px">
          <span style="float:right;color: #9ca9b1;margin-left: 90px;width: 180px;" v-for='(value1,index1) in value.data' :key='index1'>
            <span v-if="index1>=4+8*(i-1)&&index1<4+8*(i-1)+4">
              <!--循环判断是否带图标-->
              <span style="border:#fb265d solid 4px;float:left;margin: 6px 0 0 0;border-radius:2em;" v-if="value1.status===0"></span>
              <span style="border: #63cd81 solid 4px;float:left;margin: 6px 0 0 0;border-radius:2em;" v-if="value1.status===1"></span>
              <!--上方ip等信息-->
              <span v-if="value1.ip&&value1.port" style="margin-left: 5px;float:right">{{ value1.desc + ":" + value1.ip + ":" + value1.port }}</span>
              <span v-if="!value1.ip&&(index1===0)" style="padding-left: 10px;margin-left: 5px">{{ value1.desc }}</span>
              <span v-if="!value1.ip&&!(index1===0)" style="padding-left: 35px;margin-left: 5px">{{ value1.desc }}</span>
              <span v-if="value1.ip&&!value1.port" style="margin-left:5px;">{{ value1.desc +':' +value1.ip }}</span>
							<!-- 2.0 -->
							<button type="button" class="button-host-info" @click="syn(value1)" v-if="(value1.desc==='合成'||value1.desc==='混音')&&value1.status===0">
							  <span style="text-decoration: underline;">查看</span>
							</button>
							<!-- 2.0 end -->
            </span>
          </span>
        </div>
        <!--大于4个时-->
        <div style="height: 42px;margin-right: 214px;" v-if="value.data.length>=4*i">
          <!--除第一个外的图标-->
          <span v-for='(value2,index2) in value.data' :key='index2'>
            <el-tooltip placement="bottom-start">
              <div slot="content" style="width:300px;height: 20px" v-for="( toopTip, indexAll) in value.data[index2+1]" v-if="indexAll!=='name'&&indexAll!=='desc'&&indexAll!=='ip'&&indexAll!=='port'&&indexAll!=='status'">
                <span style="display:block; float:left;min-width: 90px; text-align:right;">{{ indexAll }}</span> :<span style="">{{ toopTip }}</span>
              </div>
              <i class='ops-icons-bg icon-link-model-meetting' style='float:right;margin-left: 10px;margin-right: 10px;position: relative' v-if="(index2 !== value.data.length-1)&&4+8*(i-1)-1<=index2&&index2<4+8*(i-1)+4-1"></i>
            </el-tooltip>
            <terminalLinkChartsReverse style='position: relative;float: right' v-if="(index2 <= value.data.length-3)&&4+8*(i-1)-1<=index2&&index2<4+8*(i-1)+4-2"></terminalLinkChartsReverse>
          </span>
        </div>
        <terminalLinkChartY style='margin-left: 170px'  v-if="value.data.length>8*i"></terminalLinkChartY>
      </div>

			<!-- 2.0 -->
			<!-- 混音弹出框 -->
			<el-dialog
			title="详情"
			:visible.sync="mixDialog"
			width="800px"
			:close-on-click-modal="false">
				<div style="height: 500px;">
					<el-table
						stripe
						:data='mixTable'
						:cell-style='changeCellStyle'
						style='max-height: 500px;margin-top: 30px;margin-bottom: 30px;'>
						<el-table-column type="index" label='序号' min-width="57px"></el-table-column>
						<el-table-column label='终端' prop='mt_name' show-overflow-tooltip ></el-table-column>
						<el-table-column label='能量值' prop='energy' show-overflow-tooltip ></el-table-column>
						<el-table-column label='状态' prop='status' show-overflow-tooltip ></el-table-column>
					</el-table>
				</div>
				
			</el-dialog>
	
	
			<!-- 合成器弹出框 -->
			<el-dialog
			title="详情"
			:visible.sync="synDialog"
			width="700px"
			:close-on-click-modal="false">
				<div style="height: 500px;margin-left: 50px;margin-right: 50px;">
					<pictureSynthesis ></pictureSynthesis>
				</div>
				
			</el-dialog>
		</div>
	</div>
</template>

<script>
	export default{
    components: {
			pictureSynthesis: () => import('@/view/monitor/MonitorAlarmMeetingInfo/pictureSynthesis.vue'),
      terminalLinkChart: () => import('@/view/monitor/MonitorAlarmMeetingInfo/terminalLinkCharts.vue'),
      terminalLinkChartY: () => import('@/view/monitor/MonitorAlarmMeetingInfo/terminalLinkChartsY.vue'),
      terminalLinkChartsReverse: () => import('@/view/monitor/MonitorAlarmMeetingInfo/terminalLinkChartsReverse.vue'),
    },
		props: {
			callDetailTable: {
				type:Array,
				defaultList: [],
			},
		},
		data() {
			return {
				//2.0
				mixDialog:false,	
				synDialog:false,
				
        timeLine:50,
			  descriptions:[],
        timeChoice:"",
				terminalLinkTime: '',
        timeDefault:"请选择时间",
        timeitem:Date.now(),
									//日期设置对象
        // disabledtime:'',
				terminalLinkType:[{
					label:'主流',
					value:1,
				},{
					label:'辅流',
					value:2
				},{
					label:'音频',
					value:3
				}],
				terminalLinkTypes:1,
				codeStreamLinkInfo:{
			    "recv":[],
          "send":[],
        },
				sendFirstInfoSrc:"",
				recvFirstInfoSrc:'',
				showAll:false,
        withoutData:true,
        forNumbSendSecond :1,
        forNumbSendFirst:1,
        forNumbRecvFirst:1,
        forNumbRecvSecond :1,
        timeItems:"00:05:00",
        timeafter:"00:10:00",
        timebefore:"00:00:00",
			}
		},
		methods: {
			//合成器查看
      syn(value){
        if(value.desc==='合成'){
					// this.$message('合成器查看规则')
					this.synDialog = true
        }else if(value.desc==='混音'){
          // this.$message('混音器查看规则')
          this.mixDialog = true
          //发送请求混音器详情
        }
      },
			//混音器状态颜色改变
      changeCellStyle(object){																		//设置异常红色显示
      	// console.log(object)
      	let cellStyle = {
      		color:'red'
      	}
      	if (object.row.result === '异常' && object.columnIndex == 3){
      		return cellStyle
      	}
      },
      timeChange(value){
        var theTime = parseInt(value);// 秒
        var theTime1 = 0;// 分
        var theTime2 = 0;// 小时
        if(theTime > 60) {
          theTime1 = parseInt(theTime/60);
          theTime = parseInt(theTime%60);
          if(theTime1 > 60) {
            theTime2 = parseInt(theTime1/60);
            theTime1 = parseInt(theTime1%60);
          }
        }
        var result = ""+parseInt(theTime);
        if(parseInt(theTime)<10){
          result = ""+"0"+parseInt(theTime);
        }
        if(theTime1 >= 10) {
          result = ""+parseInt(theTime1)+":"+result;
        }else if(theTime1>=0){
          result = ""+"0"+parseInt(theTime1)+":"+result;
        }
        if(theTime2 >= 10) {
          result = ""+parseInt(theTime2)+":"+result;
        }else if(theTime2>=0){
          result = ""+"0"+parseInt(theTime2)+":"+result;
        }
        return result;
      },
      sendRequest(val){
        if(this.terminalLinkTime){
          var timeChoices  = this.timestampToTime(this.terminalLinkTime)
          var timeDate = timeChoices.split(" ")[0]
          timeDate = timeDate +" "+this.timeItems
          timeDate = new Date(timeDate).valueOf();
          var LinkTime = timeDate
          if(!this.callDetailTable[0].mt_e164){
            var mtE164 = this.callDetailTable[0].mt_addr
          }else {
            var mtE164 = this.callDetailTable[0].mt_e164
          }
          var params = {
            "conf_id":this.callDetailTable[0].conf_id,
            "mt_e164":mtE164,
            "time":LinkTime,
            "type":this.terminalLinkTypes,
						"conf_status":this.callDetailTable[0].conf_status,
          }
          this.requestFunction(params)
        }
      },
      timeLineChange(val){
        if(this.terminalLinkTime!==""&& this.terminalLinkTime!==null){
          var timeChoices  = this.timestampToTime(this.terminalLinkTime)
          var time = timeChoices.split(" ")[1]
          var hour = time.split(':')[0];
          var min = time.split(':')[1];
          var sec = time.split(':')[2];
          var s = Number(hour*3600) + Number(min*60) + Number(sec);
          this.timebefore = this.timeChange(s-300)
          this.timeafter = this.timeChange(s+300)
          if(val*6<300){
            var timeOne = 300-val*6
            this.timeItems = this.timeChange(s-timeOne)
          }else if(val*6>300){
            var timeOne = val*6-300
            this.timeItems = this.timeChange(s+timeOne)
          }else {
            this.timeItems = this.timeChange(s)
          }
        }else {
          this.timeItems = this.timeChange(val*6)
        }
      },
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
      getTerminalConfInfo(){
        if (this.callDetailTable[0]){
          if(!this.callDetailTable[0].mt_e164){
            var mtE164 = null
          }else {
            var mtE164 = this.callDetailTable[0].mt_e164
          }
          var params = {
            conf_id: this.callDetailTable[0].conf_id,
            mt_e164: mtE164,
            start_time:this.callDetailTable[0].start_time,
            end_time: this.callDetailTable[0].end_time,
            conf_type:this.callDetailTable[0].conf_type,
            conf_status:this.callDetailTable[0].conf_status,
          }
        }
				// console.log(params)
        this.$api.monitor.getterminalConfInfo(params).then(res=>{
          if(res.data.success===1){
						// console.log(res.data.data.info[0].data[res.data.data.info[0].data.length-1])
            this.terminalLinkTime = res.data.data.info[0].data[res.data.data.info[0].data.length-1].start_time
            if(!this.callDetailTable[0].mt_e164){
              var mtE164 = this.callDetailTable[0].mt_addr
            }else {
              var mtE164 = this.callDetailTable[0].mt_e164
            }
            var params = {
              "conf_id":this.callDetailTable[0].conf_id,
              "mt_e164":mtE164,
              "time":this.terminalLinkTime,
              "type":this.terminalLinkTypes,
							"conf_status":this.callDetailTable[0].conf_status,
            }
						this.timeLineChange()
            this.requestFunction(params)
          }else{}
        }).catch(err=>{})
      },
			getData(){
				// console.log(this.callDetailTable[0])
        if(this.callDetailTable[0].conf_status === 0){
          this.timeDefault = '请选择时间'
					// console.log(this.terminalLinkTime)
          if (this.terminalLinkTime === '' || this.terminalLinkTime === null){
            this.getTerminalConfInfo()
            // this.$message('请选择时间')
          }else {
            if(!this.callDetailTable[0].mt_e164){
              var mtE164 = this.callDetailTable[0].mt_addr
            }else {
              var mtE164 = this.callDetailTable[0].mt_e164
            }
            var params = {
              "conf_id":this.callDetailTable[0].conf_id,
              "mt_e164":mtE164,
              "time":this.terminalLinkTime,
              "type":this.terminalLinkTypes,
							"conf_status":this.callDetailTable[0].conf_status,
            }
            this.requestFunction(params)
          }
        }else if (this.callDetailTable[0].conf_status === 1 || this.callDetailTable[0].conf_status==="now"){
          this.timeDefault =this.timestampToTime(Date.now())
          if(this.terminalLinkTime===''){
            this.terminalLinkTime = (new Date()).valueOf()
          }
          if(!this.callDetailTable[0].mt_e164){
            var mtE164 = this.callDetailTable[0].mt_addr
          }else {
            var mtE164 = this.callDetailTable[0].mt_e164
          }
          var params = {
            "conf_id":this.callDetailTable[0].conf_id,
            "mt_e164":mtE164,
            "time":this.terminalLinkTime,
            "type":this.terminalLinkTypes,
						"conf_status":this.callDetailTable[0].conf_status,
          }
          this.requestFunction(params)
        }
			},
      requestFunction(params){
        this.$api.monitor.getTerminalMtsLinkInfo(params).then(res=>{
          if (res.data.success === 1){
            // 转换recv tooptip文字
            if (res.data.data.info.recv){
              if(res.data.data.info.recv[0]){
                for (let value in res.data.data.info.recv[0].data){
                  res.data.data.info.recv[0].data[value] = this.changeItemToChin(res.data.data.info.recv[0].data[value])
                }
              }
              if(res.data.data.info.recv[1]){
                for (let value in res.data.data.info.recv[1].data){
                  res.data.data.info.recv[1].data[value] = this.changeItemToChin(res.data.data.info.recv[1].data[value])
                }
              }
            }
            // 转换send tooptip文字
            if (res.data.data.info.send){
              if(res.data.data.info.send[0]){
                for (let value in res.data.data.info.send[0].data){
                  res.data.data.info.send[0].data[value] = this.changeItemToChin(res.data.data.info.send[0].data[value])
                }
              }
              if(res.data.data.info.send[1]){
                for (let value in res.data.data.info.send[1].data){
                  res.data.data.info.send[1].data[value] = this.changeItemToChin(res.data.data.info.send[1].data[value])
                }
              }
            }
            //识别上行循环几次
            if(res.data.data.info.send){
              if(res.data.data.info.send[1]){
                if(res.data.data.info.send[1].data){
                  this.forNumbSendSecond=Math.ceil(res.data.data.info.send[1].data.length/8)
                }
              }
              if(res.data.data.info.send[0]){
                if(res.data.data.info.send[0].data){
                  this.forNumbSendFirst = Math.ceil(res.data.data.info.send[0].data.length/8)
                }
              }
            }
            if(res.data.data.info.recv){
              if(res.data.data.info.recv[1]){
                this.forNumbRecvSecond=Math.ceil(res.data.data.info.recv[1].data.length/8)
              }else if(res.data.data.info.recv[0]){
                this.forNumbRecvFirst=Math.ceil(res.data.data.info.recv[0].data.length/8)
              }
            }
            this.codeStreamLinkInfo = res.data.data.info
            if (this.codeStreamLinkInfo.recv.length===0&&this.codeStreamLinkInfo.send.length===0){
              this.withoutData=true
              this.showAll = false
            }else{
              this.withoutData=false
              this.showAll = true
            }
          }
        }).catch(err=>{})

      },
			terminalLinkTypeChange(){
				this.getData()
			},
			terminalDateLink(){
        this.timeLine = 50
				this.getData()
        this.timeLineChange()
			},
      changeItemToChin(val){
        for (let key in val){
          if (key === "bitrate"){
            if(val[key]){
              val["码率"] = val[key]+"kbps"
            }else{
              val["码率"] = val[key]
            }
            delete val.bitrate
          }else if (key==="format"){
            val["视频格式"] = val[key]
            delete val.format
          }else if (key==="res"){
            val["视频分辨率格式"] = val[key]
            delete val.res
          }else if (key==="callid"){
            delete val.callid
          }else if (key==="lose_percent"){
            if(val[key]){
              val["丢包率"] = val[key]+"%"
            }else{
              val["丢包率"] = val[key]
            }
            delete val.lose_percent
          }else if (key==="channel"){
            val["通道id"] = val[key]
            delete val.channel
          }else if (key==="handle"){
            val["媒体句柄"] = val[key]
            delete val.handle
          }else if (key==="bps"){
            if(val[key]){
              val["码率"] = val[key]+"kbps"
            }else{
              val["码率"] = val[key]
            }
            delete val.bps
          }else if (key==="pps"){
            if(val[key]){
              val["帧率"] = val[key]+"fps"
            }else{
              val["帧率"] = val[key]
            }
            delete val.pps
          }
        }
        return val
      },
		},
		mounted(){
			this.getData()
		},
		watch: {
			callDetailTable(newValue, oldValue) {
				this.getData()
			}
		},

	}
</script>

<style>
.block .el-slider__button-wrapper{
  top: -17px;
}
  .block .el-slider__bar{
    height: 1px;
    background-color: #5d6368;
  }
  .block .el-slider__runway{
    height: 1px;
    background-color: #5d6368;
  }
  .block .el-slider__button{
    width: 1px;
    height: 1px;
    border: 1px solid #9ca9b1;
    background: none;
    box-shadow:
    0 0 0 10px inset #9ca9b1, 0 0 0 4px #232629, 0 0 0 5px #9ca9b1;
    background:#9ca9b1;
  }
</style>
