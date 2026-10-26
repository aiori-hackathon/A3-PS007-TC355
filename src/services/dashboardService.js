/**
 * Dashboard Data Helper Service
 */
import { api } from './api';

export const dashboardService = {
  async fetchOverview(tenantId) {
    const [dashboardData, trafficData, alertData] = await Promise.all([
      api.getDashboard(tenantId),
      api.getTrafficAnalytics(tenantId).catch(() => ({ data: { normal_events: 0, suspicious_events: 0, time_series: [] } })),
      api.getAlertAnalytics(tenantId).catch(() => ({ data: { by_severity: [], by_category: [] } }))
    ]);

    return {
      summary: dashboardData.summary || {},
      monitoringActive: dashboardData.monitoring_active ?? true,
      recentAlerts: dashboardData.recent_alerts || [],
      recentEvents: dashboardData.recent_events || [],
      traffic: trafficData.data || {},
      alertsMeta: alertData.data || {}
    };
  }
};
