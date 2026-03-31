import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import api from "../api";

const STATUSES = ["applied","screening","interview","offer","accepted","rejected"];
const STATUS_COLORS = {
  applied:"#6366f1", screening:"#f59e0b", interview:"#3b82f6",
  offer:"#10b981", accepted:"#22c55e", rejected:"#ef4444"
};

export default function Dashboard() {
  const [apps, setApps] = useState([]);
  const [stats, setStats] = useState(null);
  const [filter, setFilter] = useState("");
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ company:"", role:"", location:"", applied_date:"", source:"", notes:"" });
  const [error, setError] = useState("");
  const [selected, setSelected] = useState(null);
  const navigate = useNavigate();

  useEffect(() => { fetchAll(); }, [filter]);

  async function fetchAll() {
    const [appsRes, statsRes] = await Promise.all([
      api.get("/applications" + (filter ? `?status=${filter}` : "")),
      api.get("/applications/stats")
    ]);
    setApps(appsRes.data);
    setStats(statsRes.data);
  }

  async function handleCreate(e) {
    e.preventDefault();
    setError("");
    try {
      await api.post("/applications", form);
      setShowForm(false);
      setForm({ company:"", role:"", location:"", applied_date:"", source:"", notes:"" });
      fetchAll();
    } catch (err) {
      setError(err.response?.data?.error || "Failed to create");
    }
  }

  async function handleTransition(appId, newStatus) {
    try {
      await api.patch(`/applications/${appId}/status`, { status: newStatus });
      fetchAll();
      setSelected(null);
    } catch (err) {
      alert(err.response?.data?.error || "Transition failed");
    }
  }

  async function handleDelete(appId) {
    if (!confirm("Delete this application?")) return;
    await api.delete(`/applications/${appId}`);
    fetchAll();
    setSelected(null);
  }

  function logout() {
    localStorage.removeItem("token");
    navigate("/login");
  }

  return (
    <div style={styles.page}>
      <div style={styles.header}>
        <h1 style={{margin:0}}>Job Tracker</h1>
        <div style={{display:"flex", gap:"1rem", alignItems:"center"}}>
          <button style={styles.btnPrimary} onClick={() => setShowForm(true)}>+ Add Application</button>
          <button style={styles.btnGhost} onClick={logout}>Logout</button>
        </div>
      </div>

      {stats && (
        <div style={styles.statsRow}>
          <div style={styles.statCard}><strong>{stats.total}</strong><span>Total</span></div>
          {STATUSES.map(s => (
            <div key={s} style={{...styles.statCard, borderTop:`3px solid ${STATUS_COLORS[s]}`}}>
              <strong>{stats.by_status[s]}</strong><span>{s}</span>
            </div>
          ))}
        </div>
      )}

      <div style={styles.filterRow}>
        <span>Filter:</span>
        <button style={filter===""?styles.filterActive:styles.filterBtn} onClick={()=>setFilter("")}>All</button>
        {STATUSES.map(s => (
          <button key={s} style={filter===s?styles.filterActive:styles.filterBtn} onClick={()=>setFilter(s)}>{s}</button>
        ))}
      </div>

      {showForm && (
        <div style={styles.modal}>
          <div style={styles.modalCard}>
            <h3>New Application</h3>
            {error && <p style={{color:"red"}}>{error}</p>}
            <form onSubmit={handleCreate}>
              {["company","role","location","source"].map(f => (
                <input key={f} style={styles.input} placeholder={f} value={form[f]}
                  onChange={e => setForm({...form,[f]:e.target.value})} required={f==="company"||f==="role"} />
              ))}
              <input style={styles.input} type="date" value={form.applied_date}
                onChange={e => setForm({...form,applied_date:e.target.value})} required />
              <textarea style={styles.input} placeholder="notes" value={form.notes}
                onChange={e => setForm({...form,notes:e.target.value})} />
              <div style={{display:"flex",gap:"0.5rem"}}>
                <button style={styles.btnPrimary} type="submit">Save</button>
                <button style={styles.btnGhost} type="button" onClick={()=>setShowForm(false)}>Cancel</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {selected && (
        <div style={styles.modal}>
          <div style={styles.modalCard}>
            <h3>{selected.company} — {selected.role}</h3>
            <p><strong>Status:</strong> <span style={{color:STATUS_COLORS[selected.status]}}>{selected.status}</span></p>
            <p><strong>Applied:</strong> {selected.applied_date}</p>
            {selected.location && <p><strong>Location:</strong> {selected.location}</p>}
            {selected.source && <p><strong>Source:</strong> {selected.source}</p>}
            {selected.notes && <p><strong>Notes:</strong> {selected.notes}</p>}
            <h4>Status History</h4>
            <ul>
              {selected.status_history.map((h,i) => (
                <li key={i}>{h.from_status ? `${h.from_status} → ` : ""}{h.to_status} <small style={{color:"#888"}}>({new Date(h.changed_at).toLocaleString()})</small></li>
              ))}
            </ul>
            <h4>Transition Status</h4>
            <div style={{display:"flex",flexWrap:"wrap",gap:"0.4rem"}}>
              {STATUSES.map(s => (
                <button key={s} style={{...styles.filterBtn, background:STATUS_COLORS[s], color:"white"}}
                  onClick={() => handleTransition(selected.id, s)}>{s}</button>
              ))}
            </div>
            <div style={{display:"flex",gap:"0.5rem",marginTop:"1rem"}}>
              <button style={{...styles.btnGhost,color:"red"}} onClick={() => handleDelete(selected.id)}>Delete</button>
              <button style={styles.btnGhost} onClick={() => setSelected(null)}>Close</button>
            </div>
          </div>
        </div>
      )}

      <div style={styles.grid}>
        {apps.length === 0 && <p style={{color:"#888"}}>No applications yet. Add one!</p>}
        {apps.map(app => (
          <div key={app.id} style={styles.card} onClick={() => setSelected(app)}>
            <div style={{display:"flex",justifyContent:"space-between",alignItems:"start"}}>
              <div>
                <strong>{app.company}</strong>
                <p style={{margin:"0.2rem 0",color:"#555"}}>{app.role}</p>
                {app.location && <p style={{margin:0,fontSize:"0.85rem",color:"#888"}}>{app.location}</p>}
              </div>
              <span style={{...styles.badge, background:STATUS_COLORS[app.status]}}>{app.status}</span>
            </div>
            <p style={{margin:"0.5rem 0 0",fontSize:"0.8rem",color:"#aaa"}}>{app.applied_date}</p>
          </div>
        ))}
      </div>
    </div>
  );
}

const styles = {
  page: { maxWidth:"1100px", margin:"0 auto", padding:"1.5rem", fontFamily:"sans-serif" },
  header: { display:"flex", justifyContent:"space-between", alignItems:"center", marginBottom:"1.5rem" },
  statsRow: { display:"flex", gap:"0.75rem", flexWrap:"wrap", marginBottom:"1rem" },
  statCard: { background:"white", borderRadius:"6px", padding:"0.75rem 1rem", minWidth:"80px", textAlign:"center", boxShadow:"0 1px 4px rgba(0,0,0,0.08)", display:"flex", flexDirection:"column", gap:"0.2rem" },
  filterRow: { display:"flex", gap:"0.4rem", flexWrap:"wrap", alignItems:"center", marginBottom:"1rem" },
  filterBtn: { padding:"0.3rem 0.7rem", borderRadius:"4px", border:"1px solid #ddd", cursor:"pointer", background:"white", color:"#333", fontSize:"0.85rem" },
  filterActive: { padding:"0.3rem 0.7rem", borderRadius:"4px", border:"1px solid #4f46e5", cursor:"pointer", background:"#4f46e5", color:"white", fontSize:"0.85rem" },
  grid: { display:"grid", gridTemplateColumns:"repeat(auto-fill,minmax(240px,1fr))", gap:"1rem" },
  card: { background:"white", borderRadius:"8px", padding:"1rem", boxShadow:"0 1px 4px rgba(0,0,0,0.08)", cursor:"pointer", transition:"box-shadow 0.2s" },
  badge: { padding:"0.2rem 0.6rem", borderRadius:"12px", color:"white", fontSize:"0.75rem", whiteSpace:"nowrap" },
  modal: { position:"fixed", top:0, left:0, right:0, bottom:0, background:"rgba(0,0,0,0.4)", display:"flex", justifyContent:"center", alignItems:"center", zIndex:100 },
  modalCard: { background:"white", borderRadius:"8px", padding:"1.5rem", width:"420px", maxHeight:"80vh", overflowY:"auto", boxShadow:"0 4px 20px rgba(0,0,0,0.15)" },
  input: { display:"block", width:"100%", margin:"0.4rem 0", padding:"0.6rem", borderRadius:"4px", border:"1px solid #ccc", boxSizing:"border-box", fontFamily:"sans-serif" ,background:"white", color:"#333"},
  btnPrimary: { padding:"0.6rem 1.2rem", background:"#4f46e5", color:"white", border:"none", borderRadius:"4px", cursor:"pointer" },
  btnGhost: { padding:"0.6rem 1.2rem", background:"white", color:"#333", border:"1px solid #ddd", borderRadius:"4px", cursor:"pointer" },
};