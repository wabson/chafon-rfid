#!/usr/bin/env python

from .base import G2InventoryResponse as BaseG2InventoryResponse, ReaderResponseFrame, Tag, TagData


class G2InventoryResponseFrame(ReaderResponseFrame):

    def __init__(self, resp_bytes, offset=0):
        super(G2InventoryResponseFrame, self).__init__(resp_bytes, offset)
        self.num_tags = 0
        if len(self.data) > 0:
            self.num_tags = self.data[0]

    def get_tag(self):
        if len(self.data) > 1:
            tag_data = TagData(self.data, prefix_bytes=0, suffix_bytes=0)
            for data_item in tag_data.get_tag_data():
                epc_value = data_item[1]
                yield Tag(epc_value)


class G2InventoryResponse(BaseG2InventoryResponse):

    frame_class = G2InventoryResponseFrame
