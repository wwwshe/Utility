# Secrets And Privacy Policy

## Purpose

Avoid exposing credentials, private data, or user-sensitive information.

## Secrets

- Do not print, copy, commit, or summarize secrets such as API keys, tokens, passwords, private keys, cookies, or session values.
- Treat `.env`, keychain exports, credential files, provisioning profiles, and private config files as sensitive.
- If a secret appears in command output, redact it in the response.
- If a secret is accidentally added to a file, tell the user and recommend rotation.

## Data Handling

- Read only the files needed for the task.
- Do not include private file contents in the response unless the user asks for them and it is necessary.
- Avoid sending sensitive project data to external services unless the user explicitly asks and understands the risk.

## Commits And Logs

- Check staged changes for accidental secrets before committing when secrets may be involved.
- Do not add secret values to logs, generated reports, screenshots, or test fixtures.
