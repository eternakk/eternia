"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const vitest_1 = require("vitest");
// Minimal smoke test to ensure Vitest discovers tests and coverage can run.
(0, vitest_1.describe)('smoke', () => {
    (0, vitest_1.it)('runs a basic assertion', () => {
        (0, vitest_1.expect)(1 + 1).toBe(2);
    });
});
