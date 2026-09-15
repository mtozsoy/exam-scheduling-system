export interface Invigilator {
  invigilator_id: number;
  first_name: string;
  last_name: string;
}

export interface InvigilatorCreateData {
  first_name: string;
  last_name: string;
}

export interface InvigilatorUpdateData {
  first_name?: string;
  last_name?: string;
}
