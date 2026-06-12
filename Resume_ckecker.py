import PyPDF2
import os

def process_resumes():
    # Folder paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    resumes_folder = os.path.join(script_dir, 'resumes')
    result_file = os.path.join(script_dir, 'Result2.txt')
    
    # Requirement files
    req_files = {'FRONTEND': 'frontend.txt', 'BACKEND': 'backend.txt', 'API': 'api.txt'}
    requirements = {}

    # 1. Load job descriptions
    for category, filename in req_files.items():
        filepath = os.path.join(script_dir, filename)
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                requirements[category] = {s.strip().lower() for s in f.read().split(',')}
        else:
            print(f"Error: {filename} nahi mili!")
            return

    # 2. Check resumes folder
    if not os.path.exists(resumes_folder):
        print(f"Error: 'resumes' folder nahi mila!")
        return

    pdf_list = [f for f in os.listdir(resumes_folder) if f.lower().endswith('.pdf')]
    
    if not pdf_list:
        print("Error: 'resumes' folder mein koi PDF nahi mili!")
        return

    # 3. Process each PDF
    with open(result_file, 'w', encoding='utf-8') as res:
        res.write("--- MISSING SKILLS ANALYSIS REPORT ---\n\n")
        
        for pdf_name in pdf_list:
            pdf_path = os.path.join(resumes_folder, pdf_name)
            
            # Extract text
            text = ""
            try:
                with open(pdf_path, 'rb') as f:
                    reader = PyPDF2.PdfReader(f)
                    for page in reader.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text.lower()
            except Exception as e:
                print(f"Could not read {pdf_name}: {e}")
                continue

            # Compare and Find Missing Skills
            res.write(f"Candidate: {pdf_name}\n")
            for category, req_skills in requirements.items():
                missing = [s for s in req_skills if s not in text]
                if missing:
                    res.write(f"  [{category}] Missing: {', '.join(missing)}\n")
                else:
                    res.write(f"  [{category}] All skills present!\n")
            res.write("-" * 50 + "\n")

    print(f"Process complete! Check '{result_file}' for results.")

if __name__ == "__main__":
    process_resumes()