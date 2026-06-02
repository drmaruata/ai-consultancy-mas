terraform {
  required_providers {
    redpanda = {
      source  = "redpanda-data/redpanda"
      version = "~> 0.8"
    }
    upstash = {
      source  = "upstash/upstash"
      version = "~> 1.5"
    }
    supabase = {
      source  = "supabase/supabase"
      version = "~> 1.0"
    }
  }
}

provider "redpanda" {
  client_id     = var.redpanda_client_id
  client_secret = var.redpanda_client_secret
}

provider "upstash" {
  email   = var.upstash_email
  api_key = var.upstash_api_key
}

provider "supabase" {
  access_token = var.supabase_access_token
}
