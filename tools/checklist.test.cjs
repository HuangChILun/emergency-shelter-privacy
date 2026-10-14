const test = require('node:test');
const assert = require('node:assert/strict');
const { readState, saveState } = require('../assets/checklist.js');

test('corrupt, unavailable and obsolete browser storage cannot break a checklist', () => {
  for (const raw of ['{bad', 'null', JSON.stringify({version: 0, checked: ['water']}), JSON.stringify({version: 1, checked: 'water'})]) {
    assert.deepEqual(readState({getItem: () => raw}, 'kit', ['water']), []);
  }
  assert.deepEqual(readState(null, 'kit', ['water']), []);
  assert.equal(saveState({setItem: () => { throw new Error('quota'); }}, 'kit', ['water']), false);
});

test('saved progress remains scoped to the current page and known item IDs', () => {
  const data = new Map();
  const storage = {getItem: key => data.get(key) ?? null, setItem: (key, value) => data.set(key, value)};
  assert.equal(saveState(storage, 'kit', ['water', 'retired-item']), true);
  assert.deepEqual(readState(storage, 'kit', ['water', 'light']), ['water']);
  assert.deepEqual(readState(storage, 'pets', ['water']), []);
  saveState(storage, 'pets', ['carrier']);
  saveState(storage, 'kit', []);
  assert.deepEqual(readState(storage, 'pets', ['carrier']), ['carrier']);
});
