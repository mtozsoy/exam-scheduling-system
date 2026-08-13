import type {
  Course,
  SchedulingProposalRequest,
  SchedulingProposalResponse,
  SchedulingConfirmRequest,
  SchedulingConfirmResponse,
} from "../types/scheduling";

const BASE_URL = "http://localhost:8000";

/**
 * Yardımcı fonksiyon: Fetch isteklerini işler ve backend'den gelen HTTP hatalarını yakalar.
 */
async function fetchWithErrorHandling<T>(url: string, options?: RequestInit): Promise<T> {
  const response = await fetch(url, options);

  if (!response.ok) {
    let errorMessage = `HTTP Error ${response.status}`;
    try {
      const errorData = await response.json();
      if (errorData.detail) {
        // FastAPI'den dönen standart hata (HTTPException detail)
        errorMessage = errorData.detail;
      } else if (errorData.message) {
        errorMessage = errorData.message;
      }
    } catch (e) {
      // JSON parse hatası veya düz metin
      const text = await response.text();
      if (text) errorMessage = text;
    }
    throw new Error(errorMessage);
  }

  return response.json();
}

/**
 * Sistemdeki tüm dersleri (Courses) getirir.
 */
export async function getCourses(): Promise<Course[]> {
  return fetchWithErrorHandling<Course[]>(`${BASE_URL}/courses`);
}

/**
 * Verilen kriterlere ve akademik takvime göre sınav planı önerileri üretir.
 */
export async function getSchedulingProposals(
  request: SchedulingProposalRequest
): Promise<SchedulingProposalResponse> {
  return fetchWithErrorHandling<SchedulingProposalResponse>(
    `${BASE_URL}/scheduling/proposals`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(request),
    }
  );
}

/**
 * Seçilen sınav önerisini veritabanına kaydeder (onaylar).
 */
export async function confirmScheduling(
  request: SchedulingConfirmRequest
): Promise<SchedulingConfirmResponse> {
  return fetchWithErrorHandling<SchedulingConfirmResponse>(
    `${BASE_URL}/scheduling/confirm`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(request),
    }
  );
}
