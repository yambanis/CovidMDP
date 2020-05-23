def clusterize_relation(df, relation_name='home', x_coord='home_x', y_coord='home_y',
                            new_col_name = 'Neighbourhood', n_participants = 10, seed=13):
    data = []
    means = []

    for zone in df[relation_name].unique():
        if pd.notna(zone):
            tmp = df[df[relation_name] == zone].copy()
            X = tmp[[x_coord, y_coord]]
            n_clusters = int(np.sum(df[relation_name] == zone) / n_participants)
            kmeans = KMeans(n_clusters=n_clusters, random_state=seed).fit(X)
            tmp[new_col_name] = kmeans.labels_

            data.append(tmp)

    df = pd.concat(data)

    return df