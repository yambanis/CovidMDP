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

costs = {'Unrestricted': 0,
 'Social Distancing': 0.1,
 'Light Quarantine': 0.5,
 'Hard Quarantine': 0.65,
 'Lockdown': 0.75}