from cadCAD_tools.types import Signal, VariableUpdate
from prey_predator_model.types import PreyPredatorModelParams, PreyPredatorModelState

def p_evolve_time(params: PreyPredatorModelParams, _2, _3, _4) -> Signal:
    return {'delta_days': params['timestep_in_days']}

def s_days_passed(_1, _2, _3,
                  state: PreyPredatorModelState,
                  signal: Signal) -> VariableUpdate:
    return ('days_passed', state['days_passed'] + signal['delta_days'])

def s_delta_days(_1, _2, _3, _4, signal: Signal) -> VariableUpdate:
    return ('delta_days', signal['delta_days'])
