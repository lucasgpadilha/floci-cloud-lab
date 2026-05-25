# S3 object storage

This project uses S3-compatible object storage through Floci at `http://localhost:4566`. The goal is to demonstrate practical S3 patterns beyond a basic `PutObject`/`GetObject` demo while keeping the lab local-first and cost-free by default.

## Bucket

Local bucket:

```text
floci-cloud-lab-local-objects
```

Terraform module:

```text
infra/modules/object-storage/main.tf
```

Currently applied local resource behavior:

- bucket exists in Floci
- bucket versioning is enabled by Terraform
- application writes object content, content type, metadata, and SHA-256 integrity metadata

## Object key convention

Application object keys use:

```text
objects/<safe-owner-id>/<object-id>/<safe-filename>
```

Example:

```text
objects/s3-pattern-user/obj_123/s3-pattern-proof.txt
```

Why this shape:

- groups user-owned objects under a readable prefix
- keeps object IDs in the path for uniqueness
- keeps the original filename idea without allowing path traversal characters
- maps well to lifecycle/event prefixes such as `objects/`

## Metadata and content type

Every upload stores:

- `ContentType` from the API payload
- system metadata:
  - `owner-id`
  - `object-id`
  - `sha256`
- user metadata copied from the request metadata with a `user-` prefix

Example S3 metadata:

```json
{
  "owner-id": "lucas",
  "object-id": "obj_123",
  "sha256": "...",
  "user-category": "notes",
  "user-ttl-days": "30"
}
```

S3 metadata values are strings, so the app converts request metadata values with `str(value)` before upload.

## Integrity checks

The repository computes SHA-256 before upload and stores it in both:

- DynamoDB metadata record as `sha256`
- S3 object metadata as `sha256`

On retrieval, the repository reads object bytes, recomputes SHA-256, compares against S3 metadata, and returns:

```json
{"integrity_verified": true}
```

This demonstrates an application-level integrity check. Real AWS S3 also exposes checksums and ETag behavior, but ETag is not a reliable MD5 for multipart or encrypted objects.

## Versioning

The bucket has versioning enabled via Terraform:

```hcl
resource "aws_s3_bucket_versioning" "objects" {
  versioning_configuration {
    status = "Enabled"
  }
}
```

The app records `s3_version_id` when the emulator returns a `VersionId` from `PutObject`. Some local emulator responses may omit or simplify version IDs, so docs and tests treat versioning as a bucket capability and preserve returned evidence when available.

## Presigned URLs

The integration test generates a local presigned GET URL with boto3:

```python
s3.generate_presigned_url(
    "get_object",
    Params={"Bucket": bucket, "Key": key},
    ExpiresIn=300,
)
```

For local Floci this URL starts with:

```text
http://localhost:4566/...
```

The signature query string may use either legacy `Signature=` or SigV4 `X-Amz-Signature=` depending on client configuration. The portfolio point is that the app can produce time-bound download URLs without exposing bucket-wide public access.

## Lifecycle policy example

The current Terraform module documents lifecycle behavior but does not apply a lifecycle resource yet, so the local plan remains drift-free without requiring another apply.

Real AWS example:

```hcl
resource "aws_s3_bucket_lifecycle_configuration" "objects" {
  bucket = aws_s3_bucket.objects.id

  rule {
    id     = "expire-old-demo-objects"
    status = "Enabled"

    filter {
      prefix = "objects/"
    }

    noncurrent_version_expiration {
      noncurrent_days = 30
    }

    expiration {
      days = 90
    }
  }
}
```

Lifecycle rules are useful for cost control, retention, and cleanup. They should be carefully reviewed before production use because they can permanently delete data.

## Multipart upload

Multipart upload is not needed for this small demo API, but it matters for real AWS:

- use multipart for large objects
- validate checksum behavior per part and final object
- abort incomplete multipart uploads with lifecycle rules
- avoid assuming ETag equals MD5 for multipart objects

The local API intentionally caps object content size, so multipart is documented as a future/real-AWS pattern rather than implemented in the handler.

## Security and public access

Real AWS S3 hardening should include:

- Block Public Access enabled
- bucket ownership controls with ACLs disabled
- default encryption, commonly SSE-S3 by default or SSE-KMS for stronger key governance
- HTTPS-only bucket policy using `aws:SecureTransport=false` deny
- least-privilege IAM allowing only required prefixes/actions
- access logging or CloudTrail data events where appropriate
- no public read policy for this lab's object bucket

This repo uses local fake credentials and a local endpoint by default. It does not create real AWS buckets or mutate real bucket policies.

## Events and replication

Object-created events are planned for later event-driven phases. In real AWS, S3 event notifications can target SQS, SNS, Lambda, or EventBridge. Replication would require versioning, IAM roles, destination buckets, and cost/security review.

## Cost drivers in real AWS

Important S3 cost dimensions:

- storage GB-month by storage class
- request count: PUT, GET, LIST, lifecycle transitions
- data transfer out
- replication transfer and request costs
- KMS request costs if using SSE-KMS
- CloudTrail data events if enabled
- incomplete multipart uploads if not cleaned up

## Local validation

Relevant tests:

```bash
.venv/bin/python -m pytest tests/unit/test_s3_storage_model.py -q
.venv/bin/python -m pytest tests/integration/test_s3_patterns.py -q
.venv/bin/python -m pytest tests -q
```

Acceptance criteria covered:

- object key naming convention
- content type persistence
- user and system metadata persistence
- SHA-256 metadata on upload
- retrieval integrity verification
- local presigned URL generation
