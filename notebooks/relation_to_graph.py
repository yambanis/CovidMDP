def add_work_to_graph(G, trab_esc):
    for w in tqdm(trab_esc['work'].unique()):
        if pd.notna(w):
            tmp = trab_esc[trab_esc['work'] == w]
            zone = tmp['work'].value_counts().index[0]

            if len(tmp) > 1:
                possible_combinations = np.array(list(itertools.combinations(tmp['id'].values, 2)))
                size_comb = int(len(possible_combinations))
                index_combs = np.random.choice(size_comb, size=int(size_comb*.05))
                real_combs = possible_combinations[index_combs]        
                for p1, p2 in real_combs:
                    add_edge(G, p1, p2, 'work', zone)

    print(len(G.nodes))
    print(len(G.edges))
    print(50*'*')