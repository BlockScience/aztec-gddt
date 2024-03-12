import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.tree import plot_tree
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
import pandas as pd


def f(X: pd.DataFrame,
      y: pd.Series,
      target: str,
      ax_dt: object,
      ax_rf: object,
      label: str = 'target',
      font_size: int = 12):
    """
    Fit DT and RF classifiers for summarizing the sensivity.
    """
    model = DecisionTreeClassifier(class_weight='balanced',
                                   max_depth=5,
                                   )
    rf = RandomForestClassifier()
    model.fit(X, y)
    rf.fit(X, y)

    if model.get_depth() > 0:
    
        df = (pd.DataFrame(list(zip(X.columns, rf.feature_importances_)),
                           columns=['features', 'importance'])
              .sort_values(by='importance', ascending=False)
              )
    
        plot_tree(model,
                  rounded=True,
                  proportion=True,
                  fontsize=font_size,
                  feature_names=X.columns,
                  class_names=['threshold not met', 'threshold met'],
                  filled=True,
                  ax=ax_dt)
        ax_dt.set_title(
            f'Decision tree for {label}, score: {model.score(X, y) :.0%}. N: {len(X) :.2e}')
        sns.barplot(data=df,
                    x=df.features,
                    y=df.importance,
                    ax=ax_rf,
                    label='small')
        plt.setp(ax_rf.xaxis.get_majorticklabels(), rotation=45)
        ax_rf.tick_params(axis='x', labelsize=14)
        ax_rf.set_xlabel("Parameters", fontsize=14)
        ax_rf.set_title(f'Feature importance for the {label}')
        
        return df.assign(target=target)
    else:
        raise ValueError


def param_sensitivity_plot(df: pd.DataFrame,
                           control_params: set,
                           target: str,
                           label: str = 'target',
                           height: int = 12,
                           width: int = 36,
                           font_size: int = 12):
    """
    Plot the sensivity of the 'target' column vs
    a list of control parameters, which are data frame columns.
    """
    
    features = set(control_params) - {target}
    X = df.loc[:, list(features)]
    y = (df[target] > 0)
    # Visualize
    fig, axes = plt.subplots(nrows=2,
                             figsize=(width, height),
                             dpi=100,
                             gridspec_kw={'height_ratios': [3, 1]})
    try:
        f(X, y, 'target', axes[0], axes[1], label, font_size)
    except ValueError:
        plt.close()
    return None


def kpi_sensitivity_plot(df: pd.DataFrame,
                         run_utility: callable,
                         control_params: set,
                         label: str = 'target'):
    """
    Plots the sensitivity of a result dataset towards a KPI.

    Arguments
    df: data frame containing all the simulation results, incl params.
    run_utility: function that aggregates a (subset_id, run) data into a number
    control_params: columns on data frame for doing sensitivity analysis
    """

    labels = df.groupby(['subset', 'run']).apply(run_utility)
    labels.name = 'target'
    labels_df = labels

    cols = ['subset', 'run', *tuple(control_params)]
    subset_map = df[cols].drop_duplicates().set_index(['subset', 'run'])
    feature_df = subset_map

    full_df = feature_df.join(labels_df)
    param_sensitivity_plot(full_df,
                           control_params,
                           'target',
                           label)
