# -*- coding:utf-8 -*-
# @FileName  :school_opt.py
# @Time      :2022/9/16 9:24
# @Author    :JN

import requests

from lib.common import login_host, username, password, dls_host, pid, city_id, school_type, book_version_id, \
    version_alias_id, term, course_id, course_type, course_city_id, start_time, end_time

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
        self.session.headers = headers
        # 登录
        self.session.post(f'{login_host}/User/login.html', data={
            'username': username, 'password': password, 'act': 'auto'
        }, verify=False)

    # 获取指定地区学校列表
    def get_school_list(self, zid):
        response = self.session.post(f'{dls_host}/School/schoolList.html', data={
            'name': '', 'pid': pid, 'cid': city_id, 'zid': zid, 'type': school_type, 'bshow': 1
        })
        response = response.json()
        school_list = response['info']
        school = {}
        for i in school_list:
            school[i['name']] = i['id']
        return school

    # 在指定地区添加学校
    def add_school(self, zid, school_name):
        response = self.session.post(f'{dls_host}/School/addSchool.html', data={
            'name': school_name, 'pid': pid, 'cid': city_id, 'zid': zid, 'type': school_type
        })

        response = response.json()
        return response['info']['status']

    # 在指定学校添加教师
    def add_teacher(self, name, username_t, phone, zid, school_id):
        response = self.session.post(f'{dls_host}/School/applyTeacher.html', data={
            'name': name,
            'username': username_t,
            'mobile': phone,
            'province_id': pid,
            'city_id': city_id,
            'zone_id': zid,
            'school_id': school_id,
            'book_version_id': book_version_id,
            'version_alias_id': version_alias_id,
            'create_class': False
        })
        response = response.json()
        if response['info'] == '用户名已被占用了！':
            return False
        return response['info']['id']

    # 获取指定学校的教师列表
    def get_teacher_list(self, school_id, zid):
        response = self.session.post(f'{dls_host}/school/teacherList.html', data={
            'schoolId': school_id,
            'provinceId': pid,
            'cityId': city_id,
            'zoneId': zid,
            'subject_type': 1
        })
        response = response.json()
        teacher_info = {}
        for teacher in response['info']['teachers']:
            teacher_info[teacher['username']] = teacher['id']

        return teacher_info

    # 在指定教师下添加班级
    def add_class_ss(self, teacher_id, class_name, grade):
        response = self.session.post(f'{dls_host}/School/addClass.html', data={
            'teacher_id': teacher_id, 'name': class_name, 'comment': '', 'term': term, 'grade': grade
        })
        response = response.json()
        return response['status']

    # 查找班级
    def get_class_list(self, tid):
        response = self.session.post(f'{dls_host}/School/detailTeacherInfos.html', data={
            'tid': tid, 'subject_type': 1
        })
        response = response.json()
        class_list = {}
        for item in response['info']:
            class_list[item['name']] = item['class_id']
        return class_list

    # 指定班级里添加学生
    def add_student(self, username_s, name, c_id):
        response = self.session.post(f'{dls_host}/Business/addStudent.html', data={
            'username': username_s, 'name': name, 'cid': c_id
        })
        response = response.json()
        return response['info']

    def get_student_list(self, class_id, tid, sid):
        response = self.session.post(f'{dls_host}/school/studentList.html', data={
            'classId': class_id, 'term': term, 'teacherId': tid, 'schoolId': sid
        })
        users = response.json()['info']['students']
        username_s = {}
        for i in users:
            username_s[i['username']] = i['id']
        return username_s

    # 根据用户名查询教师id
    def search_teacher_info(self, username_t):
        response = self.session.post(f'{dls_host}/School/getTeacherForSearch.html', data={
            'search_type': 'username', 'search_key': username_t
        })
        response = response.json()
        return response['info']['teachers'][0]['id']

    def setClassCourse(self, cid):
        response = self.session.post(f'{dls_host}/ClassCourse/store.html', data={
            'class_id': cid, 'course_id': course_id, 'course_type': course_type, 'course_city_id': course_city_id,
            'start_time': start_time, 'end_time': end_time
        })
        response = response.json()
        return response['info']


school_opt = SchoolOpt()

if __name__ == '__main__':
    print(SchoolOpt().get_teacher_list(10005415, 2584))
