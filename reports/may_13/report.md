# Guilherme Yambanis Thomaz 

06/05/2020

# Graph

The graph is a representation of a population and its relations. On a given graph, a node represents a person and an edge represents some kind of relation, such as, lives with, studies with, buys from etc.

# Spread of Infection

At each time step of the pandemic, a time step representing a single day, the chance of someone becoming infected is given by:

### $1 - (1-\lambda)*(1-p_r)^2$

Where $\lambda$ is the leak probability and $p_r$ is the probability that an infected individual  infects a susceptible individual  that is connected through relation r.

![imagem1](figures\\infection_graph.png)


In the code, we model this behavior as follows:
```python
if G.nodes[node]['status'] == 'susceptible':
    # Infection through leak
    if np.random.random() < lambda_leak:
        newly_infected.append(node)    
    else:
        for contact in adjacencies[1].keys():
            # Infection through infected neighbour
            if G.nodes[contact]['status'] == 'infected' and np.random.random() < p_r:
                    newly_infected.append(node)
                    G.nodes[contact]['contacts_infected'] += 1
                    # Here we model that once infected, additional infections have no effect
                    break  
```

# Graph Types

The graphs will be randomly generated and its type and parameters will be used to model different kinds of societal relationships.

All graphs were generated so that the population size was equal to 5000 people(nodes).

## Relaxed Caveman

The caveman graph was used to model people that cohabit in the same house or living space.
The parameters used were k(size of cliques) = 4, l(number of groups) = 5000/4 and p(probability of rewiring each edge) = 25%. With these parameters we expect to model an average of 4 people per residence.

![imagem1](figures\\relaxed_caveman.png)


![imagem1](figures\\relaxed_caveman_hist.png)

## Scale Free

The scale free graph was used to model the buy and sell relation within the population. It was constructed with the default parameters of the scale free graph from networkx. Here we have "Hubs'' or nodes that have a high number of connections compared to the rest of the population. These nodes represent someone that has a high number of customers.

![imagem1](figures\\scale_free.png)


![imagem1](figures\\scale_free_hist.png)


# Simulating the pandemic

We ran simulations for both the Scale Free and the Relaxed caveman graphs independently to validate their behaviour in contrast to the standard SIR model simulation.

## SIR Simulation

### Parameters: B = 3.2 and v = 0.23

![imagem1](figures\\SIR_simulation.png)


## Caveman simulation

### Parameters : p_r = 0.5, lambda_leak=.01, pop_size=5000, initial_infection = 1/5000)

![imagem1](figures\\relaxed_caveman_simulation.png)


## Scale Free simulation

### Parameters : p_r = 0.5, lambda_leak=.01, pop_size=5000, initial_infection = 1/5000)

![imagem1](figures\\scale_free_simulation.png)


