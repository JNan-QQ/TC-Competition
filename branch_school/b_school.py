# -*- coding:utf-8 -*-
# @FileName  :b_school.py
# @Time      :2022/9/20 12:49
# @Author    :JN
import glob
import os

import pandas as pd


# 列表去重并不改变顺序
def list_set_key(data: list):
    l1 = list(set(data))
    l1.sort(key=data.index)
    return l1


class ExcelOpt1:
    # excel 文件路径
    excel_path = os.getcwd()
    excel_data = pd.DataFrame()

    # 获取excel文件路径
    def get_file_path(self):
        full_file_path = glob.glob(fr'{self.excel_path}/*.xlsx')
        return full_file_path

    # 获取excel数据
    def get_file_data(self):
        file_path_list = self.get_file_path()
        df = pd.DataFrame()
        # 遍历目录下的表格
        for file_path in file_path_list:
            data = pd.read_excel(io=file_path, sheet_name=None)
            # 遍历工作表
            for sheet in data:
                if data[sheet].empty:
                    continue
                df = pd.concat([df, data[sheet]], ignore_index=True)
        self.excel_data = df

    #
    def zl(self):
        self.excel_data.columns = ['序号', '学生姓名', '县', '学校', '年级', '班级', '教师姓名', '教师用户名', 'zid', 'sid', '班级码', 'cid',
                                   '学生id']
        self.excel_data['班级码'] = self.excel_data['班级码'].map(lambda x: str(x))
        self.excel_data['学生用户名'] = self.excel_data['学生姓名'].str.cat(self.excel_data['班级码'])
        df = self.excel_data[['学校', '年级', '班级', '班级码', '教师姓名', '教师用户名', '学生id', '学生姓名', '学生用户名']]
        self.excel_data = df

    def writeExcel(self):
        school_list = self.excel_data['学校'].values.tolist()
        school_list = list_set_key(school_list)
        for school in school_list:
            data = self.excel_data[self.excel_data['学校'] == school]
            data.to_excel(f'{self.excel_path}/res/{school}.xlsx', index=False)


if __name__ == '__main__':
    ss = ExcelOpt1()
    ss.get_file_data()
    ss.zl()
    ss.writeExcel()
