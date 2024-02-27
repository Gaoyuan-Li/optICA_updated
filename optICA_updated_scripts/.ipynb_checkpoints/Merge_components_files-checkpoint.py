import os
import sys
import pandas as pd
import math
import numpy as np

def adjust_matrices(core_count, tmp_dir):
    for core in range(core_count):
        # Adjust S matrix
        s_file = os.path.join(tmp_dir, f"proc_{core}_S.csv")
        s_df = pd.read_csv(s_file, index_col=0)
        num_rows = s_df.shape[0]
        s_df /= np.sqrt(num_rows)
        s_df.to_csv(s_file)

        # Adjust A matrix
        a_file = os.path.join(tmp_dir, f"proc_{core}_A.csv")
        a_df = pd.read_csv(a_file, index_col=0)
        a_df *= np.sqrt(num_rows)
        a_df.to_csv(a_file)
        
def merge_files(core_count, tmp_dir, file_type):
    print(f"\nMerging files of '{file_type}' matrices")
    
    # Print the absolute path of the directory
    abs_tmp_dir = os.path.abspath(tmp_dir)
    all_files = os.listdir(abs_tmp_dir)
    
    # Find all files for this file type, using a general pattern
    files = sorted([f for f in all_files if 'proc_tmp_' in f and f.endswith(f'_{file_type}.csv')])

    # Calculate the number of source files per output file
    files_per_core = int(math.ceil(len(files) / float(core_count)))

    for core in range(core_count):
        start_index = core * files_per_core
        end_index = start_index + files_per_core
        selected_files = files[start_index:end_index]

        # Read and concatenate the files
        df_list = [pd.read_csv(os.path.join(tmp_dir, f), index_col=0) for f in selected_files]
        df_all = pd.concat(df_list, axis=1)

        # Output file name
        output_file = os.path.join(tmp_dir, f"proc_{core}_{file_type}.csv")
        df_all.to_csv(output_file)

def delete_temp_files(tmp_dir):
    print(f"\nDeleting temporary files in directory '{tmp_dir}'")
    for f in os.listdir(tmp_dir):
        file_path = os.path.join(tmp_dir, f)
        try:
            if os.path.isfile(file_path) and 'proc_tmp_' in file_path:
                os.unlink(file_path)
        except Exception as e:
            print(f"Error occurred while deleting file: {file_path}. Error: {e}")
            
# Command-line arguments
if len(sys.argv) != 5 or sys.argv[1] != '-n' or sys.argv[3] != '-o':
    print("Usage: python merge_files.py -n <number_of_cores> -o <output_subdir>")
    sys.exit(1)

core_count = int(sys.argv[2])
out_subdir = sys.argv[4]
tmp_dir = os.path.join(out_subdir, "tmp")  # Temporary directory

merge_files(core_count, tmp_dir, 'S')
merge_files(core_count, tmp_dir, 'A')

# Adjust S and A matrices
adjust_matrices(core_count, tmp_dir)

# Once merging is done, delete the temporary files
delete_temp_files(tmp_dir)
print('\nMerging completed')