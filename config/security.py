import re

from django.utils.deprecation import MiddlewareMixin

PROMPT_INJECTION_PATTERNS = [
    r'ignore\s+previous\s+instructions',
    r'ignore\s+all\s+previous',
    r'system\s*:',
    r'assistant\s*:',
    r'developer\s*:',
    r'prompt\s*inject',
    r'you\s+are\s+chatgpt',
]


def sanitize_untrusted_text(value, max_length=500):
    if not value:
        return ''

    cleaned = ''.join(ch for ch in str(value) if ch.isprintable() or ch in '\n\r\t')
    cleaned = cleaned.strip()
    for pattern in PROMPT_INJECTION_PATTERNS:
        cleaned = re.sub(pattern, '[filtered]', cleaned, flags=re.IGNORECASE)
    return cleaned[:max_length]


class SecurityHeadersMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        response['X-Content-Type-Options'] = 'nosniff'
        response['Referrer-Policy'] = 'same-origin'
        response['X-Frame-Options'] = 'DENY'
        response['Permissions-Policy'] = 'camera=(), microphone=(), geolocation=()'
        response['Content-Security-Policy'] = (
            "default-src 'self'; "
            "img-src 'self' data: https: https://maps.gstatic.com https://maps.googleapis.com; "
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://fonts.googleapis.com https://fonts.gstatic.com; "
            "font-src 'self' https://cdn.jsdelivr.net https://fonts.gstatic.com data:; "
            "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://js.stripe.com https://maps.googleapis.com; "
            "connect-src 'self' https://api.stripe.com https://maps.googleapis.com https://maps.gstatic.com; "
            "frame-src https://js.stripe.com https://www.google.com;"
        )
        return response
