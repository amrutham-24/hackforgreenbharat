export default function NotFound() {
  return (
    <div style={{ padding: "2rem", textAlign: "center" }}>
      <h2 style={{ fontSize: "1.5rem", fontWeight: "bold" }}>Page Not Found</h2>
      <p style={{ color: "#666", marginTop: "0.5rem" }}>The page you are looking for does not exist.</p>
      <a href="/dashboard" style={{ color: "#10b981", marginTop: "1rem", display: "inline-block" }}>
        Go to Dashboard
      </a>
    </div>
  );
}
