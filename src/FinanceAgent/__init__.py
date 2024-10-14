# -*- coding: utf-8 -*-
# @Time    : 2024/06/27
# @Author  : Derek

from .base import *

SUPPORTED_APIS = {
}

def api(**kwargs):
    api_cls = FinanceDataFetchParallelAPI(None)
    res_dict = {}
    try:
        # required fields
        res_dict = api_cls.api(kwargs)
    except Exception as e:
        print (e)
    return res_dict
