from KitModels import CheckPoint, CheckPointChain

#检查点链条的评估是一个递归的过程

REAL_SOLUTION_GENERIC_CHAIN = (
    ('立项报告'),# 整体预算，
    ('rld_for_small_scale', '小试参比购买'),
    ('rld_reverse', '参比解析'),
    ('lab_material_get', '小试物料购买'),
    ('prescription_confirm', '处方确认'),
    ('quality_study', '质量研究'),
    ('factory_survey', '工厂检查'),
    ('pre_scaling_confirm', '放大前审核'),
    ('factory_transfer', '工厂对接文件'),
    ('mid_scale_material_get', '中试物料购买'),
    ('mid_scale_study', '中试研究'),
    ('validation_batch_production', '验证批生产'),
    ('microbe_test_method_validation', '生物检验方法验证'),
    ('', '稳定性、相容性、密封性考察'),
    ('整理资料'),
    ('注册申报'),
    ('site_inspection', '现场检查'),
)

FACTORY_SURVEY_CHAIN = (
    ('production_line_compatibility_check', '生产线匹配性考察'),
    ('analytical_instruments_compatibility_check', '检验设备符合性考察'),# 要有考察清单，   项目难点、原辅料清单  自身画像、整体客户画像、项目画像/ 竞争对手画像； 需要公司提供的支持
    ('')
)

FACTORY_TRANSFER_CHAIN = (
    ('委托检查项目签署'),
    ('tech_trans_files', '技术转移文件'),
    ('车间工艺放大方案'),# 由工厂起草
    ('qc_and_validation_files', '指导质量控制文件和验证方案'),
    ('生产工艺转移'),
    ('分析方法转移'),# 中试后或验证前进行分析方法转移
    ('预稳定性研究'),
)

TECH_TRANS_FILES = (
    ('技术转移方案'),
    ('生产工艺文件'),
    ('质量标准草案'),
    ('标准操作规程和记录'),
    ('中试批生产记录'),
    ('分析方法转移方案'),#中试后或验证前进行分析方法转移
    ('工艺转移方案'),
)

QC_AND_VALIDATION_FILES = (
    ('批生产记录文件'),
    ('清洁验证方案'),
    ('工艺规程'),
    ('批检验记录文件'),
    ('稳定性考察方案'),
    ('工艺验证方案'),
)