# Monitoring and Alerting for Eternia

This document describes the monitoring and alerting setup for the Eternia project. It covers the tools used, the metrics collected, the alerts configured, and how to use the monitoring system.

## Overview

The Eternia monitoring system uses the following components:

- **Prometheus**: For metrics collection and alerting
- **Alertmanager**: For alert routing and notification
- **Grafana**: For metrics visualization and dashboards
- **Node Exporter**: For host metrics collection
- **cAdvisor**: For container metrics collection
- **Prometheus Client Library**: For application metrics instrumentation

The monitoring system is designed to provide visibility into the health and performance of the Eternia application and its infrastructure. It also provides alerting capabilities to notify operators of potential issues.

## Architecture

The monitoring architecture follows the standard Prometheus architecture:

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Eternia        │     │  Node Exporter  │     │  cAdvisor       │
│  Application    │     │                 │     │                 │
└────────┬────────┘     └────────┬────────┘     └────────┬────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                          Prometheus                             │
└────────────────────────────────┬──────────────────────────────┬─┘
                                 │                              │
                                 ▼                              ▼
                     ┌─────────────────────┐        ┌─────────────────┐
                     │     Alertmanager    │        │     Grafana     │
                     └─────────────────────┘        └─────────────────┘
                                 │
                                 ▼
                     ┌─────────────────────┐
                     │   Notifications     │
                     │  (Email, Slack)     │
                     └─────────────────────┘
```

## Metrics Collection

### Application Metrics

The Eternia application exposes metrics via the `/metrics` endpoint. These metrics include:

- **HTTP Metrics**:
  - `http_requests_total`: Total number of HTTP requests (labeled by method, endpoint, and status)
  - `http_request_duration_seconds`: HTTP request duration in seconds (labeled by method and endpoint)

- **Simulation Metrics**:
  - `simulation_step_duration_seconds`: Simulation step duration in seconds
  - `simulation_steps_total`: Total number of simulation steps
  - `simulation_entities`: Number of entities in the simulation (labeled by type)

- **Governor Metrics**:
  - `governor_interventions_total`: Total number of governor interventions (labeled by type and reason)
  - `governor_state`: Current state of the governor (labeled by state)

- **System Metrics**:
  - `system_memory_usage_bytes`: Memory usage in bytes

- **API Metrics**:
  - `api_requests_in_flight`: Number of API requests currently being processed
  - `api_request_latency_seconds`: API request latency in seconds (labeled by method and endpoint)

### Host Metrics

Node Exporter collects host metrics, including:

- CPU usage
- Memory usage
- Disk usage
- Network traffic
- System load

### Container Metrics

cAdvisor collects container metrics, including:

- CPU usage
- Memory usage
- Network traffic
- Disk I/O

## Alerting

Alerts are configured in Prometheus and routed through Alertmanager. The following alerts are configured:

- **HighCPUUsage**: Alerts when CPU usage is above 80% for 5 minutes
- **HighMemoryUsage**: Alerts when memory usage is above 80% for 5 minutes
- **DiskSpaceRunningOut**: Alerts when disk space is below 10% for 5 minutes
- **ServiceDown**: Alerts when a service is down for 1 minute
- **HighHTTPErrorRate**: Alerts when HTTP error rate is above 5% for 5 minutes
- **SlowHTTPResponseTime**: Alerts when HTTP response time is above 1 second for 5 minutes

Alerts are routed to different notification channels based on their severity:

- **Critical Alerts**: Sent to the ops-team-pager channel (email, Slack, and PagerDuty)
- **Warning Alerts**: Sent to the ops-team channel (email and Slack)

## Dashboards

Grafana dashboards are provided for visualizing metrics. The following dashboards are available:

- **Eternia Overview**: Provides an overview of the Eternia application, including CPU usage, memory usage, HTTP request rate, and HTTP error rate.

## Setup and Configuration

### Prerequisites

- Docker and Docker Compose installed
- Eternia application running

### Starting the Monitoring Stack

To start the monitoring stack, run:

```bash
docker-compose --profile monitoring up -d
```

This will start Prometheus, Alertmanager, Grafana, Node Exporter, and cAdvisor.

### Accessing the Monitoring Tools

- **Prometheus**: http://localhost:9090
- **Alertmanager**: http://localhost:9093
- **Grafana**: http://localhost:3000 (default credentials: admin/admin)

### Configuration Files

The monitoring configuration files are located in the `monitoring` directory:

- **Prometheus**: `monitoring/prometheus/prometheus.yml`
- **Alertmanager**: `monitoring/alertmanager/alertmanager.yml`
- **Grafana**: `monitoring/grafana/grafana.ini`

## Using the Monitoring System

### Viewing Metrics

1. Open Grafana at http://localhost:3000
2. Log in with the default credentials (admin/admin)
3. Navigate to the Eternia Overview dashboard

### Viewing Alerts

1. Open Alertmanager at http://localhost:9093
2. View active alerts and their status

### Querying Metrics

1. Open Prometheus at http://localhost:9090
2. Use the query interface to explore metrics

## Extending the Monitoring System

### Adding New Metrics

To add new metrics to the application:

1. Add the metric to the `EterniaMetrics` class in `modules/monitoring.py`
2. Use the metric in the appropriate part of the application

### Adding New Alerts

To add new alerts:

1. Add the alert rule to `monitoring/prometheus/alert_rules.yml`
2. Restart Prometheus

### Adding New Dashboards

To add new dashboards:

1. Create the dashboard in Grafana
2. Export the dashboard to JSON
3. Save the JSON file in `monitoring/grafana/provisioning/dashboards/`
4. Update the dashboard provisioning configuration if necessary

## Troubleshooting

### Common Issues

- **Prometheus can't scrape metrics**: Check that the `/metrics` endpoint is accessible and returning data
- **Alerts not firing**: Check the alert rules in Prometheus and the alert status
- **Grafana can't connect to Prometheus**: Check the Prometheus data source configuration in Grafana

### Logs

- **Prometheus**: Check the Prometheus container logs
- **Alertmanager**: Check the Alertmanager container logs
- **Grafana**: Check the Grafana container logs

## Conclusion

The monitoring and alerting system provides comprehensive visibility into the Eternia application and its infrastructure. It helps operators detect and respond to issues quickly, ensuring the reliability and performance of the application.