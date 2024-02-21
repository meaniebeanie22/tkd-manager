from dashboard.models import Style
from django.shortcuts import get_object_or_404

def style_context(request):
    style = get_object_or_404(Style, pk=request.session.get('pk', 1))
    styles = Style.objects.all()
    return {'style': style, 
            'styles': styles}