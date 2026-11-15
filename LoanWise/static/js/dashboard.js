/* LoanWise Dashboard Analytics & Chart.js Visualizations */

document.addEventListener('DOMContentLoaded', async () => {
    try {
        const statsRes = await fetch('/api/dashboard-stats');
        const stats = await statsRes.json();
        
        const historyRes = await fetch('/api/history');
        const historyData = await historyRes.json();

        // Update summary KPI counters
        document.getElementById('totalAssessmentsVal').textContent = stats.total_assessments || 0;
        document.getElementById('eligibleCountVal').textContent = stats.eligible || 0;
        document.getElementById('conditionalCountVal').textContent = stats.conditionally_eligible || 0;
        document.getElementById('notEligibleCountVal').textContent = stats.not_eligible || 0;
        document.getElementById('highRiskCountVal').textContent = stats.high_risk || 0;
        document.getElementById('avgScoreVal').textContent = stats.average_score || 0;
        document.getElementById('avgCreditVal').textContent = stats.average_credit_score || 0;

        // Render Dashboard Charts
        renderEligibilityChart(stats);
        renderRiskChart(stats);
        renderHistoryTable(historyData.history || []);
    } catch (err) {
        console.error('Error loading dashboard analytics:', err);
    }
});

function renderEligibilityChart(stats) {
    const ctx = document.getElementById('eligibilityChart');
    if (!ctx) return;

    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Eligible', 'Conditionally Eligible', 'Not Eligible'],
            datasets: [{
                data: [stats.eligible || 0, stats.conditionally_eligible || 0, stats.not_eligible || 0],
                backgroundColor: ['#10b981', '#f59e0b', '#ef4444'],
                borderWidth: 2,
                borderColor: '#1e293b'
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { position: 'bottom', labels: { color: '#94a3b8' } }
            }
        }
    });
}

function renderRiskChart(stats) {
    const ctx = document.getElementById('riskDistributionChart');
    if (!ctx) return;

    new Chart(ctx, {
        type: 'pie',
        data: {
            labels: ['Low Risk', 'Medium Risk', 'High Risk'],
            datasets: [{
                data: [stats.eligible || 0, stats.conditionally_eligible || 0, stats.high_risk || 0],
                backgroundColor: ['rgba(16, 185, 129, 0.8)', 'rgba(245, 158, 11, 0.8)', 'rgba(239, 68, 68, 0.8)'],
                borderWidth: 2,
                borderColor: '#1e293b'
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { position: 'bottom', labels: { color: '#94a3b8' } }
            }
        }
    });
}

function renderHistoryTable(records) {
    const tbody = document.getElementById('recentAssessmentsTbody');
    if (!tbody) return;

    if (records.length === 0) {
        tbody.innerHTML = `<tr><td colspan="7" class="text-center text-muted py-4">No assessments recorded in database yet.</td></tr>`;
        return;
    }

    tbody.innerHTML = records.slice(0, 10).map(rec => {
        let badge = 'bg-success';
        if (rec.decision === 'CONDITIONALLY_ELIGIBLE') badge = 'bg-warning text-dark';
        else if (rec.decision === 'NOT_ELIGIBLE') badge = 'bg-danger';

        return `
            <tr>
                <td>#${rec.id}</td>
                <td>${rec.applicant_name}</td>
                <td>${formatCurrency(rec.loan_amount)}</td>
                <td>${rec.credit_score}</td>
                <td><strong>${rec.final_score}</strong>/100</td>
                <td><span class="badge ${badge}">${rec.decision.replace('_', ' ')}</span></td>
                <td>${new Date(rec.created_at).toLocaleDateString()}</td>
            </tr>
        `;
    }).join('');
}
