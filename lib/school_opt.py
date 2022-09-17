# -*- coding:utf-8 -*-
# @FileName  :school_opt.py
# @Time      :2022/9/16 9:24
# @Author    :JN

import requests

from lib.common import login_host, username, password, dls_host

headers = {
    'Accept': '*/*',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Cache-Control': 'max-age=0',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/98.0.4758.102 Safari/537.36 Edg/98.0.1108.62',
    'Connection': 'keep-alive',
    'X-Requested-With': 'XMLHttpRequest',
    'Sec-Fetch-Mode': 'cors'
}


class SchoolOpt:
    def __init__(self):
        self.session = requests.Session()
        # 登录
        self.session.post(f'{login_host}/User/login.html', data={
            'username': username, 'password': password, 'act': 'auto'
        }, headers=headers, verify=False)

    # 获取指定地区学校列表
    def get_school_list(self, zid, school_type=1):
        response = self.session.post(f'{dls_host}/School/schoolList.html', data={
            'name': '', 'pid': 17, 'cid': 323, 'zid': zid, 'type': school_type, 'bshow': 1
        }, headers=headers)
        response = response.json()
        school_list = response['info']
        school = {}
        for i in school_list:
            school[i['name']] = {
                'id': i['id'],
                'name': i['name'],
                'zone_id': zid
            }
        return school

    # 在指定地区添加学校
    def add_school(self, zid, school_name, school_type=1):
        response = self.session.post(f'{dls_host}/School/addSchool.html', data={
            'name': school_name, 'pid': 17, 'cid': 323, 'zid': zid, 'type': school_type
        }, headers=headers, verify=False)

        response = response.json()
        return response['info']['status']

    # 在指定学校添加教师
    def add_teacher(self, name, username_t, phone, zid, school_id, book_version_id=29, version_alias_id=572):
        response = self.session.post(f'{dls_host}/School/applyTeacher.html', data={
            'name': name,
            'username': username_t,
            'mobile': phone,
            'province_id': 17,
            'city_id': 323,
            'zone_id': zid,
            'school_id': school_id,
            'book_version_id': book_version_id,
            'version_alias_id': version_alias_id,
            'create_class': False
        }, headers=headers, verify=False)
        response = response.json()
        if response['info'] == '用户名已被占用了！':
            return False
        return response['info']['id']

    # 获取指定学校的教师列表
    def get_teacher_list(self, school_id):
        response = self.session.post(f'{dls_host}/School/detailSchoolInfos.html', data={
            'sid': school_id,
            'store_status': 1,
            'need_all': True,
            'need_group': 1
        }, headers=headers, verify=False)
        response = response.json()
        teacher_info = {}
        if not response['info']['teachers']:
            return teacher_info
        for teacher in response['info']['teachers'][0][0]['teachers']:
            teacher_info[teacher['name']] = teacher

        return teacher_info

    # 在指定教师下添加班级
    def add_class_ss(self, teacher_id, class_name, grade):
        response = self.session.post(f'{dls_host}/School/addClass.html', data={
            'teacher_id': teacher_id, 'name': class_name, 'comment': '', 'term': 2022, 'grade': grade
        }, headers=headers, verify=False)
        response = response.json()
        return response['status']

    # 查找班级
    def get_class_list(self, tid):
        response = self.session.post(f'{dls_host}/School/detailTeacherInfos.html', data={
            'tid': tid, 'subject_type': 1
        }, headers=headers, verify=False)
        response = response.json()
        class_list = {}
        for item in response['info']:
            class_list[item['name']] = item['class_id']
        return class_list

    # 指定班级里添加学生
    def add_student(self, username_s, name, c_id):
        response = self.session.post(f'{dls_host}/Business/addStudent.html', data={
            'username': username_s, 'name': name, 'cid': c_id
        }, headers=headers, verify=False)
        response = response.json()
        return response['info']

    def get_student_list(self, class_id):
        response = self.session.post(f'{dls_host}/Business/importList.html', data={
            'str': class_id, 'type': 1, 'class_type': 1
        }, headers=headers, verify=False)
        users = response.json()['info']['classes'][0]['users']
        username_s = {}
        if not users:
            return username_s
        else:
            for i in response.json()['info']['classes'][0]['users']['importUsers']:
                username_s[i['username']] = i['id']
            return username_s

    # 根据用户名查询教师id
    def search_teacher_info(self, username_t):
        response = self.session.post(f'{dls_host}/School/getTeacherForSearch.html', data={
            'search_type': 'username', 'search_key': username_t
        }, headers=headers, verify=False)
        response = response.json()
        return response['info']['teachers'][0]['id']


if __name__ == '__main__':
    print(SchoolOpt().get_student_list(95161))
