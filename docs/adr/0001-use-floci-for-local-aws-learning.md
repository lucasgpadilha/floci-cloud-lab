# ADR 0001: Use Floci for Local AWS Learning

## Status

Accepted.

## Context

The project should demonstrate AWS learning and portfolio skills without cloud costs or account requirements.

## Decision

Use Floci as the local AWS emulator and target `http://localhost:4566` by default.

## Consequences

Positive:

- No AWS cost by default.
- No AWS account required.
- Reproducible local demos.
- AWS SDK/CLI/Terraform workflows remain familiar.

Trade-offs:

- Emulator behavior may differ from AWS in edge cases.
- Some services or operations may have incomplete compatibility.
- Real AWS deployment remains a separate future concern.
