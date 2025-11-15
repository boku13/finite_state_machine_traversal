"""
Verilog Parser for FSM Extraction
Parses gate-level and behavioral Verilog to extract FSM structure
"""

from pyverilog.vparser.parser import parse, VerilogCodeParser
from pyverilog.vparser.ast import *
from pyeda.inter import *
from typing import Dict, Set, List, Tuple
import re
import os
import sys
from behavioral_simulator import BehavioralFSMSimulator
import ast


class VerilogFSMParser:
    """Parser to extract FSM structure from Verilog descriptions"""
    
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.module = None
        self.inputs = set()
        self.outputs = set()
        self.registers = set()
        self.wires = set()
        self.expressions = {}
        self.state_registers = []
        self.next_state_logic = {}
        self.output_logic = {}
        self.parameters = {}
        
        self.GATE_MAP = {
            'And': And, 'Or': Or, 'Xor': Xor, 'Not': Not,
            'Nand': Nand, 'Nor': Nor, 'Xnor': Xnor, 'Buf': lambda x: x
        }
    
    def parse_verilog(self):
        """Parse Verilog file and extract module structure"""
        print(f"\n{'='*80}")
        print(f"Parsing Verilog file: {self.filepath}")
        print(f"{'='*80}")
        
        # Windows-compatible parsing - monkey-patch subprocess to avoid external tools
        import subprocess
        import tempfile
        
        # Save original subprocess.call
        original_call = subprocess.call
        
        # Read the Verilog content
        with open(self.filepath, 'r') as f:
            content = f.read()
        
        def mock_subprocess_call(cmd, *args, **kwargs):
            """Mock subprocess that creates the expected output file"""
            # PyVerilog expects preprocessor to create 'preprocess.output'
            if isinstance(cmd, list) and len(cmd) > 0:
                # Find the output file argument
                for i, arg in enumerate(cmd):
                    if arg == '-o' and i + 1 < len(cmd):
                        output_file = cmd[i + 1]
                        # Write our content to the output file
                        with open(output_file, 'w') as f:
                            f.write(content)
                        return 0
            # Default: write to preprocess.output
            with open('preprocess.output', 'w') as f:
                f.write(content)
            return 0
        
        # Replace subprocess.call temporarily
        subprocess.call = mock_subprocess_call
        
        try:
            # Now parse with mocked preprocessor
            ast, _ = parse([self.filepath])
        finally:
            # Restore original subprocess.call
            subprocess.call = original_call
            # Clean up temp files
            for temp_file in ['preprocess.output', 'parser.out', 'parsetab.py']:
                if os.path.exists(temp_file):
                    try:
                        os.unlink(temp_file)
                    except:
                        pass
        
        if ast is None:
            raise ValueError("Failed to parse Verilog file")
        
        self.module = ast.description.definitions[0]
        
        # Extract port information
        self._extract_ports()
        
        # Extract declarations
        self._extract_declarations()
        
        print(f"\nModule: {self.module.name}")
        print(f"Inputs: {sorted(list(self.inputs))}")
        print(f"Outputs: {sorted(list(self.outputs))}")
        print(f"Registers: {sorted(list(self.registers))}")
        print(f"Wires: {sorted(list(self.wires))}")
        
        return True
    
    def _extract_ports(self):
        """Extract input and output ports"""
        if hasattr(self.module, 'portlist') and self.module.portlist:
            for p in self.module.portlist.ports:
                if isinstance(p.first, Input):
                    port_name = p.first.name
                    # Filter out clock and reset signals - they are not FSM inputs
                    if port_name.lower() not in ['clk', 'clock', 'rst', 'reset']:
                        self.inputs.add(port_name)
                elif isinstance(p.first, Output):
                    self.outputs.add(p.first.name)
    
    def _extract_declarations(self):
        """Extract register and wire declarations"""
        for item in self.module.items:
            if isinstance(item, Decl):
                for decl_item in item.list:
                    if isinstance(decl_item, Reg):
                        self.registers.add(decl_item.name)
                    elif isinstance(decl_item, Wire):
                        self.wires.add(decl_item.name)
                    elif isinstance(decl_item, Parameter):
                        self._process_parameter(decl_item)

    def _process_parameter(self, param):
        """Process a parameter declaration"""
        if not hasattr(param, 'name') or not hasattr(param, 'value'):
            return
        
        param_name = param.name
        param_value = self._eval_const(param.value)
        
        self.parameters[param_name] = param_value
        print(f"    - Found parameter: {param_name} = {param_value}")

    def verilog_to_pyeda_expressions(self) -> Dict[str, any]:
        """
        Parse Verilog gate-level description and convert to PyEDA boolean expressions
        Returns a dictionary of PyEDA expressions for each output port
        """
        print(f"\n{'-'*80}")
        print(f"Converting to PyEDA expressions")
        print(f"{'-'*80}")
        
        # Initialize expressions with input variables
        self.expressions = {name: exprvar(name) for name in self.inputs}
        
        # Also add registers as variables (for sequential logic)
        for reg in self.registers:
            if reg not in self.expressions:
                self.expressions[reg] = exprvar(reg)
        
        # Get all items (gate instantiations, assignments, etc.)
        items = list(self.module.items)
        
        # First, try to extract behavioral logic (always blocks)
        behavioral_extracted = self._extract_behavioral_logic(items)
        
        if behavioral_extracted:
            print(f"[OK] Extracted behavioral FSM logic")
            return self.expressions
        
        # If no behavioral logic, fall back to gate-level parsing
        # Iteratively resolve wire expressions
        iteration = 1
        while items:
            print(f"\nPass {iteration}: Resolving {len(items)} remaining items...")
            iteration += 1
            next_items = []
            processed_this_pass = False
            
            for item in items:
                if isinstance(item, InstanceList):
                    if self._process_gate_instance(item):
                        processed_this_pass = True
                    else:
                        next_items.append(item)
                elif isinstance(item, Assign):
                    if self._process_assign(item):
                        processed_this_pass = True
                    else:
                        next_items.append(item)
                else:
                    # Keep non-processable items for next pass
                    next_items.append(item)
            
            # Check if stuck in a loop
            if not processed_this_pass and next_items:
                print("\n[WARNING] Could not resolve all expressions.")
                print("   Possible combinational loops or unsupported constructs.")
                unresolved_wires = set()
                for item in next_items:
                    if isinstance(item, InstanceList):
                        inst = item.instances[0]
                        unresolved_wires.add(inst.portlist[0].argname.name)
                print(f"   Unresolved wires: {sorted(list(unresolved_wires))}")
                break
            
            items = next_items
        
        # Extract final expressions for outputs
        final_expressions = {o: self.expressions[o] for o in self.outputs if o in self.expressions}
        
        if len(final_expressions) != len(self.outputs):
            print(f"\n[WARNING] Not all outputs were resolved.")
            unresolved = self.outputs - set(final_expressions.keys())
            print(f"   Unresolved outputs: {sorted(list(unresolved))}")
        
        print(f"\n[OK] Parsing complete: {len(final_expressions)}/{len(self.outputs)} outputs resolved")
        return final_expressions
    
    def _extract_behavioral_logic(self, items) -> bool:
        """
        Extract FSM structure from behavioral Verilog (always blocks, case statements)
        Returns True if behavioral logic was found and extracted
        """
        found_behavioral = False
        
        for item in items:
            if isinstance(item, Always):
                found_behavioral = True
                self._process_always_block(item)
            elif isinstance(item, Assign):
                # Handle continuous assignments for outputs
                self._process_continuous_assign(item)
        
        return found_behavioral
    
    def _process_always_block(self, always_block):
        """Process an always block to extract FSM logic"""
        statement = always_block.statement
        
        # Handle if-else statements in always blocks
        if isinstance(statement, Block):
            for stmt in statement.statements:
                self._process_statement(stmt)
        else:
            self._process_statement(statement)
    
    def _process_statement(self, stmt):
        """Process individual statements in always blocks"""
        if isinstance(stmt, IfStatement):
            self._process_if_statement(stmt)
        elif isinstance(stmt, CaseStatement):
            self._process_case_statement(stmt)
        elif isinstance(stmt, NonblockingSubstitution) or isinstance(stmt, BlockingSubstitution):
            self._process_assignment(stmt)
        elif isinstance(stmt, Block):
            for s in stmt.statements:
                self._process_statement(s)
    
    def _process_if_statement(self, if_stmt):
        """Process if-else statements"""
        if if_stmt.true_statement:
            self._process_statement(if_stmt.true_statement)
        if if_stmt.false_statement:
            self._process_statement(if_stmt.false_statement)
    
    def _process_case_statement(self, case_stmt):
        """Process case statements to extract state transitions"""
        if not hasattr(case_stmt, 'caselist') or not case_stmt.caselist:
            return
        
        for case in case_stmt.caselist:
            if hasattr(case, 'statement') and case.statement:
                # case.statement can be a list or a single Block/statement
                if isinstance(case.statement, list):
                    for stmt in case.statement:
                        self._process_statement(stmt)
                else:
                    self._process_statement(case.statement)
    
    def _process_assignment(self, assign_stmt):
        """Process assignments (blocking or non-blocking)"""
        if hasattr(assign_stmt, 'left') and hasattr(assign_stmt.left, 'var'):
            lhs = assign_stmt.left.var.name if hasattr(assign_stmt.left.var, 'name') else None
            if lhs and ('next' in lhs.lower() or 'ns' in lhs.lower()):
                if lhs not in self.next_state_logic:
                    self.next_state_logic[lhs] = []
    
    def _process_continuous_assign(self, assign):
        """Process continuous assignments (assign statements)"""
        if not hasattr(assign, 'left') or not hasattr(assign, 'right'):
            return
        
        try:
            if hasattr(assign.left, 'var') and hasattr(assign.left.var, 'name'):
                lhs_name = assign.left.var.name
                if lhs_name in self.outputs:
                    self.expressions[lhs_name] = exprvar(f"{lhs_name}_expr")
        except:
            pass
    
    def _process_gate_instance(self, item: InstanceList) -> bool:
        """Process a gate instantiation"""
        inst = item.instances[0]
        gate_type = inst.module.capitalize()
        
        # Output wire
        out_wire = inst.portlist[0].argname.name
        
        # Process inputs
        in_args = []
        all_inputs_resolved = True
        
        for p in inst.portlist[1:]:
            arg = p.argname
            if isinstance(arg, IntConst):
                # Handle constants like 1'b1
                in_args.append(expr(int(arg.value.split("'b")[-1])))
            elif hasattr(arg, 'name') and arg.name in self.expressions:
                in_args.append(self.expressions[arg.name])
            else:
                all_inputs_resolved = False
                break
        
        # If all inputs resolved, compute output
        if all_inputs_resolved and gate_type in self.GATE_MAP:
            self.expressions[out_wire] = self.GATE_MAP[gate_type](*in_args)
            print(f"  [OK] Resolved: {out_wire} = {gate_type}(...)")
            return True
        
        return False
    
    def _process_assign(self, item: Assign) -> bool:
        """Process a continuous assignment"""
        # This is a simplified version - extend as needed
        # For now, just mark as processed
        return False
    
    def identify_state_registers(self) -> List[str]:
        """
        Identify which registers are state registers
        Heuristics: look for registers named 'state', 'current_state', etc.
        Exclude 'next_state' as it's the combinational next-state signal
        """
        state_keywords = ['state', 'curr', 'present', 'ps', 'fsm']
        exclude_keywords = ['next', 'ns', 'n_']
        self.state_registers = []
        
        for reg in self.registers:
            reg_lower = reg.lower()
            
            # Skip if it contains exclude keywords
            if any(excl in reg_lower for excl in exclude_keywords):
                continue
            
            # Include if it contains state keywords
            if any(keyword in reg_lower for keyword in state_keywords):
                self.state_registers.append(reg)
        
        if not self.state_registers and self.registers:
            # If no obvious state register, use first non-next register
            for reg in sorted(list(self.registers)):
                reg_lower = reg.lower()
                if not any(excl in reg_lower for excl in exclude_keywords):
                    self.state_registers = [reg]
                    break
        
        print(f"\nIdentified state registers: {self.state_registers}")
        return self.state_registers
    
    def extract_fsm_structure(self) -> Dict:
        """
        Extract complete FSM structure including states, transitions, and outputs
        """
        self.parse_verilog()
        expressions = self.verilog_to_pyeda_expressions()
        state_regs = self.identify_state_registers()
        
        # Get actual bit width of state registers
        state_bit_width = self._get_state_bit_width()
        
        # Extract FSM transition table from behavioral Verilog
        transition_table = self._build_fsm_transition_table()
        
        return {
            'module_name': self.module.name,
            'inputs': self.inputs,
            'outputs': self.outputs,
            'registers': self.registers,
            'state_registers': state_regs,
            'state_bit_width': state_bit_width,
            'expressions': expressions,
            'raw_expressions': self.expressions,
            'transition_table': transition_table,
            'parameters': self.parameters,
            'fsm_extracted': len(transition_table) > 0
        }
    
    def _get_state_bit_width(self) -> int:
        """Get the total bit width of all state registers"""
        total_bits = 0
        for reg_name in self.state_registers:
            for item in self.module.items:
                if isinstance(item, Decl):
                    for decl in item.list:
                        if isinstance(decl, Reg) and decl.name == reg_name:
                            if decl.width:
                                if hasattr(decl.width, 'msb') and hasattr(decl.width, 'lsb'):
                                    msb = self._eval_const(decl.width.msb)
                                    lsb = self._eval_const(decl.width.lsb)
                                    total_bits += (msb - lsb + 1)
                                else:
                                    total_bits += 1
                            else:
                                total_bits += 1
        return total_bits if total_bits > 0 else 1
    
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
                    if base_and_value.startswith('b'):  # Binary
                        return int(base_and_value[1:], 2)
                    elif base_and_value.startswith('d'):  # Decimal
                        return int(base_and_value[1:], 10)
                    elif base_and_value.startswith('h'):  # Hexadecimal
                        return int(base_and_value[1:], 16)
                    elif base_and_value.startswith('o'):  # Octal
                        return int(base_and_value[1:], 8)
            # Plain integer
            try:
                return int(value_str, 0)  # Auto-detect base
            except (ValueError, TypeError):
                return 0
        elif isinstance(node, Constant):
            try:
                return int(node.value, 0)
            except (ValueError, TypeError):
                return 0
        elif isinstance(node, Identifier):
            # If a parameter is defined in terms of another, it might be an identifier
            if node.name in self.parameters:
                return self.parameters[node.name]
        return 0
    
    def _build_fsm_transition_table(self) -> Dict:
        """
        Build an explicit FSM transition table from behavioral Verilog
        Returns a dictionary mapping (state, input) -> next_state
        """
        # Use the behavioral simulator to build transition table
        simulator = BehavioralFSMSimulator(
            self.module,
            self.state_registers,
            self.inputs,
            self.outputs,
            self.parameters
        )
        
        transition_table = simulator.build_transition_table()
        return transition_table
    
    def _extract_transitions_from_always(self, always_block, transition_table):
        """Extract state transitions from always block"""
        statement = always_block.statement
        
        if isinstance(statement, Block):
            for stmt in statement.statements:
                self._extract_transitions_from_statement(stmt, transition_table)
        else:
            self._extract_transitions_from_statement(statement, transition_table)
    
    def _extract_transitions_from_statement(self, stmt, transition_table):
        """Recursively extract transitions from statements"""
        if isinstance(stmt, CaseStatement):
            self._extract_from_case(stmt, transition_table)
        elif isinstance(stmt, Block):
            for s in stmt.statements:
                self._extract_transitions_from_statement(s, transition_table)
        elif isinstance(stmt, IfStatement):
            if stmt.true_statement:
                self._extract_transitions_from_statement(stmt.true_statement, transition_table)
            if stmt.false_statement:
                self._extract_transitions_from_statement(stmt.false_statement, transition_table)
    
    def _extract_from_case(self, case_stmt, transition_table):
        """Extract transitions from a case statement"""
        # This is simplified - a full implementation would parse the entire AST
        # For now, we just mark that case-based logic exists
        if hasattr(case_stmt, 'caselist'):
            for case_item in case_stmt.caselist:
                # Each case represents a state
                # The statement inside contains the next state logic
                pass


def parse_verilog_fsm(filepath: str) -> Dict:
    """
    Convenience function to parse Verilog FSM
    """
    parser = VerilogFSMParser(filepath)
    return parser.extract_fsm_structure()
