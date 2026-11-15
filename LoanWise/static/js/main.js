/* LoanWise Common JS Helpers */

// Helper to format currency (INR)
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-IN', {
        style: 'currency',
        currency: 'INR',
        maximumFractionDigits: 0
    }).format(amount);
}

// Global EMI Loan Calculator handler
document.addEventListener('DOMContentLoaded', () => {
    const calcForm = document.getElementById('globalCalcForm');
    const calcAmountEl = document.getElementById('calcAmount');
    const calcRateEl = document.getElementById('calcRate');
    const calcTermEl = document.getElementById('calcTerm');
    const calcErrorAlert = document.getElementById('calcErrorAlert');
    const calcResultsContainer = document.getElementById('calcResultsContainer');

    function calculateClientSideEMI(loanAmount, interestRate, loanTerm) {
        if (!loanAmount || loanAmount <= 0 || isNaN(loanAmount) ||
            interestRate === undefined || interestRate < 0 || isNaN(interestRate) ||
            !loanTerm || loanTerm <= 0 || isNaN(loanTerm)) {
            return null;
        }

        const monthlyRate = (interestRate / 100.0) / 12.0;
        let emi = 0;
        if (monthlyRate > 0) {
            emi = (loanAmount * monthlyRate * Math.pow(1 + monthlyRate, loanTerm)) / (Math.pow(1 + monthlyRate, loanTerm) - 1);
        } else {
            emi = loanAmount / loanTerm;
        }

        const totalPayment = emi * loanTerm;
        const totalInterest = Math.max(0, totalPayment - loanAmount);

        return {
            monthly_emi: Math.round(emi * 100) / 100,
            total_interest: Math.round(totalInterest * 100) / 100,
            total_payment: Math.round(totalPayment * 100) / 100,
            principal: loanAmount,
            rate: interestRate,
            term_months: loanTerm
        };
    }

    function renderCalculatorResults(data) {
        if (!data || data.monthly_emi === undefined) return;

        if (calcErrorAlert) {
            calcErrorAlert.classList.add('d-none');
            calcErrorAlert.textContent = '';
        }

        const emiEl = document.getElementById('calcEmiResult');
        const interestEl = document.getElementById('calcInterestResult');
        const paymentEl = document.getElementById('calcPaymentResult');

        if (emiEl) emiEl.textContent = formatCurrency(data.monthly_emi);
        if (interestEl) interestEl.textContent = formatCurrency(data.total_interest);
        if (paymentEl) paymentEl.textContent = formatCurrency(data.total_payment);

        // Visual progress bar breakdown
        const total = data.total_payment || (data.principal + data.total_interest);
        if (total > 0) {
            const principalPct = Math.round((data.principal / total) * 100);
            const interestPct = 100 - principalPct;

            const principalBar = document.getElementById('calcPrincipalBar');
            const interestBar = document.getElementById('calcInterestBar');
            const principalPctEl = document.getElementById('calcPrincipalPct');
            const interestPctEl = document.getElementById('calcInterestPct');

            if (principalBar) principalBar.style.width = `${principalPct}%`;
            if (interestBar) interestBar.style.width = `${interestPct}%`;
            if (principalPctEl) principalPctEl.innerHTML = `<i class="fas fa-square me-1"></i>Principal: ${principalPct}%`;
            if (interestPctEl) interestPctEl.innerHTML = `<i class="fas fa-square me-1"></i>Interest: ${interestPct}%`;
        }

        if (calcResultsContainer) {
            calcResultsContainer.classList.remove('d-none');
        }
    }

    function showError(msg) {
        if (calcErrorAlert) {
            calcErrorAlert.textContent = msg;
            calcErrorAlert.classList.remove('d-none');
        }
        if (calcResultsContainer) {
            calcResultsContainer.classList.add('d-none');
        }
    }

    async function executeCalculation() {
        if (!calcAmountEl || !calcRateEl || !calcTermEl) return;

        const loanAmount = parseFloat(calcAmountEl.value);
        const interestRate = parseFloat(calcRateEl.value);
        const loanTerm = parseInt(calcTermEl.value);

        if (isNaN(loanAmount) || loanAmount <= 0) {
            showError('Please enter a valid loan amount greater than ₹0.');
            return;
        }
        if (isNaN(interestRate) || interestRate < 0) {
            showError('Please enter a valid positive interest rate.');
            return;
        }
        if (isNaN(loanTerm) || loanTerm <= 0) {
            showError('Please enter a valid loan tenure in months (min 1).');
            return;
        }

        // 1. Instant local calculation for zero latency
        const localRes = calculateClientSideEMI(loanAmount, interestRate, loanTerm);
        if (localRes) {
            renderCalculatorResults(localRes);
        }

        // 2. Sync with backend API endpoint
        try {
            const response = await fetch('/api/calculator', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    loan_amount: loanAmount,
                    interest_rate: interestRate,
                    loan_term: loanTerm
                })
            });
            const data = await response.json();
            if (response.ok && data.monthly_emi !== undefined) {
                renderCalculatorResults(data);
            } else if (data.error) {
                showError(data.error);
            }
        } catch (err) {
            console.warn('API calculator fetch failed, fallback applied:', err);
        }
    }

    if (calcForm) {
        calcForm.addEventListener('submit', (e) => {
            e.preventDefault();
            executeCalculation();
        });

        [calcAmountEl, calcRateEl, calcTermEl].forEach(input => {
            if (input) {
                input.addEventListener('input', executeCalculation);
                input.addEventListener('change', executeCalculation);
            }
        });
    }

    // Auto calculate on modal trigger
    const modalEl = document.getElementById('emiCalcModal');
    if (modalEl) {
        modalEl.addEventListener('shown.bs.modal', executeCalculation);
    }
});
