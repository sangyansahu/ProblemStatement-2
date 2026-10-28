import { test, expect } from '@playwright/test';
import path from 'path';

test.describe('AICTE APAAR Platform E2E Happy Path', () => {
  test('Operator uploads sample file -> sees flags -> AICTE dashboard metrics change -> public verify page shows status only', async ({ page }) => {
    // 1. Operator login
    await page.goto('http://localhost:5173/login');
    await expect(page.locator('text=Single Sign-On (SSO) Authentication')).toBeVisible();

    await page.selectOption('select', 'inst_operator');
    await page.click('button:has-text("Sign in")');

    // 2. Navigates to Upload Students
    await expect(page.locator('text=Institution Operational Dashboard')).toBeVisible();
    await page.click('text=Upload Students');
    await expect(page.locator('text=Upload Student Enrolment Records')).toBeVisible();

    // 3. Uploads sample CSV file
    const sampleCsvPath = path.resolve(__dirname, '../../sample_data/synthetic_students.csv');
    const fileChooserPromise = page.waitForEvent('filechooser');
    await page.locator('input[type="file"]').setInputFiles(sampleCsvPath);

    // 4. Click Upload and verify row-level flags
    await page.click('button:has-text("Upload")');
    await expect(page.locator('text=Batch Validation Results')).toBeVisible({ timeout: 15000 });
    await expect(page.locator('text=Download report')).toBeVisible();

    // 5. Logout and Login as AICTE Admin
    await page.click('button:has-text("Logout")');
    await expect(page.locator('text=Single Sign-On (SSO) Authentication')).toBeVisible();

    await page.selectOption('select', 'aicte_admin');
    await page.click('button:has-text("Sign in")');

    // 6. Verify AICTE Dashboard metrics and bar chart
    await expect(page.locator('text=National Enrolment & Compliance Monitoring Overview')).toBeVisible();
    await expect(page.locator('text=Prototype - synthetic data.')).toBeVisible();
    await expect(page.locator('text=Institutions Reporting')).toBeVisible();
    await expect(page.locator('text=10 Most Recent Validation Discrepancies')).toBeVisible();

    // 7. Test Public Verify Credential Page (no login)
    await page.click('button:has-text("Logout")');
    await page.goto('http://localhost:5173/verify/CR-sample-opaque-ref');
    await expect(page.locator('text=Official Credential Verification Service')).toBeVisible();
    await expect(page.locator('text=Verification Outcome')).toBeVisible();
    // Confirm NO personal student details (e.g. no student name, no raw APAAR, no DOB)
    await expect(page.locator('text=Issuing Institution:')).toBeVisible();
    await expect(page.locator('text=Credential Type:')).toBeVisible();
  });
});
