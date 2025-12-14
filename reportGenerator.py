import os
import re
from collections import Counter, defaultdict



# For SATD
def _parse_report_file(path: str):
	"""Parse a single SATD report file to extract finding types and per-file counts."""
	types = []
	try:
		with open(path, 'r', encoding='utf-8', errors='replace') as f:
			for line in f:
				# Lines look like: "Line 23 [TODO]:"
				m = re.search(r"\[(?P<type>[A-Z\-]+)\]", line)
				if m:
					types.append(m.group('type'))
	except Exception:
		# Skip unreadable files silently
		pass
	return types



# For SATD
def generate_satd_overview(output_dir: str, repo_name: str) -> str:
	"""
	Generate a concise SATD overview TXT report.

	- Aggregates counts of SATD types across all files in output_dir
	- Highlights the most frequent SATD categories

	Returns the path to the created overview file.
	"""
	os.makedirs(output_dir, exist_ok=True)

	type_counter = Counter()
	file_type_counter = defaultdict(Counter)

	# Collect data from all .txt reports in the findings folder (excluding the overview itself)
	for fname in os.listdir(output_dir):
		if not fname.lower().endswith('.txt'):
			continue
		if fname.lower().startswith('satd_overview'):
			continue
		fpath = os.path.join(output_dir, fname)
		types = _parse_report_file(fpath)
		if types:
			type_counter.update(types)
			file_type_counter[fname].update(types)

	total_findings = sum(type_counter.values())
	files_with_satd = len([fn for fn, cnt in file_type_counter.items() if sum(cnt.values()) > 0])

	# Determine top categories
	top_types = type_counter.most_common(5)

	overview_path = os.path.join(output_dir, 'SATD_Overview.txt')
	with open(overview_path, 'w', encoding='utf-8') as out:
		out.write(f"Repository: {repo_name}\n")
		out.write(f"Overview of SATD findings (summary)\n")
		out.write("=" * 60 + "\n\n")
		out.write(f"Total SATD items detected: {total_findings}\n")
		out.write(f"Files containing SATD: {files_with_satd}\n")
		out.write("\n")

		if top_types:
			out.write("Top SATD categories:\n")
			for t, c in top_types:
				out.write(f"- {t}: {c}\n")
			out.write("\n")
		else:
			out.write("No SATD categories detected.\n\n")

		# Brief guidance and pointer to detailed reports
		out.write("Notes:\n")
		out.write("- This report provides a high-level overview of the most important SATD categories.\n")
		out.write("- More detailed SATD findings are available in the newly created 'SATD_findings' folder.\n")
		out.write("- Review per-file reports for specific lines and comments.\n")

	return overview_path




# Main summary report in base folder

def generate_base_summary(base_dir: str, repo_name: str, satd_total: int, satd_files: int, github_metrics: dict | None = None) -> str:
	


	os.makedirs(base_dir, exist_ok=True)
	summary_path = os.path.join(base_dir, 'Project_Summary.txt')
	

	with open(summary_path, 'w', encoding='utf-8') as out:
		out.write(f"Repository: {repo_name}\n")
		out.write("Project Summary\n")
		out.write("=" * 60 + "\n\n")


		# SATD section
		out.write("[SATD]\n")
		out.write(f"- Total SATD items: {satd_total}\n")
		out.write(f"- Files with SATD: {satd_files}\n")
		out.write("- Detailed SATD findings are available in the 'SATD_findings' folder.\n")
		out.write("- See 'SATD_Overview.txt' in that folder for a summarized breakdown.\n\n")


		# GitHub data section
		out.write("[GitHub Data]\n")
		if github_metrics:
			for key, value in github_metrics.items():
				out.write(f"- {key}: {value}\n")
		else:
			out.write("- No GitHub metrics provided yet. This section will include contributors, commits, and file change stats when available.\n")

	return summary_path

