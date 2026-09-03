"use client";

import { useState, useEffect } from "react";

const API_BASE = "http://localhost:5000/api";

type Alert = {
  id: string;
  rule_id: string;
  rule_name: string;
  severity: "critical" | "high" | "warning" | "info";
  category: string;
  habitation_id: string;
  habitation_name: string;
  message: string;
  rpi: number | null;
  is_read: boolean;
  created_at: string;
};

type Notification = {
  id: string;
  alert_id: string;
  title: string;
  message: string;
  severity: "critical" | "high" | "warning" | "info";
  category: string;
  is_read: boolean;
  created_at: string;
};

type AlertRule = {
  id: string;
  name: string;
  description: string;
  severity: string;
  category: string;
};

type Summary = {
  total_alerts: number;
  critical: number;
  high: number;
  warning: number;
  habitations_evaluated: number;
  rules_checked: number;
  generated_at: string;
};

const SEVERITY_STYLES: Record<string, { bg: string; border: string; badge: string; icon: string }> = {
  critical: { bg: "bg-red-50", border: "border-red-300", badge: "bg-red-600 text-white", icon: "🔴" },
  high: { bg: "bg-orange-50", border: "border-orange-300", badge: "bg-orange-500 text-white", icon: "🟠" },
  warning: { bg: "bg-yellow-50", border: "border-yellow-300", badge: "bg-yellow-500 text-white", icon: "🟡" },
  info: { bg: "bg-blue-50", border: "border-blue-300", badge: "bg-blue-500 text-white", icon: "🔵" },
};

export default function NotificationsPage() {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [rules, setRules] = useState<AlertRule[]>([]);
  const [summary, setSummary] = useState<Summary | null>(null);
  const [loading, setLoading] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState("");
  const [activeTab, setActiveTab] = useState<"alerts" | "notifications" | "rules">("alerts");
  const [filterSeverity, setFilterSeverity] = useState<string>("all");

  // Fetch existing data on mount
  useEffect(() => {
    fetchAlerts();
    fetchNotifications();
    fetchRules();
  }, []);

  const fetchAlerts = async () => {
    try {
      const res = await fetch(`${API_BASE}/alerts/list`);
      const data = await res.json();
      setAlerts(data.alerts || []);
    } catch { /* alerts not generated yet */ }
  };

  const fetchNotifications = async () => {
    try {
      const res = await fetch(`${API_BASE}/alerts/notifications`);
      const data = await res.json();
      setNotifications(data.notifications || []);
    } catch { /* notifications not generated yet */ }
  };

  const fetchRules = async () => {
    try {
      const res = await fetch(`${API_BASE}/alerts/rules`);
      const data = await res.json();
      setRules(data.rules || []);
    } catch { /* backend not available */ }
  };

  const generateAlerts = async () => {
    setGenerating(true);
    setError("");
    try {
      // Load habitation and hazard data
      const habRes = await fetch("/data/habitations.geojson");
      const habData = await habRes.json();
      const hazRes = await fetch("/data/hazards.geojson");
      const hazData = await hazRes.json();

      const habitations = habData.features.map((f: any) => ({
        ...f.properties,
        longitude: f.geometry.coordinates[0],
        latitude: f.geometry.coordinates[1],
        geom_geojson: JSON.stringify(f.geometry),
      }));

      const hazards = hazData.features.map((f: any) => ({
        ...f.properties,
        geom_geojson: JSON.stringify(f.geometry),
      }));

      const res = await fetch(`${API_BASE}/alerts/generate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ habitations, hazards }),
      });

      if (!res.ok) throw new Error("Alert generation failed");

      const data = await res.json();
      setAlerts(data.alerts || []);
      setNotifications(data.notifications || []);
      setSummary(data.summary || null);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setGenerating(false);
    }
  };

  const markAlertRead = async (alertId: string) => {
    await fetch(`${API_BASE}/alerts/${alertId}/read`, { method: "PATCH" });
    setAlerts((prev) => prev.map((a) => (a.id === alertId ? { ...a, is_read: true } : a)));
  };

  const markNotificationRead = async (notifId: string) => {
    await fetch(`${API_BASE}/alerts/notifications/${notifId}/read`, { method: "PATCH" });
    setNotifications((prev) => prev.map((n) => (n.id === notifId ? { ...n, is_read: true } : n)));
  };

  const markAllRead = async () => {
    await fetch(`${API_BASE}/alerts/notifications/read-all`, { method: "PATCH" });
    setNotifications((prev) => prev.map((n) => ({ ...n, is_read: true })));
  };

  const filteredAlerts = filterSeverity === "all" ? alerts : alerts.filter((a) => a.severity === filterSeverity);
  const unreadCount = notifications.filter((n) => !n.is_read).length;

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      {/* Page Header */}
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Alerts & Notification Center</h1>
          <p className="text-gray-600 mt-1">
            Rule-based alert engine monitoring habitation risk thresholds. Generate, view, and manage system alerts.
          </p>
        </div>
        <button
          onClick={generateAlerts}
          disabled={generating}
          className="bg-red-600 text-white px-5 py-2.5 rounded-lg font-semibold hover:bg-red-700 disabled:opacity-50 transition-colors shadow-sm flex items-center gap-2"
        >
          {generating ? (
            <>
              <span className="animate-spin">⚙</span> Running Engine...
            </>
          ) : (
            <>🔔 Run Alert Engine</>
          )}
        </button>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 p-4 rounded-lg">
          <strong>Error:</strong> {error}. Make sure the backend is running on <code>localhost:5000</code>.
        </div>
      )}

      {/* Summary Cards */}
      {summary && (
        <div className="grid grid-cols-5 gap-4">
          <div className="bg-white border rounded-lg p-4 shadow-sm">
            <div className="text-xs font-bold text-gray-500 uppercase">Total Alerts</div>
            <div className="text-3xl font-black text-gray-900 mt-1">{summary.total_alerts}</div>
          </div>
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 shadow-sm">
            <div className="text-xs font-bold text-red-600 uppercase">Critical</div>
            <div className="text-3xl font-black text-red-700 mt-1">{summary.critical}</div>
          </div>
          <div className="bg-orange-50 border border-orange-200 rounded-lg p-4 shadow-sm">
            <div className="text-xs font-bold text-orange-600 uppercase">High</div>
            <div className="text-3xl font-black text-orange-700 mt-1">{summary.high}</div>
          </div>
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 shadow-sm">
            <div className="text-xs font-bold text-yellow-600 uppercase">Warning</div>
            <div className="text-3xl font-black text-yellow-700 mt-1">{summary.warning}</div>
          </div>
          <div className="bg-white border rounded-lg p-4 shadow-sm">
            <div className="text-xs font-bold text-gray-500 uppercase">Villages Scanned</div>
            <div className="text-3xl font-black text-gray-900 mt-1">{summary.habitations_evaluated}</div>
          </div>
        </div>
      )}

      {/* Tab Navigation */}
      <div className="flex gap-1 bg-gray-100 p-1 rounded-lg w-fit">
        {[
          { key: "alerts" as const, label: "Alerts", count: alerts.length },
          { key: "notifications" as const, label: "Notifications", count: unreadCount > 0 ? unreadCount : notifications.length },
          { key: "rules" as const, label: "Engine Rules", count: rules.length },
        ].map((tab) => (
          <button
            key={tab.key}
            onClick={() => setActiveTab(tab.key)}
            className={`px-4 py-2 rounded-md text-sm font-semibold transition-colors flex items-center gap-2 ${
              activeTab === tab.key
                ? "bg-white text-gray-900 shadow-sm"
                : "text-gray-600 hover:text-gray-900"
            }`}
          >
            {tab.label}
            <span className={`text-[10px] px-1.5 py-0.5 rounded-full font-bold ${
              activeTab === tab.key
                ? tab.key === "notifications" && unreadCount > 0
                  ? "bg-red-600 text-white"
                  : "bg-gray-200 text-gray-700"
                : "bg-gray-200 text-gray-500"
            }`}>
              {tab.key === "notifications" && unreadCount > 0 ? `${unreadCount} new` : tab.count}
            </span>
          </button>
        ))}
      </div>

      {/* ─── ALERTS TAB ─── */}
      {activeTab === "alerts" && (
        <div className="bg-white border rounded-lg shadow-sm">
          <div className="bg-gray-50 border-b px-4 py-3 flex items-center justify-between">
            <h2 className="font-bold text-gray-800">System Alerts</h2>
            <div className="flex items-center gap-2">
              <span className="text-xs text-gray-500">Filter:</span>
              {["all", "critical", "high", "warning"].map((sev) => (
                <button
                  key={sev}
                  onClick={() => setFilterSeverity(sev)}
                  className={`text-xs px-3 py-1 rounded-full font-bold transition-colors ${
                    filterSeverity === sev
                      ? sev === "critical"
                        ? "bg-red-600 text-white"
                        : sev === "high"
                        ? "bg-orange-500 text-white"
                        : sev === "warning"
                        ? "bg-yellow-500 text-white"
                        : "bg-gray-900 text-white"
                      : "bg-gray-200 text-gray-600 hover:bg-gray-300"
                  }`}
                >
                  {sev.charAt(0).toUpperCase() + sev.slice(1)}
                </button>
              ))}
            </div>
          </div>
          <div className="divide-y max-h-[600px] overflow-y-auto">
            {filteredAlerts.length === 0 ? (
              <div className="p-10 text-center text-gray-500">
                <div className="text-4xl mb-2">🔕</div>
                <p className="font-semibold">No alerts generated yet</p>
                <p className="text-sm mt-1">Click &quot;Run Alert Engine&quot; to scan habitations against risk thresholds.</p>
              </div>
            ) : (
              filteredAlerts.map((alert) => {
                const style = SEVERITY_STYLES[alert.severity] || SEVERITY_STYLES.info;
                return (
                  <div
                    key={alert.id}
                    className={`p-4 flex items-start gap-3 transition-colors ${
                      alert.is_read ? "opacity-60" : style.bg
                    }`}
                  >
                    <span className="text-lg mt-0.5">{style.icon}</span>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <span className={`text-[10px] px-2 py-0.5 rounded-full font-bold uppercase ${style.badge}`}>
                          {alert.severity}
                        </span>
                        <span className="text-[10px] px-2 py-0.5 rounded-full font-bold bg-gray-200 text-gray-700 uppercase">
                          {alert.category}
                        </span>
                        <span className="text-xs text-gray-500 ml-auto">{alert.habitation_name}</span>
                      </div>
                      <p className="text-sm text-gray-900 font-medium">{alert.message}</p>
                      <div className="flex items-center gap-3 mt-2 text-xs text-gray-500">
                        <span>Rule: {alert.rule_name}</span>
                        {alert.rpi !== null && <span>RPI: {alert.rpi.toFixed(1)}</span>}
                      </div>
                    </div>
                    {!alert.is_read && (
                      <button
                        onClick={() => markAlertRead(alert.id)}
                        className="text-xs text-blue-600 hover:underline whitespace-nowrap mt-1"
                      >
                        Mark read
                      </button>
                    )}
                  </div>
                );
              })
            )}
          </div>
        </div>
      )}

      {/* ─── NOTIFICATIONS TAB ─── */}
      {activeTab === "notifications" && (
        <div className="bg-white border rounded-lg shadow-sm">
          <div className="bg-gray-50 border-b px-4 py-3 flex items-center justify-between">
            <h2 className="font-bold text-gray-800">
              Notifications
              {unreadCount > 0 && (
                <span className="ml-2 text-xs bg-red-600 text-white px-2 py-0.5 rounded-full font-bold">
                  {unreadCount} unread
                </span>
              )}
            </h2>
            {unreadCount > 0 && (
              <button
                onClick={markAllRead}
                className="text-xs text-blue-600 hover:underline font-semibold"
              >
                Mark all as read
              </button>
            )}
          </div>
          <div className="divide-y max-h-[600px] overflow-y-auto">
            {notifications.length === 0 ? (
              <div className="p-10 text-center text-gray-500">
                <div className="text-4xl mb-2">📭</div>
                <p className="font-semibold">No notifications</p>
                <p className="text-sm mt-1">Notifications will appear here after running the Alert Engine.</p>
              </div>
            ) : (
              notifications.map((notif) => {
                const style = SEVERITY_STYLES[notif.severity] || SEVERITY_STYLES.info;
                return (
                  <div
                    key={notif.id}
                    className={`p-4 flex items-start gap-3 cursor-pointer transition-colors hover:bg-gray-50 ${
                      notif.is_read ? "opacity-50" : ""
                    }`}
                    onClick={() => !notif.is_read && markNotificationRead(notif.id)}
                  >
                    <div className={`w-2 h-2 rounded-full mt-2 flex-shrink-0 ${notif.is_read ? "bg-gray-300" : "bg-blue-600"}`} />
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <span className="text-sm font-bold text-gray-900">{notif.title}</span>
                        <span className={`text-[10px] px-2 py-0.5 rounded-full font-bold uppercase ${style.badge}`}>
                          {notif.severity}
                        </span>
                      </div>
                      <p className="text-sm text-gray-600 mt-0.5">{notif.message}</p>
                    </div>
                  </div>
                );
              })
            )}
          </div>
        </div>
      )}

      {/* ─── RULES TAB ─── */}
      {activeTab === "rules" && (
        <div className="bg-white border rounded-lg shadow-sm">
          <div className="bg-gray-50 border-b px-4 py-3">
            <h2 className="font-bold text-gray-800">Configured Alert Rules</h2>
            <p className="text-xs text-gray-500 mt-0.5">
              These rules are evaluated against every habitation when the Alert Engine runs.
            </p>
          </div>
          <div className="p-4">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b text-xs uppercase text-gray-500">
                  <th className="text-left py-2">Rule ID</th>
                  <th className="text-left py-2">Name</th>
                  <th className="text-left py-2">Description</th>
                  <th className="text-center py-2">Severity</th>
                  <th className="text-center py-2">Category</th>
                </tr>
              </thead>
              <tbody>
                {rules.length === 0 ? (
                  <tr>
                    <td colSpan={5} className="py-8 text-center text-gray-500">
                      No rules loaded. Make sure the backend is running.
                    </td>
                  </tr>
                ) : (
                  rules.map((rule) => {
                    const style = SEVERITY_STYLES[rule.severity] || SEVERITY_STYLES.info;
                    return (
                      <tr key={rule.id} className="border-b last:border-b-0 hover:bg-gray-50 transition-colors">
                        <td className="py-2.5 font-mono text-xs text-gray-500">{rule.id}</td>
                        <td className="py-2.5 font-semibold text-gray-900">{rule.name}</td>
                        <td className="py-2.5 text-gray-600 text-xs">{rule.description}</td>
                        <td className="py-2.5 text-center">
                          <span className={`text-[10px] px-2 py-0.5 rounded-full font-bold uppercase ${style.badge}`}>
                            {rule.severity}
                          </span>
                        </td>
                        <td className="py-2.5 text-center">
                          <span className="text-[10px] px-2 py-0.5 rounded-full font-bold bg-gray-200 text-gray-700 uppercase">
                            {rule.category}
                          </span>
                        </td>
                      </tr>
                    );
                  })
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
