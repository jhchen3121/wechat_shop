var util = require('../../../utils/util.js');
var api = require('../../../config/api.js');
const app = getApp()

Page({
    data: {
        expressList: [],
        hasExpress: 1
    },
    onLoad: function (options) {
        let that =this;
        let orderId = options.id;
        that.getExpressList(orderId);
    },
    getExpressList(orderId) {
        let that = this;
        util.request(api.OrderExpressInfo, {orderId: orderId}, 'POST').then(function (res) {
            if (res.data.header.code === 0) {
                let expressList = res.data.body.data;
                let traces = JSON.parse(res.data.body.data.traces);
                expressList.traces = traces;
                that.setData({
                    expressList: expressList
                });
                if (traces.length == 0) {
                    that.setData({
                        hasExpress: 0
                    });
                }
            }
        });
    },
})
