from pyexpat import model
from django.db import models

class contactform(models.Model):
    """
    @brief this is a form for users to send/contact the admin
    @details this form consists of 3 fields name which is of string type, email is of emailfield type and message of textfield of string type
    """
    name = models.CharField(max_length=50)
    email = models.EmailField()
    message = models.TextField()

