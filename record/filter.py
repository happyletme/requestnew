import logging
def filter(teststepList):
    for teststep in  teststepList:
        try:
            teststep['name'] = "loadCase"
        except:
            logging.error("替换名字出错")
        '''
        #替换api
        #监控项
        if teststep['request'].get('api','') == '/monitor-api/stat/queryV2':
            teststep['request']['api'] = '/api/stat/queryV2'
        #指标
        elif teststep['request'].get('api', '') == '/monitor-api/metric_item_stat/query':
            teststep['request']['api'] = '/api/metric_item_stat/query'
        #替换时间戳
        try:
            teststep['request']['json']['interval']['start'] = '${__get_later_minutes_Timestamp(6)}'
            teststep['request']['json']['interval']['end'] = '${__get_later_minutes_Timestamp(1)}'
        except:
            logging.error("替换时间戳出错")
        # 替换返回值长度
        try:
            teststep['request']['json']['limit']['size'] = 500
        except:
            logging.error("替换返回值长度出错")
        # 替换名字出错
        try:
            teststep['request']['json']['limit']['size'] = 500
        except:
            logging.error("替换返回值长度出错")
            # 替换名字出错
        try:
            teststep['name'] = teststep['request']['json']['table']+'_'+teststep['request']['json']['measures'][0]['field']
        except:
            teststep['name'] = teststep['request']['json']['metricItemId']
            logging.error("替换名字出错")
        '''
    return teststepList