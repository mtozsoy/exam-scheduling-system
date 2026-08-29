export interface Exam {
  exam_id: number;
  course_code: string;
  exam_type: string;
  date: string;
  start_time: string;
  duration_minutes: number;
}

export interface ExamUpdateData {
  exam_type: string;
  date: string;
  start_time: string;
  duration_minutes: number;
}
