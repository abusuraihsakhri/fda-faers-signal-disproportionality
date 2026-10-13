"use strict";
const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");
const html = fs.readFileSync("web/index.html", "utf8");
const match = html.match(/<script[^>]*>([\s\S]*?)<\/script>/);
assert.ok(match, "Inline calculation bundle exists");
const elements = new Map();
function el(id) {
  if (!elements.has(id)) {
    elements.set(id, {
      id, value:"", checked:false, textContent:"", className:"", disabled:false,
      files:[], listeners:{}, children:[],
      addEventListener(name,fn){this.listeners[name]=fn;},
      replaceChildren(){this.children=[];},
      appendChild(child){this.children.push(child);},
    });
  }
  return elements.get(id);
}
["a","b","c","d"].forEach((id,i)=>el(id).value=[30,70,20,880][i]);
const document = {
  getElementById:el,
  createElement(tag){return el("created-"+tag+"-"+Math.random());},
  body:{appendChild(){}},
};
vm.runInNewContext(match[1], {document, Number, Math, Error, setTimeout}, {timeout:2000});
assert.equal(el("prr").textContent, "13.500");
assert.equal(el("ror").textContent, "18.857");
assert.equal(el("chi").textContent, "140.409");
assert.match(el("flag").textContent, /Meets exploratory/);
el("a").value="-1";
el("signal-form").listeners.submit({preventDefault(){}});
assert.match(el("error").textContent, /must be an integer/);
el("reset").listeners.click();
assert.equal(el("prr").textContent,"13.500");
assert.equal(el("error").textContent,"");
console.log("Static browser calculation and input-validation smoke tests passed.");
