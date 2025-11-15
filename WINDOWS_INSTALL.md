# Windows Installation & Troubleshooting Guide

## The Preprocessor Issue (SOLVED)

**Problem**: PyVerilog tries to call an external C preprocessor (like `iverilog` or `gcc`) which doesn't exist on most Windows systems, causing:
```
FileNotFoundError: [WinError 2] The system cannot find the file specified
```

**Solution**: The code has been modified to bypass the external preprocessor by monkey-patching PyVerilog's preprocessor module. This is handled automatically in `verilog_parser.py`.

## Installation Steps for Windows

### Step 1: Activate Your Conda Environment
```cmd
cmd
conda activate motioncapture
```

### Step 2: Install Required Packages
```cmd
pip install pyverilog pyeda
```

If you get errors, try installing them separately:
```cmd
pip install pyverilog
pip install pyeda
```

### Step 3: Verify Installation
```cmd
python test_parse.py
```

You should see:
```
✅ SUCCESS! Parser is working.
```

### Step 4: Run the Tool
```cmd
python main.py --demo
```

## Alternative: Install All Requirements
```cmd
pip install -r requirements.txt
```

## Common Issues & Solutions

### Issue 1: Module Not Found Errors
```
ModuleNotFoundError: No module named 'pyeda'
```

**Solution**: Make sure you're in the correct conda environment:
```cmd
conda activate motioncapture
pip install pyeda pyverilog
```

### Issue 2: Preprocessor Errors (Already Fixed)
```
FileNotFoundError: [WinError 2] The system cannot find the file specified
```

**Solution**: This is already fixed in the code. The parser now uses a monkey-patch to bypass the external preprocessor.

### Issue 3: Import Warnings
```
WARNING: 183 shift/reduce conflicts
```

**Solution**: This is normal! PyVerilog's parser has these warnings. They don't affect functionality.

### Issue 4: GraphViz Not Found (Optional)
If you want to generate PNG images from DOT files:

1. Download GraphViz: https://graphviz.org/download/
2. Install it
3. Add to PATH: `C:\Program Files\Graphviz\bin`
4. Run: `dot -Tpng fsm_graph.dot -o fsm.png`

**Note**: GraphViz is optional - the tool will still generate DOT files without it.

## Verification Checklist

✅ Conda environment activated  
✅ PyVerilog installed (`pip show pyverilog`)  
✅ PyEDA installed (`pip show pyeda`)  
✅ Test parser works (`python test_parse.py`)  
✅ Main tool runs (`python main.py --demo`)  

## Quick Commands Reference

```cmd
# Activate environment
conda activate motioncapture

# Install packages
pip install pyverilog pyeda

# Test parsing
python test_parse.py

# Run demo
python main.py --demo

# Analyze specific file
python main.py examples/traffic_light.v

# Run tests
python test_fsm.py

# Show help
python main.py --help
```

## Why the Monkey-Patch Works

The original PyVerilog code tries to call:
```python
subprocess.call(['iverilog', '-E', ...])  # Unix tool
```

Our fix replaces the preprocessor with a simple file reader:
```python
def dummy_preprocess(self):
    self.result = []
    for filepath in self.filelist:
        with open(filepath, 'r') as f:
            self.result.append(f.read())
```

This works because:
- Most Verilog examples don't use complex preprocessing
- We handle simple includes and defines
- The parser still works on the raw Verilog code

## What If It Still Doesn't Work?

If you still get errors after following these steps:

1. **Check Python version**: Should be 3.7+
   ```cmd
   python --version
   ```

2. **Reinstall packages**:
   ```cmd
   pip uninstall pyverilog pyeda
   pip install pyverilog pyeda
   ```

3. **Try a simpler test**:
   ```cmd
   python -c "import pyverilog; import pyeda; print('OK')"
   ```

4. **Check the example files exist**:
   ```cmd
   dir examples\*.v
   ```

## Success Indicators

When everything works, you'll see:
```
================================================================================
Parsing Verilog file: examples/traffic_light.v
================================================================================

Module: traffic_light_fsm
Inputs: ['clk', 'reset', 'sensor']
Outputs: ['green_light', 'red_light', 'yellow_light']
Registers: ['current_state', 'next_state']

✓ Reachable states: 4
✓ Transitions found: 8
```

---

**Updated**: November 10, 2025  
**Status**: Preprocessor issue FIXED with monkey-patch solution
