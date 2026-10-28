export type UserRole = 'institute' | 'admin' | 'super_admin';

export interface User {
  id: number;
  username: string;
  email: string;
  full_name: string;
  phone?: string;
  role: UserRole;
  institution_id: number | null;
  institution_name: string | null;
  institution_code: string | null;
  is_active: boolean;
  created_at: string;
  last_login: string | null;
}

export interface Institution {
  id: number;
  code: string;
  name: string;
  type: string;
  state: string;
  district: string;
  address?: string;
  contact_email?: string;
  contact_phone?: string;
  principal_name?: string;
  status: 'active' | 'inactive' | 'suspended';
  created_at: string;
  updated_at: string;
  student_count?: number;
  programme_count?: number;
  upload_count?: number;
  programmes?: Programme[];
  recent_uploads?: UploadBatch[];
  verification_summary?: {
    verified: number;
    pending: number;
    discrepancy: number;
    total: number;
  };
}

export interface Programme {
  id: number;
  institution_id: number;
  institution_name?: string;
  institution_code?: string;
  programme_code: string;
  programme_name: string;
  branch_or_department: string;
  level: string;
  academic_year: string;
  approved_intake: number;
  supernumerary_intake: number;
  total_capacity: number;
  actual_enrolment: number;
  utilization_rate: number;
  discrepancy_status: 'normal' | 'supernumerary_utilized' | 'exceeds_approved_capacity' | 'low_intake_utilization';
  is_demo_intake: boolean;
  created_at: string;
}

export type VerificationStatus =
  | 'not_submitted'
  | 'pending'
  | 'verified'
  | 'unable_to_verify'
  | 'mismatch_detected'
  | 'requires_manual_review'
  | 'rejected';

export interface Student {
  id: number;
  institution_id: number;
  institution_name: string | null;
  institution_code: string | null;
  student_id: string;
  apaar_id_masked: string;
  apaar_id?: string;
  student_name: string;
  programme_id: number | null;
  programme_name: string;
  branch_or_department: string;
  academic_year: string;
  admission_date: string | null;
  enrolment_status: 'Active' | 'Completed' | 'Dropped Out' | 'Suspended' | 'Transferred';
  admission_category: string;
  supernumerary_status: boolean;
  verification_status: VerificationStatus;
  verification_source: string;
  verification_notes: string | null;
  verified_at: string | null;
  is_duplicate_flagged: boolean;
  data_quality_issues?: any[];
  upload_batch_id: number | null;
  created_at: string;
  updated_at: string;
  change_history?: RecordChangeHistory[];
  related_duplicate_cases?: DuplicateReviewCase[];
}

export interface RecordChangeHistory {
  id: number;
  student_id: number;
  changed_by_name: string;
  change_type: string;
  field_name: string | null;
  old_value: string | null;
  new_value: string | null;
  reason: string | null;
  timestamp: string;
}

export interface UploadBatch {
  id: number;
  batch_id: string;
  institution_id: number;
  institution_name?: string;
  institution_code?: string;
  file_name: string;
  file_size_bytes: number;
  file_size_kb: number;
  total_rows: number;
  valid_rows: number;
  invalid_rows: number;
  warning_rows: number;
  duplicate_rows: number;
  status: 'uploaded' | 'previewing' | 'processing' | 'completed' | 'failed';
  error_report?: UploadRowError[];
  error_count: number;
  created_by: string;
  created_at: string;
  completed_at: string | null;
}

export interface UploadRowError {
  row_number: number;
  student_id: string;
  field: string;
  error: string;
  suggestion: string;
}

export interface DuplicateReviewCase {
  id: number;
  case_reference: string;
  issue_type: string;
  severity: 'critical' | 'caution' | 'notice';
  status: 'open' | 'pending_institution_correction' | 'resolved' | 'dismissed' | 'referred';
  institution_id: number;
  institution_name: string | null;
  institution_code: string | null;
  secondary_institution_id: number | null;
  secondary_institution_name: string | null;
  secondary_institution_code: string | null;
  student_id: string;
  student_name: string | null;
  apaar_id_masked: string | null;
  description: string;
  details: any;
  resolution_decision: string | null;
  resolution_notes: string | null;
  resolved_by: string | null;
  detected_at: string;
  resolved_at: string | null;
}

export interface Notification {
  id: number;
  user_id: number | null;
  institution_id: number | null;
  role_target: string;
  title: string;
  message: string;
  link: string | null;
  type: 'info' | 'success' | 'warning' | 'critical';
  is_read: boolean;
  created_at: string;
}

export interface AuditLog {
  id: number;
  actor_id: number | null;
  actor_name: string;
  actor_role: string;
  action: string;
  target_type: string;
  target_id: string | null;
  summary?: string;
  outcome?: string;
  ip_address: string;
  details: any;
  created_at: string;
}
