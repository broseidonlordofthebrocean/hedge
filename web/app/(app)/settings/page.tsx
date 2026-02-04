"use client";

import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

type Tab = "account" | "billing" | "notifications" | "api";

interface User {
  name: string;
  email: string;
  subscription_tier: string;
  api_calls_remaining: number;
  api_calls_total: number;
}

interface ApiKey {
  id: string;
  name: string;
  last_used: string | null;
  created_at: string;
}

export default function SettingsPage() {
  const [activeTab, setActiveTab] = useState<Tab>("account");
  const [user, setUser] = useState<User>({
    name: "John Doe",
    email: "john@example.com",
    subscription_tier: "pro",
    api_calls_remaining: 850,
    api_calls_total: 1000,
  });
  const [apiKeys, setApiKeys] = useState<ApiKey[]>([
    {
      id: "1",
      name: "Production App",
      last_used: "2024-06-15T10:30:00Z",
      created_at: "2024-01-15T08:00:00Z",
    },
  ]);
  const [notifications, setNotifications] = useState({
    email_alerts: true,
    push_alerts: false,
    weekly_digest: true,
    score_changes: true,
    threshold_alerts: true,
  });

  const [newKeyName, setNewKeyName] = useState("");
  const [showNewKey, setShowNewKey] = useState<string | null>(null);

  const createApiKey = () => {
    if (!newKeyName.trim()) return;

    const newKey: ApiKey = {
      id: Date.now().toString(),
      name: newKeyName,
      last_used: null,
      created_at: new Date().toISOString(),
    };

    setApiKeys((prev) => [...prev, newKey]);
    setNewKeyName("");
    setShowNewKey(`hedge_${Math.random().toString(36).substring(2, 34)}`);
  };

  const revokeApiKey = (id: string) => {
    setApiKeys((prev) => prev.filter((key) => key.id !== id));
  };

  const tabs: { id: Tab; label: string }[] = [
    { id: "account", label: "Account" },
    { id: "billing", label: "Billing" },
    { id: "notifications", label: "Notifications" },
    { id: "api", label: "API Keys" },
  ];

  return (
    <div className="min-h-screen bg-charcoal">
      {/* Header */}
      <div className="border-b border-charcoal-light p-6">
        <div className="max-w-4xl mx-auto">
          <h1 className="text-2xl font-bold text-white">Settings</h1>
          <p className="text-gray-400 mt-1">
            Manage your account, billing, and preferences
          </p>
        </div>
      </div>

      <div className="max-w-4xl mx-auto p-6">
        {/* Tab Navigation */}
        <div className="flex gap-2 mb-6 border-b border-charcoal-light">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
                activeTab === tab.id
                  ? "text-gold border-gold"
                  : "text-gray-400 border-transparent hover:text-white"
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* Account Tab */}
        {activeTab === "account" && (
          <div className="space-y-6">
            <Card className="bg-charcoal-light border-charcoal-lighter">
              <CardHeader>
                <CardTitle className="text-white">Profile</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <label className="block text-sm text-gray-400 mb-2">Name</label>
                  <input
                    type="text"
                    value={user.name}
                    onChange={(e) => setUser({ ...user, name: e.target.value })}
                    className="w-full bg-charcoal border border-charcoal-lighter rounded-lg px-4 py-2 text-white focus:border-gold focus:outline-none"
                  />
                </div>
                <div>
                  <label className="block text-sm text-gray-400 mb-2">Email</label>
                  <input
                    type="email"
                    value={user.email}
                    onChange={(e) => setUser({ ...user, email: e.target.value })}
                    className="w-full bg-charcoal border border-charcoal-lighter rounded-lg px-4 py-2 text-white focus:border-gold focus:outline-none"
                  />
                </div>
                <div className="pt-4">
                  <Button className="bg-gold hover:bg-gold-dark text-charcoal font-semibold">
                    Save Changes
                  </Button>
                </div>
              </CardContent>
            </Card>

            <Card className="bg-charcoal-light border-charcoal-lighter">
              <CardHeader>
                <CardTitle className="text-white">Password</CardTitle>
              </CardHeader>
              <CardContent>
                <Button variant="outline" className="border-charcoal-lighter text-gray-300">
                  Change Password
                </Button>
              </CardContent>
            </Card>

            <Card className="bg-charcoal-light border-charcoal-lighter border-red-500/20">
              <CardHeader>
                <CardTitle className="text-red-400">Danger Zone</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-gray-400 mb-4">
                  Once you delete your account, there is no going back. Please be
                  certain.
                </p>
                <Button
                  variant="outline"
                  className="border-red-500 text-red-500 hover:bg-red-500/10"
                >
                  Delete Account
                </Button>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Billing Tab */}
        {activeTab === "billing" && (
          <div className="space-y-6">
            <Card className="bg-charcoal-light border-charcoal-lighter">
              <CardHeader>
                <CardTitle className="text-white">Current Plan</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex items-center justify-between mb-6">
                  <div>
                    <p className="text-2xl font-bold text-gold capitalize">
                      {user.subscription_tier}
                    </p>
                    <p className="text-sm text-gray-400">
                      $29/month • Renews on July 15, 2024
                    </p>
                  </div>
                  <Button variant="outline" className="border-charcoal-lighter text-gray-300">
                    Manage Subscription
                  </Button>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div className="p-4 bg-charcoal rounded-lg">
                    <p className="text-sm text-gray-400">API Calls This Month</p>
                    <p className="text-xl font-semibold text-white">
                      {user.api_calls_total - user.api_calls_remaining} /{" "}
                      {user.api_calls_total}
                    </p>
                    <div className="h-2 bg-charcoal-light rounded-full mt-2 overflow-hidden">
                      <div
                        className="h-full bg-gold rounded-full"
                        style={{
                          width: `${
                            ((user.api_calls_total - user.api_calls_remaining) /
                              user.api_calls_total) *
                            100
                          }%`,
                        }}
                      />
                    </div>
                  </div>
                  <div className="p-4 bg-charcoal rounded-lg">
                    <p className="text-sm text-gray-400">Portfolios</p>
                    <p className="text-xl font-semibold text-white">2 / 3</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className="bg-charcoal-light border-charcoal-lighter">
              <CardHeader>
                <CardTitle className="text-white">Upgrade Plan</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="p-4 border border-charcoal-lighter rounded-lg">
                    <h3 className="text-lg font-semibold text-white">Pro</h3>
                    <p className="text-2xl font-bold text-gold mt-2">$29/mo</p>
                    <ul className="mt-4 space-y-2 text-sm text-gray-400">
                      <li>✓ Full rankings access</li>
                      <li>✓ 1,000 API calls/month</li>
                      <li>✓ 3 portfolios</li>
                      <li>✓ Custom alerts</li>
                    </ul>
                    <Button
                      disabled
                      className="w-full mt-4 bg-charcoal border border-gold text-gold"
                    >
                      Current Plan
                    </Button>
                  </div>
                  <div className="p-4 border border-gold/50 rounded-lg bg-gold/5">
                    <h3 className="text-lg font-semibold text-white">Institutional</h3>
                    <p className="text-2xl font-bold text-gold mt-2">$199/mo</p>
                    <ul className="mt-4 space-y-2 text-sm text-gray-400">
                      <li>✓ Everything in Pro</li>
                      <li>✓ Unlimited API calls</li>
                      <li>✓ Unlimited portfolios</li>
                      <li>✓ Custom factor weights</li>
                      <li>✓ Priority support</li>
                    </ul>
                    <Button className="w-full mt-4 bg-gold hover:bg-gold-dark text-charcoal font-semibold">
                      Upgrade
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className="bg-charcoal-light border-charcoal-lighter">
              <CardHeader>
                <CardTitle className="text-white">Billing History</CardTitle>
              </CardHeader>
              <CardContent>
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-charcoal-lighter">
                      <th className="text-left py-2 text-sm text-gray-400">Date</th>
                      <th className="text-left py-2 text-sm text-gray-400">
                        Description
                      </th>
                      <th className="text-right py-2 text-sm text-gray-400">Amount</th>
                      <th className="text-right py-2 text-sm text-gray-400">Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr className="border-b border-charcoal-lighter">
                      <td className="py-2 text-white">Jun 15, 2024</td>
                      <td className="py-2 text-gray-400">Pro Plan - Monthly</td>
                      <td className="py-2 text-right text-white">$29.00</td>
                      <td className="py-2 text-right">
                        <span className="text-green-500 text-sm">Paid</span>
                      </td>
                    </tr>
                    <tr className="border-b border-charcoal-lighter">
                      <td className="py-2 text-white">May 15, 2024</td>
                      <td className="py-2 text-gray-400">Pro Plan - Monthly</td>
                      <td className="py-2 text-right text-white">$29.00</td>
                      <td className="py-2 text-right">
                        <span className="text-green-500 text-sm">Paid</span>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Notifications Tab */}
        {activeTab === "notifications" && (
          <div className="space-y-6">
            <Card className="bg-charcoal-light border-charcoal-lighter">
              <CardHeader>
                <CardTitle className="text-white">Email Notifications</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-white">Alert Emails</p>
                    <p className="text-sm text-gray-400">
                      Receive email when your alerts trigger
                    </p>
                  </div>
                  <button
                    onClick={() =>
                      setNotifications({
                        ...notifications,
                        email_alerts: !notifications.email_alerts,
                      })
                    }
                    className={`w-12 h-6 rounded-full transition-colors ${
                      notifications.email_alerts ? "bg-gold" : "bg-charcoal"
                    }`}
                  >
                    <div
                      className={`w-5 h-5 bg-white rounded-full shadow transition-transform ${
                        notifications.email_alerts ? "translate-x-6" : "translate-x-1"
                      }`}
                    />
                  </button>
                </div>

                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-white">Weekly Digest</p>
                    <p className="text-sm text-gray-400">
                      Summary of your portfolio performance
                    </p>
                  </div>
                  <button
                    onClick={() =>
                      setNotifications({
                        ...notifications,
                        weekly_digest: !notifications.weekly_digest,
                      })
                    }
                    className={`w-12 h-6 rounded-full transition-colors ${
                      notifications.weekly_digest ? "bg-gold" : "bg-charcoal"
                    }`}
                  >
                    <div
                      className={`w-5 h-5 bg-white rounded-full shadow transition-transform ${
                        notifications.weekly_digest ? "translate-x-6" : "translate-x-1"
                      }`}
                    />
                  </button>
                </div>

                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-white">Score Changes</p>
                    <p className="text-sm text-gray-400">
                      Notify when watched stocks have significant score changes
                    </p>
                  </div>
                  <button
                    onClick={() =>
                      setNotifications({
                        ...notifications,
                        score_changes: !notifications.score_changes,
                      })
                    }
                    className={`w-12 h-6 rounded-full transition-colors ${
                      notifications.score_changes ? "bg-gold" : "bg-charcoal"
                    }`}
                  >
                    <div
                      className={`w-5 h-5 bg-white rounded-full shadow transition-transform ${
                        notifications.score_changes ? "translate-x-6" : "translate-x-1"
                      }`}
                    />
                  </button>
                </div>
              </CardContent>
            </Card>

            <Card className="bg-charcoal-light border-charcoal-lighter">
              <CardHeader>
                <CardTitle className="text-white">Push Notifications</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-white">Browser Notifications</p>
                    <p className="text-sm text-gray-400">
                      Receive push notifications in your browser
                    </p>
                  </div>
                  <button
                    onClick={() =>
                      setNotifications({
                        ...notifications,
                        push_alerts: !notifications.push_alerts,
                      })
                    }
                    className={`w-12 h-6 rounded-full transition-colors ${
                      notifications.push_alerts ? "bg-gold" : "bg-charcoal"
                    }`}
                  >
                    <div
                      className={`w-5 h-5 bg-white rounded-full shadow transition-transform ${
                        notifications.push_alerts ? "translate-x-6" : "translate-x-1"
                      }`}
                    />
                  </button>
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* API Keys Tab */}
        {activeTab === "api" && (
          <div className="space-y-6">
            <Card className="bg-charcoal-light border-charcoal-lighter">
              <CardHeader>
                <CardTitle className="text-white">Create API Key</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex gap-4">
                  <input
                    type="text"
                    value={newKeyName}
                    onChange={(e) => setNewKeyName(e.target.value)}
                    placeholder="Key name (e.g., Production App)"
                    className="flex-1 bg-charcoal border border-charcoal-lighter rounded-lg px-4 py-2 text-white placeholder-gray-500 focus:border-gold focus:outline-none"
                  />
                  <Button
                    onClick={createApiKey}
                    className="bg-gold hover:bg-gold-dark text-charcoal font-semibold"
                  >
                    Create Key
                  </Button>
                </div>

                {showNewKey && (
                  <div className="mt-4 p-4 bg-charcoal rounded-lg border border-gold/50">
                    <p className="text-sm text-gray-400 mb-2">
                      Your new API key (copy it now, it won&apos;t be shown again):
                    </p>
                    <div className="flex gap-2">
                      <code className="flex-1 p-2 bg-charcoal-light rounded text-gold font-mono text-sm">
                        {showNewKey}
                      </code>
                      <Button
                        onClick={() => {
                          navigator.clipboard.writeText(showNewKey);
                        }}
                        variant="outline"
                        className="border-charcoal-lighter text-gray-300"
                      >
                        Copy
                      </Button>
                    </div>
                    <Button
                      onClick={() => setShowNewKey(null)}
                      variant="ghost"
                      className="mt-2 text-gray-400"
                    >
                      Dismiss
                    </Button>
                  </div>
                )}
              </CardContent>
            </Card>

            <Card className="bg-charcoal-light border-charcoal-lighter">
              <CardHeader>
                <CardTitle className="text-white">Your API Keys</CardTitle>
              </CardHeader>
              <CardContent>
                {apiKeys.length > 0 ? (
                  <table className="w-full">
                    <thead>
                      <tr className="border-b border-charcoal-lighter">
                        <th className="text-left py-2 text-sm text-gray-400">Name</th>
                        <th className="text-left py-2 text-sm text-gray-400">
                          Last Used
                        </th>
                        <th className="text-left py-2 text-sm text-gray-400">Created</th>
                        <th className="text-right py-2 text-sm text-gray-400"></th>
                      </tr>
                    </thead>
                    <tbody>
                      {apiKeys.map((key) => (
                        <tr key={key.id} className="border-b border-charcoal-lighter">
                          <td className="py-3 text-white">{key.name}</td>
                          <td className="py-3 text-gray-400">
                            {key.last_used
                              ? new Date(key.last_used).toLocaleDateString()
                              : "Never"}
                          </td>
                          <td className="py-3 text-gray-400">
                            {new Date(key.created_at).toLocaleDateString()}
                          </td>
                          <td className="py-3 text-right">
                            <Button
                              onClick={() => revokeApiKey(key.id)}
                              variant="ghost"
                              className="text-red-400 hover:text-red-500"
                            >
                              Revoke
                            </Button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                ) : (
                  <p className="text-gray-400 text-center py-4">
                    No API keys created yet
                  </p>
                )}
              </CardContent>
            </Card>

            <Card className="bg-charcoal-light border-charcoal-lighter">
              <CardHeader>
                <CardTitle className="text-white">API Usage</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="mb-4">
                  <div className="flex justify-between text-sm mb-2">
                    <span className="text-gray-400">Monthly Usage</span>
                    <span className="text-white">
                      {user.api_calls_total - user.api_calls_remaining} /{" "}
                      {user.api_calls_total}
                    </span>
                  </div>
                  <div className="h-2 bg-charcoal rounded-full overflow-hidden">
                    <div
                      className="h-full bg-gold rounded-full"
                      style={{
                        width: `${
                          ((user.api_calls_total - user.api_calls_remaining) /
                            user.api_calls_total) *
                          100
                        }%`,
                      }}
                    />
                  </div>
                </div>
                <p className="text-sm text-gray-400">
                  API calls reset on the 1st of each month
                </p>
              </CardContent>
            </Card>
          </div>
        )}
      </div>
    </div>
  );
}
