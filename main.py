"""
Complex FSM Traversal Tool
Main entry point for FSM analysis from Verilog descriptions

Usage:
    python main.py <verilog_file> [options]
    python main.py --demo
    python main.py --help
"""

import sys
import os
import argparse
from pathlib import Path

from verilog_parser import parse_verilog_fsm
from fsm_traversal import FSMTraversal, FSMState
from fsm_reporter import FSMReporter, print_summary


def print_banner():
    """Print tool banner"""
    banner = """
================================================================================
                                                                            
                 Complex FSM Traversal Tool v1.0                            
                                                                            
        Comprehensive Analysis of Finite State Machines from Verilog        
                                                                            
================================================================================
    """
    print(banner)


def analyze_verilog_fsm(verilog_file: str, 
                       method: str = 'bfs',
                       output_dir: str = None,
                       max_states: int = 1000,
                       verbose: bool = True) -> dict:
    """
    Analyze a Verilog FSM file
    
    Args:
        verilog_file: Path to Verilog file
        method: Traversal method ('bfs' or 'dfs')
        output_dir: Output directory for reports
        max_states: Maximum states to explore
        verbose: Print detailed progress
    
    Returns:
        Dictionary containing analysis results
    """
    
    # Check file exists
    if not os.path.exists(verilog_file):
        raise FileNotFoundError(f"Verilog file not found: {verilog_file}")
    
    print(f"\n{'='*80}")
    print(f"Analyzing: {os.path.basename(verilog_file)}")
    print(f"{'='*80}")
    
    # Step 1: Parse Verilog
    print("\n[Step 1/4] Parsing Verilog file...")
    fsm_structure = parse_verilog_fsm(verilog_file)
    
    if not fsm_structure:
        raise ValueError("Failed to parse Verilog file")
    
    # Step 2: Create traversal engine
    print("\n[Step 2/4] Initializing FSM traversal engine...")
    traversal = FSMTraversal(fsm_structure, verbose=verbose)
    
    # Step 3: Perform analysis
    print(f"\n[Step 3/4] Performing FSM analysis using {method.upper()}...")
    results = traversal.full_analysis(method=method)
    
    # Step 4: Generate reports
    print("\n[Step 4/4] Generating reports...")
    
    if output_dir is None:
        module_name = fsm_structure.get('module_name', 'fsm')
        output_dir = f"fsm_reports/{module_name}"
    
    reporter = FSMReporter(results, output_dir=output_dir)
    reporter.generate_all_reports()
    
    # Print summary
    print_summary(results)
    
    return results


def run_demo():
    """Run demonstration on example files"""
    print_banner()
    print("\nRunning demonstration on example Verilog designs...\n")
    
    examples_dir = Path(__file__).parent / "examples"
    
    if not examples_dir.exists():
        print(f"ERROR: Examples directory not found: {examples_dir}")
        print("   Please ensure example Verilog files are in the 'examples' directory")
        return
    
    verilog_files = list(examples_dir.glob("*.v"))
    
    if not verilog_files:
        print(f"ERROR: No Verilog files found in {examples_dir}")
        return
    
    print(f"Found {len(verilog_files)} example design(s):\n")
    for vf in verilog_files:
        print(f"  - {vf.name}")
    
    print("\n" + "="*80 + "\n")
    
    # Analyze each example
    all_results = {}
    for vf in verilog_files:
        try:
            results = analyze_verilog_fsm(
                str(vf),
                method='bfs',
                verbose=False
            )
            all_results[vf.name] = results
        except Exception as e:
            print(f"\nERROR: Error analyzing {vf.name}: {e}")
            continue
    
    # Print comparison summary
    print("\n" + "#"*80)
    print("# COMPARATIVE SUMMARY")
    print("#"*80 + "\n")
    
    print(f"{'Design':<25} {'States':<10} {'Trans':<10} {'Dead':<8} {'Cycles':<8}")
    print("-" * 80)
    
    for filename, result in all_results.items():
        summary = result.get('analysis_summary', {})
        name = filename.replace('.v', '')
        states = summary.get('total_reachable_states', 'N/A')
        trans = summary.get('total_transitions', 'N/A')
        dead = summary.get('deadlock_count', 'N/A')
        cycles = summary.get('cycle_count', 'N/A')
        
        print(f"{name:<25} {str(states):<10} {str(trans):<10} {str(dead):<8} {str(cycles):<8}")
    
    print("\n✓ Demo complete! Check the fsm_reports/ directory for detailed reports.\n")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Complex FSM Traversal Tool - Analyze FSMs from Verilog',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py examples/traffic_light.v
  python main.py design.v --method dfs --output my_reports
  python main.py --demo
        """
    )
    
    parser.add_argument(
        'verilog_file',
        nargs='?',
        help='Path to Verilog file to analyze'
    )
    
    parser.add_argument(
        '--demo',
        action='store_true',
        help='Run demonstration on example designs'
    )
    
    parser.add_argument(
        '--method',
        choices=['bfs', 'dfs'],
        default='bfs',
        help='Traversal method (default: bfs)'
    )
    
    parser.add_argument(
        '--output',
        '-o',
        help='Output directory for reports (default: fsm_reports/<module_name>)'
    )
    
    parser.add_argument(
        '--max-states',
        type=int,
        default=1000,
        help='Maximum states to explore (default: 1000)'
    )
    
    parser.add_argument(
        '--quiet',
        '-q',
        action='store_true',
        help='Suppress verbose output'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='FSM Traversal Tool v1.0'
    )
    
    args = parser.parse_args()
    
    # Handle demo mode
    if args.demo or (not args.verilog_file and len(sys.argv) == 1):
        run_demo()
        return
    
    # Handle file analysis
    if not args.verilog_file:
        parser.print_help()
        return
    
    print_banner()
    
    try:
        analyze_verilog_fsm(
            verilog_file=args.verilog_file,
            method=args.method,
            output_dir=args.output,
            max_states=args.max_states,
            verbose=not args.quiet
        )
        
        print("\n[OK] Analysis complete!\n")
        
    except Exception as e:
        print(f"\nERROR: {e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
