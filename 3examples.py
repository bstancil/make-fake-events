import datetime
import sys
sys.dont_write_bytecode = True

import generate_users as gu
import generate_signup_events as gse
import generate_login_events as gle
import generate_arbitrary_events as gae
import generate_billing as gb
import generate_test_treatments as gtt
import helpers as h

## Schema
user_headers = ['user_id','created_at','company_id','activated_at','state']
user_include = [0,2,3,4,5]

event_headers = ['user_id','occurred_at','event_type','event_name']
event_include = [0,2,3,4]

billing_headers = ['company_id','signed_date','contract_amount','contract_length']
billing_include = [0,2,3,4]

## User inputs
start = datetime.datetime(2013,6,1,0,0,0,0)
end = datetime.datetime(2014,6,1,0,0,0,0)
monthly_growth = 1.02
weekend_signup_ratio = .3
users = 10000

## Signup inputs
signup_event_list = ['create_user','complete_signup']
starting_flow = [.9]
ending_flow = [.95]
step_time = 30
weekend_signup_flow_ratio = .8

## Contract inputs
company_dist = [.3,.3,.4]
start_monetize_rate = [.8,.6,.1]
end_monetize_rate = [.5,.5,.2]
start_churn_rate = [.1,.1,.1]
end_churn_rate = [.2,.2,.2]
contract_length = 6
contract_range = [1000,100000]

## Login inputs
start_user_dist = [.1,.3,.6]
end_user_dist = [.1,.3,.6]
starts_odds_of_returning = [.8,.5,.1]
end_odds_of_returning = [.9,.7,.3]
start_days_to_return = [1,7,15]
end_days_to_return = [1,5,12]
weekend_login_ratio = .3

# Test inputs
test_start_date = datetime.datetime(2014,4,1,0,0,0,0)
test_end_date = datetime.datetime(2014,5,1,0,0,0,0)
test_on_event = 'login'
test_event_names = ['test_1_test_group','test_1_control_group']
test_ratios = [[.35,.65],[.2,.8],[.18,.82]]

test_treatment_params = [test_start_date,test_end_date,test_on_event,test_event_names,test_ratios]

## Events inputs
## Dictionary
# from_event: The event to select events after
# sequence_type: Either 'funnel' or 'collection'
# event_distribution: IF 'funnel', the odds of moving on to each. IF 'collection', the starting prob dist of the events
# odds_to_continue: Odds fo starting the process at all
# number_of_events: Only used for 'collection', determines dist of event numbers per session.

## From login event collection
from_event = 'login'
sequence_type = 'collection'
event_list = ['send_message','like_message','upload_picture']
start_event_distribution = [.3,.5,.2]
end_event_distribution = [.4,.5,.1]
start_odds_to_continue = [.5,.2,.1]
end_odds_to_continue = [.4,.3,.2]
start_number_of_events = [3,2,1]
end_number_of_events = [3,2,1]

event_params_from_login = [start,end,from_event,sequence_type,event_list,start_event_distribution,end_event_distribution,start_odds_to_continue,
    end_odds_to_continue,start_number_of_events,end_number_of_events]

## From view company event funnel
# from_event = 'view_company_page'
# sequence_type = 'funnel'
# event_list = ['click_create_company','enter_company_info','confirm_company_creation','share_company_creation']
# start_event_distribution = [1,.5,.9,.3]
# end_event_distribution = [1,.3,1,.5]
# start_odds_to_continue = [.5,.2,.1]
# end_odds_to_continue = [.5,.2,.1]
# start_number_of_events = [8,5,2]
# end_number_of_events = [10,6,2]
# 
# event_params_from_view_company = [start,end,from_event,sequence_type,event_list,start_event_distribution,end_event_distribution,start_odds_to_continue,
#     end_odds_to_continue,start_number_of_events,end_number_of_events]


## MAKE DATA
user_table = gu.generate_user_table(users,start,end,monthly_growth,weekend_signup_ratio)
signup_events = gse.generate_signup_events(user_table,signup_event_list,start,end,starting_flow,ending_flow,step_time,weekend_signup_flow_ratio)
login_events = gle.generate_login_events(signup_events[0],signup_event_list,start_user_dist,end_user_dist,starts_odds_of_returning,
    end_odds_of_returning,start,end,start_days_to_return,end_days_to_return,weekend_login_ratio)

events = login_events
events = gae.generate_arbitrary_events(events,event_params_from_login)
# events = gae.generate_arbitrary_events(events,event_params_from_view_company)
events = gtt.generate_test_treaments(events,test_treatment_params)

user_table = signup_events[1]

# billing_table = gb.generate_billing_table(user_table,company_dist,start_monetize_rate,end_monetize_rate,start_churn_rate,end_churn_rate,
#     contract_length,contract_range,start,end)

event_table = events

## Clean and write to CSV
clean_user_table = h.prepare_table(user_table,user_headers,user_include)
clean_event_table = h.prepare_table(event_table,event_headers,event_include)
# clean_billing_table = h.prepare_table(billing_table,billing_headers,billing_include)

h.write_to_csv("fake_dimension_users.csv",clean_user_table)
h.write_to_csv("fake_fact_events.csv",clean_event_table)
# h.write_to_csv("fake_dimension_subscriptions.csv",clean_billing_table)