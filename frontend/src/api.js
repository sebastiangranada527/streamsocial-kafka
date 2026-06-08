// Módulo que encapsula las llamadas a la API de StreamSocial.
// Aísla la lógica de red del resto de la interfaz.

// URL base de la API de Python (FastAPI corre en el puerto 8000)
const API_URL = "http://localhost:8000";

// Obtiene los eventos recientes procesados por el consumidor.
export async function fetchRecentEvents() {
  const response = await fetch(`${API_URL}/events/recent`);
  if (!response.ok) {
    throw new Error(`Error HTTP: ${response.status}`);
  }
  return response.json();
}

// Publica un evento de registro de usuario (lo usaremos para generar datos).
export async function registerUser(userId, email) {
  const response = await fetch(`${API_URL}/events/user/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ user_id: userId, email: email }),
  });
  if (!response.ok) {
    throw new Error(`Error HTTP: ${response.status}`);
  }
  return response.json();
}
