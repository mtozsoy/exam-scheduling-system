export interface Room {
  room_code: string;
  building: string;
  floor: number;
  capacity: number;
}

export interface RoomCreateData {
  room_code: string;
  building: string;
  floor: number;
  capacity: number;
}

export interface RoomUpdateData {
  building?: string;
  floor?: number;
  capacity?: number;
}
