const API_BASE_URL = "http://localhost:3001";

export async function predictAdmission(formData) {
  const response = await fetch(`${API_BASE_URL}/api/predict`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(formData),
  });

  if (!response.ok) {
    const errorBody = await response.text();
    throw new Error(`API error ${response.status}: ${errorBody}`);
  }

  return response.json();
}