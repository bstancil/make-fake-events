import time
import datetime
import pytz
import random
import numpy as np
from datetime import timedelta
import helpers as h

def generate_user_table(users,start_date,end_date,monthly_growth_rate,weekend_ratio):
    
    daily_growth = get_daily_growth(monthly_growth_rate)
    
    day_diff_obj = end_date - start_date
    sec_diff = day_diff_obj.total_seconds()
    day_diff = int( sec_diff / (60 * 60 * 24) )
    
    first_day_new_users = figure_first_day_users(users,daily_growth,day_diff,weekend_ratio)
    first_day_new_users = max(1,first_day_new_users)
    
    user_table = make_user_table(first_day_new_users,start_date,day_diff,daily_growth,weekend_ratio)
    
    user_table = add_company_id(user_table)
    
    return user_table


def get_daily_growth(monthly_growth_rate):
    daily_rate = monthly_growth_rate ** (1.0/30)
    return daily_rate


def figure_first_day_users(users,daily_growth,day_diff,weekend_ratio):
    total_users = 0
    
    for n in range(day_diff):
        total_users += 1 * (daily_growth ** n)
    
    adj_users = users * (7 / (5 + (2*weekend_ratio)))
    
    first_day_users = adj_users/total_users
    
    return int(first_day_users)


def make_user_table(first_day_count,start_date,number_of_days,daily_growth_rate,weekend_ratio):
    
    user_table = []
    
    diff_d = timedelta(days=1)
    
    todays_count = first_day_count
    user_id = 0
    
    for d in range(number_of_days):
        date = start_date + (d * diff_d)
        
        count_to_pass = todays_count
        todays_count = random.normalvariate(todays_count,(todays_count/10))
        
        if date.weekday() <= 4:
            todays_count = int(todays_count)
        else:
            todays_count = int(todays_count * weekend_ratio)
        
        for i in range(todays_count):
            user_row = generate_user(date,user_id)
            user_table.append(user_row)
            user_id += 1
        
        todays_count = count_to_pass * daily_growth_rate
    
    return user_table

def generate_user(date,user_id):
    
    hour = h.create_hour()
    minute = h.create_minute()
    second = h.create_minute()
    
    create_date = datetime.datetime(date.year,date.month,date.day,hour,minute,second,0)
    formatted_date = h.ts(create_date)
    
    row = [user_id,create_date,formatted_date]
    
    return row

def add_company_id(user_table):
    
    output_table = []
    
    total_users = len(user_table)
    rand_dist = np.random.zipf(1.05,total_users)
    rand_dist = renumber_rand(rand_dist)
    
    for idx, val in enumerate(user_table):
        row = val + [rand_dist[idx]]
        output_table.append(row)
    
    return output_table

def renumber_rand(rand_dist):
    sort = sorted(rand_dist)
    new_dist = []
    
    for idx, val in enumerate(rand_dist):
        if idx == 0:
            new_val = 1
        else:
            if sort[idx] == sort[idx - 1]:
                new_val = new_dist[idx - 1]
            else:
                new_val = new_dist[idx - 1] + 1
        
        new_dist.append(new_val)
    
    random.shuffle(new_dist)
    
    return new_dist
