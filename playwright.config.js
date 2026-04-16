// @ts-check
const { defineConfig } = require('@playwright/test');

module.exports = defineConfig({
  testDir: './tests/e2e',
  timeout: 30_000,
  retries: 0,
  use: {
    baseURL: 'http://127.0.0.1:8002',
    headless: true,
    viewport: { width: 1366, height: 900 },
  },
  reporter: [['list']],
});

