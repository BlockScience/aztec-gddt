# Importing Necessary Libraries

import sys
sys.path.append('../')

import numpy as np
import pandas as pd

import plotly.express as px
import seaborn as sns 
import matplotlib.pyplot as plt

import plotly.io as pio
pio.renderers.default = "png"

from IPython.display import display, Markdown
import ipywidgets as widgets
from typing import List, Union


from aztec_gddt.experiment import *
from aztec_gddt.params import *
from aztec_gddt.utils.sim_run import sim_run

# Creating a primitive GUI. 


# NOTE: It would be nice to make this a bit more elegant for re-use, but
# this will do for now. 

################################################
## Creating text input boxes for different    ##
## phase duration parameters. Each parameter  ##
# has one text input box.                     ##
################################################

# Create a styled label widget for the headline
phase_duration_headline_label = widgets.Label(value="Phase Durations", 
                                              style={'font-weight': 'bold', 'font-size': '72px'})

# Proposal Phase Duration 
phase_duration_proposal_label = widgets.Label(value="Proposal Phase:")
phase_duration_proposal_input = widgets.Text(
     value='10',
     placeholder='Enter values separated by commas',
     disabled=False
 )
proposal_duration_proposal_input_box = widgets.HBox([phase_duration_proposal_label, 
                                                     phase_duration_proposal_input])

# Reveal Phase Duration 

phase_duration_reveal_label = widgets.Label(value="Reveal Phase:")
phase_duration_reveal_input = widgets.Text(
     value='10',
     placeholder='Enter values separated by commas',
     disabled=False
 )
proposal_duration_reveal_input_box = widgets.HBox([phase_duration_reveal_label,
                                                   phase_duration_proposal_input])

# Commit Bond Phase Duration
phase_duration_commit_bond_label = widgets.Label(value="Commit Bond Phase:")
phase_duration_commit_bond_input = widgets.Text(
     value='10',
     placeholder='Enter values separated by commas',
     disabled=False
 )
proposal_duration_commit_bond_input_box = widgets.HBox([phase_duration_commit_bond_label,
                                                        phase_duration_commit_bond_input])

all_phase_duration_boxes = [phase_duration_headline_label, 
                            proposal_duration_proposal_input_box,
                            proposal_duration_reveal_input_box,
                            proposal_duration_commit_bond_input_box
                            ]
phase_duration_input_box = widgets.VBox(all_phase_duration_boxes)

################################################
## Creating text input boxes for different    ##
## behavioral probability parameters.         ##
## Each parameter has one text input box.     ##
################################################

proposal_headline_label = widgets.Label(value="Probabilities for Proposals",
                                        style={'font-weight': 'bold', 'font-size': '72px'})

# Proposal Probability
proposal_probability_label = widgets.Label(value="Proposal Probability:")
proposal_probability_input = widgets.Text(value='0.2',
                                          placeholder='Enter values separated by commas',
                                          disabled=False
                                          )

proposal_probability_input_box = widgets.HBox([proposal_probability_label,
                                               proposal_probability_input])

# Block Content Reveal Probability
block_content_reveal_probability_label = widgets.Label(value="Block Content Reveal:")
block_content_reveal_probability_input = widgets.Text(value='0.2',
                                          placeholder='Enter values separated by commas',
                                          disabled=False
                                          )
block_content_reveal_probability_input_box = widgets.HBox([block_content_reveal_probability_label,
                                               block_content_reveal_probability_input])

# Transaction Proof Reveal

tx_proof_reveal_probability_label = widgets.Label(value="Transaction Proof Reveal:")
tx_proof_reveal_probability_input = widgets.Text(value='0.2',
                                          placeholder='Enter values separated by commas',
                                          disabled=False
                                          )
tx_proof_reveal_probability_input_box = widgets.HBox([tx_proof_reveal_probability_label,
                                               tx_proof_reveal_probability_input])


all_probability_proof_boxes = [proposal_headline_label, 
                            proposal_probability_input_box,
                            block_content_reveal_probability_input_box,
                            tx_proof_reveal_probability_input_box
                            ]
probability_proof_input_box = widgets.VBox(all_probability_proof_boxes)


# TODO: Other phase duration parameters



# Combine the existing input boxes into one item. 

param_input_boxes = widgets.HBox([phase_duration_input_box,
                                probability_proof_input_box])

# TODO: Make the numbers below be inputtable through text boxes. 

N_timesteps = 700
N_simulations = 1 

############################################
## Data processing functions for working  ##
## with strings from input text boxes.    ##
############################################

def process_input(input_string):
    # Splitting the string by commas and stripping whitespace
    values_list = [float(item.strip()) for item in input_string.split(',')]
    return values_list

############################################
## A map of parameters to the GUI         ##
## elements that inform them.             ##
############################################

params_sources_dict = {"phase_duration_proposal" : phase_duration_proposal_input,
                      "phase_duration_reveal" : phase_duration_reveal_input,
                      "phase_duration_commit_bond" : phase_duration_commit_bond_input,
                     "proposal_probability_per_user_per_block" : proposal_probability_input,
                      "block_content_reveal_probability" : block_content_reveal_probability_input,
                     "tx_proof_reveal_probability": tx_proof_reveal_probability_input
                     }

def process_inputs_to_params(dict_to_use = None) -> Dict[str, List]:
    """
    Captures the desired parameter values from the input boxes. 
    """

    params_dict = dict()

    if dict_to_use is None:
        dict_to_use = params_sources_dict
    
    for param, source in params_sources_dict.items():
        params_dict[param] = process_input(source.value)
        
    return params_dict

def process_data(df: pd.DataFrame) -> pd.DataFrame:
    # TODO: Change this to actually do processing. 
    # NOTE: At the moment, this just returns the input; no processing. 
    return df

plot1 = widgets.Output()
plot2 = widgets.Output()
plot3 = widgets.Output()

def run_simulation(b: widgets.Button,
                      save_data_to_file: bool = False,
                      filename: str = None):
    """
    This is the logic that will be followed when the 'Run Simulation' button is clicked. 
    """
    params_dict = process_inputs_to_params(dict_to_use = params_sources_dict)
    sim_df = custom_run(params_to_modify=params_dict)
    processed_df = process_data(sim_df)
    
    with plot1:
        sns.scatterplot(data = sim_df,
                 x = "time_l1", 
                 y = "finalized_blocks_count",
                 hue = "proposal_probability_per_user_per_block")
        plt.title('Impact of Proposal Probability on Finalized Blocks ')
        plt.xlabel('Time (L1 Blocks)')
        plt.ylabel('Finalized Blocks Count')
        plt.show()

    with plot2:
        data = pd.DataFrame({
            'x': [1, 2, 3, 4],
            'y1': [10, 15, 13, 18]
        })
        sns.lineplot(data = data, 
                      x='x',
                       y='y1')
        plt.title('Placeholder Plot')
        plt.xlabel('X Label 2')
        plt.ylabel('Y Label 2')
        plt.show()

    with plot3:
        data = pd.DataFrame({
            'x': [1, 2, 3, 4],
            'y1': [10, 15, 13, 18]
        })
        sns.lineplot(x='x', y='y1', data=data)
        plt.title('Another Placeholder Plot')
        plt.xlabel('X Label 3')
        plt.ylabel('Y Label 3')
        plt.show()




button = widgets.Button(description="Run Simulation")
button.on_click(run_simulation)


gui = widgets.VBox([param_input_boxes, button])




# def on_button_clicked(b, 
#                      val_to_set: str = 'gas_threshold_for_tx'):
#     # Using the text input's value
#     vals_list = process_input(text_input.value)
#     params_dict[val_to_set] = vals_list

#     my_table = create_model_params_table(model_name = "Gas Threshold Test",
#                           params_to_modify = params_dict,  
#                           params_to_exclude = ["gas_estimators", "tx_estimators", "slash_params"],                      
#                           display_to_screen = True)

#     sim_df = custom_run(params_to_modify=params_dict)
#     sim_df["num_transactions"] = sim_df['transactions'].apply(lambda x: len(x))
#     sns.scatterplot(data = sim_df,
#                 x = "time_l1",
#                 y = "num_transactions",
#                 hue = "gas_threshold_for_tx")

#     plt.title("Influence of Gas Threshold on Transactions Over Time") #TODO: Generalize
#     plt.show()
    
#     return params_dict

# button.on_click(on_button_clicked)

# gui = widgets.VBox(all_inputs)



