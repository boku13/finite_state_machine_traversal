"""
Main Demo Script for FSM Traversal Tool
Demonstrates parsing, traversal, and analysis of sequential designs
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from verilog_parser import VerilogFSMParser, parse_verilog_fsm
from fsm_traversal import FSMTraversal, FSMState
from fsm_reporter import FSMReporter, print_summary


def demo_simple_fsm(verilog_file: str):
    """
    Demonstrate FSM analysis on a simple design
    """
    print("\n" + "="*80)
    print(f"DEMO: Analyzing {os.path.basename(verilog_file)}")
    print("="*80)
    
    try:
        # Step 1: Parse Verilog
        print("\n[Step 1] Parsing Verilog file...")
        fsm_structure = parse_verilog_fsm(verilog_file)
        
        # Step 2: Create traversal engine
        print("\n[Step 2] Creating FSM traversal engine...")
        traversal = FSMTraversal(fsm_structure, verbose=True)
        
        # Step 3: Perform full analysis
        print("\n[Step 3] Performing full FSM analysis...")
        results = traversal.full_analysis(method='bfs')
        
        # Step 4: Print summary
        print_summary(results)
        
        # Step 5: Generate reports
        print("\n[Step 4] Generating reports...")
        module_name = fsm_structure['module_name']
        reporter = FSMReporter(results, output_dir=f"fsm_reports/{module_name}")
        reporter.generate_all_reports()
        
        return results
        
    except Exception as e:
        print(f"\n❌ Error analyzing {verilog_file}: {e}")
        import traceback
        traceback.print_exc()
        return None


def demo_manual_fsm():
    """
    Demonstrate FSM traversal with manually created FSM structure
    (useful when Verilog parsing is not available)
    """
    print("\n" + "="*80)
    print("DEMO: Manual FSM Creation and Traversal")
    print("="*80)
    
    # Create a simple FSM structure manually
    fsm_structure = {
        'module_name': 'manual_fsm',
        'inputs': {'a', 'b'},
        'outputs': {'out'},
        'registers': {'state'},
        'state_registers': ['state'],
        'expressions': {},
        'raw_expressions': {}
    }
    
    print("\nCreated manual FSM with:")
    print(f"  Inputs: {fsm_structure['inputs']}")
    print(f"  Outputs: {fsm_structure['outputs']}")
    print(f"  State registers: {fsm_structure['state_registers']}")
    
    # Create traversal engine
    traversal = FSMTraversal(fsm_structure, verbose=False)
    
    # Manually define a simple transition function
    # This is a workaround since we don't have actual logic
    print("\nNote: Manual FSM requires custom transition logic implementation")
    print("For real analysis, use Verilog parsing")


def analyze_all_examples():
    """
    Analyze all example Verilog files
    """
    print("\n" + "#"*80)
    print("# ANALYZING ALL EXAMPLE DESIGNS")
    print("#"*80)
    
    examples_dir = os.path.join(os.path.dirname(__file__), "examples")
    
    if not os.path.exists(examples_dir):
        print(f"\n❌ Examples directory not found: {examples_dir}")
        return
    
    verilog_files = [f for f in os.listdir(examples_dir) if f.endswith('.v')]
    
    if not verilog_files:
        print(f"\n❌ No Verilog files found in {examples_dir}")
        return
    
    print(f"\nFound {len(verilog_files)} Verilog file(s):")
    for vf in verilog_files:
        print(f"  • {vf}")
    
    results = {}
    for vf in verilog_files:
        verilog_path = os.path.join(examples_dir, vf)
        result = demo_simple_fsm(verilog_path)
        if result:
            results[vf] = result
    
    # Summary of all analyses
    print("\n" + "#"*80)
    print("# ANALYSIS SUMMARY FOR ALL DESIGNS")
    print("#"*80)
    
    for filename, result in results.items():
        summary = result.get('analysis_summary', {})
        print(f"\n{filename}:")
        print(f"  States: {summary.get('total_reachable_states', 'N/A')}")
        print(f"  Transitions: {summary.get('total_transitions', 'N/A')}")
        print(f"  Deadlocks: {summary.get('deadlock_count', 'N/A')}")
        print(f"  Cycles: {summary.get('cycle_count', 'N/A')}")


def main():
    """Main demo function"""
    print("""
╔════════════════════════════════════════════════════════════════════════════╗
║                                                                            ║
║              Complex FSM Traversal Tool - Demonstration                    ║
║                                                                            ║
║  This tool performs comprehensive analysis of Finite State Machines        ║
║  from Verilog descriptions, supporting:                                    ║
║    • BFS/DFS traversal of state spaces with 50+ states                     ║
║    • Reachability analysis                                                 ║
║    • Deadlock detection                                                    ║
║    • Cycle detection                                                       ║
║    • Report generation (text, CSV, DOT, JSON)                              ║
║                                                                            ║
╚════════════════════════════════════════════════════════════════════════════╝
    """)
    
    # Check if specific file provided
    if len(sys.argv) > 1:
        verilog_file = sys.argv[1]
        if os.path.exists(verilog_file):
            demo_simple_fsm(verilog_file)
        else:
            print(f"❌ File not found: {verilog_file}")
    else:
        # Run all examples
        analyze_all_examples()
    
    print("\n" + "="*80)
    print("Demo complete!")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
