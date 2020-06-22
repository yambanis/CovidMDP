policies = {
    'Lockdown':  {
        'work': .9,  'school': 1,   'home': 0, 'neighbor':  .9
    },
    'Hard Quarantine': {
        'work': .7, 'school': 1,   'home': 0, 'neighbor': .7
    },
    'Light Quarantine': {
        'work': .4, 'school': 1,   'home': 0, 'neighbor': .4
    },
    'Social Distancing': {
        'work': .2, 'school': .2,  'home': 0, 'neighbor': .2
    },
    'Unrestricted': {
        'work': 0,  'school': 0,   'home': 0, 'neighbor': 0
    }
}

costs = {
    'Unrestricted': 0.0,
    'Social Distancing': 0.0266,
    'Light Quarantine': 0.03917,
    'Hard Quarantine': 0.04743,
    'Lockdown': 0.05732
}

closest_actions = {
    'Lockdown':  (['Lockdown', 
                  'Hard Quarantine', 'Light Quarantine', 
                  'Social Distancing', 'Unrestricted'],
                   [.6, .3, .1, .0, .0]),
    'Hard Quarantine':  (['Hard Quarantine', 
                        'Lockdown', 'Light Quarantine', 
                        'Social Distancing', 'Unrestricted'], 
                        [.5, .2, .2, .05, .05]),
    'Light Quarantine': (['Light Quarantine', 
                         'Hard Quarantine', 'Social Distancing', 
                         'Lockdown', 'Unrestricted'],
                          [.5, .2, .2, .05, .05]),
    'Social Distancing': (['Social Distancing', 
                         'Light Quarantine', 'Unrestricted',
                         'Hard Quarantine', 'Lockdown'],
                          [.5, .2, .2, .05, .05]), 
    'Unrestricted': (['Unrestricted', 
                     'Social Distancing', 'Light Quarantine',
                     'Hard Quarantine', 'Lockdown'],
                      [.6, .3, .1, .0, .0])
}