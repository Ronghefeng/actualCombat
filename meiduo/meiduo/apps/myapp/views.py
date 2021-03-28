from django.shortcuts import render

# Create your views here.
from rest_framework.generics import ListAPIView

from . import models



class ArticleView(ListAPIView):

    queryset = models.Article
    serializer_class = None
