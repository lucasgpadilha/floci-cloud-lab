# DynamoDB data model

This project uses DynamoDB-compatible storage through Floci at `http://localhost:4566`. The goal is to show practical DynamoDB design without requiring a real AWS account or cloud spend.

## Table

Local table:

```text
floci-cloud-lab-local-metadata
```

Primary key:

```text
pk = OWNER#<owner_id>
sk = OBJECT#<object_id>
```

The table uses `PAY_PER_REQUEST` in Terraform, matching the on-demand billing mode a small serverless app would commonly start with on real AWS.

## Item shape

Example item:

```json
{
  "pk": "OWNER#lucas",
  "sk": "OBJECT#obj_abc123",
  "object_id": "obj_abc123",
  "owner_id": "lucas",
  "name": "demo.txt",
  "content_type": "text/plain",
  "size_bytes": 42,
  "metadata": {"category": "notes", "ttl_days": 30},
  "category": "notes",
  "version": 1,
  "s3_bucket": "floci-cloud-lab-local-objects",
  "s3_key": "objects/lucas/obj_abc123/demo.txt",
  "created_at": "2026-05-25T10:00:00Z",
  "gsi1pk": "OWNER#lucas#CATEGORY#notes",
  "gsi1sk": "CREATED#2026-05-25T10:00:00Z#OBJECT#obj_abc123",
  "expires_at": 1790000000,
  "ttl_status": "scheduled"
}
```

The object content itself lives in S3-compatible storage. DynamoDB stores metadata and pointers to the S3 object.

## Access patterns

| Access pattern | Current implementation | DynamoDB concept shown |
| --- | --- | --- |
| Create object metadata | `PutItem` with `attribute_not_exists(pk) AND attribute_not_exists(sk)` | conditional writes / accidental overwrite protection |
| Get object by id | `GetItem` by `pk` + `sk` | direct key lookup |
| List recent objects by owner | `Query` by owner partition, then sort/page in repository | partition query, pagination contract |
| Query by owner/category | Writes `gsi1pk`/`gsi1sk`; attempts `gsi1`, falls back locally if the index is absent | GSI access pattern and emulator/migration gap handling |
| Soft delete | Planned: write `deleted_at` and filter active views | tombstone modeling |
| TTL cleanup | Optional `expires_at` epoch from `metadata.ttl_days` | DynamoDB TTL lifecycle field |
| Optimistic concurrency | `version` attribute starts at `1`; update flows planned for later phases | versioned conditional updates |

## Why this key design

The owner partition groups all records owned by a caller:

```text
OWNER#lucas
```

The sort key addresses individual objects:

```text
OBJECT#obj_abc123
```

This keeps `GetItem` simple and makes owner-scoped list queries local to one partition. For a small portfolio lab this is intentionally easy to explain.

For high-volume real AWS workloads, the design would need additional thinking around hot partitions. A single very active owner could overload one partition. Common mitigations include write sharding, time-bucketed partition keys, or separating high-cardinality access patterns into additional indexes.

## GSI design

The app now writes projected index attributes:

```text
gsi1pk = OWNER#<owner_id>#CATEGORY#<category>
gsi1sk = CREATED#<created_at>#OBJECT#<object_id>
```

A real or approved migrated local table can add:

```hcl
global_secondary_index {
  name            = "gsi1"
  hash_key        = "gsi1pk"
  range_key       = "gsi1sk"
  projection_type = "ALL"
}
```

The current Terraform table intentionally does not add the GSI yet because that would require an approved local apply/migration. The repository attempts the `gsi1` query and falls back to the base owner query plus category filtering if the local table does not expose the index.

## Pagination

`GET /objects` accepts:

```text
limit=<1..100>
cursor=<opaque cursor>
category=<optional category>
```

The API returns:

```json
{
  "data": {
    "count": 2,
    "objects": [],
    "next_cursor": "eyJvZmZzZXQiOjJ9"
  },
  "request_id": "..."
}
```

The cursor is intentionally opaque to callers. In this local lab it encodes an offset; in production DynamoDB code this would usually wrap `LastEvaluatedKey`.

## TTL

If the create-object payload includes `metadata.ttl_days` as a positive integer, the repository writes `expires_at` as an epoch timestamp. DynamoDB TTL requires an epoch-seconds number attribute. Floci/local behavior may not physically delete expired items, so the lab treats TTL as a modeled lifecycle field and documents the real AWS behavior.

## Conditional writes

Object creation writes metadata with:

```text
attribute_not_exists(pk) AND attribute_not_exists(sk)
```

This demonstrates a common DynamoDB safety pattern: never overwrite an existing item unless the caller explicitly uses an update path with a matching version.

## Optimistic concurrency

New records start with:

```json
{"version": 1}
```

A real update endpoint would use a condition similar to:

```text
version = :expected_version
```

and increment the version on success. The repo has the model field and test coverage now; mutation endpoints are intentionally left for a later phase.

## Emulator support notes

- Primary key queries are exercised against Floci through integration tests.
- Conditional write behavior is implemented in the repository and covered by unit/model tests.
- Category query GSI fields are written now, but the physical local GSI is treated as a future approved migration to avoid changing applied local infrastructure without explicit approval.
- TTL fields are modeled as data. Real AWS DynamoDB TTL deletion is asynchronous and should not be used as an immediate-delete guarantee.

## Validation

Relevant tests:

```bash
.venv/bin/python -m pytest tests/unit/test_dynamodb_model.py -q
.venv/bin/python -m pytest tests/integration/test_app_floci_integration.py -q
.venv/bin/python -m pytest tests -q
```
