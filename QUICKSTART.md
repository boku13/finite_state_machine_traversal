# Quick Start Guide - FSM Traversal Tool

## Installation (5 minutes)

### Step 1: Verify Python Installation
```powershell
python --version
```
Ensure Python 3.7 or higher is installed.

### Step 2: Install Dependencies
```powershell
cd c:\Users\SQREAM\Desktop\semester_seven\formal_verification
pip install -r requirements.txt
```

### Step 3: Run Test Suite
```powershell
python test_fsm.py
```

## Running the Tool (3 methods)

### Method 1: Quick Demo (Recommended for first-time users)
```powershell
python main.py --demo
```
This analyzes all example designs and generates reports.

### Method 2: Analyze a Specific Design
```powershell
python main.py examples/traffic_light.v
```

### Method 3: Advanced Usage
```powershell
# Use DFS instead of BFS
python main.py examples/vending_machine.v --method dfs

# Specify custom output directory
python main.py examples/complex_counter.v --output my_analysis

# Quiet mode
python main.py examples/sequence_detector.v --quiet
```

## Understanding the Output

After running analysis, you'll find reports in `fsm_reports/<module_name>/`:

1. **fsm_report.txt** - Comprehensive text report with:
   - Summary statistics
   - List of reachable states
   - Transition table
   - Deadlock states
   - Detected cycles

2. **transition_table.csv** - Spreadsheet-compatible transition table

3. **fsm_graph.dot** - GraphViz diagram (visualize with: `dot -Tpng fsm_graph.dot -o fsm.png`)

4. **fsm_data.json** - Machine-readable data for further processing

## Example: Analyzing Your Own Design

1. **Create your Verilog file** (e.g., `my_fsm.v`)

2. **Ensure your FSM follows these guidelines:**
   - Name state registers with keywords: "state", "curr", "present", "ps"
   - Use clear input/output declarations
   - Include reset logic

3. **Run analysis:**
```powershell
python main.py my_fsm.v
```

4. **Check the output:**
```powershell
cd fsm_reports/my_fsm
type fsm_report.txt
```

## Programmatic Usage Example

Create a Python script:

```python
from verilog_parser import parse_verilog_fsm
from fsm_traversal import FSMTraversal
from fsm_reporter import FSMReporter

# Parse Verilog
fsm = parse_verilog_fsm("my_design.v")

# Analyze
traversal = FSMTraversal(fsm)
results = traversal.full_analysis()

# Generate reports
reporter = FSMReporter(results)
reporter.generate_all_reports()
```

## Troubleshooting

**Problem**: Import errors
```powershell
# Solution: Reinstall dependencies
pip install --upgrade -r requirements.txt
```

**Problem**: "No obvious state register found"
```
# Solution: Ensure your state register contains one of these keywords:
# "state", "curr", "current", "present", "ps", "fsm"
```

**Problem**: Analysis takes too long
```powershell
# Solution: Limit state exploration
python main.py design.v --max-states 100
```

## Next Steps

1. ✅ Run the demo: `python main.py --demo`
2. ✅ Explore example designs in `examples/` folder
3. ✅ Read the full README.md for detailed documentation
4. ✅ Analyze your own Verilog designs
5. ✅ Check generated reports in `fsm_reports/`

## Getting Help

```powershell
# Show help message
python main.py --help

# Run tests
python test_fsm.py

# Run specific example
python fsm_demo.py examples/traffic_light.v
```

## Key Features at a Glance

| Feature | Command | Output |
|---------|---------|--------|
| Demo all examples | `python main.py --demo` | Reports for all examples |
| Analyze one file | `python main.py design.v` | Full analysis report |
| Use DFS | `python main.py design.v --method dfs` | DFS-based analysis |
| Quiet mode | `python main.py design.v -q` | Minimal console output |
| Custom output | `python main.py design.v -o mydir` | Reports in mydir/ |

---

**Ready to start?** Run: `python main.py --demo`
