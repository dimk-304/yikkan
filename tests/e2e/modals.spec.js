const { test, expect } = require('@playwright/test');

async function loginAsAdmin(page) {
  await page.goto('/login');
  await page.fill('#username', 'admin');
  await page.fill('#password', 'admin123');
  await page.click('#loginBtn');
  await expect(page).toHaveURL(/dashboard/);
}

test.describe('Modal close behavior', () => {
  test('employees edit modal closes with X and Cancelar', async ({ page }) => {
    await loginAsAdmin(page);

    await page.goto('/employees');
    const editButton = page.getByRole('button', { name: /editar/i }).first();
    await expect(editButton).toBeVisible();

    // Open modal and close with top-right X
    await editButton.click();
    const modal = page.locator('#editModal');
    await expect(modal).toBeVisible();
    await modal.locator('button').first().click();
    await expect(modal).toBeHidden();

    // Open modal and close with Cancel button
    await editButton.click();
    await expect(modal).toBeVisible();
    await modal.getByRole('button', { name: /cancelar/i }).click();
    await expect(modal).toBeHidden();
  });

  test('employees management modal closes with X and Cancelar', async ({ page }) => {
    await loginAsAdmin(page);

    await page.goto('/employees/management');
    await page.getByRole('button', { name: /nuevo empleado/i }).click();

    const modal = page.locator('#employeeModal');
    await expect(modal).toBeVisible();

    // Close with top-right X
    await modal.locator('button').first().click();
    await expect(modal).toBeHidden();

    // Re-open and close with Cancel button
    await page.getByRole('button', { name: /nuevo empleado/i }).click();
    await expect(modal).toBeVisible();
    await modal.getByRole('button', { name: /cancelar/i }).click();
    await expect(modal).toBeHidden();
  });
});

