import os
import shutil
import tempfile

import matplotlib.pyplot as plt
import numpy as np
from multiprocess import Pool, cpu_count

from epyt import epanet

# Paths
base_dir = os.path.dirname(os.path.abspath(__file__))
inpname = os.path.join(base_dir, '..', '..', 'networks', 'asce-tf-wdst', 'Net1.inp')
inpname = os.path.normpath(inpname)

# Number of simulations
Nsim = 1000
# 5% max uncertainty in base demands
eta_bar = 0.05


def run_simulation(i):
    with tempfile.NamedTemporaryFile(suffix='.inp', delete=False) as tmp_inp_file:
        # tempfile.NamedTemporaryFile(suffix='.bin', delete=False) as tmp_bin_file:

        shutil.copy(inpname, tmp_inp_file.name)
        temp_inp_path = tmp_inp_file.name
        # temp_bin_path = tmp_bin_file.name

    try:

        G = epanet(temp_inp_path, display_msg=False)

        # Modify demands
        base_demands = G.getNodeBaseDemands()[1]
        rand_factors = (2 * np.random.rand(len(base_demands)) - 1) * eta_bar
        new_base_demands = base_demands + rand_factors * base_demands
        G.setNodeBaseDemands(new_base_demands)

        res = G.getComputedHydraulicTimeSeries()
        # res = G.getComputedTimeSeries_ENepanet(tempfile=temp_inp_path, binfile=temp_bin_path)

        print(f'Epoch {i}')
        return res

    finally:
        try:
            # Clean up temporary files
            if os.path.exists(temp_inp_path):
                os.remove(temp_inp_path)
            # if os.path.exists(temp_bin_path):
            #     os.remove(temp_bin_path)
        except:
            pass


if __name__ == '__main__':
    with Pool(cpu_count()) as pool:
        Pmcs = pool.map(run_simulation, range(1, Nsim + 1))

    node_index = 4
    plt.figure(figsize=(12, 6))
    for i in range(Nsim):
        plt.plot(Pmcs[i].Pressure[:, node_index], color='gray', alpha=0.05)

    plt.xlabel('Time Step')
    plt.ylabel('Pressure')
    plt.title('Pressure - 1000 Scenarios at Node 5')
    plt.grid(True)
    plt.tight_layout()
    plt.show()
