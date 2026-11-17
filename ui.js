import {predict, STATUS} from './browser_model.js';

const account = document.querySelector('#account');
const months = document.querySelector('#months');
function numeric(name, label, value, hint = '') {
  return `<label>${label}<input id="${name}" name="${name}" type="number" step="any" value="${value}" required>${hint ? `<span class="hint">${hint}</span>` : ''}</label>`;
}
function select(name, label, options, selected) {
  return `<label>${label}<select id="${name}" name="${name}">${options.map(([value, text]) => `<option value="${value}" ${value === selected ? 'selected' : ''}>${text}</option>`).join('')}</select></label>`;
}
account.innerHTML = numeric('LIMIT_BAL', 'Credit limit (NT$)', 200000) +
  numeric('AGE', 'Age in years', 35) +
  select('SEX', 'Sex as recorded in dataset', [[1,'Male (code 1)'],[2,'Female (code 2)']],2) +
  select('EDUCATION','Education',[[1,'Graduate school'],[2,'University'],[3,'High school'],[4,'Other']],2) +
  select('MARRIAGE','Marital status',[[1,'Married'],[2,'Single'],[3,'Other']],1);
const names = ['September','August','July','June','May','April'];
const statuses = [[-2,'-2 (observed source code)'],[-1,'-1 (paid duly)'],[0,'0 (observed source code)'],...Array.from({length:9},(_,i)=>[i+1,i === 8 ? '9 or more months delay' : `${i+1} month delay`])];
months.innerHTML = names.map((month,i) => `<details ${i < 2 ? 'open' : ''}><summary>Month ${i+1} · ${month}</summary><div class="fields">${select(STATUS[i], STATUS[i]+' repayment status', statuses, 0)}${numeric('BILL_AMT'+(i+1),'Statement balance (NT$)',50000-i*5000,'BILL_AMT'+(i+1)+' · negative balances are allowed')}${numeric('PAY_AMT'+(i+1),'Previous payment (NT$)',5000,'PAY_AMT'+(i+1))}</div></details>`).join('');
let model, examples;
const error = document.querySelector('#error');
const button = document.querySelector('#predict');
function fill(record) {
  for (const [name,value] of Object.entries(record)) document.getElementById(name).value = value;
  error.textContent = '';
  document.querySelector('#score').textContent = '—';
  document.querySelector('#flag').textContent = 'Select Estimate model score';
}
document.querySelector('#example-regular').onclick = () => {if(examples)fill(examples[0].record);};
document.querySelector('#example-delayed').onclick = () => {if(examples)fill(examples[1].record);};
document.querySelector('#form').onsubmit = event => {
  event.preventDefault(); error.textContent = '';
  try {
    const record = Object.fromEntries(model.features.map(name => [name,document.getElementById(name).value]));
    const result = predict(record,model);
    document.querySelector('#score').textContent = result.model_score.toFixed(4);
    document.querySelector('#flag').textContent = result.review_flag;
  } catch(e) {
    error.textContent = e.message;
    document.querySelector('#score').textContent = '—';
    document.querySelector('#flag').textContent = 'Check the highlighted message';
  }
};
try {
  const responses = await Promise.all([fetch('./model.json',{cache:'no-store'}),fetch('./examples.json')]);
  if(responses.some(response=>!response.ok))throw new Error('The model files could not be loaded. Refresh the page after the deployment finishes.');
  [model,examples] = await Promise.all(responses.map(response=>response.json()));
  button.disabled = false;button.textContent = 'Estimate model score';
}catch(e){error.textContent=e.message;button.textContent='Model unavailable';}
