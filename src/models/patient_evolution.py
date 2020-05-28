from disease_evolution import incubation, hospitalization_to_removed
from disease_evolution import onset_to_hosp_or_asymp, needs_hospitalization
from disease_states import states_dict

def change_state(person):
    """
    Receives an array representing a person, calls the appropriate function dependending on it's current 
    state and return the person array in the next disease state

    Args:
        person (np.array): Array containing id, state, day of infection and current state duration of a person.

    Returns:
        person (np.array): The same person in the next state of the disease.
    Raises:
        ValueError: If persons time in state (person[3]) is different from zero

    """
    if person[3] != 0:
        raise ValueError("Person's time in state was not zero but was passed to change_state")
    if person[1] == states_dict['exposed']:
        person = exposed_to_infected(person)
        return person
    if person[1] == states_dict['infected']:
        person = infected_to_new_state(person)
        return person
    if person[1] == states_dict['hospitalized']:
        hospitalized_to_removed(person)
        return person

def susceptible_to_exposed(person, day):
    """
    Receives an array representing a person and the current day of simulation and change it's state from
    susceptible to exposed. The new period duration is sampled from incubation().

    Args:
        person (np.array): Array containing id, state, day of infection and current state duration of a person.

    Returns:
        person (np.array): The same person, exposed at the current day
    Raises:
        ValueError: If person's state (person[1]) is different from susceptible

    """
    
    if person[1] != states_dict['susceptible']:
        raise ValueError("Node status different from susceptible")
        
    person[1] = states_dict['exposed']
    person[2] = day
    person[3] = incubation()

    return person

def exposed_to_infected(person):
    """
    Receives an array representing a person and change it's state from exposed to infected.
    The new period duration is sampled from onset_to_hosp_or_asymp().

    Args:
        person (np.array): Array containing id, state, day of infection and current state duration of a person.

    Returns:
        person (np.array): The same person, infected
    Raises:
        ValueError: If person's state (person[1]) is different from exposed or if the state duration has not yet
            reached zero
    """
    if person[1] != states_dict['exposed']:
        raise ValueError("person status different from exposed")
    if person[3] > 0:
        raise ValueError("Not yet time to change")
    
    person[1] = states_dict['infected']
    person[3] = onset_to_hosp_or_asymp()
    
    return person

def infected_to_new_state(person):
    """
    Receives an array representing a person and change it's state from infected to either hospitalized or removed.
    needs_hospitalization(person[4]) determines if the person will need hospitalization based on the person's age
    (person[4] is the person's age in years) and, if the person is going to be hospitalized, the period of stay
    at the hospital is sampled from hospitalization_to_removed().

    Args:
        person (np.array): Array containing id, state, day of infection and current state duration of a person.

    Returns:
        person (np.array): The same person, hospitalized, with hospitalization time, or removed
    Raises:
        ValueError: If person's state (person[1]) is different from infected or if the state duration has not yet
            reached zero
    """
    if person[1] != states_dict['infected']:
        raise ValueError("person status different from infected")
    if person[3] > 0:
        raise ValueError("Not yet time to change")
    
    if needs_hospitalization(person[4]):
        person[1] = states_dict['hospitalized']
        person[3] = hospitalization_to_removed()
    else:
        person[1] = states_dict['removed']
        
    return person

def hospitalized_to_removed(person):
    """
    Receives an array representing a person and change it's state from hospitalized to removed.
    
    Args:
        person (np.array): Array containing id, state, day of infection and current state duration of a person.

    Returns:
        person (np.array): The same person, removed
    Raises:
        ValueError: If person's state (person[1]) is different from hospitalized or if the state duration 
        has not yet reached zero
    """
    if person[1] != states_dict['hospitalized']:
        raise ValueError("person status different from hospitalized")
    if person[3] > 0:
        raise ValueError("Not yet time to change")
        
    person[1] = states_dict['removed']
    
    return person