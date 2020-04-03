<template>
	<div class='theme-dark MonitorAlarmSettings' >
		<el-row type='flex' justify="space-around" >
			<el-col :span='6' style="background: #232629;margin-right: 20px; ">
				<div  style="float: left ;width: 288px;height: 326px;background: #232629; padding: 12px 20px;color: #9ca9b1;">
					<div style="color: #9ca9b1;font-size: 14px;">平台服务器硬件资源</div>
					<el-form label-width="100px" label-position="left" :model='platformServerHardwareResources' style="color: #9ca9b1;font-size: 12px">
						<el-form-item label='CPU使用率' style='padding-top: 16px;margin: 0px;'>
							<el-input  @blur="hardware" style='width:80px;' v-model='platformServerHardwareResources.cpu' maxlength="3" oninput ="value=value.replace(/\D/g,'')"  ></el-input><span style="margin-left: 10px" >%</span>
						</el-form-item>
						<el-form-item label='内存使用率' style="margin: 4px 0px 0px 0px">
							<el-input @blur="hardware" style='width:80px;' v-model='platformServerHardwareResources.memory'  maxlength="3" oninput ="value=value.replace(/\D/g,'')"  ></el-input><span style="margin-left: 10px">%</span>
						</el-form-item>
						<el-form-item label='硬盘分区使用率' style="margin: 4px 0px 0px 0px">
							<el-input @blur="hardware" style='width:80px;' v-model='platformServerHardwareResources.disk'  maxlength="3" oninput ="value=value.replace(/\D/g,'')"  ></el-input><span style="margin-left: 10px">%</span>
						</el-form-item>
						<el-form-item label='硬盘读写速率' style="margin: 4px 0px 0px 0px">
							<el-input @blur="hardware" style='width:80px;' v-model='platformServerHardwareResources.diskwritespeed' maxlength="5" oninput ="value=value.replace(/\D/g,'')"  ></el-input><span style="margin-left: 10px">M</span>
						</el-form-item>
						<el-form-item label='网口吞吐' style="margin: 4px 0px 0px 0px">
							<el-input @blur="hardware" style='width:80px;' v-model='platformServerHardwareResources.rateofflow' maxlength="5" oninput ="value=value.replace(/\D/g,'')"  ></el-input><span style="margin-left: 10px">Mbps</span>
						</el-form-item>
						<el-form-item label='磁盘寿命' style="margin: 4px 0px 0px 0px">
							<el-input @blur="hardware" style='width:80px;' v-model='platformServerHardwareResources.diskage' maxlength="3" oninput ="value=value.replace(/\D/g,'')"  ></el-input><span style="margin-left: 10px">%</span>
						</el-form-item>
					</el-form>
				</div>
			</el-col>
			<el-col :span='6' style="background: #232629;margin-right: 20px; ">
				<div  style="float: left ;width: 288px;height: 326px;background: #232629; padding: 12px 20px;color: #9ca9b1;">
					<div style="color: #9ca9b1;font-size: 14px;">平台硬件媒体资源使用率</div>
					<el-form label-width="100px" label-position="left" :model='platformHardwareMediaResourceUsage'>
						<el-form-item label='合成器' style='padding-top: 16px;margin: 0px;'>
							<el-input @blur="hardwareMedia" style='width:80px;' v-model="platformHardwareMediaResourceUsage.vmp"  maxlength="3" oninput ="value=value.replace(/\D/g,'')"  ></el-input><span style="margin-left: 10px">%</span>
						</el-form-item>
						<el-form-item label='混音器' style="margin: 4px 0px 0px 0px">
							<el-input @blur="hardware" style='width:80px;' v-model="platformHardwareMediaResourceUsage.mixer" maxlength="3" oninput ="value=value.replace(/\D/g,'')"  ></el-input><span style="margin-left: 10px">%</span>
						</el-form-item>
					</el-form>
				</div>
			</el-col>
			<el-col :span='6' style="background: #232629;margin-right: 20px; ">
				<div  style="float: left ;width: 288px;height: 326px;background: #232629; padding: 12px 20px;color: #9ca9b1;">
					<div style="color: #9ca9b1;font-size: 14px;">平台媒体授权资源使用率</div>
					<el-form label-width="100px" label-position="left" :model="platformMediaAuthorResourceUsage">
						<el-form-item label='媒体端口(MP)' style='padding-top: 16px;margin: 0px;'>
              <el-input @blur="mediaAuthor(platformMediaAuthorResourceUsage.mp,)" style='width:80px;' v-model='platformMediaAuthorResourceUsage.mp' maxlength="3" oninput ="value=value.replace(/\D/g,'')" ></el-input><span style="margin-left: 10px">%</span>
						</el-form-item>
						<el-form-item label='接入端口(AP)' style="margin: 4px 0px 0px 0px">
							<el-input @blur="mediaAuthor" style='width:80px;' v-model='platformMediaAuthorResourceUsage.ap' maxlength="3" oninput ="value=value.replace(/\D/g,'')"  ></el-input><span style="margin-left: 10px">%</span>
						</el-form-item>
					</el-form>
				</div>
			</el-col>
			<el-col :span='6' style="background: #232629;">
				<div  style="float: left ;width: 288px;height: 326px;background: #232629; padding: 12px 20px;color: #9ca9b1;">
					<div style="color: #9ca9b1;font-size: 14px;">外设服务器授权资源</div>
					<el-form label-width="100px" label-position="left" :model="peripheralResources">
						<el-form-item label='录像并发数' style='padding-top: 16px;margin: 0px;'>
							<el-input @blur="peripheral" style='width:80px;' v-model='peripheralResources.video_num' maxlength="5" oninput ="value=value.replace(/\D/g,'')"  ></el-input><span style="margin-left: 10px">个</span>
						</el-form-item>
						<el-form-item label='直播会议并发数' style="margin: 4px 0px 0px 0px">
							<el-input @blur="peripheral" style='width:80px;' v-model='peripheralResources.live_num' maxlength="5" oninput ="value=value.replace(/\D/g,'')"  ></el-input><span style="margin-left: 10px">个</span>
						</el-form-item>
						<el-form-item label='直播观看人数' style="margin: 4px 0px 0px 0px">
							<el-input @blur="peripheral" style='width:80px;' v-model='peripheralResources.viewer_num' maxlength="5" oninput ="value=value.replace(/\D/g,'')"  ></el-input><span style="margin-left: 10px">个</span>
						</el-form-item>
						<el-form-item label='协作会议数' style="margin: 4px 0px 0px 0px">
							<el-input @blur="peripheral" style='width:80px;' v-model='peripheralResources.dcs_conf_num' maxlength="5" oninput ="value=value.replace(/\D/g,'')"  ></el-input><span style="margin-left: 10px">个</span>
						</el-form-item>
						<el-form-item label='协作人员数' style="margin: 4px 0px 0px 0px">
							<el-input @blur="peripheral" style='width:80px;' v-model='peripheralResources.dcs_user_num' maxlength="5" oninput ="value=value.replace(/\D/g,'')"  ></el-input><span style="margin-left: 10px">个</span>
						</el-form-item>
					</el-form>
				</div>
		</el-col>
		</el-row>
		<div style="clear:both"></div>
	</div>
</template>

<script>
    export default {
			name: "MonitorAlarmSettings",
			data() {
				return {
					beginData:{},
					platformServerHardwareResources:{},
					platformHardwareMediaResourceUsage:{},
					platformMediaAuthorResourceUsage:{},
					peripheralResources: {},
				}
			},
			methods: {
				getData(){
					this.$api.monitor.GetThresholds().then(res=>{
						if (res.data.success === 1){
							this.beginData = res.data.data[0]
							this.platformServerHardwareResources = res.data.data[0]
							this.platformHardwareMediaResourceUsage = res.data.data[0]
							this.platformMediaAuthorResourceUsage = res.data.data[0]
							this.peripheralResources = res.data.data[0]
							// console.log(res.data.data[0])
						}
						else if(res.data.success === 0){
							console.log(res.data.msg)
						}
						
					})
				},
				sendData(params) {																							//修改阈值信息
					// console.log(params)
					// console.log(this.beginData)
					for (var i in params){
						if (typeof params[i] === "string"){
              if(i==='cpu'||i==='memory'||i==='disk'||i==='vmp'||i==='mixer'||i==='mp'||i==='ap'){
                if(parseInt(params[i])>100||params[i]===''||parseInt(params[i])===0){
                  params[i]='80'
                }
              }
              if(i==='diskage'){
                if(parseInt(params[i])>100||params[i]===''||parseInt(params[i])===0){
                  params[i]='20'
                }
              }
              if(i==="video_num"){
                if(parseInt(params[i])===0||params[i]===''){
                  params[i]='16'
                }
              }
              if(i==="live_num"){
                if(parseInt(params[i])===0||params[i]===''){
                  params[i]='3'
                }
              }
              if(i==="viewer_num"){
                if(parseInt(params[i])===0||params[i]===''){
                  params[i]='300'
                }
              }
              if(i==="dcs_conf_num"){
                if(parseInt(params[i])===0||params[i]===''){
                  params[i]='25'
                }
              }
              if(i==="dcs_user_num"){
                if(parseInt(params[i])===0||params[i]===''){
                  params[i]='25'
                }
              }
              if(i==="rateofflow"){
                if(parseInt(params[i])===0||params[i]===''){
                  params[i]='60'
                }
              }
              if(i==="diskwritespeed"){
                if(parseInt(params[i])===0||params[i]===''){
                  params[i]='2'
                }
              }
							var m ={}
							m[i] = parseInt(params[i])
							// console.log(m)
							this.modify = {
								"m":m,
								"id":params.id
							}
							this.$api.monitor.putThresholds(this.modify).then(res=>{
								if (res.data.success === 1){
									this.$message('设置成功')
                  this.getData()
								}else if(res.data.success===0){
								  this.$message('设置失败')
                  this.getData()
                }
							}).catch(err=>{
                this.getData()
              })
						}
						
					}
					// console.log(this.modify)
					
				},
				hardware(event) {
					// console.log(event,this.platformServerHardwareResources)
					this.sendData(this.platformServerHardwareResources)
				},
				hardwareMedia(event) {
					// console.log(this.platformHardwareMediaResourceUsage)
					this.sendData(this.platformHardwareMediaResourceUsage)
				},
				mediaAuthor(event) {
          this.sendData(this.platformMediaAuthorResourceUsage)
				},
				peripheral(event) {
					// console.log(this.peripheralResources)
					this.sendData(this.peripheralResources)
				}
			},
			mounted(){
				this.getData()
			},
      computed:{
			  _inputRules:{
			    set function(value){
            this.platformServerHardwareResources.cpu = value
          },
          get function(){
            let temp = this.inputTimeOut.replace(/[^0-9]+/g,'')
            if(!temp) temp = '60'
            return parseInt(temp) > 100 ? '100' : parseInt(temp)<=1 ? '1' : temp
          }
        }
      }
    }
</script>

<style>
  .MonitorAlarmSettings .el-form-item__label{
    font-size:12px ;
    color: #9ca9b1;
    padding:0px;

  }


</style>
