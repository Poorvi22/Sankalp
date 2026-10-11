import { useState } from "react";
import {
  Activity,
  AlertTriangle,
  ArrowDownRight,
  ArrowUpRight,
  BarChart3,
  Bell,
  Bot,
  Box,
  CalendarDays,
  Check,
  ChevronDown,
  CircleDollarSign,
  ClipboardList,
  CreditCard,
  FileBarChart,
  FileText,
  LayoutDashboard,
  Menu,
  MessageCircle,
  Mic,
  Minus,
  Package,
  Search,
  Send,
  Settings,
  ShoppingCart,
  Truck,
  Users,
  Warehouse,
  X,
  Maximize2,
  Sparkles,
  CheckCircle2,
  Clock3,
  TrendingUp,
  PackageCheck,
  ActivitySquare,
} from "lucide-react";

import {
  Area,
  AreaChart,
  CartesianGrid,
  Cell,
  Line,
  LineChart,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import "./App.css";

const navigation = [
  { label: "Dashboard", icon: LayoutDashboard },
  { label: "Inventory", icon: Package },
  { label: "Suppliers", icon: Users },
  { label: "Procurement", icon: ClipboardList },
  { label: "Sales & Orders", icon: ShoppingCart },
  { label: "Logistics", icon: Truck },
  { label: "Finance", icon: CircleDollarSign },
  { label: "Analytics", icon: BarChart3 },
];

const secondaryNavigation = [
  { label: "Approvals", icon: CheckCircle2, badge: "5" },
  { label: "Reports", icon: FileText },
  { label: "Agent Activity", icon: Activity },
  { label: "Settings", icon: Settings },
];

const revenueData = [
  { month: "Jan", revenue: 105, orders: 40 },
  { month: "Feb", revenue: 170, orders: 95 },
  { month: "Mar", revenue: 215, orders: 105 },
  { month: "Apr", revenue: 305, orders: 115 },
  { month: "May", revenue: 320, orders: 185 },
  { month: "Jun", revenue: 215, orders: 160 },
  { month: "Jul", revenue: 145, orders: 205 },
  { month: "Aug", revenue: 205, orders: 275 },
  { month: "Sep", revenue: 235, orders: 325 },
  { month: "Oct", revenue: 160, orders: 235 },
  { month: "Nov", revenue: 145, orders: 235 },
  { month: "Dec", revenue: 235, orders: 310 },
];

const inventoryItems = [
  { name: "Steel Rod (SR-001)", stock: 500, reorder: 1000, days: 5 },
  { name: "Plastic Resin (PR-002)", stock: 200, reorder: 800, days: 7 },
  { name: "Copper Wire (CW-003)", stock: 300, reorder: 1200, days: 6 },
  { name: "Aluminum Sheet (AS-004)", stock: 250, reorder: 1000, days: 8 },
];

const purchaseOrders = [
  { id: "PO-2024-089", supplier: "Global Metals Ltd.", status: "Approved", amount: "$45,000", date: "Dec 10" },
  { id: "PO-2024-088", supplier: "Prime Plastics", status: "Pending", amount: "$32,500", date: "Dec 09" },
  { id: "PO-2024-087", supplier: "Steel Supplies Co.", status: "Approved", amount: "$28,750", date: "Dec 08" },
  { id: "PO-2024-086", supplier: "MetalWorks Inc.", status: "Draft", amount: "$15,200", date: "Dec 08" },
  { id: "PO-2024-085", supplier: "Asia Components", status: "Approved", amount: "$60,000", date: "Dec 07" },
];

const expenseData = [
  { name: "Raw Materials", value: 45, color: "#3984f6" },
  { name: "Logistics", value: 20, color: "#8b5cf6" },
  { name: "Manufacturing", value: 15, color: "#f5b82e" },
  { name: "Other", value: 10, color: "#a855f7" },
  { name: "Administrative", value: 10, color: "#16b981" },
];

const suggestions = [
  "Show me products likely to run out in 14 days",
  "Compare top 3 suppliers for steel with best pricing",
  "Create purchase order for low stock items",
  "Show last 12 months sales analysis",
  "What is the current page and key information?",
];

function MetricCard({
  icon: Icon,
  title,
  value,
  change,
  positive = true,
  tone = "blue",
}) {
  return (
    <div className="metric-card">
      <div className={`metric-icon ${tone}`}>
        <Icon size={24} strokeWidth={2.1} />
      </div>

      <div className="metric-content">
        <span className="metric-title">{title}</span>
        <strong className="metric-value">{value}</strong>

        <div className={`metric-change ${positive ? "positive" : "negative"}`}>
          {positive ? (
            <ArrowUpRight size={16} />
          ) : (
            <ArrowDownRight size={16} />
          )}
          <span>{change}</span>
        </div>

        <span className="metric-caption">vs. previous period</span>
      </div>
    </div>
  );
}

function SectionHeader({ icon: Icon, title, action }) {
  return (
    <div className="section-header">
      <div className="section-title">
        <Icon size={21} />
        <h3>{title}</h3>
      </div>
      {action && (
        <button className="text-button" onClick={action.onClick}>
          {action.label}
        </button>
      )}
    </div>
  );
}

function DonutChart({ data, centerValue, centerLabel, size = 140 }) {
  return (
    <div className="donut-wrap" style={{ width: size, height: size }}>
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie
            data={data}
            dataKey="value"
            nameKey="name"
            innerRadius="65%"
            outerRadius="94%"
            paddingAngle={1}
            stroke="none"
          >
            {data.map((entry, index) => (
              <Cell key={index} fill={entry.color} />
            ))}
          </Pie>
          <Tooltip />
        </PieChart>
      </ResponsiveContainer>

      <div className="donut-center">
        <strong>{centerValue}</strong>
        <span>{centerLabel}</span>
      </div>
    </div>
  );
}

function ChatMessage({ children, user = false }) {
  return (
    <div className={`chat-message-row ${user ? "user-row" : ""}`}>
      {!user && (
        <div className="chat-avatar">
          <Bot size={20} />
        </div>
      )}
      <div className={`chat-message ${user ? "user-message" : ""}`}>
        {children}
      </div>
    </div>
  );
}

function DashboardContent() {
  const [period, setPeriod] = useState("Last 12 Months");

  return (
    <>
      <div className="page-heading">
        <div>
          <h1>Dashboard</h1>
          <p>Real-time overview of your supply chain and business operations</p>
        </div>

        <div className="dashboard-filters">
          <button className="filter-button">
            <CalendarDays size={16} />
            Jan 2024 - Dec 2024
            <ChevronDown size={14} />
          </button>

          <button className="filter-button">
            All Locations
            <ChevronDown size={14} />
          </button>
        </div>
      </div>

      <div className="demo-banner">
        <ActivitySquare size={15} />
        Demonstration data · Connect a business data source for live metrics
      </div>

      <div className="metrics-grid">
        <MetricCard
          icon={Warehouse}
          title="Total Revenue"
          value="$2.48M"
          change="12.5%"
          tone="green"
        />

        <MetricCard
          icon={ShoppingCart}
          title="Total Orders"
          value="5,842"
          change="18.2%"
          tone="blue"
        />

        <MetricCard
          icon={Box}
          title="Inventory Value"
          value="$1.12M"
          change="5.3%"
          positive={false}
          tone="purple"
        />

        <MetricCard
          icon={Users}
          title="Active Suppliers"
          value="48"
          change="9.1%"
          tone="cyan"
        />
      </div>

      <div className="dashboard-grid main-charts">
        <section className="panel revenue-panel">
          <SectionHeader
            icon={TrendingUp}
            title="Revenue & Orders Trend"
          />

          <div className="chart-toolbar">
            <div className="chart-legend">
              <span><i className="legend-dot revenue-dot" />Revenue (USD)</span>
              <span><i className="legend-dot orders-dot" />Orders</span>
            </div>

            <select
              aria-label="Chart period"
              value={period}
              onChange={(event) => setPeriod(event.target.value)}
              className="period-select"
            >
              <option>Last 12 Months</option>
              <option>Last 6 Months</option>
              <option>Last 3 Months</option>
            </select>
          </div>

          <div className="revenue-chart">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={revenueData}>
                <defs>
                  <linearGradient id="revenueFill" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#3984f6" stopOpacity={0.17} />
                    <stop offset="100%" stopColor="#3984f6" stopOpacity={0.01} />
                  </linearGradient>
                </defs>

                <CartesianGrid stroke="#e9edf4" vertical={false} />

                <XAxis
                  dataKey="month"
                  tickLine={false}
                  axisLine={false}
                  tick={{ fill: "#7b8496", fontSize: 11 }}
                  interval={0}
                />

                <YAxis
                  tickLine={false}
                  axisLine={false}
                  tick={{ fill: "#7b8496", fontSize: 11 }}
                  tickFormatter={(value) => `$${value}K`}
                  width={50}
                  domain={[0, 400]}
                />

                <Tooltip
                  formatter={(value, name) => [
                    name === "revenue" ? `$${value}K` : `${value}K`,
                    name === "revenue" ? "Revenue" : "Orders",
                  ]}
                />

                <Area
                  type="monotone"
                  dataKey="revenue"
                  stroke="#3984f6"
                  strokeWidth={2.5}
                  fill="url(#revenueFill)"
                  dot={{ r: 2.5, fill: "#3984f6" }}
                />

                <Line
                  type="monotone"
                  dataKey="orders"
                  stroke="#18b77b"
                  strokeWidth={2.5}
                  dot={{ r: 2.5, fill: "#18b77b" }}
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </section>

        <section className="panel inventory-status-panel">
          <SectionHeader icon={ShoppingCart} title="Inventory Status" />

          <div className="inventory-status-content">
            <DonutChart
              data={[
                { name: "In Stock", value: 78, color: "#18b77b" },
                { name: "Low Stock", value: 15, color: "#f5b82e" },
                { name: "Out of Stock", value: 7, color: "#ed4d58" },
              ]}
              centerValue="1,245"
              centerLabel="Total Items"
              size={152}
            />

            <div className="inventory-legend">
              <div>
                <i className="legend-dot green-dot" />
                <span><strong>In Stock</strong><small>78% (975)</small></span>
              </div>
              <div>
                <i className="legend-dot yellow-dot" />
                <span><strong>Low Stock</strong><small>15% (187)</small></span>
              </div>
              <div>
                <i className="legend-dot red-dot" />
                <span><strong>Out of Stock</strong><small>7% (83)</small></span>
              </div>
            </div>
          </div>
        </section>
      </div>

      <div className="dashboard-grid middle-grid">
        <section className="panel table-panel">
          <SectionHeader
            icon={AlertTriangle}
            title="Low Stock Alerts"
            action={{ label: "View All", onClick: () => window.dispatchEvent(new CustomEvent("navigate-page", { detail: "Inventory" })) }}
          />

          <div className="table-scroll">
            <table>
              <thead>
                <tr>
                  <th>Product</th>
                  <th>Current Stock</th>
                  <th>Reorder Level</th>
                  <th>Days Left</th>
                </tr>
              </thead>

              <tbody>
                {inventoryItems.map((item) => (
                  <tr key={item.name}>
                    <td>
                      <span className="product-thumb">
                        <Package size={17} />
                      </span>
                      {item.name}
                    </td>
                    <td>{item.stock.toLocaleString()}</td>
                    <td>{item.reorder.toLocaleString()}</td>
                    <td><span className="days-badge">{item.days} days</span></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>

        <section className="panel table-panel">
          <SectionHeader
            icon={ShoppingCart}
            title="Recent Purchase Orders"
            action={{ label: "View All", onClick: () => window.dispatchEvent(new CustomEvent("navigate-page", { detail: "Procurement" })) }}
          />

          <div className="table-scroll">
            <table>
              <thead>
                <tr>
                  <th>PO #</th>
                  <th>Supplier</th>
                  <th>Status</th>
                  <th>Amount</th>
                  <th>Date</th>
                </tr>
              </thead>

              <tbody>
                {purchaseOrders.map((order) => (
                  <tr key={order.id}>
                    <td>{order.id}</td>
                    <td>{order.supplier}</td>
                    <td>
                      <span className={`status-badge ${order.status.toLowerCase()}`}>
                        {order.status}
                      </span>
                    </td>
                    <td>{order.amount}</td>
                    <td>{order.date}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      </div>

      <div className="dashboard-grid bottom-grid">
        <section className="panel fulfillment-panel">
          <SectionHeader icon={PackageCheck} title="Order Fulfillment Rate" />

          <div className="fulfillment-content">
            <DonutChart
              data={[
                { name: "Delivered", value: 92, color: "#18b77b" },
                { name: "Pending", value: 8, color: "#e5ebf3" },
              ]}
              centerValue="92%"
              centerLabel="On time"
              size={130}
            />

            <div className="fulfillment-stats">
              <div><CheckCircle2 /><span><strong>5,842</strong><small>Total Orders</small></span></div>
              <div><PackageCheck /><span><strong>5,372</strong><small>Delivered On Time</small></span></div>
              <div><Clock3 /><span><strong>470</strong><small>Delayed Orders</small></span></div>
            </div>
          </div>
        </section>

        <section className="panel expense-panel">
          <SectionHeader icon={CircleDollarSign} title="Expense Breakdown" />

          <div className="expense-content">
            <DonutChart
              data={expenseData}
              centerValue="$1.2M"
              centerLabel="Total"
              size={145}
            />

            <div className="expense-legend">
              {expenseData.map((item) => (
                <div key={item.name}>
                  <i className="legend-dot" style={{ background: item.color }} />
                  <span>{item.name}</span>
                  <strong>{item.value}%</strong>
                </div>
              ))}
            </div>
          </div>
        </section>

        <section className="panel selling-panel">
          <SectionHeader
            icon={BarChart3}
            title="Top Selling Products"
            action={{ label: "View All", onClick: () => window.dispatchEvent(new CustomEvent("navigate-page", { detail: "Analytics" })) }}
          />

          <table>
            <thead>
              <tr><th>Product</th><th>Units Sold</th><th>Revenue</th></tr>
            </thead>
            <tbody>
              <tr><td>Steel Rod</td><td>12,450</td><td>$498,000</td></tr>
              <tr><td>Plastic Resin</td><td>8,320</td><td>$332,800</td></tr>
              <tr><td>Copper Wire</td><td>6,750</td><td>$270,000</td></tr>
              <tr><td>Aluminum Sheet</td><td>5,980</td><td>$239,200</td></tr>
            </tbody>
          </table>
        </section>
      </div>
    </>
  );
}

function ModulePage({ page }) {
  const modules = {
    Inventory: {
      icon: Package,
      subtitle: "Monitor stock levels, warehouse operations, and reorder requirements.",
      cards: [["Total Products", "1,245"], ["Low Stock Items", "187"], ["Out of Stock", "83"], ["Inventory Value", "$1.12M"]],
      rows: [["Steel Rod", "SR-001", "500", "1,000", "Low Stock"], ["Plastic Resin", "PR-002", "200", "800", "Low Stock"], ["Copper Wire", "CW-003", "300", "1,200", "Low Stock"], ["Aluminum Sheet", "AS-004", "250", "1,000", "Low Stock"]],
      headers: ["Product", "SKU", "Current Stock", "Reorder Level", "Status"],
    },
    Suppliers: {
      icon: Users,
      subtitle: "Manage supplier relationships, performance, and pricing.",
      cards: [["Total Suppliers", "48"], ["Active Suppliers", "42"], ["Pending Review", "4"], ["Average Rating", "4.6/5"]],
      rows: [["Global Metals Ltd.", "SUP-001", "Metals", "4.8/5", "Active"], ["Prime Plastics", "SUP-002", "Plastics", "4.5/5", "Active"], ["Steel Supplies Co.", "SUP-003", "Metals", "4.4/5", "Active"], ["Asia Components", "SUP-004", "Components", "4.7/5", "Active"]],
      headers: ["Supplier", "Supplier ID", "Category", "Rating", "Status"],
    },
    Procurement: {
      icon: ClipboardList,
      subtitle: "Track purchase orders, approvals, and procurement activity.",
      cards: [["Total Orders", "128"], ["Pending Approval", "12"], ["Approved Orders", "94"], ["Purchase Value", "$1.42M"]],
      rows: purchaseOrders.map((o) => [o.id, o.supplier, o.status, o.amount, o.date]),
      headers: ["Order ID", "Supplier", "Status", "Amount", "Date"],
    },
    "Sales & Orders": {
      icon: ShoppingCart,
      subtitle: "Monitor customer orders, sales performance, and order fulfillment.",
      cards: [["Total Orders", "5,842"], ["Revenue", "$2.48M"], ["Pending Orders", "126"], ["Completed Orders", "5,372"]],
      rows: [["SO-1001", "Northstar Retail", "Approved", "$12,500", "Dec 10"], ["SO-1002", "Vertex Industries", "Pending", "$8,400", "Dec 10"], ["SO-1003", "Apex Manufacturing", "Shipped", "$21,700", "Dec 09"], ["SO-1004", "Summit Supply", "Completed", "$6,200", "Dec 08"]],
      headers: ["Order ID", "Customer", "Status", "Amount", "Date"],
    },
    Logistics: {
      icon: Truck,
      subtitle: "Track shipments, delivery status, and fulfillment operations.",
      cards: [["Total Shipments", "326"], ["In Transit", "48"], ["Delivered", "264"], ["Delayed", "14"]],
      rows: [["SHIP-1001", "Bengaluru", "In Transit", "Dec 11", "On Schedule"], ["SHIP-1002", "Mumbai", "Delivered", "Dec 10", "Completed"], ["SHIP-1003", "Chennai", "Delayed", "Dec 12", "Delayed"], ["SHIP-1004", "Hyderabad", "In Transit", "Dec 12", "On Schedule"]],
      headers: ["Shipment ID", "Destination", "Status", "ETA", "Delivery"],
    },
    Finance: {
      icon: CircleDollarSign,
      subtitle: "Review revenue, expenses, cash flow, and financial performance.",
      cards: [["Total Revenue", "$2.48M"], ["Operating Expenses", "$1.20M"], ["Net Profit", "$680K"], ["Outstanding", "$145K"]],
      rows: [["INV-1001", "Northstar Retail", "Revenue", "$12,500", "Paid"], ["INV-1002", "Vertex Industries", "Revenue", "$8,400", "Pending"], ["EXP-1001", "Global Logistics", "Expense", "$4,200", "Paid"], ["EXP-1002", "Warehouse Services", "Expense", "$3,100", "Paid"]],
      headers: ["Reference", "Description", "Type", "Amount", "Status"],
    },
    Analytics: {
      icon: BarChart3,
      subtitle: "Explore business performance and operational reports.",
      cards: [["Reports", "24"], ["Revenue Growth", "+12.5%"], ["Order Growth", "+18.2%"], ["Fulfillment", "92%"]],
      rows: [["Monthly Revenue", "Finance", "Dec 10", "Available", "PDF"], ["Inventory Summary", "Inventory", "Dec 09", "Available", "CSV"], ["Supplier Performance", "Suppliers", "Dec 08", "Available", "PDF"], ["Order Fulfillment", "Logistics", "Dec 07", "Available", "PDF"]],
      headers: ["Report", "Category", "Updated", "Status", "Format"],
    },
    Approvals: {
      icon: CheckCircle2,
      subtitle: "Review pending requests and business approvals.",
      cards: [["Pending", "5"], ["Approved Today", "12"], ["Rejected", "2"], ["Awaiting Review", "5"]],
      rows: [["PO-2024-088", "Prime Plastics", "Purchase Order", "$32,500", "Pending"], ["PO-2024-090", "Global Metals", "Purchase Order", "$18,200", "Pending"], ["EXP-1004", "Operations", "Expense", "$2,100", "Pending"]],
      headers: ["Request", "Requested By", "Type", "Amount", "Status"],
    },
    Reports: {
      icon: FileText,
      subtitle: "Access business reports and downloadable summaries.",
      cards: [["Total Reports", "24"], ["Scheduled", "8"], ["Generated", "16"], ["Last Updated", "Today"]],
      rows: [["Monthly Revenue", "Finance", "Dec 10", "Available", "PDF"], ["Inventory Summary", "Inventory", "Dec 09", "Available", "CSV"], ["Supplier Performance", "Suppliers", "Dec 08", "Available", "PDF"]],
      headers: ["Report", "Category", "Updated", "Status", "Format"],
    },
    "Agent Activity": {
      icon: Activity,
      subtitle: "Review AI assistant activity and request history.",
      cards: [["Requests Today", "128"], ["Successful", "121"], ["Pending", "3"], ["Needs Review", "4"]],
      rows: [["Inventory risk analysis", "Analytics", "10:24 AM", "Completed", "Success"], ["Supplier comparison", "Suppliers", "10:12 AM", "Completed", "Success"], ["Purchase order draft", "Procurement", "09:58 AM", "Pending", "Review"]],
      headers: ["Request", "Module", "Time", "Status", "Result"],
    },
    Settings: {
      icon: Settings,
      subtitle: "Manage your workspace preferences and account settings.",
      cards: [["Workspace", "BizPilot AI"], ["Account", "Active"], ["Role", "Manager"], ["Environment", "Development"]],
      rows: [["API Connection", "Backend", "127.0.0.1:8000", "Configured", "Local"], ["AI Routing", "Agent", "Semantic", "Configured", "Active"]],
      headers: ["Setting", "Category", "Value", "Status", "Environment"],
    },
  };

  const config = modules[page] || modules.Dashboard;
  const Icon = config.icon;

  return (
    <>
      <div className="page-heading">
        <div>
          <h1>{page}</h1>
          <p>{config.subtitle}</p>
        </div>
        <button className="primary-button" onClick={() => alert("This action will be connected to the backend when the corresponding API is implemented.")}>
          <Sparkles size={16} /> New {page === "Inventory" ? "Product" : page === "Suppliers" ? "Supplier" : page === "Procurement" ? "Purchase Order" : "Report"}
        </button>
      </div>

      <div className="demo-banner">
        <ActivitySquare size={15} />
        Demonstration data · These records are illustrative, not live business records
      </div>

      <div className="metrics-grid module-metrics">
        {config.cards.map(([title, value], index) => (
          <MetricCard
            key={title}
            icon={[Icon, TrendingUp, Clock3, CreditCard][index]}
            title={title}
            value={value}
            change={index % 2 === 0 ? "8.2%" : "3.4%"}
            positive={index % 2 === 0}
            tone={["green", "blue", "purple", "cyan"][index]}
          />
        ))}
      </div>

      <section className="panel module-table-panel">
        <SectionHeader
          icon={Icon}
          title={`${page} Overview`}
          action={{ label: "Export", onClick: () => window.print() }}
        />

        <div className="table-scroll">
          <table>
            <thead>
              <tr>
                {config.headers.map((header) => <th key={header}>{header}</th>)}
              </tr>
            </thead>
            <tbody>
              {config.rows.map((row, rowIndex) => (
                <tr key={rowIndex}>
                  {row.map((cell, cellIndex) => (
                    <td key={cellIndex}>
                      {cellIndex === row.length - 1 ? (
                        <span className={`status-badge ${String(cell).toLowerCase().replaceAll(" ", "-")}`}>
                          {cell}
                        </span>
                      ) : cell}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <div className="panel module-note">
        <div className="module-note-icon"><Icon size={22} /></div>
        <div>
          <h3>Connect your business data</h3>
          <p>This screen currently uses clearly labelled demonstration records. The live API for this module has not been implemented yet.</p>
        </div>
      </div>
    </>
  );
}

function AssistantPanel({ currentPage }) {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState([]);
  const [busy, setBusy] = useState(false);
  const [expanded, setExpanded] = useState(false);
  const [minimized, setMinimized] = useState(false);

  async function sendMessage(text) {
    const query = (text || input).trim();
    if (!query || busy) return;

    setMessages((old) => [...old, { role: "user", text: query }]);
    setInput("");
    setBusy(true);

    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL || "http://127.0.0.1:8000"}/api/route`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "The request could not be processed.");
      }

      const destination = {
        PAGE_DASHBOARD: "Dashboard",
        PAGE_INVENTORY: "Inventory",
        PAGE_SUPPLIERS: "Suppliers",
        PAGE_PROCUREMENT: "Procurement",
        PAGE_SALES: "Sales & Orders",
        PAGE_LOGISTICS: "Logistics",
        PAGE_FINANCE: "Finance",
        PAGE_ANALYTICS: "Analytics",
      }[data.page_id];

      const answer = destination
        ? `I matched your request to ${destination}. I can help you navigate there. The current routing API identifies the relevant module, but it does not yet retrieve or analyze live business records.`
        : "I couldn't confidently identify a business module for that request. Try mentioning inventory, suppliers, purchase orders, sales, logistics, finance, or analytics.";

      setMessages((old) => [...old, {
        role: "assistant",
        text: answer,
        destination,
      }]);
    } catch {
      setMessages((old) => [...old, {
        role: "assistant",
        text: "I couldn't connect to the BizPilot AI backend. Check that FastAPI is running at http://127.0.0.1:8000 and that the backend allows requests from this frontend.",
      }]);
    } finally {
      setBusy(false);
    }
  }

  if (minimized) {
    return (
      <button className="assistant-restore" onClick={() => setMinimized(false)}>
        <Bot size={22} /> <span>BizPilot AI Assistant</span>
        <MessageCircle size={19} />
      </button>
    );
  }

  return (
    <aside className={`assistant-panel ${expanded ? "assistant-expanded" : ""}`}>
      <div className="assistant-heading">
        <div className="assistant-bot-icon"><Bot size={25} /></div>

        <div className="assistant-heading-copy">
          <strong>BizPilot AI Assistant</strong>
          <span><i className="online-dot" /> Online</span>
        </div>

        <div className="assistant-window-actions">
          <button title="Expand assistant" onClick={() => setExpanded(!expanded)}>
            <Maximize2 size={16} />
          </button>
          <button title="Minimize assistant" onClick={() => setMinimized(true)}>
            <Minus size={18} />
          </button>
          <button title="Close assistant" onClick={() => setMinimized(true)}>
            <X size={19} />
          </button>
        </div>
      </div>

      <div className="assistant-scroll">
        <div className="assistant-welcome">
          <h3>👋 Hi there!</h3>
          <p>I'm your AI business assistant. I can help you:</p>

          {[
            "Navigate through any page",
            "Route business questions",
            "Find relevant business modules",
            "Help prepare reports",
            "Answer questions about the current page",
          ].map((item) => (
            <div className="assistant-capability" key={item}>
              <Check size={13} />
              <span>{item}</span>
            </div>
          ))}
        </div>

        <div className="suggestion-section">
          <span className="suggestion-label">Try these suggestions:</span>
          {suggestions.map((suggestion) => (
            <button
              className="suggestion-button"
              key={suggestion}
              onClick={() => sendMessage(suggestion)}
              disabled={busy}
            >
              <MessageCircle size={14} />
              <span>{suggestion}</span>
            </button>
          ))}
        </div>

        <div className="conversation">
          {messages.map((message, index) => (
            <ChatMessage key={index} user={message.role === "user"}>
              <p>{message.text}</p>
              {message.destination && (
                <button
                  className="inline-navigation"
                  onClick={() => window.dispatchEvent(new CustomEvent("navigate-page", { detail: message.destination }))}
                >
                  Open {message.destination}
                </button>
              )}
            </ChatMessage>
          ))}

          {busy && (
            <ChatMessage>
              <div className="typing-indicator"><i /><i /><i /></div>
            </ChatMessage>
          )}
        </div>
      </div>

      <form
        className="assistant-composer"
        onSubmit={(event) => {
          event.preventDefault();
          sendMessage();
        }}
      >
        <div className="composer-input-wrap">
          <input
            value={input}
            onChange={(event) => setInput(event.target.value)}
            placeholder="Ask me anything..."
            aria-label="Ask BizPilot AI"
          />
          <button className="send-button" type="submit" disabled={busy || !input.trim()} aria-label="Send">
            <Send size={18} />
          </button>
        </div>

        <div className="composer-shortcuts">
          <button type="button" onClick={() => sendMessage(`Navigate to the ${currentPage} page`)}>
            <LayoutDashboard size={12} /> Navigate
          </button>
          <button type="button" onClick={() => sendMessage(`Analyze ${currentPage}`)}>
            <BarChart3 size={12} /> Analyze
          </button>
          <button type="button" onClick={() => sendMessage("Create a purchase order draft")}>
            <ClipboardList size={12} /> Create
          </button>
          <button type="button" onClick={() => sendMessage("Find low stock items")}>
            <Search size={12} /> Find
          </button>
          <button type="button" aria-label="Voice input" onClick={() => alert("Voice input will be added in a later step.")}>
            <Mic size={15} />
          </button>
        </div>
      </form>
    </aside>
  );
}

export default function App() {
  const [activePage, setActivePage] = useState("Dashboard");
  const [search, setSearch] = useState("");
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const allPages = [...navigation, ...secondaryNavigation];

  function navigate(page) {
    setActivePage(page);
    setSidebarOpen(false);
  }

  window.onNavigatePage = navigate;

  if (!window.__bizpilotNavigationListener) {
    window.addEventListener("navigate-page", (event) => {
      window.onNavigatePage?.(event.detail);
    });
    window.__bizpilotNavigationListener = true;
  }

  const searchResults = search.trim()
    ? allPages.filter((item) =>
        item.label.toLowerCase().includes(search.trim().toLowerCase())
      )
    : [];

  return (
    <div className="app-shell">
      <header className="topbar">
        <button
          className="mobile-menu"
          onClick={() => setSidebarOpen(!sidebarOpen)}
          aria-label="Toggle navigation"
        >
          <Menu size={23} />
        </button>

        <div className="brand">
          <div className="brand-mark">
            <span />
            <span />
            <span />
            <span />
          </div>

          <div>
            <strong>BizPilot AI</strong>
            <span>Supply Chain & Business Operations</span>
          </div>
        </div>

        <div className="global-search">
          <Search size={20} />
          <input
            placeholder="Search anything... (e.g. products, suppliers, orders, reports)"
            value={search}
            onChange={(event) => setSearch(event.target.value)}
            onKeyDown={(event) => {
              if (event.key === "Enter" && searchResults.length) {
                navigate(searchResults[0].label);
                setSearch("");
              }
            }}
          />

          {searchResults.length > 0 && (
            <div className="search-results">
              {searchResults.map((item) => (
                <button
                  key={item.label}
                  onClick={() => {
                    navigate(item.label);
                    setSearch("");
                  }}
                >
                  <item.icon size={16} />
                  {item.label}
                </button>
              ))}
            </div>
          )}
        </div>

        <button className="notification-button" title="Notifications">
          <Bell size={22} />
          <span>3</span>
        </button>

        <div className="topbar-divider" />

        <button className="profile-button">
          <div className="profile-avatar">M</div>
          <div className="profile-details">
            <strong>Demo Manager</strong>
            <span>Demo profile</span>
          </div>
          <ChevronDown size={17} />
        </button>
      </header>

      <div className="workspace">
        <aside className={`sidebar ${sidebarOpen ? "sidebar-open" : ""}`}>
          <div className="sidebar-nav">
            {navigation.map((item) => {
              const Icon = item.icon;
              const active = activePage === item.label;

              return (
                <button
                  key={item.label}
                  className={`nav-item ${active ? "active" : ""}`}
                  onClick={() => navigate(item.label)}
                >
                  <Icon size={21} strokeWidth={1.9} />
                  <span>{item.label}</span>
                </button>
              );
            })}

            <div className="sidebar-divider" />

            {secondaryNavigation.map((item) => {
              const Icon = item.icon;
              const active = activePage === item.label;

              return (
                <button
                  key={item.label}
                  className={`nav-item ${active ? "active" : ""}`}
                  onClick={() => navigate(item.label)}
                >
                  <Icon size={21} strokeWidth={1.9} />
                  <span>{item.label}</span>
                  {item.badge && <span className="nav-badge">{item.badge}</span>}
                </button>
              );
            })}
          </div>

          <div className="plan-card">
            <span>Current Plan</span>
            <strong>BizPilot AI</strong>
            <small>Development Preview</small>
            <div className="plan-status"><i /> Local environment</div>
          </div>
        </aside>

        {sidebarOpen && (
          <button
            className="sidebar-backdrop"
            onClick={() => setSidebarOpen(false)}
            aria-label="Close navigation"
          />
        )}

        <main className="main-content">
          {activePage === "Dashboard" ? (
            <DashboardContent />
          ) : (
            <ModulePage page={activePage} />
          )}
        </main>

        <AssistantPanel currentPage={activePage} />
      </div>
    </div>
  );
}