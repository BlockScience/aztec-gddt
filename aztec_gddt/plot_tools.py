from pandas import DataFrame
from typing import Callable, Dict, List

import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.tree import plot_tree
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier

######################################
## Background information for Aztec ##
######################################

governance_surface_params = [
    'phase_duration_proposal_min_blocks',
    'phase_duration_proposal_max_blocks',
    'phase_duration_reveal_min_blocks',
    'phase_duration_reveal_max_blocks',
    'phase_duration_commit_bond_min_blocks',
    'phase_duration_commit_bond_max_blocks',
    'phase_duration_rollup_min_blocks',
    'phase_duration_rollup_max_blocks',
    'phase_duration_race_min_blocks',
    'phase_duration_race_max_blocks',
    'reward_per_block'
]

trajectory_id_columns = ['simulation', 'subset', 'run']

default_agg_columns = ['simulation', 'subset', 'run'] + governance_surface_params

def extract_df(df_to_use: DataFrame,
               trajectory_kpis: Dict[str, Callable],
               agg_columns: List[str] = None,
               num_rows: int = 1000,
               cols_to_drop: List[str] = None) -> DataFrame:

    if agg_columns is None:
        agg_columns = default_agg_columns
    
    group_df = df_to_use.head(num_rows).groupby(agg_columns) #group data
    df_start = group_df.apply(lambda x: True) #create series
    col_names = list(df_start.index.names)
    data_values = list(df_start.index.values)
    base_df = DataFrame(columns = col_names, data=data_values)
    for kpi_name, kpi_func in trajectory_kpis.items():
        base_df[kpi_name] = group_df.apply(kpi_func)

    if not(cols_to_drop is None):
        base_df.drop(columns = cols_to_drop,
                     inplace = True)
    
    return base_df

def create_param_impact_dist_plots(df_to_use: DataFrame,
                                   param_cols: List[str],
                                   kpi_cols: List[str],
                                   fig_height: float = 8,                               
                                   fig_width: float = 10):
    # Define the custom color palette 
    custom_palette = ["#000000", "#FF0000"]  
    sns.set_palette(custom_palette)

# Create a plot object with subplots. 
    fig, axs = plt.subplots(len(param_cols), len(kpi_cols), 
                      figsize=(fig_height,  fig_width), 
                      sharex='row', sharey='row', 
                      gridspec_kw={'hspace': 0.5})
    fig.subplots_adjust(top=0.95)
    fig.suptitle("Parameter Impact Plot")

    for row_num, param in param_cols.enumerate():
        for col_num, kpi in kpi_cols.enumerate():
            sns.kdeplot(
                        data = df_to_use,
                        x = kpi[row_num],
                        hue = param,
                        ax = axs[row_num,col_num],
                        palette = custom_palette
            )
            axs[row_num, col_num].set_title(f"Impact of {param} on {kpi}")
    
    plt.show()
    return fig, axs

def create_decision_tree_importances_plot(df_to_use: DataFrame,
                                         params_to_use: List,
                                         kpi: str):
    features = list(set(params_to_use) - {kpi})
    X = df_to_use.loc[:, features]
    y = df_to_use.loc[:, kpi] > df_to_use.loc[:, kpi].median()

    model = DecisionTreeClassifier(max_depth=3)
    rf = RandomForestClassifier()
    model.fit(X, y)
    rf.fit(X, y)

    rf_df = (DataFrame(list(zip(X.columns, rf.feature_importances_)),
                        columns=['features', 'importance'])
            .sort_values(by='importance', ascending=False)
            )


    fig, axes = plt.subplots(nrows=2,
                                figsize=(36, 12),
                                dpi=100,
                                gridspec_kw={'height_ratios': [3, 1]})

    (ax_dt, ax_rf) = axes[0], axes[1]
    plot_tree(model,
                rounded=True,
                proportion=True,
                fontsize=8,
                feature_names=X.columns,
                class_names=['threshold not met', 'threshold met'],
                filled=True,
                ax=ax_dt)
    ax_dt.set_title(
        f'Decision tree, score: {model.score(X, y) :.0%}. N: {len(X) :.2e}')
    sns.barplot(data=rf_df,
                x=rf_df.features,
                y=rf_df.importance,
                ax=ax_rf,
                label='small')
    plt.setp(ax_rf.xaxis.get_majorticklabels(), rotation=45)
    ax_rf.set_title('Feature importance')
    plt.show()

    return fig, axes

