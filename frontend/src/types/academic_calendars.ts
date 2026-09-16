export interface AcademicCalendar {
  calendar_id: number;
  academic_year: string;
  semester: string;
  exam_type: string;
  start_date: string;
  end_date: string;
  is_active: boolean;
}

export interface AcademicCalendarCreateData {
  academic_year: string;
  semester: string;
  exam_type: string;
  start_date: string;
  end_date: string;
  is_active: boolean;
}

export interface AcademicCalendarUpdateData {
  academic_year?: string;
  semester?: string;
  exam_type?: string;
  start_date?: string;
  end_date?: string;
  is_active?: boolean;
}
