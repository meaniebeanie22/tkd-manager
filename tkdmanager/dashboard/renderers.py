from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
from requests import session, get, post
from xhtml2pdf import pisa
from sys import stderr
import os

def PDFResponse(template_src, filename, context_dict={}):
    result = render_to_pdf(template_src, context_dict)
    response = HttpResponse(result.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response

"""
def render_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html  = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
    if pdf.err:
        return None
    return result
"""

def base_render_to_pdf(template_src, context_dict):
    template = get_template(template_src)
    html  = template.render(context_dict)
    result = BytesIO()
    pisa_status = pisa.CreatePDF(html.encode('UTF-8'), dest=result, encoding='UTF-8')
    if pisa_status.err:
       return None
    return result

def render_to_pdf(template_src, context_dict):
    template = get_template(template_src)
    html  = template.render(context_dict)

    s = session()
    health = s.get(os.environ.get('WEASYPRINT_API_DOMAIN') + '/api/v1.0/health')
    if not(health):
        print('Weasyprint API did not return HEALTH, using xhtml builtin instead.', file=stderr)
        return base_render_to_pdf(template_src, context_dict)
    s.headers['X_API_KEY'] = os.environ.get('WEASYPRINT_API_KEY')
    response = s.post(os.environ.get('WEASYPRINT_API_DOMAIN') + '/api/v1.0/print', {'html': html})
    pdf = BytesIO(response.content)
    return pdf