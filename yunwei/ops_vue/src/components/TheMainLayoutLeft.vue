<template>
			<!-- <div class="kd-siderbar" :style="siderbarStyle" > -->
      <div class="kd-siderbar" :style="{width: this.siderbarWidth + 'px'}" >
        <div class="area-siderbar--time">
          <div v-if="!isCollapse">
            {{timeNowFull}}
          </div>
          <div v-else>
            <div style="margin-bottom: 3px;">{{timeNowSplit[2]}}</div><div style="margin-bottom: 3px;">{{timeNowSplit[0]}}</div><div>{{timeNowSplit[1]}}</div>
          </div>
        </div>
        <el-scrollbar :class="isCollapse ? 'siderbar-scrollbar--collapse' : 'siderbar-scrollbar'" :noresize="false">
        <el-row class="tac" :style="{width: this.siderbarWidth + 'px',}">
          <el-col :span="24" >
          <!-- 展开收起按钮 -->
			    <div class="buttom-collapse" @click="collapseStatuChange">
            <transition name="el-zoom-in-right" >
              <div v-if="!isCollapse">
              <i class="ops-icons-bg siderbar--not-collapse"></i>
              </div>
              <div v-else>
              <i class="ops-icons-bg siderbar--collapse"></i>
              </div>
            </transition>
			    </div>
          <!-- 收起状态 -->
          <transition name="kd-fade-in-linear">
			    <div class="siderbar-collapse" v-show="isCollapse">
			        <ul class="kd-menu">
			          <li :class="['kd-submenu',{'is-opened':isOpened[i.url]}]" @click="submenuClick(i.url)" 
			          v-for="i in siderbarInfo" :index="i.url" :key="i.url" v-if="i.childnode">
                  <el-tooltip class="item" effect="dark" :content="i.title" placement="right">
                    <div :class="['kd-submenu__title',{'is-active':isActived[i.url]}]">
                      <i :class="['ops-icons-bg',i.icon,{'is-active':isActived[i.url]}]"></i>
                    </div>
                  </el-tooltip>
                  <el-collapse-transition>  
                    <ul :class="['kd-menu','kd-menu--inline','menu-childnode-background-color']" v-show="isOpened[i.url]">
                      <el-tooltip v-for="i2 in i.childnode" class="item" effect="dark" :content="i2.title" placement="right" :key="i2.url">
                        <li :class="['kd-menu-item',{'is-active':isActived[i2.url]}]" :index="i2.url"  @click.stop="menuItemClick(i2.url,i.url)">
                          <div class="siderbar--selected-strip" v-if="isActived[i2.url]"></div>
                          <i :class="['ops-icons-bg',i2.icon,{'is-active':isActived[i2.url]}]"></i>
                        </li>
                      </el-tooltip>
                    </ul>
                  </el-collapse-transition>
			          </li>
                
                <el-tooltip class="item" effect="dark" :content="i.title" placement="right" v-else>
			          <li :class="['kd-menu-item',{'is-active':isActived[i.url]}]" :index="i.url" :key="i.url" @click="menuItemClick(i.url)" >
                  <div class="siderbar--selected-strip" v-if="isActived[i.url]"></div>
                  <i :class="['ops-icons-bg',i.icon,{'is-active':isActived[i.url]}]"></i>
			          </li>
                </el-tooltip>
			        </ul>
			    </div>
			    </transition>
          
          <!-- 展开状态 -->
          <transition name="kd-zoom-in-left" >
          <div class="siderbar-not-collapse" v-show="!isCollapse">
			      <ul class="kd-menu">
			        <li :class="['kd-submenu',{'is-opened':isOpened[i.url]}]" @click="submenuClick(i.url)" 
			        v-for="i in siderbarInfo" :index="i.url" :key="i.url" v-if="i.childnode">
			          <div :class="['kd-submenu__title',{'is-active':isActived[i.url]}]">
			            <i :class="['ops-icons-bg',i.icon,{'is-active':isActived[i.url]}]"></i>
			            <span class="siderbar--text">{{i.title}}</span>
			            <i :class="['ops-icons-bg','icon-arrow-right','siderbar--arrow']"></i>
			          </div>
			          <el-collapse-transition>  
			          <ul :class="['kd-menu','kd-menu--inline','menu-childnode-background-color']" v-show="isOpened[i.url]">
			            <li :class="['kd-menu-item',{'is-active':isActived[i2.url]},'siderbar-menuitem-child']" v-for="i2 in i.childnode" :index="i2.url" :key="i2.url" @click.stop="menuItemClick(i2.url,i.url)">
                    <div class="siderbar--selected-strip" v-if="isActived[i2.url]"></div>
                    <i :class="['ops-icons-bg',i2.icon,{'is-active':isActived[i2.url]}]"></i>
                    <span class="siderbar--text">{{i2.title}}</span>
			            </li>
			          </ul>
			          </el-collapse-transition>
			        </li>
			        <li :class="['kd-menu-item',{'is-active':isActived[i.url]}]" :index="i.url" :key="i.url" @click="menuItemClick(i.url)" v-else>
                <div class="siderbar--selected-strip" v-if="isActived[i.url]"></div>
                <i :class="['ops-icons-bg',i.icon,{'is-active':isActived[i.url]}]"></i>
                <span class="siderbar--text">{{i.title}}</span>
			        </li>
			      </ul>
			    </div>
          </transition>
          </el-col>
        </el-row>
        </el-scrollbar>
			</div>
</template>

<script>
	export default {
// 		props:{
// 			fisCollapse:{
// 				type:Boolean,
// 				default:false,
// 			},
// 		},
    inject: ['contentPageReload'],  // 注入重载的功能（注入依赖）
		computed: {
			isCollapse() {
				return this.$store.getters.getsiderbarCollapseStatu
			},
      activeRouteList(){
        return this.$store.getters.getactiveRouteList
      },
      timeNowFull(){
        let t = this.timeNow.split(" ")
        return t[0]+"-"+t[1]+" "+t[2]
      },
      timeNowSplit(){
        return this.timeNow.split(" ")
      },
		},
    watch:{
      activeRouteList:{
        deep:true,
        handler:function(newVal,oldVal){
          this.isActived={}
          for(let i in newVal){
            this.$set(this.isActived,newVal[i],true)
          }
        }
      },
      isCollapse(newVal){
        this.collapseStatusWidth(newVal)
      }
    },
		data() {
			return {
			  timeNow:'',
				siderbarInfo: '',
//         siderbarStyle:{
//           height:'',
//           },
        isOpened:{},
        isActived:{},
        collapseIsOpened:{},
        siderbarWidth: 0,
			};
		},
		methods: {
		  // 设置时间
      setNowTime(){
        let timestamp = new Date();
        this.timeNow =timestamp.format('Y m-d H:i')
      },

      // 定时器
      setTimer(time=60){
        const timer = setInterval(()=>{
          this.setNowTime()
        },time*1000)
        this.$once('hook:beforeDestroy',()=>{
          clearInterval(timer)
        })
      },

      // 侧边栏下拉收起函数
			sidebarHandleOpen(key, keyPath) {
				// console.log(key, keyPath);
			},
			sidebarHandleClose(key, keyPath) {
				// console.log(key, keyPath);
			},
      // 设置侧边栏高度
//       setSiderbarStyleHeight(){
//         this.siderbarStyle.height=window.innerHeight-52+'px';
//       },
      // 获取侧边栏数据
			getSidebar(){
				this.$api.sidebarapi.sidebarList()
				.then(res=>{
					this.siderbarInfo=res.data.data
				})
			},
       // 折叠栏点击事件
      submenuClick(index) {
        this.$set(this.isOpened,index,!this.isOpened[index])
      },
      // 路由栏点击事件
      menuItemClick(...index){
        this.$router.push({
          path:index[0],
        });
        // console.log(index,this.activeRouteList)
        // 如果路由没有变化，则重新加载内容区域
        if(index[0]===this.activeRouteList[0]){
          this.contentPageReload()
        }
        // 将当前url列表传递给vuex
        this.$nextTick(()=>this.$store.dispatch('activeRouteChange',index))
      },
      // 判断侧边栏收起状态下的二级三级菜单是否展开
      collapseIsOpenedChange(index,value){
        this.$set(this.collapseIsOpened,index,value)
        // console.log(this.collapseIsOpened[index])
      },
      
      // 侧边栏收起展开函数
      collapseStatuChange(){
        this.$store.dispatch('toggel',!this.$store.getters.getsiderbarCollapseStatu)
      },
      // 判断侧边栏收起与展开
      collapseStatusWidth(val){
        if (val){
          this.siderbarWidth=62
        }
        else{
          this.siderbarWidth=180
        }
      },
      // 页面载入初始化
      initPage(){
         this.isActived={}
         let curRoutePath=this.$route.path.split("\/").slice(1)
         let initPath=''
         for(let i in curRoutePath){
           // this.$set(this.isActived,index[i],true)
           initPath=initPath+"/"+curRoutePath[i]
           // console.log(initPath,this.activeRouteList)
           this.$set(this.isActived,initPath,true)
         }
      }
		},
		mounted(){
			this.getSidebar();
      // this.setSiderbarStyleHeight();
      this.initPage();
      this.collapseStatusWidth(this.$store.getters.getsiderbarCollapseStatu)

      this.setNowTime()
      this.setTimer(10)
      // window.addEventListener('resize',this.setSiderbarStyleHeight)
		}
	}
</script>

<style >
  @import '../assets/css/keda-siderbar.css';
  .kd-siderbar{
    list-style: none;
    position: relative;
    margin: 0;
    padding-left: 0;
    background-color: #292e30;
    height:calc(100vh - 52px);
    bottom: 0px;
    /* overflow: auto; */
    /* overflow-x: visible; */
    color: #9ca9b1;
    text-align:left;
  }
  .area-siderbar--time{
    position: absolute;
    bottom: 9px;
    width: 100%;
    text-align: center;
    color: #9ba3aa;
  }
  .tac{
    /* overflow: hidden; */
  }
 .siderbar-scrollbar{
    height: calc(100% - 25px);
  }
  .siderbar-scrollbar--collapse{
    height: calc(100% - 66px);
  }
 .kd-siderbar .el-scrollbar .el-scrollbar__wrap 
  {overflow-x: hidden;overflow-y: auto;}
  /* .siderbat-scrollbar .el-scrollbar__bar{
    overflow-x: hidden;
  } */

  .menu-childnode-background-color .siderbar-menuitem-child{
    padding-left: 31px;
  }
  .buttom-collapse{
    height: 48px;
    text-align:center;
    vertical-align:middle;
    box-sizing: border-box;
    padding-top: 18px;
  }
  .buttom-collapse:hover
  {cursor:pointer;}
  .menu-childnode-background-color{
   background-color:#232629;
  }
  .kd-gradation-blue{
    background: linear-gradient(to right,#2c83b4,#56a5d6);
    background: -ms-linear-gradient(to right,#2c83b4,#56a5d6);
    background: -webkit-linear-gradient(to right,#2c83b4,#56a5d6);
    background: -o-linear-gradient(to right,#2c83b4,#56a5d6);
    background: -moz-linear-gradient(to right,#2c83b4,#56a5d6);
  }
  .siderbar--icon{
    /*line-height: 42px;*/
  }
  .siderbar--text{
    margin-left: 7px;
    vertical-align: middle;
    display: inline-block;
  }
  .siderbar--selected-strip{
    position: absolute;
    height: 100%;
    width: 2px;
    background-color: #299dFF;
    z-index: 199;
    left: 0px;
  }
  .siderbar--arrow{
    position: absolute;
    top: 16px;
    right: 10px;
    -webkit-transition:-webkit-transform .3s;
    transition:-webkit-transform .3s;
    transition:transform .3s;
    transition:transform .3s,-webkit-transform .3s;
  }
  .kd-menu--collapse .kd-submenu.is-opened>.kd-submenu__title .siderbar--arrow
  {-webkit-transform:none;transform:none}
  .kd-submenu.is-opened>.kd-submenu__title .siderbar--arrow
  {-webkit-transform:rotateZ(90deg);transform:rotateZ(90deg)}
  .horizontal-collapse-transition .kd-submenu__title .siderbar--arrow
  {-webkit-transition:.2s;transition:.2s;opacity:0}

  .kd-submenu__title:hover .siderbar--arrow{
    background-position: -32px -197px;
  }

</style>
