import xlrd
import redis
import os
import re
import json

r = redis.Redis(host="localhost", port=6379, db=0)

def transfer(x):        # transfer studentNo ('123456' or 'AB123456') to string
    if (type(x) == type('')):
        return x
    else:
        return str(int(x))

def update_redis(new_dict, test_name):
    '''
    update info into redis database
    new_dict: {header_name: header_grade}
    '''
    for key in new_dict.keys():
        r.hset(key, test_name, new_dict[key]) # insert { key: {test_name: new_dict[key]} }
        # print(r.hget(key, test_name))

def new_dict_to_redis(dict_name, new_dict):
    r.hmset(dict_name, new_dict)

def get_new_dict(table, header_name, header_grade):
    '''
    target redis structure: (key = string, value = hash)
    update every (key = header_name) by (value[test_name] = header_grade)
    return: {header_name: header_grade} for future update
    '''
    nrows, ncols = table.nrows, table.ncols
    header_name_idx = (-1, -1)
    header_grade_idx = (-1, -1)
    for i in range(nrows):
        line = table.row_values(i, start_colx = 0, end_colx = None)
        if (header_name in line and header_grade in line):
            header_name_idx = (i, line.index(header_name))
            header_grade_idx = (i, line.index(header_grade))
            break
    if (header_name_idx == (-1, -1) or header_grade_idx == (-1, -1)):
        return None
    
    name_list = table.col_values(header_name_idx[1], start_rowx = header_name_idx[0]+1, end_rowx = None)
    grade_list = table.col_values(header_grade_idx[1], start_rowx = header_grade_idx[0]+1, end_rowx = None)

    if (len(name_list) != len(grade_list)):
        return None

    name_list = [transfer(x) for x in name_list]    # transfer header_name into string
    name_to_grade = dict(zip(name_list, grade_list))
    return name_to_grade

def xlsx_into_redis():
    # 作用：读入整个成绩xlsx的信息（学号，密码，每次成绩）并写入redis中
    data = xlrd.open_workbook('test_data/grades.xlsx').sheet_by_index(0)
    header = data.row_values(0)
    idx = [i for i in range(len(header))]
    test_name = header[2:]
    name_to_name = get_new_dict(data, "登录名", "登录名")
    for key in name_to_name.keys():
        if (len(key) >= 6):
            name_to_name[key] = key[-6:]
        else:
            name_to_name[key] = key
    # 初始化：用学号后6位作为用户名：密码
    update_redis(name_to_name, "password")  # name_to_name: key->password, 

    # grade_dicts_list = [{}] * len(test_name)
    grade_dicts_list = []
    for i in range(len(test_name)):
        grade_dicts_list.append({})
    
    for i in range(1, data.nrows):
        line = data.row_values(i, start_colx = 1, end_colx = None)
        uid = str(int(line[0]))
        for j in range(1, len(line)-1):
            grade_dicts_list[j-1][uid] = line[j]        # {uid -> score}
    test_num_to_name = {}
    for i in range(len(test_name)):
        test_num_to_name["test_{0}".format(i+1)] = test_name[i]
    # print(test_num_to_name)

    r.hmset("test_name", test_num_to_name)
    test_identifier = ["test_{0}".format(i+1) for i in range(len(test_name))]
    # print(test_identifier)

    for i in range(len(test_name)):
        print(grade_dicts_list[i])
        update_redis(grade_dicts_list[i], test_identifier[i])

def generate_student_dict():
    # get radar info
    path = os.curdir + r"/templates/students profiles.html"
    ret = {}
    with open(path, "r", encoding="utf-8") as fr:
        x = json.loads(fr.read())["series"]
        for student_info in x:
            ret[student_info['name']] = str(student_info['data'])
    print(ret)
    new_dict_to_redis("radar_info", ret)
    return ret

def test_redis():
    print(r.hget("test_name", "test_1"))
    print(r.hgetall("181830158"))
    print(r.hget("radar_info", "181830158"))

if __name__ == "__main__":
    xlsx_into_redis()
    generate_student_dict()
    test_redis()