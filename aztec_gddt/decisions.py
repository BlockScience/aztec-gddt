from random import choice
from typing import Dict

from aztec_gddt.helper import bernoulli_trial 

################################
## Begin general  things      ##
################################

def always_true(info_dict: Dict) -> bool:
    return True

################################
## End general  things        ##
################################


################################
## Begin agent decisions     ## 
################################

################################
## Commit Bond Reveal         ##
################################

def decide_commit_bond_reveal_random(vars_dict: Dict) -> bool:
    """ 
    Make a probabilistic decision based on model parameters. 
    """
    probability = vars_dict["probability"]
    decision = bernoulli_trial(probability=probability)
    return decision




################################
## End agent decisions        ##
################################

################################
## Begin system decisions     ## 
################################

def decide_proving_marketplace_use_random(vars_dict: Dict) -> bool:
    """
    Decide whether to use the proving marketplace, based on system parameters. 
    """
    probability = vars_dict["probability"]
    decision = bernoulli_trial(probability = probability)
    return decision

def decide_prover_random(params: dict,
                         state: dict):
    agents = state['agents']
    bond_amount = params['commit_bond_amount']

    potential_provers: list = [a_id 
                               for (a_id, a) 
                               in agents.items() 
                               if a.is_prover and a.balance >= bond_amount]
    prover = choice(potential_provers)
    return prover 
 
################################
## End agent decisions        ## 
################################