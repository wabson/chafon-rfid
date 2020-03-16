#!/usr/bin/env python

from .base import G2InventoryResponse as BaseG2InventoryResponse
from .uhfreader288m import G2InventoryCommand as BaseG2InventoryCommand, G2InventoryResponseFrame as BaseG2InventoryResponseFrame

class G2InventoryCommand(BaseG2InventoryCommand):
    pass

class G2InventoryResponseFrame(BaseG2InventoryResponseFrame):
    pass

class G2InventoryResponse(BaseG2InventoryResponse):

    frame_class = G2InventoryResponseFrame