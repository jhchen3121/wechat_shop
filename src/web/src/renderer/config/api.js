// const rootUrl = 'http://www.hiolabs.com:8360/admin/';
// const rootUrl = 'http://127.0.0.1:8360/admin/';
const rootUrl = '/service/';
// 之所以设计baseurl因为富文本框添加图片后图片src都进行包装且字符串化，小程序端无法展示
//const baseUrl = 'https://www.jhchen3121.com'
const baseUrl = 'http://81.68.144.209:8878'

const api = {
    rootUrl : rootUrl,
    baseUrl: baseUrl,
    // express: {
    //     // 快递物流信息查询使用的是快递鸟接口，申请地址：http://www.kdniao.com/
    //     appid: '123', // 对应快递鸟用户后台 用户ID
    //     appkey: '123123', // 对应快递鸟用户后台 API key
    //     request_url: 'http://api.kdniao.cc/Ebusiness/EbusinessOrderHandle.aspx'
    // },
	// 4.19更新，物流查询不需要以上配置，只需要在server的config配置阿里云物流接口就可以
    qiniu: 'http://up.qiniu.com',
    // 请根据自己创建的七牛的区域进行设置：
    // https://developer.qiniu.com/kodo/manual/1671/region-endpoint
};


// import api from './config/api'
// Axios.defaults.baseURL = api.rootUrl;

export default api
