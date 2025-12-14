import React, { useMemo, useState } from "react";
import "./App.css";

const API_BASE = "http://localhost:8000";

const GOLDEN_QUESTIONS = [
  "Show top 5 customers by balance",
  "Show recent transactions",
  "Show accounts in Istanbul",
  "List customers",
];

function ResultTable({ columns, rows }) {
  if (!columns?.length) return null;

  return (
    <div className="card">
      <div className="cardTitle">Result</div>
      <div className="tableWrap">
        <table className="tbl">
          <thead>
            <tr>
              {columns.map((c) => (
                <th key={c}>{c}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows?.length ? (
              rows.map((r, i) => (
                <tr key={i}>
                  {r.map((cell, j) => (
                    <td key={j}>{cell === null || cell === undefined ? "" : String(cell)}</td>
                  ))}
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan={columns.length} className="emptyCell">
                  No rows returned.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default function App() {
  const [question, setQuestion] = useState("");
  const [loading, setLoading] = useState(false);

  const [sql, setSql] = useState("");
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [ms, setMs] = useState(null);

  // “presentation” controls (UI only)
  const [dbUser, setDbUser] = useState("LP61205");
  const [dbPass, setDbPass] = useState("••••••••••••");
  const [connOk, setConnOk] = useState(true);

  const [showSQL, setShowSQL] = useState(true);
  const [showTable, setShowTable] = useState(true);

  const canAsk = useMemo(() => question.trim().length > 0 && !loading, [question, loading]);

  async function ask(qOverride) {
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

      if (!res.ok) throw new Error(data?.detail || "Request failed");

      setSql(data.sql || "");
      setResult(data.result || null);
    } catch (e) {
      const t1 = performance.now();
      setMs(Math.round(t1 - t0));
      const msg = (e.message || "Unknown error");
      if (msg.includes("Unknown LLM_MODE")) {
        setError("Model yapılandırması hatalı. Lütfen sistem yöneticisiyle iletişime geçin.");
      } else {
        setError(msg);
      }

    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="layout">
      {/* Sidebar */}
      <aside className="sidebar">
        <div className="brand">
          <div className="brandLogo">AKBANK</div>
        </div>

        <div className="nav">
          <div className="navItem active">🏠 AnaSayfa</div>
          <div className="navItem">📘 Eğitim</div>
          <div className="navItem">🗂️ Eğitilen Veriler</div>
        </div>

        <details className="panel" open>
          <summary>Kullanıcı DB Bilgileri</summary>

          <label className="label">Database Username</label>
          <input className="input" value={dbUser} onChange={(e) => setDbUser(e.target.value)} />

          <label className="label">Database Şifre</label>
          <div className="row">
            <input
              className="input"
              value={dbPass}
              onChange={(e) => setDbPass(e.target.value)}
              type="password"
            />
            <button className="iconBtn" title="show/hide" onClick={() => {}}>
              👁️
            </button>
          </div>

          <button
            className="btn"
            onClick={() => {
              // mock “update connection”
              setConnOk(true);
            }}
          >
            Güncelle
          </button>

          <div className={`status ${connOk ? "ok" : "bad"}`}>
            {connOk ? "Bağlantı Başarılı." : "Bağlantı Hatası."}
          </div>
        </details>

        <details className="panel" open>
          <summary>Çıktı Seçenekleri</summary>

          <label className="check">
            <input type="checkbox" checked={showSQL} onChange={(e) => setShowSQL(e.target.checked)} />
            SQL Sorgusunu Göster
          </label>

          <label className="check">
            <input
              type="checkbox"
              checked={showTable}
              onChange={(e) => setShowTable(e.target.checked)}
            />
            Tabloyu Göster
          </label>
        </details>

        <details className="panel">
          <summary>Örnek Sorular</summary>
          <div className="chips">
            {GOLDEN_QUESTIONS.map((q) => (
              <button
                key={q}
                className="chip"
                disabled={loading}
                onClick={() => {
                  setQuestion(q);
                  ask(q);
                }}
                title="Click to run"
              >
                {q}
              </button>
            ))}
          </div>
        </details>

        <button
          className="btn ghost"
          onClick={() => {
            setQuestion("");
            setSql("");
            setResult(null);
            setError("");
            setMs(null);
          }}
        >
          ✏️ Yeni Sohbet
        </button>

        <div className="smallNote">
          Backend: <span className="mono">{API_BASE}</span>
        </div>
      </aside>

      {/* Main */}
      <main className="main">
        <div className="topbar">
          <div className="topbarRight">
            <button className="topIcon" title="Accessibility">♿</button>
            <button className="topIcon" title="Stop" onClick={() => {}}>Stop</button>
            <button className="topIcon" title="Menu">⋮</button>
          </div>
        </div>

        <div className="hero">
          <h1>Doğal Dil ile Veri Analizi</h1>
          <p>Sorularınızı Sorgulara Dönüştürün</p>
        </div>

        {/* “Chat bubble” area like slides */}
        <div className="content">
          {(loading || sql || result || error) && (
            <div className="bubble">
              <div className="bubbleIcon">🤖</div>
              <div className="bubbleText">
                <div className="bubbleQ">{question || "—"}</div>
                {loading && <div className="muted">SQL üretiliyor…</div>}
                {ms !== null && <div className="muted">Yanıt süresi: <b>{ms} ms</b></div>}
              </div>
            </div>
          )}

          {error && <div className="error">{error}</div>}

          {showSQL && sql && (
            <div className="card">
              <div className="cardTitle">Generated SQL</div>
              <pre className="code">{sql}</pre>
            </div>
          )}

          {showTable && result && (
            <ResultTable columns={result.columns} rows={result.rows} />
          )}
        </div>

        {/* Bottom prompt bar */}
        <div className="promptBar">
          <input
            className="promptInput"
            placeholder="Veriniz ile ilgili bir soru sorun"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && canAsk) ask();
            }}
          />
          <button className="sendBtn" disabled={!canAsk} onClick={() => ask()} title="Send">
            ➤
          </button>
        </div>
      </main>
    </div>
  );
}
