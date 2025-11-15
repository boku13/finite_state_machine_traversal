"""
Test Script for FSM Traversal Tool
Validates functionality with known FSM examples
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fsm_traversal import FSMTraversal, FSMState


def test_manual_fsm():
    """
    Test with a manually created simple FSM
    """
    print("\n" + "="*80)
    print("TEST: Manual FSM with 3 states")
    print("="*80)
    
    # Create a 3-state FSM manually (2-bit state encoding)
    # States: 00 (S0), 01 (S1), 10 (S2)
    # Single input: a
    # Transitions: S0 --0--> S0, S0 --1--> S1
    #              S1 --0--> S2, S1 --1--> S0
    #              S2 --0--> S1, S2 --1--> S2
    
    fsm_structure = {
        'module_name': 'test_fsm',
        'inputs': {'a'},
        'outputs': {'out'},
        'registers': {'state'},
        'state_registers': ['state', 'state_bit1'],  # 2-bit state
        'expressions': {},
        'raw_expressions': {}
    }
    
    # Create traversal engine
    traversal = FSMTraversal(fsm_structure, verbose=True)
    
    # Override the next state evaluation with our manual logic
    original_eval = traversal.evaluate_next_state
    
    def manual_next_state(current_state, input_vector):
        """Manual transition function for testing"""
        state_val = current_state.state_vector[0] + 2 * current_state.state_vector[1]
        input_val = input_vector[0] if input_vector else 0
        
        # Define transitions
        transitions = {
            (0, 0): 0,  # S0 with input 0 -> S0
            (0, 1): 1,  # S0 with input 1 -> S1
            (1, 0): 2,  # S1 with input 0 -> S2
            (1, 1): 0,  # S1 with input 1 -> S0
            (2, 0): 1,  # S2 with input 0 -> S1
            (2, 1): 2,  # S2 with input 1 -> S2
        }
        
        next_val = transitions.get((state_val, input_val), 0)
        next_state_vector = (next_val & 1, (next_val >> 1) & 1)
        
        return FSMState(next_state_vector, f"S{next_val}")
    
    traversal.evaluate_next_state = manual_next_state
    
    # Run BFS traversal
    print("\nRunning BFS traversal...")
    results = traversal.bfs_traversal(max_states=10)
    
    # Validate results
    print("\n" + "-"*80)
    print("VALIDATION:")
    print("-"*80)
    
    expected_states = 3
    actual_states = len(results['reachable_states'])
    
    print(f"Expected states: {expected_states}")
    print(f"Actual states: {actual_states}")
    
    if actual_states == expected_states:
        print("[PASS] Correct number of states found")
    else:
        print("[FAIL] Incorrect number of states")
    
    # Check for deadlocks (should be none)
    deadlocks = traversal.detect_deadlocks()
    if len(deadlocks) == 0:
        print("[PASS] No unexpected deadlocks")
    else:
        print(f"[WARNING] Found {len(deadlocks)} deadlock(s)")
    
    # Check for cycles
    cycles = traversal.detect_cycles()
    print(f"ℹ INFO: Found {len(cycles)} cycle(s)")
    
    return results


def test_state_encoding():
    """Test state encoding and enumeration"""
    print("\n" + "="*80)
    print("TEST: State Encoding")
    print("="*80)
    
    fsm_structure = {
        'module_name': 'test_encoding',
        'inputs': set(),
        'outputs': set(),
        'registers': {'s0', 's1', 's2'},
        'state_registers': ['s0', 's1', 's2'],
        'expressions': {},
        'raw_expressions': {}
    }
    
    traversal = FSMTraversal(fsm_structure, verbose=False)
    
    # Test state enumeration
    all_states = traversal.enumerate_all_states()
    
    print(f"\nNumber of state bits: {traversal.num_state_bits}")
    print(f"Maximum possible states: {2**traversal.num_state_bits}")
    print(f"Enumerated states: {len(all_states)}")
    
    assert len(all_states) == 2**traversal.num_state_bits, "State enumeration failed"
    print("[PASS] State enumeration correct")
    
    # Test input enumeration
    fsm_structure['inputs'] = {'a', 'b'}
    traversal = FSMTraversal(fsm_structure, verbose=False)
    all_inputs = traversal.enumerate_all_inputs()
    
    print(f"\nNumber of input bits: {traversal.num_input_bits}")
    print(f"Possible input combinations: {2**traversal.num_input_bits}")
    print(f"Enumerated inputs: {len(all_inputs)}")
    
    assert len(all_inputs) == 2**traversal.num_input_bits, "Input enumeration failed"
    print("[PASS] Input enumeration correct")


def run_all_tests():
    """Run all tests"""
    print("""
================================================================================
                                                                            
                    FSM Traversal Tool - Test Suite                         
                                                                            
================================================================================
    """)
    
    tests = [
        ("State Encoding", test_state_encoding),
        ("Manual FSM", test_manual_fsm),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            test_func()
            passed += 1
            print(f"\n[PASS] {test_name} test PASSED\n")
        except Exception as e:
            failed += 1
            print(f"\n[FAIL] {test_name} test FAILED: {e}\n")
            import traceback
            traceback.print_exc()
    
    print("\n" + "="*80)
    print(f"TEST SUMMARY: {passed} passed, {failed} failed out of {len(tests)} total")
    print("="*80 + "\n")
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
