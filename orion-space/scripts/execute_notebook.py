"""
Execute 01_nasa_temperature_analysis.ipynb and save outputs directly into the notebook.
"""
import json
import os
import sys
import matplotlib
matplotlib.use('Agg')

# Change working directory to notebooks/ folder so relative paths match
notebook_dir = r"c:\Users\mah54\Desktop\Nasa_Space_APP_Challenge\orion-space\notebooks"
os.chdir(notebook_dir)

notebook_file = "01_nasa_temperature_analysis.ipynb"
with open(notebook_file, "r", encoding="utf-8") as f:
    nb = json.load(f)

# Global execution context
exec_globals = {}

execution_count = 1
for cell in nb["cells"]:
    if cell["cell_type"] == "code":
        code = "".join(cell["source"])
        print(f"Executing cell {execution_count}...")
        
        # Capture stdout
        from io import StringIO
        old_stdout = sys.stdout
        redirected_output = StringIO()
        sys.stdout = redirected_output
        
        try:
            exec(code, exec_globals)
            out_text = redirected_output.getvalue()
            cell["execution_count"] = execution_count
            outputs = []
            if out_text:
                outputs.append({
                    "name": "stdout",
                    "output_type": "stream",
                    "text": out_text.splitlines(keepends=True)
                })
            cell["outputs"] = outputs
        except Exception as e:
            out_text = redirected_output.getvalue()
            cell["execution_count"] = execution_count
            cell["outputs"] = [
                {
                    "name": "stderr",
                    "output_type": "stream",
                    "text": (out_text + "\n" + str(e)).splitlines(keepends=True)
                }
            ]
            print(f"Error in cell {execution_count}: {e}", file=old_stdout)
        finally:
            sys.stdout = old_stdout
            
        execution_count += 1

with open(notebook_file, "w", encoding="utf-8") as f:
    json.dump(nb, f, indent=2)

print("Notebook execution and saving completed successfully!")
