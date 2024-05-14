# Exemple de consommateur WebSocket
from channels.generic.websocket import AsyncWebsocketConsumer
import json

class AlertConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Joindre un groupe
        await self.channel_layer.group_add(
            'alert_group',
            self.channel_name
        )
        await self.accept()
        
        # Logger un message de test au lieu de l'envoyer

    async def disconnect(self, close_code):
        # Quitter le groupe
        await self.channel_layer.group_discard(
            'alert_group',
            self.channel_name
        )

    async def alert_message(self, event):
        message = event['message']
        print(f"Message WebSocket reçu : {message}")  # Log pour vérifier le message reçu

        await self.send(text_data=json.dumps({
            'message': message
        }))

    async def receive(self, text_data):
        print(f"Texte reçu: {text_data}")  # Log pour afficher le texte reçu
        data = json.loads(text_data)
        print(f"Message JSON analysé: {data}")  # Log pour afficher le JSON analysé
        await self.send(text_data=json.dumps({
            'message': data.get('message', 'Message non reçu correctement')
        }))
        
    # async def receive(self, text_data):
    #     data = json.loads(text_data)
    #     await self.send(text_data=json.dumps({
    #         'message': data['message']
    #     }))


    
