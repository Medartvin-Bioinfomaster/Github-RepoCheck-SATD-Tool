import json
import os
import webbrowser
import urllib.request

def generate_full_report(repo_path, report_data, stats):
    # Konverter data til JSON-streng for injisering i JS
    json_data = json.dumps(report_data["files"])
    
    # HTML-malen som en f-streng
    html_content = f"""<!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>SATD Knowledge Base - {os.path.basename(repo_path)}</title>
        <style>
            /* Her limer du inn all CSS-en din */
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background-color: #f5f5f5; padding: 20px; }}
            .container {{ max-width: 1100px; margin: 0 auto; background: white; border: 1px solid #ddd; border-radius: 4px; overflow: hidden; }}
            header {{ padding: 30px 40px; border-bottom: 2px solid #333; }}
            .stats-bar {{ display: flex; gap: 30px; padding: 25px 40px; background: #fafafa; border-bottom: 1px solid #ddd; }}
            .stat-item .number {{ font-size: 1.8em; font-weight: 600; }}
            .stat-item .label {{ color: #666; font-size: 0.9em; }}
            .divider {{ display: flex; width: 100%; height: 600px; background-color: #eee; gap: 1px; }}
            .file-list-column {{ flex: 4; display: flex; flex-direction: column; background: white; padding: 20px; }}
            .analysis-column {{ flex: 6; background: #fafafa; padding: 20px; overflow-y: auto; }}
            .search-box {{ width: 100%; padding: 10px; margin-bottom: 10px; border: 1px solid #ccc; border-radius: 4px; }}
            .filter-group {{ display: flex; gap: 5px; margin-bottom: 10px; }}
            .filter-btn {{ padding: 5px 10px; font-size: 0.8em; cursor: pointer; border: 1px solid #ccc; background: white; }}
            .filter-btn.active {{ background: #333; color: white; }}
            .file-entries-scroll {{ flex-grow: 1; overflow-y: auto; border: 1px solid #eee; }}
            .file-item {{ padding: 12px; border-bottom: 1px solid #eee; cursor: pointer; display: flex; justify-content: space-between; align-items: center; }}
            .file-item:hover {{ background: #f0f7ff; }}
            .file-item.selected {{ background: #e3f2fd; border-left: 4px solid #2196f3; }}
            .satd-badge {{ font-size: 0.7em; padding: 2px 6px; border-radius: 10px; background: #e0e0e0; }}
            .satd-badge.true {{ background: #d4edda; color: #155724; }}
            .placeholder-text {{ color: #999; text-align: center; margin-top: 50px; font-style: italic; }}
            footer {{ text-align: center; padding: 20px; color: #666; font-size: 0.85em; border-top: 1px solid #ddd; }}
        </style>
    </head>
    <body>
        <div class="container">
            <header>
                <h1>Repository Analyzer</h1>
                <p>Analysis for: <strong>{repo_path}</strong></p>
            </header>
            
            <div class="stats-bar">
                <div class="stat-item"><div class="number">{stats['satd_count']}</div><div class="label">SATD comments</div></div>
                <div class="stat-item"><div class="number">{stats['loc']}</div><div class="label">Loc</div></div>
                <div class="stat-item"><div class="number">{stats['density']}%</div><div class="label">SATD Density</div></div>
            </div>
            
            <div class="divider">
                <div class="file-list-column">
                    <div class="controls-area">
                        <input type="text" class="search-box" id="fileSearch" placeholder="Search files..." onkeyup="filterFiles()">
                        <div class="filter-group">
                            <button class="filter-btn active" onclick="setSatdFilter('BOTH', this)">Both</button>
                            <button class="filter-btn" onclick="setSatdFilter('WITH', this)">WithSatd</button>
                            <button class="filter-btn" onclick="setSatdFilter('NO', this)">NoSatd</button>
                        </div>
                    </div>
                    <div class="file-entries-scroll" id="fileList"></div>
                </div>
                <div class="analysis-column" id="analysisView">
                    <div class="placeholder-text">Click on a file to view its analysis</div>
                </div>
            </div>

            <footer>
                <p>&copy; 2026 Repository Analyzer Tool</p>
            </footer>
        </div>

        <script>
            const allFiles = {json_data};
            let currentFilter = 'BOTH';

            function renderFiles() {{
                const list = document.getElementById('fileList');
                const searchVal = document.getElementById('fileSearch').value.toLowerCase();
                list.innerHTML = '';

                allFiles.forEach(file => {{
                    const matchesSearch = file.name.toLowerCase().includes(searchVal);
                    const matchesFilter = 
                        currentFilter === 'BOTH' || 
                        (currentFilter === 'WITH' && file.hasSatd) || 
                        (currentFilter === 'NO' && !file.hasSatd);

                    if (matchesSearch && matchesFilter) {{
                        const div = document.createElement('div');
                        div.className = 'file-item';
                        div.innerHTML = `
                            <span>📄 ${{file.name}}</span>
                            <span class="satd-badge ${{file.hasSatd ? 'true' : ''}}">${{file.hasSatd ? '✓ HasSatd' : 'NoSatd'}}</span>
                        `;
                        div.onclick = () => showAnalysis(file, div);
                        list.appendChild(div);
                    }}
                }});
            }}

            function showAnalysis(file, element) {{
                document.querySelectorAll('.file-item').forEach(el => el.classList.remove('selected'));
                element.classList.add('selected');

                const view = document.getElementById('analysisView');
                // Her kan du tilpasse hvordan dataene vises
                view.innerHTML = `
                    <h2>${{file.name}}</h2>
                    <hr style="margin: 15px 0; border: 0; border-top: 1px solid #ddd;">
                    <div style="background: #1e1e1e; color: #d4d4d4; padding: 20px; border-radius: 4px; font-family: monospace; white-space: pre-wrap;">${{file.data}}</div>
                `;
            }}

            function setSatdFilter(type, btn) {{
                currentFilter = type;
                document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                renderFiles();
            }}

            function filterFiles() {{ renderFiles(); }}

            // Start visning
            window.onload = renderFiles;
        </script>
    </body>
    </html>"""

    # Lagre filen i den spesifikke mappen for dette repoet
    # if not os.path.exists(repo_path):
    #     os.makedirs(repo_path)
    
    report_file = os.path.join(repo_path, 'report.html')
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    return 'file:///' + urllib.request.pathname2url(os.path.abspath(report_file))