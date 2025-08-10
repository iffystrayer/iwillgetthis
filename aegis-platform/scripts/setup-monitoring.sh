#!/bin/bash
# ==============================================
# Aegis Platform - Monitoring Setup Script
# ==============================================
# This script sets up comprehensive monitoring infrastructure
# ==============================================

set -e

# Configuration
MONITORING_DIR="$(pwd)/monitoring"
GRAFANA_ADMIN_PASSWORD="${GRAFANA_ADMIN_PASSWORD:-admin_change_this_password}"
DOMAIN="${DOMAIN:-yourdomain.com}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_header() {
    echo -e "${BLUE}======================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}======================================${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

check_requirements() {
    print_header "Checking Requirements"
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        print_error "Docker is required but not installed"
        exit 1
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        print_error "Docker Compose is required but not installed"
        exit 1
    fi
    
    # Check if monitoring directory exists
    if [ ! -d "$MONITORING_DIR" ]; then
        print_error "Monitoring directory not found: $MONITORING_DIR"
        exit 1
    fi
    
    print_success "Requirements check passed"
}

create_monitoring_directories() {
    print_header "Creating Monitoring Directories"
    
    # Create necessary directories
    mkdir -p "${MONITORING_DIR}/grafana/provisioning/dashboards"
    mkdir -p "${MONITORING_DIR}/grafana/provisioning/datasources"
    mkdir -p "${MONITORING_DIR}/grafana/dashboards"
    mkdir -p "${MONITORING_DIR}/alert_rules"
    mkdir -p "${MONITORING_DIR}/recording_rules"
    mkdir -p "${MONITORING_DIR}/templates"
    mkdir -p "${MONITORING_DIR}/loki"
    mkdir -p "${MONITORING_DIR}/promtail"
    mkdir -p "${MONITORING_DIR}/exporters"
    
    print_success "Monitoring directories created"
}

setup_grafana_provisioning() {
    print_header "Setting Up Grafana Provisioning"
    
    # Create datasources configuration
    cat > "${MONITORING_DIR}/grafana/provisioning/datasources/prometheus.yml" << EOF
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    url: http://prometheus:9090
    access: proxy
    isDefault: true
    basicAuth: false
    editable: true
    
  - name: Loki
    type: loki
    url: http://loki:3100
    access: proxy
    basicAuth: false
    editable: true
    
  - name: Alertmanager
    type: alertmanager
    url: http://alertmanager:9093
    access: proxy
    basicAuth: false
    editable: true
EOF

    # Create dashboards configuration
    cat > "${MONITORING_DIR}/grafana/provisioning/dashboards/default.yml" << EOF
apiVersion: 1

providers:
  - name: 'Aegis Dashboards'
    orgId: 1
    folder: 'Aegis Platform'
    folderUid: aegis
    type: file
    disableDeletion: false
    updateIntervalSeconds: 10
    allowUiUpdates: true
    options:
      path: /var/lib/grafana/dashboards
EOF
    
    print_success "Grafana provisioning configured"
}

setup_loki_config() {
    print_header "Setting Up Loki Configuration"
    
    cat > "${MONITORING_DIR}/loki/loki-config.yml" << EOF
auth_enabled: false

server:
  http_listen_port: 3100
  grpc_listen_port: 9096

common:
  path_prefix: /loki
  storage:
    filesystem:
      chunks_directory: /loki/chunks
      rules_directory: /loki/rules
  replication_factor: 1
  ring:
    instance_addr: 127.0.0.1
    kvstore:
      store: inmemory

query_scheduler:
  max_outstanding_requests_per_tenant: 4096

schema_config:
  configs:
    - from: 2020-10-24
      store: boltdb-shipper
      object_store: filesystem
      schema: v11
      index:
        prefix: index_
        period: 24h

ruler:
  alertmanager_url: http://alertmanager:9093

limits_config:
  reject_old_samples: true
  reject_old_samples_max_age: 168h
  ingestion_rate_mb: 16
  ingestion_burst_size_mb: 32
  max_query_parallelism: 100
  max_streams_per_user: 10000
  max_line_size: 256000
  retention_period: 744h

chunk_store_config:
  max_look_back_period: 0s

table_manager:
  retention_deletes_enabled: false
  retention_period: 0s

compactor:
  working_directory: /loki
  shared_store: filesystem
  compaction_interval: 10m
  retention_enabled: true
  retention_delete_delay: 2h
  retention_delete_worker_count: 150
EOF

    print_success "Loki configuration created"
}

setup_promtail_config() {
    print_header "Setting Up Promtail Configuration"
    
    cat > "${MONITORING_DIR}/promtail/promtail-config.yml" << EOF
server:
  http_listen_port: 9080
  grpc_listen_port: 0

positions:
  filename: /tmp/positions.yaml

clients:
  - url: http://loki:3100/loki/api/v1/push

scrape_configs:
  - job_name: containers
    static_configs:
      - targets:
          - localhost
        labels:
          job: containerlogs
          __path__: /var/lib/docker/containers/*/*log

    pipeline_stages:
      - json:
          expressions:
            output: log
            stream: stream
            attrs:
      - json:
          expressions:
            tag:
          source: attrs
      - regex:
          expression: (?P<container_name>(?:[^|]*)*)
          source: tag
      - timestamp:
          format: RFC3339Nano
          source: time
      - labels:
          stream:
          container_name:
      - output:
          source: output

  - job_name: syslog
    static_configs:
      - targets:
          - localhost
        labels:
          job: syslog
          __path__: /var/log/syslog

  - job_name: aegis-backend
    static_configs:
      - targets:
          - localhost
        labels:
          job: aegis-backend
          __path__: /var/log/aegis/*.log
EOF

    print_success "Promtail configuration created"
}

setup_postgres_exporter() {
    print_header "Setting Up PostgreSQL Exporter"
    
    cat > "${MONITORING_DIR}/exporters/postgres-queries.yaml" << EOF
pg_replication:
  query: "SELECT CASE WHEN NOT pg_is_in_recovery() THEN 0 ELSE GREATEST (0, EXTRACT(EPOCH FROM (now() - pg_last_xact_replay_timestamp()))) END AS lag"
  master: true
  metrics:
    - lag:
        usage: "GAUGE"
        description: "Replication lag behind master in seconds"

pg_postmaster:
  query: "SELECT pg_postmaster_start_time as start_time_seconds from pg_postmaster_start_time()"
  master: true
  metrics:
    - start_time_seconds:
        usage: "GAUGE"
        description: "Time at which postmaster started"

pg_stat_user_tables:
  query: |
   SELECT current_database() datname, schemaname, tablename, seq_scan, seq_tup_read, idx_scan, idx_tup_fetch, n_tup_ins, n_tup_upd, n_tup_del, n_tup_hot_upd, n_live_tup, n_dead_tup, n_mod_since_analyze, COALESCE(last_vacuum, '1970-01-01Z'), COALESCE(last_autovacuum, '1970-01-01Z') as last_autovacuum, COALESCE(last_analyze, '1970-01-01Z') as last_analyze, COALESCE(last_autoanalyze, '1970-01-01Z') as last_autoanalyze, vacuum_count, autovacuum_count, analyze_count, autoanalyze_count FROM pg_stat_user_tables
  metrics:
    - datname:
        usage: "LABEL"
        description: "Name of current database"
    - schemaname:
        usage: "LABEL"
        description: "Name of the schema that this table is in"
    - tablename:
        usage: "LABEL"
        description: "Name of this table"
    - seq_scan:
        usage: "COUNTER"
        description: "Number of sequential scans initiated on this table"
    - seq_tup_read:
        usage: "COUNTER"
        description: "Number of live rows fetched by sequential scans"
    - idx_scan:
        usage: "COUNTER"
        description: "Number of index scans initiated on this table"
    - idx_tup_fetch:
        usage: "COUNTER"
        description: "Number of live rows fetched by index scans"
    - n_tup_ins:
        usage: "COUNTER"
        description: "Number of rows inserted"
    - n_tup_upd:
        usage: "COUNTER"
        description: "Number of rows updated"
    - n_tup_del:
        usage: "COUNTER"
        description: "Number of rows deleted"
    - n_tup_hot_upd:
        usage: "COUNTER"
        description: "Number of rows HOT updated"
    - n_live_tup:
        usage: "GAUGE"
        description: "Estimated number of live rows"
    - n_dead_tup:
        usage: "GAUGE"
        description: "Estimated number of dead rows"
    - n_mod_since_analyze:
        usage: "GAUGE"
        description: "Estimated number of rows changed since last analyze"
    - last_vacuum:
        usage: "GAUGE"
        description: "Last time at which this table was manually vacuumed"
    - last_autovacuum:
        usage: "GAUGE"
        description: "Last time at which this table was vacuumed by the autovacuum daemon"
    - last_analyze:
        usage: "GAUGE"
        description: "Last time at which this table was manually analyzed"
    - last_autoanalyze:
        usage: "GAUGE"
        description: "Last time at which this table was analyzed by the autovacuum daemon"
    - vacuum_count:
        usage: "COUNTER"
        description: "Number of times this table has been manually vacuumed"
    - autovacuum_count:
        usage: "COUNTER"
        description: "Number of times this table has been vacuumed by the autovacuum daemon"
    - analyze_count:
        usage: "COUNTER"
        description: "Number of times this table has been manually analyzed"
    - autoanalyze_count:
        usage: "COUNTER"
        description: "Number of times this table has been analyzed by the autovacuum daemon"
EOF

    print_success "PostgreSQL exporter configuration created"
}

update_domain_configs() {
    print_header "Updating Domain Configuration"
    
    if [ "$DOMAIN" != "yourdomain.com" ]; then
        print_warning "Updating domain references from yourdomain.com to $DOMAIN"
        
        # Update Prometheus config
        sed -i "s/yourdomain\.com/$DOMAIN/g" "${MONITORING_DIR}/prometheus.yml"
        
        # Update Alertmanager config
        sed -i "s/yourdomain\.com/$DOMAIN/g" "${MONITORING_DIR}/alertmanager.yml"
        
        # Update monitoring docker-compose
        sed -i "s/yourdomain\.com/$DOMAIN/g" "${MONITORING_DIR}/docker-compose.monitoring.yml"
        
        print_success "Domain configuration updated to $DOMAIN"
    fi
}

start_monitoring_stack() {
    print_header "Starting Monitoring Stack"
    
    # Start monitoring services
    docker-compose -f "${MONITORING_DIR}/docker-compose.monitoring.yml" up -d
    
    print_success "Monitoring stack started"
    
    # Wait for services to be ready
    print_warning "Waiting for services to be ready..."
    sleep 30
    
    # Check service health
    print_header "Checking Service Health"
    
    services=("prometheus:9090" "grafana:3000" "alertmanager:9093")
    for service in "${services[@]}"; do
        service_name="${service%%:*}"
        port="${service##*:}"
        if curl -f -s "http://localhost:$port" > /dev/null 2>&1; then
            print_success "$service_name is healthy"
        else
            print_warning "$service_name may not be ready yet"
        fi
    done
}

print_access_info() {
    print_header "Monitoring Services Access Information"
    
    echo -e "${GREEN}Monitoring services are now available:${NC}"
    echo ""
    echo -e "${BLUE}📊 Grafana (Dashboards):${NC}"
    echo "   URL: http://localhost:3001"
    echo "   Username: admin"
    echo "   Password: $GRAFANA_ADMIN_PASSWORD"
    echo ""
    echo -e "${BLUE}📈 Prometheus (Metrics):${NC}"
    echo "   URL: http://localhost:9090"
    echo ""
    echo -e "${BLUE}🚨 Alertmanager (Alerts):${NC}"
    echo "   URL: http://localhost:9093"
    echo ""
    echo -e "${BLUE}💻 System Metrics:${NC}"
    echo "   Node Exporter: http://localhost:9100"
    echo "   cAdvisor: http://localhost:8080"
    echo ""
    echo -e "${YELLOW}Next Steps:${NC}"
    echo "1. Configure your domain-specific settings"
    echo "2. Set up notification channels in Alertmanager"
    echo "3. Import additional dashboards in Grafana"
    echo "4. Configure SSL certificates for production"
    echo "5. Set up external monitoring endpoints"
}

main() {
    print_header "Aegis Platform - Monitoring Setup"
    
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --domain)
                DOMAIN="$2"
                shift 2
                ;;
            --grafana-password)
                GRAFANA_ADMIN_PASSWORD="$2"
                shift 2
                ;;
            --help)
                echo "Usage: $0 [--domain yourdomain.com] [--grafana-password password]"
                echo "Options:"
                echo "  --domain DOMAIN              Set the domain name"
                echo "  --grafana-password PASSWORD  Set Grafana admin password"
                echo "  --help                       Show this help message"
                exit 0
                ;;
            *)
                print_error "Unknown option: $1"
                exit 1
                ;;
        esac
    done
    
    check_requirements
    create_monitoring_directories
    setup_grafana_provisioning
    setup_loki_config
    setup_promtail_config
    setup_postgres_exporter
    update_domain_configs
    start_monitoring_stack
    print_access_info
    
    print_header "Monitoring Setup Complete"
    print_success "All monitoring services are running and configured"
    print_warning "Remember to secure your monitoring endpoints for production use"
}

main "$@"