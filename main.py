# -*- coding:utf-8 -*-
# @FileName  :main.py
# @Time      :2022/9/16 9:23
# @Author    :JN
import os
import traceback
from threading import Thread
from time import sleep

import pandas as pd

from lib.excel_opt import ExcelOpt
from lib.school_opt import SchoolOpt


def write_log(msg):
    with open('logs.txt', 'a+', encoding='utf8') as fb:
        fb.write(msg)


# 添加学生线程
def run_thread(student_segment_list, tid, cid, cname, sname, online_list):
    for student in student_segment_list:
        sleep(0.2)
        # 判断是否重复
        if student.endswith('a'):
            student_username = student[:-1] + str(tid) + 'a'
        else:
            student_username = student + str(tid)
        if student_username in online_list:
            print(f'学生已在班！-- {student}')
            success_info.append(
                [online_list[student_username], student_username, student, cid, cname, cname[0], tid, sname])
            continue
        try:
            res_add_student = school_opt.add_student(student_username, student, cid)
            if 'uid' in res_add_student:
                success_info.append(
                    [res_add_student['uid'], student_username, student, cid, cname, cname[0], tid, sname])
                print(f'添加成功！-- {student}')
            else:
                error_info.append([student_username, student, cid, cname, cname[0], tid, sname])
                with open('logs.txt', 'a+', encoding='utf8') as f:
                    f.write(f'------ 学生：{student}创建失败！跳过该学生(1)。\n')
        except:
            error_info.append([student_username, student, cid, cname, cname[0], tid, sname])
            with open('logs.txt', 'a+', encoding='utf8') as f:
                f.write(f'------ 学生：{student}创建失败！跳过该学生(2)。\n')


if __name__ == '__main__':

    thread_num = 5

    excel_opt = ExcelOpt()
    school_opt = SchoolOpt()
    # 获取账号信息
    account = excel_opt.format_df()

    # 学校
    try:
        for school_name, school_value in account.items():
            success_info = []
            error_info = []
            print(f'学校：{school_name}查找成功！。\n')
            # 获取该学校地区学校列表
            zid = school_value['zid']
            school_info = school_opt.get_school_list(zid)

            # 学校不存在添加学校
            if school_name not in school_info:
                try:
                    school_opt.add_school(zid, school_name)
                except:
                    write_log(f'学校：{school_name}创建失败！跳过该学校。\n')
                    continue
                school_info = school_opt.get_school_list(zid)

            # 学校id
            school_id = school_info[school_name]['id']
            write_log(f'学校：{school_name}查找成功！。\n')

            # 教师
            for teacher_name, teacher_value in school_value['teacher'].items():
                # 获取该学校教师列表
                teacher_info = school_opt.get_teacher_list(school_id)
                # 添加教师
                if teacher_name not in teacher_info:
                    try:
                        res = school_opt.add_teacher(teacher_value['name'], teacher_value['username'],
                                                     teacher_value['phone'],
                                                     zid, school_id)
                        if res:
                            teacher_id = res
                        else:
                            teacher_id = school_opt.search_teacher_info(teacher_value['phone'])
                    except:
                        write_log(f'--- 教师：{teacher_name}创建失败！跳过该教师。\n')
                        continue
                else:
                    teacher_id = teacher_info[teacher_name]['id']
                write_log(f'--- 教师：{teacher_name}查找成功！。\n')
                print(f'--- 教师：{teacher_name}查找成功！。\n')

                # 班级
                for class_name, student_list in teacher_value['class_room'].items():
                    class_room = school_opt.get_class_list(teacher_id)
                    if class_name not in class_room:
                        try:
                            school_opt.add_class_ss(teacher_id, int(class_name), int(class_name[0]))
                        except:
                            traceback.print_exc()
                            write_log(f'----- 班级：{class_name}创建失败！跳过该班级。\n')
                            continue
                        class_room = school_opt.get_class_list(teacher_id)
                    class_id = class_room[class_name]
                    write_log(f'----- 班级：{class_name}查找成功！\n')
                    print(f'----- 班级：{class_name}查找成功！\n')

                    # 班级里的学生
                    online_student_list = school_opt.get_student_list(class_id)
                    # 重复名称的学生
                    repeat_student = []

                    for index, i in enumerate(student_list):
                        if i in repeat_student:
                            student_list[index] += 'a'
                        if student_list.count(i) > 1:
                            repeat_student.append(i)

                    print('a')
                    # 添加启动线程
                    thread_list = []
                    student_num = len(student_list)
                    for i in range(1, thread_num + 1):
                        thread = Thread(target=run_thread, args=(
                            student_list[int((i - 1) * student_num / thread_num):int(i * student_num / thread_num)],
                            teacher_id, class_id, class_name, school_name, online_student_list))
                        thread.start()
                        thread_list.append(thread)

                    print('b')
                    for t_j in thread_list:
                        t_j.join()
                    print('c')

            df_success = pd.DataFrame(success_info, columns=['学生id', '用户名', '姓名', '班级id', '班级名称', '年级', '教师id', '学校'])
            df_success.to_excel(os.path.join(os.getcwd(), f'excel/result/success-{school_name}.xlsx'))
            if error_info:
                df_error = pd.DataFrame(error_info, columns=['用户名', '姓名', '班级id', '班级名称', '年级', '教师id', '学校'])
                df_error.to_excel(os.path.join(os.getcwd(), f'excel/result/error-{school_name}.xlsx'))
            print('d')
    except:
        traceback.print_exc()
