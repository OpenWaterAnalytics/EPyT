Installation
============
There are two ways to install EPyT: using PyPI or downloading the package from the GitHub repository.

Using PyPI:

.. code-block:: console

   $ pip install epyt

Downloading from GitHub:

To download the EPyT package from the `GitHub repository` run the following command:
.. GitHub repository: https://github.com/OpenWaterAnalytics/EPyT

.. code-block:: console

    $ git clone https://github.com/OpenWaterAnalytics/EPyT.git

    $ cd EPyT

Then, install the package by running the following command:

.. code-block:: console

    $ python setup.py install

**Recommendation**

We recommend using Anaconda and either Spyder IDE or PyCharm to run EPyT.

**Spyder IDE**

To configure Spyder IDE for use with EPyT, follow these steps:

Update the Python interpreter in Tools -> Preferences.

    .. image:: https://user-images.githubusercontent.com/2945956/154067349-3aed266f-3a23-4573-8b93-db0b4f224964.png

Select the "Matlab" layout in View -> Window layouts.
Enable interactive plots in Matplotlib by going to Tools -> Preferences -> IPython console -> Graphics -> Graphics backend -> Backend: Automatic.

**Requirements**

- Python >=3.8
- Windows, OSX or Linux
- `EPANET 2.2 <https://github.com/OpenWaterAnalytics/epanet>`_

.. _installation: