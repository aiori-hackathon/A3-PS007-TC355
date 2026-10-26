import express, { Request, Response } from 'express';
import { execFile } from 'child_process';
import path from 'path';
import fs from 'fs';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
const PORT = 3000;

app.use(express.json());

// Helper function to invoke Python bridge
function callPythonBridge(action: string, args: Record<string, any> = {}): Promise<any> {
  return new Promise((resolve, reject) => {
    const bridgePath = path.join(__dirname, 'backend', 'bridge.py');
    const argsJson = JSON.stringify(args);

    execFile('python', [bridgePath, action, argsJson], { maxBuffer: 10 * 1024 * 1024 }, (error, stdout, stderr) => {
      if (error) {
        console.error(`Bridge error on [${action}]:`, stderr || error.message);
        return reject(error);
      }
      try {
        const parsed = JSON.parse(stdout.trim());
        resolve(parsed);
      } catch (parseErr) {
        console.error('Failed to parse bridge output:', stdout);
        reject(parseErr);
      }
    });
  });
}

// ========================================================
// REST API ROUTES
// ========================================================

// 1. General & Health
app.get('/api/health', async (_req: Request, res: Response) => {
  try {
    const out = await callPythonBridge('health');
    res.json(out);
  } catch (err: any) {
    res.status(500).json({ status: 'unhealthy', error: err.message });
  }
});

app.get('/api/dashboard', async (req: Request, res: Response) => {
  try {
    const tenant_id = (req.query.tenant_id as string) || 'tenant-alpha';
    const out = await callPythonBridge('get_dashboard', { tenant_id });
    res.json(out);
  } catch (err: any) {
    res.status(500).json({ success: false, error: err.message });
  }
});

// 2. Devices
app.get('/api/devices', async (req: Request, res: Response) => {
  try {
    const tenant_id = (req.query.tenant_id as string) || 'tenant-alpha';
    const out = await callPythonBridge('get_devices', { tenant_id });
    res.json(out);
  } catch (err: any) {
    res.status(500).json({ success: false, error: err.message });
  }
});

app.get('/api/devices/:device_id/events', async (req: Request, res: Response) => {
  try {
    const tenant_id = (req.query.tenant_id as string) || 'tenant-alpha';
    const out = await callPythonBridge('get_device_events', {
      device_id: req.params.device_id,
      tenant_id
    });
    res.json(out);
  } catch (err: any) {
    res.status(500).json({ success: false, error: err.message });
  }
});

app.post('/api/devices/:device_id/rotate-address', async (req: Request, res: Response) => {
  try {
    const tenant_id = req.body?.tenant_id || (req.query.tenant_id as string) || 'tenant-alpha';
    const out = await callPythonBridge('rotate_address', {
      device_id: req.params.device_id,
      tenant_id
    });
    res.json(out);
  } catch (err: any) {
    res.status(500).json({ success: false, error: err.message });
  }
});

app.post('/api/devices/:device_id/connect', async (req: Request, res: Response) => {
  try {
    const tenant_id = req.body?.tenant_id || (req.query.tenant_id as string) || 'tenant-alpha';
    const out = await callPythonBridge('connect_device', {
      device_id: req.params.device_id,
      tenant_id
    });
    res.json(out);
  } catch (err: any) {
    res.status(500).json({ success: false, error: err.message });
  }
});

app.post('/api/devices/:device_id/disconnect', async (req: Request, res: Response) => {
  try {
    const tenant_id = req.body?.tenant_id || (req.query.tenant_id as string) || 'tenant-alpha';
    const out = await callPythonBridge('disconnect_device', {
      device_id: req.params.device_id,
      tenant_id
    });
    res.json(out);
  } catch (err: any) {
    res.status(500).json({ success: false, error: err.message });
  }
});

// 3. Monitoring
app.get('/api/monitoring/status', async (req: Request, res: Response) => {
  try {
    const tenant_id = (req.query.tenant_id as string) || 'tenant-alpha';
    const out = await callPythonBridge('get_monitoring_status', { tenant_id });
    res.json(out);
  } catch (err: any) {
    res.status(500).json({ success: false, error: err.message });
  }
});

app.post('/api/monitoring/start', async (_req: Request, res: Response) => {
  try {
    const out = await callPythonBridge('start_monitoring');
    res.json(out);
  } catch (err: any) {
    res.status(500).json({ success: false, error: err.message });
  }
});

app.post('/api/monitoring/stop', async (_req: Request, res: Response) => {
  try {
    const out = await callPythonBridge('stop_monitoring');
    res.json(out);
  } catch (err: any) {
    res.status(500).json({ success: false, error: err.message });
  }
});

// 4. Simulation
app.post('/api/simulation/normal-traffic', async (req: Request, res: Response) => {
  try {
    const tenant_id = req.body?.tenant_id || 'tenant-alpha';
    const count = req.body?.count || 5;
    const out = await callPythonBridge('simulate_normal_traffic', { tenant_id, count });
    res.json(out);
  } catch (err: any) {
    res.status(500).json({ success: false, error: err.message });
  }
});

app.post('/api/simulation/rogue-ra', async (req: Request, res: Response) => {
  try {
    const tenant_id = req.body?.tenant_id || 'tenant-alpha';
    const source_ipv6 = req.body?.source_ipv6 || 'fe80::dead:beef:666';
    const advertised_prefix = req.body?.advertised_prefix || '2001:db8:evil::/64';
    const out = await callPythonBridge('simulate_rogue_ra', {
      tenant_id,
      source_ipv6,
      advertised_prefix
    });
    res.json(out);
  } catch (err: any) {
    res.status(500).json({ success: false, error: err.message });
  }
});

app.post('/api/simulation/ndp-anomaly', async (req: Request, res: Response) => {
  try {
    const tenant_id = req.body?.tenant_id || 'tenant-alpha';
    const burst_count = req.body?.burst_count || 55;
    const pseudonym = req.body?.pseudonym;
    const out = await callPythonBridge('simulate_ndp_anomaly', {
      tenant_id,
      burst_count,
      pseudonym
    });
    res.json(out);
  } catch (err: any) {
    res.status(500).json({ success: false, error: err.message });
  }
});

app.post('/api/simulation/reset', async (_req: Request, res: Response) => {
  try {
    const out = await callPythonBridge('reset_demo');
    res.json(out);
  } catch (err: any) {
    res.status(500).json({ success: false, error: err.message });
  }
});

// 5. Alerts
app.get('/api/alerts', async (req: Request, res: Response) => {
  try {
    const tenant_id = (req.query.tenant_id as string) || 'tenant-alpha';
    const severity = req.query.severity as string;
    const category = req.query.category as string;
    const out = await callPythonBridge('get_alerts', { tenant_id, severity, category });
    res.json(out);
  } catch (err: any) {
    res.status(500).json({ success: false, error: err.message });
  }
});

app.post('/api/alerts/:alert_id/acknowledge', async (req: Request, res: Response) => {
  try {
    const alert_id = req.params.alert_id;
    const tenant_id = req.body?.tenant_id || 'tenant-alpha';
    const analyst = req.body?.analyst || 'SOC-Analyst-1';
    const out = await callPythonBridge('acknowledge_alert', { alert_id, tenant_id, analyst });
    res.json(out);
  } catch (err: any) {
    res.status(500).json({ success: false, error: err.message });
  }
});

// 6. Privacy
app.get('/api/privacy/status', async (req: Request, res: Response) => {
  try {
    const tenant_id = (req.query.tenant_id as string) || 'tenant-alpha';
    const out = await callPythonBridge('get_privacy_status', { tenant_id });
    res.json(out);
  } catch (err: any) {
    res.status(500).json({ success: false, error: err.message });
  }
});

app.get('/api/privacy/pseudonyms', async (req: Request, res: Response) => {
  try {
    const tenant_id = (req.query.tenant_id as string) || 'tenant-alpha';
    const out = await callPythonBridge('get_pseudonyms', { tenant_id });
    res.json(out);
  } catch (err: any) {
    res.status(500).json({ success: false, error: err.message });
  }
});

app.post('/api/privacy/pseudonyms/expire', async (req: Request, res: Response) => {
  try {
    const tenant_id = req.body?.tenant_id || 'tenant-alpha';
    const pseudonym = req.body?.pseudonym;
    if (!pseudonym) {
      return res.status(400).json({ success: false, error: 'pseudonym is required' });
    }
    const out = await callPythonBridge('expire_pseudonym', { tenant_id, pseudonym });
    res.json(out);
  } catch (err: any) {
    res.status(500).json({ success: false, error: err.message });
  }
});

app.get('/api/privacy/sessions', async (req: Request, res: Response) => {
  try {
    const tenant_id = (req.query.tenant_id as string) || 'tenant-alpha';
    const out = await callPythonBridge('get_sessions', { tenant_id });
    res.json(out);
  } catch (err: any) {
    res.status(500).json({ success: false, error: err.message });
  }
});

app.post('/api/privacy/sessions/revoke', async (req: Request, res: Response) => {
  try {
    const tenant_id = req.body?.tenant_id || 'tenant-alpha';
    const session_id = req.body?.session_id;
    if (!session_id) {
      return res.status(400).json({ success: false, error: 'session_id is required' });
    }
    const out = await callPythonBridge('revoke_session', { tenant_id, session_id });
    res.json(out);
  } catch (err: any) {
    res.status(500).json({ success: false, error: err.message });
  }
});

// 7. Analytics
app.get('/api/analytics/traffic', async (req: Request, res: Response) => {
  try {
    const tenant_id = (req.query.tenant_id as string) || 'tenant-alpha';
    const out = await callPythonBridge('get_traffic', { tenant_id });
    res.json(out);
  } catch (err: any) {
    res.status(500).json({ success: false, error: err.message });
  }
});

app.get('/api/analytics/alerts', async (req: Request, res: Response) => {
  try {
    const tenant_id = (req.query.tenant_id as string) || 'tenant-alpha';
    const out = await callPythonBridge('get_alert_analytics', { tenant_id });
    res.json(out);
  } catch (err: any) {
    res.status(500).json({ success: false, error: err.message });
  }
});

app.get('/api/analytics/detection', async (req: Request, res: Response) => {
  try {
    const tenant_id = (req.query.tenant_id as string) || 'tenant-alpha';
    const out = await callPythonBridge('get_detection', { tenant_id });
    res.json(out);
  } catch (err: any) {
    res.status(500).json({ success: false, error: err.message });
  }
});

// 8. Evaluation
app.post('/api/evaluation/run', async (req: Request, res: Response) => {
  try {
    const tenant_id = req.body?.tenant_id || 'tenant-alpha';
    const out = await callPythonBridge('run_evaluation', { tenant_id });
    res.json(out);
  } catch (err: any) {
    res.status(500).json({ success: false, error: err.message });
  }
});

app.get('/api/evaluation/results', async (_req: Request, res: Response) => {
  try {
    const out = await callPythonBridge('get_evaluation_results');
    res.json(out);
  } catch (err: any) {
    res.status(500).json({ success: false, error: err.message });
  }
});

// 9. Settings
app.get('/api/settings', async (_req: Request, res: Response) => {
  try {
    const out = await callPythonBridge('get_settings');
    res.json(out);
  } catch (err: any) {
    res.status(500).json({ success: false, error: err.message });
  }
});

app.put('/api/settings', async (req: Request, res: Response) => {
  try {
    const out = await callPythonBridge('update_settings', req.body || {});
    res.json(out);
  } catch (err: any) {
    res.status(500).json({ success: false, error: err.message });
  }
});

// 10. Export ZIP Download Endpoint
app.get('/api/export-zip', (_req: Request, res: Response) => {
  const exportScript = path.join(__dirname, 'scripts', 'export_project_zip.py');
  execFile('python', [exportScript], (err) => {
    if (err) {
      return res.status(500).json({ error: 'Failed to build ZIP archive' });
    }
    const zipPath = path.join(__dirname, 'PrivacyGuard-IPv6.zip');
    res.download(zipPath, 'PrivacyGuard-IPv6.zip');
  });
});

// ========================================================
// VITE DEV SERVER / STATIC HANDLER
// ========================================================
async function startServer() {
  const isDev = process.env.NODE_ENV !== 'production';

  if (isDev) {
    const { createServer: createViteServer } = await import('vite');
    const vite = await createViteServer({
      server: { middlewareMode: true },
      appType: 'spa'
    });
    app.use(vite.middlewares);
  } else {
    app.use(express.static(path.join(__dirname, 'dist')));
    app.get('*', (_req, res) => {
      res.sendFile(path.join(__dirname, 'dist', 'index.html'));
    });
  }

  app.listen(PORT, '0.0.0.0', () => {
    console.log(`[PrivacyGuard IPv6] SOC Dashboard running at http://0.0.0.0:${PORT}`);
  });
}

startServer().catch((err) => {
  console.error('Failed to start server:', err);
});
