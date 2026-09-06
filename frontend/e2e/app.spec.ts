import { test, expect } from "@playwright/test";

/**
 * Disaster Relocation DSS — E2E Test Suite
 * 
 * Prerequisites:
 *   1. Frontend dev server running on http://localhost:3000
 *   2. Backend Flask server running on http://localhost:8000
 * 
 * Run with: npx playwright test
 */

const BASE_URL = "http://localhost:3000";
const API_URL = "http://localhost:8000";

// ─── Home Page ───────────────────────────────────────────────────────

test.describe("Home Page", () => {
  test("should load the dashboard home page with title and quick links", async ({ page }) => {
    await page.goto(BASE_URL);
    
    // Verify page title
    await expect(page).toHaveTitle(/Disaster Relocation DSS/);
    
    // Verify main heading
    await expect(
      page.getByRole("heading", { name: /Command Center Dashboard/ })
    ).toBeVisible();

    // Verify quick links exist
    await expect(page.getByRole("link", { name: "Open Risk Map" })).toBeVisible();
    await expect(page.getByRole("link", { name: "View Action Plan" })).toBeVisible();
  });
});


// ─── Sidebar Navigation ─────────────────────────────────────────────

test.describe("Sidebar Navigation", () => {
  test("should display all navigation links in sidebar", async ({ page }) => {
    await page.goto(BASE_URL);
    
    const expectedLinks = [
      "Dashboard",
      "Risk Map",
      "Data Management",
      "ML Evaluation",
    ];
    
    for (const linkName of expectedLinks) {
      await expect(page.locator("nav").getByRole("link", { name: linkName, exact: true })).toBeVisible();
    }
  });

  test("should navigate to Risk Map page", async ({ page }) => {
    await page.goto(BASE_URL);
    
    await page.locator("nav").getByRole("link", { name: "Risk Map", exact: true }).click();
    await page.waitForURL("**/risk-map");
    
    await expect(
      page.getByRole("heading", { name: /Geospatial Risk Map/ })
    ).toBeVisible();
  });

  test("should navigate to ML Evaluation page", async ({ page }) => {
    await page.goto(BASE_URL);
    
    await page.locator("nav").getByRole("link", { name: "ML Evaluation", exact: true }).click();
    await page.waitForURL("**/ml-evaluation");
    
    await expect(
      page.getByRole("heading", { name: /Machine Learning Evaluation/ })
    ).toBeVisible();
  });

  test("should navigate to Data Management page with Ingestion Wizard and Active Registry", async ({ page }) => {
    await page.goto(`${BASE_URL}/data-management`);
    
    await expect(
      page.getByRole("heading", { name: /Geospatial Data Management/ })
    ).toBeVisible();

    // Verify Ingestion Wizard is present
    await expect(page.getByText("Real Data Ingestion Wizard")).toBeVisible();
    await expect(page.getByText(/Step 1 of 5/)).toBeVisible();

    // Verify Active Datasets Registry table exists
    await expect(page.getByRole("heading", { name: /Active Datasets Registry/ })).toBeVisible();

    // Verify template download buttons exist
    await expect(page.getByRole("button", { name: /Habitations \(CSV\)/ })).toBeVisible();
    await expect(page.getByRole("button", { name: /Habitations \(GeoJSON\)/ })).toBeVisible();
  });

  test("should navigate to Safe Sites page with dynamic suitability and factor matrix", async ({ page }) => {
    await page.goto(`${BASE_URL}/safe-sites`);
    
    await expect(
      page.getByRole("heading", { name: /Safe-Site Suitability/ })
    ).toBeVisible();

    // Verify dynamic origin habitation selector
    await expect(page.getByText("Evaluate Relocation for Affected Habitation")).toBeVisible();

    // Verify recommendation section
    await expect(page.getByRole("heading", { name: /Optimal Relocation Recommendation/ })).toBeVisible();

    // Verify factor matrix table
    await expect(page.getByRole("heading", { name: /Multi-Criteria Factor Matrix/ })).toBeVisible();
  });

  test("should navigate to Carrying Capacity page with planning disclaimer and dynamic site selector", async ({ page }) => {
    await page.goto(`${BASE_URL}/capacity`);
    
    await expect(
      page.getByRole("heading", { name: /Carrying Capacity Analysis/ })
    ).toBeVisible();

    // Verify mandatory planning disclaimer
    await expect(page.getByText("Planning estimate — not legally certified carrying capacity.")).toBeVisible();

    // Verify site selector and planned population inputs
    await expect(page.getByText("Select Candidate Relocation Site")).toBeVisible();
    await expect(page.getByText("Planned Relocated Population")).toBeVisible();

    // Verify infrastructure capacity breakdown and binding bottleneck
    await expect(page.getByRole("heading", { name: /Per-Dimension Infrastructure Capacity/ })).toBeVisible();
    await expect(page.getByRole("heading", { name: /Binding Bottleneck Analysis/ })).toBeVisible();
  });

});

// ─── Engine Testing Page ─────────────────────────────────────────────

test.describe("Engine Testing Page", () => {
  test("should load engine testing UI with all engine sections", async ({ page }) => {
    await page.goto(`${BASE_URL}/engines`);
    
    await expect(
      page.getByRole("heading", { name: /Analysis Engines/ })
    ).toBeVisible();

    // Verify all 4 engine buttons exist
    await expect(page.getByRole("button", { name: /Test Hazard/ })).toBeVisible();
    await expect(page.getByRole("button", { name: /Test Exposure/ })).toBeVisible();
    await expect(page.getByRole("button", { name: /Test Vulnerability/ })).toBeVisible();
    await expect(page.getByRole("button", { name: /Run Full Pipeline/ })).toBeVisible();
  });
});

// ─── Backend API Health ──────────────────────────────────────────────

test.describe("Backend API", () => {
  test("health endpoint should return OK", async ({ request }) => {
    const response = await request.get(`${API_URL}/api/health`);
    
    expect(response.ok()).toBeTruthy();
    
    const body = await response.json();
    expect(body.status).toBe("ok");
    expect(body.app).toBe("Disaster Relocation DSS");
  });

  test("master engine should return scored habitations", async ({ request }) => {
    // Minimal test payload
    const payload = {
      habitations: [
        {
          id: "test-1",
          name: "Test Village",
          longitude: 82.1,
          latitude: 25.05,
          elevation: 80,
          slope: 20,
          population: 1200,
          households: 150,
          geom_geojson: JSON.stringify({ type: "Point", coordinates: [82.1, 25.05] }),
        },
      ],
      hazards: [],
    };

    const response = await request.post(`${API_URL}/api/engines/master`, {
      data: payload,
    });

    expect(response.ok()).toBeTruthy();
    
    const body = await response.json();
    expect(body.results).toBeDefined();
    expect(body.results.length).toBe(1);
    expect(body.results[0].rpi).toBeDefined();
    expect(body.results[0].risk_category).toBeDefined();
  });
});
