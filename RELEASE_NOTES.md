# Sentrix v1.0.0 — Final Release Notes

**Final release date:** August 8, 2026  
**Product:** Sentrix by HR-Presents  
**Official source branch:** `main`  
**Official release tag:** `v1.0.0`

## Release status

Sentrix v1.0.0 is the **final official Windows customer release** for this version.

The official customer download is:

```text
Sentrix-v1.0.0-Windows.zip
```

Download it from the GitHub Release page:

https://github.com/HR-Presents/HR-Presents-Sentrix/releases/tag/v1.0.0

The customer package contains a compiled Windows executable at:

```text
Runtime\Sentrix.exe
```

Customers do not need a separate Python installation, Git, Docker, Visual Studio, or GitHub access to run the packaged application.

## Final package identity

The finalized application identity is **Sentrix — Presented by HR-Presents**, using the Sentrix Electric Wing branding throughout the application and packaged static assets.

Official final customer ZIP SHA-256:

```text
224d3c7cc161f5fce787931fc20aaaaacb9776be865e65769728ea09dd1ed4b0
```

The release also includes `Sentrix-v1.0.0-Windows.sha256.txt` for independent verification.

## Customer startup

1. Download `Sentrix-v1.0.0-Windows.zip` from the official release.
2. Extract the ZIP completely.
3. Open the extracted `Sentrix-v1.0.0-Windows` folder.
4. Double-click `Start Sentrix.bat`.
5. Keep the Sentrix console window open while using the application.
6. Sentrix opens locally at `http://127.0.0.1:5000`.

User data is stored separately under:

```text
%LOCALAPPDATA%\Sentrix
```

## Included product areas

- Registration, login, logout, sessions, password hashing, profiles, and settings
- Signed expiring password-reset links with SMTP delivery
- Python file and ZIP-project upload
- Secure ZIP extraction and resource controls
- Syntax, Pylint, Bandit, Radon, Black, formatting, and structural analysis
- Dashboard, project history, analysis history, and reviews
- Owner-scoped results and report access
- Professional branded HTML reports
- Project-specific standards and security-control interpretation
- Persistent light and dark appearance modes
- Compiled source-free Windows customer distribution

## Professional reporting

Reports may include:

- Executive summary and project health
- Scope and methodology
- Quality, security, and complexity findings
- Scanner evidence, rules, file names, and line numbers when available
- Root cause and exploitation context
- Business and technical impact
- Severity interpretation
- Secure implementation and remediation guidance
- Prevention and verification steps
- Standards and compliance interpretation
- Security-control analysis

Standards guidance may reference OWASP Top 10, OWASP ASVS, CWE Top 25, MITRE CAPEC and ATT&CK where applicable, NIST SSDF, NIST CSF, NIST SP 800-53, CIS, SANS, CERT, PCI DSS, ISO/IEC 27001, ISO/IEC 27002, SOC 2, GDPR, and HIPAA.

Mappings are evidence-aware. When retained scanner output does not establish a project-specific relationship or location, Sentrix reports insufficient evidence instead of creating unsupported claims. Standards mapping is guidance and does not constitute certification or legal advice.

## Security protections

- Password hashing and authenticated sessions
- CSRF-protected browser forms
- Signed password-reset tokens
- Generic reset responses to reduce account enumeration
- User ownership checks for projects, analyses, and reports
- Report-content escaping
- Environment-based secrets and production configuration
- Secure-cookie and security-header options
- ZIP traversal, absolute-path, symlink, nested-archive, duplicate-path, member-count, expanded-size, per-member-size, and compression-ratio controls

Static analysis is an aid to secure development and does not prove that software is vulnerability-free. Findings require developer review and risk validation.

## Windows customer package

The official compiled package is built with Nuitka and structured as:

```text
Sentrix-v1.0.0-Windows/
├── Start Sentrix.bat
├── README.txt
├── LICENSE.txt
└── Runtime/
    ├── Sentrix.exe
    └── compiled/runtime dependencies
```

The customer distribution intentionally excludes readable Sentrix project source files and development files such as project `.py` source, tests, `.git`, `.github`, and `requirements.txt`.

## Validation

The final compiled Windows workflow performs source validation, unit tests, Nuitka compilation, packaged analyzer self-tests, compiled web-startup checks, customer-package validation, ZIP creation, SHA-256 generation, workflow-artifact upload, and GitHub Release publishing.

## Developer source

The full source code, documentation, build workflows, tests, templates, static assets, analyzer modules, and development configuration remain available in this repository.

The official source-of-truth branch is now:

```text
main
```

Older RC1 and `production/sentrix-permanent` references are historical and are not the final v1.0.0 source-of-truth location.

## Final release

Sentrix v1.0.0 is published as a stable, non-prerelease GitHub Release under:

```text
v1.0.0
```

For customers, use only **`Sentrix-v1.0.0-Windows.zip`** from the release Assets section. GitHub's automatically generated source archives are intended for source access, not as the Windows customer application.

Presented by **HR-Presents**.
