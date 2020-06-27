from scipy.special import expit

def normallize_to_range(x,  x_min, x_max, scale=1, a=-4, b=4):
    x = (x - x_min)/(x_max - x_min)
    x = (x*(b-a)) + a
    return x

def exposed_cost(h, limit=0.025, scale=1):
    y = expit(normallize_to_range(h, 0, limit, scale))
    return y*scale
 
costs = {
  'Lockdown': 0.46009,
  'Hard Quarantine': 0.24601,
  'Light Quarantine': 0.11106,
  'Social Distancing': 0.03357,
  'Unrestricted': 0.0
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