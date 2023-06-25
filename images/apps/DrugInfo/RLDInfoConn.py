'''CREATE TABLE rld_official (
    _id                         PRIMARY KEY
                                UNIQUE
                                NOT NULL,
    serial_num                  UNIQUE
                                NOT NULL,
    generic_name  VARCHAR (100) NOT NULL,
    en_trade_name VARCHAR (100) NOT NULL,
    specification VARCHAR (100) NOT NULL,
    dosage_form   VARCHAR (30)  NOT NULL,
    holder        VARCHAR (100) NOT NULL,
    desc_1        TEXT,
    desc_2        TEXT,
    release_date  DATE          NOT NULL,
    update_date   DATE
);'''
import sys

import openpyxl,csv, datetime
import ConnSqlite as CS

def load_rld_from_xlsx(file_name:str) :
    sheet = openpyxl.load_workbook(filename= file_name,data_only=True)
    sheet = sheet.active.values
    excel_header = next(sheet)
    field_names = CS.drugData('getTableFields','rld_official')
    print(field_names)
    i = 0
    from ID_Generate import Snow
    id_get = Snow('rld')
    def trans_date(date:str):
        if not date:
            return None
        time_list = date.split('.')
        if len(time_list[1]) == 1:
            time_list[1] = '0' + time_list[1]
        return '-'.join(time_list)
    for line in sheet:
        _id = id_get.get()
        values = (_id,) + line
        key_values = dict(zip(field_names,values))
        for key in key_values.keys():
            if key_values[key] is not None:
                key_values[key] = str(key_values[key]).strip()
        key_values['release_date'] = trans_date(key_values['release_date'])
        key_values['update_date'] = trans_date(key_values['update_date'])
        # key_values['release_date'] = time.strftime('YYYY-MM-DD',key_values['release_date'].strip())
        # print(key_values)
        CS.drugData('upsertSqlite','rld_official',key_values.keys(),key_values.values())
        # i += 1
        # if i > 50 :
        #     break


def make_map_table_atc_rld():
    # row_count = CS.drugData('getTableRowCount', 'atc_ddd')
    names = CS.drugData('getLinesFromTable', 'atc_ddd', conditions = {}, columns_required = ['atc_name','atc_code'])
    # print(names)
    for name in names:
        rlds = CS.drugData('getLikeLinesFromTable', 'rld_official', like_conditions = {'en_trade_name':name[0],})
        if rlds:
            field_names = rlds.pop()
        for rld in rlds:
            rld_serial = rld[1]
            atc_code = name[1]
            data = {'rld_serial': rld_serial, 'atc_code': atc_code}
            CS.drugData('insertSqlite', 'map_atc_rld', data)

        # print(rlds)

    # for i in range(row_count):
    pass

def make_atc_rld_csv():
    from ConnSqlite import c_drug
    rows = c_drug.execute(
        'SELECT * FROM '
            'atc_ddd a '
        ' INNER JOIN '
            'map_atc_rld m '
        ' ON '
            'a.atc_code = m.atc_code'
        ' INNER JOIN '
            'rld_official r'
        ' ON '
            'm.rld_serial = r.serial_num'
    ).fetchall()
    with open('../../workfiles/atc_rld_map.csv', 'w',encoding='u8', newline='') as f:
        workbook = csv.writer(f)
        i = 0
        for row in rows:
            print('第%s行：'%i)
            print(row)
            row = list(row)
            row[13] = row[13] +'\t'
            workbook.writerow(row )
            i += 1
            # if i > 20:
            #     break

    # print(rows)


def show_clipboard():
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)

    clipboard = QApplication.clipboard()
    clipboard.dataChanged.connect(lambda : print(clipboard.mimeData().data('text/html').data().decode('utf-8')))
    # print(clipboard.mimeData().data('text/plain'))
    app.exec_()
    # app.exit(0)

if __name__ == '__main__':
    # load_rld_from_xlsx('../../workfiles/rld_61.xlsx')
    # row_count = CS.drugData('getTableRowCount', 'rld_official')
    # print(row_count)
    # make_map_table_atc_rld()
    # make_atc_rld_csv()
    show_clipboard()