"""Debug script to inspect parameter AST structure"""
import subprocess
from pyverilog.vparser.parser import parse
from pyverilog.vparser.ast import *

# Mock subprocess.call to bypass iverilog on Windows
original_call = subprocess.call
def mock_call(cmd, *args, **kwargs):
    if 'iverilog' in str(cmd):
        # Read the input file and write to preprocess.output
        input_file = None
        for arg in cmd:
            if arg.endswith('.v'):
                input_file = arg
                break
        if input_file:
            with open(input_file, 'r') as f:
                content = f.read()
            with open('preprocess.output', 'w') as f:
                f.write(content)
        return 0
    return original_call(cmd, *args, **kwargs)
subprocess.call = mock_call

# Parse the traffic light file
ast, _ = parse(['examples/traffic_light.v'])

# Find the module
for item in ast.description.definitions:
    if isinstance(item, ModuleDef):
        print(f"Module: {item.name}")
        for module_item in item.items:
            if isinstance(module_item, Decl):
                for decl in module_item.list:
                    if isinstance(decl, Parameter):
                        print(f"\nParameter: {decl.name}")
                        print(f"  Value type: {type(decl.value)}")
                        print(f"  Value: {decl.value}")
                        if isinstance(decl.value, Rvalue):
                            print(f"  Rvalue.var type: {type(decl.value.var)}")
                            print(f"  Rvalue.var: {decl.value.var}")
                            if isinstance(decl.value.var, IntConst):
                                print(f"  IntConst.value: {decl.value.var.value}")
