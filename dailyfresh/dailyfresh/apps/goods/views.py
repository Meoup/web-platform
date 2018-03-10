from django.shortcuts import render
from django.views.generic import View

# Create your views here.


# / 主页
class IndexView(View):
    """显示主页"""
    def get(self, request):

        return render(request, "index.html")

