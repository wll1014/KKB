var scaleObj = {//该方法仅适用于chrome内核浏览器， 重要：火狐、IE、edge浏览器不支持
  minWidth:-1,
  init:function(minWidth){
    this.minWidth = minWidth==undefined?this.minWidth:minWidth
  },
  getScreenResolution:function(){
    return {
      height:window.screen.height,
      width:window.screen.width
    }
  },
  getBrowserDpr:function(){
    return this.fixed(window.outerWidth / window.innerWidth);
  },
  getScreenDpr:function(){
    return this.fixed(this.getDpr()/this.getBrowserDpr());
  },
  getDpr:function(){
    return window.devicePixelRatio==undefined?this.getBrowserDpr():this.fixed(window.devicePixelRatio);//IE版本比较低（IE10及以下）的情况下，可能为undefined，先不做处理
  },
  sacleByWidth:function(minWidth){

    var scrollWidth = minWidth*0.03//这是竖向滚动条的宽度，目前暂定默认值，后续可精确计算
    //var screen = this.getScreenResolution()//获取屏幕分辨率
    var screen_width = screen.width;
    var zoom = this.fixed((screen_width)/(minWidth+scrollWidth))
    window.document.getElementsByTagName('body')[0].style.zoom = zoom>1?1:zoom

    console.log("结合dpr和您的屏幕分辩，您的屏幕适合的缩放比例为......",window.document.getElementsByTagName('body')[0].style.zoom)
  },
  autoScale:function(minWidth){//自动缩放
    var dpr = this.getScreenDpr();
    var screen_width = screen.width;
    if(dpr<=1||screen_width>minWidth){
      this.restore();
      return ;
    }

    var minWidth = minWidth==undefined?this.minWidth:minWidth
    this.sacleByWidth(minWidth);

  },
  restore:function(){
    window.document.getElementsByTagName('body')[0].style.zoom = 1
  },

  fixed:function(x){
    return Math.round(x*100)/100
  }

}
