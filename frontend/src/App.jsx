import React, { useMemo, useState } from "react";

const API_BASE = "http://localhost:8000";

const GOLDEN_QUESTIONS = [
  "Show top 5 customers by balance",
  "Show recent transactions",
  "Show accounts in Istanbul",
  "List customers",
];

function Table({ columns, rows }) {
  if (!columns?.length) return null;

  return (
    <div style={{ overflowX: "auto", border: "1px solid #ddd", borderRadius: 8 }}>
      <table style={{ width: "100%", borderCollapse: "collapse" }}>
        <thead>
          <tr>
            {columns.map((c) => (
              <th
                key={c}
                style={{
                  textAlign: "left",
                  padding: "10px 12px",
                  borderBottom: "1px solid #ddd",
                  background: "#fafafa",
                  fontWeight: 600,
                }}
              >
                {c}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((r, idx) => (
            <tr key={idx}>
              {r.map((cell, j) => (
                <td
                  key={j}
                  style={{
                    padding: "10px 12px",
                    borderBottom: "1px solid #eee",
                    whiteSpace: "nowrap",
                  }}
                >
                  {cell === null || cell === undefined ? "" : String(cell)}
                </td>
              ))}
            </tr>
          ))}
          {!rows?.length && (
            <tr>
              <td colSpan={columns.length} style={{ padding: 12, color: "#666" }}>
                No rows returned.
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
}

export default function App() {
  const [question, setQuestion] = useState(GOLDEN_QUESTIONS[0]);
  const [loading, setLoading] = useState(false);
  const [sql, setSql] = useState("");
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [ms, setMs] = useState(null);

  const canAsk = useMemo(() => question.trim().length > 0 && !loading, [question, loading]);

  async function onAsk(qOverride) {
    const q = (qOverride ?? question).trim();
    if (!q) return;

    setLoading(true);
    setError("");
    setSql("");
    setResult(null);
    setMs(null);

    const t0 = performance.now();
    try {
      const res = await fetch(`${API_BASE}/ask`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: q }),
      });

      const data = await res.json();
      const t1 = performance.now();
      setMs(Math.round(t1 - t0));

      if (!res.ok) {
        throw new Error(data?.detail || "Request failed");
      }

      setSql(data.sql || "");
      setResult(data.result || null);
    } catch (e) {
      const t1 = performance.now();
      setMs(Math.round(t1 - t0));
      setError(e.message || "Unknown error");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div
      style={{
        maxWidth: 980,
        margin: "40px auto",
        padding: "0 16px",
        fontFamily: "system-ui, -apple-system, Segoe UI, Roboto, sans-serif",
      }}
    >
      <h1 style={{ margin: 0, fontSize: 26 }}>Mock NL → SQL Demo</h1>
      <p style={{ marginTop: 8, color: "#555" }}>
        Type a question. The backend generates SQL, validates it (read-only), runs it on synthetic Postgres,
        and returns a table.
      </p>

      {/* Golden questions */}
      <div style={{ display: "flex", flexWrap: "wrap", gap: 8, marginTop: 14 }}>
        {GOLDEN_QUESTIONS.map((q) => (
          <button
            key={q}
            onClick={() => {
              setQuestion(q);
              onAsk(q); // optional: auto-run when clicked
            }}
            disabled={loading}
            style={{
              padding: "8px 10px",
              borderRadius: 999,
              border: "1px solid #ddd",
              background: "#fff",
              cursor: loading ? "not-allowed" : "pointer",
              fontSize: 13,
            }}
            title="Click to run this test"
          >
            {q}
          </button>
        ))}
      </div>

      {/* Input row */}
      <div style={{ display: "flex", gap: 10, alignItems: "center", marginTop: 14 }}>
        <input
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder='Ask something like: "Show accounts in Istanbul"'
          style={{
            flex: 1,
            padding: "12px 12px",
            borderRadius: 10,
            border: "1px solid #ccc",
            fontSize: 14,
          }}
          onKeyDown={(e) => {
            if (e.key === "Enter" && canAsk) onAsk();
          }}
        />
        <button
          onClick={() => onAsk()}
          disabled={!canAsk}
          style={{
            padding: "12px 14px",
            borderRadius: 10,
            border: "1px solid #111",
            background: loading ? "#eee" : "#111",
            color: loading ? "#111" : "#fff",
            cursor: canAsk ? "pointer" : "not-allowed",
            fontWeight: 600,
            minWidth: 92,
          }}
        >
          {loading ? "Asking..." : "Ask"}
        </button>
      </div>

      {/* Latency */}
      {ms !== null && (
        <div style={{ marginTop: 10, color: "#555", fontSize: 13 }}>
          Response time: <b>{ms} ms</b>
        </div>
      )}

      {/* Error */}
      {error && (
        <div
          style={{
            marginTop: 14,
            padding: 12,
            borderRadius: 10,
            background: "#ffecec",
            border: "1px solid #ffb3b3",
            color: "#7a0000",
          }}
        >
          {error}
        </div>
      )}

      {/* SQL */}
      {sql && (
        <div style={{ marginTop: 18 }}>
          <div style={{ fontWeight: 700, marginBottom: 8 }}>Generated SQL</div>
          <pre
            style={{
              margin: 0,
              padding: 12,
              borderRadius: 10,
              background: "#f6f6f6",
              border: "1px solid #e6e6e6",
              overflowX: "auto",
            }}
          >
            {sql}
          </pre>
        </div>
      )}

      {/* Result */}
      {result && (
        <div style={{ marginTop: 18 }}>
          <div style={{ fontWeight: 700, marginBottom: 8 }}>Result</div>
          <Table columns={result.columns} rows={result.rows} />
        </div>
      )}

      <div style={{ marginTop: 28, color: "#666", fontSize: 13 }}>
        Backend: {API_BASE}
      </div>
    </div>
  );
}
