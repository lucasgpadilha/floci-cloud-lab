locals {
  common_tags = merge(
    {
      Project     = "FlociCloudLab"
      Environment = var.environment
      ManagedBy   = "Terraform"
      Owner       = "Lucas"
      CostCenter  = "PersonalCloudLab"
      Runtime     = "FlociLocal"
    },
    var.tags,
  )
}

module "object_storage" {
  source = "../../modules/object-storage"

  bucket_name = "${var.name_prefix}-${var.environment}-objects"
  tags        = local.common_tags
}

module "database" {
  source = "../../modules/database"

  table_name = "${var.name_prefix}-${var.environment}-metadata"
  tags       = local.common_tags
}

module "observability" {
  source = "../../modules/observability"

  log_group_name     = "/floci-cloud-lab/${var.environment}/app"
  log_retention_days = var.log_retention_days
  tags               = local.common_tags
}
