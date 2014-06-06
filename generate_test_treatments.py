import random

def generate_test_treaments(events,test_treatment_params):
    
    treatment_events = []
    
    ttp = test_treatment_params
    test_start_date = ttp[0]
    test_end_date = ttp[1]
    test_event = ttp[2]
    test_event_names = ttp[3]
    test_ratios = ttp[4]
    
    possible_treatments = []
    treated_users = []
    
    for e in events:
        if e[1] > test_start_date and e[1] < test_end_date and e[4] == test_event:
            possible_treatments.append(e)
            treated_users.append(e[0])
    
    treated_users = list(set(treated_users))
    
    for u in treated_users:
        logins = [item for item in possible_treatments if item[0] == u]
        
        login_dates = []
        for l in logins:
            login_dates.append(l[1])
        
        first_login = min(login_dates)
        first_event = [item for item in logins if item[1] == first_login]
        
        treatment_event = make_treatment_event(first_event[0],test_ratios,test_event_names)
        
        treatment_events.append(treatment_event)
    
    full_events = events + treatment_events
    
    return full_events


def make_treatment_event(event,test_ratios,test_event_names):
    user_type = event[5]
    treatment_ratio = test_ratios[user_type - 1]
    
    random_assignment = random.random()
    
    if random_assignment < treatment_ratio[0]:
        treatment_group = test_event_names[0]
    else:
        treatment_group = test_event_names[1]
    
    event = [event[0],event[1],event[2],'test_treatment',treatment_group,user_type]
    
    return event