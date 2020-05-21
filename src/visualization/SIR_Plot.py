import matplotlib.pyplot as plt
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