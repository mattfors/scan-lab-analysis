"""Validate scan data against schema and timing invariants."""

import pandas as pd


def validate_scans_strict(df: pd.DataFrame) -> None:
    """
    Validate scans dataframe strictly against schema and timing invariants.
    
    Raises exceptions immediately if any rule is violated.
    
    Args:
        df: Dataframe containing scan data.
    
    Raises:
        ValueError: If any schema or timing validation rule is violated.
    """
    if df.empty:
        raise ValueError("Dataframe is empty")
    
    # Required columns
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
    missing = required_columns - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
    
    # Validate targetScanStyle values
    invalid_styles = set(df["targetScanStyle"].unique()) - {"compliant", "non_compliant"}
    if invalid_styles:
        raise ValueError(
            f"targetScanStyle contains invalid values: {invalid_styles}. "
            "Must be 'compliant' or 'non_compliant'."
        )
    
    # Validate per-experiment invariants
    for exp_id, group in df.groupby("experimentId", sort=False):
        group = group.sort_values("scanIndex").reset_index(drop=True)
        
        # Check scanIndex is zero-based, increments by 1 with no gaps
        expected_indices = list(range(len(group)))
        actual_indices = group["scanIndex"].tolist()
        if actual_indices != expected_indices:
            raise ValueError(
                f"Experiment {exp_id}: scanIndex is not zero-based or has gaps. "
                f"Expected {expected_indices}, got {actual_indices}"
            )
        
        # Check userName is constant
        if group["userName"].nunique() != 1:
            raise ValueError(
                f"Experiment {exp_id}: userName is not constant across scans"
            )
        
        # Check targetScanStyle is constant
        if group["targetScanStyle"].nunique() != 1:
            raise ValueError(
                f"Experiment {exp_id}: targetScanStyle is not constant across scans"
            )
        
        # Check barcode is constant
        if group["barcode"].nunique() != 1:
            raise ValueError(
                f"Experiment {exp_id}: barcode is not constant across scans"
            )
        
        # Get the style for this experiment
        style = group["targetScanStyle"].iloc[0]
        
        # Check targetClusterSize validity
        if style == "compliant":
            if group["targetClusterSize"].isna().any():
                raise ValueError(
                    f"Experiment {exp_id}: targetClusterSize cannot be null "
                    "when targetScanStyle is 'compliant'"
                )
            cluster_sizes = group["targetClusterSize"].unique()
            if len(cluster_sizes) != 1:
                raise ValueError(
                    f"Experiment {exp_id}: targetClusterSize is not constant"
                )
            cluster_size = cluster_sizes[0]
            if not isinstance(cluster_size, (int, float)) or cluster_size <= 1:
                raise ValueError(
                    f"Experiment {exp_id}: targetClusterSize must be > 1 "
                    f"for compliant style, got {cluster_size}"
                )
        elif style == "non_compliant":
            # targetClusterSize should be null for non_compliant
            if not group["targetClusterSize"].isna().all():
                # Allow if it's present but value doesn't hurt the analysis
                pass
        
        # Validate timestamps are integers and strictly increasing
        if not pd.api.types.is_integer_dtype(group["timestampMs"]):
            raise ValueError(
                f"Experiment {exp_id}: timestampMs must be integer type"
            )
        
        if not (group["timestampMs"].diff().dropna() > 0).all():
            raise ValueError(
                f"Experiment {exp_id}: timestampMs is not strictly increasing"
            )
        
        # Validate elapsedMs are integers and strictly increasing
        if not pd.api.types.is_integer_dtype(group["elapsedMs"]):
            raise ValueError(
                f"Experiment {exp_id}: elapsedMs must be integer type"
            )
        
        if not (group["elapsedMs"].diff().dropna() > 0).all():
            raise ValueError(
                f"Experiment {exp_id}: elapsedMs is not strictly increasing"
            )
        
        # First scan must have elapsedMs == 0
        if group["elapsedMs"].iloc[0] != 0:
            raise ValueError(
                f"Experiment {exp_id}: first scan elapsedMs must equal 0, "
                f"got {group['elapsedMs'].iloc[0]}"
            )
        
        # Validate deltaMs: null only for first scan
        if group["deltaMs"].isna().sum() > 1:
            raise ValueError(
                f"Experiment {exp_id}: deltaMs has more than one null value"
            )
        if group["deltaMs"].isna().any() and not pd.isna(group["deltaMs"].iloc[0]):
            raise ValueError(
                f"Experiment {exp_id}: deltaMs null values must only occur at first scan"
            )
        
        # Validate timing math: deltaMs = timestamp difference
        for i in range(1, len(group)):
            expected_delta = (
                group["timestampMs"].iloc[i] - group["timestampMs"].iloc[i - 1]
            )
            actual_delta = group["deltaMs"].iloc[i]
            if actual_delta != expected_delta:
                raise ValueError(
                    f"Experiment {exp_id}, scanIndex {i}: deltaMs timing mismatch. "
                    f"Expected {expected_delta}, got {actual_delta}"
                )
        
        # Validate timing math: elapsedMs = timestamp - first timestamp
        first_timestamp = group["timestampMs"].iloc[0]
        expected_elapsed = group["timestampMs"] - first_timestamp
        actual_elapsed = group["elapsedMs"]
        if not (expected_elapsed == actual_elapsed).all():
            raise ValueError(
                f"Experiment {exp_id}: elapsedMs timing mismatch. "
                f"elapsedMs must equal timestampMs - first_timestampMs"
            )
