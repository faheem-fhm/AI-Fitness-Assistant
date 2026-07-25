/* FitAI Pro - Main Client Interactions & Calculator Engine */

document.addEventListener('DOMContentLoaded', () => {
  initBmiCalculatorModal();
  initToastNotifications();
});

function calculateBmiClient(weight, height) {
  if (!weight || !height || height <= 0) return 0;
  const heightM = height / 100.0;
  return (weight / (heightM * heightM)).toFixed(1);
}

function getBmiCategoryClient(bmi) {
  const val = parseFloat(bmi);
  if (val < 18.5) return { category: 'Underweight', color: '#3b82f6', advice: 'Focus on nutrient-rich surplus calories with protein.' };
  if (val < 25.0) return { category: 'Normal Weight', color: '#10b981', advice: 'Great job! Maintain your balanced active lifestyle.' };
  if (val < 30.0) return { category: 'Overweight', color: '#f59e0b', advice: 'Incorporate consistent workouts and a slight calorie deficit.' };
  return { category: 'Obese', color: '#ef4444', advice: 'Consult a coach for a structured, gradual body weight plan.' };
}

function calculateBmrClient(weight, height, age, gender) {
  const base = (10.0 * weight) + (6.25 * height) - (5.0 * age);
  const bmr = (gender.toLowerCase() === 'female') ? base - 161.0 : base + 5.0;
  return Math.max(bmr, 800.0).toFixed(1);
}

function runBodyMetricsCalculation() {
  const weightInput = document.getElementById('calc-weight');
  const heightInput = document.getElementById('calc-height');
  const ageInput = document.getElementById('calc-age');
  const genderInput = document.getElementById('calc-gender');
  const goalInput = document.getElementById('calc-goal');
  const resDiv = document.getElementById('calc-results');

  if (!resDiv || !weightInput || !heightInput) return;

  const weight = parseFloat(weightInput.value) || 70.0;
  const height = parseFloat(heightInput.value) || 175.0;
  const age = parseInt(ageInput.value) || 25;
  const gender = genderInput ? genderInput.value : 'male';
  const goal = goalInput ? goalInput.value : 'Gain Muscle';

  const clientBmi = calculateBmiClient(weight, height);
  const clientCat = getBmiCategoryClient(clientBmi);
  const clientBmr = calculateBmrClient(weight, height, age, gender);
  const clientTdee = (parseFloat(clientBmr) * 1.55).toFixed(1);
  
  let targetCal = parseFloat(clientTdee);
  if (goal.includes('Lose')) targetCal -= 500;
  else if (goal.includes('Gain')) targetCal += 400;
  targetCal = Math.max(targetCal, 1200).toFixed(1);
  
  const proteinG = (weight * 2.0).toFixed(1);
  const waterL = ((weight * 0.035) + 0.5).toFixed(1);

  resDiv.style.display = 'block';
  resDiv.innerHTML = `
    <div style="padding: 1.25rem; background: rgba(0,0,0,0.5); border-radius: 12px; border: 1px solid var(--primary-glow); box-shadow: 0 4px 20px rgba(0,0,0,0.4);">
      <h4 style="color: ${clientCat.color}; font-size: 1.25rem; margin-bottom: 0.4rem;">
        BMI: ${clientBmi} (${clientCat.category})
      </h4>
      <p style="font-size: 0.9rem; margin-bottom: 0.85rem; color: var(--text-muted);">${clientCat.advice}</p>
      <div style="font-size: 0.88rem; color: #ffffff; display: grid; grid-template-columns: 1fr 1fr; gap: 0.6rem; background: rgba(255,255,255,0.05); padding: 0.85rem; border-radius: 8px;">
        <div>⚡ <b>BMR:</b> ${clientBmr} kcal</div>
        <div>🔥 <b>TDEE:</b> ${clientTdee} kcal</div>
        <div>🎯 <b>Target Cal:</b> ${targetCal} kcal</div>
        <div>🥩 <b>Protein:</b> ${proteinG}g</div>
        <div>💧 <b>Water:</b> ${waterL} L</div>
      </div>
    </div>
  `;
}

function initBmiCalculatorModal() {
  const openBtn = document.getElementById('open-calc-modal');
  const closeBtn = document.getElementById('close-calc-modal');
  const modal = document.getElementById('calc-modal');
  const calcBtn = document.getElementById('calc-submit-btn');

  if (openBtn && modal) {
    openBtn.addEventListener('click', (e) => {
      e.preventDefault();
      modal.classList.add('active');
    });
  }

  if (closeBtn && modal) {
    closeBtn.addEventListener('click', () => {
      modal.classList.remove('active');
    });
  }

  if (modal) {
    modal.addEventListener('click', (e) => {
      if (e.target === modal) {
        modal.classList.remove('active');
      }
    });
  }

  if (calcBtn) {
    calcBtn.addEventListener('click', (e) => {
      e.preventDefault();
      runBodyMetricsCalculation();
    });
  }
}

function initToastNotifications() {
  const alerts = document.querySelectorAll('.alert-auto-dismiss');
  alerts.forEach(alert => {
    setTimeout(() => {
      alert.style.opacity = '0';
      alert.style.transition = 'opacity 0.5s ease';
      setTimeout(() => alert.remove(), 500);
    }, 4000);
  });
}
