#!/usr/bin/env python

from .base import G2InventoryResponse as BaseG2InventoryResponse, ReaderCommand, ReaderResponseFrame, Tag, TagData
from .command import G2_TAG_INVENTORY


class G2InventoryCommand(ReaderCommand):

    def __init__(self, q_value, deliver_statistics=0, session=0, strategy=0, fast_id=0):
        # TODO check q_value in range 0 ~ 15, session 0 ~ 3
        q_value_byte = (deliver_statistics << 7) + (strategy << 6) + (fast_id << 5) + q_value
        cmd_data = [ q_value_byte, session ]
        #cmd_data = [ 0x04, 0x00, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x80, 0x14 ]
        super(G2InventoryCommand, self).__init__(G2_TAG_INVENTORY, data=cmd_data)


def translate_antenna_num(antenna_code):
    if antenna_code == 1:
        return 1
    elif antenna_code == 2:
        return 2
    elif antenna_code == 4:
        return 3
    elif antenna_code == 8:
        return 4
    else:
        return None


class G2InventoryResponseFrame(ReaderResponseFrame):

    tag_prefix_bytes = 0
    tag_suffix_bytes = 1

    tag_data_prefix_bytes = 1 # Number of bytes before 'num tags' byte

    def __init__(self, resp_bytes, offset=0):
        super(G2InventoryResponseFrame, self).__init__(resp_bytes, offset)
        self.num_tags = 0
        self.antenna = 0
        if len(self.data) > self.tag_data_prefix_bytes:
            self.antenna = translate_antenna_num(self.data[0])
            self.num_tags = self.data[1]

    def get_tag(self):
        tag_data_prefix_and_num_tags_bytes = self.tag_data_prefix_bytes + 1
        if len(self.data) > tag_data_prefix_and_num_tags_bytes:
            tag_data = TagData(self.data[self.tag_data_prefix_bytes:], prefix_bytes=self.tag_prefix_bytes, suffix_bytes=self.tag_suffix_bytes)
            for data_item in tag_data.get_tag_data():
                epc_value = data_item[1]
                rssi = data_item[2][0]
                yield Tag(epc_value, antenna_num=self.antenna, rssi=rssi)


class G2InventoryResponse(BaseG2InventoryResponse):

    frame_class = G2InventoryResponseFrame
