Usage
=====

Requirements
------------

* Python 3.7
* Windows, OSX or Linux
* `EPANET 2.2 <https://github.com/OpenWaterAnalytics/epanet>`_

.. _installation:

Installation
------------

PyPI:

.. code-block:: console

   $ pip install epyt
   

How to use the Toolkit
----------------------
Minimum Example:

.. code-block:: console
   
   >>> from epyt import epanet
   >>> d = epanet('Net1.inp')
   >>> d.getNodeCount()
   >>> d.getNodeElevations()


How to fix/report bugs
----------------------
To fix a bug Fork the EPyT, Edit the code and make the appropriate change, and then Pull it so that we evaluate it.

Keep in mind that some bugs may exist in the EPANET libraries, in case you are not receiving the expected results.


Recommendation
--------------

Install Anaconda

Run EPyT with Spyder IDE

Run EPyT with PyCharm




