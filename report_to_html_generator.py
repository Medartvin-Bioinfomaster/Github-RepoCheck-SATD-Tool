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

            .contrib-bar-container {{ display: flex; align-items: center; gap: 10px; margin-bottom: 8px; }}
            .contrib-mini-avatar {{ width: 24px; height: 24px; background: #333; color: white; border-radius: 50%;  display: flex; align-items: center; justify-content: center; font-size: 0.7em; font-weight: bold; flex-shrink: 0;            }}
            .progress-bg {{ background: #eee; border-radius: 15px; flex-grow: 1; height: 15px; overflow: hidden; position: relative; }}
            .progress-fill {{ background: #4c4c4c; height: 100%; border-radius: 4px; transition: width 0.5s ease-out; }} /*##97b0ff*/
            .contrib-label {{ min-width: 120px; font-size: 0.85em; color: #444; }}
            .contrib-percent {{ min-width: 45px; font-size: 0.8em; font-weight: bold; text-align: right; }}
            .file-divide {{display: flex; flex-direction: row-reverse; align-items: center;}}
            .file-notific {{background: #ff0000; color: white; border-radius: 50%; width: 20px; aspect-ratio: 1 / 1; display: flex; justify-content: center; align-items: center; font-size: 11px; font-weight: bold; flex-shrink: 0; margin-left: 10px;}}
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
                    <div class="stat-item"><div class="number">{stats['locCompromised']}</div><div class="label">Loc affected by SATD</div></div>
                    <div class="stat-item"><div class="number" style="color: {StatusDebtPercent(percentCompromised)};">{percentCompromised}%</div><div class="label">Percentage affected</div></div>
                </div>
                <div class="stat-item"><div class="number">{stats['density']}</div><div class="label">Technical Debt Density (pr 1000 loc)</div></div>
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
                            <button class="filter-btn" onclick="setSatdFilter('HasSATD', this)">Satd</button>
                            <button class="filter-btn" onclick="setSatdFilter('Clean', this)">Clean</button>
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
            let currentSatdFilter = 'BOTH'; // 'BOTH', 'HasSATD', 'Clean'
            let currentSearchTerm = '';

            function renderFiles() {{
                const list = document.getElementById('fileList');
                list.innerHTML = '';

                Object.values(allFiles).forEach(file => {{
                    const hasSatd = file.Text.includes("Contains SATD: True");
                    
                    const matchesSearch = file.filename.toLowerCase().includes(currentSearchTerm.toLowerCase());
                    let matchesSatd = true;
                    if (currentSatdFilter === 'HasSATD') matchesSatd = hasSatd;
                    if (currentSatdFilter === 'Clean') matchesSatd = !hasSatd;

                    if (matchesSearch && matchesSatd) {{
                        const div = document.createElement('div');
                        div.className = 'file-item';
                        div.dataset.hasSatd = hasSatd; 
                        
                        div.innerHTML = `
                            <div style="display: flex; align-items: center; gap: 10px;">
                                <span class="satd-badge" style="background-color: ${{StatusDebt(hasSatd)}}; min-width: 50px; text-align: center;">
                                    ${{hasSatd ? 'SATD' : 'Clean'}}
                                </span>
                                <div>
                                    <div class="file-divide">
                                        ${{hasSatd ? `<span class="file-notific">${{file.metrics.satd_count}}</span>` : ''}}
                                        <strong>📄${{file.filename}}</strong><br>
                                    </div>
                                    <small>Risk: ${{file.risk_level}}</small>
                                </div>
                            </div>
                        `;
                        div.onclick = () => showAnalysis(file, div);
                        list.appendChild(div);
                    }}
                }});
            }}

            function filterFiles() {{
                currentSearchTerm = document.getElementById('fileSearch').value;
                renderFiles();
            }}

            function setSatdFilter(type, btn) {{
                currentSatdFilter = type;
                
                document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                
                renderFiles();
            }}

            function StatusDebt(status) {{
                return status ? "#ff8282" : "#99d1ff";
            }}
            
            function StatusDebtPercent(percent) {{
                return percent > 30 ? "#ff3e3e" : percent > 10 ? "#ff9600" : "#31a524";
            }}

            function showAnalysis(file, element) {{
                document.querySelectorAll('.file-item').forEach(el => el.classList.remove('selected'));
                element.classList.add('selected');

                const view = document.getElementById('analysisView');
                const percentage = ((file.metrics.lines_compromised / file.metrics.loc) * 100).toFixed(1);

                let contributorHtml = '';
                if (file.contributor_data && file.contributor_data.length > 0) {{
                    contributorHtml = '<div style="margin: 20px 0;"><h3>Ownership Distribution:</h3>';
                    file.contributor_data.forEach(c => {{
                        const initials = c.username ? c.username.substring(0, 2).toUpperCase() : '??';
                        contributorHtml += `
                            <div class="contrib-bar-container">
                                <div class="contrib-mini-avatar">${{initials}}</div>
                                <div class="contrib-label">${{c.username}}</div>
                                <div class="progress-bg">
                                    <div class="progress-fill" style="width: ${{c.contribution_percent}};"></div>
                                </div>
                                <div class="contrib-percent">${{c.contribution_percent}}</div>
                            </div>
                        `;
                    }});
                    contributorHtml += '</div>';
                }}
                
                view.innerHTML = `
                    <h2>📄${{file.filename}}</h2>
                    <p><strong>File path:</strong> ${{file.file}}</p>
                    <p><strong>Contains SATD:</strong> <span style="color: ${{StatusDebt(file.metrics.hasSatd)}};">${{file.metrics.hasSatd ? "Yes" : "No"}}</span></p>
                    <p><strong>Total SATD Occurrences:</strong> <span style="font-weight: 700; color: red;"> ${{file.metrics.satd_count}}</span></p>
                    <p><strong>Lines of Code:</strong> ${{file.metrics.loc}}</p>
                    <p><strong>Lines Compromised:</strong> ${{file.metrics.lines_compromised}}</p>
                    <p><strong>Total Churn:</strong> ${{file.metrics.churn_total}}</p>
                    <p><strong>Churn Activity:</strong> ${{file.metrics.churn_activity}}</p>
                    <p><strong>SATD density (pr 1000 loc):</strong> ${{file.metrics.file_td_density}} (${{file.metrics.td_density_percentage}}%)</p>
                    <p><strong>Compromised Lines density (pr 1000 loc):</strong> ${{file.metrics.lines_compromised_density}} (${{file.metrics.lines_compromised_density_percentage}}%)</p>
                    <p><strong>Past yearly activity:
                        Average Churn: </strong> ${{file.metrics.past_year_activity.average}} (Normalized: ${{file.metrics.past_year_activity.average_normalized}})
                        Total Churn: </strong> ${{file.metrics.past_year_activity.total}} (Normalized: ${{file.metrics.past_year_activity.total_normalized}})
                        Biggest Churn: </strong> ${{file.metrics.past_year_activity.peak}} (Normalized: ${{file.metrics.past_year_activity.peak_normalized}})
                    </p>
                    <p><strong>Development status (Past year):</strong> ${{file.metrics.past_year_activity.dev_status}}</p>
                    <p><strong>Percentage:</strong> <span style="color: ${{StatusDebtPercent(parseFloat(percentage))}};">${{percentage}}%</span></p>
                    <p><strong>Risk Level:</strong> ${{riskState(file.risk_level)}} ${{file.risk_level}}</p>
                    <p><strong>Total commits:</strong><span style="font-weight: 700;color:#319fec;"> ${{file.metrics.commits}}</span></p>
                    ${{contributorHtml}}
                    <hr style="margin: 20px 0;">
                    <h3>Report:</h3>
                    <pre style="background: #eee; padding: 15px; border-radius: 4px; white-space: pre-wrap;">${{file.Text}}</pre>
                `;
            }}

            const contributorData = {json_contributors};

            function renderContributors() {{
                const container = document.getElementById('contributorList');
                
                if (!container || !contributorData) return;

                container.innerHTML = '';

                Object.values(contributorData).forEach(c => {{
                    const card = document.createElement('div');
                    card.classList.add("contributor-card");

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

    </script>


    </body>
    </html>"""

    report_file = os.path.join(repo_path, 'report.html')
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    return 'file:///' + urllib.request.pathname2url(os.path.abspath(report_file))

def StatusDebt(status): # status is bool
    return "#ff8282" if status else "#99d1ff"

def StatusDebtPercent(percent): # status is bool
    return "#ff3e3e" if percent > 30 else "#ff9600" if percent > 10 else "#31a524"
