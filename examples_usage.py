"""
Usage Examples for FSM Traversal Tool
Demonstrates various use cases and features
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from verilog_parser import VerilogFSMParser, parse_verilog_fsm
from fsm_traversal import FSMTraversal, FSMState
from fsm_reporter import FSMReporter, print_summary


def example_1_basic_analysis():
    """
    Example 1: Basic FSM analysis workflow
    """
    print("\n" + "="*80)
    print("EXAMPLE 1: Basic FSM Analysis")
    print("="*80)
    
    verilog_file = "examples/traffic_light.v"
    
    # Parse Verilog
    fsm_structure = parse_verilog_fsm(verilog_file)
    
    # Create traversal engine
    traversal = FSMTraversal(fsm_structure, verbose=True)
    
    # Run BFS traversal
    results = traversal.bfs_traversal()
    
    # Print summary
    print_summary(results)


def example_2_custom_initial_state():
    """
    Example 2: Analysis with custom initial state
    """
    print("\n" + "="*80)
    print("EXAMPLE 2: Custom Initial State")
    print("="*80)
    
    verilog_file = "examples/vending_machine.v"
    
    fsm_structure = parse_verilog_fsm(verilog_file)
    traversal = FSMTraversal(fsm_structure, verbose=False)
    
    # Define custom initial state (e.g., start with 5 cents)
    # Assuming 3-bit state encoding
    custom_init = FSMState(
        state_vector=(1, 0, 0),  # Binary 001 = state S5 (5 cents)
        state_name="S5_INIT"
    )
    
    print(f"\nStarting from custom initial state: {custom_init.state_vector}")
    
    results = traversal.bfs_traversal(initial_state=custom_init)
    
    print(f"\nReachable from custom init: {len(results['reachable_states'])} states")


def example_3_compare_bfs_dfs():
    """
    Example 3: Compare BFS vs DFS traversal
    """
    print("\n" + "="*80)
    print("EXAMPLE 3: BFS vs DFS Comparison")
    print("="*80)
    
    verilog_file = "examples/sequence_detector.v"
    
    fsm_structure = parse_verilog_fsm(verilog_file)
    
    # BFS analysis
    print("\n--- BFS Analysis ---")
    traversal_bfs = FSMTraversal(fsm_structure, verbose=False)
    results_bfs = traversal_bfs.bfs_traversal()
    
    # DFS analysis
    print("\n--- DFS Analysis ---")
    traversal_dfs = FSMTraversal(fsm_structure, verbose=False)
    results_dfs = traversal_dfs.dfs_traversal()
    
    # Compare
    print("\n--- Comparison ---")
    print(f"BFS found: {len(results_bfs['reachable_states'])} states")
    print(f"DFS found: {len(results_dfs['reachable_states'])} states")
    print(f"BFS time: {results_bfs['stats']['time_elapsed']:.4f}s")
    print(f"DFS time: {results_dfs['stats']['time_elapsed']:.4f}s")


def example_4_deadlock_detection():
    """
    Example 4: Focus on deadlock detection
    """
    print("\n" + "="*80)
    print("EXAMPLE 4: Deadlock Detection")
    print("="*80)
    
    verilog_file = "examples/traffic_light.v"
    
    fsm_structure = parse_verilog_fsm(verilog_file)
    traversal = FSMTraversal(fsm_structure, verbose=False)
    
    # First traverse to find all states
    traversal.bfs_traversal()
    
    # Then detect deadlocks
    deadlocks = traversal.detect_deadlocks()
    
    print(f"\n📊 Analysis Results:")
    print(f"   Total reachable states: {len(traversal.reachable_states)}")
    print(f"   Deadlock states: {len(deadlocks)}")
    
    if deadlocks:
        print(f"\n⚠ Warning: Found deadlock states:")
        for state in deadlocks:
            print(f"   • {state.state_vector}")
    else:
        print(f"\n✓ No deadlock states found")


def example_5_cycle_detection():
    """
    Example 5: Detect cycles in FSM
    """
    print("\n" + "="*80)
    print("EXAMPLE 5: Cycle Detection")
    print("="*80)
    
    verilog_file = "examples/complex_counter.v"
    
    fsm_structure = parse_verilog_fsm(verilog_file)
    traversal = FSMTraversal(fsm_structure, verbose=False)
    
    # Traverse and detect cycles
    traversal.bfs_traversal(max_states=50)  # Limit for large state space
    cycles = traversal.detect_cycles()
    
    print(f"\n📊 Cycle Analysis:")
    print(f"   States explored: {len(traversal.reachable_states)}")
    print(f"   Cycles found: {len(cycles)}")
    
    if cycles:
        print(f"\n   Showing first 3 cycles:")
        for i, cycle in enumerate(cycles[:3], 1):
            cycle_str = " -> ".join(str(s.state_vector) for s in cycle[:5])
            if len(cycle) > 5:
                cycle_str += " -> ..."
            print(f"   {i}. {cycle_str}")


def example_6_report_generation():
    """
    Example 6: Generate comprehensive reports
    """
    print("\n" + "="*80)
    print("EXAMPLE 6: Report Generation")
    print("="*80)
    
    verilog_file = "examples/vending_machine.v"
    
    fsm_structure = parse_verilog_fsm(verilog_file)
    traversal = FSMTraversal(fsm_structure, verbose=False)
    results = traversal.full_analysis()
    
    # Generate all report types
    reporter = FSMReporter(results, output_dir="example_reports")
    
    print("\nGenerating reports...")
    reporter.generate_text_report("example_text.txt")
    reporter.generate_transition_table("example_table.csv")
    reporter.generate_state_graph_dot("example_graph.dot")
    reporter.generate_json_export("example_data.json")
    
    print("\n✓ All reports generated in 'example_reports/' directory")


def example_7_parser_details():
    """
    Example 7: Explore parser details
    """
    print("\n" + "="*80)
    print("EXAMPLE 7: Parser Exploration")
    print("="*80)
    
    verilog_file = "examples/traffic_light.v"
    
    # Create parser
    parser = VerilogFSMParser(verilog_file)
    
    # Parse
    parser.parse_verilog()
    
    # Get expressions
    expressions = parser.verilog_to_pyeda_expressions()
    
    # Identify state registers
    state_regs = parser.identify_state_registers()
    
    print("\n📋 Parser Details:")
    print(f"   Module name: {parser.module.name}")
    print(f"   Inputs: {parser.inputs}")
    print(f"   Outputs: {parser.outputs}")
    print(f"   Registers: {parser.registers}")
    print(f"   State registers: {state_regs}")
    print(f"   Expressions resolved: {len(expressions)}")


def example_8_manual_state_exploration():
    """
    Example 8: Manual state-by-state exploration
    """
    print("\n" + "="*80)
    print("EXAMPLE 8: Manual State Exploration")
    print("="*80)
    
    verilog_file = "examples/traffic_light.v"
    
    fsm_structure = parse_verilog_fsm(verilog_file)
    traversal = FSMTraversal(fsm_structure, verbose=False)
    
    # Start from reset state
    current = FSMState((0, 0), "RESET")
    
    print(f"\nStarting from: {current.state_vector}")
    print("\nExploring transitions...")
    
    # Try different inputs
    for i, input_vec in enumerate(traversal.enumerate_all_inputs()[:4]):
        next_state = traversal.evaluate_next_state(current, input_vec)
        output_vec = traversal.evaluate_outputs(current, input_vec)
        
        print(f"\n  Input {input_vec}:")
        if next_state:
            print(f"    → Next state: {next_state.state_vector}")
            print(f"    → Output: {output_vec}")
        else:
            print(f"    → Could not evaluate")


def run_all_examples():
    """Run all examples"""
    examples = [
        ("Basic Analysis", example_1_basic_analysis),
        ("Custom Initial State", example_2_custom_initial_state),
        ("BFS vs DFS", example_3_compare_bfs_dfs),
        ("Deadlock Detection", example_4_deadlock_detection),
        ("Cycle Detection", example_5_cycle_detection),
        ("Report Generation", example_6_report_generation),
        ("Parser Details", example_7_parser_details),
        ("Manual Exploration", example_8_manual_state_exploration),
    ]
    
    print("""
╔════════════════════════════════════════════════════════════════════════════╗
║                                                                            ║
║                   FSM Traversal Tool - Usage Examples                      ║
║                                                                            ║
╚════════════════════════════════════════════════════════════════════════════╝
    """)
    
    print("\nAvailable examples:")
    for i, (name, _) in enumerate(examples, 1):
        print(f"  {i}. {name}")
    
    print("\nRunning all examples...\n")
    
    for name, func in examples:
        try:
            func()
        except Exception as e:
            print(f"\n❌ Error in {name}: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "="*80)
    print("All examples completed!")
    print("="*80 + "\n")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        example_num = int(sys.argv[1])
        examples = [
            example_1_basic_analysis,
            example_2_custom_initial_state,
            example_3_compare_bfs_dfs,
            example_4_deadlock_detection,
            example_5_cycle_detection,
            example_6_report_generation,
            example_7_parser_details,
            example_8_manual_state_exploration,
        ]
        if 1 <= example_num <= len(examples):
            examples[example_num - 1]()
        else:
            print(f"Invalid example number. Choose 1-{len(examples)}")
    else:
        run_all_examples()
