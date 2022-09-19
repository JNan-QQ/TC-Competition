# -*- coding:utf-8 -*-
# @FileName  :main.py
# @Time      :2022/9/16 9:23
# @Author    :JN
import os
import traceback
from threading import Lock
from time import time

import pandas as pd

from lib import school_opt
from lib.common import threadPool
from lib.excel_opt import ExcelOpt
from lib.school_opt import school_opt


class StudentInfo:
    user_excel_path = os.path.join(os.getcwd(), 'excel/2-new/user_add.xlsx')
    online_student = {}
    student_info_Lock = Lock()

    def get_excel_data(self):
        data = pd.read_excel(io=self.user_excel_path, sheet_name='Sheet1')
        data = data.to_dict(orient='records')
        return data

    def add_student(self, data):
        s_name = data['姓名'].replace(' ', '').replace('\n', '')
        tid = str(data['tid'])
        s_username = s_name + tid
        cid = str(data['cid'])
        t_c_s = tid + '_' + cid

        if cid == '0':
            print('班级不存在，跳过')
            data['uid'] = 0
            return data

        if t_c_s not in self.online_student:
            self.student_info_Lock.acquire()
            if t_c_s not in self.online_student:
                self.online_student[t_c_s] = school_opt.get_student_list(cid, tid, data['sid'])
            self.student_info_Lock.release()
        if s_username in self.online_student[t_c_s]:
            data['uid'] = self.online_student[t_c_s][s_username]
            print(f'学生 {s_username} 已在班')
        else:
            # noinspection PyBroadException
            try:
                res_add_student = school_opt.add_student(s_username, s_name, cid)
                print(f'-- {res_add_student}')
                if 'uid' in res_add_student:
                    print(f'学生 {s_username} 已添加')
                    data['uid'] = res_add_student['uid']
                else:
                    data['uid'] = 0
                    print(f'学生 {s_username} 添加失败！！！')
            except Exception as e:
                traceback.print_exc()
                data['uid'] = 0
                print(f'学生 {s_username} 添加失败！！！')
        return data

    def write_result(self, add_id_user):
        df = sorted(add_id_user, key=lambda x: x['序号'])
        df = pd.DataFrame(df)
        df.to_excel(self.user_excel_path, index=False)


if __name__ == '__main__':
    mode = input('请输入模式 1-整理表格，2-录入学生：')
    if mode == '1':
        ExcelOpt().format_df()
    elif mode == '2':
        student_info = StudentInfo()
        user_data = student_info.get_excel_data()
        new_user_data = []
        # 将任务导入线程池
        begin = time()
        for result in threadPool.map(student_info.add_student, user_data):
            new_user_data.append(result)
        print(time() - begin)
        df_data = pd.DataFrame(new_user_data)
        df_data.to_excel(os.path.join(os.getcwd(), 'excel/3-result/user_add_id.xlsx'), index=False)
