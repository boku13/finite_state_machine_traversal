"""
FSM Visualization and Reporting Module
Generates reports, transition tables, state diagrams, and statistics
"""

import json
from typing import Dict, Set, List, Optional
from collections import defaultdict
import os


class FSMReporter:
    """Generate comprehensive reports for FSM analysis"""
    
    def __init__(self, analysis_results: Dict, output_dir: str = "fsm_reports"):
        self.results = analysis_results
        self.output_dir = output_dir
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
    
    def generate_text_report(self, filename: str = "fsm_report.txt") -> str:
        """Generate a comprehensive text report"""
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w') as f:
            f.write("="*80 + "\n")
            f.write("FSM ANALYSIS REPORT\n")
            f.write("="*80 + "\n\n")
            
            # Summary section
            f.write("SUMMARY\n")
            f.write("-"*80 + "\n")
            summary = self.results.get('analysis_summary', {})
            for key, value in summary.items():
                f.write(f"{key.replace('_', ' ').title()}: {value}\n")
            f.write("\n")
            
            # Statistics section
            f.write("STATISTICS\n")
            f.write("-"*80 + "\n")
            stats = self.results.get('stats', {})
            for key, value in stats.items():
                f.write(f"{key.replace('_', ' ').title()}: {value}\n")
            f.write("\n")
            
            # Reachable states
            f.write("REACHABLE STATES\n")
            f.write("-"*80 + "\n")
            reachable = self.results.get('reachable_states', set())
            f.write(f"Total: {len(reachable)} states\n\n")
            for i, state in enumerate(sorted(reachable, key=lambda s: s.state_vector), 1):
                f.write(f"{i:4d}. {state.state_vector} ({state.state_name})\n")
            f.write("\n")
            
            # Transitions
            f.write("TRANSITIONS\n")
            f.write("-"*80 + "\n")
            transitions = self.results.get('transitions', [])
            f.write(f"Total: {len(transitions)} transitions\n\n")
            for i, trans in enumerate(transitions[:100], 1):  # Limit to first 100
                f.write(f"{i:4d}. {trans.from_state.state_vector} --[I:{trans.input_vector}, O:{trans.output_vector}]--> {trans.to_state.state_vector}\n")
            if len(transitions) > 100:
                f.write(f"... ({len(transitions) - 100} more transitions omitted)\n")
            f.write("\n")
            
            # Deadlock states
            f.write("DEADLOCK STATES\n")
            f.write("-"*80 + "\n")
            deadlocks = self.results.get('deadlock_states', set())
            if deadlocks:
                f.write(f"Total: {len(deadlocks)} deadlock state(s)\n\n")
                for state in deadlocks:
                    f.write(f"  - {state.state_vector}\n")
            else:
                f.write("No deadlock states found.\n")
            f.write("\n")
            
            # Cycles
            f.write("CYCLES\n")
            f.write("-"*80 + "\n")
            cycles = self.results.get('cycles', [])
            if cycles:
                f.write(f"Total: {len(cycles)} cycle(s)\n\n")
                for i, cycle in enumerate(cycles, 1):
                    f.write(f"Cycle {i}: ")
                    f.write(" -> ".join(str(s.state_vector) for s in cycle))
                    f.write("\n")
            else:
                f.write("No cycles detected.\n")
            f.write("\n")
            
            f.write("="*80 + "\n")
            f.write("END OF REPORT\n")
            f.write("="*80 + "\n")
        
        print(f"\n[OK] Text report saved to: {filepath}")
        return filepath
    
    def generate_transition_table(self, filename: str = "transition_table.csv") -> str:
        """Generate a CSV transition table"""
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w') as f:
            # Header
            f.write("From_State,Input,Next_State,Output\n")
            
            # Transitions
            transitions = self.results.get('transitions', [])
            for trans in transitions:
                from_state = ''.join(str(b) for b in trans.from_state.state_vector)
                to_state = ''.join(str(b) for b in trans.to_state.state_vector)
                input_vec = ''.join(str(b) for b in trans.input_vector)
                output_vec = ''.join(str(b) for b in trans.output_vector) if trans.output_vector else 'N/A'
                
                f.write(f"{from_state},{input_vec},{to_state},{output_vec}\n")
        
        print(f"[OK] Transition table saved to: {filepath}")
        return filepath
    
    def generate_state_graph_dot(self, filename: str = "fsm_graph.dot", max_states: int = 50) -> str:
        """
        Generate a GraphViz DOT file for visualization
        Limited to max_states for readability
        """
        filepath = os.path.join(self.output_dir, filename)
        
        reachable = list(self.results.get('reachable_states', set()))
        if len(reachable) > max_states:
            print(f"[WARNING] {len(reachable)} states exceeds max_states={max_states}")
            print(f"  Only showing first {max_states} states in graph")
            reachable = reachable[:max_states]
        
        state_graph = self.results.get('state_graph', {})
        deadlocks = self.results.get('deadlock_states', set())
        
        with open(filepath, 'w') as f:
            f.write("digraph FSM {\n")
            f.write("  rankdir=LR;\n")
            f.write("  node [shape=circle];\n\n")
            
            # Add states
            for state in reachable:
                state_label = ''.join(str(b) for b in state.state_vector)
                if state in deadlocks:
                    f.write(f'  "{state_label}" [color=red, style=filled, fillcolor=pink];\n')
                else:
                    f.write(f'  "{state_label}";\n')
            
            f.write("\n")
            
            # Add transitions (limited)
            transition_count = 0
            max_transitions = 200
            
            for state in reachable:
                if state not in state_graph:
                    continue
                
                from_label = ''.join(str(b) for b in state.state_vector)
                
                for trans in state_graph[state]:
                    if trans.to_state not in reachable:
                        continue
                    
                    to_label = ''.join(str(b) for b in trans.to_state.state_vector)
                    input_label = ''.join(str(b) for b in trans.input_vector)
                    
                    f.write(f'  "{from_label}" -> "{to_label}" [label="{input_label}"];\n')
                    
                    transition_count += 1
                    if transition_count >= max_transitions:
                        break
                
                if transition_count >= max_transitions:
                    break
            
            f.write("}\n")
        
        print(f"[OK] DOT graph saved to: {filepath}")
        print(f"  To visualize: dot -Tpng {filename} -o fsm_graph.png")
        return filepath
    
    def generate_json_export(self, filename: str = "fsm_data.json") -> str:
        """Export FSM data as JSON for further processing"""
        filepath = os.path.join(self.output_dir, filename)
        
        # Convert sets and custom objects to serializable format
        export_data = {
            'summary': self.results.get('analysis_summary', {}),
            'stats': self.results.get('stats', {}),
            'reachable_states': [
                {
                    'state_vector': list(s.state_vector),
                    'state_name': s.state_name
                }
                for s in self.results.get('reachable_states', set())
            ],
            'transitions': [
                {
                    'from': list(t.from_state.state_vector),
                    'to': list(t.to_state.state_vector),
                    'input': list(t.input_vector),
                    'output': list(t.output_vector) if t.output_vector else None
                }
                for t in self.results.get('transitions', [])
            ],
            'deadlock_states': [
                list(s.state_vector) for s in self.results.get('deadlock_states', set())
            ],
            'cycles': [
                [list(s.state_vector) for s in cycle]
                for cycle in self.results.get('cycles', [])
            ]
        }
        
        with open(filepath, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        print(f"[OK] JSON export saved to: {filepath}")
        return filepath
    
    def generate_all_reports(self):
        """Generate all available report formats"""
        print(f"\n{'='*80}")
        print(f"Generating All Reports")
        print(f"{'='*80}")
        
        self.generate_text_report()
        self.generate_transition_table()
        self.generate_state_graph_dot()
        self.generate_json_export()
        
        print(f"\n[OK] All reports saved to directory: {self.output_dir}")
        return self.output_dir


def print_summary(analysis_results: Dict):
    """Print a quick summary to console"""
    print(f"\n{'#'*80}")
    print(f"# FSM ANALYSIS SUMMARY")
    print(f"{'#'*80}")
    
    summary = analysis_results.get('analysis_summary', {})
    
    print(f"\nStatistics:")
    print(f"  - Reachable States: {summary.get('total_reachable_states', 'N/A')}")
    print(f"  - Total Transitions: {summary.get('total_transitions', 'N/A')}")
    print(f"  - State Coverage: {summary.get('coverage', 'N/A')}")
    print(f"  - Deadlock States: {summary.get('deadlock_count', 'N/A')}")
    print(f"  - Cycles Detected: {summary.get('cycle_count', 'N/A')}")
    
    stats = analysis_results.get('stats', {})
    if 'time_elapsed' in stats:
        print(f"  - Analysis Time: {stats['time_elapsed']:.2f}s")
    
    print(f"\n{'#'*80}\n")
