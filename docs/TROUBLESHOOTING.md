# Sentrix Troubleshooting

## Application does not start

Confirm the virtual environment is active and that `which python`/`where python` and `pip` point to the same environment. Reinstall dependencies with `python -m pip install -r requirements.txt`. Read the first traceback, not only the final line.

## Import error despite an installed package

Run:

```bash
python -m pip show PACKAGE_NAME
python -c "import PACKAGE_NAME; print(PACKAGE_NAME.__file__)"
```

A package installed under another interpreter will not be visible. Also verify the import name; package and module names sometimes differ.

## IndentationError or SyntaxError

Open the exact file and line from the traceback and inspect the preceding block. Python reports where parsing failed, which may be just after the real mistake. Use consistent four-space indentation and run `python -m compileall .` on a clean working tree.

## Database errors

Confirm `DATABASE_URL`, database availability, filesystem permissions for SQLite, and migration state. Back up data before modifying schema. Do not delete the database to hide a migration problem in a production-like environment.

## Registration or login fails

Check form validation messages, session secret stability, database writes, password hashing, user activation/verification state, and server logs. Changing `SECRET_KEY` between restarts invalidates signed sessions and tokens.

## Verification or reset email is missing

Verify SMTP host, port, TLS mode, username, application password, sender policy, provider security blocks, and spam folder. Avoid printing passwords or reset links in logs. Test with a controlled non-production recipient.

## Upload rejected

Check configured maximum request size, allowed type, archive integrity, file count, expanded size, nesting, and unsafe paths. A `413` response means the reverse proxy or Flask limit may have rejected the request before route handling.

## Analysis stalls or times out

Inspect project size, analyzer subprocesses, worker timeout, CPU/memory pressure, and external AI latency. Run analyzers individually against a sanitized fixture. Do not solve persistent long-running work only by making web timeouts unlimited.

## Empty or incomplete findings

Check analyzer status and captured errors. Missing output may mean a tool failed, timed out, could not parse a file, or was not installed. A failed analyzer is not equivalent to zero findings.

## Report generation fails

Verify the analysis exists, belongs to the current user, has complete data, and that report directories are writable. Check available disk space, filename safety, font/image dependencies, and bounded content size.

## Static files or pages appear outdated

Hard refresh the browser, inspect cache headers, confirm the server is using the expected checkout, and verify there is only one matching template/static file. Restart the correct process after deployment.

## Reverse proxy errors

For `502`, verify Gunicorn is running and bound to the configured address. For `504`, inspect worker timeout and analysis duration. For wrong scheme or redirect loops, review forwarded headers and proxy trust configuration.

## Docker issues

Confirm Docker assets actually exist in the checked-out release. RC1 documentation does not make missing Docker files operational. Inspect container logs, environment injection, volume ownership, health checks, and the production command.

## Getting useful diagnostics

Record the exact commit, operating system, Python version, virtual-environment path, dependency version, command, full sanitized traceback, affected route/workflow, and minimal reproduction. Remove secrets, tokens, user data, and proprietary source before sharing.
