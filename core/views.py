from rest_framework.decorators import api_view
from django.http import HttpResponse


@api_view(["GET"])
def homepage(request):
    return HttpResponse("<h1>Server Up and Running</h1><br>")
