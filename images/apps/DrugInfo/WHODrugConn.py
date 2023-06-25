'''CREATE TABLE atc_ddd (
    _id         VARCHAR (20)  NOT NULL
                              UNIQUE
                              PRIMARY KEY,
    atc_code    VARCHAR (10)  UNIQUE
                              NOT NULL,
    atc_name    VARCHAR (100) NOT NULL,
    ddd         REAL,
    uom         VARCHAR (10),
    adm_r       VARCHAR (20),
    note        VARCHAR (100),
    atc_name_zh VARCHAR (50),
    [desc]      TEXT
);
'''
import csv
import ConnSqlite as CS


def load_atc_ddd_form_csv(file_name:str):
    with open(file_name,  encoding='gbk') as f:
        sheet = csv.reader(f)
        field_names = next(sheet)
        print(field_names)
        from ID_Generate import Snow
        id_get = Snow('atc')
        field_names = CS.drugData('getTableFields', 'atc_ddd')
        print(field_names)
        for row in sheet:
            # print(row)
            _id = id_get.get()
            values = [_id] + row[:-2]
            for i, value in enumerate(values):
                if value is not None:
                    value = str(value).strip()
                    values[i] = None if value == 'NA' or value == '' else value
            print(values)
            CS.drugData('upsertSqlite', 'atc_ddd', field_names, values)


if __name__ == '__main__':
    load_atc_ddd_form_csv('../../workfiles/ATC-DDD.csv')