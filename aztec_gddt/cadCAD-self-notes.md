# Notes to Self on cadCAD and Aztec

## Structure of cadCAD Models

Fundamentally, the **update rule** in this cadCAD model consists of three pieces:
1. **Policy functions**, which return specific types of *Signals* (inheriting from `TypedDict`, so probably any dictionary could be returned here).
2. **State Update functions**, which return a *VariableUpdate* tuple consisting of (`str`, value)
3. **Partial State Update Blocks**, which "wire" together the policy functions to the variables that need to be updated in the block. This creates a coherent chronology for the system's logical evolution.

The **state** of the cadCAD model is a dictionary, subclassed in this instance to `AztecModelState`. The keys of this dictionary correspond to the variables that will be updated throughout the simulation.

The **parameters** of the cadCAD model form another dictionary, subclassed in this instance to `AztecModelParams`. The keys of this dictionary correspond to aspects of the system that can be set prior to beginning a simulation run, but are not changed during the run itself. 

## Reasonable Approach

### Design

1. Identify overall steps in process.
2. For each step, identify state variables that should be changed in that step.
3. Write wireframe state update functions for the state variables that need to be updated, returning a standard format of (`var_name`, new_var_name_value)
4. Determine the signals needed to update the state variable. Add these as arguments to 

## Blocks

1. Time Tracking
2. Exogeneous Processes
3. Agent Actions
4. Evolve Block Process
5. Payouts
6. Dynamically Evolve Time
7. Metrics

