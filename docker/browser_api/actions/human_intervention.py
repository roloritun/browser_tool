"""
Human intervention actions for browser automation.
This module handles various types of human intervention scenarios.
"""
import base64
import logging
import os
import uuid
from datetime import datetime
from typing import Dict

from browser_api.core.browser_automation import BrowserAutomation
from browser_api.models.intervention_models import (
    InterventionType, InterventionStatus, InterventionRequest,
    InterventionRequestAction, InterventionCompleteAction, InterventionCancelAction,
    InterventionStatusAction, AutoDetectAction
)
from browser_api.models.result_models import BrowserActionResult

class HumanInterventionActions:
    """Actions for handling human intervention in browser automation"""
    
    _active_interventions: Dict[str, InterventionRequest] = {}
    _logger = logging.getLogger("human_intervention")
    
    @classmethod
    async def request_intervention(cls, browser: BrowserAutomation, action: InterventionRequestAction) -> BrowserActionResult:
        """Request human intervention and wait for completion"""
        try:
            # Generate unique intervention ID
            intervention_id = str(uuid.uuid4())
            
            # Get current page info
            page = await browser.get_current_page()
            current_url = page.url
            
            # Take screenshot if requested
            screenshot_path = None
            screenshot_base64 = None
            if action.take_screenshot:
                screenshot_path = os.path.join(browser.screenshot_dir, f"intervention_{intervention_id}.png")
                await page.screenshot(path=screenshot_path)
                
                # Convert to base64 for API response
                with open(screenshot_path, "rb") as img_file:
                    screenshot_base64 = base64.b64encode(img_file.read()).decode()
            
            # Create intervention request
            intervention = InterventionRequest(
                id=intervention_id,
                intervention_type=action.intervention_type,
                message=action.message,
                instructions=action.instructions,
                url=current_url,
                screenshot_path=screenshot_path,
                context=action.context,
                timeout_seconds=action.timeout_seconds,
                auto_detected=action.auto_detect
            )
            
            # Store intervention
            cls._active_interventions[intervention_id] = intervention
            
            # Display intervention UI on the page
            await cls._display_intervention_ui(page, intervention)
            
            cls._logger.info(f"🚨 Human intervention requested: {action.intervention_type.value}")
            cls._logger.info(f"Message: {action.message}")
            cls._logger.info(f"URL: {current_url}")
            cls._logger.info(f"Intervention ID: {intervention_id}")
            
            # Return immediate response with intervention details
            return BrowserActionResult(
                success=True,
                message=f"Human intervention requested: {action.intervention_type.value}",
                content={
                    "intervention_id": intervention_id,
                    "status": InterventionStatus.PENDING,
                    "timeout_seconds": action.timeout_seconds,
                    "screenshot_base64": screenshot_base64,
                    "url": current_url
                }
            )
            
        except Exception as e:
            cls._logger.error(f"Error requesting intervention: {e}")
            return BrowserActionResult(
                success=False,
                message="Failed to request intervention",
                error=str(e)
            )
    
    @classmethod
    async def complete_intervention(cls, browser: BrowserAutomation, action: InterventionCompleteAction) -> BrowserActionResult:
        """Mark an intervention as complete"""
        try:
            intervention = cls._active_interventions.get(action.intervention_id)
            if not intervention:
                return BrowserActionResult(
                    success=False,
                    message="Intervention not found",
                    error=f"No intervention found with ID: {action.intervention_id}"
                )
            
            # Update intervention status
            intervention.status = InterventionStatus.COMPLETED if action.success else InterventionStatus.FAILED
            intervention.completed_at = datetime.now()
            intervention.user_message = action.user_message
            
            # Remove intervention UI from page
            page = await browser.get_current_page()
            await cls._remove_intervention_ui(page)
            
            # Clean up from active interventions
            del cls._active_interventions[action.intervention_id]
            
            cls._logger.info(f"✅ Intervention {action.intervention_id} completed successfully")
            
            return BrowserActionResult(
                success=True,
                message="Intervention completed successfully",
                content={
                    "intervention_id": action.intervention_id,
                    "status": intervention.status,
                    "user_message": action.user_message
                }
            )
            
        except Exception as e:
            cls._logger.error(f"Error completing intervention: {e}")
            return BrowserActionResult(
                success=False,
                message="Failed to complete intervention",
                error=str(e)
            )
    
    @classmethod
    async def cancel_intervention(cls, browser: BrowserAutomation, action: InterventionCancelAction) -> BrowserActionResult:
        """Cancel an intervention request"""
        try:
            intervention = cls._active_interventions.get(action.intervention_id)
            if not intervention:
                return BrowserActionResult(
                    success=False,
                    message="Intervention not found",
                    error=f"No intervention found with ID: {action.intervention_id}"
                )
            
            # Update intervention status
            intervention.status = InterventionStatus.CANCELLED
            intervention.completed_at = datetime.now()
            
            # Remove intervention UI from page
            page = await browser.get_current_page()
            await cls._remove_intervention_ui(page)
            
            # Clean up from active interventions
            del cls._active_interventions[action.intervention_id]
            
            cls._logger.info(f"❌ Intervention {action.intervention_id} cancelled")
            
            return BrowserActionResult(
                success=True,
                message="Intervention cancelled",
                content={
                    "intervention_id": action.intervention_id,
                    "status": intervention.status,
                    "reason": action.reason
                }
            )
            
        except Exception as e:
            cls._logger.error(f"Error cancelling intervention: {e}")
            return BrowserActionResult(
                success=False,
                message="Failed to cancel intervention",
                error=str(e)
            )
    
    @classmethod
    async def get_intervention_status(cls, browser: BrowserAutomation, action: InterventionStatusAction) -> BrowserActionResult:
        """Get the status of an intervention"""
        try:
            # If no intervention_id provided, get the latest active intervention
            if action.intervention_id is None:
                if not cls._active_interventions:
                    return BrowserActionResult(
                        success=False,
                        message="No active interventions found",
                        error="No intervention ID provided and no active interventions exist"
                    )
                
                # Get the most recent intervention (latest created_at)
                latest_intervention = max(
                    cls._active_interventions.values(),
                    key=lambda x: x.created_at
                )
                intervention = latest_intervention
                intervention_id = latest_intervention.id
            else:
                intervention = cls._active_interventions.get(action.intervention_id)
                intervention_id = action.intervention_id
                
                if not intervention:
                    return BrowserActionResult(
                        success=False,
                        message="Intervention not found",
                        error=f"No intervention found with ID: {action.intervention_id}"
                    )
            
            # Check for timeout
            if intervention.status == InterventionStatus.PENDING:
                elapsed = (datetime.now() - intervention.created_at).total_seconds()
                if elapsed > intervention.timeout_seconds:
                    intervention.status = InterventionStatus.TIMEOUT
                    intervention.completed_at = datetime.now()
                    
                    # Remove intervention UI from page
                    page = await browser.get_current_page()
                    await cls._remove_intervention_ui(page)
                    
                    # Clean up from active interventions
                    del cls._active_interventions[intervention_id]
                    
                    cls._logger.warning(f"⏰ Intervention {intervention_id} timed out")
            
            time_remaining = None
            if intervention.status == InterventionStatus.PENDING:
                elapsed = (datetime.now() - intervention.created_at).total_seconds()
                time_remaining = max(0, intervention.timeout_seconds - elapsed)
            
            return BrowserActionResult(
                success=True,
                message="Intervention status retrieved",
                content={
                    "intervention_id": intervention_id,
                    "status": intervention.status,
                    "message": intervention.message,
                    "url": intervention.url,
                    "time_remaining": time_remaining,
                    "created_at": intervention.created_at.isoformat(),
                    "completed_at": intervention.completed_at.isoformat() if intervention.completed_at else None
                }
            )
            
        except Exception as e:
            cls._logger.error(f"Error getting intervention status: {e}")
            return BrowserActionResult(
                success=False,
                message="Failed to get intervention status",
                error=str(e)
            )
    
    @classmethod
    async def auto_detect_intervention_needed(cls, browser: BrowserAutomation, action: AutoDetectAction) -> BrowserActionResult:
        """Automatically detect if human intervention is needed"""
        try:
            page = await browser.get_current_page()
            detected_types = []
            recommendations = []
            confidence_scores = {}
            page_indicators = {}
            
            # Check for CAPTCHA
            if action.check_captcha:
                captcha_found, confidence = await cls._detect_captcha(page)
                if captcha_found:
                    detected_types.append(InterventionType.CAPTCHA)
                    recommendations.append("Please solve the CAPTCHA verification")
                    confidence_scores[InterventionType.CAPTCHA] = confidence
            
            # Check for login requirements
            if action.check_login:
                login_found, confidence = await cls._detect_login_required(page)
                if login_found:
                    detected_types.append(InterventionType.LOGIN_REQUIRED)
                    recommendations.append("Please complete the login process")
                    confidence_scores[InterventionType.LOGIN_REQUIRED] = confidence
            
            # Check for security checks
            if action.check_security:
                security_found, confidence = await cls._detect_security_check(page)
                if security_found:
                    detected_types.append(InterventionType.SECURITY_CHECK)
                    recommendations.append("Please complete the security verification")
                    confidence_scores[InterventionType.SECURITY_CHECK] = confidence
            
            # Check for anti-bot protection
            if action.check_anti_bot:
                antibot_found, confidence = await cls._detect_anti_bot_protection(page)
                if antibot_found:
                    detected_types.append(InterventionType.ANTI_BOT_PROTECTION)
                    recommendations.append("Please wait for anti-bot protection to complete")
                    confidence_scores[InterventionType.ANTI_BOT_PROTECTION] = confidence
            
            # Check for cookie consent
            if action.check_cookies:
                cookies_found, confidence = await cls._detect_cookie_consent(page)
                if cookies_found:
                    detected_types.append(InterventionType.COOKIES_CONSENT)
                    recommendations.append("Please accept or decline cookie consent")
                    confidence_scores[InterventionType.COOKIES_CONSENT] = confidence
            
            # Get page indicators
            page_indicators = {
                "url": page.url,
                "title": await page.title(),
                "has_password_field": bool(await page.query_selector('input[type="password"]')),
                "has_captcha_iframe": bool(await page.query_selector('iframe[src*="recaptcha"]')),
                "page_text_length": len(await page.text_content('body') or "")
            }
            
            intervention_needed = len(detected_types) > 0
            
            return BrowserActionResult(
                success=True,
                message=f"Auto-detection completed. Intervention needed: {intervention_needed}",
                content={
                    "intervention_needed": intervention_needed,
                    "detected_types": [t.value for t in detected_types],
                    "recommendations": recommendations,
                    "confidence_scores": {k.value: v for k, v in confidence_scores.items()},
                    "page_indicators": page_indicators
                }
            )
            
        except Exception as e:
            cls._logger.error(f"Error in auto-detection: {e}")
            return BrowserActionResult(
                success=False,
                message="Failed to auto-detect intervention needs",
                error=str(e)
            )
    
    @classmethod
    async def _display_intervention_ui(cls, page, intervention: InterventionRequest):
        """Display intervention UI on the page"""
        # Prepare instruction HTML if instructions exist
        instruction_html = f'<div style="font-size: 12px; margin-bottom: 15px; color: #ffdddd; font-style: italic;">{intervention.instructions}</div>' if intervention.instructions else ''
        
        # Create the JavaScript for the intervention UI
        ui_script = f"""
        // Remove existing intervention notice if any
        const existingNotice = document.getElementById('human-intervention-notice');
        if (existingNotice) existingNotice.remove();
        
        // Create intervention notice
        const notice = document.createElement('div');
        notice.id = 'human-intervention-notice';
        notice.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            background: linear-gradient(135deg, #ff4444, #cc0000);
            color: white;
            padding: 20px;
            text-align: center;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            font-size: 16px;
            font-weight: bold;
            z-index: 999999;
            box-shadow: 0 4px 20px rgba(0,0,0,0.3);
            border-bottom: 3px solid #990000;
        `;
        
        const typeEmojis = {{
            'captcha': '🔍',
            'login_required': '🔐',
            'security_check': '🛡️',
            'anti_bot_protection': '🤖',
            'cookies_consent': '🍪',
            'two_factor_auth': '📱',
            'age_verification': '🔞',
            'custom': '⚠️'
        }};
        
        const emoji = typeEmojis['{intervention.intervention_type.value}'] || '⚠️';
        const interventionType = '{intervention.intervention_type.value}'.replace('_', ' ').replace(/\\b\\w/g, l => l.toUpperCase());
        
        notice.innerHTML = 
            '<div style="margin-bottom: 10px;">' +
                '<span style="font-size: 24px;">' + emoji + '</span>' +
                '<span style="margin-left: 10px;">HUMAN INTERVENTION REQUIRED</span>' +
            '</div>' +
            '<div style="font-size: 18px; margin-bottom: 8px; color: #ffdddd;">' +
                interventionType +
            '</div>' +
            '<div style="font-size: 14px; margin-bottom: 15px; color: #ffeeee;">' +
                '{intervention.message}' +
            '</div>' +
            '{instruction_html}' +
            '<div style="display: flex; justify-content: center; gap: 15px; flex-wrap: wrap;">' +
                '<button id="complete-intervention-btn" style="' +
                    'padding: 10px 25px;' +
                    'background: #28a745;' +
                    'color: white;' +
                    'border: none;' +
                    'border-radius: 6px;' +
                    'cursor: pointer;' +
                    'font-size: 14px;' +
                    'font-weight: bold;' +
                    'box-shadow: 0 2px 8px rgba(0,0,0,0.2);' +
                    'transition: all 0.2s;' +
                '" onmouseover="this.style.background=\\'#218838\\'" ' +
                   'onmouseout="this.style.background=\\'#28a745\\'">' +
                    '✅ Task Complete' +
                '</button>' +
                '<button id="cancel-intervention-btn" style="' +
                    'padding: 10px 25px;' +
                    'background: #dc3545;' +
                    'color: white;' +
                    'border: none;' +
                    'border-radius: 6px;' +
                    'cursor: pointer;' +
                    'font-size: 14px;' +
                    'font-weight: bold;' +
                    'box-shadow: 0 2px 8px rgba(0,0,0,0.2);' +
                    'transition: all 0.2s;' +
                '" onmouseover="this.style.background=\\'#c82333\\'" ' +
                   'onmouseout="this.style.background=\\'#dc3545\\'">' +
                    '❌ Cancel' +
                '</button>' +
            '</div>' +
            '<div style="font-size: 11px; margin-top: 10px; color: #ffcccc;">' +
                'Intervention ID: {intervention.id}' +
            '</div>';
        
        document.body.insertBefore(notice, document.body.firstChild);
        
        // Add click handlers
        document.getElementById('complete-intervention-btn').onclick = function() {{
            window.interventionCompleted = '{intervention.id}';
            notice.style.background = 'linear-gradient(135deg, #28a745, #1e7e34)';
            notice.innerHTML = '<div style="font-size: 18px;">✅ Intervention completed! Resuming automation...</div>';
            
            // Make an API call to notify the server
            fetch('/automation/complete_intervention', {{
                method: 'POST',
                headers: {{ 'Content-Type': 'application/json' }},
                body: JSON.stringify({{ intervention_id: '{intervention.id}', success: true }})
            }}).catch(err => console.error('Error completing intervention:', err));
            
            setTimeout(() => notice.remove(), 3000);
        }};
        
        document.getElementById('cancel-intervention-btn').onclick = function() {{
            window.interventionCancelled = '{intervention.id}';
            notice.style.background = 'linear-gradient(135deg, #dc3545, #bd2130)';
            notice.innerHTML = '<div style="font-size: 18px;">❌ Intervention cancelled!</div>';
            
            // Make an API call to notify the server
            fetch('/automation/cancel_intervention', {{
                method: 'POST',
                headers: {{ 'Content-Type': 'application/json' }},
                body: JSON.stringify({{ intervention_id: '{intervention.id}', reason: 'User cancelled' }})
            }}).catch(err => console.error('Error cancelling intervention:', err));
            
            setTimeout(() => notice.remove(), 3000);
        }};
        """
        
        await page.evaluate(ui_script)
    
    @classmethod
    async def _remove_intervention_ui(cls, page):
        """Remove intervention UI from the page"""
        remove_script = """
        const notice = document.getElementById('human-intervention-notice');
        if (notice) notice.remove();
        """
        try:
            await page.evaluate(remove_script)
        except Exception:
            pass  # Ignore errors if page is not available
    
    @classmethod
    async def _detect_captcha(cls, page) -> tuple[bool, float]:
        """Detect CAPTCHA on the page"""
        try:
            captcha_selectors = [
                'iframe[src*="recaptcha"]',
                'iframe[src*="hcaptcha"]', 
                '.g-recaptcha',
                '#recaptcha',
                '[data-callback*="recaptcha"]',
                '.h-captcha',
                '.captcha'
            ]
            
            for selector in captcha_selectors:
                if await page.query_selector(selector):
                    return True, 0.9
            
            # Check for text indicators
            page_text = await page.text_content('body') or ""
            captcha_keywords = ["captcha", "verify you're human", "prove you're not a robot"]
            
            for keyword in captcha_keywords:
                if keyword.lower() in page_text.lower():
                    return True, 0.7
            
            return False, 0.0
            
        except Exception:
            return False, 0.0
    
    @classmethod
    async def _detect_login_required(cls, page) -> tuple[bool, float]:
        """Detect if login is required"""
        try:
            login_selectors = [
                'input[type="password"]',
                'button:has-text("Sign in")',
                'button:has-text("Log in")',
                'a:has-text("Login")',
                'form[action*="login"]',
                'form[action*="signin"]'
            ]
            
            for selector in login_selectors:
                if await page.query_selector(selector):
                    return True, 0.8
            
            # Check for text indicators
            page_text = await page.text_content('body') or ""
            login_keywords = ["sign in", "log in", "login required", "authentication required"]
            
            for keyword in login_keywords:
                if keyword.lower() in page_text.lower():
                    return True, 0.6
            
            return False, 0.0
            
        except Exception:
            return False, 0.0
    
    @classmethod
    async def _detect_security_check(cls, page) -> tuple[bool, float]:
        """Detect security verification"""
        try:
            page_text = await page.text_content('body') or ""
            security_keywords = [
                "verify your identity", "security check", "unusual activity",
                "verify it's you", "account verification", "suspicious activity",
                "additional verification", "confirm your identity"
            ]
            
            for keyword in security_keywords:
                if keyword.lower() in page_text.lower():
                    return True, 0.8
            
            return False, 0.0
            
        except Exception:
            return False, 0.0
    
    @classmethod
    async def _detect_anti_bot_protection(cls, page) -> tuple[bool, float]:
        """Detect anti-bot protection"""
        try:
            # Check for Cloudflare and similar services
            antibot_selectors = [
                'div[class*="cf-browser-verification"]',
                'div[class*="cloudflare"]',
                'div:has-text("Checking your browser")',
                'div:has-text("Please wait while we verify")',
                'div:has-text("DDoS protection")'
            ]
            
            for selector in antibot_selectors:
                if await page.query_selector(selector):
                    return True, 0.9
            
            page_text = await page.text_content('body') or ""
            antibot_keywords = [
                "checking your browser", "ddos protection", "cloudflare", 
                "please wait while we verify", "bot protection"
            ]
            
            for keyword in antibot_keywords:
                if keyword.lower() in page_text.lower():
                    return True, 0.7
            
            return False, 0.0
            
        except Exception:
            return False, 0.0
    
    @classmethod
    async def _detect_cookie_consent(cls, page) -> tuple[bool, float]:
        """Detect cookie consent dialogs"""
        try:
            cookie_selectors = [
                'div:has-text("cookie")',
                'div:has-text("Accept")',
                'button:has-text("Accept")',
                'div[class*="cookie"]',
                'div[class*="consent"]',
                'div[id*="cookie"]'
            ]
            
            for selector in cookie_selectors:
                element = await page.query_selector(selector)
                if element:
                    text = await element.text_content() or ""
                    if "cookie" in text.lower() or "consent" in text.lower():
                        return True, 0.8
            
            return False, 0.0
            
        except Exception:
            return False, 0.0
