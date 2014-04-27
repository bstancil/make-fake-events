import time
import datetime
import pytz
import random
import math
import numpy as np
from datetime import timedelta
import helpers as h

def generate_arbitrary_events(login_events,from_login_event_params):
    
    new_event_list = []
    
    ## Define variables
    ep = from_login_event_params
    
    start_date = ep[0]
    end_date = ep[1]
    from_event = ep[2]
    sequence_type = ep[3]
    event_list = ep[4]
    event_dist_start = ep[5]
    event_dist_end = ep[6]
    odds_to_cont_start = ep[7]
    odds_to_cont_end = ep[8]
    num_of_events_start = ep[9]
    num_of_events_end = ep[10]
    
    ## Check total_diff
    day_diff = h.get_day_diff(start_date,end_date)
    
    for e in login_events:
        ## Write event to new table
        new_event_list.append(e)
        
        if e[4] == from_event:
            
            ## Check time and interpolate
            occurred_at = e[1]
            since_start = h.get_day_diff(start_date,occurred_at)
            current_odds_to_cont = h.interpolate_list(since_start,day_diff,odds_to_cont_start,odds_to_cont_end)
            
            ## Check to continue
            user_type = e[5]
            go_on = check_to_continue(user_type,current_odds_to_cont)
            
            if go_on == True:
                
                event_dist = h.interpolate_list(since_start,day_diff,event_dist_start,event_dist_end)
                
                if sequence_type == 'collection':
                    current_num_of_events = h.interpolate_list(since_start,day_diff,num_of_events_start,num_of_events_end)
                    new_events = make_collection_events(e,event_list,event_dist,current_num_of_events)
                    
                elif sequence_type == 'funnel':
                    new_events = make_funnel_events(e,event_list,event_dist)
                
                for e in new_events:
                    new_event_list.append(e)
    
    return new_event_list

def check_to_continue(user_type,odds_to_continue):
    
    odds = odds_to_continue[user_type - 1]
    
    random_assignment = random.random()
    
    if random_assignment < odds:
        go_on = True
    else:
        go_on = False
    return go_on

def make_collection_events(e,event_list,event_dist,current_num_of_events):
    
    user_type = e[5]
    event_mean = current_num_of_events[user_type - 1]
    rand_events = random.gammavariate(event_mean/2.,2)
    number_of_events = int(math.ceil(rand_events))
    
    small_event_table = []
    last_event = 'none'
    last_event_time = e[1]
    
    for i in range(number_of_events):
        
        event = generate_event(e,event_list,event_dist,last_event,last_event_time)
        small_event_table.append(event)
        
        last_event = event[4]
        last_event_time = event[1]
    
    return small_event_table

def generate_event(e,event_list,event_dist,last_event,last_event_time):
    time_between = random.normalvariate(30,30/5)
    time_between = max(int(time_between),2)
    
    diff_s = timedelta(seconds=1)
    occurred_at = last_event_time + (time_between * diff_s)
    formatted_occurred_at = h.ts(occurred_at)
    
    user_id = e[0]
    user_type = e[5]
    
    event_name = pick_event(event_list,event_dist,last_event)
    
    event = (user_id,occurred_at,formatted_occurred_at,'engagement',event_name,user_type)
    
    return event

def pick_event(event_list,event_dist,last_event):
    
    number_of_events = len(event_list)
    rand_value = random.random()
    
    if last_event == 'none':
        cum_dist = h.create_cumulative_dist(event_dist)
        
        event = event_from_dist(rand_value,event_list,cum_dist)
    
    else:
        event_to_drop = event_list.index(last_event)
        
        new_list = h.drop_from_list(event_list,event_to_drop)
        new_dist = h.drop_from_list(event_dist,event_to_drop)
        
        new_total = sum(new_dist)
        multiple = 1/new_total
        new_cum_dist = [i * multiple for i in new_dist]
        
        cum_dist = h.create_cumulative_dist(new_cum_dist)
        
        event = event_from_dist(rand_value,new_list,cum_dist)
    
    return event

def event_from_dist(rand_value,event_list,cum_dist):
    
    for idx, val in enumerate(cum_dist):
        if rand_value < val:
            event = event_list[idx]
            break
        else:
            event = event_list[0]
    
    return event

def make_funnel_events(e,event_list,event_dist):
    
    small_event_table = []
    last_event_time = e[1]
    
    for i in range(len(event_list)):
        
        rand_val = random.random()
        if rand_val < event_dist[i]:
            event = generate_funnel_event(e,i,event_list,last_event_time)
            small_event_table.append(event)
            
            last_event_time = event[1]
        else:
            break
    
    return small_event_table

def generate_funnel_event(e,i,event_list,last_event_time):
    user_id = e[0]
    user_type = e[5]
    
    time_between = random.normalvariate(30,30/5)
    time_between = max(int(time_between),2)
    
    diff_s = timedelta(seconds=1)
    occurred_at = last_event_time + (time_between * diff_s)
    formatted_occurred_at = h.ts(occurred_at)
    
    event_name = event_list[i]
    
    event = (user_id,occurred_at,formatted_occurred_at,'engagement',event_name,user_type)
    
    return event