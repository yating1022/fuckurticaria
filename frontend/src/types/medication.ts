export interface Medication {
  id: number
  user_id: number | null
  name: string
  category: string | null
  default_dose: string | null
  is_system: boolean
}

export interface MedicationRecord {
  id: number
  user_id: number
  medication_id: number
  dose: string
  taken_at: string
  notes: string | null
  is_prn: boolean
  effectiveness: number | null
  side_effects: string[] | null
  feedback_note: string | null
  created_at: string
  medication: Medication | null
}
