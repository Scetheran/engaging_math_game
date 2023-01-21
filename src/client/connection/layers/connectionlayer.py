
from client.common.layer import GameAppLayer

class ConnectionLayer(GameAppLayer):
    def __init__(self, layerID):
        super().__init__("connection.layer.id")
