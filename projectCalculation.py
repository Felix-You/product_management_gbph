import math, time

import DataCenter
import GColour
from GColour import ProjectRGBColour,TaskColour
import DataView
# from numba import jit

def nan_BoolJudge(val) :  # 判断数据的布尔值
    try :
        if math.isnan(val) :
            return False
        else :
            if val in [ 'FALSE', 'False', 'false', '0', '0.0' ] :
                return False
            else :
                return bool(val)
    except :
        if val in [ 'FALSE', 'False', 'false', '0', '0.0' ] :
            return False
        else :
            return bool(val)
PROJECT_MODE_SET = [
    ('is_deal', '已成交', GColour.ProjectRGBColour.ProjecIsDeal, 255, 'nIsDeal'),
    ('order_tobe','预期订单',GColour.ProjectRGBColour.ProjectOrderTobe,255, 'nOrderTobe'),
    ('clear_chance','明确机会',GColour.ProjectRGBColour.ProjectClearChance,255, 'nClearChance'),
    ('highlight','高亮关注',GColour.ProjectRGBColour.ProjectHighlight,255, 'nHighlight'),
    ('in_act','上线跟进',GColour.ProjectRGBColour.ProjectInAct,255, 'nInAct'),
    ('to_visit','◆需拜访',(0,0,0),0, 'nToVisit')
]
PROJECT_PROGRESS_SET = progress_text = {
    'inv' : '调研',
            'ini' : '立项',
            'sst' : '小试',
            'sup' : '中试',
            'clt' : '临床',
            'fil' : '申报',
            'cmm' : '商业'}

def get_project_brief(project):
    '''

    :param project:
    :return: (可阅读的) 项目商机状态，颜色，机会阶段描述
    '''
    for item in PROJECT_MODE_SET:
        if project.__getattribute__(item[0]):
            project_mode = item[1]
            rgba = (*item[2], item[3])
            return project_mode, rgba, DataCenter.code_name_dict[project.status_code]
    else:
        return '', (0,0,0,0), DataCenter.code_name_dict[project.status_code]

def projectLogTextRender(log:list):
    if len(log) > 1:
        log.pop()
        logs = ['<font size = "3" face="Microsoft YaHei"><b>{0}</b><br />{1}<br /><font>'.format(log_item[0], log_item[1]) for log_item in log]
        logs_rendered = ''.join(logs)
        return logs_rendered
    else:
        return ''

def projectTextRender_add(client):
    '''
    所需字段信息包括：
    对输入的几个项目信息，渲染成html文本
    '''
    start = time.perf_counter()
    chance_status_filter = DataView.ChanceStatusFilterView()
    start_0 = time.perf_counter()
    text_log = ''
    #表格部分
    text_log +=  '<font face="Microsoft YaHei"><table cellpadding="2" width = "100%"> <colgroup><col span="1" style="background-color:yellow"></colgroup>'
    #<font>
    #<table> font-family:Microsoft YaHei font-size:3
    #   <tr> #表格行
    #       <td></td><td></td> 单元格
    #   </tr>
    #</table>
    #</font>
    client_to_visit = False
    for i, project in enumerate(client.projects):
        # loop_start = time.perf_counter()
        proj_text = '<tr>'
        #项目名称显示
        proj_to_visit = project.to_visit
        proj_name = project.product
        proj_id = project._id
        if proj_to_visit:
            client_to_visit = True
        if project.order_tobe:
            proj_text += '<td> <a  style="background:rgb%s;color:#000000;font-size:9pt;' \
                         'text-decoration:none;" href="%s#project"> %s </a>'%(ProjectRGBColour.ProjectOrderTobe,proj_id, proj_name)#预期订单


        elif project.clear_chance:
            proj_text += '<td> <a style="background:rgb%s;color:#000000;font-size:9pt;' \
                         'text-decoration:none;" ' \
                         'href="%s#project"> %s </a>'%(str(ProjectRGBColour.ProjectClearChance),proj_id, proj_name)#明确机会

        elif project.highlight:
            proj_text += '<td> <a style="background:rgb%s;color:#000000;font-size:9pt;' \
                         'text-decoration:none;" ' \
                         'href="%s#project"> %s </a>'%(str(ProjectRGBColour.ProjectHighlight),proj_id, proj_name)#明确机会

        elif project.in_act:
            proj_text += '<td> <a style="background:rgb%s;color:#000000;font-size:9pt;' \
                         'text-decoration:none;" ' \
                         'href="%s#project"> %s </a>'%(str(ProjectRGBColour.ProjectInAct),proj_id, proj_name)#上线跟进


        else:
            proj_text += '<td> <a style="color:#000000;text-decoration:none;font-size:9pt;" href="%s#project"> %s </a>'%(proj_id, proj_name)
        if proj_to_visit:
            to_visit_colour = 'rgb%s'%str(ProjectRGBColour.ProjectToVisit)
            proj_text += '<b style="color:%s;">◆'%to_visit_colour+'</b>'

        proj_text += '</td>'

        # 任务类型部分
        task_dict = {'A':'A上游信息',
                    'B':'B下游信息',
                    'C':'C内部决策',
                    'D':'D合同协议',
                    'E':'E文件资料'}
        chance_name = chance_status_filter.code_name_dict[project.status_code]# 项目机会部分
        critical_colour = 'transparent'
        if project.tasks:
            current_task_num = project.current_task_num if project.current_task_num and project.current_task_num <= len(project.tasks) else 1
            current_task = project.tasks[current_task_num - 1]
            #job_type = current_task.officejob_type if str(current_task.officejob_type) in "ABCDE" else "A"
            if current_task.is_critical:
                critical_colour = 'rgb%s'%str(TaskColour.TaskIsCritial)
            proj_text += '<td><span style="background:%s;font-size:8pt;"> %s </span></td>'%(critical_colour,chance_name)#紧急
        else:
            proj_text += '<td><span style="background:%s;font-size:8pt;"> %s </span></td>'%(critical_colour,chance_name)#紧急
        proj_text += '</tr>'
        text_log += proj_text
        # 项目机会部分
        #chance_name = chance_status_filter.code_name_dict[project.status_code]
        # loop_end = time.perf_counter()
        # print('loop%s'%i, loop_end - loop_start)

    start_1 = time.perf_counter()
    text_log += '</table></font>'


    #标题部分--客户名称链接
    company_name = client.short_name
    caption_log = '<p><font size = "4" face="Microsoft YaHei"><b><a style="color:#000000;text-decoration:none;" href="%s#client" > %s </a>'%(company_name, company_name)+'</b></font>'
    if client_to_visit:
        to_visit_colour = 'rgb%s'%str(ProjectRGBColour.ProjectToVisit)
        caption_log += '<b style="color:%s;">◆'%to_visit_colour+'</b>'
        # caption_log += '<font color = "green" ><b>◆</b></font>'
        # n = 1
    caption_log += '</p>'
    #合并
    html_text = caption_log + text_log
    # stop = time.perf_counter()
    # print('time before loop:', start_0 - start)
    # print('time for loops:',start_1 - start_0)
    # print ('time for all:',stop - start)
    return html_text

# @jit(nopython=True,forceobj=)
def projectTextRender_list(client):
    '''
    所需字段信息包括：
    对输入的几个项目信息，渲染成html文本
    '''
    start = time.perf_counter()
    nProject = 0
    nOrderTobe = 0
    nisDeal = 0
    nToVisit = 0
    nClearChance = 0
    nInAct = 0
    nHighlight = 0
    fraction_list = []
    chance_status_filter = DataView.ChanceStatusFilterView()
    start_0 = time.perf_counter()
    # text_log = ''
    #表格部分
    text_log =  '<font face="Microsoft YaHei"><table cellpadding="2" width = "100%"> <colgroup><col span="1" style="background-color:yellow"></colgroup>'
    #<font>
    #<table> font-family:Microsoft YaHei font-size:3
    #   <tr> #表格行
    #       <td></td><td></td> 单元格
    #   </tr>
    #</table>
    #</font>
    fraction_list.append(text_log)
    client_to_visit = False
    for i, project in enumerate(client.projects):
        loop_start = time.perf_counter()
        # proj_text = '<tr>'
        nProject += 1
        fraction_list.append('<tr>')
        #项目名称显示
        proj_to_visit = project.to_visit
        proj_name = project.product
        proj_id = project._id
        if proj_to_visit:
            client_to_visit = True
            nToVisit += 1

        if project.is_deal:
            nisDeal += 1
            proj_text = '<td> <a style="background:rgb%s;color:#000000;font-size:9pt;' \
                        'text-decoration:none;" ' \
                        'href="%s#project"> %s </a>' % (str(ProjectRGBColour.ProjecIsDeal), proj_id, proj_name)  # 上线跟进
        elif project.order_tobe:
            nOrderTobe += 1
            proj_text = '<td> <a  style="background:rgb%s;color:#000000;font-size:9pt;' \
                         'text-decoration:none;" href="%s#project"> %s </a>'%(ProjectRGBColour.ProjectOrderTobe,proj_id, proj_name)#预期订单


        elif project.clear_chance:
            nClearChance += 1
            proj_text = '<td> <a style="background:rgb%s;color:#000000;font-size:9pt;' \
                         'text-decoration:none;" ' \
                         'href="%s#project"> %s </a>'%(str(ProjectRGBColour.ProjectClearChance),proj_id, proj_name)#明确机会

        elif project.highlight:
            nHighlight += 1
            proj_text = '<td> <a style="background:rgb%s;color:#000000;font-size:9pt;' \
                         'text-decoration:none;" ' \
                         'href="%s#project"> %s </a>'%(str(ProjectRGBColour.ProjectHighlight),proj_id, proj_name)#明确机会

        elif project.in_act:
            nInAct += 1
            proj_text = '<td> <a style="background:rgb%s;color:#000000;font-size:9pt;' \
                         'text-decoration:none;" ' \
                         'href="%s#project"> %s </a>'%(str(ProjectRGBColour.ProjectInAct),proj_id, proj_name)#上线跟进
        else:
            proj_text = '<td> <a style="color:#000000;text-decoration:none;font-size:9pt;" href="%s#project"> %s </a>'%(proj_id, proj_name)
        fraction_list.append(proj_text)
        if proj_to_visit:
            to_visit_colour = 'rgb%s'%str(ProjectRGBColour.ProjectToVisit)
            proj_text = '<b style="color:%s;">◆'%to_visit_colour+'</b>'
            fraction_list.append(proj_text)
        # proj_text += '</td>'
        fraction_list.append('</td>')

        # 任务类型部分
        task_dict = {'A':'A上游信息',
                    'B':'B下游信息',
                    'C':'C内部决策',
                    'D':'D合同协议',
                    'E':'E文件资料'}
        chance_name = chance_status_filter.code_name_dict[project.status_code]# 项目机会部分

        critical_colour = 'transparent'
        if project.has_active_task_critical:
            critical_colour = 'rgb%s'%str(TaskColour.TaskIsCritial)
            proj_text = '<td><span style="background:%s;font-size:8pt;"> %s </span></td>'%(critical_colour,chance_name)#紧急
        else:
            proj_text = '<td><span style="background:%s;font-size:8pt;"> %s </span></td>'%(critical_colour,chance_name)#紧急
        fraction_list.append(proj_text)
        # proj_text += '</tr>'
        fraction_list.append('</tr>')
        # text_log += proj_text
        # 项目机会部分
        #chance_name = chance_status_filter.code_name_dict[project.status_code]
        loop_end = time.perf_counter()
        # print('loop%s'%i, loop_end - loop_start)
    # text_log += '</table></font>'
    fraction_list.append('</table></font>')

    #标题部分--客户名称链接
    caption_log_list = []
    company_name = client.short_name
    caption_log = '<p><font size = "4" face="Microsoft YaHei"><b><a style="color:#000000;text-decoration:none;" href="%s#client" > %s </a>'%(company_name, company_name)+'</b></font>'
    caption_log_list.append(caption_log)
    if client_to_visit:
        to_visit_colour = 'rgb%s'%str(ProjectRGBColour.ProjectToVisit)
        # caption_log += '<b style="color:%s;">◆'%to_visit_colour+'</b>'
        caption_log_list.append('<b style="color:%s;">◆'%to_visit_colour+'</b>')
        # caption_log += '<font color = "green" ><b>◆</b></font>'
        # n = 1
    # caption_log += '</p>'
    caption_log_list.append('</p>')
    start_1 = time.perf_counter()
    #合并
    caption_log_list.extend(fraction_list)
    html_text = ''.join(caption_log_list) #+ ''.join(fraction_list)
    stop = time.perf_counter()
    # print('time before loop:', start_0 - start)
    # print('time for loops:', start_1 - start_0)
    # print('time for unit html:', stop - start)
    return html_text,nisDeal,nProject,nOrderTobe,nClearChance,nHighlight,nInAct,nToVisit
