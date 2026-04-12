// frontend/src/api.js (исправленный)
const API_BASE_URL = 'http://localhost:8000/api';

export async function processCipher(requestBody) {
  // Убеждаемся, что read_method передан
  if (!requestBody.read_method) {
    requestBody.read_method = 'row';
  }
  
  const response = await fetch(`${API_BASE_URL}/process`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(requestBody),
  });
  
  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || `Ошибка ${response.status}: ${response.statusText}`);
  }
  
  const data = await response.json();
  return data;
}

export async function checkHealth() {
  const response = await fetch(`${API_BASE_URL}/health`);
  if (!response.ok) {
    throw new Error('API недоступно');
  }
  return response.json();
}