resource "aws_dynamodb_table" "metadata" {
  name         = var.table_name
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "pk"
  range_key    = "sk"

  # Phase 4 DynamoDB modeling notes:
  # - The app now writes category/index projection fields (`gsi1pk`, `gsi1sk`), a
  #   `version` attribute, and optional TTL epoch (`expires_at`) for portfolio evidence.
  # - The current local table shape remains unchanged to avoid an unapproved local
  #   migration/apply. Category queries fall back to the base owner query when the
  #   optional GSI is not present. See docs/dynamodb-data-model.md.
  # - A future approved local migration can add a GSI named `gsi1` with hash key
  #   `gsi1pk` and range key `gsi1sk`, plus a TTL block on `expires_at`.

  attribute {
    name = "pk"
    type = "S"
  }

  attribute {
    name = "sk"
    type = "S"
  }

  tags = var.tags
}
