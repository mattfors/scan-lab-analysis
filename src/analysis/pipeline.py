"""End-to-end pipeline for processing raw scan data to Parquet."""

from .load import load_all_raw_csv
from .validate import validate_scans_strict
from .io import save_parquet


def process_raw_to_parquet(
    raw_folder: str = "data/raw",
    output_path: str = "data/processed/scans.parquet",
) -> str:
    """
    Load raw CSV files, validate strictly, and save to Parquet.
    
    This is the main entry point for the data ingestion pipeline.
    
    Args:
        raw_folder: Path to folder containing raw CSV files.
        output_path: Path to output Parquet file.
    
    Returns:
        Path to the saved Parquet file.
    
    Raises:
        FileNotFoundError: If no CSV files are found.
        ValueError: If validation fails for any reason.
    """
    print(f"Loading CSV files from {raw_folder}...")
    df = load_all_raw_csv(raw_folder)
    print(f"Loaded {len(df)} scan records from {len(df['experimentId'].unique())} experiments")
    
    print("Validating data against schema and timing invariants...")
    validate_scans_strict(df)
    print("Validation passed!")
    
    print(f"Saving processed data to {output_path}...")
    output_file = save_parquet(df, output_path)
    print(f"Success! Data saved to {output_file}")
    
    return output_file
