# -*- coding:utf-8 -*-
# @FileName  :excel_opt.py
# @Time      :2022/9/16 9:23
# @Author    :JN

import os
from os.path import isfile, join

import pandas as pd

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


class ExcelOpt:
    # excel 文件路径
    excel_path = join(os.path.realpath(__file__).split(r'\lib')[0], 'excel')
    header = ['序号', '姓名', '县（区）', '学校（公章一致）', '年级', '班级', '指导老师', '备注']
    excel_df = None

    # 获取excel文件路径
    def get_file_path(self):
        targetDir = join(self.excel_path, 'old')
        filename_list = [f for f in os.listdir(targetDir) if isfile(join(targetDir, f))]
        full_file_path = [join(targetDir, i) for i in filename_list]
        return full_file_path

    # 获取excel数据
    def get_file_data(self):
        file_path_list = self.get_file_path()
        df = None
        for file_path in file_path_list:
            data = pd.read_excel(io=file_path, header=1, sheet_name=None)
            for sheet in data:
                if data[sheet].empty:
                    continue
                assert data[sheet].columns.tolist() == self.header, f'{file_path}：{sheet}表头异常'
                df = pd.concat([df, data[sheet]], ignore_index=True)
        return df

    # 格式化数据
    def format_df(self):
        account = {}
        df = self.get_file_data()
        for row in df.itertuples():
            student_name = getattr(row, '姓名').strip().replace(' ', '')
            zid = zid_dict[getattr(row, '_3')]
            school_name = getattr(row, '_4')
            grade = str(getattr(row, '年级'))
            class_room = str(getattr(row, '班级'))
            teacher_name = getattr(row, '指导老师').strip()
            phone = getattr(row, '备注')
            if not class_room.isdigit():
                class_num = ''.join(list(filter(str.isdigit, class_room)))
                school_name = school_name + class_room.split(class_num)[0] + '校区'
                school_name = school_name.replace('校区校区', '校区')
                school_name = school_name.strip()
                class_room = class_num
            if school_name not in account:
                account[school_name] = {
                    'zid': zid,
                    'school_name': school_name,
                    'teacher': {

                    }
                }
            if teacher_name not in account[school_name]['teacher']:
                account[school_name]['teacher'][teacher_name] = {
                    'phone': phone,
                    'name': teacher_name,
                    'username': phone,
                    'class_room': {},
                }
            if class_room not in account[school_name]['teacher'][teacher_name]['class_room']:
                account[school_name]['teacher'][teacher_name]['class_room'][class_room] = []

            account[school_name]['teacher'][teacher_name]['class_room'][class_room].append(student_name)
        return account


if __name__ == '__main__':
    a = ExcelOpt.excel_path
    print(a)
