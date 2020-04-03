<template>
    <div class="theme-dark">
      <el-select :popper-append-to-body="false" popper-class="theme-dark" v-model="optionSelectedMapCountry" disabled placeholder="请选择区域" >
        <el-option
          v-for="item in optionsMapCountry" :key="item.name" :label="item.name" :value="item.name">
        </el-option>
      </el-select>
      <el-select @change="provinceChange" filterable :popper-append-to-body="false" popper-class="theme-dark" v-model="optionSelectedMapProvince" placeholder="请选择区域" style="margin-left: 7px;">
        <el-option
          v-for="item in optionsMapProvince" :key="item.id" :label="item.name" :value="item.id">
        </el-option>
      </el-select>
      <el-select @change="cityChange" filterable :popper-append-to-body="false" popper-class="theme-dark" v-model="optionSelectedMapCity" placeholder="请选择区域" v-show="optionSelectedMapProvince!=='all'" style="margin-left: 7px;">
        <el-option
          v-for="item in optionsMapCity" :key="item.id" :label="item.name" :value="item.id">
        </el-option>
      </el-select>
    </div>
</template>

<script>
export default {
  name: "MapSettingGeoInfoGlobal",
  data(){
    return {
      // 地图配置
      mapConfig:'',

      // 下拉菜单选择项
      optionsMapCountry:[{
        name:"中华人民共和国"
      }],
      optionsMapProvince:[{
        id:'all',
        name:"不限"
      }],
      optionsMapCity:[{
        id:'all',
        name:"不限",
        province:'all'
      }],

      optionSelectedMapCountry:'中华人民共和国',
      optionSelectedMapProvince:'all',
      optionSelectedMapCity:'all',

    }
  },
  methods:{
    // 选择省
   async provinceChange(val){
     let paramsProvince=val
     if(val!=="all"){
      let getCity=await this.$api.homePage.getCityInfo({province:val})
      this.optionsMapCity=[this.optionsMapCity[0],...getCity]
       this.optionSelectedMapCity="all"
     }
     else{
       this.optionsMapCity=[{
         id:'all',
         name:"不限",
         province:'all'
       }]
       this.optionSelectedMapCity="all"
       paramsProvince=null
     }
     this.$api.homePage.putMapBaseConfig(this.mapConfig.id,{province:paramsProvince,city:null})
       .then(res=>{
         // console.log("provinceChange")
       })
    },
    // 选择市
    cityChange(val){
      // console.log(val)
      let paramsCity=val
      if(val==="all"){
        paramsCity=null
      }
      this.$api.homePage.putMapBaseConfig(this.mapConfig.id,{province:this.optionSelectedMapProvince,city:paramsCity})
        .then(res=>{
          // console.log("cityChange")
        })
    },
    // API START

    // API end

    async init(){
      this.mapConfig= await this.$api.homePage.getMapBaseConfig()
      if(this.mapConfig && this.mapConfig.length>0){
        this.mapConfig=this.mapConfig[0]
        let getProvince=await this.$api.homePage.getProvinceInfo()
        this.optionsMapProvince=[...this.optionsMapProvince,...getProvince]
        if(this.mapConfig.city){
          let getCity=await this.$api.homePage.getCityInfo({province:this.mapConfig.province.id})
          this.optionsMapCity=[this.optionsMapCity[0],...getCity]
          this.optionSelectedMapProvince=this.mapConfig.province.id
          this.optionSelectedMapCity=this.mapConfig.city.id
          // console.log("city---> ",this.mapConfig.province,this.mapConfig.city)
        }else if(this.mapConfig.province){
          // console.log("province---> ",this.mapConfig.province)
          this.optionSelectedMapProvince=this.mapConfig.province.id
          let getCity=await this.$api.homePage.getCityInfo({province:this.mapConfig.province.id})
          this.optionsMapCity=[this.optionsMapCity[0],...getCity]
          this.optionSelectedMapCity="all"
        }else{
          // console.log("china--->",this.mapConfig.id)
          this.optionSelectedMapProvince="all"
        }
      }else if(this.mapConfig.length === 0){
        this.$api.homePage.postMapBaseConfig({province:null,city:null})
          .then(res=>{
            this.init()
            // console.log(res)
          })
      }else{
        // console.log("error")
      }


      // console.log(this.optionsMapProvince)
    },
  },
  mounted(){
    this.init()
  },
}
</script>

<style scoped>

</style>
