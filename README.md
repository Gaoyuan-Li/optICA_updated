# optICA_updated
[![python](https://img.shields.io/badge/Python-3.12-3776AB.svg?style=flat&logo=python&logoColor=white)](https://www.python.org)  [![scikit-learn](https://img.shields.io/badge/scikit--learn-1.4.1-009688.svg?style=flat&logo=Scikit-learn&logoColor=white)](https://fastapi.tiangolo.com)  [![MPI4py](https://img.shields.io/badge/mpi4py-3.1.5-FF4B4B.svg?style=flat&logo=Streamlit&logoColor=white)](https://mpi4py.readthedocs.io/en/stable/)

[![jupyter](https://img.shields.io/badge/Jupyter-Lab-F37626.svg?style=flat&logo=Jupyter)](https://jupyterlab.readthedocs.io/en/stable)

This repository contains scripts for running Independent Component Analysis (ICA) from a set of dimensions and get optimal dimensionality (optICA). It is updated from [SBRG/modulome-workflow/4_optICA](https://github.com/SBRG/modulome-workflow/tree/main/4_optICA), incorporating the latest enhancements and fixes.

## Update - 2/26/2024

###### General Updates

Fixed numpy sparse matrix and the order of creating folders to get compatible with large amount of cores

## Update - 2/21/2024

###### General Adaptations

The scripts have been adapted for compatibility with **Python 3.12** and **scikit-learn 1.4.1**

###### Timeout Mechanism

A timeout mechanism has been implemented. This feature is designed to stop any processor that exceeds a predefined time limit, preventing potential stuck on certain processor.

**Timeout Setting**: 1 hour by default - The timeout limit can be adjusted as needed in the script settings by **-time**

###### LOGFILE Name Update

The format of the LOGFILE name now includes both the date and time.

**Format**: `LOGFILE_yyyy-mm-dd_hh-mm-ss.log`

###### Processor Cores Utilization

The script now recognizes and utilizes the number of threads available in the system instead of being limited to the number of physical cores. 

###### compute_distance.py

The `compute_distance.py` script has been updated to remain functional even when the timeout occurs. This ensures that the script handles timeout events gracefully without crashing or causing data loss.

## Usage

```bash
Usage: run_ica.sh [ARGS] FILE

Arguments
  -i|--iter <n_iter>           Number of random restarts (default: 100)
  -t|--tolerance <tol>         Tolerance (default: 1e-7)
  -n|--n-cores <n_cores>       Number of cores to use (default: 8)
  -max|--max-dim <max_dim>     Maximum dimensionality for search (default: n_samples)
  -min|--min-dim <min_dim>     Minimum dimensionality for search (default: 20)
  -s|--step-size <step_size>   Dimensionality step size (default: n_samples/25)
  -o|--outdir <path>           Output directory for files (default: current directory)
  -l|--logfile                 Name of log file to use if verbose is off (default: ica.log)
  -v|--verbose                 Send output to stdout rather than writing to file
  -h|--help                    Display help information
  -time|--time-out             Timeout for each ICA run in seconds (default: 3600)
```

## Example Usage

```bash
./run_ica.sh -n 16 -min 100 -max 300 -i 96 -v -time 3600 -o ../_aeruPHAGE_p_aeru ../log_tpm_p_aeru.csv
```

## Conda environment

Please install the conda environment using the yml file

**Change the 'prefix' before install it**

```python
conda env create -f optICA_updated.yml
```

## Notes

OptICA may take dozens of hours to run using default arguments, depending on the size of your dataset. This can be accelerated by

1. using more processors (i.e. a supercomputer),
1. loosening the tolerance (e.g. `-t 1e-3`), or
1. increasing the dimensionality step size (e.g. `--step-size 20`).

Also, if your dataset has over 500 datasets, we recommend limiting the maximum dimensionality to the number of unique conditions in your dataset.

The `run_ica.sh` script produces three files and a subdirectory:

- `M.csv`: The **M** matrix
- `A.csv`: The **A** matrix
- `dimension_analysis.pdf`: Plot showing the optimal ICA dimensionality
- `ica_runs/`: A subdirectory containing all the **M** and **A** matrices for all dimensions
