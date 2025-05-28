"""
Human intervention model definitions for browser automation.
These models represent different types of human intervention requests and responses.
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from enum import Enum
from datetime import datetime

class InterventionType(str, Enum):
    """Types of human intervention scenarios"""
    CAPTCHA = "captcha"
    LOGIN_REQUIRED = "login_required"
    SECURITY_CHECK = "security_check"
    COMPLEX_DATA_ENTRY = "complex_data_entry"
    ANTI_BOT_PROTECTION = "anti_bot_protection"
    TWO_FACTOR_AUTH = "two_factor_auth"
    COOKIES_CONSENT = "cookies_consent"
    AGE_VERIFICATION = "age_verification"
    CUSTOM = "custom"

class InterventionStatus(str, Enum):
    """Status of an intervention request"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"
    FAILED = "failed"

class InterventionRequestAction(BaseModel):
    """Request for human intervention"""
    intervention_type: InterventionType
    message: str
    instructions: Optional[str] = Field(None, description="Specific instructions for the human")
    timeout_seconds: int = Field(300, description="How long to wait for human input")
    context: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional context")
    take_screenshot: bool = Field(True, description="Whether to take a screenshot")
    auto_detect: bool = Field(False, description="Whether this was auto-detected")

class InterventionCompleteAction(BaseModel):
    """Mark intervention as complete"""
    intervention_id: str
    user_message: Optional[str] = Field(None, description="Optional message from user")
    success: bool = Field(True, description="Whether intervention was successful")

class InterventionCancelAction(BaseModel):
    """Cancel an intervention request"""
    intervention_id: str
    reason: Optional[str] = Field(None, description="Reason for cancellation")

class InterventionStatusAction(BaseModel):
    """Get status of an intervention"""
    intervention_id: Optional[str] = Field(default=None, description="ID of the intervention to check. If not provided, checks the latest active intervention")

class AutoDetectAction(BaseModel):
    """Auto-detect if intervention is needed"""
    check_captcha: bool = Field(True, description="Check for CAPTCHA")
    check_login: bool = Field(True, description="Check for login requirements")
    check_security: bool = Field(True, description="Check for security checks")
    check_anti_bot: bool = Field(True, description="Check for anti-bot protection")
    check_cookies: bool = Field(True, description="Check for cookie consent")

class InterventionRequest(BaseModel):
    """Internal intervention request state"""
    id: str
    intervention_type: InterventionType
    message: str
    instructions: Optional[str] = None
    url: str
    screenshot_path: Optional[str] = None
    context: Dict[str, Any] = Field(default_factory=dict)
    timeout_seconds: int = 300
    status: InterventionStatus = InterventionStatus.PENDING
    created_at: datetime = Field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    user_message: Optional[str] = None
    auto_detected: bool = False

class InterventionResponse(BaseModel):
    """Response for intervention operations"""
    success: bool
    intervention_id: Optional[str] = None
    status: Optional[InterventionStatus] = None
    message: str
    url: Optional[str] = None
    screenshot_base64: Optional[str] = None
    time_remaining: Optional[int] = None
    context: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class DetectionResult(BaseModel):
    """Result of automatic intervention detection"""
    intervention_needed: bool
    detected_types: List[InterventionType] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    confidence_scores: Dict[InterventionType, float] = Field(default_factory=dict)
    page_indicators: Dict[str, Any] = Field(default_factory=dict)
