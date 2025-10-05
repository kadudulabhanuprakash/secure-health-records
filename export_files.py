import os
from pathlib import Path

def extract_files(root_dir, include_files=None, exclude_dirs=None, extensions=None):
    root_dir = Path(root_dir)
    if include_files is None:
        include_files = [
            'main.py',
            'backend\\app\\__init__.py',
            'backend\\app\\models.py',
            'backend\\app\\routes\\auth.py',
            'backend\\app\\routes\\storage_routes.py',
            'backend\\app\\routes\\blockchain_routes.py',
            'backend\\app\\routes\\medical_forms.py',  # Added for medical forms
            'backend\\app\\routes\\blockchain_logger.py',  # Added for blockchain logger
            'backend\\app\\blockchain.py',
            'backend\\app\\services\\blockchain_service.py',
            'contracts\\AccessLogger.sol',
            'scripts\\deploy.js',
            'hardhat.config.js',
            'contracts\\AccessLogger.json',
            'frontend\\react_app\\src\\App.js',
            'frontend\\react_app\\src\\components\\Login.js',
            'frontend\\react_app\\src\\components\\Register.js',
            'frontend\\react_app\\src\\components\\PatientDashboard.js',
            'frontend\\react_app\\src\\components\\DoctorDashboard.js',
            'frontend\\react_app\\src\\components\\Navbar.js',
            'frontend\\react_app\\src\\components\\Login.css',  # Added for Login CSS
            'frontend\\react_app\\src\\components\\MedicalFormReview.js',  # Added for medical forms
            'frontend\\react_app\\src\\components\\MedicalForms.js',  # Added for medical forms
            'frontend\\react_app\\src\\components\\PrescriptionManagement.js',  # Added for prescriptions
            'frontend\\react_app\\src\\index.js',  # Added for index.js
            'frontend\\react_app\\package.json',
            '.env',
            'check.py',
            'test_env.py',
            'azure_blob_demo.py',
            'package.json',
            'patients\\sample_patient.txt',
            'patients\\sample_patient1.txt',
            'patients\\sample_patient2.txt',
            'patients\\sample_patient3.txt',
        ]
    if exclude_dirs is None:
        exclude_dirs = ['.venv', 'node_modules', '__pycache__', 'artifacts', 'cache', 'Projects-main']  # Added Projects-main to exclude
    if extensions is None:
        extensions = ['.py', '.js', '.json', '.sol', '.md', '.txt', '.html', '.css', '.gitignore']

    output = []
    found_files = set()

    # Normalize include_files to use backslashes
    normalized_include_files = [f.replace('/', '\\') for f in include_files]

    # Log all text files
    output.append("All Text Files Found:")
    for root, dirs, files in os.walk(root_dir, topdown=True):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        for file in files:
            if any(file.endswith(ext) for ext in extensions):
                file_path = Path(root) / file
                relative_path = str(file_path.relative_to(root_dir)).replace('/', '\\')
                output.append(f"- {relative_path}")
    output.append("\n---\n")

    # Extract contents of included files
    for root, dirs, files in os.walk(root_dir, topdown=True):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        for file in files:
            file_path = Path(root) / file
            relative_path = str(file_path.relative_to(root_dir)).replace('/', '\\')
            if (relative_path in normalized_include_files or 
                relative_path.lower() in [f.lower() for f in normalized_include_files] or
                file.lower() in [Path(f).name.lower() for f in normalized_include_files]):
                output.append(f"File: {relative_path}")
                found_files.add(relative_path)
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        lines = f.readlines()
                        for line_num, line in enumerate(lines, start=1):
                            output.append(f"Line {line_num}: {line.strip()}")
                    output.append("\n---\n")
                except Exception as e:
                    output.append(f"Error reading {relative_path}: {e}\n---\n")
            if file == 'package-lock.json':
                output.append(f"Skipped: {relative_path} (large generated file)\n---\n")

    # Log missing files
    missing_files = [f for f in normalized_include_files if f not in found_files]
    if missing_files:
        output.append("Missing Files:")
        for f in missing_files:
            output.append(f"- {f}")
        output.append("\n---\n")

    return '\n'.join(output)

if __name__ == "__main__":
    root_dir = r'C:\secure-health-records'
    extracted_content = extract_files(root_dir)
    with open('extracted_files.txt', 'w', encoding='utf-8') as out_f:
        out_f.write(extracted_content)
    print("Extracted content saved to 'extracted_files.txt'")