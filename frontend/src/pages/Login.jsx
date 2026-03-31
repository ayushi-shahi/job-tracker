import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import api from "../api";

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const navigate = useNavigate();

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    try {
      const res = await api.post("/auth/login", { email, password });
      localStorage.setItem("token", res.data.token);
      navigate("/");
    } catch (err) {
      setError(err.response?.data?.error || "Login failed");
    }
  }

  return (
    <div style={styles.container}>
      <div style={styles.card}>
        <h2>Job Tracker — Login</h2>
        {error && <p style={styles.error}>{error}</p>}
        <form onSubmit={handleSubmit}>
          <input style={styles.input} type="email" placeholder="Email"
            value={email} onChange={e => setEmail(e.target.value)} required />
          <input style={styles.input} type="password" placeholder="Password"
            value={password} onChange={e => setPassword(e.target.value)} required />
          <button style={styles.button} type="submit">Login</button>
        </form>
        <p>No account? <Link to="/register">Register</Link></p>
      </div>
    </div>
  );
}

const styles = {
  container: { display:"flex", justifyContent:"center", alignItems:"center", height:"100vh", background:"#f0f2f5" },
  card: { background:"white", padding:"2rem", borderRadius:"8px", width:"320px", boxShadow:"0 2px 8px rgba(0,0,0,0.1)" },
  input: { display:"block", width:"100%", margin:"0.5rem 0", padding:"0.6rem", borderRadius:"4px", border:"1px solid #ccc", boxSizing:"border-box", background:"white", color:"#333" },  button: { width:"100%", padding:"0.7rem", background:"#4f46e5", color:"white", border:"none", borderRadius:"4px", cursor:"pointer", marginTop:"0.5rem" },
  error: { color:"red", fontSize:"0.9rem" }
};