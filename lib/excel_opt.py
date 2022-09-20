# -*- coding:utf-8 -*-
# @FileName  :excel_opt.py
# @Time      :2022/9/16 9:23
# @Author    :JN

import os
import traceback
from os.path import isfile, join

import pandas as pd

from lib.common import zid_dict
from lib.school_opt import school_opt


# 列表去重并不改变顺序
def list_set_key(data: list):
    l1 = list(set(data))
    l1.sort(key=data.index)
    return l1


class ExcelOpt:
    # excel 文件路径
    excel_path = join(os.path.realpath(__file__).split(r'\lib')[0], 'excel')
    header = ['序号', '姓名', '县（区）', '学校（公章一致）', '年级', '班级', '指导老师', '备注']
    excel_data = pd.DataFrame()

    # 获取excel文件路径
    def get_file_path(self):
        targetDir = join(self.excel_path, '1-old')
        filename_list = [f for f in os.listdir(targetDir) if isfile(join(targetDir, f))]
        full_file_path = [join(targetDir, i) for i in filename_list]
        return full_file_path

    # 获取excel数据
    def get_file_data(self):
        file_path_list = self.get_file_path()
        df = pd.DataFrame()
        # 遍历目录下的表格
        for file_path in file_path_list:
            data = pd.read_excel(io=file_path, header=1, sheet_name=None)
            # 遍历工作表
            for sheet in data:
                if data[sheet].empty:
                    continue
                assert data[sheet].columns.tolist() == self.header, f'{file_path}：{sheet}表头异常'
                df = pd.concat([df, data[sheet]], ignore_index=True)
        self.excel_data = df

    def format_school_id(self):
        school_id = {}
        zid = None
        # 判断是否是分校
        class_list = self.excel_data['班级'].values.tolist()
        school_list = self.excel_data['学校（公章一致）'].values.tolist()
        for index, class_name in enumerate(class_list):
            if not str(class_name).isdigit():
                class_num: str = ''.join(list(filter(str.isdigit, class_name)))
                s_name: str = school_list[index] + class_name.split(class_num)[0] + '校区'
                s_name = s_name.replace('校区校区', '校区').strip()
                school_list[index] = s_name
                class_list[index] = class_num
        self.excel_data['学校（公章一致）'] = school_list
        self.excel_data['班级'] = class_list

        # 表格的学校名称
        school_list = list_set_key(school_list)
        # 线上学校列表
        school_list_online = None
        # 根据地区遍历学校
        for school_name in school_list:
            zid_ = self.excel_data[self.excel_data['学校（公章一致）'] == school_name]
            zid_ = zid_.iat[0, 8]
            if zid_ != zid:
                school_list_online = school_opt.get_school_list(zid_)
                zid = zid_
            if school_name in school_list_online:
                school_id[school_name] = school_list_online[school_name]
                print(f'学校 {school_name} 已存在')
            else:
                # noinspection PyBroadException
                try:
                    school_opt.add_school(zid, school_name)
                    school_list_online = school_opt.get_school_list(zid_)
                    school_id[school_name] = school_list_online[school_name]
                    print(f'学校 {school_name} 添加成功')
                except Exception as e:
                    traceback.print_exc()
                    school_id[school_name] = 0
                    print(f'学校 {school_name} 添加失败！！！！')
        self.excel_data['sid'] = self.excel_data['学校（公章一致）'].map(lambda x: school_id[x])

    def format_teacher_id(self):
        self.excel_data['备注'] = self.excel_data['指导老师'].str.cat(self.excel_data['备注'])
        phone_list = list_set_key(self.excel_data['备注'].values.tolist())
        teacher_list_online = None
        sid = None
        teacher_id = {}

        for phone in phone_list:
            df = self.excel_data[self.excel_data['备注'] == phone]
            teacher_name = df.iat[0, 6].strip()
            sid_ = df.iat[0, 9]
            username_t = str(phone)
            zid = df.iat[0, 8]
            if sid_ == 0:
                print('教师学校不存在，跳过')
                teacher_id[username_t] = 0
                continue
            if sid_ != sid:
                teacher_list_online = school_opt.get_teacher_list(sid_, zid)
                sid = sid_
            if username_t in teacher_list_online:
                print(f'教师 {teacher_name}({username_t}) 已存在')
                teacher_id[username_t] = teacher_list_online[username_t]
            else:
                # noinspection PyBroadException
                try:
                    res = school_opt.add_teacher(teacher_name, username_t, phone, zid, sid_)
                    if res:
                        teacher_id[username_t] = res
                        print(f'教师 {teacher_name}({username_t}) 添加成功')
                    else:
                        print(f'教师 {teacher_name}({username_t}) 已存在')
                        # noinspection PyBroadException
                        try:
                            teacher_id[username_t] = school_opt.search_teacher_info(username_t)
                        except Exception as e:
                            traceback.print_exc()
                            teacher_id[username_t] = 0
                            print(f'-- 可能注册成学生账号')
                except Exception as e:
                    traceback.print_exc()
                    teacher_id[username_t] = 0
                    print(f'教师 {teacher_name}({username_t}) 添加失败！！！！')
        self.excel_data['tid'] = self.excel_data['备注'].map(lambda x: teacher_id[str(x)])

    def format_class_id(self):
        self.excel_data['tid'] = self.excel_data['tid'].map(lambda x: str(x))
        self.excel_data['s_c'] = self.excel_data['tid'].str.cat(self.excel_data['班级'], sep="-")
        class_teacher = list_set_key(self.excel_data['s_c'].values.tolist())

        tid = None
        class_list_online = None
        class_id = {}
        for class_name in class_teacher:
            tid_ = class_name.split('-')[0]
            name = class_name.split('-')[-1]
            if tid_ == '0' or tid_ == 0:
                print(f'班级 {name}({tid_}) 教师不存在，跳过\n')
                class_id[class_name] = 0
                continue
            if tid_ != tid:
                class_list_online = school_opt.get_class_list(tid_)
                tid = tid_
            if name in class_list_online:
                print(f'班级 {name}({tid_}) 已存在\n')
                class_id[class_name] = class_list_online[name]
            else:
                # noinspection PyBroadException
                try:
                    school_opt.add_class_ss(tid_, name, name[:2])
                    class_list_online = school_opt.get_class_list(tid_)
                    class_id[class_name] = class_list_online[name]
                    print(f'班级 {name}({tid_}) 添加成功')
                    # 添加体验套餐
                    print('-- 添加班级体验套餐\n')
                    school_opt.setClassCourse(class_list_online[name])
                except Exception as e:
                    traceback.print_exc()
                    class_id[class_name] = 0
                    print(f'班级 {name}({tid_}) 添加失败\n')
        self.excel_data['cid'] = self.excel_data['s_c'].map(lambda x: class_id[x])

    # 格式化数据
    def format_df(self):
        # 获取表格原数据
        print('1.开始获取表格数据：')
        self.get_file_data()
        print('表格数据获取成功！\n')
        # 添加区域id列
        print('2.整理区域id')
        self.excel_data['zid'] = self.excel_data['县（区）'].map(lambda x: zid_dict[x])
        self.excel_data['备注'] = self.excel_data['备注'].map(lambda x: str(x))
        self.excel_data['班级'] = self.excel_data['班级'].map(lambda x: str(x))
        self.excel_data['姓名'] = self.excel_data['姓名'].map(lambda x: x.replace(' ', '').strip())
        self.excel_data['指导老师'] = self.excel_data['指导老师'].map(lambda x: x.replace(' ', '').strip())
        print('区域id整理成功！\n')
        # 添加学校id
        print('3.整理学校id')
        self.format_school_id()
        print('学校id整理成功！\n')
        # 添加教师id
        print('4.整理教师id')
        self.format_teacher_id()
        print('教师id整理成功！\n')
        # 添加班级id
        print('3.整理班级id')
        self.format_class_id()
        print('班级id整理成功！\n')
        # 保存
        print('保存')
        del self.excel_data['s_c']
        self.excel_data.to_excel(os.path.join(self.excel_path, '2-new/user_add.xlsx'), index=False)


if __name__ == '__main__':
    pass
