const { test, expect } = require('@playwright/test');

async function loginAsSuperadmin(page) {
  await page.goto('/login');
  await page.fill('#username', 'admin');
  await page.fill('#password', 'admin123');
  await page.click('#loginBtn');
  await expect(page).toHaveURL(/dashboard/);
}

test('permite editar y persistir horarios de empleado', async ({ page, request }) => {
  await loginAsSuperadmin(page);

  await page.goto('/employees');
  await page.getByPlaceholder('Buscar empleado...').fill('ALI-003');

  const row = page.locator('tr', { hasText: 'ALI-003' }).first();
  await expect(row).toBeVisible();
  await row.getByRole('button', { name: /editar/i }).click();

  const modal = page.locator('#editModal');
  await expect(modal).toBeVisible();

  await modal.locator('#editWorkStart').fill('08:30');
  await modal.locator('#editWorkEnd').fill('17:30');
  await modal.locator('#editLunchStart').fill('14:00');
  await modal.locator('#editLunchEnd').fill('15:00');

  await modal.getByRole('button', { name: /guardar cambios/i }).click();
  await expect(modal).toBeHidden({ timeout: 6000 });

  const employeeId = await row.locator('button[onclick*="editEmployee"]').first().evaluate((btn) => {
    const onclick = btn.getAttribute('onclick') || '';
    const match = onclick.match(/editEmployee\((\d+)\)/);
    return match ? Number(match[1]) : null;
  });
  expect(employeeId).not.toBeNull();

  const response = await request.get(`/api/employees/${employeeId}/`);
  expect(response.ok()).toBeTruthy();
  const payload = await response.json();

  expect(payload.work_start_time).toContain('08:30');
  expect(payload.work_end_time).toContain('17:30');
  expect(payload.lunch_start_time).toContain('14:00');
  expect(payload.lunch_end_time).toContain('15:00');
});
