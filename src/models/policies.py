policies_restrictions_by_name = {
    'Lockdown':  {
        'work': 1,  'school': 1,   'home': 0, 'neighbor':  1
    },
    'Hard Quarantine': {
        'work': .8, 'school': 1,   'home': 0, 'neighbor': .6
    },
    'Medium Quarantine': {
        'work': .6, 'school': 1,   'home': 0, 'neighbor': .4
    },
    'Light Quarantine': {
        'work': .4, 'school': 1,   'home': 0, 'neighbor': .2
    },
    'Social Distancing': {
        'work': .2, 'school': .2,  'home': 0, 'neighbor': .2
    },
    'Unrestricted': {
        'work': 0,  'school': 0,   'home': 0, 'neighbor': 0
    },
    'No_Policy': {
        'work': 0,  'school': 0,   'home': 0, 'neighbor': 0
    }
}

policies_restrictions_by_value = {
    10: {'work':  1,  'school': 1,  'home': 0, 'neighbor':  1},
    9: {'work': .8,  'school': 1,  'home': 0, 'neighbor': .8},
    8: {'work': .6,  'school': 1,  'home': 0, 'neighbor': .6},
    7: {'work': .4,  'school': 1,  'home': 0, 'neighbor': .4},
    6: {'work': .2,  'school': 1,  'home': 0, 'neighbor': .2},
    5: {'work':  1,  'school': 0,  'home': 0, 'neighbor': .5},
    4: {'work': .8,  'school': 0,  'home': 0, 'neighbor': .4},
    3: {'work': .6,  'school': 0,  'home': 0, 'neighbor': .3},
    2: {'work': .4,  'school': 0,  'home': 0, 'neighbor': .2},
    1: {'work': .2,  'school': 0,  'home': 0, 'neighbor': .1},
    0: {'work':  0,  'school': 0,  'home': 0, 'neighbor':  0}
}
