"""
FSM Traversal Engine
Performs state space exploration for complex FSMs with 50+ states
Supports BFS, DFS, reachability analysis, deadlock detection, and cycle detection
"""

from typing import Dict, Set, List, Tuple, Optional
from collections import deque, defaultdict
from pyeda.inter import *
import itertools
from dataclasses import dataclass, field
import time


@dataclass
class FSMState:
    """Represents a state in the FSM"""
    state_vector: Tuple[int, ...]  # Binary representation of state
    state_name: str = ""
    
    def __hash__(self):
        return hash(self.state_vector)
    
    def __eq__(self, other):
        return self.state_vector == other.state_vector
    
    def __str__(self):
        return f"{self.state_name if self.state_name else self.state_vector}"


@dataclass
class FSMTransition:
    """Represents a transition in the FSM"""
    from_state: FSMState
    to_state: FSMState
    input_vector: Tuple[int, ...]
    output_vector: Optional[Tuple[int, ...]] = None
    
    def __str__(self):
        return f"{self.from_state} --[{self.input_vector}]--> {self.to_state}"


class FSMTraversal:
    """
    Main FSM traversal engine for complex sequential designs
    """
    
    def __init__(self, fsm_structure: Dict, verbose: bool = True):
        self.fsm_structure = fsm_structure
        self.verbose = verbose
        
        # Filter out clock and reset signals - they are not FSM inputs
        all_inputs = fsm_structure['inputs']
        self.inputs = sorted([inp for inp in all_inputs if inp.lower() not in ['clk', 'clock', 'rst', 'reset']])
        self.outputs = sorted(list(fsm_structure['outputs']))
        self.state_registers = fsm_structure['state_registers']
        self.expressions = fsm_structure.get('raw_expressions', {})
        self.transition_table = fsm_structure.get('transition_table', {})
        
        # Traversal results
        self.reachable_states: Set[FSMState] = set()
        self.transitions: List[FSMTransition] = []
        self.state_graph: Dict[FSMState, List[FSMTransition]] = defaultdict(list)
        self.deadlock_states: Set[FSMState] = set()
        self.cycles: List[List[FSMState]] = []
        
        # State encoding
        self.num_state_bits = fsm_structure.get('state_bit_width', len(self.state_registers))
        self.num_input_bits = len(self.inputs)
        self.num_output_bits = len(self.outputs)
        
        print(f"\n{'='*80}")
        print(f"FSM Traversal Engine Initialized")
        print(f"{'='*80}")
        print(f"State bits: {self.num_state_bits}")
        print(f"Input bits: {self.num_input_bits}")
        print(f"Output bits: {self.num_output_bits}")
        print(f"Maximum possible states: {2**self.num_state_bits}")
        if self.transition_table:
            print(f"[OK] Using pre-computed transition table ({len(self.transition_table)} entries)")
    
    def _get_reset_state_value(self) -> int:
        """Get the reset state value from FSM parameters"""
        parameters = self.fsm_structure.get('parameters', {})
        # Look for common reset state parameter names
        reset_names = ['RED', 'IDLE', 'S0', 'RESET', 'INIT', 'STATE_0']
        for name in reset_names:
            if name in parameters:
                return parameters[name]
        return 0  # Default to 0
    
    def enumerate_all_states(self) -> List[FSMState]:
        """Generate all possible state encodings"""
        all_states = []
        for i in range(2**self.num_state_bits):
            state_vector = tuple((i >> j) & 1 for j in range(self.num_state_bits))
            state = FSMState(state_vector, f"S{i}")
            all_states.append(state)
        return all_states
    
    def enumerate_all_inputs(self) -> List[Tuple[int, ...]]:
        """Generate all possible input combinations"""
        return list(itertools.product([0, 1], repeat=self.num_input_bits))
    
    def evaluate_next_state(self, current_state: FSMState, input_vector: Tuple[int, ...]) -> Optional[FSMState]:
        """
        Evaluate next state logic given current state and inputs
        """
        # First, try using the pre-computed transition table
        if self.transition_table:
            key = (current_state.state_vector, input_vector)
            if key in self.transition_table:
                next_state_vector = self.transition_table[key]
                return FSMState(next_state_vector)
        
        # Fallback: Create assignment dictionary and evaluate expressions
        assignment = {}
        
        # Assign input values
        for i, inp in enumerate(self.inputs):
            if i < len(input_vector):
                assignment[inp] = input_vector[i]
        
        # Assign current state values
        for i, reg in enumerate(self.state_registers):
            if i < len(current_state.state_vector):
                assignment[reg] = current_state.state_vector[i]
        
        # Evaluate next state (look for next state expressions)
        next_state_vector = []
        
        # Try to find next state logic
        # Look for signals like 'next_state', 'ns', etc.
        next_state_signals = []
        for key in self.expressions.keys():
            key_lower = key.lower()
            if 'next' in key_lower or 'ns' in key_lower or '_n' in key_lower:
                next_state_signals.append(key)
        
        if not next_state_signals:
            # If no explicit next state, assume combinational logic on state registers
            next_state_signals = self.state_registers
        
        for sig in next_state_signals[:self.num_state_bits]:
            if sig in self.expressions:
                try:
                    expr_eval = self.expressions[sig]
                    # Evaluate the expression with current assignments
                    result = self._evaluate_expression(expr_eval, assignment)
                    next_state_vector.append(result)
                except Exception as e:
                    if self.verbose:
                        print(f"  Warning: Could not evaluate {sig}: {e}")
                    return None
        
        if len(next_state_vector) != self.num_state_bits:
            return None
        
        return FSMState(tuple(next_state_vector))
    
    def _evaluate_expression(self, expr, assignment: Dict) -> int:
        """
        Evaluate a PyEDA expression with given variable assignment
        """
        try:
            # Substitute all variables
            result = expr.restrict(assignment)
            # If result is a constant, return it
            if hasattr(result, 'is_zero') and result.is_zero():
                return 0
            elif hasattr(result, 'is_one') and result.is_one():
                return 1
            else:
                # Try to evaluate to a boolean
                return int(bool(result))
        except:
            return 0
    
    def evaluate_outputs(self, current_state: FSMState, input_vector: Tuple[int, ...]) -> Tuple[int, ...]:
        """Evaluate output logic given current state and inputs"""
        assignment = {}
        
        for i, inp in enumerate(self.inputs):
            if i < len(input_vector):
                assignment[inp] = input_vector[i]
        
        for i, reg in enumerate(self.state_registers):
            if i < len(current_state.state_vector):
                assignment[reg] = current_state.state_vector[i]
        
        output_vector = []
        for out in self.outputs:
            if out in self.expressions:
                result = self._evaluate_expression(self.expressions[out], assignment)
                output_vector.append(result)
            else:
                output_vector.append(0)
        
        return tuple(output_vector)
    
    def bfs_traversal(self, initial_state: Optional[FSMState] = None, 
                      max_states: int = 1000) -> Dict:
        """
        Perform breadth-first search traversal of the FSM
        """
        print(f"\n{'='*80}")
        print(f"Starting BFS Traversal")
        print(f"{'='*80}")
        
        start_time = time.time()
        
        # Default initial state - try to get reset value from parameters
        if initial_state is None:
            initial_value = self._get_reset_state_value()
            initial_state_tuple = tuple((initial_value >> i) & 1 for i in range(self.num_state_bits))
            initial_state = FSMState(initial_state_tuple, "RESET")
            print(f"Initial state: {initial_state_tuple} (value={initial_value})")
        
        queue = deque([initial_state])
        visited = {initial_state}
        self.reachable_states = {initial_state}
        self.transitions = []
        self.state_graph = defaultdict(list)
        
        states_explored = 0
        transitions_found = 0
        
        while queue and states_explored < max_states:
            current_state = queue.popleft()
            states_explored += 1
            
            if self.verbose and states_explored % 10 == 0:
                print(f"  Explored {states_explored} states, found {transitions_found} transitions...")
            
            # Try all possible input combinations
            for input_vector in self.enumerate_all_inputs():
                next_state = self.evaluate_next_state(current_state, input_vector)
                
                if next_state is not None:
                    output_vector = self.evaluate_outputs(current_state, input_vector)
                    
                    # Create transition
                    transition = FSMTransition(
                        from_state=current_state,
                        to_state=next_state,
                        input_vector=input_vector,
                        output_vector=output_vector
                    )
                    
                    self.transitions.append(transition)
                    self.state_graph[current_state].append(transition)
                    transitions_found += 1
                    
                    # Add to queue if not visited
                    if next_state not in visited:
                        visited.add(next_state)
                        self.reachable_states.add(next_state)
                        queue.append(next_state)
        
        elapsed_time = time.time() - start_time
        
        print(f"\n{'='*80}")
        print(f"BFS Traversal Complete")
        print(f"{'='*80}")
        print(f"[OK] Reachable states: {len(self.reachable_states)}")
        print(f"[OK] Transitions found: {len(self.transitions)}")
        print(f"[OK] Time elapsed: {elapsed_time:.2f}s")
        
        return {
            'reachable_states': self.reachable_states,
            'transitions': self.transitions,
            'state_graph': self.state_graph,
            'stats': {
                'num_states': len(self.reachable_states),
                'num_transitions': len(self.transitions),
                'time_elapsed': elapsed_time
            }
        }
    
    def dfs_traversal(self, initial_state: Optional[FSMState] = None,
                      max_depth: int = 100) -> Dict:
        """
        Perform depth-first search traversal of the FSM
        """
        print(f"\n{'='*80}")
        print(f"Starting DFS Traversal")
        print(f"{'='*80}")
        
        start_time = time.time()
        
        # Default initial state - try to get reset value from parameters
        if initial_state is None:
            initial_value = self._get_reset_state_value()
            initial_state_tuple = tuple((initial_value >> i) & 1 for i in range(self.num_state_bits))
            initial_state = FSMState(initial_state_tuple, "RESET")
            print(f"Initial state: {initial_state_tuple} (value={initial_value})")
        
        stack = [(initial_state, 0)]  # (state, depth)
        visited = {initial_state}
        self.reachable_states = {initial_state}
        self.transitions = []
        self.state_graph = defaultdict(list)
        
        states_explored = 0
        transitions_found = 0
        
        while stack:
            current_state, depth = stack.pop()
            states_explored += 1
            
            if depth >= max_depth:
                continue
            
            if self.verbose and states_explored % 10 == 0:
                print(f"  Explored {states_explored} states at depth {depth}...")
            
            for input_vector in self.enumerate_all_inputs():
                next_state = self.evaluate_next_state(current_state, input_vector)
                
                if next_state is not None:
                    output_vector = self.evaluate_outputs(current_state, input_vector)
                    
                    transition = FSMTransition(
                        from_state=current_state,
                        to_state=next_state,
                        input_vector=input_vector,
                        output_vector=output_vector
                    )
                    
                    self.transitions.append(transition)
                    self.state_graph[current_state].append(transition)
                    transitions_found += 1
                    
                    if next_state not in visited:
                        visited.add(next_state)
                        self.reachable_states.add(next_state)
                        stack.append((next_state, depth + 1))
        
        elapsed_time = time.time() - start_time
        
        print(f"\n{'='*80}")
        print(f"DFS Traversal Complete")
        print(f"{'='*80}")
        print(f"[OK] Reachable states: {len(self.reachable_states)}")
        print(f"[OK] Transitions found: {len(self.transitions)}")
        print(f"[OK] Time elapsed: {elapsed_time:.2f}s")
        
        return {
            'reachable_states': self.reachable_states,
            'transitions': self.transitions,
            'state_graph': self.state_graph,
            'stats': {
                'num_states': len(self.reachable_states),
                'num_transitions': len(self.transitions),
                'time_elapsed': elapsed_time
            }
        }
    
    def detect_deadlocks(self) -> Set[FSMState]:
        """
        Detect deadlock states (states with no outgoing transitions)
        """
        print(f"\n{'='*80}")
        print(f"Detecting Deadlock States")
        print(f"{'='*80}")
        
        self.deadlock_states = set()
        
        for state in self.reachable_states:
            if state not in self.state_graph or len(self.state_graph[state]) == 0:
                self.deadlock_states.add(state)
        
        print(f"[OK] Found {len(self.deadlock_states)} deadlock state(s)")
        if self.deadlock_states:
            for state in list(self.deadlock_states)[:10]:  # Show first 10
                print(f"  - {state}")
        
        return self.deadlock_states
    
    def detect_cycles(self) -> List[List[FSMState]]:
        """
        Detect cycles in the FSM using DFS-based cycle detection
        """
        print(f"\n{'='*80}")
        print(f"Detecting Cycles")
        print(f"{'='*80}")
        
        self.cycles = []
        visited = set()
        rec_stack = set()
        path = []
        
        def dfs_cycle(state):
            visited.add(state)
            rec_stack.add(state)
            path.append(state)
            
            for transition in self.state_graph.get(state, []):
                next_state = transition.to_state
                
                if next_state not in visited:
                    dfs_cycle(next_state)
                elif next_state in rec_stack:
                    # Found a cycle
                    cycle_start = path.index(next_state)
                    cycle = path[cycle_start:] + [next_state]
                    self.cycles.append(cycle)
            
            path.pop()
            rec_stack.remove(state)
        
        for state in self.reachable_states:
            if state not in visited:
                dfs_cycle(state)
        
        print(f"[OK] Found {len(self.cycles)} cycle(s)")
        if self.cycles:
            for i, cycle in enumerate(self.cycles[:5]):  # Show first 5
                print(f"  Cycle {i+1}: {' -> '.join(str(s) for s in cycle)}")
        
        return self.cycles
    
    def full_analysis(self, method: str = 'bfs', initial_state: Optional[FSMState] = None) -> Dict:
        """
        Perform complete FSM analysis including traversal, deadlock detection, and cycle detection
        """
        print(f"\n{'#'*80}")
        print(f"# FULL FSM ANALYSIS")
        print(f"{'#'*80}")
        
        # Perform traversal
        if method.lower() == 'bfs':
            results = self.bfs_traversal(initial_state)
        else:
            results = self.dfs_traversal(initial_state)
        
        # Detect deadlocks
        deadlocks = self.detect_deadlocks()
        
        # Detect cycles
        cycles = self.detect_cycles()
        
        # Compile final results
        analysis_results = {
            **results,
            'deadlock_states': deadlocks,
            'cycles': cycles,
            'analysis_summary': {
                'total_reachable_states': len(self.reachable_states),
                'total_transitions': len(self.transitions),
                'deadlock_count': len(deadlocks),
                'cycle_count': len(cycles),
                'coverage': f"{len(self.reachable_states) / (2**self.num_state_bits) * 100:.2f}%"
            }
        }
        
        return analysis_results
