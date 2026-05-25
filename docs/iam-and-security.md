# IAM and Security Foundations

This phase demonstrates IAM fluency without using a real AWS account. The policy documents live in `infra/modules/iam/policy-documents/` and are intentionally safe to inspect locally because they are JSON documents, not live AWS mutations.

## Local vs real AWS boundary

The current lab runs against Floci at `http://localhost:4566` with fake credentials. IAM in this phase is therefore an educational and design artifact: it shows how the application should be authorized when translated to real AWS, while the default workflow remains local-only.

Do not use real AWS credentials or real AWS endpoints unless a future task explicitly approves that scope.

## Core IAM concepts

### Users

IAM users represent long-lived identities. They are useful for understanding IAM basics, but production workloads should avoid long-lived access keys where possible.

### Roles

IAM roles are assumable identities. In a real AWS version of this project, the application runtime would use a role such as a Lambda execution role rather than static credentials.

### Trust policies

A trust policy controls who or what can assume a role. For a real Lambda deployment, the trust policy would allow `lambda.amazonaws.com` to assume the execution role.

### Permission policies

A permission policy controls what the assumed role can do. The app permission policy in this repo grants only the actions needed for:

- object read/write under the app object prefix;
- metadata table reads/writes;
- app log stream writes.

### Least privilege

Least privilege means granting the smallest action and resource set that still lets the workload function. For this lab, that means no `Action: "*"` and no `Resource: "*"` in generated policy JSON.

### Explicit deny

An explicit deny overrides allows. The educational deny policy shows how a real AWS design could block destructive or out-of-bound operations even if a broader allow appears elsewhere.

## Policy documents

| Document | Purpose |
| --- | --- |
| `infra/modules/iam/policy-documents/app-permissions.json` | Least-privilege allow policy for the app runtime. |
| `infra/modules/iam/policy-documents/educational-explicit-denies.json` | Educational examples of explicit deny guardrails. |

## Application permission model

The app should be able to:

- list only the application object prefix;
- get, put, and delete objects only under `objects/*` in the local object bucket;
- read and write metadata in the local metadata table;
- create/write app log streams for the app log group.

The app should not be able to:

- administer S3 buckets;
- delete arbitrary objects outside the app prefix;
- scan or mutate unrelated DynamoDB tables;
- mutate IAM, account, billing, organizations, or network controls;
- access real AWS accounts by default.

## Threat model

| Threat | Risk | Local guardrail | Real AWS translation |
| --- | --- | --- | --- |
| Accidental real AWS use | Cloud cost or unwanted mutations | Local endpoint validation and fake credentials | SCPs, permission boundaries, sandbox account, budget alarms |
| Leaked local env files | Secrets exposure habits | `.env` ignored; fake credentials only | Secrets Manager/SSM, no long-lived keys, secret scanning |
| Public bucket access | Data exposure | No public policy in local IaC | S3 Block Public Access, bucket policies, access analyzer |
| Overbroad IAM | Privilege escalation or accidental damage | Tests fail on exact wildcard action/resource policies | IAM Access Analyzer, policy reviews, permission boundaries |
| Untrusted uploads | Malicious content or abuse | Object prefix isolation and metadata validation | Content scanning, size limits, signed URLs, WAF where applicable |
| Drift between IaC and runtime | Unreviewed changes | `make devops-audit` uses Terraform drift detection | CI/CD plan gates, CloudTrail, Config rules |

## How this would translate to real AWS

A future real AWS template would likely add:

- a Lambda execution role;
- a trust policy for the Lambda service principal;
- the app permission policy attached to that role;
- S3 bucket policy and Block Public Access settings;
- DynamoDB table access scoped to the app table ARN;
- CloudWatch Logs access scoped to the app log group ARN;
- optional permission boundary preventing IAM/account/network administration.

That future template must remain optional. The default repository workflow should continue to target local Floci only.

## Validation

Use:

```bash
make check
make devops-audit
```

The unit tests parse the IAM policy JSON and fail on exact wildcard `Action: "*"` or `Resource: "*"`. The DevOps audit also scans the IAM module for exact wildcard policy patterns.
