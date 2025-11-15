"""
Behavioral FSM Simulator
Simulates behavioral Verilog to extract FSM transitions
Uses symbolic execution to build state transition table
"""

from typing import Dict, Set, Tuple, List
from pyverilog.vparser.ast import *


class BehavioralFSMSimulator:
    """
    Simulates behavioral Verilog FSM to extract transition table
    """
    
    def __init__(self, module, state_registers, inputs, outputs, parameters=None):
        self.module = module
        self.state_registers = state_registers
        # Filter out clock and reset signals
        self.inputs = [inp for inp in inputs if inp.lower() not in ['clk', 'clock', 'rst', 'reset']]
        self.outputs = list(outputs)
        self.transition_table = {}
        self.parameters = parameters if parameters is not None else {}
        
        # If parameters were not passed, extract them
        if not self.parameters:
            self._extract_parameters()
        
        # Determine bit widths
        self.state_bits = self._get_register_width(state_registers)
        self.num_inputs = len(self.inputs)
    
    def _extract_parameters(self):
        """Extract parameter definitions from the module"""
        for item in self.module.items:
            if isinstance(item, Decl):
                for decl in item.list:
                    if isinstance(decl, Parameter):
                        param_name = decl.name
                        param_value = self._eval_const(decl.value)
                        self.parameters[param_name] = param_value
                        print(f"      DEBUG: Parameter {param_name} = {decl.value} -> {param_value}")
        
        if self.parameters:
            print(f"   Found parameters: {self.parameters}")
    
    def _get_register_width(self, registers):
        """Get the bit width of state registers"""
        if not registers:
            return 1
            
        total_bits = 0
        for reg_name in registers:
            # Look for register declarations to find width
            for item in self.module.items:
                if isinstance(item, Decl):
                    for decl in item.list:
                        if isinstance(decl, Reg) and decl.name == reg_name:
                            if decl.width:
                                # Has explicit width [msb:lsb]
                                if hasattr(decl.width, 'msb') and hasattr(decl.width, 'lsb'):
                                    msb = self._eval_const(decl.width.msb)
                                    lsb = self._eval_const(decl.width.lsb)
                                    total_bits += (msb - lsb + 1)
                                else:
                                    total_bits += 1
                            else:
                                # Single bit register
                                total_bits += 1
        
        # If no width found from declarations, default to 2 bits
        return total_bits if total_bits > 0 else 2
    
    def _eval_const(self, node):
        """Evaluate a constant expression"""
        # Handle Rvalue (wrapper for value)
        if isinstance(node, Rvalue):
            return self._eval_const(node.var)
        
        if isinstance(node, IntConst):
            value_str = node.value
            # Handle Verilog number formats: <width>'<base><value>
            # Examples: 2'b00, 4'd15, 8'hFF
            if "'" in value_str:
                parts = value_str.split("'")
                if len(parts) == 2:
                    base_and_value = parts[1]
                    if base_and_value[0] == 'b':  # Binary
                        return int(base_and_value[1:], 2)
                    elif base_and_value[0] == 'd':  # Decimal
                        return int(base_and_value[1:], 10)
                    elif base_and_value[0] == 'h':  # Hexadecimal
                        return int(base_and_value[1:], 16)
                    elif base_and_value[0] == 'o':  # Octal
                        return int(base_and_value[1:], 8)
            # Plain integer
            return int(value_str, 0)  # Auto-detect base
        elif isinstance(node, Constant):
            return int(node.value, 0)
        return 0
    
    def build_transition_table(self) -> Dict:
        """
        Build FSM transition table by symbolically simulating all state/input combinations
        Returns dict: {(state_tuple, input_tuple): next_state_tuple}
        """
        print(f"\n{'~'*80}")
        print(f"Building FSM Transition Table via Simulation")
        print(f"{'~'*80}")
        print(f"State bits: {self.state_bits}")
        print(f"Inputs: {len(self.inputs)}")
        
        # Find the next-state logic (combinational always block)
        next_state_always = self._find_next_state_logic()
        
        if not next_state_always:
            print("[WARNING] No next-state logic found (no combinational always block with case)")
            return {}
        
        # Simulate all possible state/input combinations
        num_states = 2 ** self.state_bits
        num_input_combos = 2 ** self.num_inputs
        
        print(f"Simulating {num_states} states × {num_input_combos} inputs = {num_states * num_input_combos} transitions...")
        
        transitions_found = 0
        
        for state_val in range(num_states):
            state_tuple = tuple((state_val >> i) & 1 for i in range(self.state_bits))
            
            for input_val in range(num_input_combos):
                input_tuple = tuple((input_val >> i) & 1 for i in range(self.num_inputs))
                
                # Simulate the next-state logic
                next_state = self._simulate_next_state(state_tuple, input_tuple, next_state_always)
                
                if next_state is not None:
                    self.transition_table[(state_tuple, input_tuple)] = next_state
                    transitions_found += 1
        
        print(f"[OK] Built transition table with {transitions_found} transitions")
        return self.transition_table
    
    def _find_next_state_logic(self):
        """Find the always block that contains next-state logic (combinational)"""
        always_blocks = []
        candidate = None
        
        for item in self.module.items:
            if isinstance(item, Always):
                always_blocks.append(item)
                
                # Check if this contains next-state assignments
                if self._contains_next_state_assignment(item):
                    # Save as candidate (will use the LAST one found, which is typically combinational)
                    candidate = item
        
        if candidate:
            return candidate
        
        return None
    
    def _contains_next_state_assignment(self, always_block):
        """Check if always block assigns to next_state registers"""
        # Look for assignments to signals with 'next' in the name
        return self._check_statement_for_next_state(always_block.statement)
    
    def _check_statement_for_next_state(self, stmt):
        """Recursively check if statement assigns to next_state"""
        if stmt is None:
            return False
        
        if isinstance(stmt, (BlockingSubstitution, NonblockingSubstitution)):
            if hasattr(stmt.left, 'var') and hasattr(stmt.left.var, 'name'):
                var_name = stmt.left.var.name
                if 'next' in var_name.lower() or var_name in self.state_registers:
                    return True
        
        if isinstance(stmt, Block):
            return any(self._check_statement_for_next_state(s) for s in stmt.statements)
        
        if isinstance(stmt, IfStatement):
            return (self._check_statement_for_next_state(stmt.true_statement) or
                    self._check_statement_for_next_state(stmt.false_statement))
        
        if isinstance(stmt, CaseStatement):
            if hasattr(stmt, 'caselist'):
                for case in stmt.caselist:
                    if hasattr(case, 'statement') and case.statement:
                        # case.statement can be a single Block or a list
                        if isinstance(case.statement, list):
                            for s in case.statement:
                                if self._check_statement_for_next_state(s):
                                    return True
                        else:
                            if self._check_statement_for_next_state(case.statement):
                                return True
        
        return False
    
    def _simulate_next_state(self, state_tuple, input_tuple, always_block):
        """
        Simulate the next-state logic for given state and input
        Returns the next state tuple
        """
        # Create a simple context with current state and inputs
        context = {}
        
        # Map state registers to their integer values (multi-bit)
        for i, reg in enumerate(self.state_registers):
            # Convert state tuple to integer for this register
            state_int = 0
            for bit_idx in range(min(len(state_tuple), self.state_bits)):
                state_int |= (state_tuple[bit_idx] << bit_idx)
            context[reg] = state_int
        
        # Map inputs to input values
        for i, inp in enumerate(self.inputs):
            if i < len(input_tuple):
                context[inp] = input_tuple[i]
        
        # Execute the always block and track next_state assignments
        next_state_values = {}
        self._execute_statement(always_block.statement, context, next_state_values)
        
        # Convert next_state integer value back to bit tuple
        next_state_int = None
        
        # Look for next_state assignment
        # First, look for explicit next_state register
        if 'next_state' in next_state_values:
            next_state_int = next_state_values['next_state']
        else:
            # Try other common next-state names
            for key in next_state_values:
                if 'next' in key.lower() or 'ns' in key.lower():
                    next_state_int = next_state_values[key]
                    break
        
        # If we found a next state value, convert to tuple
        if next_state_int is not None:
            next_state_list = []
            for bit_idx in range(self.state_bits):
                next_state_list.append((next_state_int >> bit_idx) & 1)
            return tuple(next_state_list)
        
        return None
    
    def _execute_statement(self, stmt, context, next_state_values):
        """Execute a statement and update next_state_values"""
        if stmt is None:
            return
        
        if isinstance(stmt, Block):
            for s in stmt.statements:
                self._execute_statement(s, context, next_state_values)
        
        elif isinstance(stmt, CaseStatement):
            # Evaluate the case expression
            case_value = self._evaluate_expression(stmt.comp, context)
            
            # Find matching case
            if hasattr(stmt, 'caselist'):
                matched = False
                for case in stmt.caselist:
                    if self._case_matches(case, case_value, context):
                        if hasattr(case, 'statement') and case.statement:
                            if isinstance(case.statement, list):
                                for s in case.statement:
                                    self._execute_statement(s, context, next_state_values)
                            else:
                                self._execute_statement(case.statement, context, next_state_values)
                        matched = True
                        break
                # Handle default case if no other case matched
                if not matched:
                    for case in stmt.caselist:
                        if not hasattr(case, 'cond') or not case.cond: # Default case
                            if hasattr(case, 'statement') and case.statement:
                                if isinstance(case.statement, list):
                                    for s in case.statement:
                                        self._execute_statement(s, context, next_state_values)
                                else:
                                    self._execute_statement(case.statement, context, next_state_values)
                                break
        
        elif isinstance(stmt, IfStatement):
            # Evaluate condition
            cond_value = self._evaluate_expression(stmt.cond, context)
            
            if cond_value:
                self._execute_statement(stmt.true_statement, context, next_state_values)
            elif stmt.false_statement:
                self._execute_statement(stmt.false_statement, context, next_state_values)
        
        elif isinstance(stmt, (BlockingSubstitution, NonblockingSubstitution)):
            # Evaluate right-hand side and assign to left
            if hasattr(stmt.left, 'var') and hasattr(stmt.left.var, 'name'):
                lhs = stmt.left.var.name
                rhs_value = self._evaluate_expression(stmt.right, context)
                next_state_values[lhs] = rhs_value
    
    def _evaluate_expression(self, expr, context):
        """Evaluate an expression in the given context"""
        if expr is None:
            return 0
        
        if isinstance(expr, (IntConst, Constant)):
            return self._eval_const(expr)
        
        if isinstance(expr, Identifier):
            name = expr.name
            # Check parameters first
            if name in self.parameters:
                return self.parameters[name]
            # Then check context
            return context.get(name, 0)
        
        # Handle Rvalue wrapper
        if isinstance(expr, Rvalue):
            return self._evaluate_expression(expr.var, context)
        
        # Unary operators
        if isinstance(expr, Unot):
            operand = self._evaluate_expression(expr.right, context)
            return 1 if operand == 0 else 0
        
        if isinstance(expr, Ulnot):
            operand = self._evaluate_expression(expr.right, context)
            return 1 if operand == 0 else 0
        
        # Binary operators
        if isinstance(expr, Eq):
            left = self._evaluate_expression(expr.left, context)
            right = self._evaluate_expression(expr.right, context)
            return 1 if left == right else 0
        
        if isinstance(expr, NotEq):
            left = self._evaluate_expression(expr.left, context)
            right = self._evaluate_expression(expr.right, context)
            return 1 if left != right else 0
        
        if isinstance(expr, Land):
            left = self._evaluate_expression(expr.left, context)
            right = self._evaluate_expression(expr.right, context)
            return 1 if (left and right) else 0
        
        if isinstance(expr, Lor):
            left = self._evaluate_expression(expr.left, context)
            right = self._evaluate_expression(expr.right, context)
            return 1 if (left or right) else 0
        
        if isinstance(expr, And):
            left = self._evaluate_expression(expr.left, context)
            right = self._evaluate_expression(expr.right, context)
            return left & right
        
        if isinstance(expr, Or):
            left = self._evaluate_expression(expr.left, context)
            right = self._evaluate_expression(expr.right, context)
            return left | right
        
        if isinstance(expr, Xor):
            left = self._evaluate_expression(expr.left, context)
            right = self._evaluate_expression(expr.right, context)
            return left ^ right
        
        return 0
    
    def _case_matches(self, case, value, context):
        """Check if a case item matches the value"""
        if not hasattr(case, 'cond') or not case.cond:
            # Default case
            return True
        
        for cond in case.cond:
            cond_val = self._evaluate_expression(cond, context)
            if cond_val == value:
                return True
        
        return False
