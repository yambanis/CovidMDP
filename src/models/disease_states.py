states_dict = {
    'susceptible': 0,
    'exposed': 1,
    'infected': 2,
    'hospitalized': 3,
    'removed': -1
}

reverse_states = {
    0: 'susceptible',
    1: 'exposed',
    2: 'infected',
    3: 'hospitalized',
    -1: 'removed'
}

state_to_color = {
    0: 'blue',
    1: 'orange',
    2: 'red',
    3: 'purple',
    -1: 'gray'
}
