# -*- coding:utf-8 -*-
# @FileName  :common.py
# @Time      :2022/9/16 12:37
# @Author    :JN

from concurrent.futures import ThreadPoolExecutor

env = 'beta'
if env == 'alpha':
    # 登录url
    login_host = 'https://jiangnan-www.b.waiyutong.org'
    # 代理商网址
    dls_host = 'http://jiangnan-dls.b.waiyutong.org/'
    # 代理商用户名
    username = 'TsWeb08006'
    # 代理商密码
    password = 'e10adc3949ba59abbe56e057f20f883e'

elif env == 'beta':
    # 登录url
    login_host = 'https://www-beta.waiyutong.org'
    # 代理商网址
    dls_host = 'http://dls-beta.waiyutong.org'
    # 代理商用户名
    username = '伊犁渠道专员'
    # 代理商密码
    password = '4cb4643ba064093bafcef6156a165ba2'

# 实例化线程池
threadPool = ThreadPoolExecutor(max_workers=5)

# 地区id 表
zid_dict = {
    '亭湖区': 2577,
    '亭湖': 2577,
    '盐都区': 2578,
    '盐都': 2578,
    '响水县': 2579,
    '响水': 2579,
    '滨海县': 2580,
    '滨海': 2580,
    '阜宁县': 2581,
    '阜宁': 2581,
    '射阳县': 2582,
    '射阳': 2582,
    '建湖县': 2583,
    '建湖': 2583,
    '东台市': 2584,
    '东台': 2584,
    '大丰区': 2585,
    '大丰': 2585,
    '市直属': 3031,
    '市直': 3031,
    '开发区': 3032,
    '盐南高新区': 3033
}

# 省份id 江苏省
pid = 17
# 城市id 盐城
city_id = 323
# 学校类型 1：小学 2：初中 3：高中
school_type = 3
# 地区教材id
book_version_id = 38
version_alias_id = 603

# 盐城地区班级体验套餐
course_id = 436
course_type = 8
course_city_id = 91941
start_time = '2022-09-30 00:00'
end_time = '2022-10-08 00:00'

# 班级学年
term = 2022
