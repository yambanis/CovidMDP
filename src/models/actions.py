from scipy.special import expit

def normallize_to_range(x,  x_min, x_max, scale=1, a=-4, b=4):
    x = (x - x_min)/(x_max - x_min)
    x = (x*(b-a)) + a
    return x

def exposed_cost(h, limit=0.0025, scale=1):
    y = expit(normallize_to_range(h, 0, limit, scale))
    return y*scale
 
costs = {
	'Unrestricted': 0.0,
	'Social Distancing': 0.03356922328148252,
 	'Light Quarantine': 0.11105596671140756,
 	'Hard Quarantine': 0.2460112835510519,
 	'Lockdown': 0.6899744811276125
 }

city_restrictions = {
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

action_children = {
	'Lockdown':     	 ['Lockdown',                              'Hard Quarantine'],
    'Hard Quarantine':   ['Hard Quarantine',   'Lockdown',         'Light Quarantine'],
    'Light Quarantine':  ['Light Quarantine',  'Hard Quarantine',  'Social Distancing'],
    'Social Distancing': ['Social Distancing', 'Light Quarantine', 'Unrestricted'],
    'Unrestricted': 	 ['Unrestricted',      'Social Distancing']	
}