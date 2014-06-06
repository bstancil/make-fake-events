import csv
import time
import datetime
import random
from datetime import timedelta

def ts(timestamp):
    val = timestamp.strftime("%Y-%m-%dT%H:%M:%S")
    return val

def write_to_csv(csv_name,array):
    columns = len(array[0])
    rows = len(array)
    
    with open(csv_name, "wb") as test_file:
        file_writer = csv.writer(test_file)
        for i in range(rows):
            file_writer.writerow([array[i][j] for j in range(columns)])

def prepare_table(table,headers,columns_to_include):
    output = []
    output.append(headers)
    
    for row in table:
        new_row = list( row[i] for i in columns_to_include)
        output.append(new_row)
    
    return output

def create_hour():
    t = random.random()
    if t <= .10:
        hour = random.randint(0,6)
    elif t < .14:
        hour = 7
    elif t < .185:
        hour = 8
    elif t < .85:
        hour = random.randint(9,17)
    elif t < .92:
        hour = 18
    elif t < .95:
        hour = 19
    else:
        hour = random.randint(20,23)
    
    return hour

def create_minute():
    minute = int( random.random() * 59 )
    return minute

def interpolate_list(since_start,day_diff,start_list,end_list):
    new_list = []
    for d in range(len(start_list)):
        
        start_val = start_list[d]
        end_val = end_list[d]
        diff_val = end_val - start_val
        
        current_val = ((since_start/(day_diff*1.)) * diff_val) + start_val
        new_list.append(current_val)
    
    return new_list

def get_day_diff(start_date,end_date):
    day_diff_obj = end_date - start_date
    sec_diff = day_diff_obj.total_seconds()
    day_diff = int( sec_diff / (60 * 60 * 24) )
    
    return day_diff

def create_cumulative_dist(current_user_dist):
    cum_dist = [0]
    
    for n in range(len(current_user_dist)):
        total_so_far = cum_dist[n]
        cum_dist.append( current_user_dist[n] + total_so_far )
    
    return cum_dist[1:]

def drop_from_list(list_obj,to_drop):    
    new = []
    for idx,val in enumerate(list_obj):
        if idx != to_drop:
            new.append(val)
    return new
# 
def plot_dist(event_list,event_dist,last_event):
    data = []
    for i in range(1000):
        e = pick_event(event_list,event_dist,last_event)
        x = event_list.index(e)
        data.append(x)
        
    print sum(data)/len(data)
    plt.hist(data, 5)
    plt.show()
    

import matplotlib.pyplot as plt
import numpy as np

def plot_gamma(a,b):
    data = []
    for i in range(1000):
        x = random.gammavariate(a,b)
        data.append(x)
        
    print sum(data)/len(data)
    plt.hist(data, 20)
    plt.show()
