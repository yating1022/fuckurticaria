export interface OutbreakDetail {
  id: number
  outbreak_id: number
  body_part: string | null
  symptom_type: string | null
  severity: number | null
  photo_id: number | null
}

export interface Outbreak {
  id: number
  user_id: number
  started_at: string
  ended_at: string | null
  severity: number | null
  location_text: string | null
  notes: string | null
  trigger_guess: string | null
  created_at: string
  details: OutbreakDetail[]
}

export interface OutbreakCreate {
  started_at: string
  ended_at?: string | null
  severity?: number | null
  location_text?: string | null
  notes?: string | null
  trigger_guess?: string | null
}
