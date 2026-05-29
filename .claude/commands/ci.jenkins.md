---
command: qakit.ci.jenkins
description: Generate a declarative Jenkinsfile for test execution with parallel stages.
---

# /qakit.ci.jenkins

Generate a declarative Jenkinsfile for the project's test suite.

## Context

**Input:** $ARGUMENTS
*(Optional: Jenkins agent label, Docker registry, or specific stages to include/exclude.)*

Before writing, read:
- `.qakit/memory/test-policy.md` — environment matrix, coverage threshold, CI/CD gates
- `.qakit/memory/test-plan.md` — test types and their expected runtimes

Inspect the project:
- Package manager (npm/pnpm/yarn)
- Whether Docker is used for services (Postgres, Redis)
- Whether Playwright or Cypress is in use
- Whether Python tests exist alongside JS

## What to generate

`Jenkinsfile` — declarative pipeline with parallel stages:

```groovy
pipeline {
  agent { label 'linux-docker' }   // replace with your agent label

  environment {
    NODE_VERSION = '20'
    CI = 'true'
  }

  options {
    timeout(time: 30, unit: 'MINUTES')
    disableConcurrentBuilds()
    buildDiscarder(logRotator(numToKeepStr: '20'))
  }

  stages {
    stage('Install') {
      steps {
        sh 'node --version'
        sh 'npm ci'
      }
    }

    stage('Lint') {
      steps {
        sh 'npm run lint'
      }
    }

    stage('Tests') {
      parallel {
        stage('Unit') {
          steps {
            sh 'npm run test:unit -- --coverage --ci'
          }
          post {
            always {
              junit 'coverage/junit.xml'
              publishHTML(target: [
                reportDir: 'coverage/lcov-report',
                reportFiles: 'index.html',
                reportName: 'Unit Coverage',
              ])
            }
          }
        }

        stage('Integration') {
          steps {
            withCredentials([string(credentialsId: 'DATABASE_URL', variable: 'DATABASE_URL')]) {
              sh 'npm run test:integration'
            }
          }
          post {
            always {
              junit 'test-results/integration.xml'
            }
          }
        }
      }
    }

    stage('E2E') {
      matrix {
        axes {
          axis {
            name 'BROWSER'
            values 'chromium', 'firefox', 'webkit'
          }
        }
        stages {
          stage('Playwright') {
            steps {
              sh "npx playwright install --with-deps ${BROWSER}"
              sh "npx playwright test --project=${BROWSER} --reporter=junit,html"
            }
            post {
              always {
                junit "playwright-results/${BROWSER}.xml"
                archiveArtifacts artifacts: "playwright-report-${BROWSER}/**", allowEmptyArchive: true
              }
            }
          }
        }
      }
    }

    stage('Coverage Gate') {
      steps {
        script {
          def coverage = sh(
            script: "node -e \"const c=require('./coverage/coverage-summary.json'); console.log(c.total.lines.pct)\"",
            returnStdout: true
          ).trim().toDouble()
          def threshold = 80  // from test-policy.md
          if (coverage < threshold) {
            error("Coverage ${coverage}% is below threshold ${threshold}%")
          }
          echo "Coverage: ${coverage}% — PASSED"
        }
      }
    }
  }

  post {
    always {
      cleanWs()
    }
    failure {
      emailext(
        subject: "FAILED: ${env.JOB_NAME} [${env.BUILD_NUMBER}]",
        body: "Build URL: ${env.BUILD_URL}",
        to: '${DEFAULT_RECIPIENTS}'
      )
    }
  }
}
```

## Required adjustments

1. Replace `'linux-docker'` with the actual Jenkins agent label
2. Replace the coverage threshold with the value from `test-policy.md`
3. Replace the browser matrix with P0 browsers from `test-policy.md`
4. Add credential IDs for any secrets (DATABASE_URL, test account tokens)
5. Adjust `npm ci` to the correct package manager command
6. Remove the `emailext` post step if the team uses Slack or another notification channel

## Output

Save as `Jenkinsfile` in the project root.
After writing, print: `Generated Jenkinsfile — replace agent label and credential IDs before committing.`
