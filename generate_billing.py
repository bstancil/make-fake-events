import random
import math
from datetime import timedelta
import helpers as h

def generate_billing_table(user_table,company_dist,start_monetize_rate,end_monetize_rate,start_churn_rate,end_churn_rate,contract_length,
contract_range,start,end):
    
    companies = get_company_ids(user_table)
    companies = add_company_type(companies,company_dist)
    
    billing_table = []
    for c in companies:
        company_type = c[3]
        start_date = c[2]
        next_month = start_date + timedelta(days=32)
        first_billing_date = next_month.replace(day=1,hour=0,minute=0,second=0,microsecond=0)
        
        monetize_date = get_monetize_date(company_type,first_billing_date,start_monetize_rate,end_monetize_rate,start,end)
        
        if monetize_date != 0:
            contract_amount = get_contract_amount(0,contract_range)
            entry = [c[0],monetize_date,h.ts(monetize_date),contract_amount,contract_length]
            billing_table.append(entry)
            
            next_billing_period = get_next_billing_period(monetize_date,contract_length)
            
            renew = check_renewal(company_type,start_churn_rate,end_churn_rate,next_billing_period,start,end)
            
            while next_billing_period < end and renew == True:
                
                contract_amount = get_contract_amount(contract_amount,contract_range)
                
                entry = [c[0],next_billing_period,h.ts(next_billing_period),contract_amount,contract_length]
                billing_table.append(entry)
                next_billing_period = get_next_billing_period(next_billing_period,contract_length)
                print 'made it here'
    
    return billing_table
    

def get_company_ids(user_table):
    company_list = []
    companies = []
    
    for u in user_table:
        company_list.append(u[3])
    
    company_list = list(set(company_list))
    
    for c in company_list:
        users = [item for item in user_table if item[3] == c]
        dates = [item[1] for item in users]
        
        user_count = len(users)
        start_date = min(dates)
        company_entry = [c,user_count,start_date]
        
        companies.append(company_entry)
    
    return companies

def add_company_type(company_table,company_dist):
    table = []
    cumulative_dist = h.create_cumulative_dist(company_dist)
    
    for c in company_table:
        random_assignment = random.random()
        
        for idx, val in enumerate(cumulative_dist):
            if random_assignment < val:
                company_type = idx + 1
                break
            else:
                company_type = len(cumulative_dist)
                
        c = c + [company_type]
        table.append(c)
    
    return table

def get_monetize_date(company_type,first_billing_date,start_monetize_rate,end_monetize_rate,start,end):
    day_diff = h.get_day_diff(start,end)
    since_start = h.get_day_diff(start,first_billing_date)
    current_monetize_rates = h.interpolate_list(since_start,day_diff,start_monetize_rate,end_monetize_rate)
    
    monetize_rate = current_monetize_rates[company_type - 1]
    monetize_date = 0
    
    billing_date = first_billing_date
    
    while billing_date < end:
        random_assignment = random.random()
        if random_assignment < monetize_rate:
            monetize_date = billing_date
            break
        else:
            monetize_date = 0
            monetize_rate = monetize_rate * .8
            m = billing_date.month
            if m == 12:
                y = billing_date.year
                billing_date = billing_date.replace(year=y+1,month=1)
            else:
                billing_date = billing_date.replace(month=m+1)
    
    return monetize_date

def get_contract_amount(previous_value,contract_range):
    min_value = contract_range[0]
    max_value = contract_range[1]
    
    if previous_value == 0:
        value = random.gammavariate(min_value/1000,max_value/4000)
        
        round_value = round(value)*1000
        final_value = min(max(round_value,min_value),max_value)
        
    else:
        random_assignment = random.random()
        if random_assignment < .8:
            change = random.random()/2 + 1
        else:
            change = 1 - random.random()/2
        
        value = previous_value * change
        round_value = round(value/1000)*1000
        final_value = min(max(round_value,min_value),max_value)
    
    return final_value

def check_renewal(company_type,start_churn_rate,end_churn_rate,next_billing_period,start,end):
    day_diff = h.get_day_diff(start,end)
    since_start = h.get_day_diff(start,next_billing_period)
    current_churn_rates = h.interpolate_list(since_start,day_diff,start_churn_rate,end_churn_rate)
    
    churn_rate = current_churn_rates[company_type - 1]
    
    random_assignment = random.random()
    
    if random_assignment < churn_rate:
        print 'churned'
        return False
    else:
        return True

def get_next_billing_period(next_billing_period,contract_length):
    m = next_billing_period.month
    next_month = m + contract_length
    
    if next_month > 12:
        y = next_billing_period.year
        additional_years = int(math.floor(next_month/12))
        ending_month = int(next_month - 12*additional_years)
        
        next_period = next_billing_period.replace(year=y+additional_years,month=ending_month)
    else:
        next_period = next_billing_period.replace(month=next_month)
    
    return next_period
