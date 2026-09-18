"""
Member 10 - Backend Developer
Loads and caches the cleaned attendance dataset for use across all routes.
"""

import os
import pandas as pd

from database.data_preprocessing import load_and_clean

_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_RAW_CSV_PATH = os.path.join(_BASE_DIR, "data", "attendance.csv")

_cached_df = None


def get_db_dataframe() -> pd.DataFrame:
    """
    Returns the cleaned attendance dataset as a DataFrame, loading and
    cleaning it once (via Member 3's pipeline) and caching the result.
    """
    global _cached_df
    if _cached_df is None:
        _cached_df = load_and_clean(_RAW_CSV_PATH)
    return _cached_df.copy()
