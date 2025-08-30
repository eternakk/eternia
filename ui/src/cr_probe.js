// Simple JS file to validate complexity-report behaves as expected on this codebase.
// It is not imported anywhere and will not affect the built bundle.

function simple(a, b) {
  if (a > b) return a - b;
  if (a < b) return b - a;
  return 0;
}

function slightlyComplex(x) {
  // Cyclomatic complexity intentionally small (< 10)
  let s = 0;
  for (let i = 0; i < x; i++) {
    if (i % 15 === 0) s += 3;
    else if (i % 3 === 0) s += 2;
    else if (i % 5 === 0) s += 1;
    else s += 0;
  }
  return s;
}

module.exports = { simple, slightlyComplex };
