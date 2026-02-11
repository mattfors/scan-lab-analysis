"""Save processed scan data to Parquet format."""

import os

import pandas as pd


def save_parquet(
    df: pd.DataFrame,
    output_path: str = "data/processed/scans.parquet",
) -> str:
    """
    Save dataframe to Parquet format with proper data types.
    
    Args:
        df: Dataframe containing validated scan data.
        output_path: Path to output Parquet file. Defaults to "data/processed/scans.parquet".
    
    Returns:
        The output path where file was saved.
    
    Raises:
        ValueError: If dataframe is invalid or cannot be saved.
    """
    if df.empty:
        raise ValueError("Cannot save empty dataframe to Parquet")
    
    # Create output directory if it doesn't exist
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
    
    # Ensure correct data types
    df_out = df.copy()
    
    # Integer columns (millisecond timestamps and indices)
    int_cols = ["scanIndex", "timestampMs", "elapsedMs"]
    for col in int_cols:
        if col in df_out.columns:
            df_out[col] = pd.array(df_out[col], dtype="Int64")
    
    # deltaMs can be null, so use nullable integer
    if "deltaMs" in df_out.columns:
        df_out["deltaMs"] = pd.array(df_out["deltaMs"], dtype="Int64")
    
    # targetClusterSize can be null, so use nullable integer
    if "targetClusterSize" in df_out.columns:
        df_out["targetClusterSize"] = pd.array(
            df_out["targetClusterSize"], dtype="Int64"
        )
    
    # String columns
    str_cols = ["experimentId", "userName", "targetScanStyle", "barcode"]
    for col in str_cols:
        if col in df_out.columns:
            df_out[col] = df_out[col].astype("string")
    
    # Save to Parquet
    df_out.to_parquet(output_path, index=False, engine="pyarrow")
    
    return output_path
