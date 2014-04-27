import time
import datetime
import pytz
import random
import numpy as np
from datetime import timedelta
import helpers as h


def generate_login_events(signup_event_table,signup_event_list,start_user_dist,end_user_dist,start_odds_of_returning,end_odds_of_returning,
    start_date,end_date,start_days_to_return,end_days_to_return,weekend_login_ratio):
    
    day_diff = h.get_day_diff(start_date,end_date)
    
    event_table = []
    final_signup_event = signup_event_list[len(signup_event_list) - 1]
    
    for e in signup_event_table:
        user_type = 0
        e.append(user_type)
        event_table.append(e)
        
        if e[4] == final_signup_event:
            ## Get basic event info
            user_id = e[0]
            occurred_at = e[1]
            
            ## Figure out how long it's been since range start
            since_start = h.get_day_diff(start_date,occurred_at)
            
            ## Get current distributions and make user type
            current_user_dist = h.interpolate_list(since_start,day_diff,start_user_dist,end_user_dist)
            current_odds_of_return = h.interpolate_list(since_start,day_diff,start_odds_of_returning,end_odds_of_returning)
            current_days_to_return = h.interpolate_list(since_start,day_diff,start_days_to_return,end_days_to_return)
            
            ## Get user type and add first event
            user_type = get_user_type(current_user_dist)
            event = create_login_event(user_id,occurred_at,user_type)
            event_table.append(event)
            
            ## Check to see if should continue
            go_on = check_to_continue(occurred_at,end_date,user_type,current_odds_of_return,1)
            
            while go_on == True:
                
                ## Figure out when next event should be
                time_of_next_event = get_time_of_next(user_type,occurred_at,current_days_to_return)
                adj_time_of_next_event = adjust_time_of_next(time_of_next_event,weekend_login_ratio)
                
                ## Create event
                event = create_login_event(user_id,adj_time_of_next_event,user_type)
                event_table.append(event)
                
                ## Move occurred at forward, check to continue
                occurred_at = adj_time_of_next_event
                go_on = check_to_continue(occurred_at,end_date,user_type,current_odds_of_return,1.2)
    
    return event_table


def create_login_event(user_id,occurred_at,user_type):
    formatted_occurred_at = h.ts(occurred_at)
    event = [user_id,occurred_at,formatted_occurred_at,'engagement','login',user_type]
    
    return event

def get_user_type(current_user_dist):
    cumulative_dist = h.create_cumulative_dist(current_user_dist)
    random_assignment = random.random()
    
    for idx, val in enumerate(cumulative_dist):
        if random_assignment < val:
            user_type = idx + 1
            break
        else:
            user_type = len(cumulative_dist)
    
    return user_type

def check_to_continue(occurred_at,end_date,user_type,current_odds_of_return,multiple):
    if occurred_at > end_date:
        go_on = False
    else:
        odds_of_returning = current_odds_of_return[user_type - 1]
        adj_odds_of_returning = odds_of_returning * multiple
        
        random_assignment = random.random()
        
        if random_assignment < adj_odds_of_returning:
            go_on = True
        else:
            go_on = False
    
    return go_on

def get_time_of_next(user_type,occurred_at,current_days_to_return):
    mean_days_to_return = current_days_to_return[user_type - 1] 
    lmda = 1./mean_days_to_return
    days_to_return = random.expovariate(lmda)
    
    diff_s = timedelta(seconds=1)
    seconds_to_return = days_to_return * 24 * 60 * 60
    seconds_to_return = int(seconds_to_return)
    
    return_time = occurred_at + (seconds_to_return * diff_s)
    
    return return_time

def adjust_time_of_next(time_of_event,weekend_login_ratio):
    event_hour = time_of_event.hour
    diff_h = timedelta(hours=1)
    
    if event_hour <= 6 or event_hour >= 20:
        rand_hour = h.create_hour()
        
        if rand_hour <= 6 or rand_hour >= 20:
            hour_to_add = 0
        if rand_hour > 6 and rand_hour < 20 and rand_hour >= event_hour:
            hour_to_add = rand_hour - event_hour
        if rand_hour > 6 and rand_hour < 20 and rand_hour < event_hour:
            hour_to_add = (23 - event_hour) + rand_hour
    else:
        hour_to_add = 0
    
    adj_time_of_event = time_of_event + (hour_to_add * diff_h)
    event_day = adj_time_of_event.weekday()
    
    if event_day > 4:
        diff_d = timedelta(days=1)
        rand_value = random.random()
        
        if rand_value < weekend_login_ratio:
            if event_day == 5:
                adj_time_of_event = adj_time_of_event + (diff_d * 2)
            else:
                adj_time_of_event = adj_time_of_event + (diff_d * 1)
    
    return adj_time_of_event
