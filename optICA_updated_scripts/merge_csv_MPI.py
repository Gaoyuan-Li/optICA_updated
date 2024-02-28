import os
import pandas as pd
from mpi4py import MPI
import argparse
import math
import re
import numpy as np
import sys

def adjust_matrices(core_count, tmp_dir, rank):
    """
    Adjusts matrices for the given core's files within the MPI environment.
    Each core adjusts its own S and A matrices.
    """
    # Adjust S matrix
    s_file = os.path.join(tmp_dir, f"proc_{rank}_S.csv")
    if os.path.exists(s_file):  # Check if the file exists
        s_df = pd.read_csv(s_file, index_col=0)
        num_rows = s_df.shape[0]
        s_df /= np.sqrt(num_rows)
        s_df.to_csv(s_file)

    # Adjust A matrix
    a_file = os.path.join(tmp_dir, f"proc_{rank}_A.csv")
    if os.path.exists(a_file):  # Check if the file exists
        a_df = pd.read_csv(a_file, index_col=0)
        # This assumes num_rows is defined or accessible. Adjust accordingly.
        a_df *= np.sqrt(num_rows)
        a_df.to_csv(a_file)

def merge_and_cleanup_files(folder, file_type, rank, size, comm):
    """
    Merge files of a given type (S or A) into equally sized groups, leaving any leftovers unprocessed.
    Save the merged files in the 'tmp' folder. Abort the run if the number of files is less than the number of cores.
    """
    tmp_files_path = os.path.join(folder, "tmp")
    files = [f for f in os.listdir(tmp_files_path) if re.match(f"proc_tmp_\\d+_{file_type}.csv", f)]
    files.sort(key=lambda x: int(re.search(r'(\d+)', x).group()))

    total_files = len(files)

    # Abort the run if the number of proc_tmp files is lower than the number of cores
    if total_files < size:
        if rank == 0:  # Let only the root process print the error message
            print(f"Error: The number of {file_type} files ({total_files}) is less than the number of cores ({size}). Aborting.")
        comm.Abort()  # Abort the run across all processes

    files_to_be_merged = total_files - (total_files % size)
    files_per_process = files_to_be_merged // size

    start_index = rank * files_per_process
    end_index = start_index + files_per_process

    process_files = files[start_index:end_index]
    dfs = []
    for file_index, f in enumerate(process_files):
        df = pd.read_csv(os.path.join(tmp_files_path, f))
        if file_index > 0:
            df = df.drop(df.columns[0], axis=1)
        dfs.append(df)
    merged_df = pd.concat(dfs, axis=1)

    if dfs:  # Check if there are dataframes to merge
        output_file = os.path.join(tmp_files_path, f"proc_{rank}_{file_type}.csv")
        merged_df.to_csv(output_file, index=False)

    # Synchronize processes before cleanup
    comm.Barrier()

    # Process 0 handles deletion of processed files
    if rank == 0:
        for i in range(files_to_be_merged):
            os.remove(os.path.join(tmp_files_path, files[i]))

def main():
    parser = argparse.ArgumentParser(description='Merge CSV files with MPI, ensuring equal distribution of files.')
    parser.add_argument('-o', '--output_folder', required=True, help='Output folder name')
    parser.add_argument('-n', '--num_cores', type=int, required=True, help='Number of cores')
    args = parser.parse_args()

    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()

    if rank == 0:
        print("\nMerging csv files")
    
    if size != args.num_cores:
        if rank == 0:
            print("Error: The number of MPI processes does not match the number of specified cores.")
        sys.exit()

    merge_and_cleanup_files(args.output_folder, "S", rank, size, comm)
    merge_and_cleanup_files(args.output_folder, "A", rank, size, comm)

    # Adjust matrices
    tmp_dir = os.path.join(args.output_folder, "tmp")
    adjust_matrices(size, tmp_dir, rank)
    
    if rank == 0:
        print("\nMerging completed")

if __name__ == "__main__":
    main()
