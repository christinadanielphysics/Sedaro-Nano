import doctest
import json
from functools import reduce
from operator import __or__
from random import random

# MODELING & SIMULATION

t_0 = 0
delta_t = 1

rod_length = 15
rod_velocity = 1

c = 2

init = {
    'end_A_in_stationary_system': {'time': t_0, 'timeStep': delta_t, 'x': 0, 'y': 0, 'vx': rod_velocity, 'vy': 0}, # 'time' refers to t_A
    'end_B_in_stationary_system': {'time': t_0, 'timeStep': delta_t, 'x': rod_length, 'y': 0, 'vx': rod_velocity, 'vy': 0}, # 'time' refers to t_B
    'light_in_stationary_system': {'time': t_0, 'timeStep': delta_t, 'x': 0, 'y': 0, 'vx': c, 'vy': 0}
}

def propagate(agentId, universe):
    """Propagate agentId from `time` to `time + timeStep`."""
    state = universe[agentId]
    time, timeStep, x, y, vx, vy = state['time'], state['timeStep'], state['x'], state['y'], state['vx'], state['vy']

    if agentId == 'end_A_in_stationary_system':
        x += vx * timeStep
        y += delta_t
    elif agentId == 'end_B_in_stationary_system':
        x += vx * timeStep
        y += delta_t
    elif agentId == 'light_in_stationary_system':
        if not (abs(x - (rod_length + rod_velocity * (time + delta_t - t_0))) >= c * delta_t): # will not be enough room for light to continue travelling at speed c
            vx = -c 
            x += vx * timeStep 
            y += delta_t
        elif not ( abs(x - (rod_velocity * (time + delta_t - t_0))) >= c * delta_t): # will not be enough room for light to continue travelling at speed c
            vx = c 
            x += vx * timeStep 
            y += delta_t
        else: 
            x += vx * timeStep
            y += delta_t


    return {'time': time + timeStep, 'timeStep': timeStep, 'x': x, 'y': y, 'vx': vx, 'vy': vy}

# DATA STRUCTURE

class QRangeStore:
    """
    A Q-Range KV Store mapping left-inclusive, right-exclusive ranges [low, high) to values.
    Reading from the store returns the collection of values whose ranges contain the query.
    ```
    0  1  2  3  4  5  6  7  8  9
    [A      )[B)            [E)
    [C   )[D   )
           ^       ^        ^  ^
    ```
    >>> store = QRangeStore()
    >>> store[0, 3] = 'Record A'
    >>> store[3, 4] = 'Record B'
    >>> store[0, 2] = 'Record C'
    >>> store[2, 4] = 'Record D'
    >>> store[8, 9] = 'Record E'
    >>> store[2, 0] = 'Record F'
    Traceback (most recent call last):
    IndexError: Invalid Range.
    >>> store[2.1]
    ['Record A', 'Record D']
    >>> store[8]
    ['Record E']
    >>> store[5]
    Traceback (most recent call last):
    IndexError: Not found.
    >>> store[9]
    Traceback (most recent call last):
    IndexError: Not found.
    """
    def __init__(self): self.store = []
    def __setitem__(self, rng, value): 
        (low, high) = rng
        if not low < high: raise IndexError("Invalid Range.")
        self.store.append((low, high, value))
    def __getitem__(self, key):
        ret = [v for (l, h, v) in self.store if l <= key < h] 
        if not ret: raise IndexError("Not found.")
        return ret
    
doctest.testmod()

# SIMULATOR

def read(t):
    try:
        data = store[t]
    except IndexError:
        data = []
    return reduce(__or__, data, {})

store = QRangeStore()
store[-999999999, 0] = init
times = {agentId: state['time'] for agentId, state in init.items()}

for _ in range(100):
    for agentId in init:
        t = times[agentId] # get the time for the agentId
        universe = read(t-0.001) # get data
        if set(universe) == set(init):
            newState = propagate(agentId, universe) # propagate
            store[t, newState['time']] = {agentId: newState} # store data
            times[agentId] = newState['time'] # update times

with open('./public/data.json', 'w') as f:
    f.write(json.dumps(store.store, indent=4))