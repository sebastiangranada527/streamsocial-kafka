import { useState, useEffect } from "react";
import { fetchRecentEvents, registerUser } from "../api";

// Componente principal del dashboard de StreamSocial.
function Dashboard() {
  // --- ESTADO ---
  // useState crea "variables reactivas": cuando cambian, React repinta la UI.
  // [valor, funcionParaCambiarlo] = useState(valorInicial)
  const [events, setEvents] = useState([]); // lista de eventos
  const [total, setTotal] = useState(0); // total acumulado
  const [error, setError] = useState(null); // mensaje de error, si hay

  // --- EFECTO: POLLING ---
  // useEffect ejecuta código en momentos del ciclo de vida del componente.
  // Aquí: arranca un intervalo que consulta la API cada 2 segundos.
  useEffect(() => {
    // Función que pide los eventos a la API y actualiza el estado.
    async function loadEvents() {
      try {
        const data = await fetchRecentEvents();
        setEvents(data.events);
        setTotal(data.total);
        setError(null);
      } catch {
        setError("No se pudo conectar con la API. ¿Está corriendo?");
      }
    }

    loadEvents(); // primera carga inmediata
    const intervalId = setInterval(loadEvents, 2000); // cada 2 segundos

    // Limpieza: cuando el componente se desmonta, detener el intervalo.
    // Sin esto, el intervalo seguiría corriendo y causaría fugas de memoria.
    return () => clearInterval(intervalId);
  }, []); // [] = ejecutar solo una vez, al montar el componente

  // --- MÉTRICAS DERIVADAS ---
  // Se calculan a partir de los eventos. No necesitan estado propio.
  const registros = events.filter(
    (e) => e.event_type === "user_registration"
  ).length;
  const likes = events.filter((e) => e.event_type === "content_like").length;

  // --- ACCIÓN: generar un evento de prueba ---
  async function handleRegister() {
    const randomId = `user_${Math.floor(Math.random() * 10000)}`;
    try {
      await registerUser(randomId, `${randomId}@example.com`);
    } catch {
      setError("No se pudo publicar el evento.");
    }
  }

  // --- RENDER (JSX) ---
  return (
    <div style={{ fontFamily: "sans-serif", maxWidth: 800, margin: "0 auto" }}>
      <h1>📡 StreamSocial — Dashboard en vivo</h1>

      {error && <p style={{ color: "red" }}>{error}</p>}

      <button onClick={handleRegister} style={{ marginBottom: 20 }}>
        Generar registro de usuario
      </button>

      {/* Métricas */}
      <div style={{ display: "flex", gap: 20, marginBottom: 20 }}>
        <MetricCard label="Total eventos" value={total} />
        <MetricCard label="Registros" value={registros} />
        <MetricCard label="Likes" value={likes} />
      </div>

      {/* Lista de eventos recientes */}
      <h2>Eventos recientes</h2>
      <ul>
        {events.map((e) => (
          <li key={e.event_id}>
            <strong>{e.event_type}</strong> — {e.user_id}
            <span style={{ color: "#888" }}> ({e.timestamp})</span>
          </li>
        ))}
      </ul>
    </div>
  );
}

// Componente pequeño y reutilizable para mostrar una métrica.
function MetricCard({ label, value }) {
  return (
    <div
      style={{
        border: "1px solid #ccc",
        borderRadius: 8,
        padding: 16,
        textAlign: "center",
        minWidth: 120,
      }}
    >
      <div style={{ fontSize: 32, fontWeight: "bold" }}>{value}</div>
      <div style={{ color: "#666" }}>{label}</div>
    </div>
  );
}

export default Dashboard;
