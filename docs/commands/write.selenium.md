# /qakit.write.selenium

Write Selenium WebDriver tests in Python or Java.

## Description

Generates Selenium WebDriver test files for a given user flow. Supports Python (pytest + selenium) and Java (JUnit 5 + TestNG). Applies explicit waits, Page Object Model patterns, and TC-NNN IDs from the test plan.

Selenium is for legacy or cross-platform scenarios. Prefer `/qakit.write.playwright` for new test suites unless `test-policy.md` specifies Selenium as the approved framework.

## Usage

```
/qakit.write.selenium <feature or journey> [--lang python|java]
```

## Arguments

- Feature name or user journey
- `--lang python` (default) or `--lang java`

## Reads from memory

- `.qakit/memory/test-plan.md` — TC-NNN IDs and target paths
- `.qakit/memory/test-policy.md` — browser targets, approved WebDriver version

## Produces

A test file at the path specified in `test-plan.md`:
- Python: `tests/selenium/<journey>_test.py` using `pytest` + `webdriver-manager`
- Java: `src/test/java/<journey>Test.java` using JUnit 5 + `@ExtendWith`

Conventions applied:
- `WebDriverWait` + `ExpectedConditions` — no `time.sleep()` / `Thread.sleep()`
- Page Object Model classes in `pages/` directory
- Browser options passed via environment variable (`BROWSER=chrome|firefox`)

## Example

```
/qakit.write.selenium TC-003 login flow
```

## Related commands

- `/qakit.write.pom` — generate POM classes for each page
- `/qakit.maintain.upgrade` — upgrade Selenium to a newer version
