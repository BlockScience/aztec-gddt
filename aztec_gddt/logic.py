from cadCAD_tools.types import Signal, VariableUpdate
from aztec_gddt.types import AztecModelParams, AztecModelState

def p_evolve_time(params: AztecModelParams, _2, _3, _4) -> Signal:
    return {'delta_blocks': params['timestep_in_blocks']}

def s_block_time(_1, _2, _3,
                  state: AztecModelState,
                  signal: Signal) -> VariableUpdate:
    return ('block_time', state['block_time'] + signal['delta_blocks'])

def s_delta_blocks(_1, _2, _3, _4, signal: Signal) -> VariableUpdate:
    return ('delta_blocks', signal['delta_blocks'])
