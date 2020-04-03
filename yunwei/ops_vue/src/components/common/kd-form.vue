<!-- 封装el-form
* 1.支持常规设置宽度
* 2.设置规则
* 3.存在el-input、el-select、el-date-picker
* 4.可以写按钮直接搜索功能
* 5.支持可隐藏选项
* 			 -->

<template>
	<el-form
		:inline='true'
		:model='value'
		:label-width="formConfig.labelWidth"
		:rules='rules'
		size='mini'>
			
			<slot name="formItem" />
			<el-form-item
				v-for='(item,index) in formConfig.formItemList'
				:key='index'
				:label='item.label'
				:prop='item.prop'
			>
				<el-input
					v-if='item.type=="input"'
					v-model='value[item.prop]'
					:disabled='item.disabled'
					:type='item.type'
					:clearable='true'
					:placeholder="item.placeholder"></el-input>
				<el-select
					:clearable="true"
					v-else-if='item.type=="select"'
					v-model='value[item.prop]'
					:disabled="item.disabled"
					:placeholder="item.placeholder"
				>
					<el-option
						v-for='(optItem,index) in item.optList'
						:key='index'
						:label='optItem.label'
						:value='optItem.value'></el-option>
				</el-select>
				<el-date-picker
					:value-format="item.dateFormate"
					v-else-if='item.type=="datetimerange"'
					range-separator="=>"
					start-placeholder="开始时间"
					end-placeholder="结束时间"
					v-model='value[item.prop]'
					type='datetimerange'
					:disabled="item.disabled"
					:placeholder="item.label"></el-date-picker>
			</el-form-item>
			<span class='searchBtn'>
				<el-button
					v-for='(item, index) in formConfig.operate'
					:key='index'
					:type='item.type'
					:icon='item.icon'
					@click='item.handleClick'
					:style='item.style'>
					{{ item.name }}
				</el-button>
				<slot name='operate'></slot>
			</span>
	</el-form>
</template>

<script>
	export default {
		components: {},
		props: {
			formConfig: {
				type: Object,
				required: true
			},
			value: {
				type:Object,
				required: true
			},
			rules: {
				type: Object
			}
		},
		computed: {},
		methods: {
			setDefaultValue() {
				// const fromData = { ...this.value };
				// 设置默认值
				// this.formConfig.formItemList.forEach(({ key, value}) => {
				// 	if (formData[key] === undefined || formData[key] === null){
				// 		formData[key] = this.value;
				// 	}
				// });
				this.$emit("input", this.value);
			}
		},
		mounted() {
			this.setDefaultValue();
		}
	}
</script>

<!-- 用法示例
* 1. 引入组件 并注册
* components: {
	searchForm
},
* 
* 2.页面中的使用方法
* <search-form
* 	:formConfig='formConfig'
* 	:value='form'
* 	></search-form>
* 
* 3.data() {
			return{
				formConfig: {
					formItemList: [
						{
							type: "dateFormate",
							dateFormate: 'yyyy-MM-SS', //选择显示时间格式
							prop: 'time', //prop相当于el-form-item中的v-model
							label: '时间', 
							palceholder:'ok',
						},
						{
							type:'select',
							prop:'自定义',
							label:'自定义',
							optList: []
						}
					],
					operate: [
						{
							icon:'el-icon-search',
							type:'primary',
							name:'搜索',
							handleClick:this.search
						}
					]
				},
				form: {			
				},
			}
	},
	
	
	 
	methods: {
		search() {
		}
	}-->
