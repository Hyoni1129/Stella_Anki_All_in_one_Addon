---
agent: agent
---
@workspace /fix Act as a Senior Software Engineer and Code Quality Expert. I am handing over SonarQube analysis results for this codebase. Your goal is to analyze the provided context, fix the reported issues, and refactor the code to meet high industry standards.

**Context:**
I have identified several code quality issues via SonarQube (Bugs, Vulnerabilities, and Code Smells). I need you to address these in the current scope.

**Instructions:**

1.  **Analyze & Diagnose:**
    *   Scan the files within the current @workspace context.
    *   Identify areas violating standard SonarQube rules (e.g., Null pointer dereferences, resource leaks, cognitive complexity, magic numbers, or duplication).
    *   *Specifically address the following error/rule if applicable:* [PASTE SPECIFIC SONAR ERROR MESSAGE OR RULE ID HERE, e.g., "java:S2095 - Resources should be closed"]

2.  **Refactor & Fix:**
    *   **Security:** Fix any potential security hotspots (SQL injection, XSS, weak cryptography).
    *   **Reliability:** Handle edge cases, null checks, and exception handling to prevent crashes.
    *   **Maintainability:**
        *   Reduce Cognitive Complexity: Break down complex methods into smaller, helper functions.
        *   Remove Code Duplication: Extract repeated logic into shared utilities.
        *   Naming Conventions: Rename variables and methods to be descriptive and consistent.
        *   Remove "Dead Code" or unused variables.

3.  **Refactoring Guidelines:**
    *   Apply **SOLID principles** where applicable.
    *   Ensure the code remains **DRY (Don't Repeat Yourself)**.
    *   Maintain the original **business logic** strictly—do not alter the intended functionality, only the implementation structure.

4.  **Documentation:**
    *   Add or update Javadoc/Docstrings for modified complex methods explaining *why* the change was made.

**Output Format:**
Please present the solution in a step-by-step format:
1.  **Summary of Issues Found:** Briefly list what you detected based on the SonarQube rules.
2.  **Proposed Changes:** The refactored code blocks with comments explaining the specific SonarQube fix.
3.  **Verification:** Explain why this fix resolves the issue without breaking logic.
