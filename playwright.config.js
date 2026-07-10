const { defineConfig, devices } = require("@playwright/test");

module.exports = defineConfig({
  testDir: "./runtime/tests/e2e",
  timeout: 60_000,
  fullyParallel: false,
  workers: 1,
  reporter: "line",
  use: {
    baseURL: "http://127.0.0.1:8011",
    trace: "retain-on-failure",
    screenshot: "only-on-failure",
  },
  projects: [
    {
      name: "mobile-chromium",
      use: { ...devices["Pixel 7"] },
    },
    {
      name: "desktop-chromium",
      use: { ...devices["Desktop Chrome"] },
    },
  ],
  webServer: {
    command: ".venv/bin/python runtime/tests/e2e/server.py",
    url: "http://127.0.0.1:8011/api/health",
    reuseExistingServer: false,
    timeout: 30_000,
  },
});
