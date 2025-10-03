# Donkey Betz Monitoring Guide

## Overview

This guide covers the comprehensive monitoring infrastructure for the Donkey Betz platform using Prometheus and Grafana.

## Architecture

The monitoring stack consists of:

- **Prometheus**: Metrics collection and storage
- **Grafana**: Visualization and dashboards
- **Node Exporter**: System metrics (CPU, memory, disk)
- **PostgreSQL Exporter**: Database metrics
- **Redis Exporter**: Cache metrics
- **Django Prometheus**: Application metrics

## Quick Start

### Starting the Monitoring Stack

```bash
# Start all services including monitoring
docker-compose up -d

# View running services
docker-compose ps

# Check logs
docker-compose logs -f prometheus grafana
```

### Access Points

- **Grafana Dashboard**: http://localhost:3001
  - Username: `admin`
  - Password: `admin`
- **Prometheus**: http://localhost:9090
- **Node Exporter**: http://localhost:9100
- **PostgreSQL Exporter**: http://localhost:9187
- **Redis Exporter**: http://localhost:9121

## Key Metrics to Monitor

### System Metrics

- **CPU Usage**: `100 - (avg(irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)`
- **Memory Usage**: `(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100`
- **Disk Usage**: `(1 - (node_filesystem_avail_bytes / node_filesystem_size_bytes)) * 100`

### Application Metrics

- **HTTP Requests**: `django_http_requests_total`
- **HTTP Response Status**: `django_http_responses_total_by_status_total`
- **Request Duration**: `django_http_request_duration_seconds`
- **Database Queries**: `django_db_query_count`

### Database Metrics

- **Active Connections**: `pg_stat_activity_count`
- **Query Duration**: `pg_stat_activity_max_tx_duration`
- **Database Size**: `pg_database_size_bytes`

### Cache Metrics

- **Memory Usage**: `redis_memory_used_bytes`
- **Connected Clients**: `redis_connected_clients`
- **Commands Processed**: `redis_commands_processed_total`

## Alerts Configuration

### Critical Alerts

1. **Service Down**: Any core service (Django, PostgreSQL, Redis) is down
2. **High CPU**: CPU usage > 80% for 5 minutes
3. **High Memory**: Memory usage > 80% for 5 minutes
4. **Disk Space**: Disk usage > 85%
5. **Database Connections**: > 80 active connections

### Warning Alerts

1. **API Error Rate**: > 5% for 5 minutes
2. **High Response Time**: 95th percentile > 1 second
3. **Slow Database Queries**: Queries > 5 minutes
4. **Redis Memory**: > 80% memory usage

## Dashboards

### System Overview Dashboard

Located at: `monitoring/grafana/dashboards/system-overview.json`

Panels:
- System Health Status
- CPU Usage Over Time
- Memory Usage Over Time
- Disk Usage Over Time
- API Response Times
- API Error Rates
- Database Connection Count
- Redis Memory Usage

### Custom Dashboard Creation

1. Access Grafana at http://localhost:3001
2. Click "+" → "Dashboard"
3. Add panels with Prometheus queries
4. Save dashboard
5. Export JSON and save to `monitoring/grafana/dashboards/`

## Troubleshooting

### Common Issues

#### Prometheus Not Scraping Targets

```bash
# Check Prometheus targets
curl http://localhost:9090/api/v1/targets

# Check service connectivity
docker-compose exec prometheus wget -qO- http://backend:8000/metrics
```

#### Grafana Not Showing Data

1. Check datasource configuration
2. Verify Prometheus is running
3. Check panel queries syntax
4. Ensure proper time ranges

#### High Memory Usage

```bash
# Check container memory usage
docker stats

# Restart specific service
docker-compose restart prometheus
```

### Log Analysis

```bash
# View Prometheus logs
docker-compose logs -f prometheus

# View Grafana logs
docker-compose logs -f grafana

# View Django metrics logs
docker-compose logs -f backend | grep prometheus
```

## Maintenance

### Data Retention

- Prometheus: 30 days (configurable in prometheus.yml)
- Grafana: Depends on datasource settings

### Backup

```bash
# Backup Prometheus data
docker-compose exec prometheus tar -czf /tmp/prometheus-backup.tar.gz /prometheus

# Backup Grafana dashboards
docker-compose exec grafana tar -czf /tmp/grafana-backup.tar.gz /var/lib/grafana
```

### Updates

```bash
# Update monitoring stack
docker-compose pull prometheus grafana node_exporter postgres_exporter redis_exporter
docker-compose up -d --no-deps prometheus grafana node_exporter postgres_exporter redis_exporter
```

## Performance Optimization

### Resource Allocation

Current resource limits:
- Prometheus: 512MB memory, 0.5 CPU
- Grafana: 512MB memory, 0.5 CPU
- Exporters: 128MB memory, 0.2 CPU each

### Query Performance

- Use recording rules for frequently used queries
- Limit query time ranges
- Use appropriate step sizes for graphs

## Security

### Access Control

- Grafana admin password should be changed from default
- Consider enabling authentication
- Use HTTPS in production

### Network Security

- Monitoring services are on internal Docker networks
- Only necessary ports are exposed
- Firewall rules should restrict access

## Integration

### Alerting

To enable alerting:

1. Set up Alertmanager
2. Configure notification channels
3. Add alerting rules

### External Monitoring

Can integrate with:
- Datadog
- New Relic
- AWS CloudWatch
- Custom webhook endpoints

## Production Considerations

### Scaling

- Use external Prometheus storage for large deployments
- Consider Grafana clustering
- Use load balancers for high availability

### Monitoring the Monitoring

- Set up monitoring for the monitoring stack itself
- Use external health checks
- Monitor disk space for metrics storage

## Support

For issues with monitoring:

1. Check service logs
2. Verify configurations
3. Test connectivity between services
4. Review resource usage
5. Check Docker network connectivity

## Appendix

### Useful Prometheus Queries

```promql
# Top 5 endpoints by request count
topk(5, sum(rate(django_http_requests_total[5m])) by (method, view))

# Database connection pool usage
pg_stat_activity_count / pg_settings_max_connections * 100

# Memory usage by container
container_memory_usage_bytes / container_spec_memory_limit_bytes * 100

# Disk I/O rate
rate(node_disk_io_time_seconds_total[5m])
```

### Grafana Variables

Common variables for dynamic dashboards:
- `$instance`: Node instance
- `$job`: Prometheus job
- `$interval`: Time interval
- `$database`: Database name