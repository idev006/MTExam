from enum import StrEnum


class ActiveStatus(StrEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class OrgUnitLevel(StrEnum):
    DIVISION = "division"
    BUREAU = "bureau"
    STATION = "station"
    SUB_UNIT = "sub_unit"


class UserRole(StrEnum):
    SUPER_ADMIN = "super_admin"
    DIVISION_ADMIN = "division_admin"
    BUREAU_ADMIN = "bureau_admin"
    STATION_ADMIN = "station_admin"
    EXAM_AUTHOR = "exam_author"
    EXAM_COORDINATOR = "exam_coordinator"
    EXAMINEE = "examinee"
    VIEWER = "viewer"


class ImportBatchStatus(StrEnum):
    UPLOADED = "uploaded"
    VALIDATING = "validating"
    VALIDATION_FAILED = "validation_failed"
    READY = "ready"
    READY_WITH_WARNING = "ready_with_warning"
    APPLYING = "applying"
    APPLIED = "applied"
    APPLY_FAILED = "apply_failed"


class ImportRowStatus(StrEnum):
    PENDING = "pending"
    VALID = "valid"
    INVALID = "invalid"


class ImportAction(StrEnum):
    ADDED = "added"
    UNCHANGED = "unchanged"
    CHANGED = "changed"
    MOVED = "moved"
    MISSING = "missing"
    REACTIVATE = "reactivate"
    INVALID = "invalid"


class ContentStatus(StrEnum):
    DRAFT = "draft"
    ACTIVE = "active"
    ARCHIVED = "archived"


class PaperSelectionMode(StrEnum):
    FIXED_SET = "fixed_set"
    RANDOM_POOL = "random_pool"


class PaperStatus(StrEnum):
    DRAFT = "draft"
    GENERATED = "generated"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class ExamWindowMode(StrEnum):
    INDIVIDUAL = "individual"
    FIXED_BATCH = "fixed_batch"


class ExamCompletionPolicy(StrEnum):
    FIXED_END = "fixed_end"
    FULL_DURATION = "full_duration"


class ResultVisibilityPolicy(StrEnum):
    IMMEDIATE = "immediate"
    AFTER_WINDOW_CLOSE = "after_window_close"
    HIDDEN = "hidden"


class ExamWindowStatus(StrEnum):
    SCHEDULED = "scheduled"
    OPEN = "open"
    SUSPENDED = "suspended"
    CLOSED = "closed"
    CANCELLED = "cancelled"


class ExamSessionStatus(StrEnum):
    IN_PROGRESS = "in_progress"
    SUBMITTED = "submitted"
    TIMED_OUT = "timed_out"
    FORCE_CLOSED = "force_closed"
