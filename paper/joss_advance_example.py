from epyt import epanet
import matplotlib.pyplot as plt
import numpy as np


# Create a function to run the simulation and return the pressure results
def compute_bounds(G, nsim, base_demands, eta_bar, node_index):
    # Seed number to always get the same random results
    np.random.seed(1)
    # Initialize matrix to save MCS pressures
    pmcs = [None for _ in range(nsim)]
    for i in range(nsim):
        # Compute new base demands
        delta_bd = (2 * np.random.rand(1, len(base_demands))[0] - 1) * eta_bar * base_demands
        new_base_demands = base_demands + delta_bd
        # Set base demands
        G.setNodeBaseDemands(new_base_demands)
        # Compute pressures at each node
        pmcs[i] = G.getComputedHydraulicTimeSeries().Pressure
        print(f"Epoch {i}")

    # Compute upper and lower bounds
    pmulti = []
    for i in range(nsim):
        pmulti.append(pmcs[i][:, node_index - 1])
    pmulti = np.vstack(pmulti)
    ub = np.max(pmulti, axis=0)
    lb = np.min(pmulti, axis=0)
    meanb = np.mean(pmulti, axis=0)

    return pmulti, ub, lb, meanb


def activate_PDA(G):
    type = 'PDA'
    pmin = 0
    preq = 0.1
    pexp = 0.5
    G.setDemandModel(type, pmin, preq, pexp)  # Sets the demand model


if __name__ == "__main__":

    # Prepare network for Monte Carlo Simulations
    # Load network
    inp_name = 'Net2.inp'  # 'L-TOWN.inp'
    G = epanet(inp_name)
    # Pressure driven analysis
    activate_PDA(G)

    # Get nominal base demands
    base_demands = G.getNodeBaseDemands()[1]

    # Number of simulations
    nsim = 100
    # Pressure Simulations at Node 5
    node_id = '11'
    node_index = G.getNodeIndex(node_id)
    # 5% max uncertainty in base demands
    eta_bar = 0.02
    pmulti, ub, lb, meanb = compute_bounds(G, nsim, base_demands, eta_bar, node_index)

    # Plots
    pressure_units = G.units.NodePressureUnits
    plt.rc('xtick', labelsize=8)
    plt.rc('ytick', labelsize=8)
    fig, ax = plt.subplots(figsize=(4, 3))
    ax.plot(ub, 'k')
    ax.plot(lb, 'k')
    ax.plot(meanb, 'b')
    ax.legend(['Upper bound', 'Lower bound', 'Average'], loc='upper right', fontsize=8)
    ax.set_title(f'Pressure bounds, Node ID: {node_id}', fontsize=8)
    ax.set_xlabel('Time (hours)', fontsize=8)
    ax.set_ylabel(f'Pressure ({pressure_units})', fontsize=8)
    ax.grid(True)
    plt.show()
    fig.savefig('figures/paper_pressure_bounds.png', dpi=300)

    # Add leakage at Node ID 7 after 20 hours
    leak_scenario = 50
    leak_start = 20
    leak_value = 50  # GPM unit
    leak_node_id = '7'
    leak_node_index = G.getNodeIndex(leak_node_id)
    leak_pattern = np.zeros(max(G.getPatternLengths()))
    leak_pattern[leak_start:] = 1
    pattern_index = G.addPattern('leak', leak_pattern)
    G.setNodeDemandPatternIndex(leak_node_index, pattern_index)
    G.setNodeBaseDemands(leak_node_index, leak_value)

    scada_pressures = G.getComputedHydraulicTimeSeries().Pressure
    p7 = scada_pressures[:, node_index-1]
    e = p7 - lb
    alert = e < 0
    
    detectionTime = np.argmax(alert>1)

    # Bounds with Leakage
    fig, ax = plt.subplots(figsize=(4, 3))
    ax.plot(ub, 'k')
    ax.plot(lb, 'k')
    ax.plot(p7, 'r')
    ax.grid(True)
    ax.legend(['Upper bound', 'Lower bound', 'Sensor'], loc='upper right', fontsize=8)
    ax.set_title(f'Pressure bounds, Leak Node ID: {leak_node_id}', fontsize=8)
    ax.set_xlabel('Time (hours)', fontsize=8)
    ax.set_ylabel(f'Pressure ({pressure_units})', fontsize=8)
    plt.show()
    fig.savefig('figures/paper_pressure_bounds_leak.png', dpi=300)

    # Leakage alert
    fig, ax = plt.subplots(figsize=(4, 3))

    ax.plot(alert)
    ax.set_title(f'Leakage alert', fontsize=8)
    ax.set_xlabel('Time (hours)', fontsize=8)
    plt.show()
    fig.savefig('figures/paper_leakage_alert.png', dpi=300)
