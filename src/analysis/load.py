"""Load raw CSV files from the data/raw directory."""

import glob
import os
from pathlib import Path

import pandas as pd


def load_all_raw_csv(folder_path: str = "data/raw") -> pd.DataFrame:
    """
    Load all CSV files from the specified folder and concatenate into one dataframe.
    
    Args:
        folder_path: Path to folder containing raw CSV files. Defaults to "data/raw".
    
    Returns:
        Concatenated dataframe from all CSV files.
    
    Raises:
        FileNotFoundError: If no CSV files are found in the folder.
        ValueError: If any CSV file has incorrect columns.
    """
    csv_pattern = os.path.join(folder_path, "*.csv")
    csv_files = sorted(glob.glob(csv_pattern))
    
    if not csv_files:
        raise FileNotFoundError(f"No CSV files found in {folder_path}")
    
    required_columns = {
        "experimentId",
        "userName",
        "targetScanStyle",
        "targetClusterSize",
        "scanIndex",
        "timestampMs",
        "deltaMs",
        "elapsedMs",
        "barcode",
    }
    
    dfs = []
    for csv_file in csv_files:
        df = pd.read_csv(csv_file, dtype={"scanIndex": "Int64"})
        
        # Check all required columns are present
        missing_cols = required_columns - set(df.columns)
        if missing_cols:
            raise ValueError(
                f"CSV file {csv_file} is missing required columns: {missing_cols}"
            )
        
        # Treat empty strings as missing values for nullable columns
        nullable_cols = ["deltaMs", "targetClusterSize"]
        for col in nullable_cols:
            df.loc[df[col] == "", col] = pd.NA
        
        dfs.append(df)
    
    # Concatenate all dataframes
    combined_df = pd.concat(dfs, ignore_index=True)
    
    # Sort by experimentId and scanIndex before validation
    combined_df = combined_df.sort_values(
        by=["experimentId", "scanIndex"], ignore_index=True
    )
    
    return combined_df
