# Experiments on discretizations of dynamical systems

This package contains the notebook with all experiments run for the paper
```
@article{guiheneuf2022discrsim,
  title = {Discrepancy and discretizations of circle expanding maps II: simulations},
  author = {{Guiheneuf, Pierre-Antoine and Monge, Maurizio}},
  year = {2022},
  archivePrefix = {arXiv},
  eprint = {TODO},
}
```
and additionally the Python code library making it possible.

# How to run the code

The notebook and underlying libray requires Sage (we used Sage 9.2, but
a more recent version should work as well).
```
cd <downloaded_code_directory>
sage -n jupyterlab
```
From Jupyter notebook interface open `FinalPresentation.ipynb` and run
its cells.

Some Python packages are required (tqdm, dotmap, joblib, dill) but there
is no need to install them manually, as the first cell in the notebook will
make sure they are properly installed in Sage package repository.

NOTE: the notebook will memoize results in an "sqlite" database that will
require approximately 500Gb of disk space.

# Documentation

The underlying Python library (Python directory) is based on a reduced version
of the code developed in project
[CompInvMeas-Python](https://bitbucket.org/fph/compinvmeas-python/src/master/)
by Federico Poloni, Isaia Nisoli, Stefano Galatolo and Maurizio Monge, in the
context of the work enabling rigorous computation of invariant measures
of dynamical systems.

This is used mainly in the computation of the fixed point
vector of the Perron-Frobenius operator of a dynamical system, that we take as
reference approximation of the SRB measure for reference in our experiments
on discretized dynamics.

Additionally to it our Python code library contains:

* facilities to discretize in different ways a dinamical system (`discretization.py`)
* facilities to compute discrepance and Wasserstein distance between probability
  measures on the interval and on the circle (`discrete_distance.py`)
* facilities to "memoize" the results of computations in an sqlite database
  (`memoize_db.py`)
* a small convenience tool to display the global variables accessed inside the cells
  (`inspection_magics.py`)
