# coding: utf-8

from sqlalchemy import CHAR, Column, DECIMAL, Float, String, Text, text
from sqlalchemy.dialects.mysql import DECIMAL, INTEGER, MEDIUMINT, SMALLINT, TINYINT, VARCHAR
from sqlalchemy import create_engine
from core_backend.database.base import DomainBase

import settings

class WechatshopAd(DomainBase):
    __tablename__ = 'wechatshop_ad'

    id = Column(SMALLINT(5), primary_key=True, autoincrement=True)
    link_type = Column(TINYINT(1), nullable=False, server_default=text("'0'"))
    link = Column(String(255), server_default=text("''"))
    goods_id = Column(INTEGER(11), nullable=False, server_default=text("'0'"))
    image_url = Column(Text, nullable=False)
    end_time = Column(INTEGER(11), nullable=False, server_default=text("'0'"))
    enabled = Column(TINYINT(1), nullable=False, index=True, server_default=text("'0'"))
    sort_order = Column(TINYINT(2), nullable=False, server_default=text("'0'"))
    is_delete = Column(TINYINT(1), nullable=False, server_default=text("'0'"))


class WechatshopAddres(DomainBase):
    __tablename__ = 'wechatshop_address'

    id = Column(MEDIUMINT(8), primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False, server_default=text("''"))
    user_id = Column(MEDIUMINT(8), nullable=False, index=True, server_default=text("'0'"))
    country_id = Column(SMALLINT(5), nullable=False, server_default=text("'0'"))
    province_id = Column(SMALLINT(5), nullable=False, server_default=text("'0'"))
    city_id = Column(SMALLINT(5), nullable=False, server_default=text("'0'"))
    district_id = Column(SMALLINT(5), nullable=False, server_default=text("'0'"))
    address = Column(String(120), nullable=False, server_default=text("''"))
    mobile = Column(String(60), nullable=False, server_default=text("''"))
    is_default = Column(TINYINT(1), nullable=False, server_default=text("'0'"))
    is_delete = Column(TINYINT(1), server_default=text("'0'"))


class WechatshopAdmin(DomainBase):
    __tablename__ = 'wechatshop_admin'

    id = Column(INTEGER(11), primary_key=True, autoincrement=True)
    username = Column(String(25), nullable=False, server_default=text("''"))
    password = Column(String(255), nullable=False, server_default=text("''"))
    password_salt = Column(String(255), nullable=False, server_default=text("''"))
    last_login_ip = Column(String(60), nullable=False, server_default=text("''"))
    last_login_time = Column(INTEGER(11), nullable=False, server_default=text("'0'"))
    is_delete = Column(TINYINT(1), server_default=text("'0'"))


class WechatshopCart(DomainBase):
    __tablename__ = 'wechatshop_cart'

    id = Column(MEDIUMINT(8), primary_key=True, autoincrement=True)
    user_id = Column(MEDIUMINT(8), nullable=False, server_default=text("'0'"))
    goods_id = Column(MEDIUMINT(8), nullable=False, server_default=text("'0'"))
    goods_sn = Column(String(60), nullable=False, server_default=text("''"))
    product_id = Column(MEDIUMINT(8), nullable=False, server_default=text("'0'"))
    goods_name = Column(String(120), nullable=False, server_default=text("''"))
    goods_aka = Column(String(120), nullable=False, server_default=text("''"))
    goods_weight = Column(Float(4, True), nullable=False, server_default=text("'0.00'"))
    add_price = Column(DECIMAL(10, 2), server_default=text("'0.00'"))
    retail_price = Column(DECIMAL(10, 2), nullable=False, server_default=text("'0.00'"))
    number = Column(SMALLINT(5), nullable=False, server_default=text("'0'"))
    goods_specifition_name_value = Column(Text, nullable=False)
    goods_specifition_ids = Column(String(60), nullable=False, server_default=text("''"))
    checked = Column(TINYINT(1), nullable=False, server_default=text("'1'"))
    list_pic_url = Column(String(255), nullable=False, server_default=text("''"))
    freight_template_id = Column(MEDIUMINT(4), nullable=False)
    is_on_sale = Column(TINYINT(1), nullable=False, server_default=text("'1'"))
    add_time = Column(INTEGER(11), nullable=False, server_default=text("'0'"))
    is_fast = Column(TINYINT(1), nullable=False, server_default=text("'0'"))
    is_delete = Column(TINYINT(2), nullable=False, server_default=text("'0'"))


class WechatshopCategory(DomainBase):
    __tablename__ = 'wechatshop_category'

    id = Column(INTEGER(11), primary_key=True, autoincrement=True)
    name = Column(String(90), nullable=False, server_default=text("''"))
    keywords = Column(String(255), nullable=False, server_default=text("''"))
    front_desc = Column(String(255), nullable=False, server_default=text("''"))
    parent_id = Column(INTEGER(11), nullable=False, index=True, server_default=text("'0'"))
    sort_order = Column(TINYINT(1), nullable=False, server_default=text("'50'"))
    show_index = Column(TINYINT(1), nullable=False, server_default=text("'0'"))
    is_show = Column(TINYINT(1), nullable=False, server_default=text("'1'"))
    icon_url = Column(String(255), nullable=False)
    img_url = Column(String(255), nullable=False)
    level = Column(String(255), nullable=False)
    front_name = Column(String(255), nullable=False)
    p_height = Column(INTEGER(3), nullable=False, server_default=text("'0'"))
    is_category = Column(TINYINT(1), nullable=False, server_default=text("'0'"))
    is_channel = Column(TINYINT(1), nullable=False, server_default=text("'0'"))


class WechatshopExceptArea(DomainBase):
    __tablename__ = 'wechatshop_except_area'

    id = Column(MEDIUMINT(8), primary_key=True, autoincrement=True)
    content = Column(String(255), nullable=False)
    area = Column(String(3000), nullable=False, server_default=text("'0'"))
    is_delete = Column(TINYINT(1), nullable=False, server_default=text("'0'"))


class WechatshopExceptAreaDetail(DomainBase):
    __tablename__ = 'wechatshop_except_area_detail'

    id = Column(MEDIUMINT(8), primary_key=True, autoincrement=True)
    except_area_id = Column(INTEGER(11), nullable=False, server_default=text("'0'"))
    area = Column(INTEGER(5), nullable=False, server_default=text("'0'"))
    is_delete = Column(TINYINT(1), nullable=False, server_default=text("'0'"))


class WechatshopFootprint(DomainBase):
    __tablename__ = 'wechatshop_footprint'

    id = Column(INTEGER(11), primary_key=True, autoincrement=True)
    user_id = Column(INTEGER(11), nullable=False, server_default=text("'0'"))
    goods_id = Column(INTEGER(11), nullable=False, server_default=text("'0'"))
    add_time = Column(INTEGER(11), nullable=False, server_default=text("'0'"))


class WechatshopFormid(DomainBase):
    __tablename__ = 'wechatshop_formid'

    id = Column(INTEGER(11), primary_key=True, autoincrement=True)
    user_id = Column(INTEGER(11), nullable=False)
    order_id = Column(INTEGER(11), nullable=False)
    form_id = Column(String(255), nullable=False)
    add_time = Column(INTEGER(11), nullable=False, server_default=text("'0'"))
    use_times = Column(TINYINT(1), nullable=False, server_default=text("'0'"))


class WechatshopFreightTemplate(DomainBase):
    __tablename__ = 'wechatshop_freight_template'

    id = Column(MEDIUMINT(8), primary_key=True, autoincrement=True)
    name = Column(VARCHAR(120), nullable=False, server_default=text("'0'"))
    package_price = Column(DECIMAL(5, 2), nullable=False, server_default=text("'0.00'"))
    freight_type = Column(TINYINT(1), nullable=False, server_default=text("'0'"))
    is_delete = Column(TINYINT(1), nullable=False, server_default=text("'0'"))


class WechatshopFreightTemplateDetail(DomainBase):
    __tablename__ = 'wechatshop_freight_template_detail'

    id = Column(MEDIUMINT(8), primary_key=True, autoincrement=True)
    template_id = Column(INTEGER(11), nullable=False, server_default=text("'0'"))
    group_id = Column(INTEGER(11), nullable=False, server_default=text("'0'"))
    area = Column(INTEGER(5), nullable=False, server_default=text("'0'"))
    is_delete = Column(TINYINT(1), nullable=False, server_default=text("'0'"))


class WechatshopFreightTemplateGroup(DomainBase):
    __tablename__ = 'wechatshop_freight_template_group'

    id = Column(MEDIUMINT(8), primary_key=True, autoincrement=True)
    template_id = Column(INTEGER(11), nullable=False, server_default=text("'0'"))
    is_default = Column(TINYINT(1), nullable=False, server_default=text("'0'"))
    area = Column(String(3000), nullable=False, server_default=text("'0'"))
    start = Column(INTEGER(3), nullable=False, server_default=text("'1'"))
    start_fee = Column(DECIMAL(10, 2), nullable=False, server_default=text("'0.00'"))
    add = Column(INTEGER(3), nullable=False, server_default=text("'1'"))
    add_fee = Column(DECIMAL(10, 2), nullable=False, server_default=text("'0.00'"))
    free_by_number = Column(TINYINT(2), nullable=False, server_default=text("'0'"))
    free_by_money = Column(DECIMAL(10, 2), nullable=False, server_default=text("'0.00'"))
    is_delete = Column(TINYINT(1), nullable=False, server_default=text("'0'"))


class WechatshopGood(DomainBase):
    __tablename__ = 'wechatshop_goods'

    id = Column(INTEGER(11), primary_key=True, autoincrement=True)
    category_id = Column(INTEGER(11), nullable=False, index=True, server_default=text("'0'"))
    is_on_sale = Column(TINYINT(1), nullable=False, server_default=text("'1'"))
    name = Column(String(120), nullable=False, server_default=text("''"))
    goods_number = Column(MEDIUMINT(8), nullable=False, index=True, server_default=text("'0'"))
    sell_volume = Column(INTEGER(11), nullable=False, server_default=text("'0'"))
    keywords = Column(String(255), nullable=False, server_default=text("''"))
    retail_price = Column(String(100), nullable=False, server_default=text("'0.00'"))
    min_retail_price = Column(DECIMAL(10, 2), server_default=text("'0.00'"))
    cost_price = Column(String(100), nullable=False, server_default=text("'0.00'"))
    min_cost_price = Column(DECIMAL(10, 2), server_default=text("'0.00'"))
    goods_brief = Column(String(255), nullable=False, server_default=text("''"))
    goods_desc = Column(Text)
    sort_order = Column(SMALLINT(4), nullable=False, index=True, server_default=text("'100'"))
    is_index = Column(TINYINT(1), server_default=text("'0'"))
    is_new = Column(TINYINT(1), server_default=text("'0'"))
    goods_unit = Column(String(45), nullable=False)
    https_pic_url = Column(String(255), nullable=False, server_default=text("'0'"))
    list_pic_url = Column(String(255), nullable=False)
    freight_template_id = Column(INTEGER(5), server_default=text("'0'"))
    freight_type = Column(TINYINT(1), server_default=text("'0'"))
    is_delete = Column(TINYINT(1), nullable=False, server_default=text("'0'"))


class WechatshopGoodsGallery(DomainBase):
    __tablename__ = 'wechatshop_goods_gallery'

    id = Column(INTEGER(11), primary_key=True, autoincrement=True)
    goods_id = Column(INTEGER(11), nullable=False, index=True, server_default=text("'0'"))
    img_url = Column(String(255), nullable=False, server_default=text("''"))
    img_desc = Column(String(255), nullable=False, server_default=text("''"))
    sort_order = Column(INTEGER(11), nullable=False, server_default=text("'5'"))
    is_delete = Column(TINYINT(1), server_default=text("'0'"))


class WechatshopGoodsSpecification(DomainBase):
    __tablename__ = 'wechatshop_goods_specification'

    id = Column(INTEGER(11), primary_key=True, autoincrement=True)
    goods_id = Column(INTEGER(11), nullable=False, index=True, server_default=text("'0'"))
    specification_id = Column(INTEGER(11), nullable=False, index=True, server_default=text("'0'"))
    value = Column(String(50), nullable=False, server_default=text("''"))
    pic_url = Column(String(255), nullable=False, server_default=text("''"))
    is_delete = Column(TINYINT(1), server_default=text("'0'"))


class WechatshopKeyword(DomainBase):
    __tablename__ = 'wechatshop_keywords'

    keyword = Column(String(90), primary_key=True, nullable=False, server_default=text("''"))
    is_hot = Column(TINYINT(1), nullable=False, server_default=text("'0'"))
    is_default = Column(TINYINT(1), nullable=False, server_default=text("'0'"))
    is_show = Column(TINYINT(1), nullable=False, server_default=text("'1'"))
    sort_order = Column(INTEGER(11), nullable=False, server_default=text("'100'"))
    scheme__url = Column('scheme _url', String(255), nullable=False, server_default=text("''"))
    id = Column(INTEGER(11), primary_key=True, autoincrement=True, nullable=False)
    type = Column(INTEGER(11), nullable=False, server_default=text("'0'"))


class WechatshopNotice(DomainBase):
    __tablename__ = 'wechatshop_notice'

    id = Column(INTEGER(11), primary_key=True, autoincrement=True)
    content = Column(String(255), nullable=False, server_default=text("'0'"))
    end_time = Column(INTEGER(11), nullable=False, server_default=text("'0'"))
    is_delete = Column(TINYINT(1), nullable=False, server_default=text("'0'"))


class WechatshopOrder(DomainBase):
    __tablename__ = 'wechatshop_order'

    id = Column(MEDIUMINT(8), primary_key=True, autoincrement=True)
    order_sn = Column(String(20), nullable=False, unique=True, server_default=text("''"))
    user_id = Column(MEDIUMINT(8), nullable=False, index=True, server_default=text("'0'"))
    order_status = Column(SMALLINT(4), nullable=False, index=True, server_default=text("'0'"))
    offline_pay = Column(TINYINT(1), server_default=text("'0'"))
    shipping_status = Column(TINYINT(1), nullable=False, index=True, server_default=text("'0'"))
    print_status = Column(TINYINT(1), nullable=False, server_default=text("'0'"))
    pay_status = Column(TINYINT(1), nullable=False, index=True, server_default=text("'0'"))
    consignee = Column(String(60), nullable=False, server_default=text("''"))
    country = Column(SMALLINT(5), nullable=False, server_default=text("'0'"))
    province = Column(SMALLINT(5), nullable=False, server_default=text("'0'"))
    city = Column(SMALLINT(5), nullable=False, server_default=text("'0'"))
    district = Column(SMALLINT(5), nullable=False, server_default=text("'0'"))
    address = Column(String(255), nullable=False, server_default=text("''"))
    print_info = Column(String(255), nullable=False, server_default=text("''"))
    mobile = Column(String(60), nullable=False, server_default=text("''"))
    postscript = Column(String(255), nullable=False, server_default=text("''"))
    admin_memo = Column(VARCHAR(255))
    shipping_fee = Column(DECIMAL(10, 2), nullable=False, server_default=text("'0.00'"))
    pay_name = Column(String(120), nullable=False, server_default=text("''"))
    pay_id = Column(VARCHAR(255), nullable=False, index=True, server_default=text("'0'"))
    change_price = Column(DECIMAL(10, 2), nullable=False, server_default=text("'0.00'"))
    actual_price = Column(DECIMAL(10, 2), nullable=False, server_default=text("'0.00'"))
    order_price = Column(DECIMAL(10, 2), nullable=False, server_default=text("'0.00'"))
    goods_price = Column(DECIMAL(10, 2), nullable=False, server_default=text("'0.00'"))
    add_time = Column(INTEGER(11), nullable=False, server_default=text("'0'"))
    pay_time = Column(INTEGER(11), nullable=False, server_default=text("'0'"))
    shipping_time = Column(INTEGER(11), nullable=False, server_default=text("'0'"))
    confirm_time = Column(INTEGER(11), nullable=False, server_default=text("'0'"))
    dealdone_time = Column(INTEGER(11), nullable=False, server_default=text("'0'"))
    freight_price = Column(INTEGER(10), nullable=False, server_default=text("'0'"))
    express_value = Column(DECIMAL(10, 2), nullable=False, server_default=text("'480.00'"))
    remark = Column(String(255), nullable=False, server_default=text("'???????????????'"))
    order_type = Column(TINYINT(2), nullable=False, server_default=text("'0'"))
    is_delete = Column(TINYINT(1), nullable=False, server_default=text("'0'"))


class WechatshopOrderExpres(DomainBase):
    __tablename__ = 'wechatshop_order_express'

    id = Column(MEDIUMINT(8), primary_key=True, autoincrement=True)
    order_id = Column(MEDIUMINT(8), nullable=False, index=True, server_default=text("'0'"))
    shipper_id = Column(MEDIUMINT(8), nullable=False, server_default=text("'0'"))
    shipper_name = Column(String(120), nullable=False, server_default=text("''"))
    shipper_code = Column(String(60), nullable=False, server_default=text("''"))
    logistic_code = Column(String(40), nullable=False, server_default=text("''"))
    traces = Column(String(2000), nullable=False, server_default=text("''"))
    is_finish = Column(TINYINT(1), nullable=False, server_default=text("'0'"))
    request_count = Column(INTEGER(11), server_default=text("'0'"))
    request_time = Column(INTEGER(11), server_default=text("'0'"))
    add_time = Column(INTEGER(11), nullable=False, server_default=text("'0'"))
    update_time = Column(INTEGER(11), nullable=False, server_default=text("'0'"))
    express_type = Column(TINYINT(1), nullable=False, server_default=text("'0'"))
    region_code = Column(String(10), nullable=False, server_default=text("'0'"))


class WechatshopOrderGood(DomainBase):
    __tablename__ = 'wechatshop_order_goods'

    id = Column(MEDIUMINT(8), primary_key=True, autoincrement=True)
    order_id = Column(MEDIUMINT(8), nullable=False, index=True, server_default=text("'0'"))
    goods_id = Column(MEDIUMINT(8), nullable=False, index=True, server_default=text("'0'"))
    goods_name = Column(String(120), nullable=False, server_default=text("''"))
    goods_aka = Column(String(120), nullable=False)
    product_id = Column(MEDIUMINT(8), nullable=False, server_default=text("'0'"))
    number = Column(SMALLINT(5), nullable=False, server_default=text("'1'"))
    retail_price = Column(DECIMAL(10, 2), nullable=False, server_default=text("'0.00'"))
    goods_specifition_name_value = Column(Text, nullable=False)
    goods_specifition_ids = Column(String(255), nullable=False, server_default=text("''"))
    list_pic_url = Column(String(255), nullable=False, server_default=text("''"))
    user_id = Column(MEDIUMINT(8), nullable=False, server_default=text("'0'"))
    is_delete = Column(TINYINT(1), nullable=False, server_default=text("'0'"))


class WechatshopProduct(DomainBase):
    __tablename__ = 'wechatshop_product'

    id = Column(MEDIUMINT(8), primary_key=True, autoincrement=True)
    goods_id = Column(MEDIUMINT(8), nullable=False, server_default=text("'0'"))
    goods_specification_ids = Column(String(50), nullable=False, server_default=text("''"))
    goods_sn = Column(String(60), nullable=False, server_default=text("''"))
    goods_number = Column(MEDIUMINT(8), nullable=False, server_default=text("'0'"))
    retail_price = Column(DECIMAL(10, 2), nullable=False, server_default=text("'0.00'"))
    cost = Column(DECIMAL(10, 2), nullable=False, server_default=text("'0.00'"))
    goods_weight = Column(Float(6, True), nullable=False, server_default=text("'0.00'"))
    has_change = Column(TINYINT(1), nullable=False, server_default=text("'0'"))
    goods_name = Column(String(120), nullable=False)
    is_on_sale = Column(TINYINT(1), nullable=False, server_default=text("'1'"))
    is_delete = Column(TINYINT(1), nullable=False, server_default=text("'0'"))


class WechatshopRegion(DomainBase):
    __tablename__ = 'wechatshop_region'

    id = Column(SMALLINT(5), primary_key=True, autoincrement=True)
    parent_id = Column(SMALLINT(5), nullable=False, index=True, server_default=text("'0'"))
    name = Column(String(120), nullable=False, server_default=text("''"))
    type = Column(TINYINT(1), nullable=False, index=True, server_default=text("'2'"))
    agency_id = Column(SMALLINT(5), nullable=False, index=True, server_default=text("'0'"))
    area = Column(SMALLINT(5), nullable=False, server_default=text("'0'"))
    area_code = Column(VARCHAR(10), nullable=False, server_default=text("'0'"))
    far_area = Column(INTEGER(2), nullable=False, server_default=text("'0'"))


class WechatshopSearchHistory(DomainBase):
    __tablename__ = 'wechatshop_search_history'

    id = Column(INTEGER(10), primary_key=True, autoincrement=True)
    keyword = Column(CHAR(50), nullable=False)
    _from = Column('from', String(45), nullable=False, server_default=text("''"))
    add_time = Column(INTEGER(11), nullable=False, server_default=text("'0'"))
    user_id = Column(String(45))


class WechatshopSetting(DomainBase):
    __tablename__ = 'wechatshop_settings'

    id = Column(MEDIUMINT(8), primary_key=True, autoincrement=True)
    autoDelivery = Column(TINYINT(1), nullable=False, server_default=text("'0'"))
    Name = Column(String(100), nullable=False)
    Tel = Column(String(20), nullable=False)
    ProvinceName = Column(String(20), nullable=False)
    CityName = Column(String(20), nullable=False)
    ExpAreaName = Column(String(20), nullable=False)
    Address = Column(String(20), nullable=False)
    discovery_img_height = Column(INTEGER(4), nullable=False, server_default=text("'0'"))
    discovery_img = Column(String(255), nullable=False, server_default=text("''"))
    goods_id = Column(INTEGER(11), nullable=False, server_default=text("'0'"))
    city_id = Column(INTEGER(5), nullable=False, server_default=text("'0'"))
    province_id = Column(INTEGER(5), nullable=False, server_default=text("'0'"))
    district_id = Column(INTEGER(5), nullable=False, server_default=text("'0'"))
    countdown = Column(INTEGER(11), nullable=False, server_default=text("'0'"))
    reset = Column(TINYINT(1), nullable=False, server_default=text("'0'"))


class WechatshopShipper(DomainBase):
    __tablename__ = 'wechatshop_shipper'

    id = Column(INTEGER(11), primary_key=True, autoincrement=True, unique=True)
    name = Column(String(20), nullable=False, server_default=text("''"))
    code = Column(String(10), nullable=False, server_default=text("''"))
    sort_order = Column(INTEGER(11), nullable=False, server_default=text("'10'"))
    MonthCode = Column(String(100))
    CustomerName = Column(String(100))
    enabled = Column(TINYINT(1), nullable=False, server_default=text("'0'"))


class WechatshopShowSetting(DomainBase):
    __tablename__ = 'wechatshop_show_settings'

    id = Column(MEDIUMINT(8), primary_key=True, autoincrement=True)
    banner = Column(TINYINT(1), nullable=False, server_default=text("'0'"))
    channel = Column(TINYINT(1), nullable=False, server_default=text("'0'"))
    index_banner_img = Column(TINYINT(1), nullable=False, server_default=text("'0'"))
    notice = Column(TINYINT(1), nullable=False, server_default=text("'0'"))


class WechatshopSpecification(DomainBase):
    __tablename__ = 'wechatshop_specification'

    id = Column(INTEGER(11), primary_key=True, autoincrement=True)
    name = Column(String(60), nullable=False, server_default=text("''"))
    sort_order = Column(TINYINT(3), nullable=False, server_default=text("'0'"))
    memo = Column(VARCHAR(255), nullable=False, server_default=text("'0'"))


class WechatshopUser(DomainBase):
    __tablename__ = 'wechatshop_user'

    id = Column(MEDIUMINT(8), primary_key=True, autoincrement=True)
    nickname = Column(String(1024), nullable=False)
    name = Column(String(60), nullable=False, server_default=text("''"))
    username = Column(String(60), nullable=False, server_default=text("''"))
    password = Column(String(32), nullable=False, server_default=text("''"))
    gender = Column(TINYINT(1), nullable=False, server_default=text("'0'"))
    birthday = Column(INTEGER(11), nullable=False, server_default=text("'0'"))
    register_time = Column(INTEGER(11), nullable=False, server_default=text("'0'"))
    last_login_time = Column(INTEGER(11), nullable=False, server_default=text("'0'"))
    last_login_ip = Column(String(15), nullable=False, server_default=text("''"))
    mobile = Column(String(20), nullable=False)
    register_ip = Column(String(45), nullable=False, server_default=text("''"))
    avatar = Column(String(255), nullable=False, server_default=text("''"))
    weixin_openid = Column(String(50), nullable=False, server_default=text("''"))
    name_mobile = Column(TINYINT(1), nullable=False, server_default=text("'0'"))
    country = Column(String(255), server_default=text("'0'"))
    province = Column(String(100), server_default=text("'0'"))
    city = Column(String(100), server_default=text("'0'"))


engine = create_engine(settings.DB_URL)
DomainBase.metadata.create_all(engine)
