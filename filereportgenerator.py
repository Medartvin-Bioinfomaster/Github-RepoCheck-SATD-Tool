import json
import os
import webbrowser
import urllib.request

def generate_full_report(repo_path, report_data, stats):
    json_data = json.dumps(report_data["files"])
    
    percentCompromised = round((stats['locCompromised'] / stats['loc']) * 100, 1)
    json_contributors = json.dumps(report_data["data"]["contributorCommits"])

    html_content = f"""<!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>SATD Knowledge Base - {os.path.basename(repo_path)}</title>
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background-color: #f5f5f5; padding: 20px; }}
            .container {{ max-width: 1100px; margin: 0 auto; background: white; border: 1px solid #ddd; border-radius: 4px; overflow: hidden; }}
            header {{ padding: 30px 40px; border-bottom: 2px solid #333; }}
            .contributor-card {{ min-width: 160px;background: white;padding: 15px;border: 1px solid #ddd;border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.08);                        display: flex;                        flex-direction: column;                        align-items: center;                        text-align: center;                        flex-shrink: 0;}}
            .stats-bar {{ display: flex; gap: 30px; padding: 25px 40px; background: #fafafa; border-bottom: 1px solid #ddd; flex-wrap: wrap; }}
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
                <h1>{stats['repoName']}</h1>
                <p>Analysis for: <strong>{repo_path}</strong></p>
            </header>
            
            <div class="stats-bar">
                <div class="stat-item"><div class="number">{stats['satd_count']}</div><div class="label">SATD comments</div></div>
                <div style="display: flex; gap: 10px; background-color: #ededed; padding: 4px 15px; border-radius: 10px;">
                    <div class="stat-item"><div class="number">{stats['loc']}</div><div class="label">Lines of code (Loc)</div></div>
                    <div class="stat-item"><div class="number">{stats['locCompromised']}</div><div class="label">Loc affected</div></div>
                    <div class="stat-item"><div class="number" style="color: {StatusDebtPercent(percentCompromised)};">{percentCompromised}%</div><div class="label">Percentage</div></div>
                </div>
                <div class="stat-item"><div class="number">{stats['density']}</div><div class="label">SATD Density</div></div>
                <div class="stat-item"><div class="number">{stats['commits']}</div><div class="label">Total Commits</div></div>
                <div class="stat-item"><div class="number">{stats['totalfiles']}</div><div class="label">Files</div></div>
                <div class="stat-item"><div class="number">{stats['filessatd']}/{stats['totalfiles']}</div><div class="label">Files affected</div></div>
                <div class="stat-item"><div class="number">{stats['totalcontributors']}</div><div class="label">Contributors</div></div>
            </div>

            <div class="stats-bar" style="flex-direction: column; align-items: flex-start;">
                <h2 style="font-size: 1.1em; margin-bottom: 10px; color: #444;">Commits distributed</h2>
                <div id="contributorList" style="display: flex; gap: 15px; overflow-x: auto; width: 100%; padding-bottom: 10px;">
                    </div>
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
                <p>&copy; 2026 el calebra el calebra</p>
            </footer>
        </div>

        
        <script>
            const allFiles = {json_data};
            let currentSatdFilter = 'BOTH'; // 'BOTH', 'WITH', 'NO'
            let currentSearchTerm = '';

            function renderFiles() {{
                const list = document.getElementById('fileList');
                list.innerHTML = '';

                Object.values(allFiles).forEach(file => {{
                    const hasSatd = file.Text.includes("Contains SATD: True");
                    
                    // --- Filtreringslogikk ---
                    const matchesSearch = file.filename.toLowerCase().includes(currentSearchTerm.toLowerCase());
                    let matchesSatd = true;
                    if (currentSatdFilter === 'WITH') matchesSatd = hasSatd;
                    if (currentSatdFilter === 'NO') matchesSatd = !hasSatd;

                    if (matchesSearch && matchesSatd) {{
                        const div = document.createElement('div');
                        div.className = 'file-item';
                        // Vi bruker 'dataset' for å enkelt kunne finne tilbake til SATD-status om nødvendig
                        div.dataset.hasSatd = hasSatd; 
                        
                        div.innerHTML = `
                            <div style="display: flex; align-items: center; gap: 10px;">
                                <span class="satd-badge" style="background-color: ${{StatusDebt(hasSatd)}}; min-width: 50px; text-align: center;">
                                    ${{hasSatd ? 'SATD' : 'Clean'}}
                                </span>
                                <div>
                                    <strong>📄${{file.filename}}</strong><br>
                                    <small>Risk: ${{file.risk_level}}</small>
                                </div>
                            </div>
                        `;
                        div.onclick = () => showAnalysis(file, div);
                        list.appendChild(div);
                    }}
                }});
            }}

            // Funksjon for søkefeltet
            function filterFiles() {{
                currentSearchTerm = document.getElementById('fileSearch').value;
                renderFiles();
            }}

            // Funksjon for knappene
            function setSatdFilter(type, btn) {{
                currentSatdFilter = type;
                
                // Oppdater UI på knappene
                document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                
                renderFiles();
            }}

            function StatusDebt(status) {{
                return status ? "#ff8282" : "#63c97e";
            }}
            
            function StatusDebtPercent(percent) {{
                return percent > 30 ? "#ff3e3e" : percent > 10 ? "#ff9600" : "#31a524";
            }}

            function showAnalysis(file, element) {{
                document.querySelectorAll('.file-item').forEach(el => el.classList.remove('selected'));
                element.classList.add('selected');

                const view = document.getElementById('analysisView');
                const percentage = ((file.metrics.lines_compromised / file.metrics.loc) * 100).toFixed(1);
                
                view.innerHTML = `
                    <h2>📄${{file.filename}}</h2>
                    <p><strong>File path:</strong> ${{file.file}}</p>
                    <p><strong>Contains SATD:</strong> <span style="color: ${{StatusDebt(file.metrics.hasSatd)}};">${{file.metrics.hasSatd ? "Yes" : "No"}}</span></p>
                    <p><strong>Risk Level:</strong> ${{riskState(file.risk_level)}} ${{file.risk_level}}</p>
                    <p><strong>Lines of Code:</strong> ${{file.metrics.loc}}</p>
                    <p><strong>Lines affected by TD:</strong> ${{file.metrics.lines_compromised}}</p>
                    <p><strong>Percentage:</strong> <span style="color: ${{StatusDebtPercent(parseFloat(percentage))}};">${{percentage}}%</span></p>
                    <hr style="margin: 20px 0;">
                    <h3>Report:</h3>
                    <pre style="background: #eee; padding: 15px; border-radius: 4px; white-space: pre-wrap;">${{file.Text}}</pre>
                `;
            }}

            // Hent ut bidragsyter-data fra JSON-objektet ditt
            // (Sørg for at report_data["data"]["contributorCommits"] er inkludert i json_data i Python-scriptet)
            const contributorData = {json_contributors}; // Du kan også sende dette som en separat variabel


            function renderContributors() {{
                const container = document.getElementById('contributorList');
                
                // Sjekk at containeren finnes og at vi faktisk har data
                if (!container || !contributorData) return;

                // Tøm containeren først (i tilfelle re-render)
                container.innerHTML = '';

                // Object.values henter ut alle objektene uavhengig av hvor mange det er
                Object.values(contributorData).forEach(c => {{
                    const card = document.createElement('div');
                    card.classList.add("contributor-card");

                    // Lag en enkel avatar fra første bokstav
                    const firstLetter = c.username ? c.username.charAt(0).toUpperCase() : '?';
                    const secondLetter = c.username ? c.username.charAt(1).toUpperCase() : '?';

                    card.innerHTML = `
                        <div style="width: 45px; height: 45px; background: #333; color: white; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; margin-bottom: 10px; font-size: 1.2em;">
                            ${{firstLetter}}${{secondLetter}}
                        </div>
                        <div style="font-weight: 600; font-size: 0.95em; color: #333; margin-bottom: 4px;">${{c.username}}</div>
                        <div style="font-size: 0.85em; color: #666; background: #f0f0f0; padding: 2px 10px; border-radius: 10px;">
                            ${{c.commits}} commits
                        </div>
                    `;
                    container.appendChild(card);
                }});
            }}


            window.onload = () => {{
                renderFiles();
                renderContributors();
            }};
            
            function riskState(risk) {{
                return risk === "High" ? "⚠️" : risk === "Medium" ? "🟠" : "🟢";
            }}

            //window.onload = renderFiles;
    </script>


    </body>
    </html>"""

    report_file = os.path.join(repo_path, 'report.html')
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    return 'file:///' + urllib.request.pathname2url(os.path.abspath(report_file))

def StatusDebt(status): # status is bool
    return "#ff8282" if status else "#63c97e"

def StatusDebtPercent(percent): # status is bool
    return "#ff3e3e" if percent > 30 else "#ff9600" if percent > 10 else "#31a524"
