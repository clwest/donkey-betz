#!/bin/bash
# =============================================================================
# UNIFIED DONKEY BETZ PLATFORM - COMPREHENSIVE HEALTH CHECK SCRIPT
# Production-ready health monitoring for all services
# =============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
TIMEOUT=30
VERBOSE=${VERBOSE:-false}
OUTPUT_FORMAT=${OUTPUT_FORMAT:-"text"}  # text, json, prometheus
HEALTH_CHECK_INTERVAL=${HEALTH_CHECK_INTERVAL:-60}

# Service endpoints
BACKEND_URL=${BACKEND_URL:-"http://localhost:8000"}
FRONTEND_URL=${FRONTEND_URL:-"http://localhost:3000"}
MOBILE_URL=${MOBILE_URL:-"http://localhost:8081"}
REDIS_HOST=${REDIS_HOST:-"localhost"}
REDIS_PORT=${REDIS_PORT:-6379}
POSTGRES_HOST=${POSTGRES_HOST:-"localhost"}
POSTGRES_PORT=${POSTGRES_PORT:-5432}
POSTGRES_DB=${POSTGRES_DB:-"ai_unified_platform"}
POSTGRES_USER=${POSTGRES_USER:-"unified_user"}

# Health check results
declare -A HEALTH_RESULTS
declare -A HEALTH_DETAILS
declare -A HEALTH_RESPONSE_TIMES

# Logging function
log() {
    local level=$1
    shift
    local message="$@"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    if [[ $OUTPUT_FORMAT == "json" ]]; then
        return
    fi
    
    case $level in
        "INFO")
            echo -e "${BLUE}[INFO]${NC} ${timestamp} - $message"
            ;;
        "SUCCESS")
            echo -e "${GREEN}[SUCCESS]${NC} ${timestamp} - $message"
            ;;
        "WARNING")
            echo -e "${YELLOW}[WARNING]${NC} ${timestamp} - $message"
            ;;
        "ERROR")
            echo -e "${RED}[ERROR]${NC} ${timestamp} - $message"
            ;;
        "DEBUG")
            if [[ $VERBOSE == "true" ]]; then
                echo -e "${CYAN}[DEBUG]${NC} ${timestamp} - $message"
            fi
            ;;
    esac
}

# HTTP health check function
check_http_service() {
    local service_name=$1
    local url=$2
    local expected_status=${3:-200}
    local endpoint=${4:-"/health"}
    
    log "INFO" "Checking $service_name at $url$endpoint"
    
    local start_time=$(date +%s%3N)
    local response=$(curl -s -w "HTTPSTATUS:%{http_code};RESPONSE_TIME:%{time_total}" \
                    --connect-timeout $TIMEOUT \
                    --max-time $TIMEOUT \
                    "$url$endpoint" 2>/dev/null || echo "HTTPSTATUS:000;RESPONSE_TIME:0")
    local end_time=$(date +%s%3N)
    
    local http_status=$(echo $response | grep -o "HTTPSTATUS:[0-9]*" | cut -d: -f2)
    local response_time=$(echo $response | grep -o "RESPONSE_TIME:[0-9.]*" | cut -d: -f2)
    local body=$(echo $response | sed -E 's/HTTPSTATUS:[0-9]*;RESPONSE_TIME:[0-9.]*$//')
    
    HEALTH_RESPONSE_TIMES[$service_name]=$response_time
    
    if [[ "$http_status" == "$expected_status" ]]; then
        HEALTH_RESULTS[$service_name]="HEALTHY"
        HEALTH_DETAILS[$service_name]="HTTP $http_status - Response time: ${response_time}s"
        log "SUCCESS" "$service_name is healthy (HTTP $http_status) - ${response_time}s"
        return 0
    else
        HEALTH_RESULTS[$service_name]="UNHEALTHY"
        HEALTH_DETAILS[$service_name]="HTTP $http_status - Response time: ${response_time}s"
        log "ERROR" "$service_name is unhealthy (HTTP $http_status) - ${response_time}s"
        return 1
    fi
}

# Redis health check
check_redis() {
    log "INFO" "Checking Redis at $REDIS_HOST:$REDIS_PORT"
    
    local start_time=$(date +%s%3N)
    if timeout $TIMEOUT redis-cli -h $REDIS_HOST -p $REDIS_PORT ping > /dev/null 2>&1; then
        local end_time=$(date +%s%3N)
        local response_time=$(echo "scale=3; ($end_time - $start_time) / 1000" | bc)
        
        HEALTH_RESULTS["redis"]="HEALTHY"
        HEALTH_DETAILS["redis"]="PONG received - Response time: ${response_time}s"
        HEALTH_RESPONSE_TIMES["redis"]=$response_time
        log "SUCCESS" "Redis is healthy - ${response_time}s"
        return 0
    else
        HEALTH_RESULTS["redis"]="UNHEALTHY"
        HEALTH_DETAILS["redis"]="Connection failed or timeout"
        HEALTH_RESPONSE_TIMES["redis"]="timeout"
        log "ERROR" "Redis is unhealthy - connection failed"
        return 1
    fi
}

# PostgreSQL health check
check_postgres() {
    log "INFO" "Checking PostgreSQL at $POSTGRES_HOST:$POSTGRES_PORT"
    
    local start_time=$(date +%s%3N)
    if timeout $TIMEOUT pg_isready -h $POSTGRES_HOST -p $POSTGRES_PORT -U $POSTGRES_USER > /dev/null 2>&1; then
        # Additional check: test actual connection
        if timeout $TIMEOUT psql "postgresql://$POSTGRES_USER@$POSTGRES_HOST:$POSTGRES_PORT/$POSTGRES_DB" -c "SELECT 1;" > /dev/null 2>&1; then
            local end_time=$(date +%s%3N)
            local response_time=$(echo "scale=3; ($end_time - $start_time) / 1000" | bc)
            
            HEALTH_RESULTS["postgres"]="HEALTHY"
            HEALTH_DETAILS["postgres"]="Connection successful - Response time: ${response_time}s"
            HEALTH_RESPONSE_TIMES["postgres"]=$response_time
            log "SUCCESS" "PostgreSQL is healthy - ${response_time}s"
            return 0
        fi
    fi
    
    HEALTH_RESULTS["postgres"]="UNHEALTHY"
    HEALTH_DETAILS["postgres"]="Connection failed or timeout"
    HEALTH_RESPONSE_TIMES["postgres"]="timeout"
    log "ERROR" "PostgreSQL is unhealthy - connection failed"
    return 1
}

# Docker service health check
check_docker_service() {
    local service_name=$1
    
    log "INFO" "Checking Docker service: $service_name"
    
    if command -v docker &> /dev/null; then
        local container_status=$(docker ps --filter "name=$service_name" --format "{{.Status}}" 2>/dev/null)
        if [[ -n "$container_status" && "$container_status" =~ ^Up ]]; then
            HEALTH_RESULTS["docker_$service_name"]="HEALTHY"
            HEALTH_DETAILS["docker_$service_name"]="Container running: $container_status"
            log "SUCCESS" "Docker service $service_name is healthy"
            return 0
        else
            HEALTH_RESULTS["docker_$service_name"]="UNHEALTHY"
            HEALTH_DETAILS["docker_$service_name"]="Container not running or not found"
            log "ERROR" "Docker service $service_name is unhealthy"
            return 1
        fi
    else
        HEALTH_RESULTS["docker_$service_name"]="UNKNOWN"
        HEALTH_DETAILS["docker_$service_name"]="Docker not available"
        log "WARNING" "Docker not available, cannot check $service_name"
        return 1
    fi
}

# WebSocket health check
check_websocket() {
    local ws_url=${1:-"ws://localhost:8000/ws/"}
    
    log "INFO" "Checking WebSocket at $ws_url"
    
    # Use a simple Python script to test WebSocket
    local ws_test_result=$(python3 -c "
import asyncio
import websockets
import json
import sys
from datetime import datetime

async def test_websocket():
    try:
        start_time = datetime.now()
        async with websockets.connect('$ws_url', timeout=10) as websocket:
            await websocket.send(json.dumps({'type': 'ping', 'timestamp': str(start_time)}))
            response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
            end_time = datetime.now()
            response_time = (end_time - start_time).total_seconds()
            print(f'SUCCESS:{response_time}')
    except Exception as e:
        print(f'ERROR:{str(e)}')

asyncio.run(test_websocket())
" 2>/dev/null || echo "ERROR:Python WebSocket test failed")

    if [[ "$ws_test_result" =~ ^SUCCESS:([0-9.]+)$ ]]; then
        local response_time="${BASH_REMATCH[1]}"
        HEALTH_RESULTS["websocket"]="HEALTHY"
        HEALTH_DETAILS["websocket"]="WebSocket connection successful - Response time: ${response_time}s"
        HEALTH_RESPONSE_TIMES["websocket"]=$response_time
        log "SUCCESS" "WebSocket is healthy - ${response_time}s"
        return 0
    else
        HEALTH_RESULTS["websocket"]="UNHEALTHY"
        HEALTH_DETAILS["websocket"]="WebSocket connection failed: $ws_test_result"
        HEALTH_RESPONSE_TIMES["websocket"]="timeout"
        log "ERROR" "WebSocket is unhealthy - $ws_test_result"
        return 1
    fi
}

# Disk space check
check_disk_space() {
    local threshold=${1:-80}  # Default 80% threshold
    
    log "INFO" "Checking disk space (threshold: ${threshold}%)"
    
    local disk_usage=$(df / | awk 'NR==2 {print $5}' | sed 's/%//')
    
    if [[ $disk_usage -lt $threshold ]]; then
        HEALTH_RESULTS["disk_space"]="HEALTHY"
        HEALTH_DETAILS["disk_space"]="Disk usage: ${disk_usage}% (threshold: ${threshold}%)"
        log "SUCCESS" "Disk space is healthy - ${disk_usage}% used"
        return 0
    else
        HEALTH_RESULTS["disk_space"]="WARNING"
        HEALTH_DETAILS["disk_space"]="Disk usage: ${disk_usage}% (threshold: ${threshold}%)"
        log "WARNING" "Disk space is high - ${disk_usage}% used"
        return 1
    fi
}

# Memory usage check
check_memory_usage() {
    local threshold=${1:-80}  # Default 80% threshold
    
    log "INFO" "Checking memory usage (threshold: ${threshold}%)"
    
    local memory_usage=$(free | awk 'NR==2{printf "%.0f", $3*100/$2}')
    
    if [[ $memory_usage -lt $threshold ]]; then
        HEALTH_RESULTS["memory_usage"]="HEALTHY"
        HEALTH_DETAILS["memory_usage"]="Memory usage: ${memory_usage}% (threshold: ${threshold}%)"
        log "SUCCESS" "Memory usage is healthy - ${memory_usage}% used"
        return 0
    else
        HEALTH_RESULTS["memory_usage"]="WARNING"
        HEALTH_DETAILS["memory_usage"]="Memory usage: ${memory_usage}% (threshold: ${threshold}%)"
        log "WARNING" "Memory usage is high - ${memory_usage}% used"
        return 1
    fi
}

# Generate JSON output
output_json() {
    local timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    local overall_status="HEALTHY"
    
    # Determine overall status
    for service in "${!HEALTH_RESULTS[@]}"; do
        if [[ "${HEALTH_RESULTS[$service]}" == "UNHEALTHY" ]]; then
            overall_status="UNHEALTHY"
            break
        elif [[ "${HEALTH_RESULTS[$service]}" == "WARNING" && "$overall_status" != "UNHEALTHY" ]]; then
            overall_status="WARNING"
        fi
    done
    
    echo "{"
    echo "  \"timestamp\": \"$timestamp\","
    echo "  \"overall_status\": \"$overall_status\","
    echo "  \"services\": {"
    
    local first=true
    for service in "${!HEALTH_RESULTS[@]}"; do
        if [[ $first == false ]]; then
            echo ","
        fi
        echo -n "    \"$service\": {"
        echo -n "\"status\": \"${HEALTH_RESULTS[$service]}\", "
        echo -n "\"details\": \"${HEALTH_DETAILS[$service]}\", "
        echo -n "\"response_time\": \"${HEALTH_RESPONSE_TIMES[$service]}\""
        echo -n "}"
        first=false
    done
    
    echo ""
    echo "  }"
    echo "}"
}

# Generate Prometheus metrics output
output_prometheus() {
    echo "# HELP unified_service_health Health status of unified services (1=healthy, 0=unhealthy)"
    echo "# TYPE unified_service_health gauge"
    
    for service in "${!HEALTH_RESULTS[@]}"; do
        local value=0
        [[ "${HEALTH_RESULTS[$service]}" == "HEALTHY" ]] && value=1
        echo "unified_service_health{service=\"$service\"} $value"
    done
    
    echo "# HELP unified_service_response_time Response time of unified services in seconds"
    echo "# TYPE unified_service_response_time gauge"
    
    for service in "${!HEALTH_RESPONSE_TIMES[@]}"; do
        local response_time="${HEALTH_RESPONSE_TIMES[$service]}"
        if [[ "$response_time" != "timeout" && "$response_time" != "" ]]; then
            echo "unified_service_response_time{service=\"$service\"} $response_time"
        fi
    done
}

# Main health check function
main() {
    local failed_checks=0
    
    log "INFO" "Starting Unified Donkey Betz Platform Health Check"
    log "INFO" "Timeout: ${TIMEOUT}s, Output Format: $OUTPUT_FORMAT"
    
    # Infrastructure checks
    check_redis || ((failed_checks++))
    check_postgres || ((failed_checks++))
    
    # Application services
    check_http_service "backend" "$BACKEND_URL" "200" "/health" || ((failed_checks++))
    check_http_service "frontend" "$FRONTEND_URL" "200" "/health" || ((failed_checks++))
    check_http_service "mobile" "$MOBILE_URL" "200" "/health" || ((failed_checks++))
    
    # WebSocket check
    check_websocket || ((failed_checks++))
    
    # System resource checks
    check_disk_space 80 || ((failed_checks++))
    check_memory_usage 80 || ((failed_checks++))
    
    # Docker service checks (if Docker is available)
    if command -v docker &> /dev/null; then
        check_docker_service "unified-backend" || ((failed_checks++))
        check_docker_service "unified-frontend" || ((failed_checks++))
        check_docker_service "unified-postgres" || ((failed_checks++))
        check_docker_service "unified-redis" || ((failed_checks++))
    fi
    
    # Output results
    case $OUTPUT_FORMAT in
        "json")
            output_json
            ;;
        "prometheus")
            output_prometheus
            ;;
        "text"|*)
            echo
            log "INFO" "Health Check Summary:"
            echo "======================================"
            for service in "${!HEALTH_RESULTS[@]}"; do
                local status="${HEALTH_RESULTS[$service]}"
                local details="${HEALTH_DETAILS[$service]}"
                case $status in
                    "HEALTHY")
                        echo -e "${GREEN}✅ $service${NC}: $details"
                        ;;
                    "WARNING")
                        echo -e "${YELLOW}⚠️  $service${NC}: $details"
                        ;;
                    "UNHEALTHY"|"UNKNOWN")
                        echo -e "${RED}❌ $service${NC}: $details"
                        ;;
                esac
            done
            echo "======================================"
            
            if [[ $failed_checks -eq 0 ]]; then
                log "SUCCESS" "All health checks passed! Platform is healthy."
                exit 0
            else
                log "ERROR" "$failed_checks health check(s) failed! Platform needs attention."
                exit 1
            fi
            ;;
    esac
}

# Handle command line arguments
case "${1:-}" in
    "--json"|"-j")
        OUTPUT_FORMAT="json"
        ;;
    "--prometheus"|"-p")
        OUTPUT_FORMAT="prometheus"
        ;;
    "--verbose"|"-v")
        VERBOSE="true"
        ;;
    "--help"|"-h")
        echo "Unified Donkey Betz Platform Health Check Script"
        echo ""
        echo "Usage: $0 [OPTIONS]"
        echo ""
        echo "Options:"
        echo "  --json, -j          Output results in JSON format"
        echo "  --prometheus, -p    Output results in Prometheus metrics format"
        echo "  --verbose, -v       Enable verbose output"
        echo "  --help, -h          Show this help message"
        echo ""
        echo "Environment Variables:"
        echo "  TIMEOUT             Health check timeout in seconds (default: 30)"
        echo "  BACKEND_URL         Backend service URL (default: http://localhost:8000)"
        echo "  FRONTEND_URL        Frontend service URL (default: http://localhost:3000)"
        echo "  REDIS_HOST          Redis host (default: localhost)"
        echo "  REDIS_PORT          Redis port (default: 6379)"
        echo "  POSTGRES_HOST       PostgreSQL host (default: localhost)"
        echo "  POSTGRES_PORT       PostgreSQL port (default: 5432)"
        echo ""
        exit 0
        ;;
esac

# Run main function
main