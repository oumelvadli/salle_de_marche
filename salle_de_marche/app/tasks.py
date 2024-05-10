from salle_de_marche.celery import app
from .models import Test



@app.task
def op(): 
    for i in range(5):
        Test.objects.create(
            nom=f"mariem {i}",
            prenom="mohamed"
           
        )


