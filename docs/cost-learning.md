# Cost Learning

## Cost model

The default workflow has zero AWS cost because it runs against Floci locally.

Costs can still exist locally through:

- Docker CPU/memory/disk usage.
- Downloaded container images.
- Local persistent volumes if enabled.

## AWS cost concepts to document

Even though no real AWS resources are created, the lab should document how these resources would affect cost in AWS:

- S3 storage and requests.
- DynamoDB on-demand reads/writes/storage.
- Lambda invocations and duration.
- API Gateway requests.
- CloudWatch log ingestion and retention.
- Cognito monthly active users.

## Portfolio angle

The project demonstrates cost-aware cloud engineering by validating architecture locally before any real cloud spend.
