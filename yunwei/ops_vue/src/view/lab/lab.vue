<template>
  <div class="lab">
    <div>
      <div>
        <div class="button-icon-bg" @click="routeLink(urlWebConsole)">
          <i class="ops-icons-bg icon-web-console"></i>
        </div>
        <div class="title">
          WEB控制台
        </div>
      </div>
    </div>
    <div>
      <div>
        <div class="button-icon-bg" @click="routeLink(urlKibanaMtCall)">
          <i class="ops-icons-bg icon-kibana"></i>
        </div>
        <div class="title">
          Kibana
        </div>
      </div>
    </div>
  </div>
</template>

<script>
  export default {
    name: "lab",
    data() {
      return {
        urlWebConsole: 'http://10.67.18.11:8888/',
        urlKibanaMtCall: 'https://10.67.18.11/wk/goto/38cc203439c1cea0b6d815445a3d9314',
      }
    },
    methods: {
      routeLink(url) {
        window.open(url, "_blank");
      },
    },
  }
</script>

<style>
  .lab {
    display: flex;
    min-height: 600px;
    align-items: center;
    justify-content: center;
  }

  .lab > div {
    flex: 1;
    font-size: 0px;
    text-align: center;
  }

  .lab .button-icon-bg {
    display: inline-block;
    width: 120px;
    height: 120px;
    border-radius: 50%;
    font-size: 20px;
    background: #283232;
  }

  .lab .button-icon-bg:hover {
    cursor: pointer;
    background: #3f494a;
  }

  .lab .button-icon-bg i {
    margin-top: 20px;
  }

  .lab .title {
    font-size: 16px;
    text-align: center;
    margin-top: 10px;
  }

  .lab .tip {
    width: 200px;
    border: none;
    font-size: 12px;
    color: #e45959;
  }
</style>
