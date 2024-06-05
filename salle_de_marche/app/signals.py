from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models import Sum
from django.utils import timezone
from .models import Operation
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
SEUIL_VENTE_MAXIMAL_PAR_CONTREPARTIE = 100000

@receiver(post_save, sender=Operation)
def check_operation_alert(sender, instance, **kwargs):
    if instance.direction == 'Sell':
        start_date = timezone.now() - timezone.timedelta(days=2)
        total_sold = Operation.objects.filter(
            date_operation__gte=start_date,
            direction='Sell',
            conterpartie=instance.conterpartie
        ).aggregate(total_sold=Sum('montant_vendu'))['total_sold'] or 0

        if total_sold >= max(SEUIL_VENTE_MAXIMAL_PAR_CONTREPARTIE, 0):
            alert_message = f"Alerte pour {instance.conterpartie} : Vous êtes sur le point d'atteindre votre limite maximale de vente. Le total vendu est de {total_sold}."

            # Envoi du message via le canal WebSocket
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                'alert_group',  # Nom du groupe WebSocket
                {
                    'type': 'alert_message',  # Nom de la méthode du consommateur
                    'message': alert_message  # Contenu du message
                }
            )
