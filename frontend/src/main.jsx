import React, { useEffect, useMemo, useState } from "react";
import { createRoot } from "react-dom/client";
import { Area, AreaChart, CartesianGrid, Line, Pie, PieChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import {
  Activity, AlertTriangle, ArrowDownRight, ArrowUpRight, BarChart3, Bell, Box, Check,
  CheckCircle2, ChevronDown, CircleHelp, ClipboardCheck, Clock3, Command, FileChartColumn,
  FileText, Filter, LayoutDashboard, Lightbulb, MapPin, Menu, MessageCircle, Minus,
  Package, PackageCheck, PanelRightClose, Plus, Search, Send, Settings, ShieldCheck,
  ShoppingCart, Sparkles, Truck, Users, Wallet, Warehouse, X, Zap
} from "lucide-react";
import "./styles.css";

const API = import.meta.env.VITE_API_URL || "http://localhost:8000";
const navItems = [
  ["Dashboard","/dashboard",LayoutDashboard],["Inventory","/inventory",Package],["Suppliers","/suppliers",Users],
  ["Procurement","/procurement",FileText],["Sales & Orders","/sales",ShoppingCart],["Logistics","/logistics",Truck],
  ["Finance","/finance",Wallet],["Analytics","/analytics",BarChart3],["Approvals","/approvals",ClipboardCheck],
  ["Reports","/reports",FileChartColumn],["Agent Activity","/agent-activity",Activity],["Settings","/settings",Settings]
];
const suggestions = [
  "Show me products likely to run out in 14 days",
  "Compare top 3 suppliers for steel with best pricing",
  "Create purchase order for low stock items",
  "Show last 12 months sales analysis",
  "What is the current page and key information?"
];
const fallbackDashboard = {
  total_revenue:2480000,revenue_change:12.5,total_orders:5842,orders_change:18.2,
  inventory_value:1120000,inventory_change:-5.3,active_suppliers:48,suppliers_change:9.1,
  inventory_total:1245,in_stock:975,low_stock:187,out_of_stock:83,fulfillment_rate:92,delayed_orders:470,
  monthly:[{month:"Jan",revenue:100,orders:30},{month:"Feb",revenue:150,orders:70},{month:"Mar",revenue:205,orders:90},{month:"Apr",revenue:300,orders:100},{month:"May",revenue:315,orders:180},{month:"Jun",revenue:210,orders:155},{month:"Jul",revenue:140,orders:200},{month:"Aug",revenue:180,orders:280},{month:"Sep",revenue:230,orders:330},{month:"Oct",revenue:150,orders:220},{month:"Nov",revenue:140,orders:225},{month:"Dec",revenue:240,orders:350}],
  products:[
    {product_id:"PRD-0001",name:"Steel Rod (SR-001)",stock:500,reorder_level:1000,unit_cost:36},
    {product_id:"PRD-0002",name:"Plastic Resin (PR-002)",stock:200,reorder_level:800,unit_cost:162.5},
    {product_id:"PRD-0003",name:"Copper Wire (CW-003)",stock:300,reorder_level:1200,unit_cost:40},
    {product_id:"PRD-0004",name:"Aluminum Sheet (AS-004)",stock:250,reorder_level:1000,unit_cost:28}
  ],
  purchase_orders:[
    {po_id:"PO-2024-089",supplier:"Global Metals Ltd.",status:"Approved",amount:45000,date:"Dec 10"},
    {po_id:"PO-2024-088",supplier:"Prime Plastics",status:"Pending",amount:32500,date:"Dec 09"},
    {po_id:"PO-2024-087",supplier:"Steel Supplies Co.",status:"Approved",amount:28750,date:"Dec 08"},
    {po_id:"PO-2024-086",supplier:"MetalWorks Inc.",status:"Draft",amount:15200,date:"Dec 08"},
    {po_id:"PO-2024-085",supplier:"Asia Components",status:"Approved",amount:60000,date:"Dec 07"}
  ]
};
const rolePerms = {
  Owner:["Full business visibility","Manage users and policies","Review and approve consequential actions"],
  Manager:["Operational analytics","Prepare procurement drafts","Coordinate suppliers and logistics"],
  Warehouse:["Inventory and warehouse tasks","Receive and transfer stock","Report discrepancies"],
  Viewer:["Read-only dashboards","Ask analytical questions","No record modifications"]
};
const money = n => "$"+Number(n||0).toLocaleString("en-US",{maximumFractionDigits:0});
// Lightweight offline spelling/phrase normalization for common supply-chain requests.
function normalizeBusinessQuery(value) {
  let q = String(value || "").toLowerCase().trim();
  const fixes = [
    [/\b(stok|stoks|inventry|inventori|warehose|warehous)\b/g, "inventory"],
    [/\b(suplyer|supplir|suplier|vendorz)\b/g, "supplier"],
    [/\b(purchse|purchas|pruchase|purhcase)\b/g, "purchase"],
    [/\b(analitics|analytcs|anaylsis|analyis)\b/g, "analytics"],
    [/\b(reveneu|revnue|revinue)\b/g, "revenue"],
    [/\b(delivary|delivry|shiping|shippment|shipement)\b/g, "delivery"],
    [/\b(oder|ordr|ordres)\b/g, "orders"],
    [/\b(approvel|aprove|apprvoe)\b/g, "approval"],
    [/\b(reoder|re-order|reordr)\b/g, "reorder"],
    [/\b(prduct|prodcut|prodcts)\b/g, "product"],
    [/\b(quantites|quanity|qantity)\b/g, "quantity"],
    [/\b(finace|finacial)\b/g, "finance"],
    [/\b(logisitcs|logistic)\b/g, "logistics"],
    [/\b(show me|tell me|can you show|please show)\b/g, "show"],
    [/\b(what is|what are|can you tell me)\b/g, "show"]
  ];
  for (const [pattern, replacement] of fixes) q = q.replace(pattern, replacement);
  return q.replace(/\s+/g, " ");
}
function IconBox({children,tone="blue"}) { return <div className={`icon-box ${tone}`}>{children}</div>; }
function Status({value}) {
  const cls = String(value).toLowerCase().replaceAll(" ","-");
  return <span className={`status ${cls}`}>{value}</span>;
}
function Login({onLogin}) {
  const [role,setRole] = useState("Manager");
  const [email,setEmail] = useState("manager@bizpilot.demo");
  const [password,setPassword] = useState("Demo123!");
  const [error,setError] = useState("");
  return <div className="login-page">
    <div className="login-art">
      <div className="brand"><div className="brand-mark"><span/><span/><span/><span/></div><div><b>BizPilot AI</b><small>Supply Chain & Business Operations</small></div></div>
      <div className="login-hero"><div className="eyebrow"><Sparkles size={15}/> CONTEXT-AWARE BUSINESS COPILOT</div><h1>Your business.<br/><em>One intelligent</em><br/>conversation away.</h1><p>Navigate operations, understand your data, and turn business questions into verified actions.</p>
        <div className="login-stats"><div><b>10+</b><small>Connected pages</small></div><div><b>4</b><small>Business roles</small></div><div><b>24 mo</b><small>Analytics-ready</small></div></div>
      </div>
      <div className="login-foot">BUILT FOR CONTEXT. DESIGNED FOR ACTION.</div>
    </div>
    <div className="login-form-wrap"><form className="login-form" onSubmit={e=>{e.preventDefault();setError("");onLogin({name:role==="Owner"?"Alex Morgan":role==="Manager"?"Michael Smith":role==="Warehouse"?"Jordan Lee":"Taylor Reed",role,email});}}>
      <div className="mobile-brand brand"><div className="brand-mark"><span/><span/><span/><span/></div><div><b>BizPilot AI</b><small>Supply Chain & Business Operations</small></div></div>
      <span className="eyebrow">WELCOME BACK</span><h2>Sign in to your workspace</h2><p>Access your business workspace and AI assistant.</p>
      <label>Work email<input value={email} onChange={e=>setEmail(e.target.value)} type="email" required /></label>
      <label>Password<input value={password} onChange={e=>setPassword(e.target.value)} type="password" required /></label>
      <label>Your demo role<select value={role} onChange={e=>{setRole(e.target.value);setEmail(e.target.value.toLowerCase()+"@bizpilot.demo");}}>{["Owner","Manager","Warehouse","Viewer"].map(r=><option key={r}>{r}</option>)}</select></label>
      <button className="primary full" type="submit">Sign in securely <span>→</span></button>
      {error&&<p className="error">{error}</p>}
      <div className="login-note"><ShieldCheck size={16}/> Demo environment · Synthetic business data only</div>
    </form></div>
  </div>;
}
function App() {
  const [user,setUser] = useState(null);
  const [page,setPage] = useState("Dashboard");
  const [dashboard,setDashboard] = useState(fallbackDashboard);
  const [products,setProducts] = useState(fallbackDashboard.products);
  const [suppliers,setSuppliers] = useState([]);
  const [pos,setPos] = useState(fallbackDashboard.purchase_orders);
  const [assistantOpen,setAssistantOpen] = useState(true);
  const [input,setInput] = useState("");
  const [messages,setMessages] = useState([]);
  const [busy,setBusy] = useState(false);
  const [draft,setDraft] = useState(null);
  const [globalSearch,setGlobalSearch] = useState("");
  const [dateRange,setDateRange] = useState("Jan 2024 - Dec 2024");
  const [location,setLocation] = useState("All Locations");
  const [toast,setToast] = useState("");
  const [pendingAction,setPendingAction] = useState(null);

  useEffect(()=>{fetch(`${API}/api/dashboard`).then(r=>r.ok?r.json():null).then(d=>d&&setDashboard(d)).catch(()=>{});fetch(`${API}/api/inventory`).then(r=>r.ok?r.json():null).then(d=>d&&setProducts(d)).catch(()=>{});fetch(`${API}/api/suppliers`).then(r=>r.ok?r.json():null).then(d=>d&&setSuppliers(d)).catch(()=>{});fetch(`${API}/api/purchase-orders`).then(r=>r.ok?r.json():null).then(d=>d&&setPos(d)).catch(()=>{});},[]);
  useEffect(()=>{if(user){setMessages([{role:"assistant",text:`Hi ${user.name.split(" ")[0]}! I'm your BizPilot AI business assistant. I can navigate pages, analyze authorized business data, fill forms, prepare drafts, and explain the current page. I'll ask before consequential actions.`}]);}},[user]);
  const go = (name) => {setPage(name);setToast("");};
  const currentSuggestions = useMemo(()=>page==="Inventory"?[suggestions[0],"Show stock below reorder level","Compare stock across locations"]:page==="Procurement"?[suggestions[2],"Show purchase orders awaiting approval","Compare supplier lead times"]:suggestions, [page]);
  const notify = (text) => {setToast(text);setTimeout(()=>setToast(""),3200);};
  function resolvePageIntent(value) {
    const q=normalizeBusinessQuery(value);
    if (/\b(inventory|stock|warehouse|reorder|out of stock|low stock|sku|product stock|run out)\b/.test(q)) return "Inventory";
    if (/\b(supplier|vendor|lead time|supplier pricing|supplier reliability)\b/.test(q)) return "Suppliers";
    if (/\b(procurement|purchase order|purchase orders|buying|replenish|create po|new po)\b/.test(q)) return "Procurement";
    if (/\b(sales & orders|customer orders|sales order|order status|orders|fulfillment)\b/.test(q)) return "Sales & Orders";
    if (/\b(logistics|shipment|shipments|delivery|deliveries|tracking|delayed delivery|in transit)\b/.test(q)) return "Logistics";
    if (/\b(finance|cash flow|expenses|expense|invoice|payment|overdue|profit|costs)\b/.test(q)) return "Finance";
    if (/\b(analytics|revenue|trend|trends|growth|performance|forecast|sales analysis|analyze sales)\b/.test(q)) return "Analytics";
    if (/\b(approval|approvals|pending approval|approve)\b/.test(q)) return "Approvals";
    if (/\b(report|reports|export report|monthly report|supplier scorecard)\b/.test(q)) return "Reports";
    if (/\b(agent activity|agent logs|task history|assistant activity)\b/.test(q)) return "Agent Activity";
    if (/\b(settings|my role|permissions|profile|workspace settings)\b/.test(q)) return "Settings";
    if (/\b(dashboard|overview|home|business summary)\b/.test(q)) return "Dashboard";
    return null;
  }
  function localAnswer(value, target) {
    const q=normalizeBusinessQuery(value);
    if (target === "Inventory") {
      const low=products.filter(p=>Number(p.stock)<=Number(p.reorder_level));
      if (/how many|count|number of|total/.test(q) && /product|item|stock/.test(q)) return `The current inventory list has ${products.length} products. ${low.length} are at or below their reorder level. This is based on the data currently loaded in the demo.`;
      if (/low stock|run out|reorder|out of stock/.test(q)) return low.length ? `I found ${low.length} products at or below their reorder level: ${low.map(p=>`${p.name} (${p.stock} in stock; reorder level ${p.reorder_level})`).join('; ')}. I opened Inventory so you can review them.` : "No products in the currently loaded list are at or below their reorder level. I opened Inventory for review.";
      return `I opened Inventory. You can search products, view stock against reorder levels, and prepare a purchase-order draft if your role allows it. ${low.length} listed products are at or below reorder level.`;
    }
    if (target === "Suppliers") return `I opened Suppliers. The page shows supplier reliability and lead times for the supplier records currently loaded. ${suppliers.length ? `${suppliers.length} supplier records came from the API.` : "The page is showing demo supplier examples because no supplier records were returned by the API."}`;
    if (target === "Procurement") return `I opened Procurement, where purchase orders and drafts are reviewed. There are ${pos.length} purchase orders in the currently loaded list. I won't submit an order without an explicit review/confirmation.`;
    if (target === "Analytics") return `I opened Analytics. The currently loaded demo metrics show revenue of ${money(dashboard.total_revenue)} and ${Number(dashboard.total_orders||0).toLocaleString()} orders. These figures may be synthetic; verify the connected data before making business decisions.`;
    if (target === "Dashboard") return `I opened the Dashboard overview. The currently loaded metrics show revenue of ${money(dashboard.total_revenue)}, ${Number(dashboard.total_orders||0).toLocaleString()} orders, inventory value of ${money(dashboard.inventory_value)}, and ${dashboard.active_suppliers} active suppliers. Demo data may be synthetic.`;
    const descriptions={"Sales & Orders":"customer orders and fulfillment","Logistics":"shipments, delivery timelines and exceptions","Finance":"cash flow, expenses and outstanding transactions","Approvals":"items awaiting authorization","Reports":"available business reports","Agent Activity":"assistant task history and performance","Settings":"your demo profile and workspace permissions"};
    return `I opened ${target}. This page covers ${descriptions[target]||"the relevant business information"}. The current workspace is a demo, so confirm figures against your real system before acting.`;
  }
  async function sendMessage(text=input) {
    const value=text.trim(); if(!value||busy)return;
    const understoodValue=normalizeBusinessQuery(value);
    setInput("");setMessages(m=>[...m,{role:"user",text:value}]);setBusy(true);setPendingAction(null);
    let routeTarget=resolvePageIntent(understoodValue);
    if (!routeTarget && /\b(navigate|open|go to|take me to|show|find|search|analy[sz]e|summari[sz]e|compare|check|list|count|how many|what is|what are)\b/.test(understoodValue)) {
      routeTarget = resolvePageIntent(understoodValue + " " + page);
    }
    // Route-related requests use deterministic local context first, so a weak or unavailable API
    // cannot prevent navigation or produce an unrelated generic answer.
    if (routeTarget) {
      go(routeTarget);
      setMessages(m=>[...m,{role:"assistant",text:localAnswer(value,routeTarget),actions:[],suggestions:[]}]);
      setBusy(false);
      return;
    }
    try {
      const res=await fetch(`${API}/api/agent/chat`,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({message:value,role:user?.role||"Viewer",current_page:page})});
      if(!res.ok)throw new Error("API unavailable"); const data=await res.json();
      if(data.route){const target=navItems.find(n=>n[1]===data.route);if(target)go(target[0]);}
      if(data.intent==="navigate_analyze" && user?.role==="Manager" && /create|purchase order|draft/i.test(value)) {
        setPendingAction({type:"draft",product:products[0],quantity:100});
      }
      setMessages(m=>[...m,{role:"assistant",text:data.message||"I completed the request.",actions:data.actions||[],suggestions:data.suggestions||[]}]);
    } catch {
      const low=normalizeBusinessQuery(value);
      let target=null,reply="I can help navigate the workspace, answer questions from the data loaded here, compare suppliers, and prepare drafts. I could not confidently identify the requested task. Try naming a module or record, such as inventory, suppliers, orders, deliveries, finance, or revenue.";
      if(/inventory|stock|run out/.test(low)){target="Inventory";reply="I’ll inspect current stock against reorder thresholds and highlight items that need attention.";}
      else if(/supplier|pricing/.test(low)){target="Suppliers";reply="I’ll open supplier management so you can compare pricing, lead times and reliability.";}
      else if(/procurement|purchase|draft/.test(low)){target="Procurement";reply="I’ve opened Procurement. We can prepare a draft and review its fields before submitting.";}
      else if(/analytics|revenue|sales|report/.test(low)){target="Analytics";reply="I’ll open Analytics to review the available business trends.";}
      else if(/current page|what am i looking at/.test(low)){reply=`You are on ${page}. ${pageDescriptions[page]||"This module shows relevant business records and actions."}`;}
      if(target)go(target);
      setMessages(m=>[...m,{role:"assistant",text:reply,actions:target?[`Open ${target}`]:[],suggestions:currentSuggestions}]);
    } finally {setBusy(false);}
  }
  async function prepareDraft(product=products[0],quantity=100) {
    if(user?.role==="Viewer"||user?.role==="Warehouse"){notify("Your role cannot create purchase-order drafts.");return;}
    setPendingAction(null);
    try {
      const res=await fetch(`${API}/api/purchase-orders/drafts`,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({product_id:product.product_id,quantity})});
      if(res.ok){const d=await res.json();setDraft(d.draft);setMessages(m=>[...m,{role:"assistant",text:"I prepared an unsaved purchase-order draft. Review the populated fields below. No order has been submitted."}]);}
      else throw new Error();
    } catch {
      setDraft({po_id:"PO-DRAFT-DEMO",product:product.name,product_id:product.product_id,quantity, supplier:"Global Metals Ltd.",unit_cost:product.unit_cost,amount:product.unit_cost*quantity,state:"Unsaved"});
    }
    go("Procurement");
  }
  function commitDemoDraft() {
    if(!draft)return;
    if(user?.role!=="Owner"){notify("Only the Owner can confirm this demo purchase order.");return;}
    setDraft({...draft,state:"Submitted for approval"});
    setMessages(m=>[...m,{role:"assistant",text:`Confirmed. ${draft.po_id} is now marked as submitted for approval in this demo UI. This starter does not persist the submission to a database.`}]);
    notify("Demo status updated — not persisted");
  }
  const moneyText = n => money(n);
  return user ? <div className="app-shell">
    <aside className="sidebar">
      <div className="side-brand"><div className="brand-mark"><span/><span/><span/><span/></div><div><b>BizPilot AI</b><small>Supply Chain & Business Operations</small></div></div>
      <nav>{navItems.map(([name,route,Icon])=><button key={name} className={`nav-item ${page===name?"active":""}`} onClick={()=>go(name)}><Icon size={19}/><span>{name}</span>{name==="Approvals"&&<b className="nav-count">5</b>}</button>)}</nav>
      <div className="sidebar-bottom"><div className="plan-label">CURRENT PLAN</div><b>BizPilot AI Pro</b><small>Version 0.1.0 · Demo</small><div className="api-status"><span/> API connection optional</div></div>
    </aside>
    <main className="main-area">
      <header className="topbar">
        <button className="mobile-menu icon-button" onClick={()=>notify("Use the sidebar to navigate.")}><Menu size={20}/></button>
        <div className="global-search"><Search size={19}/><input placeholder="Search anything… (e.g. products, suppliers, orders, reports)" value={globalSearch} onChange={e=>setGlobalSearch(e.target.value)} onKeyDown={e=>e.key==="Enter"&&sendMessage(`Search the application for ${globalSearch}`)}/><kbd>⌘ K</kbd></div>
        <button className="icon-button notification" onClick={()=>go("Approvals")}><Bell size={20}/><i>3</i></button>
        <button className="profile" onClick={()=>setToast(toast?"":`Signed in as ${user.role}`)}><span className="avatar">{user.name[0]}</span><span className="profile-copy"><b>{user.name}</b><small>{user.role}</small></span><ChevronDown size={16}/></button>
      </header>
      <div className="content-scroll">
        <div className="page-heading"><div><h1>{page}</h1>{page!=="Dashboard"&&<p>{pageDescriptions[page]||"Explore authorized business information and operational workflows."}</p>}</div><div className="page-filters"><select value={dateRange} onChange={e=>setDateRange(e.target.value)}><option>Jan 2024 - Dec 2024</option><option>Last 30 days</option><option>Last 90 days</option><option>Last 12 months</option></select><select value={location} onChange={e=>setLocation(e.target.value)}><option>All Locations</option><option>Bengaluru Central</option><option>Pune Distribution</option><option>Delhi North Hub</option></select></div></div>
        {page==="Dashboard"&&<Dashboard dashboard={dashboard} products={products} pos={pos} onView={go} onDraft={()=>prepareDraft(products[0],100)}/>}
        {page==="Inventory"&&<Inventory products={products} onDraft={p=>prepareDraft(p,Math.max(1,p.reorder_level-p.stock))} role={user.role}/>}
        {page==="Suppliers"&&<Suppliers suppliers={suppliers} products={products}/>}
        {page==="Procurement"&&<Procurement pos={pos} draft={draft} setDraft={setDraft} onConfirm={commitDemoDraft} role={user.role} onPrepare={()=>prepareDraft(products[0],100)}/>}
        {page==="Sales & Orders"&&<GenericPage title="Sales & Customer Orders" icon={<ShoppingCart/>} stats={[["Total orders","5,842"],["Delivered","4,091"],["Processing","584"],["Returned","175"]]} rows={["SO-2024-1048","SO-2024-1047","SO-2024-1046","SO-2024-1045"]}/>}
        {page==="Logistics"&&<GenericPage title="Logistics & Deliveries" icon={<Truck/>} stats={[["On time","92%"],["In transit","184"],["Delayed","47"],["Exceptions","12"]]} rows={["DLV-00124","DLV-00123","DLV-00122","DLV-00121"]}/>}
        {page==="Finance"&&<GenericPage title="Finance & Cash Flow" icon={<Wallet/>} stats={[["Cash inflow","$1.82M"],["Cash outflow","$1.21M"],["Pending","$84K"],["Overdue","$32K"]]} rows={["FIN-000124","FIN-000123","FIN-000122","FIN-000121"]}/>}
        {page==="Analytics"&&<Analytics dashboard={dashboard}/>}
        {page==="Approvals"&&<GenericPage title="Approval queue" icon={<ClipboardCheck/>} stats={[["Pending approvals","5"],["Purchase orders","3"],["Expenses","1"],["Stock adjustments","1"]]} rows={["PO-2024-088","PO-2024-091","PO-2024-092","EXP-00034"]}/>}
        {page==="Reports"&&<GenericPage title="Reports" icon={<FileChartColumn/>} stats={[["Available reports","18"],["Scheduled","4"],["Recent exports","12"],["Shared reports","6"]]} rows={["Monthly revenue","Inventory health","Supplier scorecard","Delivery performance"]}/>}
        {page==="Agent Activity"&&<GenericPage title="Agent Activity" icon={<Activity/>} stats={[["Tasks today","34"],["Success rate","94%"],["Median latency","1.2s"],["Actions awaiting review","3"]]} rows={["Stockout risk analysis","Supplier comparison","Purchase order draft","Revenue comparison"]}/>}
        {page==="Settings"&&<SettingsPage user={user}/>}
      </div>
    </main>
    {assistantOpen?<aside className="assistant-panel">
      <div className="assistant-header"><div className="bot-avatar"><Sparkles size={19}/></div><div className="assistant-title"><b>BizPilot AI Assistant</b><small><span className="online-dot"/> Online · {page}</small></div><button className="icon-button" onClick={()=>setAssistantOpen(false)} title="Close assistant"><X size={18}/></button></div>
      <div className="assistant-scroll">
        {messages.map((m,i)=><div key={i} className={`message ${m.role}`}><div className="message-avatar">{m.role==="assistant"?<div className="mini-bot"><Sparkles size={14}/></div>:user.name[0]}</div><div className="message-body"><div className="bubble">{m.text}</div>{m.actions?.length>0&&<div className="action-chips">{m.actions.map(a=><button key={a} onClick={()=>sendMessage(a)}>{a}<span>→</span></button>)}</div>}{m.suggestions?.length>0&&<div className="mini-suggestions">{m.suggestions.map(s=><button key={s} onClick={()=>sendMessage(s)}>{s}</button>)}</div>}</div></div>)}
        {busy&&<div className="message assistant"><div className="message-avatar"><div className="mini-bot"><Sparkles size={14}/></div></div><div className="message-body"><div className="bubble">Understanding your request and checking available business context…<div className="typing"><i/><i/><i/></div></div></div></div>}
        {!messages.some(m=>m.role==="user")&&<div className="suggestions-block"><b>Try these suggestions</b>{currentSuggestions.map(s=><button key={s} onClick={()=>sendMessage(s)}><MessageCircle size={14}/>{s}</button>)}</div>}
        {pendingAction&&<div className="pending-card"><b>Action preview</b><p>{pendingAction.type==="draft"?"Prepare an unsaved purchase order draft for "+pendingAction.product.name:"Review requested action"}</p><div className="pending-actions"><button className="secondary" onClick={()=>setPendingAction(null)}>Cancel</button><button className="primary" onClick={()=>prepareDraft(pendingAction.product,pendingAction.quantity)}>Prepare draft</button></div></div>}
      </div>
      <div className="composer-wrap"><div className="quick-tools"><button onClick={()=>sendMessage("Navigate to "+page)}><MapPin size={13}/> Navigate</button><button onClick={()=>sendMessage("Analyze "+page)}><BarChart3 size={13}/> Analyze</button><button onClick={()=>sendMessage("Create a purchase order draft")}><Plus size={13}/> Create</button><button onClick={()=>sendMessage("Find low stock items")}><Search size={13}/> Find</button></div><form className="composer" onSubmit={e=>{e.preventDefault();sendMessage();}}><textarea value={input} onChange={e=>setInput(e.target.value)} onKeyDown={e=>{if(e.key==="Enter"&&!e.shiftKey){e.preventDefault();sendMessage();}}} placeholder="Ask me anything…" rows="1"/><button type="submit" disabled={!input.trim()||busy} className="send-button"><Send size={17}/></button></form><div className="composer-foot"><span><span className="online-dot"/> Context: {page}</span><span>Enter to send · Shift+Enter for newline</span></div></div>
    </aside>:<button className="reopen-assistant" onClick={()=>setAssistantOpen(true)}><Sparkles size={19}/> BizPilot AI</button>}
    {toast&&<div className="toast"><CheckCircle2 size={17}/>{toast}<button onClick={()=>setToast("")}><X size={14}/></button></div>}
    <div className="app-disclaimer">DEMO DATA · Illustrative values, not live business records</div>
  </div>:<Login onLogin={setUser}/>;
}
const pageDescriptions = {
  "Dashboard":"Real-time overview of your supply chain and business operations",
  "Inventory":"Monitor stock levels, reorder points and warehouse movements",
  "Suppliers":"Compare supplier reliability, pricing and lead times",
  "Procurement":"Manage purchase orders, drafts and approval workflows",
  "Sales & Orders":"Track customer orders, sales performance and fulfillment",
  "Logistics":"Monitor shipments, delivery timelines and exceptions",
  "Finance":"Review cash flow, expenses and outstanding transactions",
  "Analytics":"Explore historical trends, comparisons and business insights",
  "Approvals":"Review actions that require your authorization",
  "Reports":"Generate and explore business reports",
  "Agent Activity":"Inspect assistant tasks, action history and performance",
  "Settings":"Manage your demo profile and workspace preferences"
};
function Dashboard({dashboard:d,products,onView,onDraft}) {
  const pieData=[{name:"In Stock",value:d.in_stock||975,color:"#18b77a"},{name:"Low Stock",value:d.low_stock||187,color:"#f2b635"},{name:"Out of Stock",value:d.out_of_stock||83,color:"#e44f64"}];
  return <div className="dashboard-grid">
    <section className="kpi-grid">
      <Kpi icon={<Package size={20}/>} tone="green" label="Total Revenue" value={money(d.total_revenue)} change={d.revenue_change} />
      <Kpi icon={<ShoppingCart size={20}/>} tone="blue" label="Total Orders" value={Number(d.total_orders).toLocaleString()} change={d.orders_change}/>
      <Kpi icon={<Box size={20}/>} tone="purple" label="Inventory Value" value={money(d.inventory_value)} change={d.inventory_change}/>
      <Kpi icon={<Users size={20}/>} tone="cyan" label="Active Suppliers" value={d.active_suppliers} change={d.suppliers_change}/>
    </section>
    <section className="panel trend-panel"><div className="panel-heading"><div><Activity size={18}/><h3>Revenue & Orders Trend</h3></div><select defaultValue="Last 12 Months"><option>Last 12 Months</option><option>Last 90 Days</option></select></div><div className="legend"><span><i className="blue-dot"/> Revenue (USD, thousands)</span><span><i className="green-dot"/> Orders</span></div><div className="chart"><ResponsiveContainer width="100%" height="100%"><AreaChart data={d.monthly}><defs><linearGradient id="revFill" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopColor="#3478f6" stopOpacity={.19}/><stop offset="100%" stopColor="#3478f6" stopOpacity={0}/></linearGradient></defs><CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e8edf5"/><XAxis dataKey="month" tickLine={false} axisLine={false} tick={{fontSize:10,fill:"#8290a5"}}/><YAxis tickLine={false} axisLine={false} tick={{fontSize:10,fill:"#8290a5"}} width={38}/><Tooltip/><Area type="monotone" dataKey="revenue" name="Revenue" stroke="#3478f6" strokeWidth={2.5} fill="url(#revFill)"/><Line type="monotone" dataKey="orders" name="Orders" stroke="#18b77a" strokeWidth={2.5} dot={false}/></AreaChart></ResponsiveContainer></div></section>
    <section className="panel inventory-panel"><div className="panel-heading"><div><ShoppingCart size={18}/><h3>Inventory Status</h3></div></div><div className="inventory-chart"><div className="donut"><ResponsiveContainer width="100%" height="100%"><PieChart><Pie data={pieData} dataKey="value" nameKey="name" innerRadius="67%" outerRadius="90%" paddingAngle={2} stroke="none">{pieData.map((p,i)=><CellSafe key={p.name} fill={p.color}/>)}</Pie><Tooltip/></PieChart></ResponsiveContainer><div className="donut-center"><b>{(d.inventory_total||1245).toLocaleString()}</b><small>Total Items</small></div></div><div className="legend-list">{pieData.map(p=><div key={p.name}><i style={{background:p.color}}/><span>{p.name}<b>{Math.round(p.value/(d.inventory_total||1245)*100)}% ({p.value})</b></span></div>)}</div></div></section>
    <section className="panel low-stock-panel"><div className="panel-heading"><div><AlertTriangle size={18}/><h3>Low Stock Alerts</h3></div><button className="link-button" onClick={()=>onView("Inventory")}>View all</button></div><div className="table-wrap"><table><thead><tr><th>Product</th><th>Current Stock</th><th>Reorder Level</th><th>Days Left</th></tr></thead><tbody>{products.slice(0,4).map((p,i)=><tr key={p.product_id}><td><span className={`product-thumb thumb-${i}`}>{["▤","▦","◉","▱"][i]}</span>{p.name}</td><td>{p.stock}</td><td>{p.reorder_level.toLocaleString()}</td><td><span className="days-pill">{[5,7,6,8][i]} days</span></td></tr>)}</tbody></table></div></section>
    <section className="panel purchase-panel"><div className="panel-heading"><div><ShoppingCart size={18}/><h3>Recent Purchase Orders</h3></div><button className="link-button" onClick={()=>onView("Procurement")}>View all</button></div><div className="table-wrap"><table><thead><tr><th>PO #</th><th>Supplier</th><th>Status</th><th>Amount</th><th>Date</th></tr></thead><tbody>{(d.purchase_orders||[]).slice(0,5).map(p=><tr key={p.po_id}><td>{p.po_id}</td><td>{p.supplier}</td><td><Status value={p.status}/></td><td>{money(p.amount)}</td><td>{p.date}</td></tr>)}</tbody></table></div></section>
    <section className="panel fulfillment-panel"><div className="panel-heading"><div><PackageCheck size={18}/><h3>Order Fulfillment Rate</h3></div></div><div className="fulfillment-content"><div className="ring" style={{"--pct":`${d.fulfillment_rate}%`}}><div><b>{d.fulfillment_rate}%</b><small>Orders delivered<br/>on time</small></div></div><div className="fulfillment-stats"><div><IconBox tone="green"><Check size={16}/></IconBox><span><b>{Number(d.total_orders).toLocaleString()}</b><small>Total Orders</small></span></div><div><IconBox tone="green"><CheckCircle2 size={16}/></IconBox><span><b>{Math.round(d.total_orders*.92).toLocaleString()}</b><small>Delivered On Time</small></span></div><div><IconBox tone="red"><ArrowDownRight size={16}/></IconBox><span><b>{d.delayed_orders}</b><small>Delayed Orders</small></span></div></div></div></section>
    <section className="panel expense-panel"><div className="panel-heading"><div><Wallet size={18}/><h3>Expense Breakdown</h3></div></div><div className="expense-content"><div className="expense-donut"><ResponsiveContainer width="100%" height="100%"><PieChart><Pie data={[{value:45,color:"#3478f6"},{value:20,color:"#18b77a"},{value:15,color:"#f2b635"},{value:10,color:"#9a62e9"},{value:10,color:"#506de5"}]} dataKey="value" innerRadius="63%" outerRadius="90%" stroke="none">{["#3478f6","#18b77a","#f2b635","#9a62e9","#506de5"].map((c,i)=><CellSafe key={i} fill={c}/>)}</Pie></PieChart></ResponsiveContainer><div className="donut-center"><b>$1.2M</b><small>Total</small></div></div><div className="expense-legend">{[["Raw Materials","45%"],["Logistics","20%"],["Manufacturing","15%"],["Other","10%"],["Administrative","10%"]].map(([n,v],i)=><div key={n}><i className={`exp-dot e${i}`}/>{n}<b>{v}</b></div>)}</div></div></section>
    <section className="panel top-products-panel"><div className="panel-heading"><div><BarChart3 size={18}/><h3>Top Selling Products</h3></div><button className="link-button" onClick={()=>onView("Analytics")}>View all</button></div><table><thead><tr><th>Product</th><th>Units Sold</th><th>Revenue</th></tr></thead><tbody>{[["Steel Rod","12,450","$498,000"],["Plastic Resin","8,320","$332,800"],["Copper Wire","6,750","$270,000"],["Aluminum Sheet","5,980","$239,200"]].map(r=><tr key={r[0]}>{r.map(v=><td key={v}>{v}</td>)}</tr>)}</tbody></table></section>
  </div>;
}
function CellSafe({fill}) { return <rect fill={fill}/>; }
function Kpi({icon,tone,label,value,change}) {return <div className="kpi-card"><IconBox tone={tone}>{icon}</IconBox><div className="kpi-copy"><span>{label}</span><b>{value}</b><small className={change<0?"negative":"positive"}>{change<0?<ArrowDownRight size={14}/>:<ArrowUpRight size={14}/>} {Math.abs(change)}% <i>vs. previous period</i></small></div></div>;}
function Inventory({products,onDraft,role}) {
 const [query,setQuery]=useState("");const [filter,setFilter]=useState("All");
 const filtered=products.filter(p=>(p.name.toLowerCase().includes(query.toLowerCase())||p.product_id.toLowerCase().includes(query.toLowerCase()))&&(filter==="All"||(filter==="Low stock"&&p.stock<=p.reorder_level)||(filter==="Healthy"&&p.stock>p.reorder_level)));
 return <div className="module-content"><div className="module-toolbar"><div className="inline-search"><Search size={16}/><input placeholder="Search product or SKU" value={query} onChange={e=>setQuery(e.target.value)}/></div><select value={filter} onChange={e=>setFilter(e.target.value)}><option>All</option><option>Low stock</option><option>Healthy</option></select><span className="muted">{filtered.length} products</span></div><div className="panel"><table><thead><tr><th>Product</th><th>SKU / ID</th><th>Category</th><th>Stock</th><th>Reorder level</th><th>Status</th><th>Action</th></tr></thead><tbody>{filtered.map(p=><tr key={p.product_id}><td>{p.name}</td><td>{p.sku||p.product_id}</td><td>{p.category}</td><td>{p.stock}</td><td>{p.reorder_level}</td><td><Status value={p.stock<=p.reorder_level?"Low Stock":"In Stock"}/></td><td><button className="small-action" disabled={["Viewer","Warehouse"].includes(role)} onClick={()=>onDraft(p)}>Prepare draft</button></td></tr>)}</tbody></table></div></div>;
}
function Suppliers({suppliers,products}) {
 const [query,setQuery]=useState("");const list=(suppliers.length?suppliers:[{supplier_id:"SUP-001",name:"Global Metals Ltd.",reliability:.96,lead_days:5,region:"West"},{supplier_id:"SUP-002",name:"Prime Plastics",reliability:.93,lead_days:7,region:"South"}]).filter(s=>s.name.toLowerCase().includes(query.toLowerCase()));
 return <div className="module-content"><div className="module-toolbar"><div className="inline-search"><Search size={16}/><input placeholder="Search suppliers" value={query} onChange={e=>setQuery(e.target.value)}/></div><span className="muted">{list.length} suppliers</span></div><div className="supplier-grid">{list.map((s,i)=><div className="panel supplier-card" key={s.supplier_id}><div className="supplier-logo">{s.name.split(" ").map(x=>x[0]).slice(0,2).join("")}</div><h3>{s.name}</h3><p>{s.region} region · {s.lead_days} day lead time</p><div className="supplier-metric"><span>Reliability</span><b>{(s.reliability*100).toFixed(1)}%</b></div><div className="meter"><i style={{width:`${s.reliability*100}%`}}/></div><div className="supplier-metric"><span>Typical lead time</span><b>{s.lead_days} days</b></div></div>)}</div></div>;
}
function Procurement({pos,draft,setDraft,onConfirm,role,onPrepare}) {
 return <div className="module-content"><div className="module-toolbar"><div><h2>Purchase orders</h2><p className="muted">Review existing orders and prepare new drafts.</p></div><button className="primary" disabled={role==="Viewer"||role==="Warehouse"} onClick={onPrepare}><Plus size={16}/> New draft</button></div>{draft&&<div className="panel draft-panel"><div className="panel-heading"><div><ClipboardCheck size={18}/><h3>Purchase Order Draft</h3></div><Status value={draft.state}/></div><p className="muted">The assistant populated these fields. Review before confirming.</p><div className="draft-fields"><label>Product<input value={draft.product} onChange={e=>setDraft({...draft,product:e.target.value})}/></label><label>Product ID<input value={draft.product_id} onChange={e=>setDraft({...draft,product_id:e.target.value})}/></label><label>Supplier<input value={draft.supplier} onChange={e=>setDraft({...draft,supplier:e.target.value})}/></label><label>Quantity<input type="number" min="1" value={draft.quantity} onChange={e=>setDraft({...draft,quantity:Number(e.target.value)})}/></label><label>Unit cost<input type="number" min="0" value={draft.unit_cost} onChange={e=>setDraft({...draft,unit_cost:Number(e.target.value)})}/></label><label>Estimated total<input readOnly value={money(draft.quantity*draft.unit_cost)}/></label></div><div className="confirmation-note"><ShieldCheck size={16}/> This is a demo draft. Confirming only changes the local UI state; it does not create a persisted order.</div><div className="draft-actions"><button className="secondary" onClick={()=>setDraft(null)}>Discard draft</button><button className="primary" disabled={role!=="Owner"||draft.state!=="Unsaved"} onClick={onConfirm}>Review & confirm</button></div></div>}<div className="panel"><table><thead><tr><th>PO #</th><th>Supplier</th><th>Status</th><th>Amount</th><th>Date</th></tr></thead><tbody>{pos.map(p=><tr key={p.po_id}><td>{p.po_id}</td><td>{p.supplier}</td><td><Status value={p.status}/></td><td>{money(p.amount)}</td><td>{p.date}</td></tr>)}</tbody></table></div></div>;
}
function Analytics({dashboard}) {
 return <div className="analytics-layout"><div className="kpi-grid"><Kpi icon={<BarChart3/>} tone="blue" label="Revenue (sample)" value={money(dashboard.total_revenue)} change={dashboard.revenue_change}/><Kpi icon={<ShoppingCart/>} tone="green" label="Total orders" value={dashboard.total_orders.toLocaleString()} change={dashboard.orders_change}/></div><section className="panel"><div className="panel-heading"><div><BarChart3 size={18}/><h3>Monthly business trend</h3></div><span className="muted">Illustrative data</span></div><div className="large-chart"><ResponsiveContainer width="100%" height="100%"><AreaChart data={dashboard.monthly}><CartesianGrid strokeDasharray="3 3" vertical={false}/><XAxis dataKey="month"/><YAxis/><Tooltip/><Area dataKey="revenue" stroke="#3478f6" fill="#3478f6" fillOpacity={.12}/><Line dataKey="orders" stroke="#18b77a"/></AreaChart></ResponsiveContainer></div></section><section className="panel insight-card"><Lightbulb size={20}/><div><h3>Analysis note</h3><p>These starter metrics are synthetic and designed to demonstrate the analytics interface. Connect validated historical records before making operational decisions.</p></div></section></div>;
}
function GenericPage({title,icon,stats,rows}) {
 return <div className="module-content"><div className="kpi-grid">{stats.map(([label,value],i)=><div className="kpi-card" key={label}><IconBox tone={["blue","green","purple","cyan"][i]}>{icon}</IconBox><div className="kpi-copy"><span>{label}</span><b>{value}</b><small>Demo metric</small></div></div>)}</div><div className="panel generic-table"><div className="panel-heading"><div>{icon}<h3>{title} · Recent records</h3></div><button className="secondary" onClick={()=>alert("Demo data only")}>Export report</button></div><table><thead><tr><th>Reference</th><th>Description</th><th>Status</th><th>Updated</th></tr></thead><tbody>{rows.map((r,i)=><tr key={r}><td>{r}</td><td>{["Standard business transaction","Operational review","Business record","Scheduled activity"][i%4]}</td><td><Status value={["Completed","Pending","In Progress","Completed"][i%4]}/></td><td>{["Today","Yesterday","Oct 07","Oct 06"][i]}</td></tr>)}</tbody></table></div></div>;
}
function SettingsPage({user}) {return <div className="module-content"><section className="panel settings-card"><h2>Workspace settings</h2><p className="muted">Current demo identity and permissions.</p><div className="settings-row"><span>Signed-in user</span><b>{user.name}</b></div><div className="settings-row"><span>Role</span><b>{user.role}</b></div><div className="settings-row"><span>Access policy</span><b>{rolePerms[user.role]?.join(" · ")}</b></div><div className="settings-row"><span>Data environment</span><b>Synthetic demo data</b></div><p className="confirmation-note"><ShieldCheck size={16}/> Demo login only. Replace with secure server-side authentication before deployment.</p></section></div>;}
createRoot(document.getElementById("root")).render(<App/>);
