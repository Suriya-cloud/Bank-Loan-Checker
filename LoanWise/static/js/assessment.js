/* Multi-Step Assessment Form JS & Demo Profile Presets */

let currentStep = 1;

const demoProfiles = {
    strong: {
        applicant_name: "Aarav Sharma (Strong)",
        age: 30,
        gender: "Male",
        marital_status: "Married",
        dependents: 1,
        education: "Graduate",
        employment_status: "Salaried",
        income: 80000,
        monthly_expenses: 25000,
        savings: 300000,
        existing_emi: 10000,
        debt: 20000,
        credit_score: 790,
        previous_default: 0,
        loan_amount: 300000,
        loan_term: 36,
        loan_purpose: "Personal Loan"
    },
    moderate: {
        applicant_name: "Priya Patel (Moderate)",
        age: 35,
        gender: "Female",
        marital_status: "Married",
        dependents: 2,
        education: "Graduate",
        employment_status: "Salaried",
        income: 45000,
        monthly_expenses: 20000,
        savings: 80000,
        existing_emi: 12000,
        debt: 80000,
        credit_score: 690,
        previous_default: 0,
        loan_amount: 400000,
        loan_term: 48,
        loan_purpose: "Home Improvement"
    },
    high_risk: {
        applicant_name: "Rohan Verma (High Risk)",
        age: 42,
        gender: "Male",
        marital_status: "Single",
        dependents: 3,
        education: "Not Graduate",
        employment_status: "Unemployed",
        income: 22000,
        monthly_expenses: 18000,
        savings: 15000,
        existing_emi: 10000,
        debt: 150000,
        credit_score: 610,
        previous_default: 1,
        loan_amount: 500000,
        loan_term: 60,
        loan_purpose: "Debt Consolidation"
    },
    self_employed: {
        applicant_name: "Vikram Malhotra (Self-Employed)",
        age: 38,
        gender: "Male",
        marital_status: "Married",
        dependents: 2,
        education: "Graduate",
        employment_status: "Self-Employed",
        income: 95000,
        monthly_expenses: 35000,
        savings: 450000,
        existing_emi: 15000,
        debt: 100000,
        credit_score: 740,
        previous_default: 0,
        loan_amount: 600000,
        loan_term: 36,
        loan_purpose: "Business Expansion"
    },
    young_prof: {
        applicant_name: "Ananya Roy (Young Professional)",
        age: 24,
        gender: "Female",
        marital_status: "Single",
        dependents: 0,
        education: "Graduate",
        employment_status: "Salaried",
        income: 35000,
        monthly_expenses: 16000,
        savings: 60000,
        existing_emi: 3000,
        debt: 10000,
        credit_score: 675,
        previous_default: 0,
        loan_amount: 150000,
        loan_term: 24,
        loan_purpose: "Higher Education"
    }
};

function fillDemoProfile(key) {
    const profile = demoProfiles[key];
    if (!profile) return;

    for (const [field, value] of Object.entries(profile)) {
        const el = document.getElementById(field);
        if (el) {
            el.value = value;
        }
    }
}

function showStep(step) {
    document.querySelectorAll('.wizard-step-content').forEach(el => el.classList.add('d-none'));
    document.getElementById(`stepContent${step}`).classList.remove('d-none');

    document.querySelectorAll('.wizard-step').forEach((el, index) => {
        const stepNum = index + 1;
        el.classList.remove('active', 'completed');
        if (stepNum < step) {
            el.classList.add('completed');
        } else if (stepNum === step) {
            el.classList.add('active');
        }
    });

    currentStep = step;
    window.scrollTo({ top: 150, behavior: 'smooth' });
}

function nextStep(targetStep) {
    // Validate current step
    if (targetStep > currentStep) {
        const currentContainer = document.getElementById(`stepContent${currentStep}`);
        const inputs = currentContainer.querySelectorAll('input, select');
        let valid = true;

        inputs.forEach(input => {
            if (!input.checkValidity()) {
                input.reportValidity();
                valid = false;
            }
        });

        if (!valid) return;
    }
    showStep(targetStep);
}

function prevStep(targetStep) {
    showStep(targetStep);
}

document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('assessmentForm');
    if (form) {
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            // Collect form data
            const formData = new FormData(form);
            const data = {};
            formData.forEach((value, key) => { data[key] = value; });

            // Redirect to animated analysis page and store data in sessionStorage
            sessionStorage.setItem('loanwise_assessment_input', JSON.stringify(data));
            window.location.href = '/analyzing';
        });
    }
});
