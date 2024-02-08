from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
from requests import session
from sys import stderr
import os

def PDFResponse(template_src, filename, context_dict={}):
    result = render_to_pdf(template_src, context_dict)
    response = HttpResponse(result.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response

def render_to_pdf(template_src, context_dict):
    template = get_template(template_src)
    html  = template.render(context_dict)

    s = session()
    health = s.get(os.environ.get('WEASYPRINT_API_DOMAIN') + '/api/v1.0/health')
    if not(health):
        print('Weasyprint API did not return HEALTH, Something broken. Returning null', file=stderr)
        return None
    s.headers['X_API_KEY'] = os.environ.get('WEASYPRINT_API_KEY')
    response = s.post(os.environ.get('WEASYPRINT_API_DOMAIN') + '/api/v1.0/print', {'html': html})
    if response.status_code != 200:
        print(f'Weasyprint API did not return 200 on print, returning null.\nError Code: {response.status_code}\nReason: {response.reason}', file=stderr)
        return None
    pdf = BytesIO(response.content)
    return pdf