import type {
  Course,
  SchedulingProposalRequest,
  SchedulingProposalResponse,
  SchedulingConfirmRequest,
  SchedulingConfirmResponse,
} from "../types/scheduling";
import type { Exam, ExamUpdateData, StudentExamRoomResponse } from "../types/exams";
import type { Room, RoomCreateData, RoomUpdateData } from "../types/rooms";
import type { Invigilator, InvigilatorCreateData, InvigilatorUpdateData } from "../types/invigilators";
import type { 
  AcademicCalendar, 
  AcademicCalendarCreateData, 
  AcademicCalendarUpdateData 
} from "../types/academic_calendars";

export interface User {
  KullaniciID: number;
  KullaniciAdi: string;
  Rol: string;
}

export interface UserCreateData {
  username: string;
  password?: string;
  role: string;
}

export interface UserUpdateData {
  username?: string;
  password?: string;
  role?: string;
}


const BASE_URL = "http://localhost:8000/api/v1";

/**
 * Yardımcı fonksiyon: Fetch isteklerini işler ve backend'den gelen HTTP hatalarını yakalar.
 * Ayrıca localStorage'dan token'ı alarak Authorization header'ına ekler.
 */
async function fetchWithErrorHandling<T>(url: string, options?: RequestInit): Promise<T> {
  const token = localStorage.getItem("token");
  const headers = new Headers(options?.headers || {});
  
  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  const newOptions = { ...options, headers };
  const response = await fetch(url, newOptions);

  if (response.status === 401) {
    localStorage.removeItem("token");
    localStorage.removeItem("role");
    localStorage.removeItem("username");
    window.location.reload();
    throw new Error("Oturum süresi doldu. Lütfen tekrar giriş yapın.");
  }

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

  // Handle 204 No Content which has no JSON body
  if (response.status === 204) {
    return {} as T;
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
 * Yeni bir ders oluşturur.
 */
export async function createCourse(data: {
  course_code: string;
  course_name: string;
  term: number;
  semester: number;
}): Promise<Course> {
  return fetchWithErrorHandling<Course>(
    `${BASE_URL}/courses`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(data),
    }
  );
}

/**
 * Mevcut bir dersi günceller.
 */
export async function updateCourse(
  courseCode: string,
  data: {
    course_name?: string;
    term?: number;
    semester?: number;
  }
): Promise<Course> {
  return fetchWithErrorHandling<Course>(
    `${BASE_URL}/courses/${courseCode}`,
    {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(data),
    }
  );
}

/**
 * Bir dersi siler.
 */
export async function deleteCourse(courseCode: string): Promise<{ success: boolean; message: string }> {
  return fetchWithErrorHandling<{ success: boolean; message: string }>(
    `${BASE_URL}/courses/${courseCode}`,
    {
      method: "DELETE",
    }
  );
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

/**
 * Planlanmış tüm sınavları getirir.
 */
export async function getExams(): Promise<Exam[]> {
  return fetchWithErrorHandling<Exam[]>(`${BASE_URL}/exams`);
}

/**
 * Planlanmış bir sınavı günceller.
 */
export async function updateExam(
  examId: number,
  data: ExamUpdateData
): Promise<Exam> {
  return fetchWithErrorHandling<Exam>(
    `${BASE_URL}/exams/${examId}`,
    {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(data),
    }
  );
}

/**
 * Planlanmış bir sınavı siler.
 */
export async function deleteExam(examId: number): Promise<{ success: boolean; message: string }> {
  return fetchWithErrorHandling<{ success: boolean; message: string }>(
    `${BASE_URL}/exams/${examId}`,
    {
      method: "DELETE",
    }
  );
}

/**
 * Sınavın öğrenci-derslik dağılımını getirir.
 */
export async function getExamDistributions(examId: number): Promise<StudentExamRoomResponse[]> {
  return fetchWithErrorHandling<StudentExamRoomResponse[]>(`${BASE_URL}/exams/${examId}/distributions`);
}

/**
 * Sistemdeki tüm derslikleri (Rooms) getirir.
 */
export async function getRooms(): Promise<Room[]> {
  return fetchWithErrorHandling<Room[]>(`${BASE_URL}/rooms`);
}

/**
 * Yeni bir derslik oluşturur.
 */
export async function createRoom(data: RoomCreateData): Promise<Room> {
  return fetchWithErrorHandling<Room>(
    `${BASE_URL}/rooms`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(data),
    }
  );
}

/**
 * Mevcut bir dersliği günceller.
 */
export async function updateRoom(
  roomCode: string,
  data: RoomUpdateData
): Promise<Room> {
  return fetchWithErrorHandling<Room>(
    `${BASE_URL}/rooms/${roomCode}`,
    {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(data),
    }
  );
}

/**
 * Bir dersliği siler.
 */
export async function deleteRoom(roomCode: string): Promise<{ success: boolean; message: string }> {
  return fetchWithErrorHandling<{ success: boolean; message: string }>(
    `${BASE_URL}/rooms/${roomCode}`,
    {
      method: "DELETE",
    }
  );
}

/**
 * Sistemdeki tüm gözetmenleri (Invigilators) getirir.
 */
export async function getInvigilators(): Promise<Invigilator[]> {
  return fetchWithErrorHandling<Invigilator[]>(`${BASE_URL}/invigilators`);
}

/**
 * Yeni bir gözetmen oluşturur.
 */
export async function createInvigilator(data: InvigilatorCreateData): Promise<Invigilator> {
  return fetchWithErrorHandling<Invigilator>(
    `${BASE_URL}/invigilators`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(data),
    }
  );
}

/**
 * Mevcut bir gözetmeni günceller.
 */
export async function updateInvigilator(
  invigilatorId: number,
  data: InvigilatorUpdateData
): Promise<Invigilator> {
  return fetchWithErrorHandling<Invigilator>(
    `${BASE_URL}/invigilators/${invigilatorId}`,
    {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(data),
    }
  );
}

/**
 * Bir gözetmeni siler.
 */
export async function deleteInvigilator(invigilatorId: number): Promise<{ success: boolean; message: string }> {
  return fetchWithErrorHandling<{ success: boolean; message: string }>(
    `${BASE_URL}/invigilators/${invigilatorId}`,
    {
      method: "DELETE",
    }
  );
}

/**
 * Sistemdeki tüm akademik takvimleri getirir.
 */
export async function getAcademicCalendars(): Promise<AcademicCalendar[]> {
  return fetchWithErrorHandling<AcademicCalendar[]>(`${BASE_URL}/academic-calendars`);
}

/**
 * Aktif olan akademik takvimleri getirir.
 */
export async function getActiveAcademicCalendars(): Promise<AcademicCalendar[]> {
  return fetchWithErrorHandling<AcademicCalendar[]>(`${BASE_URL}/academic-calendars/active`);
}

/**
 * Yeni bir akademik takvim oluşturur.
 */
export async function createAcademicCalendar(data: AcademicCalendarCreateData): Promise<AcademicCalendar> {
  return fetchWithErrorHandling<AcademicCalendar>(
    `${BASE_URL}/academic-calendars`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(data),
    }
  );
}

/**
 * Mevcut bir akademik takvimi günceller.
 */
export async function updateAcademicCalendar(
  calendarId: number,
  data: AcademicCalendarUpdateData
): Promise<AcademicCalendar> {
  return fetchWithErrorHandling<AcademicCalendar>(
    `${BASE_URL}/academic-calendars/${calendarId}`,
    {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(data),
    }
  );
}

/**
 * Bir akademik takvimi siler.
 */
export async function deleteAcademicCalendar(calendarId: number): Promise<{ success: boolean; message: string }> {
  return fetchWithErrorHandling<{ success: boolean; message: string }>(
    `${BASE_URL}/academic-calendars/${calendarId}`,
    {
      method: "DELETE",
    }
  );
}

// ========================
// Kullanıcı Yönetimi (Admin)
// ========================

export async function getUsers(): Promise<User[]> {
  return fetchWithErrorHandling<User[]>(`${BASE_URL}/users`);
}

export async function createUser(data: UserCreateData): Promise<User> {
  return fetchWithErrorHandling<User>(
    `${BASE_URL}/users`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    }
  );
}

export async function updateUser(userId: number, data: UserUpdateData): Promise<User> {
  return fetchWithErrorHandling<User>(
    `${BASE_URL}/users/${userId}`,
    {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    }
  );
}

export async function deleteUser(userId: number): Promise<void> {
  return fetchWithErrorHandling<void>(
    `${BASE_URL}/users/${userId}`,
    {
      method: "DELETE",
    }
  );
}
