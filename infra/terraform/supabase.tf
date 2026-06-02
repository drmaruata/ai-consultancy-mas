resource "supabase_project" "mas_db" {
  organization_id   = var.supabase_organization_id
  name              = "mas-project-${var.environment}"
  region            = "ap-south-1"
  database_password = "ChangeMe123!" # In a real environment, use a random password provider
}

output "supabase_db_host" {
  value = supabase_project.mas_db.database_host
}
