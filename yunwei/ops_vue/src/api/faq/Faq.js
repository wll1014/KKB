import base from '@/api/base'; // 导入接口域名列表
import axios from '@/api/http'; // 导入http中创建的axios实例
const faq = {
	//faq端口
	faqGet(params){
		return axios.get(`${base.master}/faq/`,{params});
	},
	faqGetOne(params){
		return axios.get(`${base.master}/faq/${params.record_id}/`);
	},
	faqPost(params){
		return axios.post(`${base.master}/faq/`,params);
	},
	faqPut(param){
		// console.log(param)
		var params = {
			"question":param.question,
			"answer":param.answer,
			"classification":param.classification
		}
		return axios.put(`${base.master}/faq/${param.record_id}/`,params);
	},
	faqDelete(param){
		return axios.delete(`${base.master}/faq/`,{data:param});
	},
	//faq问题类型请求
	faqTypesGet(params){
		return axios.get(`${base.master}/faq/classes/`,{params});
	},	
	//增加分类
	faqTypesPost(params){
		return axios.post(`${base.master}/faq/classes/`,params);
	},
	//删除分类
	faqTypesDelete(param){
		return axios.delete(`${base.master}/faq/classes/`,{data:param});
	},
	//修改分类
	faqTypesPut(params){
		return axios.put(`${base.master}/faq/classes/${params.id}/`,params);
	}
};

export default faq;
