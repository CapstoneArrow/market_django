from django.db import models

class MarketData(models.Model):
    공중화장실보유여부 = models.CharField(max_length=1) 
    사용가능상품권 = models.CharField(max_length=200) 
    소재지도로명주소 = models.CharField(max_length=200) 
    소재지지번주소 = models.CharField(max_length=200) 
    시장명 = models.CharField(max_length=200) 
    주차장보유여부 = models.CharField(max_length=1) 

    def __str__(self):
        return self.시장명
    

