import xlrd
import redis

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
        r.hset(key, test_name, new_dict[key])

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

if __name__ == "__main__":
    data = xlrd.open_workbook('test_data/成绩记录.xlsx')
    
    # update initial user passwords
    table = data.sheets()[1]
    # update_redis(get_new_dict(table, '登录名', '分数'), "Second")
    name_to_name = get_new_dict(table, "登录名", "登录名")
    for key in name_to_name.keys():
        if (len(key) >= 6):
            name_to_name[key] = key[-6:]
        else:
            name_to_name[key] = key
    update_redis(name_to_name, "password")

    table = data.sheets()[0]
    name_to_name = get_new_dict(table, "登录名", "登录名")
    for key in name_to_name.keys():
        if (len(key) >= 6):
            name_to_name[key] = key[-6:]
        else:
            name_to_name[key] = key
    update_redis(name_to_name, "password")
