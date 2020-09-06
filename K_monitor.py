import baostock as bs
import pandas as pd

# **********************************************
# Time：    2020/08/30
# Author：  lomengshia & weiyuchen
# License： GPL
# Version： 0.10
# **********************************************



# 银行
Bank = ['sh.600926', 'sz.002142', 'sz.000001', 'sh.601838', 'sh.600036', 'sh.601009', 'sh.601128', 'sh.600908', 
        'sh.601577', 'sh.601997', 'sh.600919', 'sh.603323', 'sz.002807', 'sz.002839', 'sh.600928', 'sh.601229', 
        'sh.601860', 'sh.601166', 'sz.002936', 'sz.002958', 'sh.601818', 'sz.002948', 'sh.601077', 'sh.600016', 
        'sh.600000', 'sh.601939', 'sh.601916', 'sz.002966', 'sh.600015', 'sh.601658', 'sh.601998', 'sh.601988', 
        'sh.601398', 'sh.601328', 'sh.601169', 'sh.601288']

# 有色金属
NFmetals = ['sz.000688', 'sh.600961', 'sh.601168', 'sz.000878', 'sh.601609', 'sz.300828', 'sh.603527', 'sz.000807', 
            'sh.600362', 'sz.000630', 'sz.002171', 'sz.000060', 'sz.002540', 'sz.002114', 'sz.002203', 'sh.600531', 
            'sh.600219', 'sh.600338', 'sh.600497', 'sh.600888', 'sz.000612', 'sh.600490', 'sz.000758', 'sh.601020', 
            'sz.000933', 'sz.000426', 'sz.000751', 'sh.601212', 'sz.002295', 'sh.600331', 'sh.601600', 'sz.000603', 
            'sh.601137', 'sz.002578', 'sh.600255', 'sz.002501', 'sz.300328', 'sz.002379', 'sh.603115', 'sz.002988', 
            'sh.600768', 'sz.300337', 'sh.600595', 'sh.601677', 'sz.002806', 'sz.002824', 'sh.601388', 'sz.300697', 
            'sh.603003', 'sz.002160', 'sh.603876']

# 黄金
Gold = ['sh.601899', 'sz.002237', 'sz.000975', 'sh.601069', 'sh.600988', 'sh.600547', 'sh.600687', 'sh.600311', 'sz.002155', 
        'sh.600385', 'sh.600489', 'sh.600766']

# 证券公司
Securities = ['sh.601456', 'sh.600109', 'sh.600095', 'sh.600061', 'sh.600621', 'sh.601066', 'sh.601688', 'sh.601696', 
             'sh.600918', 'sh.600030', 'sh.601881', 'sz.300059', 'sh.601555', 'sh.600837', 'sz.002797', 'sh.601198', 
             'sh.600999', 'sz.000166', 'sz.000783', 'sh.601099', 'sh.600909', 'sz.002500', 'sz.000686', 'sz.002670', 
             'sh.600155', 'sz.002945', 'sh.601377', 'sz.000776', 'sh.601901', 'sz.002673', 'sz.000728', 'sz.002926', 
             'sh.601211', 'sh.601108', 'sh.600958', 'sh.601375', 'sz.002736', 'sz.000750', 'sz.002939', 'sh.600864', 
             'sh.601878', 'sz.000712', 'sh.600369', 'sh.601236', 'sh.601162', 'sh.601990', 'sh.601788', 'sz.000987', 
             'sh.601456', 'sh.600109', 'sh.600095', 'sh.600061', 'sh.600621', 'sh.601066', 'sh.601688', 'sh.601696', 
             'sh.600918', 'sh.600030', 'sh.601881', 'sz.300059', 'sh.601555', 'sh.600837', 'sz.002797', 'sh.601198', 
             'sh.600999', 'sz.000166', 'sz.000783', 'sh.601099', 'sh.600909', 'sz.002500', 'sz.000686', 'sz.002670', 
             'sh.600155', 'sz.002945', 'sh.601377', 'sz.000776', 'sh.601901', 'sz.002673', 'sz.000728', 'sz.002926', 
             'sh.601211', 'sh.601108', 'sh.600958', 'sh.601375', 'sz.002736', 'sz.000750', 'sz.002939', 'sh.600864', 
             'sh.601878', 'sz.000712', 'sh.600369', 'sh.601236', 'sh.601162', 'sh.601990', 'sh.601788', 'sz.000987']


# 功能：获取沪深A股历史K线数据
# 参数：bs       股票系统
#      stock    股票代码
#      date     查询日期 2020-08-08
#      category 查询指标
# 附件：
# 分钟线指标：date,time,code,open,high,low,close,volume,amount,adjustflag
# 周月线指标：date,code,open,high,low,close,volume,amount,adjustflag,turn,pctChg
def get_stock_daily(bs, stock, category, begin_date, end_date):
    rs = bs.query_history_k_data_plus(stock, category, start_date = begin_date, end_date = end_date, frequency = 'd', adjustflag = '3')
    daily_data = []
    while (rs.error_code == '0') and rs.next():
        daily_data.append(int(float(rs.get_row_data()[0])*1000))
    return daily_data

# 功能：分析峰值数据集合并得到颈线
# 参数：峰值数据集合
def get_neckline_chen(neckline_array):
    # 利用波动大小求取最合适的颈线
    wave = []
    neck_num = len(neckline_array)
    print(neck_num)
    for i in range(neck_num):
        wave.append(0.0)
        for j in range(neck_num):
            wave[i] += abs(neckline_array[i]-neckline_array[j]) / neckline_array[j]
    tmp = wave.index(min(wave[0:len(neckline_array)]))
    neckline = neckline_array[tmp]   
    return neckline

# 功能：分析当前数据并获取峰值集合
# 参数：daily_data 日常数据 [5.63, 5.65, 5.64, 5.66, 5.75]
def brust_point_monitor(daily_data):
    neckline_array = []
    neckline = 0xffffffff
    begin = 0
    tmp = 0
    end = len(daily_data) - 1
    break_succ = False

    # 生成峰值集合
    while tmp < end-2 and neckline > max(daily_data[begin:end]):
        tmp = begin + daily_data[begin:end].index(max(daily_data[begin:end]))
        tmp = tmp + 1
        neckline_array.append(max(daily_data[begin:end]))
        begin = tmp

    # 找到颈线
    neckline = get_neckline_chen(neckline_array)

    if daily_data[len(daily_data) - 1] > neckline:
        break_succ = True

    return neckline, break_succ

def main():
    #### 登陆系统 ####
    lg = bs.login()

    #### 分析数据 ####
    for att_stock in Securities:
        # 获取数据
        daily_data = get_stock_daily(bs, att_stock, "high", "2020-01-01", "2020-09-01") 
        #print(daily_data)
        point_value, break_succ = brust_point_monitor(daily_data)
        if break_succ:
            print(att_stock + " 画出颈线数据:"+ str(point_value/1000.0) +" , 并突破颈线成功！")
        else:
            print(att_stock + " 画出颈线数据:"+ str(point_value/1000.0) +" , 突破失败")
    
    #### 登出系统 ####
    bs.logout()

main()