const path = require("node:path");
const { test, expect } = require("@playwright/test");

const MULTIPLE_PURCHASE =
  "Compre dos bolsas de iniciador a 110 mil cada una, " +
  "una bolsa de maiz a 90 mil y 3 kg de vitaminas a 25000";

test("revisa y corrige una compra con varios productos", async ({ page }, testInfo) => {
  await page.goto("/");
  await page.locator("#message").fill(MULTIPLE_PURCHASE);
  await page.getByRole("button", { name: "Analizar y guardar" }).click();

  const result = page.locator("#capture-result");
  await expect(result).toContainText("Entrada guardada");
  await expect(result.locator(".detected-row")).toHaveCount(3);
  await expect(result).toContainText("385.000");

  await page.locator('.nav-button[data-target="inbox"]').click();
  const informationTab = page.locator('#inbox-filters [data-status="needs_information"]');
  expect(await informationTab.evaluate((element) => element.scrollWidth <= element.clientWidth)).toBe(true);
  await page.locator("#inbox-list .entry-card").first().click();

  const sheet = page.locator("#entry-sheet");
  const correctionModal = page.locator("#correction-modal");
  await expect(sheet).toBeVisible();
  await expect(sheet).toContainText("Entrada original");
  await expect(sheet).toContainText("Interpretación");
  await expect(sheet.locator(".purchase-read-item")).toHaveCount(3);
  await expect(sheet.locator(".section-editor")).toHaveCount(0);

  if (process.env.E2E_SCREENSHOT_PATH) {
    await expect(page.locator("#toast")).toBeHidden({ timeout: 5_000 });
    const extension = path.extname(process.env.E2E_SCREENSHOT_PATH);
    const base = process.env.E2E_SCREENSHOT_PATH.slice(0, -extension.length);
    await page.screenshot({ path: `${base}-overview-${testInfo.project.name}${extension}`, fullPage: true });
  }

  await sheet.getByRole("button", { name: "Confirmar datos" }).click();
  await expect(page.locator("#toast")).toContainText("Faltan datos obligatorios");
  await expect(sheet.locator('[data-field-path="fecha_compra"]')).toHaveClass(/is-invalid/);
  await expect(sheet.locator('[data-field-path="proveedor"]')).toHaveClass(/is-invalid/);

  await sheet.getByTitle("Editar datos generales").click();
  await expect(correctionModal).toBeVisible();
  await expect(page.locator("#correction-backdrop")).toBeVisible();
  await expect(page.locator("#toast")).toBeHidden();
  await expect(sheet).toBeVisible();
  await correctionModal.locator("#purchase-fecha_compra").fill("2026-06-20");
  await correctionModal.locator("#purchase-proveedor").fill("Proveedor de prueba");
  await correctionModal.getByRole("button", { name: "Agregar descuento" }).click();
  await correctionModal.locator("#purchase-discount-value").fill("5000");
  await correctionModal.locator("#correction-reason").selectOption("new_information");
  await expect(correctionModal.locator("#correction-reason-help")).toContainText("no estaba mencionado");

  if (process.env.E2E_SCREENSHOT_PATH) {
    const extension = path.extname(process.env.E2E_SCREENSHOT_PATH);
    const base = process.env.E2E_SCREENSHOT_PATH.slice(0, -extension.length);
    await page.screenshot({ path: `${base}-edit-modal-${testInfo.project.name}${extension}`, fullPage: true });
  }

  await correctionModal.getByRole("button", { name: "Guardar corrección" }).click();

  await expect(page.locator("#toast")).toContainText("Corrección guardada");
  await expect(correctionModal).toBeHidden();
  await expect(sheet.locator('[data-field-path="proveedor"]')).toContainText("Proveedor de prueba");
  await expect(sheet.locator('[data-field-path="proveedor"]')).toContainText("Agregado");
  await expect(sheet.locator('[data-field-path="descuento"]')).toContainText("5.000");
  await expect(sheet.locator(".section-editor")).toHaveCount(0);

  await sheet.getByTitle("Editar productos").click();
  await expect(correctionModal).toBeVisible();
  await expect(correctionModal.locator(".purchase-item")).toHaveCount(3);
  await correctionModal.getByRole("button", { name: "Agregar" }).click();
  await expect(correctionModal.locator(".purchase-item")).toHaveCount(4);
  await correctionModal.locator(".purchase-item").last().getByTitle("Quitar producto").click();
  await expect(correctionModal.locator(".purchase-item")).toHaveCount(3);
  await correctionModal.locator(".purchase-item").last().locator('[data-item-field="cantidad"]').fill("4");
  await correctionModal.locator("#correction-reason").selectOption("system_error");
  await correctionModal.getByRole("button", { name: "Guardar corrección" }).click();

  await expect(page.locator("#toast")).toContainText("Corrección guardada");
  await expect(correctionModal).toBeHidden();
  await expect(sheet.locator(".purchase-read-item")).toHaveCount(3);
  await expect(sheet.locator(".purchase-read-item").last()).toContainText("4 kg");

  if (process.env.E2E_SCREENSHOT_PATH) {
    await expect(page.locator("#toast")).toBeHidden({ timeout: 5_000 });
    await sheet.locator(".purchase-review").evaluate((element) => element.scrollIntoView({ block: "start" }));
    const extension = path.extname(process.env.E2E_SCREENSHOT_PATH);
    const base = process.env.E2E_SCREENSHOT_PATH.slice(0, -extension.length);
    await page.screenshot({ path: `${base}-purchase-${testInfo.project.name}${extension}`, fullPage: true });
  }

  await sheet.getByRole("button", { name: "Confirmar datos" }).click();
  await expect(sheet).toBeHidden();
  await expect(page.locator("#toast")).toContainText("Entrada validada");
  await expect(page.locator("#inbox-list .entry-card").first()).toContainText("Validada");

  await page.locator("#inbox-list .entry-card").first().click();
  await expect(sheet).toBeVisible();
  await expect(sheet).toContainText("Esta interpretación ya fue validada");
  await expect(sheet.getByRole("button", { name: "Confirmar datos" })).toHaveCount(0);
  await sheet.getByRole("button", { name: "Descartar entrada" }).click();
  await expect(sheet.locator("#review-decision-panel")).toBeVisible();
  await sheet.getByRole("button", { name: "Descartar", exact: true }).click();
  await expect(sheet).toBeHidden();
  await expect(page.locator("#inbox-list .entry-card").first()).toContainText("Descartada");
});
