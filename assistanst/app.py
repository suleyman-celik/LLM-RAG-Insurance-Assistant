import os
import sys
from flask import Flask, request, jsonify
import nbconvert
import nbformat

import importlib.util

app = Flask(__name__)

# Dynamically import all notebooks as modules from the notebooks folder
NOTEBOOKS_DIR = os.path.join(os.path.dirname(__file__), '../notebooks')
sys.path.append(NOTEBOOKS_DIR)

def import_notebook_modules():
    modules = {}
    for fname in os.listdir(NOTEBOOKS_DIR):
        if fname.endswith('.ipynb'):
            py_fname = fname.replace('.ipynb', '.py')
            py_path = os.path.join(NOTEBOOKS_DIR, py_fname)
            # Convert .ipynb to .py if needed (requires nbconvert)
            if not os.path.exists(py_path):
                try:
                    with open(os.path.join(NOTEBOOKS_DIR, fname), 'r', encoding='utf-8') as f:
                        nb = nbformat.read(f, as_version=4)
                    exporter = nbconvert.PythonExporter()
                    source, _ = exporter.from_notebook_node(nb)
                    with open(py_path, 'w', encoding='utf-8') as f:
                        f.write(source)
                except Exception as e:
                    print(f"Error converting {fname}: {e}")
                    continue
            # Import the .py file as a module
            module_name = py_fname.replace('.py', '')
            spec = importlib.util.spec_from_file_location(module_name, py_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            modules[module_name] = module
    return modules

notebook_modules = import_notebook_modules()

@app.route('/ask', methods=['POST'])
def ask():
    data = request.json
    question = data.get('question', '')
    # Example: Use a function from a notebook module to answer
    # You may need to adjust this logic based on your notebooks' content
    for name, module in notebook_modules.items():
        if hasattr(module, 'answer_question'):
            try:
                answer = module.answer_question(question)
                return jsonify({'answer': answer})
            except Exception as e:
                continue
    return jsonify({'answer': "Sorry, I couldn't find an answer."})

if __name__ == '__main__':
    app.run(debug=True)