policies = {
    'unrestricted': {
        'work': {
            'regular':         0,
            'high_impact':     0,
            'essential':       0
        },
        'school': {
            'nursery':              0,
            'elementary school':    0,
            'high school':          0,
            'university':           0,
            'others':               0
        },
        'neighbor': 0,
        'home': 0
    },
    'lockdown': {
        'work': {
            'regular':         .9,
            'high_impact':     .7,
            'essential':       0
        },
        'school': {
            'nursery':              1,
            'elementary school':    1,
            'high school':          1,
            'university':           1,
            'others':               1
        },
        'neighbor': .8,
        'home': 0
    },
    'restrict_jobs_8_and_schools': {
        'work': {
            'regular':         .8,
            'high_impact':     .3,
            'essential':       0
        },
        'school': {
            'nursery':              1,
            'elementary school':    1,
            'high school':          1,
            'university':           1,
            'others':               1
        },
        'neighbor': .8,
        'home': 0
    },
    'restrict_jobs_5_and_schools': {
        'work': {
            'regular':         .5,
            'high_impact':     .2,
            'essential':       0
        },
        'school': {
            'nursery':              1,
            'elementary school':    1,
            'high school':          1,
            'university':           1,
            'others':               1
        },
        'neighbor': .5,
        'home': 0
    },
    'restrict_jobs_3_and_schools': {
        'work': {
            'regular':         .3,
            'high_impact':     .1,
            'essential':       0
        },
        'school': {
            'nursery':              1,
            'elementary school':    1,
            'high school':          1,
            'university':           1,
            'others':               1
        },
        'neighbor': .3,
        'home': 0
    },
    'restrict_jobs_3_and_high_uni': {
        'work': {
            'regular':         .3,
            'high_impact':     .1,
            'essential':       0
        },
        'school': {
            'nursery':              0,
            'elementary school':    0,
            'high school':          1,
            'university':           1,
            'others':               1
        },
        'neighbor': .3,
        'home': 0
    },
    'restrict_jobs_3': {
        'work': {
            'regular':         .3,
            'high_impact':     .1,
            'essential':       0
        },
        'school': {
            'nursery':              0,
            'elementary school':    0,
            'high school':          0,
            'university':           0,
            'others':               0
        },
        'neighbor': .3,
        'home': 0
    },
}


def get_policy_cost(action):
    policy = policies[action]
    work_cost = (policy['work']['essential']*100 
                 + policy['work']['high_impact']*40
                 + policy['work']['regular']*20)
    school_cost = (policy['school']['elementary school']*3
                   + policy['school']['nursery']*2
                   + policy['school']['university']*2
                   + policy['school']['high school']*2
                   + policy['school']['others']*1)
    home_cost = policy['home']
    neighbor_cost = policy['neighbor']*1

    return work_cost + school_cost + home_cost + neighbor_cost