---
command: qakit.write.selenium
description: Write Selenium WebDriver tests (Python or Java) for a user flow.
---

# /qakit.write.selenium

Write Selenium WebDriver tests for the specified user flow.

## Context

**Input:** $ARGUMENTS
*(Provide the user flow and language preference, e.g. "checkout flow — Python" or "login flow — Java/TestNG".)*

Before writing, read:
- `.qakit/memory/test-plan.md` — TC-NNN IDs, target file paths, and environment matrix
- `.qakit/memory/test-policy.md` — approved Selenium version, browser drivers, and flakiness policy
- `.qakit/memory/qa-strategy.md` — acceptance criteria and edge cases for this flow

Detect the project language from `$ARGUMENTS` or from existing test files. Default to Python if ambiguous.

## Python conventions (pytest + selenium)

**Setup**
```python
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

@pytest.fixture
def driver():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    d = webdriver.Chrome(options=options)
    d.implicitly_wait(0)  # use explicit waits only
    yield d
    d.quit()
```

**Locator strategy** — prefer in this order:
1. `By.ID` for unique form elements
2. `By.XPATH, "//button[@aria-label='Submit']"` — accessible name
3. `By.CSS_SELECTOR, "[data-testid='submit']"` — stable test ID
4. Never use positional CSS like `div:nth-child(3)`

**Explicit waits — always**
```python
wait = WebDriverWait(driver, 10)
element = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[text()='Continue']")))
```
Never use `time.sleep()`.

**Test structure**
```python
class TestCheckoutFlow:
    def test_tc_001_happy_path(self, driver):
        """TC-001 User completes checkout with valid card."""
        # Arrange
        driver.get(f"{BASE_URL}/checkout")
        # Act
        # Assert
        assert "Order confirmed" in driver.title
```

## Java conventions (JUnit 5 + Selenium)

**Setup**
```java
@ExtendWith(SeleniumExtension.class)
class CheckoutTest {
    private WebDriver driver;

    @BeforeEach
    void setUp() {
        ChromeOptions options = new ChromeOptions();
        options.addArguments("--headless");
        driver = new ChromeDriver(options);
        driver.manage().timeouts().implicitlyWait(Duration.ZERO);
    }

    @AfterEach
    void tearDown() { driver.quit(); }
}
```

Use `WebDriverWait` with `ExpectedConditions` — no `Thread.sleep()`.

## What to write

For the flow in `$ARGUMENTS`:
1. **Happy path test** — TC-NNN, complete flow from start to success state
2. **Edge case tests** — boundary inputs, optional fields
3. **Negative path test** — invalid input, error message verification

Include a Page Object Model class for the page(s) touched (or reference the existing POM if one exists at `tests/pages/`).

## Output

Python: `tests/e2e/<feature>/<flow>_test.py`
Java: `src/test/java/<package>/<Flow>Test.java`

After writing, print: `Added N tests (TC-NNN through TC-NNN) in <path>`
