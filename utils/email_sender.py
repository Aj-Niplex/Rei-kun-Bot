# Python 3.13 | Email utility for error reporting
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
from zoneinfo import ZoneInfo
from utils.config_loader import load_env
from core.ownership import FOUNDER_EMAIL
from core.rate_limiter import is_rate_limited, record_email_send

# 🔒 SECURITY: Import secure loader for encrypted credentials
from core.security import load_secure_env

# Load email config (SMTP_PASSWORD will be auto-decrypted if encrypted)
env = load_env()
SMTP_HOST = env.get("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(env.get("SMTP_PORT", "587"))
SMTP_EMAIL = env.get("SMTP_EMAIL", "")
SMTP_PASSWORD = load_secure_env("SMTP_PASSWORD", "")  # 🔒 Auto-decrypt
SENDGRID_API_KEY = load_secure_env("SENDGRID_API_KEY", "")  # 🔒 Auto-decrypt

# 🔒 HARDCODED: Error reports ALWAYS go to founder's email
# Even if .env is changed, this ensures the original creator gets notifications
ERROR_REPORT_EMAIL = FOUNDER_EMAIL  # Locked to aj.jin.japan.2006@gmail.com

# 🚦 RATE LIMITING: Prevent email spam abuse

async def send_error_email(
    subject: str,
    simple_body: str,
    detailed_html: str,
    recipient: str = None
) -> tuple[bool, str]:
    """
    Send error report email with simple text + detailed HTML attachment.
    
    SECURITY:
    - Rate limited (5/min, 20/hr, 50/day) to prevent spam
    - SMTP password auto-decrypted from .env
    - Recipient hardcoded to founder email
    
    Args:
        subject: Email subject
        simple_body: Short summary for email body
        detailed_html: Full diagnostic as HTML attachment
        recipient: Email address (defaults to ERROR_REPORT_EMAIL)
    
    Returns:
        (success: bool, message: str)
    """
    recipient = recipient or ERROR_REPORT_EMAIL
    
    if not recipient:
        return False, "No recipient email configured"
    
    # 🚦 CHECK RATE LIMIT
    is_blocked, reason = is_rate_limited()
    if is_blocked:
        print(f"[EMAIL] {reason}")
        return False, reason
    
    # Try SendGrid first (if API key exists)
    if SENDGRID_API_KEY:
        try:
            return await _send_via_sendgrid(subject, simple_body, detailed_html, recipient)
        except Exception as e:
            print(f"[EMAIL] SendGrid failed: {e}, falling back to SMTP")
    
    # Fall back to SMTP
    return await _send_via_smtp(subject, simple_body, detailed_html, recipient)


async def _send_via_smtp(subject: str, simple_body: str, detailed_html: str, recipient: str) -> tuple[bool, str]:
    """Send email via SMTP with HTML attachment"""
    if not SMTP_EMAIL or not SMTP_PASSWORD:
        return False, "SMTP credentials not configured in .env"
    
    try:
        msg = MIMEMultipart("mixed")
        msg["From"] = SMTP_EMAIL
        msg["To"] = recipient
        msg["Subject"] = subject
        
        # Add timestamp
        ist_time = datetime.now(ZoneInfo("Asia/Kolkata")).strftime("%Y-%m-%d %I:%M:%S %p IST")
        
        # Simple text body
        text_body = f"{simple_body}\n\n📎 See attached HTML file for full diagnostic details.\n\nSent at: {ist_time}"
        msg.attach(MIMEText(text_body, "plain"))
        
        # Attach detailed HTML report
        html_attachment = MIMEBase("text", "html")
        html_attachment.set_payload(detailed_html.encode('utf-8'))
        encoders.encode_base64(html_attachment)
        html_attachment.add_header(
            'Content-Disposition',
            'attachment',
            filename='error_report.html'
        )
        msg.attach(html_attachment)
        
        # Connect and send
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_EMAIL, SMTP_PASSWORD)
            server.send_message(msg)
        
        # 🚦 RECORD SEND (for rate limiting)
        record_email_send()
        
        return True, f"Email sent successfully to {recipient}"
    
    except smtplib.SMTPAuthenticationError:
        return False, "SMTP authentication failed. Check email/password in .env"
    except smtplib.SMTPException as e:
        return False, f"SMTP error: {str(e)}"
    except Exception as e:
        return False, f"Email send failed: {str(e)}"


async def _send_via_sendgrid(subject: str, simple_body: str, detailed_html: str, recipient: str) -> tuple[bool, str]:
    """Send email via SendGrid API with HTML attachment"""
    try:
        from utils.concurrency import get_session
        import base64
        
        url = "https://api.sendgrid.com/v3/mail/send"
        headers = {
            "Authorization": f"Bearer {SENDGRID_API_KEY}",
            "Content-Type": "application/json"
        }
        
        # Encode HTML as base64 for attachment
        html_b64 = base64.b64encode(detailed_html.encode('utf-8')).decode()
        
        payload = {
            "personalizations": [{"to": [{"email": recipient}]}],
            "from": {"email": SMTP_EMAIL or "noreply@rei-kun.bot"},
            "subject": subject,
            "content": [{"type": "text/plain", "value": simple_body}],
            "attachments": [{
                "content": html_b64,
                "filename": "error_report.html",
                "type": "text/html",
                "disposition": "attachment"
            }]
        }
        
        session = get_session()
        async with session.post(url, headers=headers, json=payload) as resp:
            if resp.status == 202:
                return True, f"Email sent via SendGrid to {recipient}"
            else:
                text = await resp.text()
                return False, f"SendGrid error {resp.status}: {text}"
    
    except Exception as e:
        return False, f"SendGrid failed: {str(e)}"


def format_error_report_html(
    error_type: str,
    error_message: str,
    command: str,
    user: str,
    guild: str,
    channel: str,
    file_path: str,
    traceback: str,
    ai_explanation: str,
    temp_fix: str,
    ai_prompt: str
) -> str:
    """Format error report as beautiful HTML with Tailwind CSS + animations"""
    
    # Get current timestamp
    ist_time = datetime.now(ZoneInfo("Asia/Kolkata")).strftime("%Y-%m-%d %I:%M:%S %p IST")
    
    html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🚨 Rei-kun Error Report</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        @keyframes slideDown {{
            from {{ opacity: 0; transform: translateY(-20px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        @keyframes pulse {{
            0%, 100% {{ opacity: 1; }}
            50% {{ opacity: 0.7; }}
        }}
        @keyframes fadeIn {{
            from {{ opacity: 0; }}
            to {{ opacity: 1; }}
        }}
        .animate-slideDown {{ animation: slideDown 0.5s ease-out; }}
        .animate-pulse-slow {{ animation: pulse 2s ease-in-out infinite; }}
        .animate-fadeIn {{ animation: fadeIn 0.8s ease-in; }}
        .code-block {{
            background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
            border-radius: 12px;
            padding: 1.5rem;
            overflow-x: auto;
            font-family: 'Courier New', monospace;
            box-shadow: 0 8px 24px rgba(0,0,0,0.2);
        }}
        .gradient-border {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 2px;
            border-radius: 12px;
        }}
        .gradient-bg {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }}
        .section-card {{
            transition: all 0.3s ease;
        }}
        .section-card:hover {{
            transform: translateY(-4px);
            box-shadow: 0 12px 32px rgba(0,0,0,0.15);
        }}
        .copy-btn {{
            transition: all 0.2s ease;
            cursor: pointer;
        }}
        .copy-btn:hover {{
            transform: scale(1.05);
            background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        }}
    </style>
</head>
<body class="bg-gradient-to-br from-slate-50 to-slate-100 min-h-screen p-8">
    
    <!-- Main Container -->
    <div class="max-w-5xl mx-auto">
        
        <!-- Header -->
        <div class="gradient-bg rounded-2xl shadow-2xl p-8 mb-8 animate-slideDown">
            <div class="flex items-center justify-between">
                <div>
                    <h1 class="text-4xl font-bold text-white mb-2">🚨 Error Report</h1>
                    <p class="text-purple-100 text-lg">Automated diagnostic by Rei-kun AI</p>
                </div>
                <div class="text-right">
                    <div class="bg-white/20 backdrop-blur-sm rounded-lg px-4 py-2">
                        <p class="text-purple-100 text-sm">Timestamp</p>
                        <p class="text-white font-semibold">{ist_time}</p>
                    </div>
                </div>
            </div>
        </div>

        <!-- Error Details Card -->
        <div class="bg-white rounded-2xl shadow-xl p-6 mb-6 section-card animate-fadeIn">
            <div class="flex items-center mb-4">
                <div class="w-12 h-12 bg-red-100 rounded-full flex items-center justify-center mr-4">
                    <span class="text-2xl">⚠️</span>
                </div>
                <h2 class="text-2xl font-bold text-slate-800">Error Details</h2>
            </div>
            <div class="grid grid-cols-2 gap-4">
                <div class="bg-red-50 rounded-lg p-4">
                    <p class="text-sm text-red-600 font-semibold mb-1">Error Type</p>
                    <p class="text-red-900 font-mono text-lg">{error_type}</p>
                </div>
                <div class="bg-orange-50 rounded-lg p-4">
                    <p class="text-sm text-orange-600 font-semibold mb-1">Command</p>
                    <p class="text-orange-900 font-mono text-lg">{command}</p>
                </div>
            </div>
            <div class="mt-4 bg-slate-50 rounded-lg p-4">
                <p class="text-sm text-slate-600 font-semibold mb-2">Error Message</p>
                <p class="text-slate-900 font-mono">{error_message}</p>
            </div>
        </div>

        <!-- Context Info -->
        <div class="bg-white rounded-2xl shadow-xl p-6 mb-6 section-card animate-fadeIn" style="animation-delay: 0.1s;">
            <div class="flex items-center mb-4">
                <div class="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mr-4">
                    <span class="text-2xl">👤</span>
                </div>
                <h2 class="text-2xl font-bold text-slate-800">Context Information</h2>
            </div>
            <div class="grid grid-cols-3 gap-4">
                <div class="bg-blue-50 rounded-lg p-4">
                    <p class="text-sm text-blue-600 font-semibold mb-1">User</p>
                    <p class="text-blue-900 font-mono">{user}</p>
                </div>
                <div class="bg-indigo-50 rounded-lg p-4">
                    <p class="text-sm text-indigo-600 font-semibold mb-1">Server</p>
                    <p class="text-indigo-900 font-mono truncate">{guild}</p>
                </div>
                <div class="bg-purple-50 rounded-lg p-4">
                    <p class="text-sm text-purple-600 font-semibold mb-1">Channel</p>
                    <p class="text-purple-900 font-mono truncate">{channel}</p>
                </div>
            </div>
            <div class="mt-4 bg-slate-50 rounded-lg p-4">
                <p class="text-sm text-slate-600 font-semibold mb-2">📁 File Location</p>
                <p class="text-slate-900 font-mono text-sm break-all">{file_path}</p>
            </div>
        </div>

        <!-- AI Explanation Section -->
        <div class="gradient-border mb-6 animate-fadeIn" style="animation-delay: 0.2s;">
            <div class="bg-white rounded-xl p-6">
                <div class="flex items-center mb-4">
                    <div class="w-12 h-12 bg-gradient-to-br from-purple-500 to-indigo-600 rounded-full flex items-center justify-center mr-4 animate-pulse-slow">
                        <span class="text-2xl">🤖</span>
                    </div>
                    <h2 class="text-2xl font-bold bg-gradient-to-r from-purple-600 to-indigo-600 bg-clip-text text-transparent">
                        AI Explanation
                    </h2>
                </div>
                <div class="prose max-w-none text-slate-700 leading-relaxed">
                    {ai_explanation}
                </div>
            </div>
        </div>

        <!-- Temporary Fix Section -->
        <div class="bg-white rounded-2xl shadow-xl p-6 mb-6 section-card animate-fadeIn" style="animation-delay: 0.3s;">
            <div class="flex items-center mb-4">
                <div class="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mr-4">
                    <span class="text-2xl">🔧</span>
                </div>
                <h2 class="text-2xl font-bold text-slate-800">Temporary Fix</h2>
            </div>
            <div class="bg-green-50 rounded-lg p-4 border-l-4 border-green-500">
                <div class="prose max-w-none text-slate-700">
                    {temp_fix}
                </div>
            </div>
        </div>

        <!-- AI Auto-Fix Prompt Section -->
        <div class="bg-white rounded-2xl shadow-xl p-6 mb-6 section-card animate-fadeIn" style="animation-delay: 0.4s;">
            <div class="flex items-center justify-between mb-4">
                <div class="flex items-center">
                    <div class="w-12 h-12 bg-yellow-100 rounded-full flex items-center justify-center mr-4">
                        <span class="text-2xl">✨</span>
                    </div>
                    <h2 class="text-2xl font-bold text-slate-800">AI Coder Prompt</h2>
                </div>
                <button onclick="copyPrompt()" class="copy-btn bg-gradient-to-r from-green-500 to-emerald-600 text-white px-6 py-2 rounded-lg font-semibold shadow-lg">
                    📋 Copy Prompt
                </button>
            </div>
            <p class="text-slate-600 mb-4 text-sm">
                Copy this prompt and paste it to your AI coder (ChatGPT, Claude, etc.) along with the file causing the error.
            </p>
            <div class="code-block">
                <pre id="aiPrompt" class="text-green-400 text-sm leading-relaxed whitespace-pre-wrap">{ai_prompt}</pre>
            </div>
        </div>

        <!-- Stack Trace Section -->
        <div class="bg-white rounded-2xl shadow-xl p-6 mb-6 section-card animate-fadeIn" style="animation-delay: 0.5s;">
            <div class="flex items-center mb-4">
                <div class="w-12 h-12 bg-slate-100 rounded-full flex items-center justify-center mr-4">
                    <span class="text-2xl">📝</span>
                </div>
                <h2 class="text-2xl font-bold text-slate-800">Stack Trace</h2>
            </div>
            <div class="code-block">
                <pre class="text-red-400 text-sm leading-relaxed whitespace-pre-wrap">{traceback}</pre>
            </div>
        </div>

        <!-- Footer -->
        <div class="text-center py-8 border-t-2 border-slate-200 animate-fadeIn" style="animation-delay: 0.6s;">
            <p class="text-slate-500 text-sm mb-2">
                🤖 This is an automated error report from <span class="font-semibold text-purple-600">Rei-kun Bot</span>
            </p>
            <p class="text-slate-400 text-xs">
                To disable error emails, set <code class="bg-slate-100 px-2 py-1 rounded text-slate-700">ERROR_HANDLER_ENABLED=false</code> in .env
            </p>
        </div>

    </div>

    <script>
        function copyPrompt() {{
            const promptText = document.getElementById('aiPrompt').textContent;
            navigator.clipboard.writeText(promptText).then(() => {{
                const btn = event.target;
                const originalText = btn.innerHTML;
                btn.innerHTML = '✅ Copied!';
                btn.classList.add('bg-green-600');
                setTimeout(() => {{
                    btn.innerHTML = originalText;
                    btn.classList.remove('bg-green-600');
                }}, 2000);
            }});
        }}
    </script>

</body>
</html>
"""
    return html
