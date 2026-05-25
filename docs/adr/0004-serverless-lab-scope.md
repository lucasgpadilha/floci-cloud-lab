# ADR 0004: Serverless Lab Scope

## Status

Accepted.

## Context

The portfolio project needs a realistic but manageable architecture.

## Decision

Start with a serverless-style lab using S3, DynamoDB, Lambda, API Gateway v2, Cognito where practical, CloudWatch where practical, and Python tests.

## Consequences

Positive:

- Covers high-value AWS services.
- Keeps implementation small enough for a personal portfolio.
- Provides clear expansion paths.

Trade-offs:

- Some service combinations may require Floci compatibility checks.
- Frontend complexity is deferred until the backend/IaC lab is solid.
