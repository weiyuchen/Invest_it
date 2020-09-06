import baostock as bs
import pandas as pd
import sys, getopt
from config import *

# **********************************************
# Time：    2020/09/06
# Author：  lomengshia & weiyuchen
# License： GPL
# Version： 0.20
# **********************************************

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

def main(argv):
    #### 登陆系统 ####
    lg = bs.login()

    #### 添加输入参数的支持 ####
    inputfile = ''
    stock_code = ''
    help_info = "The usage is: python3 K_monitor.py <Option> <Target>\n" \
                "Options include: \n" \
                "-h --help , print help infomation\n" \
                "-c --code <stock code> , specify a stock code, 'sz.600000' etc \n" \
                "-i --file <file name> , specify a stock code file, 'Back.json' etc \n"

    try:
        opts, args = getopt.getopt(sys.argv[1:],"-h-i:-c:",['help','file','code'])
    except getopt.GetoptError:
        print(help_info)
        sys.exit(2)
    for opt, arg in opts:
        if opt in ('-h','--help'):
            print(help_info)
            sys.exit()
        elif opt in ('-i','--file'):
            inputfile = arg
        elif opt in ('-c','--code'):
            stock_code = arg

    if stock_code != '':
        #### 分析数据 ####
        daily_data = get_stock_daily(bs, stock_code, "high", "2020-01-01", "2020-09-01") 
        #print(daily_data)
        point_value, break_succ = brust_point_monitor(daily_data)
        if break_succ:
            print(stock_code + " 画出颈线数据:"+ str(point_value/1000.0) +" , 并突破颈线成功！")
        else:
            print(stock_code + " 画出颈线数据:"+ str(point_value/1000.0) +" , 突破失败")

    else:
        #### 确定类型 ####
        if inputfile == "Gold":
            stocks = Gold
        elif inputfile == "Bank":
            stocks = Bank
        elif inputfile == "NFmetals":
            stocks = NFmetals
        elif inputfile == "Securities":
            stocks = Securities
        elif inputfile == "selfdefine":
            stocks = selfdefine
        else:
            print("please use selfdefine as your own code name")
        #### 分析数据 ####
        for att_stock in stocks:
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

if __name__ == "__main__":
   main(sys.argv[1:])
