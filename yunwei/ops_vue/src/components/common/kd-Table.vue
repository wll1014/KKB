<!-- 封装el-table 
* 支持表格内按钮 
* 设置表格中每一格的宽度
* 可写class姓名
* 可选类型 
* 可双击设置
* selection设置-->

<template>
	<el-table 
		:data='tableData'
		empty-text='暂无数据*-*'
		@row-dblclick="rowClick"
		@selection-change='handleSelectionChange'>
		<el-table-column 
			v-for='(item,index) in tableLabel'
			:key='index'
			:label='item.label'
			:prop='item.param'
			:fixed='item.fixed'
			:min-width='item.width'
			:type='item.type'
			show-overflow-tooltip
			:class-name="item.class"
			>
		</el-table-column>
		<el-table-column
			:fixed='tableOption.fixed'
			:label='tableOption.label'>
			<template slot-scope='scope'>
				<el-button 
					v-for='(item,index) in tableOption.options'
					:key='index'
					:type='item.type'
					size='mini'
					@click='handleButton(item.methods,scope.row)'>
					{{ item.label }}
				</el-button>
			</template>
		</el-table-column>
	</el-table>
</template>

<script>
	export default{
		// 通过props获取使用者传来的参数,type用于指定传递的数据类型,default指定默认值(通常不给)
		props:{
			tableData:{
				type:Array,
				default:() => {}
			},
			tableLabel:{
				type:Array,
				default:() => {}
			},
			tableOption:{
				type:Object,
				default:() => {}
			},
		},
		// 通过methods发射给使用者事件及参数,$emit为发射事件,第一个参数为事件名,第二个为传递参数
		methods:{
			handleButton(methods,row){
				this.$emit('handleButton',{'method':methods,'row':row})
			},
			// 点击某一行时触发的函数
      // 按下左键然后移动鼠标到其它列放开左键，会有报错 -- 优化：添加点击行参数，
			rowClick(Row, Event, Column) {
        if (!Column || Column.type === 'selection' || Column.columnKey === 'operation' || Column.type === 'expand') {
          return
        }
        const data = {
          row: Row,
          event: Event,
          column: Column
        };
        this.$emit('kdRowClick', data)
      },
			handleSelectionChange(val){
				this.$emit('kdHandleSelectionChange', val);
			},
		},
	}
</script>

<!-- 使用方法
* 1.通过引用import 此vue文件，注册示例
* 		components:{
				kdTable
			}
* 2.使用过程示例：
* 		<kdTable
* 			:table-data='tableData'
* 			:table-label="tablelist"
				:table-option="tableOption"
					@handleButton='handleButton'></kdTable>
						
			data(){
				tableData:[],
				tablelist:[
					{label:'序号',param:'id'},
					{label:'日期',param:'date'},
					{label:'名称',param:'name'}
				],
				tableOption:{
					label:'操作',
					options:[
						{label:'详情',type:'primary',method:'detail'},
						{label:'删除',type:'danger',methods:'delete'}
					]
				},
			}
			method:{
				handleButton(val){
					if(val.method == 'detail'){
						this.detail(val,row)
					}else{
						this.delete(val,row)
					}
				}
			}  -->
