<template>
  <div>
    <div class="host-frame">
      <!--jd10000 机框-->
      <div class="jd10000" v-if="type ==='jd10000'">
        <div>
          <div class="vertical" v-for="i of 14">
            <div :class="['content',contentClassList[i-1]]"
                 @click.stop="onClick($event,i)"
                 @dblclick.stop="dblClick($event,i)"
                 @mouseenter="addTootipLayer($event,i)"
                 @mouseleave="removeTootipLayer">
              <p>{{data[i-1] ? data[i-1][lableKey] : ''}}</p>
            </div>
          </div>
        </div>
        <div class="shelves"></div>
        <div>
          <div class="horizontal" v-for="i of [15,16]">
            <div :class="['content',contentClassList[i-1]]"
                 @click.stop="onClick($event,i)"
                 @dblclick.stop="dblClick($event,i)"
                 @mouseenter="addTootipLayer($event,i)"
                 @mouseleave="removeTootipLayer">
              <p>{{data[i-1] ? data[i-1][lableKey] : ''}}</p>
            </div>
          </div>
        </div>
      </div>
      <!--jd10000 机框 end-->
      <!--jd6000 机框-->
      <div class="jd6000" v-if="type ==='jd6000'">
        <div>
          <div class="horizontal" v-for="i of 6">
            <div :class="['content',contentClassList[i-1]]"
                 @click.stop="onClick($event,i)"
                 @dblclick.stop="dblClick($event,i)"
                 @mouseenter="addTootipLayer($event,i)"
                 @mouseleave="removeTootipLayer">
              <p>{{data[i-1] ? data[i-1][lableKey] : ''}}</p>
            </div>
          </div>
        </div>
        <div class="shelves"></div>
        <div class="footer">
          <div class="horizontal" v-for="i of [7,8]">
            <div :class="['content',contentClassList[i-1]]"
                 @click.stop="onClick($event,i)"
                 @dblclick.stop="dblClick($event,i)"
                 @mouseenter="addTootipLayer($event,i)"
                 @mouseleave="removeTootipLayer">
              <p>{{data[i-1] ? data[i-1][lableKey] : ''}}</p>
            </div>
          </div>
        </div>
      </div>
      <!--jd6000 机框 end-->
      <!--jds6000 机框-->
      <div class="jds6000" v-if="type ==='jds6000'">
        <div class="left">
          <div class="horizontal" v-for="i of 2">
            <div :class="['content',contentClassList[i-1]]"
                 @click.stop="onClick($event,i)"
                 @dblclick.stop="dblClick($event,i)"
                 @mouseenter="addTootipLayer($event,i)"
                 @mouseleave="removeTootipLayer">
              <p>{{data[i-1] ? data[i-1][lableKey] : ''}}</p>
            </div>
          </div>
        </div>
        <div class="shelves"></div>
        <div class="right">
          <div class="horizontal" v-for="i of [3,4]">
            <div :class="['content',contentClassList[i-1]]"
                 @click.stop="onClick($event,i)"
                 @dblclick.stop="dblClick($event,i)"
                 @mouseenter="addTootipLayer($event,i)"
                 @mouseleave="removeTootipLayer">
              <p>{{data[i-1] ? data[i-1][lableKey] : ''}}</p>
            </div>
          </div>
        </div>
      </div>
      <!--jds6000 机框 end-->
    </div>
  </div>
</template>

<script>
  export default {
    name: "TheHsotFrame",
    props: {
      type: {
        type: String,
        default: 'jd10000'
      },
      lableKey: {
        type: String,
        default: 'name'
      },
      data: {
        type: Array,
        default: [],
      },
      contentClass: {  // return String ; support options:['error','normal']
        type: Function,
        default: function (val) {
          return null
        }
      },
      tipFormatter: null,
      tipZIndex: {
        type: Number,
        default: 0,
      },
      tipOffset: {
        type: Number,
        default: 5,
      }
    },
    watch: {
      data: {
        deep: true,
        handler: function (newVal, oldVal) {
          this.setContentClass()
        }
      },
    },
    data() {
      return {
        // jd10000:['1-1','2-2','3-3'] horizontal vertical
        frameCount: {  // 各类型机框总数量
          jd10000: 16,
          jd6000: 8,
          jds6000: 4,
        },
        contentClassList: [],

        activeTipNode: null,  // 用于tip异步加载
        tipTimeOut: null,
      }
    },
    methods: {
      // emit  start
      onClick(e, index) {
        let v = this.data[index - 1] || undefined
        this.$emit('onClick', e, v)
      },
      dblClick(e, index) {
        let v = this.data[index - 1] || undefined
        this.$emit('dblClick', e, v)
      },
      // emit  end

      // 设置content class
      async setContentClass() {
        for (let i = 0; i < this.frameCount[this.type]; i++) {
          let name = await this.contentClass(this.data[i])
          this.$set(this.contentClassList, i, name)
        }
      },
      // 添加tootip
      async addTootipLayer(e, index) {
        clearTimeout(this.tipTimeOut);
        let tipFlag = document.querySelector('#tipHostFrame');
        this.activeTipNode = e
        let callback = (ticket, bd) => {
          if (ticket === this.activeTipNode) {
            let tipObj = document.querySelector('#tipHostFrame');
            if (tipObj) tipObj.innerHTML = bd;
          }
        };
        let v = this.data[index - 1] || undefined
        let tipInnerHTML = this.tipFormatter ? this.tipFormatter(e, v, callback) : this.type

        let target = e.target || e.srcElement
        let eleHeight = target.offsetHeight
        let windowLeft = document.documentElement.scrollLeft
        let windowTop = document.documentElement.scrollTop
        let windowHeight = document.documentElement.scrollHeight
        let eleLeft = target.getBoundingClientRect().x
        let eleTop = target.getBoundingClientRect().y
        let top = windowTop + eleTop
        let bottom = windowHeight - eleTop - windowTop
        let left = windowLeft + eleLeft
        let tipObj = tipFlag ? document.querySelector('#tipHostFrame') : document.createElement("div");

        let placementToPosition = {
          'top-start': `
            top: ${top + eleHeight + this.tipOffset}px;
            left: ${left}px;
          `,
        };

        let placement = 'top-start'
        let pStyle = placementToPosition[placement] || placementToPosition['top-start']

        if (this.tipZIndex) pStyle += `z-index:${this.tipZIndex};` // 如果设置了z-index
        tipObj.setAttribute('id', 'tipHostFrame');
        tipObj.setAttribute('class', 'ops-tip-defalut')
        tipObj.setAttribute('style', pStyle)
        tipObj.onmouseenter = (tipE) => {
          this.tipMouseEnter(tipE)
        }
        tipObj.onmouseleave = (tipE) => {
          this.tipMouseLeave(tipE)
        }
        if (!tipFlag) document.body.appendChild(tipObj);
        document.querySelector('#tipHostFrame').innerHTML = tipInnerHTML;
      },
      // 删除tootip
      removeTootipLayer() {
        this.tipTimeOut = setTimeout(() => {
          let tipObj = document.querySelector('#tipHostFrame');
          if (tipObj) {
            document.body.removeChild(tipObj);
          }
        }, 300)
      },

      // 进入tip悬浮框
      tipMouseEnter(e) {
        e = e || window.event;
        clearTimeout(this.tipTimeOut);
      },
      // 离开tip悬浮框
      tipMouseLeave(e) {
        e = e || window.event;
        this.removeTootipLayer()
      },
    },
    mounted() {
      this.setContentClass()
    },
    beforeDestroy() {
      this.removeTootipLayer()
    },
  }
</script>

<style scoped>
  .host-frame {
    border: 1px solid #69808d;
    display: inline-block;
    box-sizing: border-box;
  }

  /*host-frame 只设置基础样式 具体宽高等由各类型自行决定*/
  .host-frame .vertical, .host-frame .horizontal {
    display: inline-block;
    padding: 2px;
    box-sizing: border-box;
    border: 1px solid #69808d;
    vertical-align: top;
  }

  .host-frame .shelves {
    border: none;
    background: #69808d;
  }

  .host-frame .vertical .content, .host-frame .horizontal .content {
    width: 100%;
    height: 100%;
    box-sizing: border-box;
    vertical-align: top;
    font-size: 12px;
    overflow: hidden;
    cursor: pointer;
    white-space: nowrap;
    text-overflow: ellipsis; /* for IE */
    -moz-text-overflow: ellipsis; /* for Firefox,mozilla */

  }

  .host-frame .content.normal {
    color: #fff;
    background: #25a5c5;
  }

  .host-frame .content.error {
    color: #fff;
    background: #e45959;
  }

  .host-frame .vertical .content {
    padding-top: 10px;
  }

  .host-frame .vertical .content p {
    transform: rotate(90deg);
    -ms-transform: rotate(90deg); /* Internet Explorer 9*/
    -moz-transform: rotate(90deg); /* Firefox */
    -webkit-transform: rotate(90deg); /* Safari 和 Chrome */
    -o-transform: rotate(90deg); /* Opera */
  }

  /*host-frame 只设置基础样式 具体宽高等由各类型自行决定 end*/

  .jd10000 .vertical {
    width: 27px;
    height: 200px;
  }

  .jd10000 .horizontal {
    width: 189px;
    height: 28px;
  }

  .jd10000 .shelves {
    width: 378px;
    height: 27px;
  }

  .jd6000 .horizontal {
    width: 378px;
    height: 28px;
    display: block;
  }

  .jd6000 .shelves {
    width: 378px;
    height: 27px;
  }

  .jd6000 .footer .horizontal {
    width: 189px;
    height: 27px;
    display: inline-block;
  }

  .jds6000 {
    font-size: 0px;
  }

  .jds6000 .horizontal {
    width: 179px;
    height: 28px;
    display: block;
  }

  .jds6000 .shelves {
    width: 30px;
    height: 56px;
    display: inline-block;
  }

  .jds6000 .left, .jds6000 .right {
    display: inline-block;
    box-sizing: border-box;
    vertical-align: top;
  }


</style>
