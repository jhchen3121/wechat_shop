var util = require('../../../utils/util.js');
var api = require('../../../config/api.js');

const app = getApp()

Page({
    data: {
        goodsList: [],
    },
    onLoad: function(options) {
        this.getGoodsList(options.id);
    },
    getGoodsList: function(id) {
        let that = this;
        let userInfo = wx.getStorageSync('userInfo');
        util.request(api.OrderGoods, {
            orderId: id,
            userId: userInfo.id
        },'POST').then(function(res) {
            if (res.data.header.code === 0) {
                that.setData({
                    goodsList: res.data.body.data
                });
            }
        });
    }
})