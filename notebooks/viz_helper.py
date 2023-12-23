# viz_helper
# very lightweight tools for automatically generating informative plots
from itertools import product
import pandas as pd
from typing import List

import matplotlib.pyplot as plt
import plotly.express as px
import seaborn as sns

def is_column_numeric(df: pd.DataFrame,
                      col_name: str):
    try:
        pd.to_numeric(df[col_name])
        return True
    except ValueError:
        return False

def find_interesting_cols(df, 
                          vars_to_exclude: List[str] = None,
                          numeric_only = True):
    """
    Find columns in a dataframe which:
        1. are actually changed during the simulation
        2. are not in a vars_to_exclude list 

    The flag numeric_only restricts to columns that only have numbers. 
    """

    excluded_vars = vars_to_exclude or []
    # Filter by numeric, according to input arg
    if numeric_only:
        cols_to_use = df.select_dtypes(include=['number']).columns
    else:
        cols_to_use = df.columns
    
    # Process only to variables that are not constant
    interesting_cols = [col for col in cols_to_use 
                        if ((len(df[col].unique()) > 1) and 
                            not(col in excluded_vars))
                        ]
    return interesting_cols

def generate_scatterplots(df: pd.DataFrame, 
                          x_cols: List[str],
                          y_cols: List[str]):
    """
    Helper method to generate plots according to specific parameters. 
    """
    col_pairs = product(x_cols, y_cols)
    for x_col, y_col in col_pairs: 
        try: 
            sns.scatterplot(data = df, 
                            x = x_col, 
                            y = y_col)    
            plt.title(f"Change in {y_col} vs. {x_col}")
            plt.xlabel(f'Value of {x_col}')
            plt.ylabel(f'Value of {y_col}')
            plt.show()
        except Exception as e:
            print("Encountered an issue while generating plots.") 






