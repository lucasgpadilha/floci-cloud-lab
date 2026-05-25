# Architecture

## Intent

Floci Cloud Lab is a local-first AWS learning lab. It uses Floci as an AWS-compatible emulator so cloud patterns can be learned, tested, and demonstrated without creating real AWS resources.

## High-level flow

1. Docker Compose starts Floci on port 4566.
2. Terraform points the AWS provider to `http://localhost:4566`.
3. Terraform creates local emulated resources.
4. Python smoke/integration tests use boto3 against the same endpoint.
5. Evidence from local runs is saved for portfolio review.

## Planned lab architecture

- S3: stores static/demo objects.
- DynamoDB: stores object metadata and profile-like records.
- Lambda: executes simple backend handlers where feasible.
- API Gateway v2: exposes HTTP routes to Lambda where feasible.
- Cognito: demonstrates auth concepts where Floci compatibility is sufficient.
- CloudWatch Logs/Metrics: captures local operational evidence where supported.
- IAM/STS: documents and validates least-privilege concepts locally where practical.

## Why local first

Local-first development avoids AWS cost and account friction while preserving AWS-shaped workflows. The portfolio value comes from reproducible architecture, IaC, tests, and runbooks rather than from spending money on cloud resources.

## Out of scope for v1

- Real AWS deployment.
- GitHub Actions.
- GitLab runners.
- Production domains, certificates, or CloudFront.
- Real AWS Budgets resources.
