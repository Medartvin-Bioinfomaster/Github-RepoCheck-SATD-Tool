import json
import os
import webbrowser
import urllib.request

def generate_full_report(repo_path, report_data, stats):
    json_data = json.dumps(report_data["files"])
    
    percentCompromised = round((stats['locCompromised'] / stats['loc']) * 100, 1)
    json_contributors = json.dumps(report_data["data"]["contributorCommits"])

        # Opprett et strukturert objekt (dictionary) fra de flate stats-verdiene
    thresholds = {
        "satd_density_average": stats["satd_density_average"], 
        "satd_density_standard_deviation": stats["satd_density_standard_deviation"],
        "satd_density_max": stats["satd_density_max"],
        "compromised_density_average": stats["compromised_density_average"],
        "compromised_density_standard_deviation": stats["compromised_density_standard_deviation"],
        "compromised_density_max": stats["compromised_density_max"]
    }

    low_stddensity_risk = thresholds["satd_density_average"] #can be within this number to be low risk
    medium_stddensity_risk = thresholds["satd_density_max"] - thresholds["satd_density_standard_deviation"]
    # high_stddensity_risk = thresholds["satd_density_max"]

    low_compdens_risk = thresholds["compromised_density_average"] #can be within this number to be low risk
    medium_compdens_risk = thresholds["compromised_density_max"] - thresholds["compromised_density_standard_deviation"]

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
            
            <div class="stats-bar" style="display: flex; flex-wrap: wrap; gap: 20px; padding: 20px; align-items: baseline;">
                <!-- Gruppe 1: SATD Core -->
                <div class="stat-item">
                    <div class="number" style="color: {stats['health_color']}">{stats['health_status']}</div>
                    <div class="label">Codebase Health</div>
                </div>
                <div class="stat-item">
                    <div class="number">{stats['satd_count']}</div>
                    <div class="label">SATD comments</div>
                </div>
                <div class="stat-item">
                    <div class="number">{stats['density']}</div>
                    <div class="label">Avg. Density (kLOC)</div>
                </div>

                <!-- Gruppe 2: LOC Detaljer (Grå boks) -->
                <div style="display: flex; gap: 15px; background-color: #f0f0f0; padding: 10px 20px; border-radius: 12px; border: 2px dashed #ccc;">
                    <div class="stat-item"><div class="number">{stats['loc']}</div><div class="label">Total LOC</div></div>
                    <div class="stat-item"><div class="number">{stats['locCompromised']}</div><div class="label">Affected LOC</div></div>
                    <div class="stat-item">
                        <div class="number" style="color: {StatusDebtPercent(percentCompromised)};">{percentCompromised}%</div>
                        <div class="label">Ratio</div>
                    </div>
                </div>

                <!-- Gruppe 3: Prosjekt helse -->
                <div class="stat-item">
                    <div class="number">{stats['filessatd']} / {stats['totalfiles']}</div>
                    <div class="label">Affected Files</div>
                </div>
                <div class="stat-item">
                    <div class="number">{stats['commits']}</div>
                    <div class="label">Commits</div>
                </div>
                <div class="stat-item">
                    <div class="number">{stats['totalcontributors']}</div>
                    <div class="label">Contributors</div>
                </div>
            </div>

            <div class="stats-bar" style="flex-direction: column; align-items: flex-start;">
                <h2 style="font-size: 1.1em; margin-bottom: 10px; color: #444;">Commits distributed</h2>
                <div id="contributorList" style="display: flex; gap: 15px; overflow-x: auto; width: 100%; padding-bottom: 10px;">
                    </div>
            </div>

            <div class="stats-bar" style="flex-direction: column; align-items: flex-start; background: #f9f9f9; padding: 20px; border-radius: 12px; border: 1px solid #ddd;">
                <h2 style="font-size: 1.1em; margin-bottom: 15px; color: #333; display: flex; align-items: center; gap: 8px;">
                    Metrics Explained ℹ️
                </h2>

                <p>Low is everything less than average. Medium is Max density - standard deviation. High is everything above the Medium threshold number. All numbers are fetched from a github repository, where an average was calculated, a max value of the density was found, aswell as standard deviation.</p>
                
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; width: 100%;">
                    <!-- SATD Forklaring -->
                    <div style="background: white; padding: 15px; border-radius: 8px; border-left: 5px solid #2ecc71;">
                        <h3 style="margin: 0 0 10px 0; font-size: 0.9em; color: #666;">SATD Density Thresholds</h3>
                        <div style="display: flex; flex-direction: column; gap: 8px; font-size: 0.85em;">
                            <div style="display: flex; align-items: center; gap: 10px;">
                                <span style="width: 12px; height: 12px; background: #2ecc71; border-radius: 50%;"></span>
                                <span><strong>Low:</strong> 0 - {round(low_stddensity_risk, 2)}</span>
                            </div>
                            <div style="display: flex; align-items: center; gap: 10px;">
                                <span style="width: 12px; height: 12px; background: #f39c12; border-radius: 50%;"></span>
                                <span><strong>Medium:</strong> {round(low_stddensity_risk, 2)} - {round(medium_stddensity_risk, 2)}</span>
                            </div>
                            <div style="display: flex; align-items: center; gap: 10px;">
                                <span style="width: 12px; height: 12px; background: #e74c3c; border-radius: 50%;"></span>
                                <span><strong>Critical:</strong> above {round(medium_stddensity_risk, 2)}</span>
                            </div>
                            <div style="display: flex; align-items: center; gap: 10px;">
                                <p>This metric counts every sample of SATD found in a file, and normalizes it to be X samples within 1000 lines of code (LoC). This metric determines low, medium, or high levels of SATD cases within a file.</p>
                            </div>
                        </div>
                    </div>

                    <!-- Compromised Forklaring -->
                    <div style="background: white; padding: 15px; border-radius: 8px; border-left: 5px solid #e74c3c;">
                        <h3 style="margin: 0 0 10px 0; font-size: 0.9em; color: #666;">Compromised Lines Density</h3>
                        <div style="display: flex; flex-direction: column; gap: 8px; font-size: 0.85em;">
                            <div style="display: flex; align-items: center; gap: 10px;">
                                <span style="width: 12px; height: 12px; background: #2ecc71; border-radius: 50%;"></span>
                                <span><strong>Normal:</strong>  0 - {round(low_compdens_risk, 2)}</span>
                            </div>
                            <div style="display: flex; align-items: center; gap: 10px;">
                                <span style="width: 12px; height: 12px; background: #f39c12; border-radius: 50%;"></span>
                                <span><strong>Advarsel:</strong> {round(low_compdens_risk, 2)} - {round(medium_compdens_risk, 2)}</span>
                            </div>
                            <div style="display: flex; align-items: center; gap: 10px;">
                                <span style="width: 12px; height: 12px; background: #e74c3c; border-radius: 50%;"></span>
                                <span><strong>Kritisk (Outlier):</strong> above {round(medium_compdens_risk, 2)}</span>
                            </div>
                            <div style="display: flex; align-items: center; gap: 10px;">
                                <p>This metric counts every compromised line found in a file. A compromised line can be a function that contains SATD. This metric is normalized to x lines pr 1000 lines of code (LoC). This metric determines low, medium, or high levels of lines potentially compromised with SATD within a file.</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="divider">
                <div class="file-list-column">
                    <div class="controls-area">
                        <input type="text" class="search-box" id="fileSearch" placeholder="Search files..." onkeyup="filterFiles()">
                        <div style="display: flex; justify-content: space-between; align-items: center; width: 100%; margin-bottom: 15px; padding: 0 5px; gap: 20px;">

                            <div class="filter-group">
                                <button class="filter-btn active" onclick="setSatdFilter('BOTH', this)">Both</button>
                                <button class="filter-btn" onclick="setSatdFilter('HasSATD', this)">Satd</button>
                                <button class="filter-btn" onclick="setSatdFilter('Clean', this)">Clean</button>
                            </div>

                            <div id="riskStats" style="display: flex; gap: 15px; font-size: 0.85em; font-weight: 600;"></div>

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

                
                s_avg = {thresholds["satd_density_average"]}
                s_std = {thresholds["satd_density_standard_deviation"]}
                c_avg = {thresholds["compromised_density_average"]}
                c_std = {thresholds["compromised_density_standard_deviation"]}

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
                    <div style="background: white; padding: 20px; border-radius: 8px;">
                        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 20px;">
                            <h2>📄 ${{file.filename}}</h2>
                            <div style="background: #f0f0f0; padding: 8px 15px; border-radius: 20px; font-weight: bold;">
                                Risk: ${{riskState(file.risk_level)}} ${{file.risk_level}}
                            </div>
                        </div>

                        <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 20px; margin-bottom: 25px;">
                            
                            <div style="padding: 15px; background: #fafafa; border-radius: 8px;">
                                <h4 style="color: #666; margin-bottom: 10px; font-size: 0.8em; text-transform: uppercase;">File Info</h4>
                                <p><strong>LOC:</strong> ${{file.metrics.loc}}</p>
                                <p><strong>Lines compromised:</strong> ${{file.metrics.lines_compromised}} (${{file.metrics.lines_compromised_percentage}}%)</p>
                                <p><strong>Commits:</strong> ${{file.metrics.commits}}</p>
                                <p><strong>Status:</strong> <span style="color: ${{StatusDebt(file.metrics.hasSatd)}}">${{file.metrics.hasSatd ? "⚠️ Contains SATD" : "✅ Clean"}}</span></p>
                            </div>

                            <div style="padding: 15px; background: #fafafa; border-radius: 8px; border-left: 4px solid #e74c3c;">
                                <h4 style="color: #666; margin-bottom: 10px; font-size: 0.8em; text-transform: uppercase;">Debt Metrics</h4>
                                <p><strong>Occurrences:</strong> <span style="color: red; font-weight: bold;">${{file.metrics.satd_count}}</span></p>
                                <p style="color: ${{getSeverityColorSatd(file.metrics.file_td_density)}}">
                                    <strong>SATD Density:</strong> ${{file.metrics.file_td_density}}
                                </p>
                                <p style="color: ${{getSeverityColorComp(file.metrics.lines_compromised_density)}}">
                                    <strong>Comp. Density:</strong> ${{file.metrics.lines_compromised_density}}
                                </p>
                            </div>

                            <div style="padding: 15px; background: #fafafa; border-radius: 8px;">
                                <h4 style="color: #666; margin-bottom: 10px; font-size: 0.8em; text-transform: uppercase;">Activity (Past Year)</h4>
                                <p><strong>Churn Activity:</strong> ${{file.metrics.churn_activity}}</p>
                                <p><strong>Dev Status:</strong> ${{file.metrics.past_year_activity.dev_status}}</p>
                                <p><strong>Avg. Churn:</strong> ${{file.metrics.past_year_activity.average}}</p>
                            </div>
                        </div>

                        <div style="border-top: 1px solid #eee; padding-top: 15px; font-size: 0.85em; color: #555;">
                            <p style="margin-bottom: 10px;"><strong>Full Path:</strong> <code>${{file.file}}</code></p>
                            ${{contributorHtml}}
                        </div>

                        <h3>Report:</h3>
                        <pre style="background: #eee; padding: 15px; border-radius: 4px; white-space: pre-wrap;">${{file.Text}}</pre>
                    </div>
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

                function updateRiskCounters() {{
                    let counts = {{ High: 0, Medium: 0, Low: 0 }};

                    // Teller opp basert på file.risk_level i JSON-dataene
                    Object.values(allFiles).forEach(file => {{
                        if (counts.hasOwnProperty(file.risk_level)) {{
                            counts[file.risk_level]++;
                        }}
                    }});

                    const statsContainer = document.getElementById('riskStats');
                    if (statsContainer) {{
                        statsContainer.innerHTML = `
                            <span style="color: #e74c3c;">High: ${{counts.High}}</span>
                            <span style="color: #f39c12;">Medium: ${{counts.Medium}}</span>
                            <span style="color: #2ecc71;">Low: ${{counts.Low}}</span>
                        `;
                    }}
                }}


            window.onload = () => {{
                renderFiles();
                renderContributors();
                updateRiskCounters();
            }};
            
            function riskState(risk) {{
                return risk === "High" ? "🔴" : risk === "Medium" ? "🟠" : "🟢";
            }}

            function getSeverityColorSatd(value) {{
                if (value > {medium_stddensity_risk}) {{
                    return "red";    
                }} else if (value > {low_stddensity_risk}) {{
                    return "orange"; 
                }} else {{
                    return "green";
                }}
            }}

            function getSeverityColorComp(value) {{
                if (value > {medium_compdens_risk}) {{
                    return "red";    
                }} else if (value > {low_compdens_risk}) {{
                    return "orange"; 
                }} else {{
                    return "green";
                }}
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
