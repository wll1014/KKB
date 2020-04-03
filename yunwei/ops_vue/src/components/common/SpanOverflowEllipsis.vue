<template>
  <div class="span-overflow-ellipsis">
    <div class="span-overflow-ellipsis-content one-line">
      <span @mouseover.self="isHiden($event,content)"
            @mouseout="removeTootipLayer">{{content}}</span>
    </div>
  </div>
</template>

<script>
  export default {
    name: "SpanOverflowEllipsis",
    props: {
      content: null,
      placement: String,
      popperClass: String,
      offset: {
        type: Number,
        default: 2,
      }
    },
    data() {
      return {};
    },
    methods: {
      // 模块功能函数start
      // 判断是否长度超过div
      isHiden(e, text) {
        let spanWidth = e.currentTarget.offsetWidth
        let divWidth = e.currentTarget.parentNode.offsetWidth
        if (spanWidth + 5 > divWidth) {
          this.addTootipLayer(e, text)
        }
      },

      // 添加tootip
      addTootipLayer(e, text) {
        let windowLeft = document.documentElement.scrollLeft
        let windowTop = document.documentElement.scrollTop
        let windowHeight = document.documentElement.scrollHeight
        let eleLeft = e.currentTarget.getBoundingClientRect().x
        let eleTop = e.currentTarget.getBoundingClientRect().y
        let bottom = windowHeight - eleTop - windowTop
        let left = windowLeft + eleLeft
        let tipObj = document.createElement("div");

        let placementToPosition = {
          'top-start': `
            bottom: ${bottom + this.offset}px;
            left: ${left}px;
          `,
        };
        let placement = this.placement || 'top-start'
        let pStyle = placementToPosition[placement] || placementToPosition['top-start']

        // let position=`bottom:${top + this.offset}px;left:${left}px;`
        tipObj.setAttribute('id', 'tipObj');
        tipObj.setAttribute('class', 'span-overflow-ellipsis-tip')
        tipObj.setAttribute('style', pStyle)
        document.body.appendChild(tipObj);
        document.querySelector('#tipObj').innerHTML = text;

      },
      // 删除tootip
      removeTootipLayer() {
        let tipObj = document.querySelector('#tipObj');
        if (tipObj) {
          document.body.removeChild(tipObj);
        }
      },

      setTipPosition() {
        let placementToPosition = {
          'top-start': {
            bottom: this.$el.offsetHeight + this.offset + 'px',
            left: '0px',
          },
          'bottom-start': {
            top: this.$el.offsetHeight + this.offset + 'px',
            left: '0px',
          },
        };
        let placement = this.placement || 'top-start'
        let pStyle = placementToPosition[placement] || placementToPosition['top-start']
      },
    },
    mounted() {

    },
  }
</script>

<style>
  .span-overflow-ellipsis {
    position: relative;
    display: inline-block;
    width: 100%;
  }

  .span-overflow-ellipsis-content {
    display: inline-block;
    padding: 1px 0px;
  }

  .span-overflow-ellipsis-content.one-line {
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    width: 100%;
  }

  .span-overflow-ellipsis-tip {
    position: absolute;
    z-index: 99;
    word-wrap: break-word;
    word-break: normal;
    padding: 14px;
    border: 1px solid #383b3c;
    background-color: #141414;
  }
</style>
