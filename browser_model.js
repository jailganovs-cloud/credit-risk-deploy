// This executes the exported trained tree. It does not train a replacement model.
export const STATUS = ['PAY_0', 'PAY_2', 'PAY_3', 'PAY_4', 'PAY_5', 'PAY_6'];
export const PAYMENTS = Array.from({length: 6}, (_, i) => `PAY_AMT${i + 1}`);

export function validateRecord(record, model) {
  if (!record || typeof record !== 'object' || Array.isArray(record)) throw new Error('Enter an account record.');
  const keys = Object.keys(record);
  if (keys.length !== model.features.length || keys.some(k => !model.features.includes(k))) throw new Error('All 23 model fields are required, with no extra fields.');
  const values = {};
  for (const name of model.features) {
    const raw = record[name];
    if (!['number', 'string'].includes(typeof raw) || (typeof raw === 'string' && !raw.trim())) throw new Error(`${name} must be a finite number.`);
    const value = Number(raw);
    if (!Number.isFinite(value) || !Number.isFinite(Math.fround(value))) throw new Error(`${name} must be a finite number in the model's supported range.`);
    values[name] = value;
  }
  const codes = {SEX: [1, 2], EDUCATION: [0, 1, 2, 3, 4, 5, 6], MARRIAGE: [0, 1, 2, 3]};
  for (const name of STATUS) codes[name] = Array.from({length: 12}, (_, i) => i - 2);
  for (const [name, allowed] of Object.entries(codes)) if (!allowed.includes(values[name])) throw new Error(`${name} has an unsupported category code.`);
  if (values.LIMIT_BAL <= 0) throw new Error('Credit limit must be greater than zero.');
  if (!Number.isInteger(values.AGE) || values.AGE < 18 || values.AGE > 100) throw new Error('Age must be an integer from 18 to 100 for this demo.');
  if (PAYMENTS.some(name => values[name] < 0)) throw new Error('Previous payment amounts cannot be negative.');
  return values;
}

export function predict(record, model) {
  const values = validateRecord(record, model);
  for (const [name, mapping] of Object.entries(model.cleaning)) values[name] = mapping[String(values[name])] ?? values[name];
  const vector = [];
  model.categorical.forEach((name, i) => model.categories[i].forEach(category => vector.push(values[name] === category ? 1 : 0)));
  for (const name of model.numeric) vector.push(Math.fround(values[name]));
  const tree = model.tree;
  let node = 0;
  for (let step = 0; step <= tree.left.length; step++) {
    if (tree.left[node] === -1) {
      const score = tree.score[node];
      return {model_score: score, threshold: model.threshold,
        review_flag: score >= model.threshold ? 'Flagged for review' : 'Not flagged for review',
        score_type: 'Uncalibrated class-weighted decision-tree score'};
    }
    const value = vector[tree.feature[node]];
    if (value === undefined) throw new Error('Model feature mapping is invalid.');
    node = value <= tree.threshold[node] ? tree.left[node] : tree.right[node];
  }
  throw new Error('Model tree is invalid.');
}
