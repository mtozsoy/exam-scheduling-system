import type { Course } from "./scheduling";

export type { Course };

export interface CourseCreateData {
  course_code: string;
  course_name: string;
  term: number;
  semester: number;
}

export interface CourseUpdateData {
  course_name?: string;
  term?: number;
  semester?: number;
}
