import base from '@/api/base'; // 导入接口域名列表
import axios from '@/api/http'; // 导入http中创建的axios实例

const ConferenceTopology = {
  async getMachineRoom(params){
    let res = await axios.get(`${base.master}/diagnose/topology/machine_rooms/`, {params: params})

    let data =  res.data.data
    return data
  },
  async getSingleMachineRoom(moid){
    let params={
      machine_room_moid:moid,
    }
    let res = await this.getMachineRoom(params)
    // console.log(res)
    let data = res[0]
    return data ? data : null
  },
  async getConfRoom(params){
    let res = await axios.get(`${base.master}/diagnose/topology/confs/`, {params: params})
    let data = res.data.data
    return data
  },
  async getConfMt(id,params){
    let res = await axios.get(`${base.master}/diagnose/topology/confs/${id}/`, {params: params})
    let data = res.data.data.info
    return data
  },
};

export default ConferenceTopology;
