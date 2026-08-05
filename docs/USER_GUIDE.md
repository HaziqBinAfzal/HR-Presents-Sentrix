# Sentrix User Guide

## Getting started

Create an account, verify your email when the installation requires verification, sign in, and complete your profile. Your projects, analyses, reports, and settings should be scoped to your account; report any cross-account visibility immediately.

## Dashboard

The dashboard summarizes recent projects, analyses, findings, and activity. Use it as an overview rather than the sole source of truth: open the related project or analysis to review detailed findings.

## New Analysis

Upload a supported Python project or archive, provide the requested project details, and start analysis. Before uploading, remove secrets, private keys, credentials, production databases, and data not required for analysis. Large or deeply nested archives may be rejected by configured safety limits.

The analysis pipeline may perform syntax validation, linting, complexity analysis, formatting checks, security checks, and optional AI-assisted recommendations. A failed optional analyzer should not be interpreted as a clean result; review status and error messages.

## Projects

Projects group uploaded source and related analyses. Open a project to review metadata, previous runs, reports, and available actions. Deleting or replacing a project may affect generated artifacts; follow the confirmation text shown by the installation.

## Results

Results organize findings by analyzer and severity or category. Review the exact file, line, explanation, and suggested remediation. Automated findings can be false positives or incomplete, so validate changes with tests and human review.

## Reports and exports

Reports capture analysis output in a shareable format. Generated files may contain private source paths, excerpts, findings, and account metadata. Download and distribute them only to authorized recipients. Regenerate a report after a new analysis rather than assuming an older report is current.

## Reviews

Reviews provide a structured way to record assessment or feedback on a project or analysis. Use clear, evidence-based notes and avoid including credentials or unrelated personal information.

## History

History shows prior activity or analyses available to your account. Use timestamps and project identifiers to distinguish repeated runs. Retention depends on administrator configuration and storage policy.

## AI recommendations

AI output is advisory. It may be unavailable, incomplete, outdated, or incorrect. Never apply generated fixes blindly. Review diffs, run tests, scan dependencies, and confirm that changes preserve security and intended behavior. Do not upload confidential code to an external provider unless your organization permits it.

## Security findings

Prioritize findings by exploitability, exposure, affected data, and confidence—not severity label alone. Typical categories include unsafe subprocess use, hard-coded secrets, weak cryptography, unsafe deserialization, injection risk, path handling, and insecure temporary-file behavior. Confirm the vulnerable path is reachable before closing or accepting a finding.

## Code quality metrics

Complexity, lint, and formatting metrics are signals. High complexity suggests code that may be harder to test or maintain, but low complexity does not prove correctness. Address metrics alongside tests, architecture, performance, and security requirements.

## Profile and settings

Keep your email and profile details current. Settings may control account preferences, analyzer behavior, mail-related actions, or integrations depending on the deployed version. Save changes and verify the resulting status message.

## Authentication and account management

Use a unique password and a trusted email account. Sign out on shared devices. Password-reset links should be treated as secrets and used promptly. Contact the administrator when verification or reset email does not arrive after checking spam and configuration status.

## Safe usage checklist

- Remove credentials and unnecessary private data before upload.
- Verify every suggested change and run tests.
- Treat reports as sensitive artifacts.
- Re-run analysis after meaningful code changes.
- Report authorization, data exposure, or suspicious behavior privately.
