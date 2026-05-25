# Security

## Local fake credentials

The values in `.env.example` are fake credentials for Floci only:

- `AWS_ACCESS_KEY_ID=test`
- `AWS_SECRET_ACCESS_KEY=test`

Do not replace these with real AWS credentials in committed files.

## Real AWS isolation

Default commands must target `http://localhost:4566`. Any command targeting real AWS requires explicit approval.

## Secrets policy

- Do not commit real `.env` files.
- Do not read or edit `~/.aws`, `~/.ssh`, or `~/.kube`.
- Do not print secrets.
- Keep local state and evidence sanitized.

## IAM learning

IAM policies in this project are for learning and local validation. They should still model least privilege to show production thinking.
