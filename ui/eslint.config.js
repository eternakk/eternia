// Minimal flat config to declare ignore patterns (replaces deprecated .eslintignore)
export default [
  {
    ignores: [
      'node_modules/**',
      'dist/**',
      'coverage/**',
      'storybook-static/**',
      '.next/**',
      '.cr-out/**',
    ],
  },
];
