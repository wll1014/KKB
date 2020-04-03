<template>
    <div class="ke-style-dark">
      <div style="color: #9ca9b1;margin-top: 4px;">主视频</div>
      <el-table stripe :data='mainVideoList' style='margin-top: 20px;'>
        <el-table-column prop='mianlay' label="上下行" show-overflow-tooltip min-width="300px"></el-table-column>
        <el-table-column prop='videoFormat' label="视频格式" show-overflow-tooltip min-width="180px"></el-table-column>
        <el-table-column prop='resolution' label="分辨率" show-overflow-tooltip min-width="180px"></el-table-column>
        <el-table-column prop='bitrate' label="码率" show-overflow-tooltip min-width="180px"></el-table-column>
        <el-table-column prop='frame' label="帧率" show-overflow-tooltip min-width="180px" v-if="this.callDetailTable[0]&&this.callDetailTable[0].conf_status===0&&this.callDetailTable[0].conf_type!==2"></el-table-column>
        <el-table-column prop='audioFormat' label="音频格式" show-overflow-tooltip min-width="315px"></el-table-column>
      </el-table>
      <div style="color: #9ca9b1;margin-top:28px;" >辅视频</div>
      <el-table stripe :data='secondaryVideoList' style='margin-top: 20px;'>
        <el-table-column prop='mianlay' label="上下行" show-overflow-tooltip min-width="300px"></el-table-column>
        <el-table-column prop='videoFormat' label="视频格式" show-overflow-tooltip min-width="180px"></el-table-column>
        <el-table-column prop='resolution' label="分辨率" show-overflow-tooltip min-width="180px"></el-table-column>
        <el-table-column prop='bitrate' label="码率" show-overflow-tooltip min-width="180px"></el-table-column>
        <el-table-column prop='frame' label="帧率" show-overflow-tooltip min-width="180px" v-if="this.callDetailTable[0]&&this.callDetailTable[0].conf_status===0&&this.callDetailTable[0].conf_type!==2"></el-table-column>
        <el-table-column prop='audioFormat' label="音频格式" show-overflow-tooltip min-width="315px"></el-table-column>
      </el-table>
<!-- 			<div style="color: #9ca9b1;margin-top:28px;" >状态</div>
			<el-table stripe :data='secondaryVideoList' style='margin-top: 20px;'>
				<el-table-column label="序号" type="index"></el-table-column>
			  <el-table-column prop='' label="接口" show-overflow-tooltip min-width=""></el-table-column>
				<el-table-column prop='' label="接口状态" show-overflow-tooltip min-width=""></el-table-column>
			  <el-table-column prop='' label="音视频采集状态" show-overflow-tooltip min-width=""></el-table-column>
			  <el-table-column prop='' label="音视频播放状态" show-overflow-tooltip min-width=""></el-table-column>
			  <el-table-column prop='' label="音视频编码状态" show-overflow-tooltip min-width=""></el-table-column>
			  <el-table-column prop='' label="音视频解码状态" show-overflow-tooltip min-width=""></el-table-column>
			  <el-table-column prop='' label="通道状态" show-overflow-tooltip min-width=""></el-table-column>
				<el-table-column label="操作">
					<template slot-scope="scope">
						<button type="button" class="button-host-info" @click="statusDetail()" v-if="status===1">
							<span style="text-decoration: underline;">详情</span>							
						</button>
						<button disabled type="button" class="button-host-info" @click="statusDetail()" v-if="status===0">
							<span style="text-decoration: underline;color: gray;" >详情</span>
						</button>
						
					</template>
				</el-table-column>
			</el-table>
			 -->
			<el-dialog
			  title="详情"
			  :visible.sync="statuslDetailInfo"
			  width="600px"
			  :close-on-click-modal="false">
			  <div style="width:526px;height: 400px;overflow:auto;padding-right: 25px" class="logShowApp" >
					<span v-if="rowAll">
						{{rowAll}}
					</span>
				</div>
			  <div align="center" slot='footer' class='theme-dark' style='margin-top:32px;margin-bottom:10px;'>
			    <el-button @click='statuslDetailInfo=false'>关闭</el-button>
			  </div>
			</el-dialog>
			
    </div>
</template>

<script>
    export default {
      name: "videoSource",
      props: {
        callDetailTable: {
          type:Array,
          defaultList: [],
        },
      },
      data(){
        return{
					statuslDetailInfo:false,								//状态详情
					rowAll:'',															//弹出框内容
          mainVideoList:[],
          secondaryVideoList:[],
					info:[],
        }
      },
      methods:{
				statusDetail(){											//状态详情
					this.statuslDetailInfo = true
				},
        getData(){
					var params={
						"start_time":this.callDetailTable[0].start_time,
						"end_time":this.callDetailTable[0].end_time,
						"conf_status":this.callDetailTable[0].conf_status,
						"mt_e164":this.callDetailTable[0].mt_e164,
						"conf_id":this.callDetailTable[0].conf_id
					}
					this.$api.monitor.getChannel(params).then(res=>{
						if(res.data.success===1){
							// console.log(res.data.data.info[0])
							this.info = res.data.data.info
							for(var item in this.info[0]) {
								if(this.info[0][item]===''){
									this.info[0][item]='   ----'
								}
							}
							if(this.info[0]){
							  if(this.info[0].privideo_video_up_bitrate!=="   ----"){
							    var privideo_video_up_bitrate = this.info[0].privideo_video_up_bitrate+"kbps"
							  }else{
							    var privideo_video_up_bitrate = "   ----"
							  }
							  if(this.info[0].privideo_video_up_framerate!=="   ----"){
							    var privideo_video_up_framerate = this.info[0].privideo_video_up_framerate+"fps"
							  }else{
							    var privideo_video_up_framerate = "   ----"
							  }
							  if(this.info[0].privideo_video_down_bitrate!=="   ----"){
							    var privideo_video_down_bitrate = this.info[0].privideo_video_down_bitrate+"kbps"
							  }else{
							    var privideo_video_down_bitrate = "   ----"
							  }if(this.info[0].privideo_video_down_framerate!=="   ----"){
							    var privideo_video_down_framerate = this.info[0].privideo_video_down_framerate+"fps"
							  }else{
							    var privideo_video_down_framerate = "   ----"
							  }if(this.info[0].assvideo_video_up_bitrate!=="   ----"){
							    var assvideo_video_up_bitrate = this.info[0].assvideo_video_up_bitrate+"kbps"
							  }else{
							    var assvideo_video_up_bitrate = "   ----"
							  }if(this.info[0].assvideo_video_up_framerate!=='   ----'){
							    var assvideo_video_up_framerate = this.info[0].assvideo_video_up_framerate+"fps"
							  }else{
							    var assvideo_video_up_framerate = "   ----"
							  }if(this.info[0].assvideo_video_down_bitrate!=="   ----"){
							    var assvideo_video_down_bitrate = this.info[0].assvideo_video_down_bitrate+"kbps"
							  }else{
							    var assvideo_video_down_bitrate = "   ----"
							  }if(this.info[0].assvideo_video_down_framerate!=="   ----"){
							    var assvideo_video_down_framerate = this.info[0].assvideo_video_down_framerate+"fps"
							  }else{
							    var assvideo_video_down_framerate = "   ----"
							  }
							  if(this.info[0].privideo_video_up_format!=="   ----"||this.info[0].privideo_video_up_res!=="   ----"||privideo_video_up_bitrate!=="   ----"||privideo_video_up_framerate!=="   ----"){
							    var upFormatFirst = this.info[0].audio_up_format
							  }else{
							    var upFormatFirst="   ----"
							  }
							  if(this.info[0].privideo_video_down_format!=="   ----"||this.info[0].privideo_video_down_res!=="   ----"||privideo_video_down_bitrate!=="   ----"||privideo_video_down_framerate!=="   ----"){
							    var downFormatFirst = this.info[0].audio_down_format
							  }else{
							    var downFormatFirst="   ----"
							  }
							  if(this.info[0].assvideo_video_up_format!=="   ----"||this.info[0].assvideo_video_up_res!=="   ----"||assvideo_video_up_bitrate!=="   ----"||assvideo_video_up_framerate!=="   ----"){
							    var upFormatSecond = this.info[0].audio_up_format
							  }else{
							    var upFormatSecond="   ----"
							  }
							  if(this.info[0].assvideo_video_down_format!=="   ----"||this.info[0].assvideo_video_down_res!=="   ----"||assvideo_video_down_bitrate!=="   ----"||assvideo_video_down_framerate!=="   ----"){
							      var downFormatSecond = this.info[0].audio_down_format
							  }else{
							    var downFormatSecond="   ----"
							  }
							  this.mainVideoList = [{
							      "mianlay":"上行",
							      "videoFormat":this.info[0].privideo_video_up_format,
							      "resolution":this.info[0].privideo_video_up_res,
							      "bitrate":privideo_video_up_bitrate,
							      "frame":privideo_video_up_framerate,
							      "audioFormat":upFormatFirst,
							  },{
							      "mianlay":"下行",
							      "videoFormat":this.info[0].privideo_video_down_format,
							      "resolution":this.info[0].privideo_video_down_res,
							      "bitrate":privideo_video_down_bitrate,
							      "frame":privideo_video_down_framerate,
							      "audioFormat":downFormatFirst,}]
							  this.secondaryVideoList=[{
							    "mianlay":"上行",
							    "videoFormat":this.info[0].assvideo_video_up_format,
							    "resolution":this.info[0].assvideo_video_up_res,
							    "bitrate":assvideo_video_up_bitrate,
							    "frame":assvideo_video_up_framerate,
							    "audioFormat":upFormatSecond,},{
							    "mianlay":"下行",
							    "videoFormat":this.info[0].assvideo_video_down_format,
							    "resolution":this.info[0].assvideo_video_down_res,
							    "bitrate":assvideo_video_down_bitrate,
							    "frame":assvideo_video_down_framerate,
							    "audioFormat":downFormatSecond,}]
							}
						}else if(res.data.success===0){}
					}).catch(err=>{})
					// console.log(this.info)
          
        },
      },
      watch: {
        callDetailTable(newValue, oldValue) {

          this.getData()
        }
      },
      mounted(){
        this.getData()
      },
    }
</script>

<style >
.logShowApp {
    white-space: pre-line;
    word-break: break-all;
    word-wrap: break-word;
    overflow: hidden;
    line-height: 26px;

  }
</style>
