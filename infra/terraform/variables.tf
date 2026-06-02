variable "environment" {
  type        = string
  description = "The environment (staging or production)"
}

variable "redpanda_client_id" {
  type        = string
  description = "Redpanda Client ID"
  sensitive   = true
}

variable "redpanda_client_secret" {
  type        = string
  description = "Redpanda Client Secret"
  sensitive   = true
}

variable "upstash_email" {
  type        = string
  description = "Upstash account email"
}

variable "upstash_api_key" {
  type        = string
  description = "Upstash API Key"
  sensitive   = true
}

variable "supabase_access_token" {
  type        = string
  description = "Supabase access token"
  sensitive   = true
}

variable "supabase_organization_id" {
  type        = string
  description = "Supabase organization ID"
}
