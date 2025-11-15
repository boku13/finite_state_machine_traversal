"""Quick test to verify parsing works"""
import sys
from verilog_parser import parse_verilog_fsm

print("Testing Verilog parser...")
try:
    result = parse_verilog_fsm("examples/traffic_light.v")
    print("\n✅ SUCCESS! Parser is working.")
    print(f"Module: {result['module_name']}")
    print(f"Inputs: {result['inputs']}")
    print(f"Outputs: {result['outputs']}")
except Exception as e:
    print(f"\n❌ FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
