# Complex FSM Traversal Tool

**Automation to perform Complex FSM (having more than 50 states or so) traversal given the Verilog description of any sequential design**

## Team Members

- **K. K. N. Shyam Sathvik (B22EE036)** - [GitHub Profile](https://github.com/boku13)
- **Neermita Bhattacharya (B22CS092)** - [GitHub Profile](https://github.com/neermita18)

## Project Overview

**Course**: Formal Verification, Semester 7  
**Date**: November 2025  
**Objective**: Automate complex FSM traversal for sequential designs with 50+ states

A comprehensive tool for analyzing Finite State Machines (FSMs) from Verilog descriptions. Supports complex FSMs with 50+ states, including state space exploration, reachability analysis, deadlock detection, and cycle detection.

## Output & Results

After running `python main.py --demo`, the tool analyzes multiple FSM designs:

```
Design                    States     Trans      Dead     Cycles
--------------------------------------------------------------------------------
traffic_light             4          8          0        4
vending_machine           5          20         0        10
protocol_fsm              56         448        0        24
complex_counter           1          4          0        4
sequence_detector         1          0          1        0
```

### Example: Protocol FSM (56 States)

The `protocol_fsm.v` example demonstrates the tool's capability with 50+ states:

**Analysis Results:**
- Total Possible States: 64 (6-bit encoding)
- Reachable States: 56
- Coverage: 87.50%
- Total Transitions: 448
- Deadlock States: 0
- Cycles Detected: 24
- Execution Time: ~0.002 seconds

**State Space:**
- IDLE, INIT_1, INIT_2, INIT_3
- TX_START_1 through TX_START_6
- TX_DATA_1 through TX_DATA_8
- TX_CRC_1 through TX_CRC_8
- TX_END_1 through TX_END_4
- WAIT_ACK_1 through WAIT_ACK_6
- RX_ACK_1 through RX_ACK_4
- RETRY_1 through RETRY_6
- ERROR_1 through ERROR_6
- CLEANUP_1, CLEANUP_2

**Input Combinations**: 8 (3 inputs: start, ack, error)
**Output Signals**: busy, done, state_out (6-bit)

## Features

**Key Capabilities:**
- **Verilog Parsing**: Extracts FSM structure from behavioral Verilog (always blocks, case statements)
- **State Space Exploration**: BFS and DFS traversal algorithms
- **Reachability Analysis**: Identifies all reachable states from initial state
- **Deadlock Detection**: Finds states with no outgoing transitions
- **Cycle Detection**: Identifies cycles in the state transition graph
- **Comprehensive Reporting**: Generates text, CSV, DOT, and JSON reports
- **Visualization**: Creates GraphViz diagrams of FSM structure

## Installation

### Prerequisites
- Python 3.7 or higher
- pip package manager

### Quick Setup

1. **Navigate to the project directory:**
```bash
cd formal_verification
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Run the demo:**
```bash
python main.py --demo
```

## Usage

### Quick Start

**Analyze all example designs:**
```bash
python main.py --demo
```

**Analyze a specific Verilog file:**
```bash
python main.py examples/traffic_light.v
```

**Analyze the 50+ state protocol FSM:**
```bash
python main.py examples/protocol_fsm.v
```

**Use BFS traversal (default):**
```bash
python main.py examples/vending_machine.v
```

**Use DFS traversal:**
```bash
python main.py examples/vending_machine.v --method dfs
```

**Specify output directory:**
```bash
python main.py examples/traffic_light.v --output my_reports
```

**Quiet mode (less verbose output):**
```bash
python main.py examples/traffic_light.v --quiet
```

### Programmatic Usage

```python
from verilog_parser import parse_verilog_fsm
from fsm_traversal import FSMTraversal
from fsm_reporter import FSMReporter, print_summary

# Parse Verilog file
fsm_structure = parse_verilog_fsm("path/to/design.v")

# Create traversal engine
traversal = FSMTraversal(fsm_structure, verbose=True)

# Perform full analysis
results = traversal.full_analysis(method='bfs')

# Print summary
print_summary(results)

# Generate reports
reporter = FSMReporter(results, output_dir="my_reports")
reporter.generate_all_reports()
```

### Advanced Usage

**Command-line options:**
```bash
python main.py --help
```

**BFS vs DFS Traversal:**
- **BFS (Breadth-First)**: Explores all states level by level, guarantees shortest path
- **DFS (Depth-First)**: Explores depth-first, more memory efficient

```python
# Use BFS for complete reachability (default)
results_bfs = traversal.full_analysis(method='bfs')

# Use DFS for depth-limited exploration
results_dfs = traversal.full_analysis(method='dfs')
```

**Custom Initial State:**
```python
from fsm_traversal import FSMState

# Define custom initial state
initial = FSMState(state_vector=(1, 0, 1, 0), state_name="CUSTOM_INIT")
results = traversal.bfs_traversal(initial_state=initial)
```

**Individual Analyses:**
```python
# Only run traversal
results = traversal.bfs_traversal()

# Detect deadlocks
deadlocks = traversal.detect_deadlocks()

# Detect cycles
cycles = traversal.detect_cycles()
```

## Project Structure

```
formal_verification/
├── main.py                    # Main entry point (CLI)
├── verilog_parser.py          # Verilog parsing and FSM extraction
├── behavioral_simulator.py    # Behavioral Verilog simulation
├── fsm_traversal.py           # State space traversal algorithms
├── fsm_reporter.py            # Report generation and visualization
├── requirements.txt           # Python dependencies
├── README.md                  # This file
├── examples/                  # Example Verilog designs
│   ├── traffic_light.v        # 4-state traffic light controller
│   ├── vending_machine.v      # 5-state vending machine
│   ├── protocol_fsm.v         # 56-state communication protocol (50+ states)
│   ├── complex_counter.v      # 256-state counter FSM
│   └── sequence_detector.v    # Gate-level sequence detector
└── fsm_reports/               # Generated reports (created after running)
    ├── traffic_light_fsm/
    ├── vending_machine/
    └── complex_counter/
```

## Example Verilog Designs

### 1. Traffic Light Controller (`traffic_light.v`)
- **States**: 4 (RED, YELLOW, GREEN, RED_YELLOW)
- **Inputs**: 1 (sensor)
- **Outputs**: 3 (red_light, yellow_light, green_light)
- **Result**: 100% state coverage, 8 transitions

### 2. Vending Machine (`vending_machine.v`)
- **States**: 5 (0¢, 5¢, 10¢, 15¢, 20¢)
- **Inputs**: 2 (coin_5, coin_10)
- **Outputs**: 2 (dispense, change_5)
- **Result**: 62.5% state coverage (3 unreachable states), 20 transitions

### 3. Protocol FSM (`protocol_fsm.v`) - **50+ States**
- **States**: 56 reachable out of 64 possible (6-bit encoding)
- **Inputs**: 3 (start, ack, error)
- **Outputs**: 3 (busy, done, state_out)
- **Description**: Complex communication protocol with initialization, data transmission, CRC, acknowledgment, retry, and error handling phases
- **Result**: 87.5% state coverage, 448 transitions
- **Demonstrates**: Complex FSM traversal with 50+ states

### 4. Complex Counter (`complex_counter.v`)
- **States**: 256 (8-bit counter)
- **Inputs**: 2 (2-bit mode selector)
- **Outputs**: 3 (8-bit count + overflow + underflow)
- **Result**: Successfully builds 1024-entry transition table

## Output Reports

The tool generates multiple report formats in the `fsm_reports/<module_name>/` directory:

### 1. Text Report (`fsm_report.txt`)
Comprehensive human-readable analysis including:
- Summary statistics
- List of reachable states
- Transition table
- Deadlock states
- Detected cycles

### 2. Transition Table (`transition_table.csv`)
CSV format with columns:
- From_State
- Input
- Next_State
- Output

### 3. GraphViz DOT (`fsm_graph.dot`)
Graph representation for visualization:
```bash
# Generate PNG from DOT file
dot -Tpng fsm_graph.dot -o fsm_graph.png
```

### 4. JSON Export (`fsm_data.json`)
Machine-readable format for further processing

## Algorithm Details

### State Space Exploration

**Breadth-First Search (BFS):**
- Explores states level by level
- Guarantees shortest path to each state
- Better for finding all reachable states
- Memory-intensive for large FSMs

**Depth-First Search (DFS):**
- Explores along each branch
- More memory-efficient
- Good for detecting cycles
- Can be depth-limited

### Deadlock Detection
Identifies states with no outgoing transitions by checking if any input combination leads to a next state.

### Cycle Detection
Uses DFS-based algorithm with recursion stack to detect back edges, indicating cycles in the state graph.

## Verilog Parsing

The parser supports:
- **Behavioral Verilog**: always blocks, case statements, if-else statements
- **Sequential logic**: registers, state machines with next-state logic
- **Combinational logic**: continuous assignments
- **Parameters**: state encoding and constants

**Supported constructs:**
- Module declarations with parameters
- Input/output ports (automatically filters clock/reset)
- Register and wire declarations
- Always blocks (both sequential and combinational)
- Case statements for state transitions
- If-else statements for conditional logic

**Important Notes:**
- Clock (`clk`, `clock`) and reset (`rst`, `reset`) signals are automatically filtered from FSM inputs
- The tool uses the last `always` block containing next-state assignments (typically the combinational logic)
- State registers are identified by keywords: `state`, `curr`, `present`

## Troubleshooting

**Issue: "No obvious state register found"**
- **Solution**: Name your state register with `state`, `curr`, or `present` in the name
- Example: `reg [1:0] current_state;` or `reg [2:0] state;`

**Issue: "No next-state logic found"**
- **Solution**: Ensure you have an `always @(*)` block with case/if statements that assign to `next_state`
- The tool looks for assignments to variables containing "next" in the name

**Issue: "Only 1 state found" or low coverage**
- **Solution**: Check that your next-state logic is in a separate combinational `always @(*)` block
- Verify parameter values are correctly defined (e.g., `parameter RED = 2'b00;`)

**Issue: Unicode encoding errors**
- **Solution**: This has been fixed - all Unicode characters replaced with ASCII

## Limitations

1. **Parser Limitations:**
   - Focuses on behavioral Verilog (always blocks with case/if statements)
   - Gate-level designs may have limited support
   - Advanced SystemVerilog features not supported

2. **Traversal Limitations:**
   - Maximum state limit (default: 1000) for memory efficiency
   - Large state spaces (>10000 states) may be slow
   - Graph visualization limited to 50 states for readability

3. **State Identification:**
   - Relies on naming conventions (registers with "state" in name)
   - Clock and reset signals must be named conventionally

## Command Reference

```bash
# Run demo on all examples
python main.py --demo

# Analyze specific file
python main.py examples/traffic_light.v

# Use DFS instead of BFS
python main.py examples/vending_machine.v --method dfs

# Specify custom output directory
python main.py design.v --output my_reports

# Quiet mode (less verbose)
python main.py design.v --quiet

# Show help
python main.py --help
```

## Testing

Run the test suite:
```bash
python test_fsm.py
```



## Requirements

See `requirements.txt`:
```
pyverilog>=1.3.0    # Verilog parsing
pyeda>=0.28.0       # Boolean algebra
```

Optional for visualization:
```
graphviz>=0.20.0    # DOT file rendering
```

## License

This project is for educational purposes as part of formal verification coursework.

## References

- PyVerilog: https://github.com/PyHDI/Pyverilog
- PyEDA: https://pyeda.readthedocs.io/
- GraphViz: https://graphviz.org/

---

For questions or issues, refer to the course materials or contact the teaching staff.
