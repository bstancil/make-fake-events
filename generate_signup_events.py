import time
import datetime
import pytz
import random
import numpy as np
from datetime import timedelta
import helpers as h

def generate_signup_events(user_table,events,start_date,end_date,start_flow,end_flow,step_time,weekend_ratio):
    
    day_diff = h.get_day_diff(start_date,end_date)
    
    updated_user_table = []
    event_table = []
    
    for user in user_table:
        user_id = user[0]
        created_at = user[1]
        created_at_formatted = h.ts(created_at)
        
        dow = created_at.weekday()
        
        since_start = h.get_day_diff(start_date,created_at)
        
        step1 = [user_id,created_at,created_at_formatted,'signup_flow','create_user']
        event_table.append(step1)
        
        last_event_time = created_at
        
        for e in range(len(start_flow)):
            
            stepX = create_signup_event(e,user,events,start_flow,end_flow,step_time,since_start,day_diff,weekend_ratio,dow,last_event_time)
            
            if stepX[0] == False:
                activated_at = ''
                break
            
            else:
                activated_at = stepX[1][2]
                event_table.append(stepX[1])
                last_event_time = stepX[1][1]
            
        updated_user = update_user(user,activated_at)
        updated_user_table.append(updated_user)
    
    return [event_table,updated_user_table]

def create_signup_event(event_number,user,events,start_flow,end_flow,step_time,since_start,day_diff,weekend_ratio,dow,last_event_time):
    
    current_odds = get_current_odds(event_number,start_flow,end_flow,since_start,day_diff)
    
    if dow > 4:
        current_odds = current_odds * weekend_ratio
    
    random_value = random.random()
    
    if random_value <= current_odds:
        event = make_event(user,event_number,events,step_time,last_event_time)
        entry = (True,event)
    else:
        entry = (False,[])
    
    return entry

def update_user(user,activated_at):
    
    if activated_at == '':
        state = 'pending'
    else:
        state = 'active'
    
    updated_user = user + [activated_at,state]
    return updated_user

def get_current_odds(event_number,start_flow,end_flow,since_start,day_diff):
    start_odds = start_flow[event_number]
    end_odds = end_flow[event_number]
    
    diff_odds = end_odds - start_odds
    
    current_odds = ((since_start/(day_diff*1.)) * diff_odds) + start_odds
    
    return current_odds

def make_event(user,event_number,events,step_time,last_event_time):
    user_id = user[0]
    e = event_number + 1
    
    time_between = random.normalvariate(step_time,step_time/5)
    time_between = max(int(time_between),2)
    
    diff_s = timedelta(seconds=1)
    
    occurred_at = last_event_time + (time_between * diff_s)
    formatted_occurred_at = h.ts(occurred_at)
    
    event_name = events[e]
    
    event = [user_id,occurred_at,formatted_occurred_at,'signup_flow',event_name]
    
    return event