export interface Course {
  course_code: string;
  course_name: string;
  semester: number;
  term: number;
}

export interface SchedulingProposalRequest {
  course_code: string;
  exam_type: string;
  duration_minutes: number;
  daily_start_time: string; // HH:MM:SS format
  daily_end_time: string; // HH:MM:SS format
}

export interface RoomDistribution {
  room_code: string;
  capacity: number;
  assigned_count: number;
  students: number[];
  invigilator_id: number;
}

export interface Proposal {
  date: string; // YYYY-MM-DD
  start_time: string; // HH:MM:SS
  end_time: string; // HH:MM:SS
  total_students: number;
  rooms: RoomDistribution[];
}

export interface SchedulingProposalResponse {
  success: boolean;
  message: string;
  proposals: Proposal[];
}

export interface RoomAssignmentInput {
  room_code: string;
  invigilator_id: number;
}

export interface SchedulingConfirmRequest {
  course_code: string;
  exam_type: string;
  date: string; // YYYY-MM-DD
  start_time: string; // HH:MM:SS
  end_time?: string; // HH:MM:SS
  duration_minutes?: number;
  total_students?: number;
  rooms: RoomAssignmentInput[];
}

export interface SchedulingConfirmResponse {
  success: boolean;
  message: string;
  exam_id?: number;
}
