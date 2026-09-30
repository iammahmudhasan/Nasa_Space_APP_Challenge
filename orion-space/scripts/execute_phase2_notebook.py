"""
execute_phase2_notebook.py
==========================
Executes 02_nasa_earth_system_multivariable_fdr.ipynb, capturing:
- All stdout text streams
- All matplotlib figures converted to base64 embedded display_data
- Sequential execution counts

Ensures the notebook is completely self-contained with rendered outputs for reviewers.
"""

import json
import os
import sys
import io
import base64
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

notebook_dir = Path(r"c:\Users\mah54\Desktop\Nasa_Space_APP_Challenge\orion-space\notebooks")
os.chdir(notebook_dir)

notebook_file = "02_nasa_earth_system_multivariable_fdr.ipynb"
with open(notebook_file, "r", encoding="utf-8") as f:
    nb = json.load(f)

# Global execution context
exec_globals = {}

execution_count = 1
for cell in nb["cells"]:
    if cell["cell_type"] == "code":
        code = "".join(cell["source"])
        print(f"Executing code cell {execution_count}...")

        # Monkeypatch plt.show to capture figure in display_data
        captured_figs = []
        original_show = plt.show

        def custom_show(*args, **kwargs):
            fig = plt.gcf()
            buf = io.BytesIO()
            fig.savefig(buf, format='png', bbox_inches='tight', dpi=120)
            buf.seek(0)
            b64_str = base64.b64encode(buf.read()).decode('utf-8')
            captured_figs.append(b64_str)
            plt.close(fig)

        plt.show = custom_show

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

            # Add captured text output
            if out_text:
                outputs.append({
                    "name": "stdout",
                    "output_type": "stream",
                    "text": out_text.splitlines(keepends=True)
                })

            # Add captured figure display_data
            for b64_img in captured_figs:
                outputs.append({
                    "data": {
                        "image/png": b64_img,
                        "text/plain": ["<Figure size 1200x600 with 1 Axes>"]
                    },
                    "metadata": {},
                    "output_type": "display_data"
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
            plt.show = original_show

        execution_count += 1

with open(notebook_file, "w", encoding="utf-8") as f:
    json.dump(nb, f, indent=2)

print(f"Phase 2 Notebook executed and saved successfully with embedded figures: {notebook_file}")
