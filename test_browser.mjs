import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {test} from 'node:test';
import {predict} from './browser_model.js';

const model = JSON.parse(readFileSync(new URL('./model.json', import.meta.url)));
const fixtures = JSON.parse(readFileSync(new URL('./browser_fixtures.json', import.meta.url)));
const record = fixtures[0].record;

test('browser predictions match all Python synthetic and boundary references', () => {
  for (const f of fixtures) assert.ok(Math.abs(predict(f.record, model).model_score - f.score) < 1e-12);
});
test('field ordering is explicit', () => {
  assert.deepEqual(predict(record, model), predict(Object.fromEntries(Object.entries(record).reverse()), model));
});
test('legacy category codes use the same mapping as training', () => {
  assert.deepEqual(predict({...record, EDUCATION: 5, MARRIAGE: 0}, model), predict({...record, EDUCATION: 4, MARRIAGE: 3}, model));
});
test('invalid input is rejected', () => {
  for (const [name, value] of [['AGE', 17], ['AGE', 35.5], ['PAY_0', 10], ['SEX', 3], ['LIMIT_BAL', -1], ['PAY_AMT1', -1], ['BILL_AMT1', NaN], ['AGE', null], ['AGE', true], ['PAY_AMT1', Infinity], ['AGE', ''], ['BILL_AMT1', []], ['BILL_AMT1', 1e100]]) {
    assert.throws(() => predict({...record, [name]: value}, model));
  }
});
test('missing and extra fields are rejected', () => {
  const missing = {...record}; delete missing.AGE;
  assert.throws(() => predict(missing, model));
  assert.throws(() => predict({...record, ID: 1}, model));
});
test('negative statement balances remain valid', () => {
  const result = predict({...record, BILL_AMT1: -100}, model);
  assert.ok(result.model_score >= 0 && result.model_score <= 1);
});
test('review labels agree with the recorded threshold', () => {
  for (const f of fixtures) {
    const r = predict(f.record, model);
    assert.equal(r.review_flag, r.model_score >= r.threshold ? 'Flagged for review' : 'Not flagged for review');
  }
});
