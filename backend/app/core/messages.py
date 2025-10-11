"""
Centralized message constants for API responses.

This module provides all error and success messages for the application,
preparing for future internationalization (i18n) support.

Organization:
- ErrorMessages: Error messages grouped by HTTP status code
- SuccessMessages: Success messages for operations
- ValidationMessages: Input validation messages

Usage:
    from app.core.messages import ErrorMessages, SuccessMessages

    raise HTTPException(
        status_code=404,
        detail=ErrorMessages.CALENDAR_NOT_FOUND
    )

i18n Future:
    When adding i18n support, convert these to translation keys:
    - Current: "Calendar not found"
    - Future: t('errors.calendar_not_found')
"""


class ErrorMessages:
    """Error messages grouped by category and status code."""

    # ==========================================================================
    # 400 BAD REQUEST - Client input errors
    # ==========================================================================

    # Required fields
    CALENDAR_NAME_REQUIRED = "Calendar name is required"
    SOURCE_URL_REQUIRED = "Source URL is required"
    FILTER_NAME_REQUIRED = "Filter name is required"
    GROUP_NAME_REQUIRED = "Group name is required"
    USERNAME_REQUIRED = "username is required"
    PASSWORD_REQUIRED = "Password is required"
    RECURRING_EVENT_TITLE_REQUIRED = "recurring_event_title is required"
    RECURRING_EVENT_TITLES_REQUIRED = "recurring_event_titles is required"
    GROUP_ID_AND_EVENTS_REQUIRED = "group_id and recurring_event_titles are required"
    EMAIL_REQUIRED_FOR_PASSWORD = "Email address is required when setting a password (needed for password reset)"
    EMAIL_REQUIRED_FOR_DOMAIN_REQUEST = "Email address is required to request a domain. Please add an email to your profile first."

    # Field validation
    RECURRING_EVENT_TITLES_MUST_BE_ARRAY = "recurring_event_titles must be an array"
    CONFIGURATION_MUST_BE_OBJECT = "Configuration must be an object/dictionary"
    CALENDAR_URL_MUST_START_HTTP = "Calendar URL must start with http:// or https://"
    DOMAIN_KEY_INVALID_FORMAT = "Domain key must contain only lowercase letters, numbers, and hyphens"

    # Password validation
    PASSWORD_MIN_LENGTH = "Password must be at least {min_length} characters long"
    ADMIN_PASSWORD_MIN_LENGTH = "Admin password must be at least 4 characters"
    CURRENT_PASSWORD_REQUIRED = "Current password required to change password"
    CURRENT_PASSWORD_INCORRECT = "Current password is incorrect"
    PASSWORD_REQUIRED_FOR_ACCOUNT = "Password required for this account"

    # Invalid input
    INVALID_FILTER_CONFIGURATION = "Invalid filter configuration"
    INVALID_ADMIN_PASSWORD = "Invalid admin password"
    INVALID_USERNAME_OR_PASSWORD = "Invalid username or password"
    INVALID_AUTHORIZATION_HEADER = "Invalid authorization header format. Use: Bearer <token>"
    AUTHORIZATION_HEADER_REQUIRED = "Authorization header required"

    # Calendar validation
    CALENDAR_NO_EVENTS = "Calendar contains no events. Please add events to your calendar before submitting a request."
    CALENDAR_URL_NO_EVENTS = "Calendar URL is valid but contains no events"
    CALENDAR_URL_TIMEOUT = "Calendar URL timed out - URL took too long to respond"

    # File validation
    FILE_MUST_BE_UTF8 = "File must be UTF-8 encoded text"
    YAML_FILE_EMPTY = "YAML file is empty or invalid"
    YAML_FORMAT_INVALID = "Invalid YAML format: {error}"
    YAML_MISSING_SECTION = "Missing required section: '{section}'"
    CANNOT_DELETE_DOMAINS_REGISTRY = "Cannot delete the domains registry file"

    # Token validation
    TOKEN_AND_PASSWORD_REQUIRED = "token and new_password are required"
    RESET_TOKEN_EXPIRED = "Reset token has expired"
    RESET_TOKEN_USED = "Reset token has already been used"
    INVALID_OR_EXPIRED_TOKEN = "Invalid or expired token"
    INVALID_OR_EXPIRED_RESET_TOKEN = "Invalid or expired reset token"

    # Generic field required
    FIELD_REQUIRED = "{field} is required"

    # ==========================================================================
    # 401 UNAUTHORIZED - Authentication failures
    # ==========================================================================

    INVALID_CREDENTIALS = "Invalid username or password"
    AUTH_REQUIRED = "Authentication required"

    # ==========================================================================
    # 403 FORBIDDEN - Authorization/Permission errors
    # ==========================================================================

    ACCESS_DENIED = "Access denied"
    ACCESS_DENIED_OWNER_ONLY = "Access denied. Only domain owner can perform this action"
    ACCESS_DENIED_OWNER_ADD_ADMINS = "Access denied. Only domain owner can add admins"
    ACCESS_DENIED_OWNER_REMOVE_ADMINS = "Access denied. Only domain owner can remove admins"
    ACCESS_DENIED_OWNER_OR_ADMIN_VIEW = "Access denied. Only domain owner or admins can view admin list"
    ACCESS_DENIED_OWNER_OR_GLOBAL_ADMIN = "You must be the domain owner or global admin to manage passwords"
    ACCOUNT_LOCKED = "Account locked due to too many failed login attempts. Try again in {minutes} minutes"
    LOGIN_ATTEMPTS_REMAINING = "Invalid username or password. {attempts} attempts remaining before lockout"

    # ==========================================================================
    # 404 NOT FOUND - Resource not found
    # ==========================================================================

    CALENDAR_NOT_FOUND = "Calendar not found"
    FILTER_NOT_FOUND = "Filter not found"
    GROUP_NOT_FOUND = "Group not found"
    DOMAIN_NOT_FOUND = "Domain '{domain}' not found"
    USER_NOT_FOUND = "User not found"
    USERNAME_NOT_FOUND = "Username not found"
    DOMAIN_REQUEST_NOT_FOUND = "Domain request not found"
    BACKUP_NOT_FOUND = "Backup not found"
    CONFIG_NOT_FOUND = "Configuration file not found"

    # ==========================================================================
    # 409 CONFLICT - Resource conflicts
    # ==========================================================================

    USERNAME_TAKEN = "Username already taken"
    EMAIL_TAKEN = "Email already taken"
    EMAIL_REGISTERED = "Email already registered"
    DOMAIN_OWNER_ALREADY_ADMIN = "Domain owner is already admin by default"
    USER_ALREADY_ADMIN = "User '{username}' is already an admin"
    USER_NOT_ADMIN = "User '{username}' is not an admin"
    DOMAIN_KEY_EXISTS = "Domain key already exists"

    # ==========================================================================
    # 500 INTERNAL SERVER ERROR - Server errors
    # ==========================================================================

    INTERNAL_SERVER_ERROR = "Internal server error: {error}"
    EXPORT_ERROR = "Export error: {error}"
    IMPORT_ERROR = "Import error: {error}"
    CACHE_ERROR = "Cache error: {error}"
    SYNC_ERROR = "Sync failed: {error}"
    RESET_ERROR = "Reset error: {error}"
    BACKUP_ERROR = "Backup operation failed: {error}"
    RESTORE_ERROR = "Restore operation failed: {error}"
    DELETE_ERROR = "Delete operation failed: {error}"
    RULE_APPLICATION_ERROR = "Rule application failed: {error}"
    NO_BASELINE_CONFIG = "No baseline configuration found: {error}"
    ADMIN_PASSWORD_SET_FAILED = "Admin password set failed: {error}"
    USER_PASSWORD_SET_FAILED = "User password set failed: {error}"
    ADMIN_PASSWORD_REMOVAL_FAILED = "Admin password removal failed: {error}"
    USER_PASSWORD_REMOVAL_FAILED = "User password removal failed: {error}"


class SuccessMessages:
    """Success messages for API operations."""

    # Calendar operations
    CALENDAR_CREATED = "Calendar created successfully"
    CALENDAR_DELETED = "Calendar deleted successfully"
    CALENDAR_UPDATED = "Calendar updated successfully"

    # Filter operations
    FILTER_CREATED = "Filter created successfully"
    FILTER_UPDATED = "Filter updated successfully"
    FILTER_DELETED = "Filter deleted successfully"

    # Group operations
    GROUP_CREATED = "Group created successfully"
    GROUP_UPDATED = "Group updated successfully"
    GROUP_DELETED = "Group deleted successfully"

    # Event assignment operations
    EVENTS_ASSIGNED = "{count} recurring events assigned to group"
    EVENTS_REMOVED = "{count} events removed from group"
    EVENTS_UNASSIGNED = "{count} recurring events unassigned"
    EVENT_UNASSIGNED = "Event '{title}' unassigned"

    # Backup operations
    BACKUP_CREATED = "Backup created successfully"
    BACKUP_DELETED = "Backup deleted successfully"
    BACKUP_RESTORED = "Domain restored from backup"

    # Domain operations
    DOMAIN_CREATED = "Domain '{domain_key}' created successfully"
    DOMAIN_UPDATED = "Domain updated successfully"
    DOMAIN_DELETED = "Domain deleted successfully"

    # Password operations
    PASSWORD_SET = "Password set successfully"
    PASSWORD_UPDATED = "Password updated successfully"
    PASSWORD_REMOVED = "Password removed successfully"
    ADMIN_PASSWORD_SET = "Admin password set successfully"
    USER_PASSWORD_SET = "User password set successfully"
    ADMIN_PASSWORD_REMOVED = "Admin password removed successfully"
    USER_PASSWORD_REMOVED = "User password removed successfully"

    # User operations
    USER_REGISTERED = "User registered successfully"
    USER_LOGGED_IN = "Login successful"
    USER_UPDATED = "Profile updated successfully"

    # Admin operations
    ADMIN_ADDED = "Admin added successfully"
    ADMIN_REMOVED = "Admin removed successfully"
    DOMAIN_REQUEST_APPROVED = "Domain request approved and calendar created"
    DOMAIN_REQUEST_REJECTED = "Domain request rejected"

    # Configuration operations
    CONFIG_UPLOADED = "Configuration file '{filename}' uploaded successfully"
    CONFIG_DELETED = "Configuration file '{filename}' deleted (backed up to {backup_filename})"
    CONFIG_SYNCED = "Configuration synced successfully"
    CONFIG_RESET = "Configuration reset to baseline"
    CONFIG_IMPORTED = "Successfully imported {groups} groups, {assignments} assignments, {rules} rules"

    # Generic success
    OPERATION_SUCCESSFUL = "Operation successful"
    NO_CHANGES_REQUESTED = "No changes requested"


class ValidationMessages:
    """Input validation messages."""

    # Username validation
    USERNAME_TOO_SHORT = "Username must be at least 3 characters long"
    USERNAME_TOO_LONG = "Username must not exceed 50 characters"
    USERNAME_INVALID_CHARS = "Username can only contain letters, numbers, underscores, and hyphens"

    # Email validation
    EMAIL_INVALID = "Invalid email address format"

    # Password validation
    PASSWORD_TOO_SHORT = "Password must be at least 8 characters long"
    PASSWORD_TOO_LONG = "Password must not exceed 100 characters"

    # Domain key validation
    DOMAIN_KEY_TOO_SHORT = "Domain key must be at least 3 characters long"
    DOMAIN_KEY_TOO_LONG = "Domain key must not exceed 100 characters"
    DOMAIN_KEY_INVALID_CHARS = "Domain key can only contain lowercase letters, numbers, and hyphens"

    # URL validation
    URL_INVALID = "Invalid URL format"
    URL_TOO_SHORT = "URL must be at least 10 characters"
    URL_TOO_LONG = "URL must not exceed 2000 characters"

    # Description validation
    DESCRIPTION_TOO_SHORT = "Description must be at least 10 characters"
    DESCRIPTION_TOO_LONG = "Description must not exceed 500 characters"


class InfoMessages:
    """Informational messages (non-error)."""

    # Password reset
    PASSWORD_RESET_EMAIL_SENT = "If an admin account exists, a password reset email has been sent"

    # Account status
    ACCOUNT_LOCKED_UNTIL = "Account locked until {time}"
    PASSWORD_RESET_SENT = "Password reset instructions sent to your email"


# Helper functions for common message patterns
def format_count_message(count: int, singular: str, plural: str) -> str:
    """Format a message with proper singular/plural."""
    return f"{count} {singular if count == 1 else plural}"


def format_field_required(field: str) -> str:
    """Format a field required message."""
    return ErrorMessages.FIELD_REQUIRED.format(field=field)


def format_domain_not_found(domain: str) -> str:
    """Format a domain not found message."""
    return ErrorMessages.DOMAIN_NOT_FOUND.format(domain=domain)
