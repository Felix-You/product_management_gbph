from ID_Generate import Snow
import time
import pandas as pd
import datetime
import ConnSqlite as csqlt
import sqlite3
# cx = sqlite3.connect('db.sqlite3')

def getID(startLable:str):
    s = Snow(startLable)
    return s.get()

# 1440751417.283 --> '2015-08-28 16:43:37.283'
def timestamp2string(timeStamp):
    try:
        d = datetime.datetime.fromtimestamp(timeStamp)
        str1 = d.strftime("%Y-%m-%d %H:%M:%S")
        # 2015-08-28 16:43:37'
        return str1
    except Exception as e:
        print(e)
        return ''

def parseText_Datetime_Log(text:str) :  # 解析单元格内容
    # print('读取', text)
    tmp_list = text.split('<log>')
    history_log = []
    # print('分割记录', tmp_list)
    for tmp in tmp_list :  # 遍历初步分割的记录列表
        if tmp in ['','nan'] : continue
        tmp_1 = tmp.replace('</log>','')  # 清理单条记录
        if tmp_1.find('<ts>') == -1 :  # 处理没有时间的记录
            history_log.append(('2020-01-01 00:00:00',tmp_1))
        else :  # 处理包含时间的记录
            tmp_1_list = tmp_1.split('</ts>')
            timestamp0 = float(tmp_1_list[0].replace('<ts>',''))
            time0 = timestamp2string(timestamp0)
            history_log.append((time0,tmp_1_list[1]))
    return history_log

#注意！！！使用之前一定要先把province，city信息导出来！！
def dumpClients(filepath:str):
#注意！！！使用之前一定要先把province，city信息导出来！！
    #csqlt.insertSqlite('clients',row)
    clients = pd.read_excel(filepath)
    s = Snow('cl')
    for i in range(clients.shape[0]):
        id = s.get()
        row = {'client_name': clients.iloc[i,1],
               'client_id':id,
               'log_table':clients.iloc[i,6],
               'log_num':0}
        print(row)
        csqlt.insertSqlite('clients',row)


def dumpStatus(filepath1,filepath2):
    projects = pd.read_excel(filepath1,keep_default_na=False)
    projection = pd.read_excel(filepath2,keep_default_na=False)
    s = Snow('st')
    for i in range(projects.shape[0]):
        proj_id = projects.iloc[i,28]
        proj_status = projects.iloc[i,2]
        proj_code = projection[projection['标签'] == proj_status]['code']
        int(proj_code)
        row = {'conn_project_id': proj_id,
               'status_code': int(proj_code),
               '_id':s.get()}
        csqlt.insertSqlite('proj_status_log',row)

def dumpProjects(filepath:str):
    projects = pd.read_excel(filepath,keep_default_na=False)
    for i in range(projects.shape[0]):
        client_id = csqlt.getLineFromSqlite('clients',{'short_name':projects.iloc[i,9]})[0][0]
        product = projects.iloc[i,0]
        product_fetch = csqlt.getLineFromSqlite('product_supply', {'name_cn':product})
        if len(product_fetch) == 0:
            product_id = None
        else:
            product_id = product_fetch[0][0]

        clear_chance = bool(projects.iloc[i,19]) if projects.iloc[i,19] != '' else False
        highlight = bool(projects.iloc[i,18]) if projects.iloc[i,18] != '' else False
        in_act= bool(projects.iloc[i,5]) if projects.iloc[i,5] != '' else False
        order_tobe = bool(projects.iloc[i,20]) if projects.iloc[i,20] != '' else False
        row = {'_id': projects.iloc[i,28],'product': projects.iloc[i,0],'product_id': product_id,
               'current_task_num': projects.iloc[i,12] if projects.iloc[i,12] != '' else 0,#
               'client': projects.iloc[i,9],'client_id': client_id,'log_table': 'project_meeting_log',
               'status_table': 'project_status','task_table': 'tasks','in_act': in_act,
               'clear_chance': clear_chance,'order_tobe': order_tobe,'highlight':highlight}
        csqlt.insertSqlite('proj_list',row)
    pass

def dumpProductsSupply(filepath:str):
    products = pd.read_excel(filepath,keep_default_na=False)
    s = Snow('ps')
    for i in range(products.shape[0]):
        _id = s.get()
        name_cn = products.iloc[i,1]
        name_en = products.iloc[i,2]
        dosage_forms = products.iloc[i,3]
        supplier = products.iloc[i,5]
        print(name_cn,supplier)
        supplier_back = csqlt.getLineFromSqlite('suppliers',{'name':supplier})
        supplier_id = supplier_back[0][0]
        manufacturer = products.iloc[i,5]
        country = products.iloc[i,4]
        manufacturer_id =csqlt.getLineFromSqlite('manufacturers',{'name':manufacturer, 'country': country})[0][0]
        thera_area =  products.iloc[i,0]
        thera_area_code = csqlt.getLineFromSqlite('thera_area', {'area_name':thera_area})[0][2]
        CA = products.iloc[i,9]
        CA_bool = False
        if CA =='通过':
            CA_bool = True
        reg_status = products.iloc[i,11]

        row = {'_id':_id,'name_cn':name_cn,'name_en':name_en,'chem_entity':name_cn,'thera_area_code':thera_area_code,
               'dosage_forms':dosage_forms,'supplier_id':supplier_id,'manufacturer_id':manufacturer_id,'reg_status':reg_status,
               'reg_spec':products.iloc[i,6],'reg_num':products.iloc[i,7],'US_DMF':products.iloc[i,8],'CA':CA_bool,
               'CEP':products.iloc[i,10],'file_table':'global_file_path','detail_table':'product_supply_detail'}
        csqlt.insertSqlite('product_supply',row)
    pass

def dumpProjectTasks(filepath:str):
    rows = pd.read_excel(filepath,keep_default_na=False)
    print(rows)
    s = Snow('ts')
    for i in range(rows.shape[0]):
        tasks = rows.iloc[i, 14]
        if tasks == '':
            continue
        task_list= parseText_Datetime_Log(tasks)
        conn_project_id = rows.iloc[i, 28]
        for j in range(len(task_list)):
            id = s.get()
            creat_time = task_list[j][0]
            task_desc = task_list[j][1]
            is_critical = True if j == len(task_list)-1 and rows.iloc[i,3] =='2.紧急' else False
            switch = True if j == len(task_list)-1 and rows.iloc[i,6] else False
            officejob_type = rows.iloc[i,22] if j == len(task_list)-1 and rows.iloc[i,22] !='' else 'A'
            inter_order_weight = j+1
            row = {'_id':id,'conn_project_id':conn_project_id,'conn_project_table':'proj_list','task_desc':task_desc,
            'create_time':creat_time,'is_critical':is_critical,'switch':switch,
            'officejob_type':officejob_type,'on_pending':False,
            'destroyed':False,'inter_order_weight':inter_order_weight}
            csqlt.insertSqlite('tasks',row)
    pass

def dumpTheraArea(filepath:str):
    area = pd.read_excel(filepath)
    s = Snow('ta')
    for i in range(area.shape[0]):
        id = s.get()
        row = {'_id':id, 'area_name':area.iloc[i,0], 'code':int(area.iloc[i,1])}
        print(type(row['_id']))
        csqlt.insertSqlite('thera_area',row)
    pass

def dumpSuppliers(filepath:str):
    suppliers = pd.read_excel(filepath)
    s = Snow('sp')
    for i in range(suppliers.shape[0]):
        id = s.get()
        row = {'_id':id, 'name':suppliers.iloc[i,0],'log_table':'supplier_log','product_table':'product_supply'}
        csqlt.insertSqlite('suppliers',row)
    pass

def dumpManufacturers(filepath:str):
    manufacturers = pd.read_excel(filepath)
    s = Snow('mn')
    for i in range(manufacturers.shape[0]):
        id = s.get()
        row = {'_id':id, 'name':manufacturers.iloc[i,1],'country':manufacturers.iloc[i,0],'log_table':'supplier_log','product_table':'product_supply'}
        csqlt.insertSqlite('manufacturers',row)
    pass

def dumpProjectMeetingLog(filepath:str):
    rows = pd.read_excel(filepath,keep_default_na=False)
    print(rows)
    s = Snow('mt')
    for i in range(rows.shape[0]):
        meetings = rows.iloc[i, 1]
        if meetings == '':
            continue
        meeting_list= parseText_Datetime_Log(meetings)
        conn_project_id = rows.iloc[i, 28]
        for j in range(len(meeting_list)):
            id = s.get()
            create_time = meeting_list[j][0]
            log_content = meeting_list[j][1]
            inter_order_weight = j
            row = {'_id':id,'create_time': create_time,'meeting_desc':log_content,
                   'conn_project_id':conn_project_id,'inter_order_weight':inter_order_weight}
            csqlt.insertSqlite('project_meeting_log',row)
    pass

def dumpProjectMemoLog(filepath:str):
    rows = pd.read_excel(filepath,keep_default_na=False)
    print(rows)
    s = Snow('mm')
    for i in range(rows.shape[0]):
        meetings = rows.iloc[i, 8]
        if meetings == '':
            continue
        meeting_list= parseText_Datetime_Log(meetings)
        conn_project_id = rows.iloc[i, 28]
        for j in range(len(meeting_list)):
            id = s.get()
            create_time = meeting_list[j][0]
            log_content = meeting_list[j][1]
            inter_order_weight = j
            row = {'_id':id,'create_time': create_time,'memo_desc':log_content,
                   'conn_project_id':conn_project_id,'inter_order_weight':inter_order_weight}
            csqlt.insertSqlite('project_memo_log',row)
    pass

if __name__ == '__main__':
    #print(parseText_Datetime_('<log><ts>1577808000.0</ts>1）提供ROS。2）如果东阳光增加我们做供应商，东阳光供应欧美市场的需求量，可否直接向VNAI采购？</log><log><ts>1621351680.868678</ts>反馈VNAI相关原料信息给物控部存档。</log><log><ts>1621351680.868678</ts>反馈VNAI相关原料信息给物控部存档。</log>'))
    #注意！！！使用之前一定要先把province，city信息导出来！！dumpClients('E:\\SourceCodes\\product_management_web\\migrate_by_hand\\1.xlsx')
    #dumpTheraArea('E:\\SourceCodes\\product_management_web\\migrate_by_hand\\thera_areas.xlsx')
    #dumpSuppliers('E:\\SourceCodes\\product_management_web\\migrate_by_hand\\suppliers2.xlsx')
    #dumpManufacturers('E:\\SourceCodes\\product_management_web\\migrate_by_hand\\manufacturers2.xlsx')
    # dumpProductsSupply('E:\\SourceCodes\\product_management_web\\migrate_by_hand\\product_supply_release2.xlsx')
    # dumpProjects('E:\\SourceCodes\\product_management_web\\migrate_by_hand\\my_projects.xlsx')
    # dumpProjectTasks('E:\\SourceCodes\\product_management_web\\migrate_by_hand\\my_projects.xlsx')
    # dumpProjectMeetingLog('E:\\SourceCodes\\product_management_web\\migrate_by_hand\\my_projects.xlsx')
    # dumpProjectMemoLog('E:\\SourceCodes\\product_management_web\\migrate_by_hand\\my_projects.xlsx')
    dumpStatus('E:\\SourceCodes\\product_management_web\\migrate_by_hand\\my_projects.xlsx',
               'E:\\SourceCodes\\product_management_web\\migrate_by_hand\\tag_projection.xlsx')

    pass