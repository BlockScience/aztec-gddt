from typing import Union
from cadCAD.configuration import Experiment # type: ignore
from cadCAD.configuration.utils import config_sim # type: ignore
from cadCAD.engine import ExecutionMode, ExecutionContext, Executor # type: ignore
from cadCAD.tools.execution.easy_run import select_config_M_dict # type: ignore
import pandas as pd # type: ignore


def policy_aggregator(a, b):
    if a is None:
        return b
    elif b is None:
        return a
    else:
        return a + b

def sim_run(state_variables,
             params,
             psubs,
             N_timesteps,
             N_samples,
             use_label=False,
             assign_params: Union[bool, set]=True,
             drop_substeps=True,
             exec_mode='local') -> pd.DataFrame:
    """
    Run cadCAD simulations without headaches.
    """

    # Set-up sim_config
    simulation_parameters = {
        'N': N_samples,
        'T': range(N_timesteps),
        'M': params
    }
    sim_config = config_sim(simulation_parameters)

    # Create a new experiment
    exp = Experiment()
    exp.append_configs(sim_configs=sim_config,
                       initial_state=state_variables,
                       partial_state_update_blocks=psubs,
                       policy_ops=[policy_aggregator])
    configs = exp.configs
    
    # Set-up cadCAD executor
    if exec_mode == 'local':
        _exec_mode = ExecutionMode().local_mode
    elif exec_mode == 'single':
        _exec_mode = ExecutionMode().single_mode
    exec_context = ExecutionContext(_exec_mode, additional_objs={'deepcopy_off': True})
    executor = Executor(exec_context=exec_context, configs=configs)

    # Execute the cadCAD experiment
    (records, tensor_field, _) = executor.execute()

    # Parse the output as a pandas DataFrame
    df = pd.DataFrame(records)

    if drop_substeps == True:
        # Drop all intermediate substeps
        first_ind = (df.substep == 0) & (df.timestep == 0)
        last_ind = df.substep == max(df.substep)
        inds_to_drop = (first_ind | last_ind)
        df = df.loc[inds_to_drop].drop(columns=['substep'])
    else:
        pass

    if assign_params == False:
        pass
    else:
        M_dict = configs[0].sim_config['M']
        params_set = set(M_dict.keys())
        
        if assign_params == True:
            pass
        else:
            params_set &= assign_params

        # Logic for getting the assign params criteria
        if type(assign_params) is list:
            selected_params = set(assign_params) & params_set
        elif type(assign_params) is set:
            selected_params = assign_params & params_set
        else:
            selected_params = params_set

        # TODO: evaluate whatever we need to keep track of the `params`
        # Attribute parameters to each row
        # df = df.assign(**select_config_M_dict(configs, 0, selected_params))
        # for i, (_, n_df) in enumerate(df.groupby(['simulation', 'subset', 'run'])):
        #     df.loc[n_df.index] = n_df.assign(**select_config_M_dict(configs,
        #                                                             i,
        #                                                             selected_params))

    # Based on Vitor Marthendal (@marthendalnunes) snippet
    if use_label == True:
        psub_map = {order + 1: psub.get('label', '')
                    for (order, psub)
                    in enumerate(psubs)}
        psub_map[0] = 'Initial State'
        df['substep_label'] = df.substep.map(psub_map)

    return df