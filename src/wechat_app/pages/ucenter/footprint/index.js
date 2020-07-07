var util = require('../../../utils/util.js');
var api = require('../../../config/api.js');

var app = getApp();

Page({
    data: {
        footprintList: [],
        allFootprintList: [],
        allPage: 1,
        allCount: 0,
        size: 8,
        hasPrint: 1,
        showNoMore: 1,
    },
    getFootprintList() {
        let that = this;
        let userInfo = wx.getStorageSync('userInfo');
        util.request(api.FootprintList, { 
            page: that.data.allPage, 
            size: that.data.size,
            userId: userInfo.id
        },'POST').then(function (res) {
            if (res.data.header.code === 0) {
                let count = res.data.body.data.count;
                let f1 = that.data.footprintList;
                let f2 = res.data.body.data.data;
                for (let i = 0; i < f2.length; i++) {
                    let last = f1.length - 1;
                    if (last >= 0 && f1[last][0].add_time == f2[i].add_time) {
                        f1[last].push(f2[i]);
                    }
                    else {
                        let tmp = [];
                        tmp.push(f2[i])
                        f1.push(tmp);
                    }
                }

                that.setData({
                    allCount: count,
                    allFootprintList: that.data.allFootprintList.concat(res.data.body.data.data),
                    allPage: res.data.body.data.currentPage,
                    footprintList: f1,
                });
                if (count == 0) {
                    that.setData({
                        hasPrint: 0,
                        showNoMore: 1
                    });
                }
            }
            // wx.hideLoading();
        });
    },
    onLoad: function (options) {
        this.getFootprintList();
    },
    deletePrint: function (e) {
        let that = this;
        let id = e.currentTarget.dataset.val;
        let userInfo = wx.getStorageSync('userInfo');
        util.request(api.FootprintDelete, { 
            footprintId: id,
            userId: userInfo.id 
        }, 'POST').then(function (res) {
            if (res.data.header.code === 0) {
                wx.showToast({
                    title: '取消成功',
                    icon: 'success',
                    mask: true
                });
                that.setData({
                    footprintList: [],
                    allFootprintList: [],
                    allPage: 1,
                    allCount: 0,
                    size: 8
                });
                that.getFootprintList();
            }
        });
    },
    toIndexPage: function (e) {
        wx.switchTab({
            url: '/pages/index/index'
        });
    },
    onReachBottom: function () {
        let that = this;
        if (that.data.allCount / that.data.size < that.data.allPage) {
            that.setData({
                showNoMore: 0
            });
            return false;
        }
        that.setData({
            allPage: that.data.allPage + 1
        });
        that.getFootprintList();
    }
})