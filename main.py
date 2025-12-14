import os
import shutil
import tempfile
from fileAnalyzer import clone_repository, scan_repo_and_save_reports
from reportGenerator import generate_satd_overview, generate_base_summary



def main_loop():
    print("#/3#/3 Welcome to the Technical Debt Management Tool 3\\#3\\#")

    #stage 1
    print("What repository do you want to analyze?")

    
    github_url = input("Enter GitHub repository URL: ").strip()

    if not github_url:
        print("No URL provided. Exiting.")
        return
    

    # Create a temporary directory for SATD scanning and for saving reports
    repo_name = github_url.rstrip('/').split('/')[-1].replace('.git', '')
    temp_dir = tempfile.mkdtemp(prefix="satd_scan_")
    output_dir = os.path.join(os.getcwd(), "SATD_findings")



    # Clone the repository and scan for SATD
    try:
        clone_repository(github_url, temp_dir)
        print("Starting TOOL")
        total, files_count, _reports = scan_repo_and_save_reports(temp_dir, output_dir, repo_name)

        print("\n" + "=" * 60)
        if total:

            # Create concise overview report in SATD_findings
            overview_path = generate_satd_overview(output_dir, repo_name)
            print(f"Overview report generated: {overview_path}")

            # Create base folder project summary with SATD and GitHub sections
            base_dir = os.getcwd()
            summary_path = generate_base_summary(base_dir, repo_name, total, files_count, github_metrics=None)
            print(f"Base project summary generated: {summary_path}")
            
        else:
            print("Scan complete. No SATD comments found.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


        # Repo for testing: https://github.com/Medartvin-Bioinfomaster/Technicaldebt_in_bioinforamtics.git



if __name__ == "__main__":
    main_loop()