import spacy

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

nlp = spacy.load('en_core_web_sm')

def attempt_send_message(group, message):
    """
    Will try to send the specified message over the WebSocket associated with the specified group.
    If any error occurs, the operation is simply and quietly aborted.

    Parameters:
    group (str): An identifier for a group that a NotificationConsumer has joined.
    message (any): Some JSON-serializable data to send over the WebSocket associated witht the specified group.
    """
    channel_layer = get_channel_layer()
    try:
        async_to_sync(channel_layer.group_send)(group, message)
    except:
        pass