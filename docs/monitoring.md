# Monitoring and Alerting Documentation for Eternia

This document explains the monitoring and alerting system set up for the Eternia project.

## Overview

The Eternia monitoring system consists of three main components:

1. **Prometheus**: Collects and stores metrics from the application and infrastructure
2. **Grafana**: Visualizes metrics in dashboards
3. **AlertManager**: Manages alerts and notifications

These components work together to provide comprehensive monitoring and alerting for the Eternia application.

## Architecture

The monitoring system is deployed in Kubernetes in a dedicated `monitoring` namespace. The components are:

- **Prometheus**: Scrapes metrics from various sources, evaluates alert rules, and sends alerts to AlertManager
- **Grafana**: Connects to Prometheus as a data source and displays metrics in dashboards
- **AlertManager**: Receives alerts from Prometheus, groups them, and sends notifications

## Accessing the Monitoring Tools

### Prometheus

Prometheus is available at:
- URL: `https://prometheus.eternia.example.com` (in production)
- Internal: `http://prometheus.monitoring.svc.cluster.local:9090` (within the cluster)

### Grafana

Grafana is available at:
- URL: `https://grafana.eternia.example.com` (in production)
- Default credentials: See the `grafana-credentials` secret in the `monitoring` namespace

### AlertManager

AlertManager is available at:
- URL: `https://alertmanager.eternia.example.com` (in production)
- Internal: `http://alertmanager.monitoring.svc.cluster.local:9093` (within the cluster)

## Metrics Collection

### Application Metrics

The Eternia backend exposes metrics at the `/metrics` endpoint. These metrics include:

- HTTP request counts and durations
- Error rates
- Application-specific metrics

To add new application metrics:

1. Add the metric to the application code
2. Ensure the metric is exposed at the `/metrics` endpoint
3. Prometheus will automatically scrape the new metric

### Infrastructure Metrics

Prometheus collects infrastructure metrics from:

- Kubernetes API server
- Kubernetes nodes
- Kubernetes pods
- Container metrics (CPU, memory, etc.)

## Dashboards

### Default Dashboards

The following dashboards are available in Grafana:

1. **Eternia Overview**: Shows high-level metrics like request rates and response times
2. **Kubernetes Cluster**: Shows cluster-level metrics
3. **Node Metrics**: Shows metrics for individual nodes
4. **Container Metrics**: Shows metrics for individual containers

### Creating Custom Dashboards

To create a custom dashboard:

1. Log in to Grafana
2. Click "Create" > "Dashboard"
3. Add panels with PromQL queries
4. Save the dashboard

To export a dashboard to version control:

1. Click the "Share" button on the dashboard
2. Select the "Export" tab
3. Save the JSON file to `kubernetes/monitoring/dashboards/`
4. Update the `grafana-dashboards` ConfigMap

## Alerting

### Alert Rules

Alert rules are defined in the `prometheus-alert-rules` ConfigMap. The default rules include:

- **HighRequestLatency**: Triggers when the 90th percentile of request latency is above 1 second for 5 minutes
- **APIHighErrorRate**: Triggers when the error rate is above 5% for 5 minutes
- **InstanceDown**: Triggers when an instance is down for 5 minutes
- **HighMemoryUsage**: Triggers when a container is using more than 85% of its memory limit for 5 minutes
- **HighCPUUsage**: Triggers when a container is using more than 85% of its CPU limit for 5 minutes

### Adding New Alert Rules

To add a new alert rule:

1. Edit the `prometheus-alert-rules` ConfigMap
2. Add a new rule to the `eternia-alerts` group
3. Apply the changes with `kubectl apply -f kubernetes/monitoring/30-alertmanager.yaml`

Example alert rule:

```yaml
- alert: DatabaseConnectionsHigh
  expr: pg_stat_activity_count > 100
  for: 5m
  labels:
    severity: warning
  annotations:
    summary: "High database connections"
    description: "Database has more than 100 connections for 5 minutes."
```

### Notification Channels

Alerts are sent to the following channels:

- **Slack**: Alerts are sent to the `#eternia-alerts` channel
- **Email**: Critical alerts can be configured to be sent via email

To configure Slack notifications:

1. Create a Slack webhook URL
2. Update the `slack_api_url` in the `alertmanager-config` ConfigMap
3. Apply the changes with `kubectl apply -f kubernetes/monitoring/30-alertmanager.yaml`

## Maintenance

### Updating Prometheus

To update Prometheus:

1. Edit the Prometheus Deployment to use a new image version
2. Apply the changes with `kubectl apply -f kubernetes/monitoring/10-prometheus.yaml`

### Updating Grafana

To update Grafana:

1. Edit the Grafana Deployment to use a new image version
2. Apply the changes with `kubectl apply -f kubernetes/monitoring/20-grafana.yaml`

### Updating AlertManager

To update AlertManager:

1. Edit the AlertManager Deployment to use a new image version
2. Apply the changes with `kubectl apply -f kubernetes/monitoring/30-alertmanager.yaml`

## Troubleshooting

### Common Issues

1. **Prometheus not scraping metrics**:
   - Check the Prometheus targets page at `/targets`
   - Ensure the service has the correct annotations
   - Check network policies

2. **Alerts not firing**:
   - Check the Prometheus rules page at `/rules`
   - Verify the alert expression with the Prometheus expression browser
   - Check the AlertManager status

3. **Grafana not showing data**:
   - Verify the Prometheus data source is configured correctly
   - Check the Grafana logs
   - Test the data source connection in Grafana

### Viewing Logs

To view logs for the monitoring components:

```bash
# Prometheus logs
kubectl logs -f deployment/prometheus -n monitoring

# Grafana logs
kubectl logs -f deployment/grafana -n monitoring

# AlertManager logs
kubectl logs -f deployment/alertmanager -n monitoring
```

## Best Practices

1. **Keep alert rules actionable**: Only create alerts for conditions that require human intervention
2. **Use appropriate severity levels**: Use "critical" for issues that need immediate attention
3. **Include clear descriptions**: Alert descriptions should explain what's happening and suggest actions
4. **Test alert rules**: Verify that alert rules work as expected before deploying to production
5. **Monitor the monitors**: Set up alerts for the monitoring system itself
6. **Version control dashboards**: Export important dashboards to version control
7. **Document custom metrics**: Keep documentation of custom metrics up to date