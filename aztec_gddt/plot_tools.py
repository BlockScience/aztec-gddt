from pandas import DataFrame
from typing import Callable, Dict, List, Optional
import pandas as pd 

import matplotlib.pyplot as plt  # type: ignore
import seaborn as sns  # type: ignore

import aztec_gddt.metrics as m

from sklearn.tree import plot_tree  # type: ignore
from sklearn.tree import DecisionTreeClassifier  # type: ignore
from sklearn.ensemble import RandomForestClassifier  # type: ignore

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

phases = ["proposal", "reveal", "commit_bond", "rollup", "race"]
fixed_info_cols = [f"is_{phase}_fixed" for phase in phases]


KPIs = {"proportion_race_mode": m.find_proportion_race_mode,
        "proportion_slashed_prover": m.find_proportion_slashed_due_to_prover,
        "proportion_slashed_sequencer": m.find_proportion_slashed_due_to_sequencer,
        "proportion_skipped": m.find_proportion_skipped,
        "average_duration_finalized_blocks": m.find_average_duration_finalized_blocks,
        "stddev_duration_finalized_blocks": m.find_stddev_duration_finalized_blocks,
        "average_duration_nonfinalized_blocks": m.find_average_duration_nonfinalized_blocks,
        "stddev_duration_nonfinalized_blocks": m.find_stddev_duration_nonfinalized_blocks,
        #       "stddev_payoffs_to_sequencers": m.find_stddev_payoffs_to_sequencers,
        #       "stddev_payoffs_to_provers": m.find_stddev_payoffs_to_provers,
        "delta_total_revenue_agents": m.find_delta_total_revenue_agents
        }


trajectory_id_columns = ['simulation', 'subset', 'run']

# default_agg_columns = ['simulation', 'subset', 'run'] + governance_surface_params


def extract_df(df_to_use: DataFrame,
               params_to_use: List[str] = None,
               trajectory_kpis: Dict[str, Callable] = None,
               agg_columns: List[str] = None,
               cols_to_drop: List[str] = None) -> DataFrame:
    """
    Given a Timestep Tensor, return a Trajectory Tensor
    """

    if params_to_use is None:
        params_to_use = governance_surface_params

    if agg_columns is None:
        agg_columns = trajectory_id_columns

    cols_to_group = agg_columns + params_to_use

    kpi_dfs: list[pd.Series] = []
    for kpi_name, kpi_func in trajectory_kpis.items():
        kpi_s: pd.Series = df_to_use.groupby(cols_to_group).apply(kpi_func, include_groups=False)
        kpi_s.name = kpi_name
        kpi_dfs.append(kpi_s)

        
    all_kpi_df: DataFrame = pd.concat(kpi_dfs, axis=1)

    return all_kpi_df


def add_additional_info(old_df: DataFrame) -> DataFrame:
    new_df = old_df.copy()
    phases = ["proposal", "reveal", "commit_bond", "rollup", "race"]
    for phase in phases:
        new_col_name = f"is_{phase}_fixed"
        new_df[new_col_name] = (
            old_df[f'phase_duration_{phase}_min_blocks'] == old_df[f'phase_duration_{phase}_max_blocks'])

    return new_df


def create_param_impact_dist_plots_by_column(df_to_use: DataFrame,
                                             param_cols: List[str],
                                             kpi_col: str,
                                             divider_col: str,
                                             plot_height: float = 4,
                                             plot_width: float = 4,
                                             shade_val = True):
    # Define the custom color palette
    custom_palette = ["#000000", "#FF0000"]
    sns.set_palette(custom_palette)

    dividers = df_to_use[divider_col].unique().tolist()
    num_dividers = len(df_to_use[divider_col].unique())

    fig_width = plot_width * num_dividers
    fig_height = plot_height * len(param_cols)

    # Create a plot object with subplots.
    fig, axs = plt.subplots(len(param_cols), num_dividers,
                            figsize=(fig_width, fig_height),
                            sharex='row', sharey='row',
                            gridspec_kw={'hspace': 0.5, 'wspace': 0.5})
    fig.subplots_adjust(top=0.8)
    fig.suptitle(f"Impact of {divider_col}", y = 0.95)

    for row_num, param in enumerate(param_cols):
        for col_num, divider in enumerate(dividers):
            sns.kdeplot(
                data=df_to_use[df_to_use[divider_col] == divider],
                x=kpi_col,
                hue=param,
                ax=axs[row_num, col_num],
                palette=custom_palette,
                shade = shade_val
            )
            axs[row_num, col_num].set_title(f"KPI measurements for \n {param} and {divider}.",
                                            fontsize=10)

    plt.show()
    return fig, axs


def create_phase_impact_dist_plots_by_kpi(df_to_use: DataFrame,
                                          phase: str,
                                          kpi_cols: List[str],
                                          plot_height: float = 3.5,
                                          plot_width: float = 3.5):
    # Generate column names based on phase
    phase_duration_min = f'phase_duration_{phase}_min_blocks'
    phase_duration_max = f'phase_duration_{phase}_max_blocks'
    is_phase_fixed = f'is_{phase}_fixed'
    phase_cols = [phase_duration_min, phase_duration_max, is_phase_fixed]

    # Define the custom color palette
    custom_palette = ["#000000", "#FF0000"]
    sns.set_palette(custom_palette)

    fig_width = plot_width * len(kpi_cols)
    fig_height = plot_height * len(phase_cols)

    # Create a plot object with subplots.
    fig, axs = plt.subplots(len(phase_cols), len(kpi_cols),
                            figsize=(fig_width, fig_height),
                            sharex='row', sharey='row',
                            gridspec_kw={'hspace': 0.65, 'wspace': 0.65})
    fig.subplots_adjust(top=0.89)
    fig.suptitle("Phase Impact Plot", y = 1.0)

    for row_num, param in enumerate(phase_cols):
        for col_num, kpi in enumerate(kpi_cols):
            sns.kdeplot(
                data=df_to_use,
                x=kpi,
                hue=param,
                ax=axs[row_num, col_num],
                palette=custom_palette,
#                common_norm = True
            )
            axs[row_num, col_num].set_title(f"Impact of \n {param} \n on {kpi}",
                                            fontsize=10)

    plt.show()
    return fig, axs


def create_decision_tree_importances_plot(data: DataFrame,
                                          col_name: str,
                                          params_to_use: List = [],
                                          plot_width: float = 36,
                                          plot_height: float = 12):
    if len(params_to_use) == 0:
        features = governance_surface_params + fixed_info_cols
    else:
        features= params_to_use

    X = data.loc[:, features]
    y = data.loc[:, col_name] > data.loc[:, col_name].median()

    model = DecisionTreeClassifier(max_depth=3)
    rf = RandomForestClassifier()
    model.fit(X, y)
    rf.fit(X, y)

    X_cols = list(X.columns)

    rf_df = (DataFrame(list(zip(X_cols, rf.feature_importances_)),
                       columns=['features', 'importance'])
             .sort_values(by='importance', ascending=False)
             )

    fig, axes = plt.subplots(nrows=2,
                             figsize=(plot_width, plot_height),
                             dpi=100,
                             gridspec_kw={'height_ratios': [3, 1]})

    (ax_dt, ax_rf) = axes[0], axes[1]
    plot_tree(model,
              rounded=True,
              proportion=True,
              fontsize=8,
              feature_names=X_cols,
              class_names=['threshold not met', 'threshold met'],
              filled=True,
              ax=ax_dt)
    ax_dt.set_title(
        f'Decision Tree for {col_name}, score: {model.score(X, y) :.0%}. N: {len(X) :.2e}')
    sns.barplot(data=rf_df,
                x=rf_df.features,
                y=rf_df.importance,
                ax=ax_rf,
                label='small')
    plt.setp(ax_rf.xaxis.get_majorticklabels(), rotation=45)
    ax_rf.set_title('Feature importance')
    plt.show()

    return fig, axes
