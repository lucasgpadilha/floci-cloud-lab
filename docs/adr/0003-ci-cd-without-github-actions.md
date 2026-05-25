# ADR 0003: CI/CD Without GitHub Actions

## Status

Accepted.

## Context

The project must not use GitHub Actions or GitLab runners, but should still demonstrate CI/CD thinking.

## Decision

Use local Makefile pipelines, Hermes agentic workflows, and later Floci-emulated CodeBuild for AWS-style CI/CD dogfooding.

## Consequences

Positive:

- No dependency on hosted CI runners.
- Strong alignment with the local AWS emulator theme.
- Demonstrates pipeline design in a distinctive way.

Trade-offs:

- Public GitHub UI will not show standard Actions badges.
- Reviewers must run local commands or inspect evidence artifacts.
