import sqlite3
from abc import abstractmethod
from abc import ABC
from itertools import chain
import ConnSqlite as CS
import FilePathInit

drug_db_file = FilePathInit.DirManager.getDrugDataBase()
if not drug_db_file:
    print('未找到药物信息数据库文件')
c_drug = sqlite3.connect(drug_db_file)


class Repository(ABC):
    HOST = None
    PORT = None
    CONNECTION = None

    # @abstractmethod
    # def getBasicData(self):
    #     pass

    @abstractmethod
    @classmethod
    def updateCells(cls, table_name: str, conditions: dict, update_fields: dict):
        pass

    @classmethod
    @abstractmethod
    def getLineCells(cls, table_name: str, conditions: dict, required_fields: list):
        pass

    @classmethod
    @abstractmethod
    def upsertLine(cls, table, keys: list, values: list):
        pass

    @classmethod
    @abstractmethod
    def getLineFromTable(cls, table_name: str, condition: dict):
        pass

    @classmethod
    @abstractmethod
    def getLinesFromTable(cls, table_name, conditions: dict, columns_required: list = None, order: list = None,
                          ascending: bool = True):
        pass

    @classmethod
    @abstractmethod
    def deletLineFromTable(cls, table_name: str, conditions: dict):
        pass

    @classmethod
    @abstractmethod
    def getLikeLinesFromTable(cls, table_name, like_conditions: dict, exact_conditions: dict = None,
                              columns_required: list = None, order: list = None, ascending: bool = True):
        pass

    @classmethod
    @abstractmethod
    def insertLine(cls, table, row_data: dict):
        pass

    @classmethod
    @abstractmethod
    def insertMultiLines(cls, table, keys: list[str], lines: list[list]):
        pass


class SQLiteRepository(Repository):
    CONNECTION = None

    @classmethod
    def updateCells(cls, table_name: str, conditions: dict, update_fields: dict):
        condition_keys = list(conditions.keys())
        condition_values = list(conditions.values())
        update_field_keys = list(update_fields.keys())
        update_field_values = list(update_fields.values())
        condition_key_expression = [key + "= ? COLLATE NOCASE" for key in condition_keys]
        conditions_sentence = ' and '.join(condition_key_expression)  # key1 = ? and key2 = ? ...
        update_field_key_expression = [key + "= ? COLLATE NOCASE" for key in update_field_keys]
        update_fields_sentence = ' , '.join(update_field_key_expression)  # key1 = ? and key2 = ? ...
        sql = "UPDATE {table_name} SET {update_fields} WHERE {conditions} ;".format(table_name=table_name,
                                                                                    conditions=conditions_sentence,
                                                                                    update_fields=update_fields_sentence)
        update_field_values.extend(condition_values)
        combined_values = tuple(update_field_values)
        print(sql, combined_values)
        result = cls.CONNECTION.execute(sql, combined_values).fetchall()
        cls.CONNECTION.commit()
        return result

    @classmethod
    def getLineCells(cls, table_name: str, conditions: dict, required_fields: list):
        condition_keys = list(conditions.keys())
        condition_values = tuple(conditions.values())
        condition_key_expression = [key + "= ? COLLATE NOCASE" for key in condition_keys]
        conditions_sentence = ' and '.join(condition_key_expression)  # key1 = ? and key2 = ? ...
        required_fields_sentence = ",".join(required_fields)
        sql = "select {columns} from {table_name} where {condition};".format(columns=required_fields_sentence,
                                                                             table_name=table_name,
                                                                             condition=conditions_sentence)
        result = cls.CONNECTION.execute(sql, condition_values).fetchall()
        return result

    @classmethod
    def upsertLine(cls, table, keys: list, values: list):
        cursor = cls.CONNECTION.cursor()

        keys_expr = ', '.join(keys)
        values_expr = ', '.join(["?"] * len(values))

        update_keys = ['{key}=excluded.{key}'.format(key=key) for key in keys]
        update_keys_expr = ', '.join(update_keys)

        sql = 'insert into {table} ({keys}) values ({values}) '\
              'on conflict(_id) do update set {update_keys_expr}'.\
            format(table=table, keys=keys_expr, values=values_expr, update_keys_expr=update_keys_expr)
        try:
            # print(tuple(row_data.values()))
            # print(sql)
            cursor.execute(sql, tuple(values))
            # print('保存成功')
            cls.CONNECTION.commit()
            return True
        except Exception as e:
            print(sql)
            print('插入失败，回滚')
            print(e)

            cls.CONNECTION.rollback()
            return False

    @classmethod
    def getLineFromTable(cls, table_name: str, condition: dict):
        result = []
        if not condition:
            sql = "select * from %s" % (table_name)
            result = cls.CONNECTION.execute(sql).fetchall()
        else:
            condition_keys = list(condition.keys())
            condition_values = list(condition.values())
            condition_key_expression = []
            for i in range(len(condition_keys)):
                if isinstance(condition_values[i], list) or isinstance(condition_values[i], tuple):
                    condition_key_expression.append(condition_keys[i] + ' in ? COLLATE NOCASE')
                    condition_values[i] = tuple(condition_values[i])
                else:
                    condition_key_expression.append(condition_keys[i] + '= ? COLLATE NOCASE')
            conditions_sentence = ' and '.join(condition_key_expression)  # key1 = ? and key2 = ? ...
            sql = "select * from {table_name} where {condition};".format(table_name=table_name,
                                                                         condition=conditions_sentence)
            try:
                # print(tuple(row_data.values()))
                print(sql, tuple(condition_values))
                result = cls.CONNECTION.execute(sql, condition_values).fetchall()

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

        col_info = cls.CONNECTION.execute('pragma table_info("{}")'.format(table_name)).fetchall()
        col_name = []
        for item in col_info:
            col_name.append(item[1])
        col_name_result = tuple(col_name)
        result.append(col_name_result)
        return result

    @classmethod
    def getLinesFromTable(cls, table_name, conditions: dict, columns_required: list = None, order: list = None,
                          ascending: bool = True):
        # 提取表Key信
        col_info = cls.CONNECTION.execute('pragma table_info("{view}")'.format(view=table_name)).fetchall()
        col_name = [item[1] for item in col_info]
        col_name_result = tuple(col_name)

        # 生成SQL语句
        # todo:这一段应该用cython改写
        if not conditions:
            sql = "select distinct * from %s " % (table_name)
        else:
            # 多key多类型（iterable or else）混合查询语句
            condition_key_expression = []
            condition_values = []
            for k, v in conditions.items():
                if isinstance(v, list) or isinstance(v, tuple):
                    condition_key_expression.append(k + ' in {} COLLATE NOCASE')
                    condition_values.append(tuple(v))
                elif isinstance(v, str):
                    condition_key_expression.append(k + "= '{}' COLLATE NOCASE")  # 字符串类型需要加上单引号
                    condition_values.append(v)
                else:
                    condition_key_expression.append(k + '= {} COLLATE NOCASE')
                    condition_values.append(v)
            conditions_sentence = ' and '.join(condition_key_expression)  # key1 = ? and key2 = ? ...
            sql = "select distinct * from {table_name} where {condition} ".format(table_name=table_name,
                                                                                  condition=conditions_sentence)
            sql = sql.format(*condition_values)
            # print(*condition_values)
            sql = sql.replace(',)', ')')  # 当list里面只有一个元素时，转换成python的tuple会出现多了一个','，需要去掉

        if columns_required:
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
        try:
            result = cls.CONNECTION.execute(sql).fetchall()
            # print(result)
            print('查找成功')
        except Exception as e:
            print('查找失败')
            result = None
            print(e)
        # print('生成sql:',end_sql - begin_sql)
        # print('查询：',end_select - end_sql)
        # cx.commit()
        # 一旦查找失败，此处会报错
        if columns_required:  #
            result.append(tuple(columns_required))
        else:
            result.append(col_name_result)
        return result
        pass

    @classmethod
    def deletLineFromTable(cls, table_name: str, conditions: dict):
        # 多key多类型（iterable or else）混合查询语句
        condition_keys = list(conditions.keys())
        condition_values = list(conditions.values())
        condition_key_expression = []
        for i in range(len(condition_keys)):
            if isinstance(condition_values[i], list) or isinstance(condition_values[i], tuple):
                condition_key_expression.append(condition_keys[i] + ' in {} COLLATE NOCASE')
                condition_values[i] = tuple(condition_values[i])
            elif isinstance(condition_values[i], str):
                condition_key_expression.append(condition_keys[i] + "= '{}' COLLATE NOCASE")
            else:
                condition_key_expression.append(condition_keys[i] + '= {} COLLATE NOCASE')
        conditions_sentence = ' and '.join(condition_key_expression)  # key1 = ? and key2 = ? ...
        sql = "DELETE from {table_name} where {condition} ".format(table_name=table_name,
                                                                   condition=conditions_sentence)
        sql = sql.format(*condition_values)
        sql = sql.replace(',)', ')')  # 当list只有1个元素时，生成的tuple里面也会有一个逗号，需要删除掉
        cls.CONNECTION.execute(sql)
        cls.CONNECTION.commit()
        pass

    @classmethod
    def getLikeLinesFromTable(cls, table_name, like_conditions: dict, exact_conditions: dict = None,
                              columns_required: list = None, order: list = None, ascending: bool = True):
        # 提取表Key信
        col_info = cls.CONNECTION.execute('pragma table_info("{view}")'.format(view=table_name)).fetchall()
        # begin_sql = time.perf_counter()
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
        like_condition_key_sentence = ' and '.join(
            like_condition_key_expression)  # key1 LIKE %{}% and key2 LIKE %{}% and (key3 LIKE %{}% or Key3 LIKE %{}%) and key4 LIKE %{}%  ...

        if exact_conditions:
            # 多key多类型（iterable or else）混合查询语句
            for k, v in exact_conditions.items():
                if isinstance(v, list) or isinstance(v, tuple):
                    exact_condition_key_expression.append(k + ' in {} COLLATE NOCASE')
                    exact_condition_values.append(tuple(v))
                elif isinstance(v, str):
                    exact_condition_key_expression.append(k + "= '{}' COLLATE NOCASE")  # 字符串类型需要加上单引号
                    exact_condition_values.append(v)
                else:
                    exact_condition_key_expression.append(k + '= {} COLLATE NOCASE')
                    exact_condition_values.append(v)
        exact_condition_key_sentence = ' and '.join(exact_condition_key_expression)  # key1 = {} and key2 = {} ...

        condition_key_sentence = ' and '.join([exact_condition_key_sentence,
                                               like_condition_key_sentence]) if exact_condition_key_sentence else like_condition_key_sentence
        condition_values = like_condition_values + exact_condition_values
        sql = "select distinct * from {table_name} where {condition} ".format(table_name=table_name,
                                                                              condition=condition_key_sentence)
        sql = sql.format(*condition_values)
        # print(*condition_values)
        sql = sql.replace(',)', ')')  # 当list里面只有一个元素时，转换成python的tuple会出现多了一个','，需要去掉

        if not like_conditions or exact_conditions:
            sql = "select distinct * from %s " % (table_name)

        if columns_required:
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
        # end_sql = time.perf_counter()
        try:
            result = cls.CONNECTION.execute(sql).fetchall()
            # print(result)
            # print('查找成功')
        except Exception as e:
            print('查找失败')
            result = None
            print(e)
        # end_select = time.perf_counter()
        # print('生成sql:',end_sql - begin_sql)
        # print('查询：',end_select - end_sql)
        # cx.commit()
        # 一旦查找失败，此处会报错
        if not result:
            print('未找到')
            result = []
        else:
            print('查找成功')
            result.append(col_name_result)
        return result
        pass

    @classmethod
    def insertLine(cls, table, row_data: dict):
        cursor = cls.CONNECTION.cursor()
        keys = ', '.join(row_data.keys())
        values = ', '.join(["?"] * len(row_data))
        sql = 'insert into {table} ({keys}) values ({values}) '.format(table=table, keys=keys, values=values)
        try:
            # print(tuple(row_data.values()))
            cursor.execute(sql, tuple(row_data.values()))
            # print(sql)
            print(sql)
            print('插入成功')
            cls.CONNECTION.commit()
        except Exception as e:
            # print(sql)
            # print('插入失败，回滚')
            print(e)
            cls.CONNECTION.rollback()

    @classmethod
    def insertMultiLines(cls, table, keys: list[str], lines: list[list]):
        cursor = cls.CONNECTION.cursor()
        # keys = ', '.join(keys)
        len_line = len(keys)
        lines = [', '.join(line) for line in lines]
        SELECT_COLUMN = "SELECT" + ', '.join([f" ? AS {key}" for key in keys])
        LINE = ', '.join("?" for i in range(len_line))
        SELECT_OTHER_LINES = ' '.join(["UNION SELECT " + LINE for i in range(len(lines) - 1)])

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
            cls.CONNECTION.commit()
        except Exception as e:
            print(sql)
            print('插入失败，回滚')
            print(e)
            cls.CONNECTION.rollback()
        pass

    def init_db(self, ext_path='./plugins/libsimple-windows-x64/simple'):
        self.CONNECTION.enable_load_extension(True)
        self.CONNECTION.load_extension(ext_path)

    def createFTSIndex(self, table:str, keys:list[str]):
        """
        :param table: table_name of the model
        :param keys: field '_id' should NOT be included.
        :return: None
        """
        keys_str = ', '.join(keys)
        SEARCH_TABLE_SQL = f"""
        CREATE VIRTUAL TABLE IF NOT EXISTS {table}_fts USING fts5(
            {keys_str}, 
            content={table}, 
            content_rowid=_id, 
            tokenize='simple'
        );"""
        new_key_str = ', '.join(['new.' + key for key in keys])
        old_key_str = ', '.join(['old.' + key for key in keys])
        TRIGGER_SQL = f"""
        CREATE TRIGGER IF NOT EXISTS {table}_fts_i AFTER INSERT ON {table} BEGIN
          INSERT INTO {table}_fts(rowid, {keys_str}) VALUES (new._id, {new_key_str});
        END;
        CREATE TRIGGER IF NOT EXISTS {table}_fts_d AFTER DELETE ON {table} BEGIN
          INSERT INTO {table}_fts({table}_fts, rowid, {keys_str}) VALUES('delete', old._id, {old_key_str});
        END;
        CREATE TRIGGER IF NOT EXISTS {table}_fts_u AFTER UPDATE ON {table} BEGIN
          INSERT INTO {table}_fts({table}_fts, rowid, {keys_str}) VALUES('delete', old._id, {new_key_str});
          INSERT INTO {table}_fts(rowid, {keys_str}) VALUES (new._id, {new_key_str});
        END;
        """
        self.CONNECTION.execute(SEARCH_TABLE_SQL)
        self.CONNECTION.execute(TRIGGER_SQL)

    def createTable(self, table:str, keys:list[str]):
        SEARCH_TABLE_SQL = f"""
        CREATE TABLE {table} (
            _id VARCHAR PRIMARY KEY,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE,
            short_description TEXT
        )
        """



class LocalProjectRepository(SQLiteRepository):
    CONNECTION = CS.cx


class LocalDrugRepository(SQLiteRepository):
    CONNECTION = c_drug
