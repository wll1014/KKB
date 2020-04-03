<template>
  <div class="theme-dark" style="position: relative;">
    <div class="logo--area" @click="backMain">
      <span class="ops-icons-bg logo"></span>
      <span class="ops-icons-bg logo--separator" style="margin-left: 8px;"></span>
      <span class="logo--text" style="margin-left: 9px;">运维可视化系统</span>
      <!-- <el-button icon="iconfont icon-menu" circle style="margin-left: 60px;" @click="sidebartoogel"></el-button> -->
      <!-- <span class="iconfont icon-menu" style="margin-left: 60px;" @click="sidebartoogel"></span> -->
    </div>
    <div class="user--area">
      <span class="ops-icons-bg logo--userdefault" style="margin-right: 5px;"></span>
      <span class="logo--usertext">{{loginInfo.account}}</span>
      <span class="ops-icons-bg logo--msg" style="margin-right: 10px;" @click="clickMsg"></span>
      <!--<span class="ops-icons-bg logo&#45;&#45;set" style="margin-right: 10px;"></span>-->
      <el-dropdown trigger="click" @command="handleSet">
        <span class="ops-icons-bg logo--set" style="margin-right: 10px;"></span>
        <el-dropdown-menu class="theme-dark" slot="dropdown" style="width: 116px;margin-top: 8px;">
          <el-dropdown-item :command="item" :key="item"
                            v-for="item in setList">{{item}}
          </el-dropdown-item>
        </el-dropdown-menu>
      </el-dropdown>
      <span class="ops-icons-bg logo--logout" @click="logout"></span>
    </div>
    <div id="headerMsg" class="msg-list" v-if="showArea==='msg'">
      <div style="height: 32px;line-height: 28px;border-bottom: 1px solid #3d4046;">
        <span style="font-weight: 700;height: 32px;line-height: 28px;">通知消息</span>
        <button type="button" class="button-host-info" style="float: right;line-height: 20px;" @click="">
          <span style="text-decoration: underline;font-size: 12px">清空</span>
        </button>
      </div>
      <div class="content">{{msgContent}}</div>
    </div>

    <!-- yp__start   above -->
    <el-dialog
      title="关于"
      :visible.sync="aboutInfo"
      width="450px"
      :modal-append-to-body="false"
      top="10%"
      style='position: fixed;'
    >
      <div class="ops-icons-bg logo" style="margin-left: 20px;margin-top:45px"></div>
      <br>
      <div style="margin-top: 20px;">
        <span class="ops-icons-bg logo--separator" style="margin-left: 250px;"></span>
        <span style="vertical-align:top;font-weight:700">运维可视化系统</span>
      </div>
      <div class='theme-dark' style='margin-top:75px;padding-bottom: 40px;margin-left: 20px'>
        <div style="margin-top: 5px;">苏州科达科技股份有限公司 版权所有</div>
        <div style="margin-top: 5px;">Copyright © 1995-2019 KEDACOM. All rights reserved.</div>
        <div style="margin-top: 5px;">
          <span>version : {{version}}</span>
          <a style="margin-left: 20px;color:#299dff;text-decoration: underline;" href="https://www.kedacom.com">
            www.kedacom.com</a>
        </div>
      </div>
    </el-dialog>
    <!-- yp__end -->

  </div>
</template>

<script>
  export default {
    inject: ['contentPageReload'],  // 注入重载的功能（注入依赖）
    data() {
      return {
        loginInfo: {},
        showArea: null,
        msgContent: "暂无消息",
        setList: [
          '帮助信息',
          '关于'
        ],
        // yp__start
        aboutInfo: false,
        version: "6.0.0.4.0",
        // yp__end
      };
    },
    methods: {
      backMain() {
        let path = this.loginInfo.url
        document.location = path
        // this.$router.push({
        //   path:path,
        // });
        // // // 如果路由没有变化，则重新加载内容区域
        // if(path[0]===this.$store.getters.getactiveRouteList[0]){
        //   this.contentPageReload()
        // }
        // // 将当前url列表传递给vuex
        // this.$nextTick(()=>this.$store.dispatch('activeRouteChange',path))
      },
      clickMsg() {
        if (this.showArea === 'msg') {
          this.showArea = null
          document.removeEventListener("mouseup", this.listenerCloseDialog);
        } else {
          this.showArea = 'msg'
          document.addEventListener("mouseup", this.listenerCloseDialog);
        }
      },
      handleSet(val) {
        if (val === '帮助信息') {
          // console.log(val)
          // yp__start
          // 跳转到另一个写好的界面
          window.open('/ops/static/help/default.html', "newwindow")
          // yp__end

        } else if (val === '关于') {
          // console.log(val)
          // yp__start
          this.aboutInfo = true
          // yp__end
        }
      },

      logout() {
        this.$api.sidebarapi.logout()
          .then(res => {
            if (res.data.success) {
              document.location = res.data.data.url
            } else {
              this.$message("注销失败")
            }
          })
      },
      //其他功能函数封装 start
      // 点击空白地方关闭终端外设弹框
      listenerCloseDialog(e) {
        if (this.showArea === 'msg') {
          let dialogE = document.getElementById("headerMsg")
          if (!this.isDOMContains(dialogE, e.target)) {
            this.clickMsg()
          }
        }
      },
      // 判断一个元素是否包含一个指定节点
      isDOMContains(parentEle, ele) {
        //parentEle: 要判断节点的父级节点
        //ele:要判断的子节点
        //container : 二者的父级节点

        //如果parentEle h和ele传的值一样，那么两个节点相同
        if (parentEle == ele) {
          return true
        }
        if (!ele || !ele.nodeType || ele.nodeType != 1) {
          return false;
        }
        //如果浏览器支持contains
        if (parentEle.contains) {
          return parentEle.contains(ele)
        }
        //火狐支持
        if (parentEle.compareDocumentPosition) {
          return !!(parentEle.compareDocumentPosition(ele) & 16);
        }
      },
      //其他功能函数封装 end
    },
    mounted() {
      this.loginInfo = this.$store.getters.getLoginInfo ? this.$store.getters.getLoginInfo : {account: '游客'}
    },
  }
</script>

<style>
  .keda-main-header .logo--area {
    -webkit-transition: width 0.3s ease-in-out;
    -o-transition: width 0.3s ease-in-out;
    transition: width 0.3s ease-in-out;
    cursor: pointer;
    float: left;
    text-align: center;
    font-family: "微软雅黑";
    padding: 18px 20px;
    font-weight: bold;
    overflow: hidden;
    font-size: 0px;
    color: #fff;
  }

  .keda-main-header .user--area {
    -webkit-transition: width 0.3s ease-in-out;
    -o-transition: width 0.3s ease-in-out;
    transition: width 0.3s ease-in-out;
    cursor: pointer;
    /*float: right;*/
    text-align: right;
    font-family: "微软雅黑";
    padding: 18px 20px;
    overflow: hidden;
    font-size: 0px;
    color: #fff;
  }

  .keda-main-header .logo--area .logo--text {
    color: #fff;
    display: inline-block;
    font-size: 13px;
    font-weight: 700;
    height: 18px;
    vertical-align: top;
    line-height: 18px;
  }

  .keda-main-header .user--area .logo--usertext {
    color: #9ba3aa;
    display: inline-block;
    font-size: 12px;
    height: 24px;
    vertical-align: top;
    line-height: 24px;
    text-align: left;
    margin-right: 18px;
    text-overflow: ellipsis;
    white-space: nowrap;
    word-break: keep-all;
    overflow: hidden;
    max-width: 100px;
  }

  .msg-list {
    position: absolute;
    padding: 15px 15px 5px;
    width: 350px;
    height: 260px;
    overflow: hidden;
    top: 54px;
    right: 20px;
    z-index: 999;
    background: #141414;
  }

  .msg-list .content {
    max-height: 225px;
    text-align: center;
    padding: 20px 0px;
    font-size: 12px;
    color: #9ca9b1;
    overflow: auto;
  }
</style>
