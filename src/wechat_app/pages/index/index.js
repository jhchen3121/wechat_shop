const util = require('../../utils/util.js');
const api = require('../../config/api.js');
const user = require('../../services/user.js');
const { SessionCheck } = require('../../config/api.js');

//获取应用实例
const app = getApp()

Page({
    data: {
        floorGoods: [],
        openAttr: false,
        showChannel: 0,
        showBanner: 0,
        showBannerImg: 0,
        goodsCount: 0,
        banner: [],
        index_banner_img: 0,
        userInfo: {},
        imgurl: '',
        sysHeight: 0,
        loading: 0,
        autoplay:true,
        baseUrl: api.BaseUrl
    },
    onHide:function(){
        this.setData({
            autoplay:false
        })
    },
    goSearch: function () {
        wx.navigateTo({
            url: '/pages/search/search',
        })
    },
    goCategory: function (e) {
        let id = e.currentTarget.dataset.cateid;
        wx.setStorageSync('categoryId', id);
        wx.switchTab({
            url: '/pages/category/index',
        })
    },
    getCatalog: function () {
        let that = this;
        util.request(api.GoodsCount).then(function (res) {
            that.setData({
                goodsCount: res.data.body.goodsCount
            });
        });
    },
    handleTap: function (event) {
        //阻止冒泡 
    },
    onShareAppMessage: function () {
        let info = wx.getStorageSync('userInfo');
        return {
            title: '陈天宝金店',
            desc: '开源微信小程序商城',
            path: '/pages/index/index?id=' + info.id
        }
    },
    toDetailsTap: function () {
        wx.navigateTo({
            url: '/pages/goods-details/index',
        });
    },
    getIndexData: function () {
        let that = this;
        util.request(api.IndexUrl).then(function (res) {
            if (res.data.header.code === 0) {
                that.setData({
                    floorGoods: res.data.body.data.categoryList,
                    banner: res.data.body.data.banner,
                    channel: res.data.body.data.channel,
                    notice: res.data.body.data.notice,
                    loading: 1,
                });
            }
        });
    },
    onLoad: function (options) {
        let systemInfo = wx.getStorageSync('systemInfo');
        var scene = decodeURIComponent(options.scene);

    },
    onShow: function () {
        // 页面初始化过程中先进行一次sessioncheck，用于登陆
        //this.sessionCheck();
        var that = this;
        wx.request({
            url: api.SessionCheck,
            header: {
                'Content-Type': 'application/json',
                'x-session-token': wx.getStorageSync('token')
            },
          success (res) {
            if (res.statusCode == 200) {
                if (res.data.header.code == -4003) {
                    util.showErrorToast("会话失效，正在重新登陆");
                    //需要登录后才可以操作
                    let code = null;
                    let userInfo = null;
                    wx.login({
                        success (res) {
                            if (res.code) {
                                code = res.code
                                wx.getUserInfo({
                                    withCredentials: true,
                                    success: function(res) {
                                        userInfo = res;
                                        //登录远程服务器
                                        wx.request({
                                            url: api.AuthLoginByWeixin, 
                                            data: {
                                                code: code,
                                                userInfo: userInfo
                                            },
                                            method: 'POST',
                                            success (res) {
                                                if (res.data.header.code === 0) {
                                                    //存储用户信息
                                                    wx.setStorageSync('userInfo', res.data.body.data.userInfo);
                                                    wx.setStorageSync('token', res.data.body.data.token);

                                                    // 登陆成功后初始化首页
                                                    that.getCatalog();
                                                    that.getCartNum();
                                                    that.getChannelShowInfo();
                                                    that.getIndexData();
                                                    //var that = this;
                                                    let userInfo = wx.getStorageSync('userInfo');
                                                    if (userInfo != '') {
                                                        that.setData({
                                                            userInfo: userInfo,
                                                        });
                                                    };
                                                } else {
                                                    util.showErrorToast(res.data.header.msg);
                                                }
                                            },
                                            fail (res) {
                                                util.showErrorToast(res);
                                            }
                                        });
                                    },
                                    fail: function(err) {
                                        util.showErrorToast(err);
                                    }
                                })
                            } else {
                                util.showErrorToast('小程序微信服务器登陆失败')
                            }
                        }
                    });
                } else if(res.data.header.code === 0){
                    //session有效首页内容初始化
                    that.getCatalog();
                    that.getCartNum();
                    that.getChannelShowInfo();
                    that.getIndexData();
                    //var that = this;
                    let userInfo = wx.getStorageSync('userInfo');
                    if (userInfo != '') {
                        that.setData({
                            userInfo: userInfo,
                        });
                    };
                }else{
                    util.showErrorToast(res.data.header.msg);
                }
            }
          },
          fail (res) {}
        });

        let info = wx.getSystemInfoSync();
        let sysHeight = info.windowHeight - 100;
        this.setData({
            sysHeight: sysHeight,
            autoplay:true
        });
        wx.removeStorageSync('categoryId');
    },

    getCartNum: function () {
        let info = wx.getStorageSync('userInfo');
        util.request(api.CartGoodsCount, {userid:info.id}, 'POST').then(function (res) {
            if (res.data.header.code === 0) {
                let cartGoodsCount = '';
                console.log(res);
                if (res.data.body.cartTotal.goodsCount == 0) {
                    wx.removeTabBarBadge({
                        index: 2,
                    })
                } else {
                    cartGoodsCount = res.data.body.cartTotal.goodsCount + '';
                    wx.setTabBarBadge({
                        index: 2,
                        text: cartGoodsCount
                    })
                }
            }
        });
    },
    getChannelShowInfo: function (e) {
        let that = this;
        util.request(api.ShowSettings).then(function (res) {
            if (res.data.header.code === 0) {
                let show_channel = res.data.body.data.channel;
                let show_banner = res.data.body.data.banner;
                let show_notice = res.data.body.data.notice;
                let index_banner_img = res.data.body.data.index_banner_img;
                that.setData({
                    show_channel: show_channel,
                    show_banner: show_banner,
                    show_notice: show_notice,
                    index_banner_img: index_banner_img
                });
            }
        });
    },
    onPullDownRefresh: function () {
        wx.showNavigationBarLoading()
        this.getIndexData();
        this.getChannelShowInfo();
        wx.hideNavigationBarLoading() //完成停止加载
        wx.stopPullDownRefresh() //停止下拉刷新
    },
})