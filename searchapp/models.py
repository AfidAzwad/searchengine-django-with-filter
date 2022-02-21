from django.db import models
from django.contrib.auth.models import User
from datetime import datetime
from django.db.models import Sum
from django.contrib.postgres.fields import ArrayField


class Search(models.Model):
    sid = models.AutoField(primary_key=True)
    keyword = models.CharField(max_length=50)
    searched_by = models.ForeignKey(to=User, db_column="Searched_by", on_delete=models.CASCADE, null=False)
    searched_at = models.DateTimeField(default=datetime.now, blank=True)
    counter = models.IntegerField()
    result = ArrayField(
        ArrayField(models.CharField(max_length=255,blank=True),
            size=8,),
        size=8,
    )
    @staticmethod
    def get_all_search():
        return Search.objects.all().order_by('-sid')
    def group_by_counter():
        return Search.objects.values('keyword').annotate(counter=Sum('counter')).order_by('-counter')
        
    def __str__(self):
        return str(self.keyword)