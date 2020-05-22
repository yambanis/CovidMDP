import matplotlib.pyplot as plt
import plotly.graph_objects as go
import numpy as np
import pandas as pd

def plot_SIR_timeline(time_series, name=None, save=False):
    plt.plot(time_series.index, time_series['susceptible'], label = 'susceptible')
    plt.plot(time_series.index, time_series['infected'], label = 'infected')
    plt.plot(time_series.index, time_series['removed'], label = 'removed')
    plt.legend()
    plt.title(f'SP Network - {name}')
    if save: plt.savefig(f'SP network Simulation- {name}.png', fromat='png', dpi = 300)
    plt.show()
    
def plot_capacity(time_series, name=None, save=True):
    plt.plot(time_series.index, time_series['hospitalized'], label = 'Hospitalized')
    plt.plot(time_series.index, len(time_series.index)*[0.0025], label = 'Capacity')
    plt.legend()
    plt.title(f'Hospital Beds - {name}')
    if save: plt.savefig(f'Hospital Beds- {name}.png', fromat='png', dpi = 300)
    plt.show()


def plot_average_infection_curve(sims):
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

    fig.update_layout(title = 'Average infection Curve - Relaxed Caveman')

    fig.show()