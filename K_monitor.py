# **********************************************
# Time：    2020/09/06
# Author：  lomengshia & weiyuchen
# License： GPL
# Version： 0.20
# **********************************************

import baostock as bs
import pandas as pd
import sys, getopt
from config import *
import datetime

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
    daily_high_data = []
    while (rs.error_code == '0') and rs.next():
        daily_high_data.append(int(float(rs.get_row_data()[0])*1000))
    return daily_high_data

# 功能：根据颈线底线计算第一涨幅位，第二涨幅位和第三涨幅位
#      并据此计算止损位
# 参数：颈线，底线
def rising_pos(neckline, bottom_line):
    firt_rising = neckline + (neckline - bottom_line)           # 第一涨幅位
    second_rising = neckline + (neckline - bottom_line) * 2     # 第二涨幅位
    third_rising = neckline + (neckline - bottom_line) * 3      # 第三涨幅位
    loss_pos = neckline * 0.96                                  # 止损位
    return firt_rising, second_rising, third_rising, loss_pos

# 功能：分析峰值数据集合并得到颈线
# 参数：峰值数据集合
def get_neckline(neckline_array, neckline_index, daily_open_data, daily_close_data):
    # 利用波动大小求取最合适的颈线
    wave = []
    neck_num = len(neckline_array)
    print(neck_num)
    for i in range(neck_num):
        wave.append(0.0)
        for j in range(neck_num):
            wave[i] += abs(neckline_array[i]-neckline_array[j]) / neckline_array[j]
    tmp = wave.index(min(wave[0:len(neckline_array)]))
    # 对颈线进行一个值缩减，让颈线不至于过高
    # neckline = neckline_array[tmp] * 0.98 by chen
    neck_pos = neckline_index[tmp]
    tmp_high_value = max(daily_open_data[neck_pos], daily_close_data[neck_pos])
    neckline = (neckline_array[tmp]-tmp_high_value) * 0.7 + tmp_high_value
    print(neckline_array[tmp])
    print(neckline)
    return neckline, neck_pos

# 功能： 根据颈线数据得到当前的底线
def get_bottom(neck_pos, daily_high_data, daily_low_data, daily_open_data, daily_close_data):
    begin = neck_pos
    end = neck_pos

    high_flag = daily_high_data[neck_pos]

    for i in range(neck_pos, -1, -1):
        if daily_high_data[i] <= high_flag:
            begin -= 1
        else:
            break
        if i == 0:
            break
    
    for i in range(neck_pos, len(daily_high_data)):
        if daily_high_data[i] <= high_flag:
            end += 1
        else:
            break

    # 找到最小值即可
    bottom_line = min(daily_low_data[begin:end])
    tmp = begin + daily_low_data[begin:end].index(min(daily_low_data[begin:end]))
    tmp_value = min(daily_open_data[tmp], daily_close_data[tmp])
    bottom_line = bottom_line + 0.03 * (tmp_value - bottom_line)

    return bottom_line

# 功能：分析当前数据并获取峰值集合
# 参数：daily_high_data 日常数据 [5.63, 5.65, 5.64, 5.66, 5.75]
def brust_point_monitor(daily_high_data, daily_open_data, daily_close_data):
    neckline_array = []
    neckline_index = []
    neckline = 0xffffffff
    begin = 0
    tmp = 0
    end = len(daily_high_data) - 1
    break_succ = False

    # 生成峰值集合
    while tmp < end-2 and neckline > max(daily_high_data[begin:end]):
        tmp = begin + daily_high_data[begin:end].index(max(daily_high_data[begin:end]))
        neckline_index.append(tmp)
        neckline_array.append(max(daily_high_data[begin:end]))
        tmp = tmp + 1
        begin = tmp

    # 找到颈线
    neckline, neck_pos = get_neckline(neckline_array, neckline_index, daily_open_data, daily_close_data)

    if daily_high_data[len(daily_high_data) - 1] > neckline:
        break_succ = True

    return neckline, break_succ, neck_pos

# 功能： 分析颈线底线得到当前的投资建议
def invest_suggestion(stock_code, daily_high_data, daily_low_data, daily_open_data, daily_close_data):
    neckline, break_succ, neck_pos = brust_point_monitor(daily_high_data, daily_open_data, daily_close_data)
    bottom_line = get_bottom(neck_pos, daily_high_data, daily_low_data, daily_open_data, daily_close_data)

    # 得到涨幅位和止损位
    firt_rising, second_rising, third_rising, loss_pos = rising_pos(neckline, bottom_line)

    # 给出投资建议
    if break_succ:
        print(stock_code + " 颈线数据: "+ str(neckline/1000.0) +" , 突破颈线成功！投资建议如下：\n")
        print("第一涨幅位（止盈位）: " + str(firt_rising/1000.0) + "\n")
        print("第二涨幅位（止盈位）: " + str(second_rising/1000.0) + "\n")
        print("第三涨幅位（止盈位）: " + str(third_rising/1000.0) + "\n")
        print("止损位: " + str(loss_pos/1000.0) + "\n")
        print("上述数据仅供参考，请仔细查看k线数据再做投资决定，祝投资成功~")
    else:
        print(stock_code + " 颈线数据:"+ str(neckline/1000.0) +" , 突破失败！暂不建议投资该股票\n")


def main(argv):
    #### 登陆系统 ####
    bs.login()
    curr_date = datetime.datetime.now().strftime('%Y-%m-%d')
    #### 添加输入参数的支持 ####
    inputfile = ''
    stock_code = ''
    help_info = "The usage is: python3 K_monitor.py <Option> <Target>\n" \
                "Options include: \n" \
                "-h --help , print help infomation\n" \
                "-c --code <stock code> , specify a stock code, 'sz.600000' etc \n" \
                "-i --file <file name> , specify a stock code file, 'Back.json' etc \n" \
                "Target include: \n" \
                "-Combinatorial type, etc: Bank , Gold , NFmetals , Securities , Selfdefine \n" \
                "-Code type, etc: sh601889 \n"

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
        #### 获取峰值数据 ####
        daily_high_data = get_stock_daily(bs, stock_code, "high", "2020-01-01", curr_date) 
        #### 获取最小数据 ####
        daily_low_data = get_stock_daily(bs, stock_code, "low", "2020-01-01", curr_date)
        #### 获取开盘数据 ####
        daily_open_data = get_stock_daily(bs, stock_code, "open", "2020-01-01", curr_date) 
        #### 获取收盘数据 ####
        daily_close_data = get_stock_daily(bs, stock_code, "close", "2020-01-01", curr_date)
        #print(daily_high_data)

        invest_suggestion(stock_code, daily_high_data, daily_low_data, daily_open_data, daily_close_data)
        '''
        point_value, break_succ = brust_point_monitor(daily_high_data)
        if break_succ:
            print(stock_code + " 画出颈线数据:"+ str(point_value/1000.0) +" , 并突破颈线成功！")
        else:
            print(stock_code + " 画出颈线数据:"+ str(point_value/1000.0) +" , 突破失败")
        '''
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
        elif inputfile == "Selfdefine":
            stocks = Selfdefine
        else:
            print("please use '-h' to see the input format~ \n")
            return 
        #### 分析数据 ####
        for att_stock in stocks:
            # 获取峰值数据
            daily_high_data = get_stock_daily(bs, att_stock, "high", "2020-01-01", curr_date) 
            # 获取最小数据
            daily_low_data = get_stock_daily(bs, att_stock, "low", "2020-01-01", curr_date)
            #### 获取开盘数据 ####
            daily_open_data = get_stock_daily(bs, att_stock, "open", "2020-01-01", curr_date) 
            #### 获取收盘数据 ####
            daily_close_data = get_stock_daily(bs, att_stock, "close", "2020-01-01", curr_date)
            #print(daily_high_data)
            
            invest_suggestion(att_stock, daily_high_data, daily_low_data, daily_open_data, daily_close_data)
            '''
            point_value, break_succ = brust_point_monitor(daily_high_data)
            if break_succ:
                print(att_stock + " 画出颈线数据:"+ str(point_value/1000.0) +" , 并突破颈线成功！")
            else:
                print(att_stock + " 画出颈线数据:"+ str(point_value/1000.0) +" , 突破失败")
            '''
    #### 登出系统 ####
    bs.logout()

if __name__ == "__main__":
   main(sys.argv[1:])
