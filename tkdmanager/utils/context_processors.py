from dashboard.models import Style
from django.shortcuts import get_object_or_404

def style_context(request):
    print(f'Request Session Data from contextprocessor: {request.session}')
    style = get_object_or_404(Style, pk=request.session.get('style', 1))
    styles = Style.objects.all()
    return {'style': style, 
            'styles': styles}