<template>
  <div style="width: 100%;height: 100%;">
		<div style="text-align: center;padding-top: 150px;font-size: 18px;">
			<span >尚 无 合 成 相 关 信 息 </span>
		</div>
<!--   <div>
			 <div style="margin: 30px 0 0 0;height: 50px;" >
				<span style="color: #9ca9b1;float: right;margin-right: 4px;font-size: 14px;">异常</span>
				<i class="ops-icons-bg icon-legend-red" style="float: right;margin-right: 7px;margin-top: 8px"></i>
				<span style="color: #9ca9b1;float: right;margin-right:26px;font-size: 14px;">正常</span>
				<i class="ops-icons-bg icon-legend-grassGreen" style="float: right;margin-right: 7px;margin-top: 8px"></i>
			 </div>
			<canvas id="mycanvas" width="550" height="400"></canvas>
    </div> -->
    
  </div>
</template>

<script>
	export default {
		methods: {
			doDraw(){
				//  获取canvas
				var canvas = document.getElementById("mycanvas")
				//  由于弹窗，确保已获取到
				var a = setInterval(() =>{
						//  重复获取
						canvas = document.getElementById("mycanvas")
						if(!canvas){
							return false
						} else {
								clearInterval(a)
								//  可以理解为一个画笔，可画路径、矩形、文字、图像						
								var context = canvas.getContext('2d')	
								context.strokeStyle = "white"
								context.lineWidth = 1;
								// 图形
								//-画面无即可------1
								// context.strokeRect(0, 0, 550, 400)
								//两画面相等-------2
								// context.strokeRect(0, 100, 275, 200)
								// context.strokeRect(275, 100, 275, 200)
								//左上------------62
								// context.strokeRect(0, 0, 550, 400)
								// context.strokeRect(0, 0, 183, 133)
								//左下------------63
								// context.strokeRect(0, 0, 550, 400)
								// context.strokeRect(0, 267, 183, 133)
								//右上------------61
								// context.strokeRect(0, 0, 550, 400)
								// context.strokeRect(367, 0, 183, 133)
								//右下------------3
								// context.strokeRect(0, 0, 550, 400)
								// context.strokeRect(367, 267, 183, 133)
								//三画面 
								//一左二右--------23
								// context.strokeRect(0, 0, 550, 400)
								// context.strokeRect(0, 100, 275, 200)
								// context.strokeRect(275, 200, 275, 200)
								// context.strokeRect(275, 0, 275, 200)
								//一上二下--------4
								// context.strokeRect(0, 0, 550, 400)
								// context.strokeRect(140, 0, 275, 200)//上方块
								// context.strokeRect(275, 200, 275, 200)//下右
								// context.strokeRect(0, 200, 275, 200)//下左
								//四画面--------5
								// context.strokeRect(0, 0, 275, 200)//上左
								// context.strokeRect(275, 0, 275, 200)//上右
								// context.strokeRect(275, 200, 275, 200)//下右
								// context.strokeRect(0, 200, 275, 200)//下左
								//五画面-------35
								// context.strokeRect(0, 0, 550, 400)
								// context.strokeRect(69, 0, 417, 300)//上
								// context.strokeRect(0, 300, 137.5, 100)//下左
								// context.strokeRect(137.5, 300, 137.5, 100)//下左中
								// context.strokeRect(275, 300, 137.5, 100)//下右中
								// context.strokeRect(412.5, 300, 137.5, 100)//下右
								//六画面-------6
								// context.strokeRect(0, 0, 366, 266)//上左0
								// context.strokeRect(366, 0, 184, 134)//上右1
								// context.strokeRect(366, 133, 184, 134)//上中2
								// context.strokeRect(0, 266, 183, 133)//下左5
								// context.strokeRect(183, 266, 183, 133)//下中4
								// context.strokeRect(366, 266, 184, 134)//下右3
								
								
								// 七画面-------13
								// context.strokeRect(0, 0, 275, 200)//上左0
								// context.strokeRect(275, 0, 275, 200)//上右1
								// context.strokeRect(0, 200, 275, 200)//下左2
								// context.strokeRect(275, 200, 137.5, 100)//下右(左上)3
								// context.strokeRect(412.5, 200, 137.5, 100)//下右(右上)4
								// context.strokeRect(275, 300, 137.5, 100)//下右(左下)5
								// context.strokeRect(412.5, 300, 137.5, 100)//下右(右下)6
								
								//八画面-------7
								// context.strokeRect(0, 0, 412.5, 300)//上左0
								// context.strokeRect(412.5, 0, 137.5, 100)//上右-1-  1
								// context.strokeRect(412.5, 100, 137.5, 100)//上右-2-  2
								// context.strokeRect(412.5, 200, 137.5, 100)//上右-3-  3
								// context.strokeRect(412.5, 300, 137.5, 100)//下右4
								// context.strokeRect(275, 300, 137.5, 100)//下右中5
								// context.strokeRect(137.5, 300, 137.5, 100)//下左中6
								// context.strokeRect(0, 300, 137.5, 100)//下左   7
								
								// 九画面
								// context.strokeRect(0, 0, 183, 133)//上左0
								// context.strokeRect(183, 0, 183, 133)//上中1
								// context.strokeRect(366, 0, 184, 134)//上右2
								// context.strokeRect(0, 133, 184, 133)//中左中3
								// context.strokeRect(183, 133, 184, 133)//中中中4
								// context.strokeRect(366, 133, 184, 134)//中右中5
								// context.strokeRect(0, 266, 183, 133)//下左6
								// context.strokeRect(183, 266, 183, 133)//下中7
								// context.strokeRect(366, 266, 184, 134)//下右8
								
								//十画面
								// context.strokeRect(0, 0, 137.5, 100)//上左2
								// context.strokeRect(137.5, 0, 137.5, 100)//上左中3
								// context.strokeRect(275, 0, 137.5, 100)//上右中4
								// context.strokeRect(412.5, 0, 137.5, 100)//上右5
								// context.strokeRect(0, 100, 275, 200)//中左0
								// context.strokeRect(275, 100, 275, 200)//中右1
								// context.strokeRect(0, 300, 137.5, 100)//下左6
								// context.strokeRect(137.5, 300, 137.5, 100)//下左中7
								// context.strokeRect(275, 300, 137.5, 100)//下右中8
								// context.strokeRect(412.5, 300, 137.5, 100)//下右9
								
								// 十一画面
								// context.strokeRect(120, 0, 300, 190)//上左0
								// context.strokeRect(0, 200, 100, 90)//下中左1
								// context.strokeRect(110, 200, 100, 90)//下中左偏中2
								// context.strokeRect(220, 200, 100, 90)//下中中3
								// context.strokeRect(330, 200, 100, 90)//下中右偏中4
								// context.strokeRect(440, 200, 100, 90)//下右5
								// context.strokeRect(0, 300, 100, 90)//下左6
								// context.strokeRect(110, 300, 100, 90)//下左偏中7
								// context.strokeRect(220, 300, 100, 90)//下左中8
								// context.strokeRect(330, 300, 100, 90)//下右偏中9
								// context.strokeRect(440, 300, 100, 90)//下右10
								
								// 十二画面
								// context.strokeRect(0, 0, 265, 190)//上左0
								// context.strokeRect(275, 0, 265, 190)//上右1
								// context.strokeRect(0, 200, 265, 190)//下左2
								// 
								// 
								// context.strokeRect(275, 200,  85, 60)//下左3    //下右九块
								// context.strokeRect(365, 200,  85, 60)//下左中4
								// context.strokeRect(455, 200,  85, 60)//下右中5
								// context.strokeRect(275, 265,  85, 60)//下右6
								// context.strokeRect(365, 265,  85, 60)//下右7
								// context.strokeRect(455, 265,  85, 60)//下左8
								// context.strokeRect(275, 330,  85, 60)//下左中9
								// context.strokeRect(365, 330,  85, 60)//下右中10
								// context.strokeRect(455, 330,  85, 60)//下   11
								
								// 十三画面
								// context.strokeRect(0, 0, 127.5, 90)//上左1
								// context.strokeRect(137.5, 0, 127.5, 90)//上左中2
								// context.strokeRect(275, 0, 127.5, 90)//上右中3
								// context.strokeRect(412.5, 0, 127.5, 90)//上右4
								// context.strokeRect(137.5, 100, 265, 190)//0
								// context.strokeRect(0, 100, 127.5, 90)//上左5
								// context.strokeRect(412.5, 100,127.5, 90)//上右6
								// context.strokeRect(0, 200, 127.5, 90)//下左7
								// context.strokeRect(412.5, 200,127.5, 90)//下右8
								// context.strokeRect(0, 300, 127.5, 90)//下左9
								// context.strokeRect(137.5, 300, 127.5, 90)//下左中10
								// context.strokeRect(275, 300, 127.5, 90)//下右中11
								// context.strokeRect(412.5, 300, 127.5, 90)//下右12
								
								// 十四画面
								// context.strokeRect(0, 0, 210, 190)//上左0
								// context.strokeRect(220, 0, 210, 190)//上左中1
								// context.strokeRect(440, 0, 100, 90)//上右2
								// context.strokeRect(440, 100, 100, 90)//上右3
								// context.strokeRect(0, 200, 100, 90)//下左4
								// context.strokeRect(110, 200,100, 90)//下右5
								// context.strokeRect(220, 200, 100, 90)//下左6
								// context.strokeRect(330, 200, 100, 90)//下左中7
								// context.strokeRect(440, 200, 100, 90)//下右中8
								// context.strokeRect(0, 300, 100, 90)//下左9
								// context.strokeRect(110, 300,100, 90)//下右10
								// context.strokeRect(220, 300, 100, 90)//下左11
								// context.strokeRect(330, 300, 100, 90)//下左中12
								// context.strokeRect(440, 300, 100, 90)//下右中13
								
								// 十五画面
								// context.strokeRect(0, 0, 176, 190)//上左0
								// context.strokeRect(186, 0, 176, 190)//上左中1
								// context.strokeRect(372, 0, 176, 190)//上左中2
								// 
								// context.strokeRect(0, 200, 83, 90)//上左3
								// context.strokeRect(93, 200, 83, 90)//上左中4
								// context.strokeRect(186, 200, 83, 90)//上左中5
								// context.strokeRect(279, 200, 83, 90)//上左6
								// context.strokeRect(372, 200, 83, 90)//上左中7
								// context.strokeRect(465, 200, 83, 90)//上左中8
								// context.strokeRect(0, 300, 83, 90)//上左9
								// context.strokeRect(93, 300, 83, 90)//上左中10
								// context.strokeRect(186, 300, 83, 90)//上左中11
								// context.strokeRect(279, 300, 83, 90)//上左12
								// context.strokeRect(372, 300, 83, 90)//上左中13
								// context.strokeRect(465, 300, 83, 90)//上左中14
								
								// 十六画面
								// context.strokeRect(0, 0, 127.5, 90)//上左0
								// context.strokeRect(137.5, 0, 127.5, 90)//上左中1
								// context.strokeRect(275, 0, 127.5, 90)//上右中2
								// context.strokeRect(412.5, 0, 127.5, 90)//上右3
								// context.strokeRect(0, 100, 127.5, 90)//上左4
								// context.strokeRect(137.5, 100, 127.5, 90)//上左中5
								// context.strokeRect(275, 100, 127.5, 90)//上右中6
								// context.strokeRect(412.5, 100,127.5, 90)//上右7
								// context.strokeRect(0, 200, 127.5, 90)//下左8
								// context.strokeRect(137.5, 200, 127.5, 90)//上左中9
								// context.strokeRect(275, 200, 127.5, 90)//上右中10
								// context.strokeRect(412.5, 200,127.5, 90)//下右11
								// context.strokeRect(0, 300, 127.5, 90)//下左12
								// context.strokeRect(137.5, 300, 127.5, 90)//下左中13
								// context.strokeRect(275, 300, 127.5, 90)//下右中14
								// context.strokeRect(412.5, 300, 127.5, 90)//下右15
								
								// 十七
								// context.strokeRect(0, 0, 320, 230)//0
								// context.strokeRect(330, 0, 100, 70)//1
								// context.strokeRect(440, 0, 100, 70)//2
								// context.strokeRect(330, 80, 100, 70)//3
								// context.strokeRect(440, 80, 100, 70)//4
								// context.strokeRect(330, 160, 100, 70)//5
								// context.strokeRect(440, 160, 100, 70)//6
								// context.strokeRect(0, 240, 100, 70)//7
								// context.strokeRect(110, 240,100, 70)/8
								// context.strokeRect(220, 240, 100, 70)//9
								// context.strokeRect(330, 240, 100, 70)//10
								// context.strokeRect(440, 240, 100, 70)//下11
								// context.strokeRect(0, 320, 100, 70)//12
								// context.strokeRect(110, 320,100, 70)//下13
								// context.strokeRect(220, 320, 100, 70)//14
								// context.strokeRect(330, 320, 100, 70)//15
								// context.strokeRect(440, 320, 100, 70)//16
								
								// 十八
								// context.strokeRect(0, 0, 83, 56)//6
								// context.strokeRect(93, 0, 83, 56)//7
								// context.strokeRect(186, 0, 83, 56)//8
								// context.strokeRect(279,0, 83, 56)//9
								// context.strokeRect(372, 0, 83, 56)//10
								// context.strokeRect(465, 0, 83, 56)//11
								// context.strokeRect(0, 66, 176, 122)//0
								// context.strokeRect(186, 66, 176, 122)//1
								// context.strokeRect(372, 66, 176, 122)//2
								// context.strokeRect(0, 198, 176, 122)//3
								// context.strokeRect(186, 198, 176, 122)//4
								// context.strokeRect(372, 198, 176, 122)//5
								// context.strokeRect(0, 330, 83, 56)//12
								// context.strokeRect(93, 330, 83, 56)//13
								// context.strokeRect(186, 330, 83, 56)//14
								// context.strokeRect(279, 330, 83, 56)//15
								// context.strokeRect(372, 330, 83, 56)//16
								// context.strokeRect(465, 330, 83, 56)//17
								
								// 十九
								// context.strokeRect(0, 0, 210, 150)//0
								// context.strokeRect(220, 0, 210, 150)//1
								// context.strokeRect(440, 0, 100, 70)//2
								// context.strokeRect(440, 80, 100, 70)//3
								// context.strokeRect(0, 160, 100, 70)//4
								// context.strokeRect(110, 160, 100, 70)//5
								// context.strokeRect(220, 160, 100, 70)//6
								// context.strokeRect(330, 160, 100, 70)//7
								// context.strokeRect(440, 160, 100, 70)//8
								// context.strokeRect(0, 240, 100, 70)//9
								// context.strokeRect(110, 240, 100, 70)//10
								// context.strokeRect(220, 240, 100, 70)//11
								// context.strokeRect(330, 240, 100, 70)//12
								// context.strokeRect(440, 240, 100, 70)//13
								// context.strokeRect(0, 320, 100, 70)//14
								// context.strokeRect(110, 320,100, 70)//下15
								// context.strokeRect(220, 320, 100, 70)//16
								// context.strokeRect(330, 320, 100, 70)//17
								// context.strokeRect(440, 320, 100, 70)//18
								
								// 二十
								// context.strokeRect(0, 0, 269, 150)//上左0
								// context.strokeRect(279, 0, 269, 150)//上左1
								// context.strokeRect(0, 160, 83, 70)//2
								// context.strokeRect(93, 160, 83, 70)//3
								// context.strokeRect(186, 160, 83, 70)//4
								// context.strokeRect(279, 160, 83, 70)//5
								// context.strokeRect(372, 160, 83, 70)//6
								// context.strokeRect(465, 160, 83, 70)//7
								// context.strokeRect(0, 240, 83, 70)//8
								// context.strokeRect(93, 240, 83, 70)//9
								// context.strokeRect(186, 240, 83, 70)//10
								// context.strokeRect(279, 240, 83, 70)//11
								// context.strokeRect(372, 240, 83, 70)//12
								// context.strokeRect(465, 240, 83, 70)//13
								// context.strokeRect(0, 320, 83, 70)//14
								// context.strokeRect(93, 320, 83, 70)//上15
								// context.strokeRect(186, 320, 83, 70)//16
								// context.strokeRect(279, 320, 83, 70)//17
								// context.strokeRect(372, 320, 83, 70)//18
								// context.strokeRect(465, 320, 83, 70)//19
								
								// 二十一
								// context.strokeRect(93, 66, 362, 254)//0
								// context.strokeRect(0, 0, 83, 56)//1
								// context.strokeRect(93, 0, 83, 56)//2
								// context.strokeRect(186, 0, 83, 56)//3
								// context.strokeRect(279,0, 83, 56)//4
								// context.strokeRect(372, 0, 83, 56)//5
								// context.strokeRect(465, 0, 83, 56)//6
								// context.strokeRect(0, 66, 83, 56)//7
								// context.strokeRect(465, 66, 83, 56)//8
								// context.strokeRect(0, 132, 83, 56)//9
								// context.strokeRect(465, 132, 83, 56)//10
								// context.strokeRect(0, 198, 83, 56)//11
								// context.strokeRect(465, 198, 83, 56)//12
								// context.strokeRect(0, 264, 83, 56)//13
								// context.strokeRect(465, 264, 83, 56)//14
								// context.strokeRect(0, 330, 83, 56)//15
								// context.strokeRect(93, 330, 83, 56)//16
								// context.strokeRect(186, 330, 83, 56)//17
								// context.strokeRect(279, 330, 83, 56)//18
								// context.strokeRect(372, 330, 83, 56)//19
								// context.strokeRect(465, 330, 83, 56)//20
								
								// 二十二
								// context.strokeRect(0, 0, 210, 150)//0
								// context.strokeRect(220, 0, 100, 70)//1
								// context.strokeRect(330, 0, 100, 70)//2
								// context.strokeRect(440, 0, 100, 70)//3
								// context.strokeRect(220, 80, 100, 70)//4
								// context.strokeRect(330, 80, 100, 70)//5
								// context.strokeRect(440, 80, 100, 70)//6
								// context.strokeRect(0, 160, 100, 70)//7
								// context.strokeRect(110, 160, 100, 70)//8
								// context.strokeRect(220, 160, 100, 70)//9
								// context.strokeRect(330, 160, 100, 70)//10
								// context.strokeRect(440, 160, 100, 70)//11
								// context.strokeRect(0, 240, 100, 70)//12
								// context.strokeRect(110, 240, 100, 70)//13
								// context.strokeRect(220, 240, 100, 70)//14
								// context.strokeRect(330, 240, 100, 70)//15
								// context.strokeRect(440, 240, 100, 70)//16
								// context.strokeRect(0, 320, 100, 70)//17
								// context.strokeRect(110, 320,100, 70)//18
								// context.strokeRect(220, 320, 100, 70)//19
								// context.strokeRect(330, 320, 100, 70)//20
								// context.strokeRect(440, 320, 100, 70)//21
								
								// 二十四
								// context.strokeRect(93, 66, 176, 122)//0
								// context.strokeRect(279, 66, 176, 122)//1
								// context.strokeRect(93, 198, 176, 122)//2
								// context.strokeRect(279, 198, 176, 122)//3
								// context.strokeRect(0, 0, 83, 56)//4
								// context.strokeRect(93, 0, 83, 56)//5
								// context.strokeRect(186, 0, 83, 56)//6
								// context.strokeRect(279,0, 83, 56)//7
								// context.strokeRect(372, 0, 83, 56)//8
								// context.strokeRect(465, 0, 83, 56)//9
								// context.strokeRect(0, 66, 83, 56)//10
								// context.strokeRect(465, 66, 83, 56)//11
								// context.strokeRect(0, 132, 83, 56)//12
								// context.strokeRect(465, 132, 83, 56)//13
								// context.strokeRect(0, 198, 83, 56)//14
								// context.strokeRect(465, 198, 83, 56)//15
								// context.strokeRect(0, 264, 83, 56)//16
								// context.strokeRect(465, 264, 83, 56)//17
								// context.strokeRect(0, 330, 83, 56)//18
								// context.strokeRect(93, 330, 83, 56)//19
								// context.strokeRect(186, 330, 83, 56)//20
								// context.strokeRect(279, 330, 83, 56)//21
								// context.strokeRect(372, 330, 83, 56)//22
								// context.strokeRect(465, 330, 83, 56)//23
								
								// 二十五
								context.strokeRect(0, 0, 100, 70)//0
								context.strokeRect(110, 0, 100, 70)//1
								context.strokeRect(220, 0, 100, 70)//2
								context.strokeRect(330, 0, 100, 70)//3
								context.strokeRect(440, 0, 100, 70)//4
								context.strokeRect(0, 80, 100, 70)//5
								context.strokeRect(110, 80, 100, 70)//6
								context.strokeRect(220, 80, 100, 70)//7
								context.strokeRect(330, 80, 100, 70)//8
								context.strokeRect(440, 80, 100, 70)//9
								context.strokeRect(0, 160, 100, 70)//10
								context.strokeRect(110, 160, 100, 70)//11
								context.strokeRect(220, 160, 100, 70)//12
								context.strokeRect(330, 160, 100, 70)//12
								context.strokeRect(440, 160, 100, 70)//14
								context.strokeRect(0, 240, 100, 70)//15
								context.strokeRect(110, 240, 100, 70)//16
								context.strokeRect(220, 240, 100, 70)//17
								context.strokeRect(330, 240, 100, 70)//18
								context.strokeRect(440, 240, 100, 70)//19
								context.strokeRect(0, 320, 100, 70)//20
								context.strokeRect(110, 320,100, 70)//21
								context.strokeRect(220, 320, 100, 70)//22
								context.strokeRect(330, 320, 100, 70)//23
								context.strokeRect(440, 320, 100, 70)//24
								
								// 内容
								context.font = "26px Arial bolder"
								context.fillStyle = 'red'
								// context.fillText('yyang',50,50)
								// context.fillText('yyang',300,250)
						}
				},1)
			},
		},
		mounted(){
			this.doDraw()
		},
	}
</script>

<style>
	#mycanvas{
		/* border: 1px solid white; */
	}
</style>
