resource "upstash_redis_database" "mas_redis" {
  database_name = "mas-redis-${var.environment}"
  region        = "eu-west-1"
  tls           = "true"
}

resource "upstash_vector_index" "mas_vector" {
  name       = "mas-vector-${var.environment}"
  dimension  = 1536
  metric     = "cosine"
  region     = "us-east-1"
}

resource "upstash_qstash_schedule" "mas_retention_cron" {
  # This is an example scaffold for the retention cron
  destination = "https://api.example.com/retention_cron"
  cron        = "0 0 * * 0" # Weekly
}

output "upstash_redis_url" {
  value = upstash_redis_database.mas_redis.endpoint
}

output "upstash_vector_url" {
  value = upstash_vector_index.mas_vector.endpoint
}
