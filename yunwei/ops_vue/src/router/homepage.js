// import homepage from '@/view/home/HomePage.vue'

export default [
	{
    path: 'homepage',
    name: 'homepage',
    // component: resolve=>(require(["@/view/home/HomePageAllScreen.vue"],resolve))
    component: resolve=>(require(["@/view/home/HomePage.vue"],resolve))
// 	children:[
// 		{
// 		path: 'he',
// 		component: he,
// 		}
// 	]
},]
