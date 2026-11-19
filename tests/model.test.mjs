import test from 'node:test';import assert from 'node:assert/strict';import {filterGroups,counts,percent}from'../web/model.mjs';
const r=[{from:1,to:2,n:9,reached:8,us:1,ca:2,unmatched:5},{from:2,to:1,n:3,reached:0,us:0,ca:0,unmatched:0}];
test('direction and independent denominators',()=>{assert.deepEqual(counts(r),{n:12,reached:8,us:1});assert.equal(filterGroups(r,'2','1','us').length,0);assert.equal(percent(1,8),'12.5%');assert.equal(percent(0,0),'—')});
