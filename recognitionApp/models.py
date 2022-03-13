from django.db import models

# Create your models here.

# This class stores the name of the person and the number of faces they have
class Person(models.Model):
    name_of_person = models.CharField(max_length = 100)
    count = models.IntegerField()

    def increase_count(self):
        self.count += 1
        self.save()

# This class is used to collect the images from add.html. The images are downloaded into media/images
class Item(models.Model):
    name = models.TextField(max_length=150)
    image = models.ImageField(upload_to="images", null=True, blank=True)


 
