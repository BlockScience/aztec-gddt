from dataclasses import dataclass
from functools import partial 
from inspect import signature
from typing import Any, Callable, Dict

@dataclass

class Agent:
    agent_logic: Dict[str, Callable]
    value: int 
    
    def bind_logic_to_agent(self,
                            logic_dict: Dict[str, Callable]) -> bool:
        """
        Takes a dictionary of logic and 
        """
        for name, func in logic_dict.items():
            func_args = signature(func).parameters
            if "agent" in func_args:
                modified_func = partial(func, agent = self)
            else:
                modified_func = func

            setattr(self, name, modified_func)
        
        return True
    
    def __post_init__(self):
        self.bind_logic_to_agent(self.agent_logic)


def agent_gt_dict_num(agent: Agent, num: int):
    if num > agent.value:
        print("The agent has the larger value.")
    else:
        print("The agent has the smaller value.")

def agent_gt_twice_dict_num(agent: Agent, num: int):
    if 2*num > agent.value:
        print("Multiplying by two, the dictionary has the larger value.")
    else:
        print("Multiplying by two, the dictionary still has the smaller value.")

mock_agent_logic = {
                    "test_normal": agent_gt_dict_num, 
                    "test_doubled": agent_gt_twice_dict_num
                    }

my_first_agent = Agent(agent_logic = mock_agent_logic,
                       value = 4)



    

