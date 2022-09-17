# -*- coding:utf-8 -*-
# @FileName  :excel_opt.py
# @Time      :2022/9/16 9:23
# @Author    :JN

import os
import traceback
from os.path import isfile, join

import pandas as pd

from lib.school_opt import school_opt

zid_dict = {
    '亭湖区': 257,
    '亭湖': 257,
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
        for file_path in file_path_list:
            data = pd.read_excel(io=file_path, header=1, sheet_name=None)
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
        for index,class_name in enumerate(class_list):
            if not str(class_name).isdigit():
                class_num = ''.join()
                s_name = school_list[index] + class_name

        # 表格的学校名称
        school_list = list_set_key(self.excel_data['学校（公章一致）'].values.tolist())
        # 线上学校列表
        school_list_online = None
        # 根据地区遍历学校
        for school_name in school_list:
            zid_ = self.excel_data[self.excel_data['学校（公章一致）'] == school_name].at[0, 'zid']
            if zid_ != zid:
                school_list_online = school_opt.get_school_list(zid_)
                zid = zid_

            if school_name in school_list_online:
                school_id[school_name] = school_list_online[school_name]
            else:
                try:
                    school_opt.add_school(zid, school_name)
                    school_list_online = school_opt.get_school_list()
                    school_id[school_name] = school_list_online[school_name]
                except Exception as e:
                    print(e)
                    school_id[school_name] = 0
        self.excel_data['sid'] = self.excel_data['学校（公章一致）'].map(lambda x: school_id[x])

    def format_teacher_id(self):
        phone_list = list_set_key(self.excel_data['备注'].values.tolist())
        teacher_list_online = None
        sid = None
        teacher_id = {}

        for phone in phone_list:
            df = self.excel_data[self.excel_data['备注'] == phone]
            teacher_name = df.at[0, '指导老师']
            sid_ = df.at[0, 'sid']
            username_t = phone
            zid = df.at[0, 'zid']
            if sid_ != sid:
                teacher_list_online = school_opt.get_teacher_list(sid_)
                sid = sid_
            if teacher_name in teacher_list_online:
                teacher_id[phone] = teacher_list_online[teacher_name]
            else:
                try:
                    res = school_opt.add_teacher(teacher_name, username_t, phone, zid, sid_)
                    if res:
                        teacher_id[phone] = res
                    else:
                        teacher_id[phone] = school_opt.search_teacher_info(username_t)
                except Exception as e:
                    print(e)
                    teacher_id[phone] = 0
        self.excel_data['tid'] = self.excel_data['备注'].map(lambda x: teacher_id[x])

    def format_class_id(self):
        pass

    # 格式化数据
    def format_df(self):
        # 获取表格原数据
        self.get_file_data()
        # 添加区域id列
        self.excel_data['zid'] = self.excel_data['县（区）'].map(lambda x: zid_dict[x])
        # 添加学校id
        self.format_school_id()


if __name__ == '__main__':
    a = ExcelOpt().format_df()
    print(a)
