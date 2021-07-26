import pandas
import numpy as np
import pandas as pd
import FinanceDataReader as fdr
from datetime import datetime, timedelta
result = []


the_day = datetime(2021, 7, 16)

# 전체 종목
krx = fdr.StockListing('KRX')
sectors = dict(list(krx.groupby('Sector')))
med_sec = sectors['의료용품 및 기타 의약 관련제품 제조업']


# default 데이터
days = 15
start_day = the_day - timedelta(days)

# 종목 선정
def security_selection(the_day, days) :
    days = days
    start_day = the_day - timedelta(days)
    med = pd.DataFrame()
    for ix, row in med_sec.iterrows():
        code, name = row['Symbol'], row['Name']
        df = fdr.DataReader(code, start_day, the_day)
        med[name] = df['Close']

    med = med.dropna(axis =1)
    acc_rets = med / med.iloc[0] - 1.0
    returns  = acc_rets.iloc[-1]
    sector_means = returns.mean()

    back_dict = pd.DataFrame()
    for days in [days]:
        end_day = the_day - timedelta(1)
        df = med[start_day:end_day]  # 특정 기간
        acc_rets = df / df.iloc[0] - 1.0
        back_dict[days] = acc_rets.iloc[-1]

    selected = back_dict[back_dict[days] > sector_means]
    selected.reset_index(inplace=True)
    fin_selected = selected.sort_values(by = days, ascending = False).head(4)
    fin_selected = fin_selected.sort_values(by = days, ascending = False)[1:4]
    fin_selected.columns = ['Name', 'Rtn']
    fin_selected = pd.merge(fin_selected, med_sec, on = 'Name')
    return sector_means, fin_selected

fin_selected = security_selection(the_day, 15)[1]

# 백테스트 실시
pf_sec = med_sec[med_sec['Symbol'].isin(fin_selected['Symbol'])].reset_index(inplace = False, drop = True)
pf = pd.DataFrame()
forth_dict = pd.DataFrame()
for ix, row in pf_sec.iterrows():
    code, name = row['Symbol'], row['Name']
    start = the_day
    end_day = the_day + timedelta(days) - timedelta(1)
    df = fdr.DataReader(code, start, end_day)
    pf[name] = df['Close']
    pf_acc_rets = pf / pf.iloc[0] - 1.0

forth_dict['Rtn'] = pf_acc_rets.iloc[-1]
forth_dict['wgt'] = 1/3

df = pd.DataFrame({'Date' : [end_day],
                   'Rtn' : [sum(forth_dict['wgt'] * forth_dict['Rtn'])]})

result.append(df)