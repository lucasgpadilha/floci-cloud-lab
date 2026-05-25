resource "aws_s3_bucket" "objects" {
  bucket = var.bucket_name
  tags   = var.tags
}

# Phase 5 S3 modeling notes:
# - Object versioning is enabled locally and evidenced through integration tests
#   where supported by the emulator response shape.
# - The application writes content type, user metadata, and SHA-256 object metadata
#   on every PutObject call.
# - Real AWS production hardening would also add public access block, default
#   encryption, bucket policy DenyInsecureTransport, lifecycle transitions, and
#   event notifications. Those are documented in docs/s3-object-storage.md rather
#   than applied here to keep the current local Terraform plan drift-free until a
#   human approves a local apply/migration.

resource "aws_s3_bucket_versioning" "objects" {
  bucket = aws_s3_bucket.objects.id

  versioning_configuration {
    status = "Enabled"
  }
}
