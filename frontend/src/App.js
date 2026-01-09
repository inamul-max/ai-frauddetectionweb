import { useState, useEffect } from "react";
import { BrowserRouter, Routes, Route, Navigate, useNavigate } from "react-router-dom";
import axios from "axios";
import "./App.css";
import { Button } from "./components/ui/button";
import { Card } from "./components/ui/card";
import { Input } from "./components/ui/input";
import { Label } from "./components/ui/label";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./components/ui/tabs";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./components/ui/select";
import { Badge } from "./components/ui/badge";
import { toast } from "sonner";
import { Toaster } from "./components/ui/sonner";
import { Shield, Activity, AlertTriangle, TrendingUp, User, LogOut, BarChart3, FileText, Plus, Eye } from "lucide-react";
import { BarChart, Bar, LineChart, Line, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from "recharts";

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const AuthContext = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem("token"));

  useEffect(() => {
    const savedUser = localStorage.getItem("user");
    if (savedUser) {
      setUser(JSON.parse(savedUser));
    }
  }, []);

  const login = (userData, authToken) => {
    setUser(userData);
    setToken(authToken);
    localStorage.setItem("user", JSON.stringify(userData));
    localStorage.setItem("token", authToken);
  };

  const logout = () => {
    setUser(null);
    setToken(null);
    localStorage.removeItem("user");
    localStorage.removeItem("token");
  };

  return children({ user, token, login, logout });
};

const LandingPage = ({ onShowAuth }) => {
  return (
    <div className="min-h-screen bg-background">
      <div className="relative overflow-hidden">
        <div className="absolute inset-0 bg-[linear-gradient(to_right,#1e293b_1px,transparent_1px),linear-gradient(to_bottom,#1e293b_1px,transparent_1px)] bg-[size:4rem_4rem] [mask-image:radial-gradient(ellipse_60%_50%_at_50%_0%,#000_70%,transparent_100%)]" />
        
        <div className="relative px-6 md:px-12 lg:px-24 py-24">
          <div className="max-w-6xl mx-auto">
            <div className="flex justify-between items-center mb-32">
              <div className="flex items-center gap-3">
                <Shield className="w-10 h-10 text-primary" />
                <h1 className="text-2xl font-chivo font-black">SafeGuard AI</h1>
              </div>
              <Button data-testid="landing-login-btn" onClick={onShowAuth} className="bg-primary hover:bg-primary/90">
                Login
              </Button>
            </div>

            <div className="grid md:grid-cols-2 gap-16 mb-24">
              <div>
                <h2 className="text-5xl lg:text-6xl font-chivo font-black leading-tight mb-8">
                  Real-Time <br />
                  <span className="text-primary">Fraud Detection</span><br />
                  Powered by AI
                </h2>
                <p className="text-lg text-muted-foreground mb-8">
                  Protect your organization from financial fraud, identity theft, and suspicious transactions with cutting-edge AI technology.
                </p>
                <Button data-testid="get-started-btn" onClick={onShowAuth} size="lg" className="bg-primary hover:bg-primary/90 text-white rounded-md px-8 py-6 font-medium hover:shadow-[0_0_20px_rgba(59,130,246,0.5)]">
                  Get Started
                </Button>
              </div>

              <div className="grid grid-cols-2 gap-6">
                <Card className="bg-card border border-border rounded-xl p-6 hover:border-primary/50">
                  <Activity className="w-8 h-8 text-primary mb-4" />
                  <h3 className="font-chivo font-black text-xl mb-2">Real-Time</h3>
                  <p className="text-sm text-muted-foreground">Instant fraud detection</p>
                </Card>
                <Card className="bg-card border border-border rounded-xl p-6 hover:border-primary/50">
                  <Shield className="w-8 h-8 text-primary mb-4" />
                  <h3 className="font-chivo font-black text-xl mb-2">AI Powered</h3>
                  <p className="text-sm text-muted-foreground">Gemini 3 Flash analysis</p>
                </Card>
                <Card className="bg-card border border-border rounded-xl p-6 hover:border-primary/50">
                  <AlertTriangle className="w-8 h-8 text-primary mb-4" />
                  <h3 className="font-chivo font-black text-xl mb-2">Smart Alerts</h3>
                  <p className="text-sm text-muted-foreground">Pattern recognition</p>
                </Card>
                <Card className="bg-card border border-border rounded-xl p-6 hover:border-primary/50">
                  <TrendingUp className="w-8 h-8 text-primary mb-4" />
                  <h3 className="font-chivo font-black text-xl mb-2">Analytics</h3>
                  <p className="text-sm text-muted-foreground">Detailed insights</p>
                </Card>
              </div>
            </div>

            <div className="grid md:grid-cols-3 gap-8">
              <div className="bg-slate-900/50 border border-white/5 rounded-2xl p-8 backdrop-blur-sm hover:bg-slate-900/80">
                <h3 className="font-chivo font-black text-2xl mb-4">Financial Fraud</h3>
                <p className="text-muted-foreground">Detect unauthorized transactions, card fraud, and suspicious payment patterns.</p>
              </div>
              <div className="bg-slate-900/50 border border-white/5 rounded-2xl p-8 backdrop-blur-sm hover:bg-slate-900/80">
                <h3 className="font-chivo font-black text-2xl mb-4">Identity Theft</h3>
                <p className="text-muted-foreground">Identify account takeovers and identity verification issues.</p>
              </div>
              <div className="bg-slate-900/50 border border-white/5 rounded-2xl p-8 backdrop-blur-sm hover:bg-slate-900/80">
                <h3 className="font-chivo font-black text-2xl mb-4">Insurance Claims</h3>
                <p className="text-muted-foreground">Flag suspicious insurance claims and prevent fraud losses.</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

const AuthPage = ({ onLogin, onBack }) => {
  const [isLogin, setIsLogin] = useState(true);
  const [formData, setFormData] = useState({ email: "", password: "", name: "", role: "user" });
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      if (isLogin) {
        const response = await axios.post(`${API}/auth/login`, {
          email: formData.email,
          password: formData.password,
        });
        onLogin(response.data.user, response.data.token);
        toast.success("Login successful!");
      } else {
        await axios.post(`${API}/auth/register`, formData);
        toast.success("Registration successful! Please login.");
        setIsLogin(true);
      }
    } catch (error) {
      toast.error(error.response?.data?.detail || "Authentication failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background flex items-center justify-center px-6">
      <div className="w-full max-w-md">
        <div className="flex items-center gap-3 mb-8 justify-center">
          <Shield className="w-10 h-10 text-primary" />
          <h1 className="text-3xl font-chivo font-black">SafeGuard AI</h1>
        </div>

        <Card className="bg-card border border-border rounded-xl p-8">
          <Tabs value={isLogin ? "login" : "register"} onValueChange={(v) => setIsLogin(v === "login")}>
            <TabsList className="grid w-full grid-cols-2 mb-6">
              <TabsTrigger data-testid="login-tab" value="login">Login</TabsTrigger>
              <TabsTrigger data-testid="register-tab" value="register">Register</TabsTrigger>
            </TabsList>

            <form onSubmit={handleSubmit}>
              {!isLogin && (
                <div className="mb-4">
                  <Label>Name</Label>
                  <Input
                    data-testid="register-name-input"
                    type="text"
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    className="mt-2"
                    required
                  />
                </div>
              )}

              <div className="mb-4">
                <Label>Email</Label>
                <Input
                  data-testid="auth-email-input"
                  type="email"
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                  className="mt-2"
                  required
                />
              </div>

              <div className="mb-4">
                <Label>Password</Label>
                <Input
                  data-testid="auth-password-input"
                  type="password"
                  value={formData.password}
                  onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                  className="mt-2"
                  required
                />
              </div>

              {!isLogin && (
                <div className="mb-6">
                  <Label>Role</Label>
                  <Select value={formData.role} onValueChange={(v) => setFormData({ ...formData, role: v })}>
                    <SelectTrigger data-testid="role-select" className="mt-2">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="user">User</SelectItem>
                      <SelectItem value="analyst">Analyst</SelectItem>
                      <SelectItem value="admin">Admin</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              )}

              <Button data-testid="auth-submit-btn" type="submit" className="w-full mb-4" disabled={loading}>
                {loading ? "Processing..." : isLogin ? "Login" : "Register"}
              </Button>

              <Button data-testid="back-to-landing-btn" type="button" variant="ghost" className="w-full" onClick={onBack}>
                Back to Home
              </Button>
            </form>
          </Tabs>
        </Card>
      </div>
    </div>
  );
};

const Dashboard = ({ user, token, onLogout }) => {
  const navigate = useNavigate();
  const [transactions, setTransactions] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [cases, setCases] = useState([]);
  const [stats, setStats] = useState(null);
  const [activeView, setActiveView] = useState("overview");
  const [newTransaction, setNewTransaction] = useState({
    amount: "",
    transaction_type: "payment",
    merchant: "",
    location: "",
  });
  const [newCase, setNewCase] = useState({ transaction_ids: [], notes: "" });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const config = { headers: { Authorization: `Bearer ${token}` } };
      
      const txResponse = await axios.get(`${API}/transactions`, config);
      setTransactions(txResponse.data);

      if (user.role !== "user") {
        const statsResponse = await axios.get(`${API}/analytics/stats`, config);
        setStats(statsResponse.data);

        const alertsResponse = await axios.get(`${API}/fraud-alerts`, config);
        setAlerts(alertsResponse.data);
      }

      if (user.role === "analyst" || user.role === "admin") {
        const casesResponse = await axios.get(`${API}/cases`, config);
        setCases(casesResponse.data);
      }
    } catch (error) {
      toast.error("Failed to load data");
    }
  };

  const submitTransaction = async (e) => {
    e.preventDefault();
    try {
      const config = { headers: { Authorization: `Bearer ${token}` } };
      await axios.post(`${API}/transactions`, newTransaction, config);
      toast.success("Transaction submitted for analysis!");
      setNewTransaction({ amount: "", transaction_type: "payment", merchant: "", location: "" });
      loadData();
    } catch (error) {
      toast.error("Failed to submit transaction");
    }
  };

  const createCase = async (e) => {
    e.preventDefault();
    try {
      const config = { headers: { Authorization: `Bearer ${token}` } };
      await axios.post(`${API}/cases`, newCase, config);
      toast.success("Investigation case created!");
      setNewCase({ transaction_ids: [], notes: "" });
      loadData();
    } catch (error) {
      toast.error("Failed to create case");
    }
  };

  const getRiskColor = (level) => {
    if (level === "high") return "bg-red-500";
    if (level === "medium") return "bg-yellow-500";
    return "bg-green-500";
  };

  return (
    <div className="min-h-screen bg-background">
      <div className="border-b border-border bg-card/50 backdrop-blur-sm sticky top-0 z-50">
        <div className="px-6 md:px-12 py-4 flex justify-between items-center">
          <div className="flex items-center gap-3">
            <Shield className="w-8 h-8 text-primary" />
            <h1 className="text-xl font-chivo font-black">SafeGuard AI</h1>
          </div>
          <div className="flex items-center gap-4">
            <div className="text-right">
              <p className="text-sm font-medium">{user.name}</p>
              <p className="text-xs text-muted-foreground capitalize">{user.role}</p>
            </div>
            <Button data-testid="logout-btn" variant="ghost" size="icon" onClick={onLogout}>
              <LogOut className="w-4 h-4" />
            </Button>
          </div>
        </div>

        <div className="px-6 md:px-12 flex gap-2 overflow-x-auto pb-2">
          <Button
            data-testid="overview-tab-btn"
            variant={activeView === "overview" ? "default" : "ghost"}
            onClick={() => setActiveView("overview")}
            className="whitespace-nowrap"
          >
            <BarChart3 className="w-4 h-4 mr-2" />
            Overview
          </Button>
          <Button
            data-testid="transactions-tab-btn"
            variant={activeView === "transactions" ? "default" : "ghost"}
            onClick={() => setActiveView("transactions")}
            className="whitespace-nowrap"
          >
            <Activity className="w-4 h-4 mr-2" />
            Transactions
          </Button>
          {user.role !== "user" && (
            <Button
              data-testid="alerts-tab-btn"
              variant={activeView === "alerts" ? "default" : "ghost"}
              onClick={() => setActiveView("alerts")}
              className="whitespace-nowrap"
            >
              <AlertTriangle className="w-4 h-4 mr-2" />
              Alerts
            </Button>
          )}
          {(user.role === "analyst" || user.role === "admin") && (
            <Button
              data-testid="cases-tab-btn"
              variant={activeView === "cases" ? "default" : "ghost"}
              onClick={() => setActiveView("cases")}
              className="whitespace-nowrap"
            >
              <FileText className="w-4 h-4 mr-2" />
              Cases
            </Button>
          )}
        </div>
      </div>

      <div className="px-6 md:px-12 py-8">
        {activeView === "overview" && (
          <div>
            <h2 className="text-3xl font-chivo font-black mb-8">Dashboard Overview</h2>

            {stats && (
              <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
                <Card data-testid="total-transactions-card" className="bg-card border border-border rounded-xl p-6">
                  <p className="text-sm text-muted-foreground mb-2">Total Transactions</p>
                  <p className="text-3xl font-chivo font-black">{stats.total_transactions}</p>
                </Card>
                <Card data-testid="flagged-transactions-card" className="bg-card border border-border rounded-xl p-6">
                  <p className="text-sm text-muted-foreground mb-2">Flagged</p>
                  <p className="text-3xl font-chivo font-black text-red-500">{stats.flagged_transactions}</p>
                </Card>
                <Card data-testid="total-alerts-card" className="bg-card border border-border rounded-xl p-6">
                  <p className="text-sm text-muted-foreground mb-2">Active Alerts</p>
                  <p className="text-3xl font-chivo font-black text-yellow-500">{stats.total_alerts}</p>
                </Card>
                <Card data-testid="active-cases-card" className="bg-card border border-border rounded-xl p-6">
                  <p className="text-sm text-muted-foreground mb-2">Open Cases</p>
                  <p className="text-3xl font-chivo font-black text-blue-500">{stats.active_cases}</p>
                </Card>
              </div>
            )}

            {stats && (
              <div className="grid md:grid-cols-2 gap-6">
                <Card className="bg-card border border-border rounded-xl p-6">
                  <h3 className="text-xl font-chivo font-black mb-6">Risk Distribution</h3>
                  <ResponsiveContainer width="100%" height={250}>
                    <PieChart>
                      <Pie
                        data={[
                          { name: "High Risk", value: stats.risk_distribution.high },
                          { name: "Medium Risk", value: stats.risk_distribution.medium },
                          { name: "Low Risk", value: stats.risk_distribution.low },
                        ]}
                        cx="50%"
                        cy="50%"
                        outerRadius={80}
                        dataKey="value"
                        label
                      >
                        <Cell fill="#ef4444" />
                        <Cell fill="#f59e0b" />
                        <Cell fill="#10b981" />
                      </Pie>
                      <Tooltip />
                    </PieChart>
                  </ResponsiveContainer>
                </Card>

                <Card className="bg-card border border-border rounded-xl p-6">
                  <h3 className="text-xl font-chivo font-black mb-6">Fraud Types Detected</h3>
                  <ResponsiveContainer width="100%" height={250}>
                    <BarChart data={stats.fraud_types}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                      <XAxis dataKey="type" stroke="#94a3b8" />
                      <YAxis stroke="#94a3b8" />
                      <Tooltip contentStyle={{ backgroundColor: "#0f172a", border: "1px solid #1e293b" }} />
                      <Bar dataKey="count" fill="#3b82f6" />
                    </BarChart>
                  </ResponsiveContainer>
                </Card>
              </div>
            )}

            {user.role === "user" && (
              <Card className="bg-card border border-border rounded-xl p-6 mt-8">
                <h3 className="text-xl font-chivo font-black mb-6">Submit New Transaction</h3>
                <form onSubmit={submitTransaction} className="grid md:grid-cols-2 gap-4">
                  <div>
                    <Label>Amount ($)</Label>
                    <Input
                      data-testid="transaction-amount-input"
                      type="number"
                      step="0.01"
                      value={newTransaction.amount}
                      onChange={(e) => setNewTransaction({ ...newTransaction, amount: e.target.value })}
                      className="mt-2"
                      required
                    />
                  </div>
                  <div>
                    <Label>Transaction Type</Label>
                    <Select
                      value={newTransaction.transaction_type}
                      onValueChange={(v) => setNewTransaction({ ...newTransaction, transaction_type: v })}
                    >
                      <SelectTrigger data-testid="transaction-type-select" className="mt-2">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="payment">Payment</SelectItem>
                        <SelectItem value="transfer">Transfer</SelectItem>
                        <SelectItem value="withdrawal">Withdrawal</SelectItem>
                        <SelectItem value="purchase">Purchase</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div>
                    <Label>Merchant</Label>
                    <Input
                      data-testid="transaction-merchant-input"
                      type="text"
                      value={newTransaction.merchant}
                      onChange={(e) => setNewTransaction({ ...newTransaction, merchant: e.target.value })}
                      className="mt-2"
                      required
                    />
                  </div>
                  <div>
                    <Label>Location</Label>
                    <Input
                      data-testid="transaction-location-input"
                      type="text"
                      value={newTransaction.location}
                      onChange={(e) => setNewTransaction({ ...newTransaction, location: e.target.value })}
                      className="mt-2"
                      required
                    />
                  </div>
                  <div className="md:col-span-2">
                    <Button data-testid="submit-transaction-btn" type="submit" className="w-full">
                      Submit for AI Analysis
                    </Button>
                  </div>
                </form>
              </Card>
            )}
          </div>
        )}

        {activeView === "transactions" && (
          <div>
            <h2 className="text-3xl font-chivo font-black mb-8">Transaction Monitor</h2>
            <div className="space-y-4">
              {transactions.map((tx) => (
                <Card key={tx.id} data-testid={`transaction-${tx.id}`} className="bg-card border border-border rounded-xl p-6">
                  <div className="flex justify-between items-start mb-4">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <p className="font-chivo font-black text-xl">${tx.amount.toFixed(2)}</p>
                        <Badge className={getRiskColor(tx.risk_level)}>
                          {tx.risk_level} - {tx.risk_score.toFixed(0)}%
                        </Badge>
                        <Badge variant={tx.status === "flagged" ? "destructive" : "default"}>{tx.status}</Badge>
                      </div>
                      <p className="text-sm text-muted-foreground">
                        {tx.merchant} • {tx.location} • {tx.transaction_type}
                      </p>
                      <p className="text-xs text-muted-foreground font-mono mt-2">ID: {tx.id}</p>
                    </div>
                  </div>
                  {tx.ai_analysis && (
                    <div className="bg-secondary/50 rounded-md p-4 mt-4">
                      <p className="text-sm font-medium mb-2">AI Analysis:</p>
                      <p className="text-sm text-muted-foreground">{tx.ai_analysis}</p>
                      {tx.fraud_types.length > 0 && (
                        <div className="flex gap-2 mt-3">
                          {tx.fraud_types.map((type) => (
                            <Badge key={type} variant="outline" className="text-xs">
                              {type}
                            </Badge>
                          ))}
                        </div>
                      )}
                    </div>
                  )}
                </Card>
              ))}
            </div>
          </div>
        )}

        {activeView === "alerts" && user.role !== "user" && (
          <div>
            <h2 className="text-3xl font-chivo font-black mb-8">Fraud Alerts</h2>
            <div className="space-y-4">
              {alerts.map((alert) => (
                <Card key={alert.id} data-testid={`alert-${alert.id}`} className="bg-card border border-destructive/50 rounded-xl p-6">
                  <div className="flex justify-between items-start mb-4">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <AlertTriangle className="w-6 h-6 text-destructive" />
                        <p className="font-chivo font-black text-xl capitalize">{alert.severity} Severity</p>
                        <Badge variant={alert.status === "active" ? "destructive" : "default"}>{alert.status}</Badge>
                      </div>
                      <p className="text-sm text-muted-foreground font-mono">Transaction: {alert.transaction_id}</p>
                    </div>
                  </div>
                  <div className="bg-destructive/10 rounded-md p-4">
                    <p className="text-sm font-medium mb-2">Detected Patterns:</p>
                    <div className="flex gap-2 mb-3">
                      {alert.detected_patterns.map((pattern) => (
                        <Badge key={pattern} variant="outline">
                          {pattern}
                        </Badge>
                      ))}
                    </div>
                    <p className="text-sm text-muted-foreground">{alert.ai_analysis}</p>
                  </div>
                </Card>
              ))}
            </div>
          </div>
        )}

        {activeView === "cases" && (user.role === "analyst" || user.role === "admin") && (
          <div>
            <h2 className="text-3xl font-chivo font-black mb-8">Investigation Cases</h2>

            {user.role === "analyst" && (
              <Card className="bg-card border border-border rounded-xl p-6 mb-8">
                <h3 className="text-xl font-chivo font-black mb-6">Create New Case</h3>
                <form onSubmit={createCase}>
                  <div className="mb-4">
                    <Label>Transaction IDs (comma separated)</Label>
                    <Input
                      data-testid="case-transaction-ids-input"
                      type="text"
                      value={newCase.transaction_ids.join(",")}
                      onChange={(e) =>
                        setNewCase({
                          ...newCase,
                          transaction_ids: e.target.value.split(",").map((id) => id.trim()),
                        })
                      }
                      className="mt-2"
                      placeholder="tx-id-1, tx-id-2"
                      required
                    />
                  </div>
                  <div className="mb-4">
                    <Label>Notes</Label>
                    <Input
                      data-testid="case-notes-input"
                      type="text"
                      value={newCase.notes}
                      onChange={(e) => setNewCase({ ...newCase, notes: e.target.value })}
                      className="mt-2"
                      required
                    />
                  </div>
                  <Button data-testid="create-case-btn" type="submit" className="w-full">
                    <Plus className="w-4 h-4 mr-2" />
                    Create Case
                  </Button>
                </form>
              </Card>
            )}

            <div className="space-y-4">
              {cases.map((caseItem) => (
                <Card key={caseItem.id} data-testid={`case-${caseItem.id}`} className="bg-card border border-border rounded-xl p-6">
                  <div className="flex justify-between items-start mb-4">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <FileText className="w-6 h-6 text-primary" />
                        <p className="font-chivo font-black text-xl">Case #{caseItem.id.slice(0, 8)}</p>
                        <Badge variant={caseItem.status === "open" ? "default" : "secondary"}>{caseItem.status}</Badge>
                      </div>
                      <p className="text-sm text-muted-foreground">
                        {caseItem.transaction_ids.length} transaction(s) under investigation
                      </p>
                    </div>
                  </div>
                  <div className="bg-secondary/50 rounded-md p-4">
                    <p className="text-sm font-medium mb-2">Notes:</p>
                    <p className="text-sm text-muted-foreground">{caseItem.notes}</p>
                  </div>
                </Card>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

function App() {
  return (
    <AuthContext>
      {({ user, token, login, logout }) => {
        const [showAuth, setShowAuth] = useState(false);

        return (
          <div className="App">
            <Toaster />
            <BrowserRouter>
              <Routes>
                <Route
                  path="/"
                  element={
                    user ? (
                      <Dashboard user={user} token={token} onLogout={logout} />
                    ) : showAuth ? (
                      <AuthPage onLogin={login} onBack={() => setShowAuth(false)} />
                    ) : (
                      <LandingPage onShowAuth={() => setShowAuth(true)} />
                    )
                  }
                />
              </Routes>
            </BrowserRouter>
          </div>
        );
      }}
    </AuthContext>
  );
}

export default App;
