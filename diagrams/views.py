from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Diagram

# عرض جميع المخططات
@login_required
def diagram_list(request):
    diagrams = Diagram.objects.all()
    return render(request, 'diagrams_list.html', {'diagrams': diagrams})

# عرض تفاصيل مخطط معين
@login_required
def diagram_detail(request, diagram_id):
    diagram = get_object_or_404(Diagram, id=diagram_id)
    return render(request, 'diagram_detail.html', {'diagram': diagram})
