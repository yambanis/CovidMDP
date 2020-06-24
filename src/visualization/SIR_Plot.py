import matplotlib.pyplot as plt
import plotly.graph_objects as go
import numpy as np
import pandas as pd

def plot_average_infection_curve(sims, title):
    fig = go.Figure()
    
    sims = np.array(sims)[:,0]
    
    for col in ['infected']:
        tmp=[sims[i][col] for i in range(len(sims))]
        infected_sims = pd.DataFrame(tmp).T.fillna(0)
        infected_sims['mean'] = infected_sims.apply(np.mean, axis=1)
        infected_sims['sd'] = infected_sims.drop(columns='mean').apply(np.std, axis=1)
        infected_sims = infected_sims.drop(columns=col)
    
    x = infected_sims.index.to_list()
    y = infected_sims['mean']
    sd = infected_sims['sd']

    fig.add_trace(go.Scatter(x=x, y=y,
        fill=None,
        mode='lines',
        line_color='indigo',
         name="Average Curve"
        ))

    fig.add_trace(go.Scatter(x=x, y=y+sd,
        fill=None,
        mode='lines',
        line_color='magenta',
        showlegend=False
       ))

    fig.add_trace(go.Scatter(
        x=x,
        y=y,
        fill='tonexty', # fill area between trace0 and trace1
        mode='lines', line_color='indigo',      name="Standard Deviation"))

    fig.add_trace(go.Scatter(x=x, y=y-sd,
        fill=None,
        mode='lines',
        line_color='magenta',    showlegend=False
        ))


    fig.add_trace(go.Scatter(
        x=x,
        y=y,
        fill='tonexty', # fill area between trace0 and trace1
        mode='lines', line_color='indigo',     showlegend=False
    ))

    fig.update_layout(title = title)

    fig.show()


def make_SIR_graph(data, ):
    d_counts = pd.DataFrame([pd.Series(d).value_counts() for d in data])
    d_counts.fillna(0, inplace=True)

    fig = go.Figure()
    x = list(range(len(d_counts[0])+1))
    
    pop = 55492
    
    fig.add_trace(go.Scatter(x=x, y=d_counts[-1]/pop, name='removed',line_color='green'))
    fig.add_trace(go.Scatter(x=x, y=d_counts[0]/pop, name='susceptible', line_color='blue'))
    fig.add_trace(go.Scatter(x=x, y=d_counts[1]/pop, name='exposed',line_color ='orange'))
    fig.add_trace(go.Scatter(x=x, y=d_counts[2]/pop, name='infected', line_color = 'red'))
    fig.add_trace(go.Scatter(x=x, y=d_counts[3]/pop, name='hospitalized', line_color = 'purple'))
    fig.update_layout(hovermode='x')
    fig.show()
    
    return d_counts

def make_beds_graph(data, actions, step_size, title, max_range=None, color_map=None, make_df=True):
    fig = go.Figure()
    
    if make_df:
        data = pd.DataFrame([pd.Series(d).value_counts() for d in data])
        data.fillna(0, inplace=True)

    color_map = {
        'Lockdown':          'rgb(0.83, 0.13, 0.15)',
        'Hard Quarantine':    'rgb(0.85, 0.35, 0.13)',
        'Light Quarantine':   'rgb(0.97, 0.91, 0.56)',
        'Social Distancing':  'rgb(0.67, 0.88, 0.69)',
        'Unrestricted':        'rgb(0.86, 0.86, 0.86)'    
    }

    pop = 55492
    
    if max_range is None:
        max_range = 1.05*(data[3].max()/pop)

    actions = list(map(color_map.get,  actions))

    x = list(range(len(data)+1))
    
    #\definecolor{royalblue(web)}{rgb}{0.25, 0.41, 0.88}
    fig.add_trace(go.Scatter(x=x, y=data[3]/pop, name='hospitalized', line_color = 'rgb(0.25, 0.41, 0.88)',
                            line=dict(width=3.5),  yaxis="y2"))
    #\definecolor{firebrick}{rgb}{0.7, 0.13, 0.13}
    fig.add_trace(go.Scatter(x=x, y=data[1]/pop, name='exposed', line_color = 'rgb(0.7, 0.13, 0.13)',
                            line=dict(width=4)))
    fig.add_trace(go.Scatter(x=x, y=len(data)*[0.0015], name='capacity', line_color = 'black',
                            line=dict(dash='dash', width = 2), yaxis="y2"))
    fig.update_layout(
        shapes=[
            dict(
                type="rect",
                # x-reference is assigned to the x-values
                xref="x",
                # y-reference is assigned to the plot paper [0,1]
                yref="paper",
                x0=x[step_size*i],
                y0=0,
                x1=x[step_size*(i+1)],
                y1=1,
                fillcolor=a,
                opacity=0.45,
                layer="below",
                line_width=0,
            ) for i,a in enumerate(actions)] 
    )

    for k,v in color_map.items():
        fig.add_trace(go.Bar(x=[None], y=[None], marker=dict(color=v), name = k))

    fig.update_layout(coloraxis = {'colorscale':'deep'}, xaxis={'showgrid': False,},
                      yaxis = {'showgrid': False, 'zerolinecolor': 'black',
                               'zerolinewidth': .5, 'zeroline': False,  'title': 'Proportion of Population'},
                      showlegend=True, hovermode="x")
    
    fig.update_layout(
        xaxis = dict(
            tickmode = 'array',
            tickvals = list(range(0, len(data)+1, 14)),
            ticktext = list(range(0, int(len(data)/7) + 1, 2)),
            title = 'Weeks'
            )
        )
    fig.update_layout(showlegend=False,
        margin=dict(
        l=50,
        r=50,
        b=50,
        t=50,
        pad=0
    ))
    
    fig.update_layout(
        yaxis=dict(
            title="Proportion of Population Exposed",
            titlefont=dict(
                color="rgb(0.7, 0.13, 0.13)"
            ),
            showgrid=False,
            tickfont=dict(
                color="rgb(0.7, 0.13, 0.13)"
            ),
            range=[0, max_range*10]

        ),
        yaxis2=dict(
            title="Proportion of Population Hospitalized",
            titlefont=dict(
                color="rgb(0.25, 0.41, 0.88)"
            ),
            tickfont=dict(
                color="rgb(0.25, 0.41, 0.88)"
            ),
            showgrid=False,
            anchor="x",
            overlaying="y",
            side="right",
            range=[0, max_range]

        ),)

    fig.update_yaxes(automargin=True)
    fig.write_image(f"{title}.pdf")

    fig.show()

def make_SIR_graph(data):
    d_counts = pd.DataFrame([pd.Series(d).value_counts() for d in data])
    d_counts.fillna(0, inplace=True)

    fig = go.Figure()
    x = list(range(len(d_counts[0])+1))

    fig.add_trace(go.Scatter(x=x, y=d_counts[-1]/55e3, name='removed',line_color='green'))
    fig.add_trace(go.Scatter(x=x, y=d_counts[0]/55e3, name='susceptible', line_color='blue'))
    fig.add_trace(go.Scatter(x=x, y=d_counts[1]/55e3, name='exposed',line_color ='orange'))
    fig.add_trace(go.Scatter(x=x, y=d_counts[2]/55e3, name='infected', line_color = 'red'))
    fig.add_trace(go.Scatter(x=x, y=d_counts[3]/55e3, name='hospitalized', line_color = 'purple'))
    fig.update_layout(hovermode='x')
    fig.show()
    
    return d_counts