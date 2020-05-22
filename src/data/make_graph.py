import networkx as nx
import pandas as pd
import numpy as np
from tqdm import tqdm
import itertools

def add_person_to_graph(G, person):
    G.add_node(person['id'],
               work = person['work'],
               school = person['school'],
               home = person['home'],
               age = person['idade'],
               private_healthcare = person['private_healthcare'],
               home_id = person['home_id']
    )    

def add_people_to_graph(G, df):
    print('Adding People Nodes')
    df.apply(lambda x: add_person_to_graph(G, x), axis=1)
    print(25*'*')

def add_edge(G, person1, person2, edge_type, edge_zone):
    G.add_edge(person1, person2, edge_type=edge_type, zone=edge_zone)

def add_relation_to_graph(G, df, relation, rewire_chance=1):
    print(f'Adding {relation} Edges')

    for rel in tqdm(df[relation].unique()):
        if pd.notna(rel):
            tmp = df[df[relation] == rel]
            zone = tmp[relation].value_counts().index[0]

            if len(tmp) > 1:
                combinations = np.array(list(itertools.combinations(tmp['id'].values, 2)))
                if rewire_chance < 1:
                    size_combinations = int(len(combinations))
                    size_sample = int(size_combinations*rewire_chance)
                    index_combs = np.random.choice(size_combinations, size=size_sample, replace=False)
                    final_combs = combinations[index_combs]        
                for p1, p2 in final_combs:
                    add_edge(G, p1, p2, relation, zone)  
    print(25*'*')
    
def add_houses_to_graph(G, df):
    print('Adding Houses Edges')
    for h in tqdm(df['home_id'].unique()):
        tmp = df[df['home_id'] == h]
        assert len(np.unique(tmp['home'])) == 1
        zone = tmp['home'].iloc[0]
        if len(tmp) > 1:
            for p1, p2 in list(itertools.combinations(tmp['id'].values, 2)):
                add_edge(G,p1, p2, 'home', zone)
    print(25*'*')
    
def add_works_to_graph(G, df, work_rewire=.05):
    return add_relation_to_graph(G, df, 'work', rewire_chance=work_rewire)


def add_schools_to_graph(G, df, school_rewire=.25):
    return add_relation_to_graph(G, df, 'school', rewire_chance=school_rewire)

def create_graph(df=None, seed=None, school_rewire=.25, work_rewire=.05, file_name=False):
    if df==None: df=pd.read_feather("../../data/raw/work_school_home_sp.feather")

    np.random.seed(seed)
    G = nx.Graph()
    add_people_to_graph(G, df)
    add_houses_to_graph(G, df)
    add_works_to_graph(G, df, work_rewire)
    add_schools_to_graph(G, df, school_rewire)

    if file_name: nx.write_gpickle(G, file_name)
    
    return G


