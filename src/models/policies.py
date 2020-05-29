policies_restrictions = {
    'Lockdown'     :  {'work' : 1,  'school' : 1,   'home' : 0, 'neighbor'   :  1},
    'Hard Quarantine'   :  {'work' : .8, 'school' : 1,  'home' : 0, 'neighbor'  : .6},
    'Medium Quarantine' :  {'work' : .6, 'school' : 1,  'home' : 0, 'neighbor'  : .4},
    'Light Quarantine'  :  {'work' : .4, 'school' : 1,  'home' : 0, 'neighbor'  : .2},
    'Social Distancing'   :  {'work' : .2, 'school' : .2, 'home' : 0, 'neighbor' : .2},
    'Unrestricted'      :  {'work' : 0,  'school' : 0,   'home' : 0, 'neighbor'   : 0},
    'No_Policy'         :  {'work' : 0,  'school' : 0,   'home' : 0, 'neighbor'   : 0}
}