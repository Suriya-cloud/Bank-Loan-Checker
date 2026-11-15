/* LoanWise Result Rendering & Chart.js Visualizations */

document.addEventListener('DOMContentLoaded', () => {
    if (window.SERVER_POST_RESULT) {
        renderResult(window.SERVER_POST_RESULT);
        return;
    }

    const rawResultData = sessionStorage.getItem('loanwise_assessment_result');
    
    if (!rawResultData) {
        // If accessed directly without running assessment, load last history item or show message
        fetch('/api/history')
            .then(res => res.json())
            .then(data => {
                if (data.history && data.history.length > 0) {
                    fetch(`/api/history/${data.history[0].id}`)
                        .then(r => r.json())
                        .then(detail => {
                            if (detail && detail.full_result) {
                                renderResult(detail.full_result);
                            }
                        });
                } else {
                    document.getElementById('resultContainer').innerHTML = `
                        <div class="glass-card text-center my-5 py-5">
                            <i class="fas fa-exclamation-circle text-warning fa-3x mb-3"></i>
                            <h3>No Recent Assessment Result Found</h3>
                            <p class="text-secondary mb-4">Please submit an assessment to view AI loan eligibility and risk predictions.</p>
                            <a href="/assessment" class="btn btn-primary-custom">Start Assessment</a>
                        </div>
                    `;
                }
            });
        return;
    }

    const result = JSON.parse(rawResultData);
    renderResult(result);
});

function renderResult(res) {
    // 1. Decision Badge & Scores
    const badgeContainer = document.getElementById('decisionBadgeContainer');
    const scoreVal = document.getElementById('finalScoreVal');
    const scoreCircle = document.getElementById('scoreCircle');
    const riskBadge = document.getElementById('riskLevelBadge');
    const confidenceBadge = document.getElementById('confidenceBadge');

    if (scoreVal) scoreVal.textContent = Math.round(res.final_score);
    if (scoreCircle) scoreCircle.style.setProperty('--score', res.final_score);

    if (badgeContainer) {
        if (res.decision === 'ELIGIBLE') {
            badgeContainer.innerHTML = `<span class="badge-eligible"><i class="fas fa-check-circle"></i> ELIGIBLE</span>`;
        } else if (res.decision === 'CONDITIONALLY_ELIGIBLE') {
            badgeContainer.innerHTML = `<span class="badge-conditional"><i class="fas fa-exclamation-triangle"></i> CONDITIONALLY ELIGIBLE</span>`;
        } else {
            badgeContainer.innerHTML = `<span class="badge-not-eligible"><i class="fas fa-times-circle"></i> NOT ELIGIBLE</span>`;
        }
    }

    if (riskBadge) {
        const rColor = res.risk_level === 'LOW' ? 'text-success' : (res.risk_level === 'MEDIUM' ? 'text-warning' : 'text-danger');
        riskBadge.innerHTML = `<i class="fas fa-shield-alt ${rColor}"></i> Risk: <strong>${res.risk_level}</strong>`;
    }

    if (confidenceBadge) {
        const cBg = res.confidence === 'HIGH' ? 'bg-success' : (res.confidence === 'MEDIUM' ? 'bg-warning text-dark' : 'bg-danger');
        confidenceBadge.innerHTML = `<span class="badge ${cBg}">Consensus Confidence: ${res.confidence}</span>`;
    }

    // 2. Disagreement Alert
    const disagAlert = document.getElementById('disagreementAlert');
    if (disagAlert) {
        if (res.has_disagreement) {
            disagAlert.classList.remove('d-none');
            document.getElementById('disagreementRangeVal').textContent = res.disagreement_range;
        } else {
            disagAlert.classList.add('d-none');
        }
    }

    // 3. Score Breakdown Cards
    if (document.getElementById('mlScoreVal')) document.getElementById('mlScoreVal').textContent = res.ml_score + '%';
    if (document.getElementById('ruleScoreVal')) document.getElementById('ruleScoreVal').textContent = res.rule_score + '/100';
    if (document.getElementById('finScoreVal')) document.getElementById('finScoreVal').textContent = res.financial_score + '/100';

    // 4. ML Models Chart (Chart.js)
    const ctxModels = document.getElementById('mlModelsChart');
    if (ctxModels && res.models) {
        new Chart(ctxModels, {
            type: 'bar',
            data: {
                labels: ['Logistic Regression', 'Random Forest', 'Decision Tree', 'XGBoost / GradBoost'],
                datasets: [{
                    label: 'Approval Probability (%)',
                    data: [
                        res.models.logistic_regression || 0,
                        res.models.random_forest || 0,
                        res.models.decision_tree || 0,
                        res.models.xgboost || 0
                    ],
                    backgroundColor: [
                        'rgba(79, 70, 229, 0.75)',
                        'rgba(6, 182, 212, 0.75)',
                        'rgba(16, 185, 129, 0.75)',
                        'rgba(245, 158, 11, 0.75)'
                    ],
                    borderColor: [
                        '#4f46e5',
                        '#06b6d4',
                        '#10b981',
                        '#f59e0b'
                    ],
                    borderWidth: 1.5,
                    borderRadius: 6
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,
                        grid: { color: 'rgba(255, 255, 255, 0.05)' },
                        ticks: { color: '#94a3b8' }
                    },
                    x: {
                        grid: { display: false },
                        ticks: { color: '#94a3b8' }
                    }
                },
                plugins: {
                    legend: { display: false }
                }
            }
        });
    }

    // 5. Triggered Rules List
    const rulesList = document.getElementById('triggeredRulesList');
    if (rulesList && res.triggered_rules) {
        if (res.triggered_rules.length === 0) {
            rulesList.innerHTML = `<li class="list-group-item bg-transparent text-secondary">No specific risk rules triggered.</li>`;
        } else {
            rulesList.innerHTML = res.triggered_rules.map(rule => {
                let badgeClass = 'bg-info';
                if (rule.severity === 'critical') badgeClass = 'bg-danger';
                else if (rule.severity === 'high') badgeClass = 'bg-warning text-dark';
                else if (rule.severity === 'positive') badgeClass = 'bg-success';

                return `
                    <div class="p-3 mb-2 rounded bg-dark border border-secondary border-opacity-25 d-flex justify-content-between align-items-center">
                        <div>
                            <span class="badge ${badgeClass} me-2">${rule.id}</span>
                            <strong class="text-light">${rule.name}</strong>
                            <div class="small text-secondary mt-1">${rule.explanation}</div>
                        </div>
                        <span class="badge bg-secondary">${rule.severity.toUpperCase()}</span>
                    </div>
                `;
            }).join('');
        }
    }

    // 6. Financial Health Metrics
    if (res.financial_metrics) {
        const fin = res.financial_metrics;
        if (document.getElementById('dtiVal')) document.getElementById('dtiVal').textContent = (fin.dti * 100).toFixed(1) + '%';
        if (document.getElementById('emiRatioVal')) document.getElementById('emiRatioVal').textContent = (fin.emi_ratio * 100).toFixed(1) + '%';
        if (document.getElementById('dispIncVal')) document.getElementById('dispIncVal').textContent = formatCurrency(fin.disposable_income);
        if (document.getElementById('savingsRatioVal')) document.getElementById('savingsRatioVal').textContent = (fin.savings_ratio * 100).toFixed(1) + '%';
    }

    // 7. Actionable Recommendations
    const recsList = document.getElementById('recommendationsList');
    if (recsList && res.recommendations) {
        recsList.innerHTML = res.recommendations.map(rec => `
            <li class="mb-2 text-light">
                <i class="fas fa-lightbulb text-warning me-2"></i> ${rec}
            </li>
        `).join('');
    }
}
