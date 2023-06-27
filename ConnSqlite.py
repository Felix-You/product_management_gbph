import json
import sqlite3, requests, importlib
import time
from abc import abstractmethod
from itertools import chain
from FilePathInit import userDir, workingDir
from abc import ABC

self = importlib.import_module("ConnSqlite")
use_service = 'local'
db_file = userDir.getDatabase()
drug_db_file = userDir.getDrugDataBase()
if not db_file:
    print('未找到主数据库文件')
path = workingDir.getUserDirectory()
# path = 'D:/'
cx = sqlite3.connect(db_file)
c_drug = sqlite3.connect(drug_db_file)
cor = cx.cursor()
dtypeDict= {
    'varchar':'U100',
    'text':'U100',
    'bool':'b',
    'real':'f',
    'INTEGER':'i'
}

"""def NpFrame(nplist:list):
    '''将sqlite返回的结果包装成带字段的array并返回'''
    names = []
    formats = []
    b = list(nplist.pop())
    print(b )
    for item in b:
        names.append(item)
        formats.append(object)

    dt = np.dtype({'names':names, 'formats':formats},)
    #print(dt)
    array = np.array(nplist,dt)

    return array

def PdFrame(pdlist:list):
    '''将sqlite返回的结果包装成带字段的dataframe并返回'''
    colum_names = list(pdlist.pop())
    print(colum_names )
    frame = pd.DataFrame(pdlist, columns=colum_names)
    return frame

def getNpFrameLines(array:np.array,fields_values:dict):
    fields = list(fields_values.keys())
    values = list(fields_values.values())
    b = np.array(array[fields[0]] == values[0])#一维布尔矩阵
    for i in range(1,len(fields)):
        b = b * np.array(array[fields[i]] == values[i] )
    return array[np.array(b)]
    pass"""

get_methods = set(['getTableFields', 'getTableRowCount', 'getLineFromSqlite', 'getInFromSqlite', 'multiConditionsGetLinesFromSqlite',
                  'innerJoin_withList_getLines', 'getLinesFromTable', 'getInFromSqlite', 'getLineFromSqlite', 'getLikeLinesFromTable',
                    'getSqliteCells'])

def fromRemote(func):
    if use_service != 'remote':
        return func
    func_name = func.__name__
    def remote(*args, **kwargs):
        # if not isinstance(args, tuple):
        #     args = (args,)
        url = 'http://127.0.0.1:8000/api/projects/'
        data = {'function': func_name,
                'args': json.dumps(args),
                'kwargs': json.dumps(kwargs)}
        if func_name in get_methods:
            res = requests.get(
                url=url,
                data=data,
            )
            data = res.json()['data']
            return data
        else:
            res = requests.post(
                url=url,
                data=data,
            )
            data = res.json()['data']
            return data
    return remote

# def __getattr__(name):
#     if use_service == 'remote':
#         return fromRemote(name)
#     else:
#         return self.__dict__[name]

def initDatabase():
    global path
    global db_file
    global cx
    path = workingDir.getUserDirectory()
    db_file = userDir.getDatabase()
    cx = sqlite3.connect(db_file)

def getTableFields(table_name:str):
    # cursor = cx.cursor()
    col_info = cx.execute('pragma table_info("{}")'.format(table_name)).fetchall()
    # print('table_name',table_name,'col_info',col_info)
    col_name = []
    for item in col_info:
        col_name.append(item[1])
    col_name_result = tuple(col_name)
    # print('table_name',table_name,'col_name_result',col_name_result)
    return col_name_result

def getTableRowCount(table_name:str):
    row_count = cx.execute('select count(*) from {}'.format(table_name)).fetchall()
    return row_count

def insertSqlite(table, row_data:dict):
    cursor = cx.cursor()
    keys = ', '.join(row_data.keys())
    values = ', '.join(["?"] * len(row_data))
    sql = 'insert into {table} ({keys}) values ({values}) '.format(table=table, keys=keys, values=values)
    try:
        #print(tuple(row_data.values()))
        cursor.execute(sql, tuple(row_data.values()))
        #print(sql)
        print(sql)
        print('插入成功')
        cx.commit()
    except Exception as e:
        #print(sql)
        # print('插入失败，回滚')
        print(e)
        cx.rollback()

def insertMultiLinesSqlite(table, keys:list[str], lines:list[list]):
    cursor = cx.cursor()
    # keys = ', '.join(keys)
    len_line = len(keys)
    lines = [', '.join(line) for line in lines]
    SELECT_COLUMN = "SELECT" + ', '.join([f" ? AS {key}" for key in keys])
    LINE = ', '.join("?" for i in range(len_line))
    SELECT_OTHER_LINES = ' '.join(["UNION SELECT "+ LINE for i in range(len(lines) - 1)])

    sql = f"INSERT INTO {table} {SELECT_COLUMN} {SELECT_OTHER_LINES}"
          # "SELECT 'data1' AS 'column1', 'data2' AS 'column2‘" \
          # "UNION SELECT 'data3', 'data4'" \
          # "UNION SELECT 'data5', 'data6'" \
          # "UNION SELECT 'data7', 'data8'"
    data = tuple(chain(lines))
    try:
        # print(tuple(row_data.values()))
        cursor.execute(sql, data)
        # print(sql)
        print(sql)
        print('插入成功')
        cx.commit()
    except Exception as e:
        print(sql)
        print('插入失败，回滚')
        print(e)
        cx.rollback()

def upsertSqlite(table, keys:list, values:list):
    cursor = cx.cursor()

    keys_expr = ', '.join(keys)
    values_expr = ', '.join(["?"] * len(values))

    update_keys = ['{key}=excluded.{key}'.format(key = key) for key in keys]
    update_keys_expr = ', '.join(update_keys)

    sql = 'insert into {table} ({keys}) values ({values}) ' \
          'on conflict(_id) do update set {update_keys_expr}'.\
        format(table=table, keys=keys_expr, values=values_expr, update_keys_expr =update_keys_expr)
    try:
        #print(tuple(row_data.values()))
        # print(sql)
        cursor.execute(sql, tuple(values))
        # print('保存成功')
        cx.commit()
        return True
    except Exception as e:
        print(sql)
        print('插入失败，回滚')
        print(e)

        cx.rollback()
        return False

def createInsertTriggers(table_name:str):
    cursor=cx.cursor()
    sql = f"create TRIGGER {table_name}_insert_log AFTER INSERT ON {table_name} FOR EACH ROW BEGIN INSERT INTO " \
          "new_change_log (updated_table_name,updated_row_id,update_time,action_type ) VALUES " \
          f"('{table_name}', new._id, datetime('now'), 'insert');END;"
    cursor.execute(sql)

def createUpdateTrigger(table_name:str):
    cursor=cx.cursor()
    sql = f"CREATE TRIGGER {table_name}_update_log AFTER UPDATE ON {table_name} FOR EACH ROW BEGIN DELETE FROM " \
          "new_change_log WHERE updated_row_id = new._id; INSERT INTO new_change_log " \
          "(updated_table_name, updated_row_id, update_time, action_type) " \
          f"VALUES ('{table_name}', new._id, datetime('now'), 'update');END;"
    cursor.execute(sql)

def getLineFromSqlite(table_name:str,condition:dict):
    result = []
    if not condition:
        sql = "select * from %s"%(table_name)
        result = cx.execute(sql).fetchall()
        # print(sql)
        # print('查找成功')
        # print(result)
        #cx.close()
    else:
        condition_keys = list(condition.keys())
        condition_values = list(condition.values())
        condition_key_expression = []
        for i in range(len(condition_keys)):
            if isinstance(condition_values[i],list) or isinstance(condition_values[i], tuple):
                condition_key_expression.append(condition_keys[i] + ' in ? COLLATE NOCASE')
                condition_values[i] = tuple(condition_values[i])
            else:
                condition_key_expression.append(condition_keys[i] + '= ? COLLATE NOCASE')
        conditions_sentence = ' and '.join(condition_key_expression)# key1 = ? and key2 = ? ...
        sql = "select * from {table_name} where {condition};".format( table_name= table_name,condition = conditions_sentence)
        try:
            #print(tuple(row_data.values()))
            print(sql, tuple(condition_values))
            result = cx.execute(sql,condition_values).fetchall()

            print('查找成功')
            #print(result)
            #cx.close()
        except Exception as e:
            #print(sql)
            print('查找失败')
            print(e)
            return None
    if len(result) == 0:
        return []

    col_info = cx.execute('pragma table_info("{}")'.format(table_name)).fetchall()
    col_name = []
    for item in col_info:
        col_name.append(item[1])
    col_name_result = tuple(col_name)
    result.append(col_name_result)
    return result

def getInFromSqlite(table_name:str,condition:dict):
    result = []
    condition_key = list(condition.keys())[0]
    condition_value = tuple(list(condition.values())[0])
    sql = "select * from {table_name} where {key} in {value} ;".format(table_name=table_name ,key = condition_key,value=condition_value)
    try:
        # print(tuple(row_data.values()))
        print(sql)
        result = cx.execute(sql).fetchall()

        print('查找成功')
        # print(result)
        # cx.close()
    except Exception as e:
        # print(sql)
        print('查找失败')
        print(e)
        return None
    if len(result) == 0:
        return []

    col_info = cx.execute('pragma table_info("{}")'.format(table_name)).fetchall()
    col_name = []
    for item in col_info:
        col_name.append(item[1])
    col_name_result = tuple(col_name)
    result.append(col_name_result)
    return result

def multiConditionsGetLinesFromSqlite(table_name:str, condition_keys:tuple, condition_values:list, columns_required:list = None):
    '''根据Key和Value的组合来查询，其中查询失败的时候，会把condition_keys的第一Key插入到空行中一并返回'''
    results = []
    col_info = cx.execute('pragma table_info("{}")'.format(table_name)).fetchall()
    col_name = []
    for item in col_info:
        col_name.append(item[1])
    col_name_result = tuple(col_name)
    # print(col_name_result)
    for values in condition_values:
        condition_key_expression = []
        for i in range(len(condition_keys)):
            if isinstance(values[i], (list,tuple)):
                condition_key_expression.append(condition_keys[i] + ' in ? COLLATE NOCASE')
                values[i] = tuple(values[i])
            else:
                condition_key_expression.append(condition_keys[i] + '= ? COLLATE NOCASE')
        conditions_sentence = ' and '.join(condition_key_expression)  # key1 = ? and key2 = ? ...
        sql = "select * from {table_name} where {condition};".format(table_name=table_name, condition=conditions_sentence)
        if columns_required:
            column_place_holders = ['%s' for i in columns_required]
            place_holder_str = ', '.join(column_place_holders)
            sql = sql.replace('*', place_holder_str)
            # print(sql)
            # print(tuple(columns_required))
            sql = sql % tuple(columns_required)
        print(sql)
        try:
            # print(tuple(row_data.values()))
            #print(sql)
            print(tuple(values))


            result = cx.execute(sql, tuple(values)).fetchall()
            results.extend(result)
            # cx.close()
            # print(result)
        except Exception as e:
            # print(sql)
            print('查找错误')
            print(e)
        if len(results) == 0:
            print('未找到')

    if columns_required:  #
        results.append(tuple(columns_required))
    else:
        results.append(col_name_result)
    return results

def renderConditionExpression(condition:dict, join_table_mark:str=None)-> [str,tuple]:
    """
    :condition: the query condition
    :join_table_mark: alias of the table name, when preparing a condition sentence for a join query,
    """
    items = condition.items()
    condition_key_expression = []
    condition_values = []
    if join_table_mark:
        mark = join_table_mark+'.'
    else:
        mark = ''
    for k, v in items:
        key = mark + k
        if isinstance(v, (list,tuple)):
            condition_key_expression.append(key + ' in ({}) COLLATE NOCASE'.format(', '.join(['?' for i in range(len(v))])))
            condition_values.extend(list(v))
        elif isinstance(v, str):
            condition_key_expression.append(key + " = ? COLLATE NOCASE")  # 字符串类型需要加上单引号
            condition_values.append(v)
        else:
            condition_key_expression.append(key + " = ? ")
            condition_values.append(v)
    conditions_sentence = ' and '.join(condition_key_expression)  # key1 = ? and key2 = ? ...
    return conditions_sentence, condition_values


    # sql = "select distinct * from {table_name} where {condition} ".format(table_name=table_name,
    #                                                                       condition=conditions_sentence)
    # sql = sql.format(*condition_values)
    # # print(*condition_values)
    # sql = sql.replace(',)', ')')  # 当list里面只有一个元素时，转换成python的tuple会出现多了一个','，需要去掉


def innerJoin_withList_getLines(table_a:str, table_b:str,
                                joint_key_a:str, joint_key_b:str,
                                target_colums_a:list[str], target_colunms_b:list[str],
                                condition_a:dict=None, condition_b:dict=None,
                                method:str = 'inner join'):
    '''
    method: "inner join", "left outer join"/"left join" or  "cross join"
    '''
    if not method in ('inner join', 'left outer join', 'left join', 'cross join'):
        raise ValueError(f'invalid method {method}')
    if not condition_a:
        condition_a = {}
    if not condition_b:
        condition_b = {}
    condition_sentence_a, condition_values_a = renderConditionExpression(condition_a, 'a')
    condition_sentence_b, condition_values_b = renderConditionExpression(condition_b, 'b')
    if condition_sentence_a and condition_sentence_b:
        condition_sentence = f'{condition_sentence_a} and {condition_sentence_b}'
        condition_values = condition_values_a + condition_values_b
    elif condition_values_a:
        condition_sentence = condition_sentence_a
        condition_values = condition_values_a
    elif condition_values_b:
        condition_sentence = condition_sentence_b
        condition_values = condition_values_b
    else:
        condition_sentence = ''
        condition_values = ()

    target_expression_a = ['a' + '.'+column for column in target_colums_a]
    target_expression_b = ['b' + '.'+column for column in target_colunms_b]
    target_expression = target_expression_a
    target_expression.extend(target_expression_b)
    targets_sentence = ', '.join(target_expression)

    if condition_values:
        # sql = "SELECT {targets} FROM " \
        #       "(SELECT * FROM {table_a} WHERE {condition_sentence_a}) as a "\
        #       "{join_method} {table_b} as b " \
        #       "ON a.{joint_key_a} = b.{joint_key_b} " \
        #       .format(targets=targets_sentence, table_a=table_a, table_b=table_b, joint_key_a=joint_key_a,
        #               joint_key_b=joint_key_b, join_method=method, condition_sentence_a=condition_sentence_a, condition_sentence = condition_sentence)
        sql = "SELECT {targets} "\
              "FROM {table_a} AS a "\
              "{join_method} {table_b} AS b "\
              "ON a.{joint_key_a} = b.{joint_key_b} "\
              "WHERE {condition_sentence};"\
              .format(targets=targets_sentence, table_a=table_a, table_b=table_b, joint_key_a=joint_key_a,
                    joint_key_b=joint_key_b, join_method=method, condition_sentence_a=condition_sentence_a,
                    condition_sentence=condition_sentence)
        # sql = sql % condition_values
        # print(sql)
        try:
            result = cx.execute(sql, condition_values).fetchall()

            # print(result)
        except Exception as e:
            print('查找失败')
            result = None
            print(e)
    else:
        sql = "select {targets} "\
              "from {table_a} a "\
              "{join_method} {table_b} b "\
              "on a.{joint_key_a} = b.{joint_key_b} "\
              .format(targets=targets_sentence, table_a=table_a, table_b=table_b, join_method=method,
                      joint_key_a=joint_key_a, joint_key_b=joint_key_b)
        # print(sql)
        try:
            result = cx.execute(sql).fetchall()
            # print(result)
        except Exception as e:
            print('查找失败')
            result = None
            print(e)
    return result

@fromRemote
def getLinesFromTable(table_name, conditions:dict, columns_required:list = None, order: list = None ,ascending:bool = True):
    #提取表Key信
    col_info = cx.execute('pragma table_info("{view}")'.format(view=table_name)).fetchall()
    begin_sql = time.perf_counter()
    col_name = [item[1] for item in col_info]
    col_name_result = tuple(col_name)

    #生成SQL语句
    # todo:这一段应该用cython改写
    if not conditions:
        sql = "select distinct * from %s "%(table_name)
    else:
        #多key多类型（iterable or else）混合查询语句
        condition_key_expression = []
        condition_values = []
        for k, v in conditions.items():
            if isinstance(v, list) or isinstance(v, tuple):
                condition_key_expression.append(k + ' in {} COLLATE NOCASE')
                condition_values.append(tuple(v))
            elif isinstance(v, str):
                condition_key_expression.append(k + "= '{}' COLLATE NOCASE")#字符串类型需要加上单引号
                condition_values.append(v)
            else:
                condition_key_expression.append(k + '= {} COLLATE NOCASE')
                condition_values.append(v)
        conditions_sentence = ' and '.join(condition_key_expression)# key1 = ? and key2 = ? ...
        sql = "select distinct * from {table_name} where {condition} ".format( table_name = table_name,condition = conditions_sentence)
        sql = sql.format(*condition_values)
        # print(*condition_values)
        sql = sql.replace(',)', ')')#当list里面只有一个元素时，转换成python的tuple会出现多了一个','，需要去掉

    if  columns_required:
        column_place_holders = ['%s' for i in columns_required]
        place_holder_str = ', '.join(column_place_holders)
        sql = sql.replace('*', place_holder_str)
        # print(sql)
        # print(tuple(columns_required))
        sql = sql % tuple(columns_required)
    if order:
        if ascending:
            sql += ' order by {} asc'.format(', '.join(order))
        else:
            sql += ' order by {} desc'.format(', '.join(order))
    # print(sql)
    end_sql = time.perf_counter()
    try:
        result = cx.execute(sql).fetchall()
        # print(result)
        print('查找成功')
    except Exception as e:
        print('查找失败')
        result = None
        print(e)
    end_select = time.perf_counter()
    # print('生成sql:',end_sql - begin_sql)
    # print('查询：',end_select - end_sql)
    # cx.commit()
    #一旦查找失败，此处会报错
    if columns_required:#
        result.append(tuple(columns_required))
    else:
        result.append(col_name_result)
    return result

def getLikeLinesFromTable(table_name,like_conditions:dict, exact_conditions:dict=None, columns_required:list = None, order: list = None ,ascending:bool = True):
    #提取表Key信
    col_info = cx.execute('pragma table_info("{view}")'.format(view=table_name)).fetchall()
    begin_sql = time.perf_counter()
    col_name = [item[1] for item in col_info]
    col_name_result = tuple(col_name)

    exact_condition_key_expression = []
    exact_condition_values = []
    like_condition_key_expression = []
    like_condition_values = []

    for k, v in like_conditions.items():
        print(v)
        if not isinstance(v, str):
            raise ValueError('item assigned to "LIKE" must be a str')
        if isinstance(v, list) or isinstance(v, tuple):
            temp_like_condition_key_expression = []
            for item in v:
                if not isinstance(item, str):
                    raise ValueError('item assigned to "LIKE" must be a str')
                temp_like_condition_key_expression.append(k + " LIKE '%{}%' COLLATE NOCASE")
                like_condition_values.append(item)
            like_condition_key_expression.append(
                "({})".format(' or '.join(temp_like_condition_key_expression)))  # 单独生成一段'or' 连接的LIKE语句
        else:
            like_condition_key_expression.append(k + " LIKE '%{}%' COLLATE NOCASE")  # 字符串类型需要加上单引号
            like_condition_values.append(v)
    like_condition_key_sentence = ' and '.join(like_condition_key_expression)  # key1 LIKE %{}% and key2 LIKE %{}% and (key3 LIKE %{}% or Key3 LIKE %{}%) and key4 LIKE %{}%  ...

    if exact_conditions:
        #多key多类型（iterable or else）混合查询语句
        for k, v in exact_conditions.items():
            if isinstance(v, list) or isinstance(v, tuple):
                exact_condition_key_expression.append(k + ' in {} COLLATE NOCASE')
                exact_condition_values.append(tuple(v))
            elif isinstance(v, str):
                exact_condition_key_expression.append(k + "= '{}' COLLATE NOCASE")#字符串类型需要加上单引号
                exact_condition_values.append(v)
            else:
                exact_condition_key_expression.append(k + '= {} COLLATE NOCASE')
                exact_condition_values.append(v)
    exact_condition_key_sentence = ' and '.join(exact_condition_key_expression) # key1 = {} and key2 = {} ...

    condition_key_sentence =  ' and '.join([exact_condition_key_sentence, like_condition_key_sentence]) if exact_condition_key_sentence else like_condition_key_sentence
    condition_values =  like_condition_values + exact_condition_values
    sql = "select distinct * from {table_name} where {condition} ".format( table_name = table_name,
                                                                           condition = condition_key_sentence)
    sql = sql.format(*condition_values)
    # print(*condition_values)
    sql = sql.replace(',)', ')')#当list里面只有一个元素时，转换成python的tuple会出现多了一个','，需要去掉

    if not like_conditions or exact_conditions:
        sql = "select distinct * from %s "%(table_name)

    if  columns_required:
        column_place_holders = ['%s' for i in columns_required]
        place_holder_str = ', '.join(column_place_holders)
        sql = sql.replace('*', place_holder_str)
        sql = sql % tuple(columns_required)
    if order:
        if ascending:
            sql += ' order by {} asc'.format(', '.join(order))
        else:
            sql += ' order by {} desc'.format(', '.join(order))
    # print(sql)
    end_sql = time.perf_counter()
    try:
        result = cx.execute(sql).fetchall()
        # print(result)
        # print('查找成功')
    except Exception as e:
        print('查找失败')
        result = None
        print(e)
    end_select = time.perf_counter()
    # print('生成sql:',end_sql - begin_sql)
    # print('查询：',end_select - end_sql)
    # cx.commit()
    #一旦查找失败，此处会报错
    if not result:
        print('未找到')
        result = []
    else:
        print('查找成功')
        result.append(col_name_result)
    return result

def updateSqliteCells(table_name:str, conditions:dict, update_fields:dict):
    condition_keys = list(conditions.keys())
    condition_values = list(conditions.values())
    update_field_keys = list(update_fields.keys())
    update_field_values = list(update_fields.values())
    condition_key_expression = [ key + "= ? COLLATE NOCASE" for key in condition_keys]
    conditions_sentence = ' and '.join(condition_key_expression)# key1 = ? and key2 = ? ...
    update_field_key_expression = [key + "= ? COLLATE NOCASE" for key in update_field_keys]
    update_fields_sentence = ' , '.join(update_field_key_expression)# key1 = ? and key2 = ? ...
    sql = "UPDATE {table_name} SET {update_fields} WHERE {conditions} ;"\
        .format(table_name = table_name,conditions= conditions_sentence,update_fields= update_fields_sentence)

    update_field_values.extend(condition_values)
    combined_values = tuple(update_field_values)
    print(sql,combined_values)
    result = cx.execute(sql,combined_values).fetchall()
    cx.commit()
    return result

def deleteLineFromTable(table_name: str, conditions: dict) :
    # 多key多类型（iterable or else）混合查询语句
    condition_keys = list(conditions.keys())
    condition_values = list(conditions.values())
    condition_key_expression = []
    for i in range(len(condition_keys)) :
        if isinstance(condition_values[i], list) or isinstance(condition_values[i], tuple) :
            condition_key_expression.append(condition_keys[i] + ' in {} COLLATE NOCASE')
            condition_values[i] = tuple(condition_values[i])
        elif isinstance(condition_values[i], str) :
            condition_key_expression.append(condition_keys[i] + "= '{}' COLLATE NOCASE")
        else :
            condition_key_expression.append(condition_keys[i] + '= {} COLLATE NOCASE')
    conditions_sentence = ' and '.join(condition_key_expression)  # key1 = ? and key2 = ? ...
    sql = "DELETE from {table_name} where {condition} ".format(table_name=table_name,
                                                                          condition=conditions_sentence)
    sql = sql.format(*condition_values)
    sql = sql.replace(',)', ')')  # 当list只有1个元素时，生成的tuple里面也会有一个逗号，需要删除掉
    cx.execute(sql)
    cx.commit()

def getSqliteCells(table_name:str, conditions:dict, required_fields:list):
    condition_keys = list(conditions.keys())
    condition_values = tuple(conditions.values())
    condition_key_expression = [ key + "= ? COLLATE NOCASE" for key in condition_keys]
    conditions_sentence = ' and '.join(condition_key_expression)# key1 = ? and key2 = ? ...
    required_fields_sentence = ",".join(required_fields)
    sql = "select {columns} from {table_name} where {condition};".format(columns = required_fields_sentence, table_name= table_name,condition = conditions_sentence)
    result = cx.execute(sql,condition_values).fetchall()
    return result

def drugData(func_name:str, *args, **kwargs):
    global cx
    db_file = userDir.getDrugDataBase()
    tmp = cx
    cx = sqlite3.connect(db_file)
    func = globals()[func_name]
    # print(func)
    result = func(*args, **kwargs)
    cx.close()
    cx = tmp
    return result


if __name__ == '__main__':
    # tables = ['client_log','clients', 'manufacturers', 'product_market_info', 'product_marketing','product_supply','product_supply_detail','proj_list',
    #           'project_meeting_log','project_memo_log','supplier_log','suppliers','tasks','thera_area']
    # for table in tables:
    #     createUpdateTrigger(table)

    #condition = {'_id':'a0000001'}
    # a = getLinesFromTable('proj_current_task',{'client':['东莞东阳光']})

    sqlite3.connect(path+'db.sqlite3')
