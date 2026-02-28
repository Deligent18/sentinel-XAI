import { useState } from "react";

// ── Auth users ────────────────────────────────────────────────────────────────
const USERS = [
  { username: "counsellor1",  password: "Care@2026",    name: "Dr. Sibanda, N.",  role: "counsellor", roleLabel: "Mental Health Counsellor" },
  { username: "welfare1",     password: "Welfare@2026", name: "Ms. Choto, R.",    role: "welfare",    roleLabel: "Student Welfare Officer"  },
  { username: "admin",        password: "Admin@2026",   name: "Mr. Dube, T.",     role: "admin",      roleLabel: "System Administrator"     },
];

const ROLES = [
  { id: "counsellor", label: "Mental Health Counsellor", icon: "🧠",
    desc: "Access full student risk profiles, SHAP explanations and clinical recommendations." },
  { id: "welfare",    label: "Student Welfare Officer",   icon: "🛡️",
    desc: "View risk summaries, manage welfare referrals and monitor intervention progress." },
  { id: "admin",      label: "System Administrator",      icon: "⚙️",
    desc: "Manage user accounts, audit logs, model settings and system configuration." },
];

// ── Student data ──────────────────────────────────────────────────────────────
const STUDENTS = [
  {
    id: "N00411234", name: "Tinashe Moyo", programme: "BSc Computer Science", year: 3,
    risk: 0.87, tier: "high",
    gpa: [3.6, 3.2, 2.4], attendance: 48, lmsLogins: 3, facilityAccess: 1,
    shap: [
      { feature: "GPA decline (−0.8 pts this semester)", value: 0.32, dir: 1 },
      { feature: "Attendance dropped to 48%",            value: 0.28, dir: 1 },
      { feature: "LMS logins: 3 this week (−74%)",       value: 0.19, dir: 1 },
      { feature: "Library access: 0 visits this month",  value: 0.11, dir: 1 },
      { feature: "After-hours WiFi sessions increased",  value: 0.07, dir: 1 },
      { feature: "Assignment submission rate normal",     value:-0.05, dir:-1 },
    ],
    explanation: "Tinashe's risk is primarily driven by a significant academic decline combined with sharply reduced campus engagement. A GPA drop of 0.8 points this semester, attendance below 50%, and near-zero LMS activity collectively signal acute distress. Immediate counsellor contact is recommended.",
    intervention: ["Immediate counsellor contact within 24 hours","Safety planning assessment","Academic load review with faculty adviser"],
    lastUpdated: "2026-02-24",
  },
  {
    id: "N00523891", name: "Rumbidzai Chikwanda", programme: "BSc Psychology", year: 2,
    risk: 0.61, tier: "medium",
    gpa: [3.8, 3.5, 3.1], attendance: 67, lmsLogins: 11, facilityAccess: 4,
    shap: [
      { feature: "GPA decline (−0.4 pts this semester)",    value: 0.18, dir: 1 },
      { feature: "Attendance at 67% (below 70% threshold)", value: 0.15, dir: 1 },
      { feature: "Social facility access reduced 60%",      value: 0.12, dir: 1 },
      { feature: "LMS logins moderate but declining",       value: 0.08, dir: 1 },
      { feature: "Peer network interactions reduced",       value: 0.07, dir: 1 },
      { feature: "Assignment submissions up to date",       value:-0.08, dir:-1 },
    ],
    explanation: "Rumbidzai shows a moderate risk profile characterised by gradual academic decline and reduced social engagement. The pattern suggests emerging distress over 4–6 weeks. Proactive outreach and academic support referral are recommended.",
    intervention: ["Proactive welfare check by personal tutor","Academic support referral","Peer mentoring programme enrolment"],
    lastUpdated: "2026-02-24",
  },
  {
    id: "N00614782", name: "Farai Dube", programme: "BEng Electrical Engineering", year: 4,
    risk: 0.44, tier: "medium",
    gpa: [3.2, 3.0, 2.8], attendance: 72, lmsLogins: 18, facilityAccess: 7,
    shap: [
      { feature: "Steady GPA decline over 3 semesters", value: 0.14, dir: 1 },
      { feature: "Late-night WiFi usage pattern changed",value: 0.11, dir: 1 },
      { feature: "Reduced dining hall access",           value: 0.08, dir: 1 },
      { feature: "Regular LMS engagement maintained",    value:-0.06, dir:-1 },
      { feature: "Attendance above threshold",           value:-0.04, dir:-1 },
    ],
    explanation: "Farai presents a low-moderate risk profile with a gradual multi-semester GPA trajectory downward and some behavioural changes. Academic engagement remains adequate. Wellness resource provision and optional check-in recommended.",
    intervention: ["General wellness resource signposting","Optional academic consultation","Financial support services notification"],
    lastUpdated: "2026-02-24",
  },
  {
    id: "N00732156", name: "Blessing Ncube", programme: "BSc Mathematics", year: 1,
    risk: 0.19, tier: "low",
    gpa: [3.5], attendance: 88, lmsLogins: 27, facilityAccess: 14,
    shap: [
      { feature: "First semester — limited historical data", value: 0.09, dir: 1 },
      { feature: "High LMS engagement",                     value:-0.08, dir:-1 },
      { feature: "Strong attendance record",                value:-0.06, dir:-1 },
      { feature: "Active campus engagement",                value:-0.05, dir:-1 },
    ],
    explanation: "Blessing presents a low risk profile with strong academic engagement and consistent campus participation. No immediate action required. Standard wellness communications applicable.",
    intervention: ["Standard wellness newsletter","Campus mental health awareness resources"],
    lastUpdated: "2026-02-24",
  },
  {
    id: "N00849023", name: "Tapiwa Sibanda", programme: "BCom Accounting", year: 3,
    risk: 0.93, tier: "high",
    gpa: [3.4, 2.9, 2.0], attendance: 31, lmsLogins: 1, facilityAccess: 0,
    shap: [
      { feature: "GPA fell from 3.4 to 2.0 over 2 semesters", value: 0.38, dir: 1 },
      { feature: "Attendance critically low at 31%",           value: 0.31, dir: 1 },
      { feature: "Zero facility access this month",            value: 0.15, dir: 1 },
      { feature: "Virtually absent from LMS",                  value: 0.12, dir: 1 },
      { feature: "No peer group interactions detected",        value: 0.09, dir: 1 },
    ],
    explanation: "Tapiwa shows a critical risk profile. Severe academic collapse, near-total withdrawal from campus and digital engagement, and complete social disengagement indicate an acute crisis state. Urgent intervention is required.",
    intervention: ["URGENT: Same-day counsellor contact required","Emergency wellness protocol activation","Faculty and Dean of Students notification","Safety assessment — do not leave uncontacted"],
    lastUpdated: "2026-02-24",
  },
];

const TIER = {
  high:   { label:"High Risk",   bg:"#FF3B30", light:"rgba(255,59,48,0.12)",  ring:"#FF3B30" },
  medium: { label:"Medium Risk", bg:"#FF9F0A", light:"rgba(255,159,10,0.12)", ring:"#FF9F0A" },
  low:    { label:"Low Risk",    bg:"#30D158", light:"rgba(48,209,88,0.12)",  ring:"#30D158" },
};

const AUDIT_LOGS = [
  { time:"06:12", user:"counsellor1", action:"Viewed risk profile", target:"N00849023", level:"high"   },
  { time:"06:08", user:"welfare1",    action:"Logged intervention",  target:"N00411234", level:"high"   },
  { time:"05:55", user:"counsellor1", action:"Exported report",      target:"N00523891", level:"medium" },
  { time:"05:40", user:"admin",       action:"User account created",  target:"welfare2",  level:"info"   },
  { time:"04:30", user:"welfare1",    action:"Viewed risk profile",   target:"N00614782", level:"medium" },
  { time:"03:15", user:"counsellor1", action:"Alert acknowledged",    target:"N00849023", level:"high"   },
];

const SYSTEM_USERS = [
  { name:"Dr. Sibanda, N.",  username:"counsellor1", role:"counsellor", status:"Active",   last:"Today 06:12" },
  { name:"Ms. Choto, R.",    username:"welfare1",    role:"welfare",    status:"Active",   last:"Today 06:08" },
  { name:"Mr. Dube, T.",     username:"admin",       role:"admin",      status:"Active",   last:"Today 05:40" },
  { name:"Dr. Khumalo, P.",  username:"counsellor2", role:"counsellor", status:"Inactive", last:"18 Feb 2026"  },
];

// ── Shared styles injected once ───────────────────────────────────────────────
const GLOBAL_CSS = `
  @import url('https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@400;600;700;800&family=DM+Sans:wght@300;400;500;600;700&display=swap');
  *{box-sizing:border-box;margin:0;padding:0;}
  body{background:#0A0A12;}
  ::-webkit-scrollbar{width:4px;}
  ::-webkit-scrollbar-thumb{background:rgba(255,255,255,0.15);border-radius:2px;}
  @keyframes pulse{0%,100%{opacity:1}50%{opacity:0.4}}
  @keyframes slideIn{from{opacity:0;transform:translateY(12px)}to{opacity:1;transform:translateY(0)}}
  @keyframes fadeUp{from{opacity:0;transform:translateY(20px)}to{opacity:1;transform:translateY(0)}}
  @keyframes bgPulse{0%,100%{opacity:0.5}50%{opacity:0.8}}
  @keyframes spin{to{transform:rotate(360deg)}}
  input:-webkit-autofill{-webkit-box-shadow:0 0 0 100px #13131E inset!important;-webkit-text-fill-color:#fff!important;}
`;

// ── Small reusable pieces ─────────────────────────────────────────────────────
function RiskGauge({ value }) {
  const r = 44, circ = 2 * Math.PI * r;
  const color = value >= 0.7 ? "#FF3B30" : value >= 0.4 ? "#FF9F0A" : "#30D158";
  return (
    <svg width="120" height="120" viewBox="0 0 120 120">
      <circle cx="60" cy="60" r={r} fill="none" stroke="rgba(255,255,255,0.06)" strokeWidth="10"/>
      <circle cx="60" cy="60" r={r} fill="none" stroke={color} strokeWidth="10"
        strokeDasharray={circ} strokeDashoffset={(1-value)*circ}
        strokeLinecap="round" transform="rotate(-90 60 60)"
        style={{filter:`drop-shadow(0 0 8px ${color})`}}/>
      <text x="60" y="54" textAnchor="middle" fill="white" fontSize="22" fontWeight="700"
        fontFamily="'Barlow Condensed',sans-serif">{Math.round(value*100)}%</text>
      <text x="60" y="72" textAnchor="middle" fill="rgba(255,255,255,0.5)" fontSize="10"
        fontFamily="'DM Sans',sans-serif">risk score</text>
    </svg>
  );
}

function ShapBar({ feature, value, dir, maxVal }) {
  const pct = Math.abs(value)/maxVal*100;
  const color = dir > 0 ? "#FF3B30" : "#30D158";
  return (
    <div style={{marginBottom:10}}>
      <div style={{display:"flex",justifyContent:"space-between",marginBottom:4}}>
        <span style={{fontSize:12,color:"rgba(255,255,255,0.75)",fontFamily:"'DM Sans',sans-serif",maxWidth:"75%"}}>{feature}</span>
        <span style={{fontSize:12,fontWeight:700,color,fontFamily:"'Barlow Condensed',sans-serif"}}>
          {dir>0?"+":""}{value.toFixed(3)}
        </span>
      </div>
      <div style={{height:6,background:"rgba(255,255,255,0.06)",borderRadius:3,overflow:"hidden"}}>
        <div style={{height:"100%",width:`${pct}%`,background:color,borderRadius:3,boxShadow:`0 0 6px ${color}`}}/>
      </div>
    </div>
  );
}

function StudentCard({ student, selected, onClick }) {
  const cfg = TIER[student.tier];
  return (
    <div onClick={onClick} style={{
      padding:"14px 18px",marginBottom:8,borderRadius:12,cursor:"pointer",
      background:selected?"rgba(255,255,255,0.08)":"rgba(255,255,255,0.03)",
      border:`1px solid ${selected?cfg.ring:"rgba(255,255,255,0.07)"}`,
      transition:"all 0.2s",boxShadow:selected?`0 0 0 2px ${cfg.ring}33`:"none",
    }}>
      <div style={{display:"flex",alignItems:"center",gap:12}}>
        <div style={{width:10,height:10,borderRadius:"50%",background:cfg.bg,flexShrink:0,boxShadow:`0 0 6px ${cfg.bg}`}}/>
        <div style={{flex:1,minWidth:0}}>
          <div style={{fontWeight:600,fontSize:14,color:"#fff",fontFamily:"'DM Sans',sans-serif",whiteSpace:"nowrap",overflow:"hidden",textOverflow:"ellipsis"}}>{student.name}</div>
          <div style={{fontSize:11,color:"rgba(255,255,255,0.4)",fontFamily:"'DM Sans',sans-serif"}}>{student.id} · Year {student.year}</div>
        </div>
        <div style={{fontSize:16,fontWeight:800,fontFamily:"'Barlow Condensed',sans-serif",color:cfg.bg,minWidth:42,textAlign:"right"}}>
          {Math.round(student.risk*100)}%
        </div>
      </div>
    </div>
  );
}

function AppHeader({ user, onLogout, alertCount }) {
  const roleColour = user.role==="counsellor"?"#636AFF":user.role==="welfare"?"#30D158":"#FF9F0A";
  return (
    <header style={{background:"rgba(10,10,18,0.95)",borderBottom:"1px solid rgba(255,255,255,0.06)",padding:"0 28px",height:60,display:"flex",alignItems:"center",justifyContent:"space-between",position:"sticky",top:0,zIndex:100,backdropFilter:"blur(20px)"}}>
      <div style={{display:"flex",alignItems:"center",gap:14}}>
        <div style={{width:32,height:32,background:"linear-gradient(135deg,#FF3B30,#FF9F0A)",borderRadius:8,display:"flex",alignItems:"center",justifyContent:"center"}}>
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none"><path d="M12 2L15.09 8.26L22 9.27L17 14.14L18.18 21.02L12 17.77L5.82 21.02L7 14.14L2 9.27L8.91 8.26L12 2Z" fill="white"/></svg>
        </div>
        <div>
          <div style={{fontSize:15,fontWeight:800,color:"#fff",fontFamily:"'Barlow Condensed',sans-serif",letterSpacing:0.5}}>XAI RISK SENTINEL</div>
          <div style={{fontSize:10,color:"rgba(255,255,255,0.35)",letterSpacing:1.5,textTransform:"uppercase"}}>NUST · Student Mental Health</div>
        </div>
      </div>
      <div style={{display:"flex",alignItems:"center",gap:14}}>
        <div style={{padding:"5px 14px",borderRadius:20,background:`${roleColour}22`,border:`1px solid ${roleColour}44`,fontSize:11,color:roleColour,fontWeight:600}}>
          {user.role==="counsellor"?"🧠":user.role==="welfare"?"🛡️":"⚙️"} {user.roleLabel}
        </div>
        <div style={{textAlign:"right"}}>
          <div style={{fontSize:13,fontWeight:600,color:"#fff"}}>{user.name}</div>
          <div style={{fontSize:11,color:"rgba(255,255,255,0.4)"}}>Logged in</div>
        </div>
        {alertCount > 0 && (
          <div style={{padding:"5px 14px",borderRadius:20,background:"rgba(255,59,48,0.12)",border:"1px solid rgba(255,59,48,0.3)",display:"flex",alignItems:"center",gap:6}}>
            <div style={{width:7,height:7,borderRadius:"50%",background:"#FF3B30",animation:"pulse 2s infinite"}}/>
            <span style={{fontSize:12,color:"#FF3B30",fontWeight:600}}>{alertCount} Critical</span>
          </div>
        )}
        <button onClick={onLogout} style={{padding:"7px 16px",borderRadius:20,border:"1px solid rgba(255,255,255,0.15)",background:"transparent",color:"rgba(255,255,255,0.6)",fontSize:12,cursor:"pointer",fontFamily:"'DM Sans',sans-serif"}}>
          Sign Out
        </button>
      </div>
    </header>
  );
}

// ── Login Page ────────────────────────────────────────────────────────────────
function LoginPage({ onLogin }) {
  const [step, setStep]         = useState("role");
  const [selectedRole, setRole] = useState(null);
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [showPwd, setShowPwd]   = useState(false);
  const [error, setError]       = useState("");
  const [loading, setLoading]   = useState(false);
  const [hovered, setHovered]   = useState(null);

  function nextStep() {
    if (!selectedRole) { setError("Please select your role to continue."); return; }
    setError(""); setStep("credentials");
  }

  function handleLogin() {
    if (!username.trim() || !password) { setError("Please enter your username and password."); return; }
    setLoading(true); setError("");
    setTimeout(() => {
      const match = USERS.find(u => u.username===username.trim() && u.password===password && u.role===selectedRole);
      if (match) { onLogin(match); }
      else { setError("Incorrect username or password for the selected role."); setLoading(false); }
    }, 900);
  }

  const roleInfo = ROLES.find(r => r.id===selectedRole);

  return (
    <div style={{minHeight:"100vh",background:"#08080F",display:"flex",alignItems:"center",justifyContent:"center",padding:24,position:"relative",overflow:"hidden"}}>
      <style>{GLOBAL_CSS}</style>

      {[{top:"12%",left:"18%",size:380,color:"rgba(255,59,48,0.07)"},{top:"65%",left:"72%",size:460,color:"rgba(255,159,10,0.06)"},{top:"42%",left:"48%",size:280,color:"rgba(48,209,88,0.04)"}].map((o,i)=>(
        <div key={i} style={{position:"absolute",width:o.size,height:o.size,borderRadius:"50%",background:o.color,top:o.top,left:o.left,transform:"translate(-50%,-50%)",filter:"blur(80px)",animation:`bgPulse ${3+i}s ease-in-out infinite`,pointerEvents:"none"}}/>
      ))}

      <div style={{width:"100%",maxWidth:step==="role"?620:440,background:"rgba(18,18,28,0.92)",borderRadius:24,border:"1px solid rgba(255,255,255,0.08)",boxShadow:"0 40px 80px rgba(0,0,0,0.6),0 0 0 1px rgba(255,255,255,0.04)",backdropFilter:"blur(24px)",overflow:"hidden",animation:"fadeUp 0.45s ease",transition:"max-width 0.4s ease"}}>

        <div style={{background:"linear-gradient(135deg,rgba(255,59,48,0.14),rgba(255,159,10,0.08))",borderBottom:"1px solid rgba(255,255,255,0.06)",padding:"26px 34px",display:"flex",alignItems:"center",gap:16}}>
          <div style={{width:44,height:44,borderRadius:12,background:"linear-gradient(135deg,#FF3B30,#FF9F0A)",display:"flex",alignItems:"center",justifyContent:"center",flexShrink:0,boxShadow:"0 4px 16px rgba(255,59,48,0.35)"}}>
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none"><path d="M12 2L15.09 8.26L22 9.27L17 14.14L18.18 21.02L12 17.77L5.82 21.02L7 14.14L2 9.27L8.91 8.26L12 2Z" fill="white"/></svg>
          </div>
          <div>
            <div style={{fontSize:20,fontWeight:800,color:"#fff",fontFamily:"'Barlow Condensed',sans-serif",letterSpacing:1}}>XAI RISK SENTINEL</div>
            <div style={{fontSize:11,color:"rgba(255,255,255,0.4)",letterSpacing:2,textTransform:"uppercase"}}>NUST · Student Mental Health System</div>
          </div>
        </div>

        <div style={{padding:"30px 34px"}}>
          <div style={{display:"flex",alignItems:"center",gap:8,marginBottom:26}}>
            {["Select Role","Sign In"].map((label,i)=>{
              const active = i===(step==="role"?0:1);
              const done   = i===0 && step==="credentials";
              return (
                <div key={i} style={{display:"flex",alignItems:"center",gap:8}}>
                  <div style={{display:"flex",alignItems:"center",gap:8}}>
                    <div style={{width:24,height:24,borderRadius:"50%",flexShrink:0,background:done?"#30D158":active?"#FF9F0A":"rgba(255,255,255,0.08)",border:`1px solid ${done?"#30D158":active?"#FF9F0A":"rgba(255,255,255,0.12)"}`,display:"flex",alignItems:"center",justifyContent:"center",fontSize:11,fontWeight:700,color:"#fff",fontFamily:"'DM Sans',sans-serif"}}>
                      {done?"✓":i+1}
                    </div>
                    <span style={{fontSize:12,color:active?"#fff":"rgba(255,255,255,0.35)",fontFamily:"'DM Sans',sans-serif",fontWeight:active?600:400}}>{label}</span>
                  </div>
                  {i<1&&<div style={{width:36,height:1,background:"rgba(255,255,255,0.1)"}}/>}
                </div>
              );
            })}
          </div>

          {step==="role" && (
            <div>
              <p style={{fontSize:15,fontWeight:600,color:"#fff",fontFamily:"'DM Sans',sans-serif",marginBottom:6}}>I am logging in as a…</p>
              <p style={{fontSize:12,color:"rgba(255,255,255,0.4)",marginBottom:20,fontFamily:"'DM Sans',sans-serif"}}>Select your role to see the appropriate view.</p>

              <div style={{display:"flex",flexDirection:"column",gap:10,marginBottom:22}}>
                {ROLES.map(role=>{
                  const active  = selectedRole===role.id;
                  const isHover = hovered===role.id;
                  return (
                    <div key={role.id} onClick={()=>{setRole(role.id);setError("");}}
                      onMouseEnter={()=>setHovered(role.id)} onMouseLeave={()=>setHovered(null)}
                      style={{padding:"15px 18px",borderRadius:14,cursor:"pointer",display:"flex",alignItems:"center",gap:16,
                        background:active?"linear-gradient(135deg,rgba(255,159,10,0.18),rgba(255,59,48,0.1))":isHover?"rgba(255,255,255,0.05)":"rgba(255,255,255,0.02)",
                        border:`1.5px solid ${active?"#FF9F0A":"rgba(255,255,255,0.08)"}`,
boxShadow:active?"0 0 0 4px rgba(255,159,10,0.1)":"none",transition:"all 0.2s"}}>
                      <div style={{width:44,height:44,borderRadius:12,flexShrink:0,background:active?"rgba(255,159,10,0.2)":"rgba(255,255,255,0.06)",border:`1px solid ${active?"rgba(255,159,10,0.4)":"rgba(255,255,255,0.1)"}`,display:"flex",alignItems:"center",justifyContent:"center",fontSize:20,transition:"all 0.2s"}}>
                        {role.icon}
                      </div>
                      <div style={{flex:1,minWidth:0}}>
                        <div style={{fontSize:14,fontWeight:700,color:active?"#FF9F0A":"#fff",fontFamily:"'DM Sans',sans-serif",transition:"color 0.2s"}}>{role.label}</div>
                        <div style={{fontSize:12,color:"rgba(255,255,255,0.45)",fontFamily:"'DM Sans',sans-serif",marginTop:2,lineHeight:1.4}}>{role.desc}</div>
                      </div>
                      <div style={{width:20,height:20,borderRadius:"50%",flexShrink:0,border:`2px solid ${active?"#FF9F0A":"rgba(255,255,255,0.2)"}`,background:active?"#FF9F0A":"transparent",display:"flex",alignItems:"center",justifyContent:"center",transition:"all 0.2s"}}>
                        {active&&<div style={{width:8,height:8,borderRadius:"50%",background:"#fff"}}/>}
                      </div>
                    </div>
                  );
                })}
              </div>

              {error&&<div style={{padding:"10px 14px",borderRadius:10,background:"rgba(255,59,48,0.1)",border:"1px solid rgba(255,59,48,0.3)",fontSize:12,color:"#FF6B6B",marginBottom:14,fontFamily:"'DM Sans',sans-serif"}}>⚠ {error}</div>}

              <button onClick={nextStep} style={{width:"100%",padding:14,borderRadius:12,border:"none",background:selectedRole?"linear-gradient(135deg,#FF9F0A,#FF3B30)":"rgba(255,255,255,0.07)",color:selectedRole?"#fff":"rgba(255,255,255,0.3)",fontSize:14,fontWeight:700,cursor:selectedRole?"pointer":"not-allowed",fontFamily:"'DM Sans',sans-serif",letterSpacing:0.5,boxShadow:selectedRole?"0 4px 20px rgba(255,59,48,0.3)":"none",transition:"all 0.2s"}}>
                Continue →
              </button>
            </div>
          )}

          {step==="credentials" && (
            <div>
              <div style={{display:"inline-flex",alignItems:"center",gap:8,padding:"7px 14px",borderRadius:20,background:"rgba(255,159,10,0.12)",border:"1px solid rgba(255,159,10,0.3)",marginBottom:22}}>
                <span style={{fontSize:16}}>{roleInfo?.icon}</span>
                <span style={{fontSize:12,color:"#FF9F0A",fontWeight:600,fontFamily:"'DM Sans',sans-serif"}}>{roleInfo?.label}</span>
                <button onClick={()=>{setStep("role");setError("");setUsername("");setPassword("");}} style={{background:"none",border:"none",color:"rgba(255,255,255,0.35)",cursor:"pointer",fontSize:12,fontFamily:"'DM Sans',sans-serif",paddingLeft:4}}>
                  ✕ Change
                </button>
              </div>

              <p style={{fontSize:15,fontWeight:600,color:"#fff",fontFamily:"'DM Sans',sans-serif",marginBottom:4}}>Sign in to your account</p>
              <p style={{fontSize:12,color:"rgba(255,255,255,0.4)",marginBottom:22,fontFamily:"'DM Sans',sans-serif"}}>Enter your NUST credentials to access the system.</p>

              <div style={{marginBottom:14}}>
                <label style={{fontSize:11,fontWeight:700,color:"rgba(255,255,255,0.5)",fontFamily:"'DM Sans',sans-serif",display:"block",marginBottom:7,letterSpacing:0.8,textTransform:"uppercase"}}>Username</label>
                <div style={{position:"relative"}}>
                  <svg style={{position:"absolute",left:14,top:"50%",transform:"translateY(-50%)"}} width="16" height="16" viewBox="0 0 24 24" fill="none">
                    <path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2M12 11a4 4 0 100-8 4 4 0 000 8z" stroke="rgba(255,255,255,0.35)" strokeWidth="2" strokeLinecap="round"/>
                  </svg>
                  <input value={username} onChange={e=>{setUsername(e.target.value);setError("");}} onKeyDown={e=>e.key==="Enter"&&handleLogin()} placeholder="Enter username"
                    style={{width:"100%",padding:"12px 14px 12px 40px",borderRadius:12,background:"rgba(255,255,255,0.05)",border:"1.5px solid rgba(255,255,255,0.1)",color:"#fff",fontSize:14,fontFamily:"'DM Sans',sans-serif",outline:"none"}}
                    onFocus={e=>e.target.style.borderColor="rgba(255,159,10,0.5)"} onBlur={e=>e.target.style.borderColor="rgba(255,255,255,0.1)"}/>
                </div>
              </div>

              <div style={{marginBottom:22}}>
                <label style={{fontSize:11,fontWeight:700,color:"rgba(255,255,255,0.5)",fontFamily:"'DM Sans',sans-serif",display:"block",marginBottom:7,letterSpacing:0.8,textTransform:"uppercase"}}>Password</label>
                <div style={{position:"relative"}}>
                  <svg style={{position:"absolute",left:14,top:"50%",transform:"translateY(-50%)"}} width="16" height="16" viewBox="0 0 24 24" fill="none">
                    <rect x="3" y="11" width="18" height="11" rx="2" stroke="rgba(255,255,255,0.35)" strokeWidth="2"/>
                    <path d="M7 11V7a5 5 0 0110 0v4" stroke="rgba(255,255,255,0.35)" strokeWidth="2" strokeLinecap="round"/>
                  </svg>
                  <input type={showPwd?"text":"password"} value={password} onChange={e=>{setPassword(e.target.value);setError("");}} onKeyDown={e=>e.key==="Enter"&&handleLogin()} placeholder="Enter password"
                    style={{width:"100%",padding:"12px 44px 12px 40px",borderRadius:12,background:"rgba(255,255,255,0.05)",border:"1.5px solid rgba(255,255,255,0.1)",color:"#fff",fontSize:14,fontFamily:"'DM Sans',sans-serif",outline:"none"}}
                    onFocus={e=>e.target.style.borderColor="rgba(255,159,10,0.5)"} onBlur={e=>e.target.style.borderColor="rgba(255,255,255,0.1)"}/>
                  <button onClick={()=>setShowPwd(!showPwd)} style={{position:"absolute",right:14,top:"50%",transform:"translateY(-50%)",background:"none",border:"none",cursor:"pointer",color:"rgba(255,255,255,0.35)",fontSize:11,fontFamily:"'DM Sans',sans-serif"}}>
                    {showPwd?"Hide":"Show"}
                  </button>
                </div>
              </div>

              {error&&<div style={{padding:"10px 14px",borderRadius:10,background:"rgba(255,59,48,0.1)",border:"1px solid rgba(255,59,48,0.3)",fontSize:12,color:"#FF6B6B",marginBottom:14,fontFamily:"'DM Sans',sans-serif"}}>⚠ {error}</div>}

              <button onClick={handleLogin} disabled={loading} style={{width:"100%",padding:14,borderRadius:12,border:"none",background:"linear-gradient(135deg,#FF9F0A,#FF3B30)",color:"#fff",fontSize:14,fontWeight:700,cursor:loading?"wait":"pointer",fontFamily:"'DM Sans',sans-serif",letterSpacing:0.5,boxShadow:"0 4px 20px rgba(255,59,48,0.3)",opacity:loading?0.8:1,display:"flex",alignItems:"center",justifyContent:"center",gap:10,transition:"opacity 0.2s"}}>
                {loading?(<><div style={{width:16,height:16,border:"2px solid rgba(255,255,255,0.3)",borderTopColor:"#fff",borderRadius:"50%",animation:"spin 0.7s linear infinite"}}/>Authenticating…</>):"Sign In →"}
              </button>

              <div style={{marginTop:18,padding:"11px 14px",borderRadius:10,background:"rgba(255,255,255,0.03)",border:"1px solid rgba(255,255,255,0.06)"}}>
                <div style={{fontSize:11,color:"rgba(255,255,255,0.35)",fontFamily:"'DM Sans',sans-serif",lineHeight:1.7}}>
                  <strong style={{color:"rgba(255,255,255,0.5)"}}>Demo credentials</strong> for this role:<br/>
                  {selectedRole==="counsellor"&&"username: counsellor1  ·  password: Care@2026"}
                  {selectedRole==="welfare"   &&"username: welfare1  ·  password: Welfare@2026"}
                  {selectedRole==="admin"     &&"username: admin  ·  password: Admin@2026"}
                </div>
              </div>
            </div>
          )}
        </div>

        <div style={{padding:"13px 34px",borderTop:"1px solid rgba(255,255,255,0.05)",textAlign:"center"}}>
          <span style={{fontSize:11,color:"rgba(255,255,255,0.2)",fontFamily:"'DM Sans',sans-serif"}}>Authorised users only · NUST Dept. of Informatics · 2026</span>
        </div>
      </div>
    </div>
  );
}

// ── Admin Dashboard ───────────────────────────────────────────────────────────
function AdminDashboard({ user, onLogout }) {
  const counts = {high:STUDENTS.filter(s=>s.tier==="high").length,medium:STUDENTS.filter(s=>s.tier==="medium").length,low:STUDENTS.filter(s=>s.tier==="low").length};
  return (
    <div style={{minHeight:"100vh",background:"#0A0A12",fontFamily:"'DM Sans',sans-serif"}}>
      <style>{GLOBAL_CSS}</style>
      <AppHeader user={user} onLogout={onLogout} alertCount={0}/>

      <div style={{padding:"26px 30px",maxWidth:1100,margin:"0 auto"}}>
        <div style={{display:"grid",gridTemplateColumns:"repeat(4,1fr)",gap:12,marginBottom:26}}>
          {[
            {label:"Students Monitored",value:STUDENTS.length,color:"#fff"},
            {label:"High Risk Alerts",  value:counts.high,    color:"#FF3B30"},
            {label:"Active Users",      value:3,              color:"#30D158"},
            {label:"Model AUC-ROC",     value:"0.88",         color:"#FF9F0A"},
          ].map(s=>(
            <div key={s.label} style={{background:"rgba(255,255,255,0.03)",border:"1px solid rgba(255,255,255,0.07)",borderRadius:14,padding:"18px 20px"}}>
              <div style={{fontSize:11,color:"rgba(255,255,255,0.4)",textTransform:"uppercase",letterSpacing:1,marginBottom:8}}>{s.label}</div>
              <div style={{fontSize:32,fontWeight:800,color:s.color,fontFamily:"'Barlow Condensed',sans-serif"}}>{s.value}</div>
            </div>
          ))}
        </div>

        <div style={{display:"grid",gridTemplateColumns:"1.3fr 1fr",gap:16}}>
          <div style={{background:"rgba(255,255,255,0.03)",border:"1px solid rgba(255,255,255,0.07)",borderRadius:16,padding:22}}>
            <div style={{fontSize:12,fontWeight:700,color:"rgba(255,255,255,0.5)",textTransform:"uppercase",letterSpacing:1.5,marginBottom:16}}>User Management</div>
            {SYSTEM_USERS.map(u=>(
              <div key={u.username} style={{display:"flex",alignItems:"center",gap:14,padding:"12px 0",borderBottom:"1px solid rgba(255,255,255,0.05)"}}>
                <div style={{width:36,height:36,borderRadius:10,background:"rgba(255,255,255,0.07)",display:"flex",alignItems:"center",justifyContent:"center",fontSize:13,fontWeight:700,color:"rgba(255,255,255,0.6)",fontFamily:"'Barlow Condensed',sans-serif"}}>
                  {u.name.split(" ").map(n=>n[0]).join("").slice(0,2)}
                </div>
                <div style={{flex:1}}>
                  <div style={{fontSize:13,fontWeight:600,color:"#fff"}}>{u.name}</div>
                  <div style={{fontSize:11,color:"rgba(255,255,255,0.4)"}}>{u.username} · {u.role}</div>
                </div>
                <div style={{textAlign:"right"}}>
                  <span style={{fontSize:11,padding:"3px 10px",borderRadius:20,background:u.status==="Active"?"rgba(48,209,88,0.15)":"rgba(255,255,255,0.06)",color:u.status==="Active"?"#30D158":"rgba(255,255,255,0.35)",border:`1px solid ${u.status==="Active"?"rgba(48,209,88,0.3)":"rgba(255,255,255,0.1)"}`}}>{u.status}</span>
                  <div style={{fontSize:10,color:"rgba(255,255,255,0.25)",marginTop:3}}>{u.last}</div>
                </div>
              </div>
            ))}
            <button style={{marginTop:14,width:"100%",padding:10,borderRadius:10,border:"1px dashed rgba(255,255,255,0.15)",background:"transparent",color:"rgba(255,255,255,0.4)",fontSize:12,cursor:"pointer",fontFamily:"'DM Sans',sans-serif"}}>+ Add User</button>
          </div>

          <div style={{background:"rgba(255,255,255,0.03)",border:"1px solid rgba(255,255,255,0.07)",borderRadius:16,padding:22}}>
            <div style={{fontSize:12,fontWeight:700,color:"rgba(255,255,255,0.5)",textTransform:"uppercase",letterSpacing:1.5,marginBottom:16}}>Recent Audit Log</div>
            {AUDIT_LOGS.map((log,i)=>(
              <div key={i} style={{display:"flex",gap:12,padding:"10px 0",borderBottom:"1px solid rgba(255,255,255,0.05)",alignItems:"flex-start"}}>
                <div style={{fontSize:11,color:"rgba(255,255,255,0.3)",fontFamily:"'Barlow Condensed',sans-serif",minWidth:36,marginTop:1}}>{log.time}</div>
                <div style={{flex:1}}>
                  <div style={{fontSize:12,color:"#fff"}}>{log.action}</div>
                  <div style={{fontSize:11,color:"rgba(255,255,255,0.4)"}}>{log.user} → {log.target}</div>
                </div>
                <div style={{width:8,height:8,borderRadius:"50%",marginTop:4,flexShrink:0,background:log.level==="high"?"#FF3B30":log.level==="medium"?"#FF9F0A":log.level==="info"?"#636AFF":"#30D158",boxShadow:`0 0 5px ${log.level==="high"?"#FF3B30":log.level==="medium"?"#FF9F0A":"#30D158"}`}}/>
              </div>
            ))}
          </div>
        </div>

        <div style={{marginTop:16,background:"rgba(255,255,255,0.02)",border:"1px solid rgba(255,255,255,0.06)",borderRadius:12,padding:"14px 20px",display:"flex",gap:32,flexWrap:"wrap"}}>
          {[["Model","XGBoost v2.1"],["Last Trained","22 Feb 2026"],["SHAP","v0.46"],["Next Retrain","01 Mar 2026"],["Records","1,000 students"],["Status","✓ Healthy"]].map(([k,v])=>(
            <div key={k}><div style={{fontSize:10,color:"rgba(255,255,255,0.3)",textTransform:"uppercase",letterSpacing:1}}>{k}</div><div style={{fontSize:13,fontWeight:600,color:"rgba(255,255,255,0.8)",marginTop:2}}>{v}</div></div>
          ))}
        </div>
      </div>
    </div>
  );
}

// ── Counsellor / Welfare Dashboard ────────────────────────────────────────────
function ClinicalDashboard({ user, onLogout }) {
  const [selected, setSelected] = useState(STUDENTS[4]);
  const [filter, setFilter]     = useState("all");

  const filtered = STUDENTS.filter(s=>filter==="all"||s.tier===filter).sort((a,b)=>b.risk-a.risk);
  const cfg      = TIER[selected.tier];
  const maxShap  = Math.max(...selected.shap.map(s=>Math.abs(s.value)));
  const counts   = {high:STUDENTS.filter(s=>s.tier==="high").length,medium:STUDENTS.filter(s=>s.tier==="medium").length,low:STUDENTS.filter(s=>s.tier==="low").length};

  return (
    <div style={{minHeight:"100vh",background:"#0A0A12",fontFamily:"'DM Sans',sans-serif",display:"flex",flexDirection:"column"}}>
      <style>{GLOBAL_CSS}</style>
      <AppHeader user={user} onLogout={onLogout} alertCount={counts.high}/>

      <div style={{background:"rgba(255,255,255,0.02)",borderBottom:"1px solid rgba(255,255,255,0.05)",padding:"10px 28px",display:"flex",gap:8,alignItems:"center"}}>
        {[{key:"all",label:"All Students",count:STUDENTS.length,color:"rgba(255,255,255,0.6)"},{key:"high",label:"High Risk",count:counts.high,color:"#FF3B30"},{key:"medium",label:"Medium Risk",count:counts.medium,color:"#FF9F0A"},{key:"low",label:"Low Risk",count:counts.low,color:"#30D158"}].map(f=>(
          <button key={f.key} onClick={()=>setFilter(f.key)} style={{padding:"6px 16px",borderRadius:20,border:"1px solid",borderColor:filter===f.key?f.color:"rgba(255,255,255,0.1)",background:filter===f.key?`${f.color}22`:"transparent",color:filter===f.key?f.color:"rgba(255,255,255,0.4)",fontSize:12,fontWeight:600,cursor:"pointer",transition:"all 0.2s",fontFamily:"'DM Sans',sans-serif"}}>
            {f.label} <span style={{opacity:0.7}}>({f.count})</span>
          </button>
        ))}
        {user.role==="welfare"&&(
          <div style={{marginLeft:"auto",padding:"5px 14px",borderRadius:20,background:"rgba(48,209,88,0.08)",border:"1px solid rgba(48,209,88,0.2)",fontSize:11,color:"rgba(48,209,88,0.8)"}}>
            🛡️ Welfare view — full SHAP details visible to counsellors only
          </div>
        )}
      </div>

      <div style={{display:"flex",flex:1,overflow:"hidden",height:"calc(100vh - 108px)"}}>
        <div style={{width:290,flexShrink:0,borderRight:"1px solid rgba(255,255,255,0.06)",overflowY:"auto",padding:"16px 14px"}}>
          {filtered.map(s=>(
            <StudentCard key={s.id} student={s} selected={selected.id===s.id} onClick={()=>setSelected(s)}/>
          ))}
        </div>

        <div style={{flex:1,overflowY:"auto",padding:"24px 28px"}} key={selected.id}>
          <div style={{animation:"slideIn 0.3s ease"}}>

            <div style={{display:"flex",alignItems:"flex-start",gap:24,marginBottom:24}}>
              <div style={{width:56,height:56,borderRadius:16,background:`linear-gradient(135deg,${cfg.bg}44,${cfg.bg}11)`,border:`1px solid ${cfg.bg}44`,display:"flex",alignItems:"center",justifyContent:"center",fontSize:20,fontWeight:800,color:cfg.bg,flexShrink:0,fontFamily:"'Barlow Condensed',sans-serif"}}>
                {selected.name.split(" ").map(n=>n[0]).join("")}
              </div>
              <div style={{flex:1}}>
                <div style={{display:"flex",alignItems:"center",gap:12,flexWrap:"wrap"}}>
                  <h2 style={{fontSize:22,fontWeight:700,color:"#fff",fontFamily:"'Barlow Condensed',sans-serif"}}>{selected.name}</h2>
                  <span style={{padding:"3px 12px",borderRadius:20,fontSize:11,fontWeight:700,background:cfg.light,color:cfg.bg,border:`1px solid ${cfg.bg}44`,letterSpacing:0.5,textTransform:"uppercase"}}>{cfg.label}</span>
                </div>
                <div style={{fontSize:13,color:"rgba(255,255,255,0.45)",marginTop:4}}>{selected.id} · {selected.programme} · Year {selected.year}</div>
              </div>
              <RiskGauge value={selected.risk}/>
            </div>

            <div style={{display:"grid",gridTemplateColumns:"repeat(3,1fr)",gap:12,marginBottom:20}}>
              {[
                {label:"Current GPA",   value:selected.gpa[selected.gpa.length-1].toFixed(1),sub:`Was ${selected.gpa[0].toFixed(1)}`,       warn:selected.gpa[selected.gpa.length-1]<2.5},
                {label:"Attendance",    value:`${selected.attendance}%`,                       sub:selected.attendance<60?"Critical":selected.attendance<75?"Below threshold":"Acceptable",warn:selected.attendance<75},
                {label:"LMS Logins/wk",value:selected.lmsLogins,                              sub:"This week",                                warn:selected.lmsLogins<5},
              ].map(c=>(
                <div key={c.label} style={{background:c.warn?"rgba(255,59,48,0.07)":"rgba(255,255,255,0.04)",border:`1px solid ${c.warn?"rgba(255,59,48,0.25)":"rgba(255,255,255,0.07)"}`,borderRadius:12,padding:"16px 18px"}}>
                  <div style={{fontSize:11,color:"rgba(255,255,255,0.4)",textTransform:"uppercase",letterSpacing:1,marginBottom:6}}>{c.label}</div>
                  <div style={{fontSize:26,fontWeight:800,color:c.warn?"#FF3B30":"#fff",fontFamily:"'Barlow Condensed',sans-serif"}}>{c.value}</div>
                  <div style={{fontSize:11,color:c.warn?"rgba(255,59,48,0.7)":"rgba(255,255,255,0.35)",marginTop:2}}>{c.sub}</div>
                </div>
              ))}
            </div>

            <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:16,marginBottom:16}}>
              <div style={{background:"rgba(255,255,255,0.03)",border:"1px solid rgba(255,255,255,0.07)",borderRadius:14,padding:20}}>
                <div style={{fontSize:12,fontWeight:700,color:"rgba(255,255,255,0.5)",textTransform:"uppercase",letterSpacing:1.5,marginBottom:16}}>
                  {user.role==="counsellor"?"SHAP Feature Contributions":"Top Risk Factors"}
                </div>
                {(user.role==="counsellor"?selected.shap:selected.shap.filter(s=>s.dir>0).slice(0,3)).map((s,i)=>(
                  <ShapBar key={i} {...s} maxVal={maxShap}/>
                ))}
                {user.role==="welfare"&&<div style={{fontSize:11,color:"rgba(255,255,255,0.25)",marginTop:10,fontStyle:"italic"}}>Full SHAP values available to Mental Health Counsellors only.</div>}
              </div>

              <div style={{display:"flex",flexDirection:"column",gap:16}}>
                <div style={{background:`linear-gradient(135deg,${cfg.bg}0A,rgba(255,255,255,0.02))`,border:`1px solid ${cfg.bg}25`,borderRadius:14,padding:20}}>
                  <div style={{fontSize:12,fontWeight:700,color:cfg.bg,textTransform:"uppercase",letterSpacing:1.5,marginBottom:12}}>XAI Explanation</div>
                  <p style={{fontSize:13,color:"rgba(255,255,255,0.75)",lineHeight:1.65}}>{selected.explanation}</p>
                </div>
                <div style={{background:"rgba(255,255,255,0.03)",border:"1px solid rgba(255,255,255,0.07)",borderRadius:14,padding:20}}>
                  <div style={{fontSize:12,fontWeight:700,color:"rgba(255,255,255,0.5)",textTransform:"uppercase",letterSpacing:1.5,marginBottom:12}}>
                    {user.role==="counsellor"?"Clinical Recommendations":"Welfare Actions"}
                  </div>
                  {selected.intervention.map((action,i)=>(
                    <div key={i} style={{display:"flex",gap:10,marginBottom:10,alignItems:"flex-start"}}>
                      <div style={{width:20,height:20,borderRadius:6,flexShrink:0,background:i===0&&selected.tier==="high"?"rgba(255,59,48,0.2)":"rgba(255,255,255,0.07)",border:`1px solid ${i===0&&selected.tier==="high"?"rgba(255,59,48,0.4)":"rgba(255,255,255,0.1)"}`,display:"flex",alignItems:"center",justifyContent:"center",fontSize:10,fontWeight:700,color:i===0&&selected.tier==="high"?"#FF3B30":"rgba(255,255,255,0.4)"}}>
                        {i+1}
                      </div>
                      <span style={{fontSize:12,color:"rgba(255,255,255,0.7)",lineHeight:1.5,flex:1}}>{action}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            <div style={{background:"rgba(255,255,255,0.03)",border:"1px solid rgba(255,255,255,0.07)",borderRadius:14,padding:20,marginBottom:16}}>
              <div style={{fontSize:12,fontWeight:700,color:"rgba(255,255,255,0.5)",textTransform:"uppercase",letterSpacing:1.5,marginBottom:16}}>Academic Trajectory — GPA per Semester</div>
              <div style={{display:"flex",alignItems:"flex-end",gap:12,height:80}}>
                {selected.gpa.map((g,i)=>{
                  const h=(g/4.0)*80;
                  const color=g<2.5?"#FF3B30":g<3.0?"#FF9F0A":"#30D158";
                  return (
                    <div key={i} style={{display:"flex",flexDirection:"column",alignItems:"center",gap:6,flex:1}}>
                      <span style={{fontSize:12,fontWeight:700,color,fontFamily:"'Barlow Condensed',sans-serif"}}>{g.toFixed(1)}</span>
                      <div style={{width:"100%",height:`${h}px`,background:color,borderRadius:"6px 6px 2px 2px",opacity:0.8,boxShadow:`0 0 8px ${color}66`}}/>
                      <span style={{fontSize:10,color:"rgba(255,255,255,0.3)"}}>Sem {i+1}</span>
                    </div>
                  );
                })}
              </div>
            </div>

            <div style={{padding:"12px 16px",background:"rgba(255,255,255,0.02)",borderRadius:10,border:"1px solid rgba(255,255,255,0.05)"}}>
              <p style={{fontSize:11,color:"rgba(255,255,255,0.3)",lineHeight:1.6,fontStyle:"italic"}}>
                ⚠️ Decision support only. All predictions must be reviewed by a qualified professional before any intervention is initiated. XAI explanations support, not replace, clinical judgement. Model: XGBoost v2.1 · SHAP v0.46 · Last trained: Feb 2026.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

// ── Root ──────────────────────────────────────────────────────────────────────
export default function App() {
  const [user, setUser] = useState(null);
  if (!user) return <LoginPage onLogin={setUser}/>;
  if (user.role==="admin") return <AdminDashboard user={user} onLogout={()=>setUser(null)}/>;
  return <ClinicalDashboard user={user} onLogout={()=>setUser(null)}/>;
}
