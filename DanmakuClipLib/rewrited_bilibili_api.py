"""
本文件重写了bilibili_api.video.Video.get_danmaku_view中的read_command_danmakus
修改内容请跳转到本文件第 105 行查看
"""
import aiohttp
from bilibili_api.exceptions import ArgsException, NetworkException
from bilibili_api.utils.BytesReader import BytesReader
from bilibili_api.utils.network import get_session
from bilibili_api.utils.utils import get_api
from bilibili_api.video import Video

API = get_api("video")


class Video(Video):
    async def get_danmaku_view(self, page_index: int = None, cid: int = None):
        """
        获取弹幕设置、特殊弹幕、弹幕数量、弹幕分段等信息。

        Args:
            page_index (int, optional): 分 P 号，从 0 开始。Defaults to None
            cid        (int, optional): 分 P 的 ID。Defaults to None

        Returns:
            dict: 调用 API 返回的结果。
        """
        if cid is None:
            if page_index is None:
                raise ArgsException("page_index 和 cid 至少提供一个。")

            cid = await self.__get_page_id_by_index(page_index)

        session = get_session()
        api = API["danmaku"]["view"]["url"]

        resp = await session.get(
            api,
            params={"type": 1, "oid": cid, "pid": self.get_aid()},
            cookies=self.credential.get_cookies(),
            headers={
                "Referer": "https://www.bilibili.com",
                "User-Agent": "Mozilla/5.0",
            },
        )

        try:
            resp.raise_for_status()
        except aiohttp.ClientResponseError as e:
            raise NetworkException(e.status, e.message)

        resp_data = await resp.read()
        json_data = {}
        reader = BytesReader(resp_data)
        # 解析二进制数据流

        def read_dm_seg(stream: bytes):
            reader_ = BytesReader(stream)
            data = {}
            while not reader_.has_end():
                t = reader_.varint() >> 3
                if t == 1:
                    data["page_size"] = reader_.varint()
                elif t == 2:
                    data["total"] = reader_.varint()
                else:
                    continue
            return data

        def read_flag(stream: bytes):
            reader_ = BytesReader(stream)
            data = {}
            while not reader_.has_end():
                t = reader_.varint() >> 3
                if t == 1:
                    data["rec_flag"] = reader_.varint()
                elif t == 2:
                    data["rec_text"] = reader_.string()
                elif t == 3:
                    data["rec_switch"] = reader_.varint()
                else:
                    continue
            return data

        def read_command_danmakus(stream: bytes):
            reader_ = BytesReader(stream)
            data = {}
            while not reader_.has_end():
                t = reader_.varint() >> 3
                if t == 1:
                    data["id"] = reader_.varint()
                elif t == 2:
                    data["oid"] = reader_.varint()
                elif t == 3:
                    data["mid"] = reader_.varint()
                elif t == 4:
                    data["commend"] = reader_.string()
                elif t == 5:
                    data["content"] = reader_.string()
                elif t == 6:
                    data["progress"] = reader_.varint()
                elif t == 7:
                    data["ctime"] = reader_.string()
                elif t == 8:
                    data["mtime"] = reader_.string()
                # elif t == 9:
                #     data["extra"] = json.loads(reader_.string())
                # bilibili_api 报错
                elif t == 10:
                    data["id_str"] = reader_.string()
                else:
                    continue
            return data

        def read_settings(stream: bytes):
            reader_ = BytesReader(stream)
            data = {}
            while not reader_.has_end():
                t = reader_.varint() >> 3

                if t == 1:
                    data["dm_switch"] = reader_.bool()
                elif t == 2:
                    data["ai_switch"] = reader_.bool()
                elif t == 3:
                    data["ai_level"] = reader_.varint()
                elif t == 4:
                    data["enable_top"] = reader_.bool()
                elif t == 5:
                    data["enable_scroll"] = reader_.bool()
                elif t == 6:
                    data["enable_bottom"] = reader_.bool()
                elif t == 7:
                    data["enable_color"] = reader_.bool()
                elif t == 8:
                    data["enable_special"] = reader_.bool()
                elif t == 9:
                    data["prevent_shade"] = reader_.bool()
                elif t == 10:
                    data["dmask"] = reader_.bool()
                elif t == 11:
                    data["opacity"] = reader_.float(True)
                elif t == 12:
                    data["dm_area"] = reader_.varint()
                elif t == 13:
                    data["speed_plus"] = reader_.float(True)
                elif t == 14:
                    data["font_size"] = reader_.float(True)
                elif t == 15:
                    data["screen_sync"] = reader_.bool()
                elif t == 16:
                    data["speed_sync"] = reader_.bool()
                elif t == 17:
                    data["font_family"] = reader_.string()
                elif t == 18:
                    data["bold"] = reader_.bool()
                elif t == 19:
                    data["font_border"] = reader_.varint()
                elif t == 20:
                    data["draw_type"] = reader_.string()
                else:
                    continue
            return data

        while not reader.has_end():
            type_ = reader.varint() >> 3

            if type_ == 1:
                json_data["state"] = reader.varint()
            elif type_ == 2:
                json_data["text"] = reader.string()
            elif type_ == 3:
                json_data["text_side"] = reader.string()
            elif type_ == 4:
                json_data["dm_seg"] = read_dm_seg(reader.bytes_string())
            elif type_ == 5:
                json_data["flag"] = read_flag(reader.bytes_string())
            elif type_ == 6:
                if "special_dms" not in json_data:
                    json_data["special_dms"] = []
                json_data["special_dms"].append(reader.string())
            elif type_ == 7:
                json_data["check_box"] = reader.bool()
            elif type_ == 8:
                json_data["count"] = reader.varint()
            elif type_ == 9:
                if "command_dms" not in json_data:
                    json_data["command_dms"] = []
                json_data["command_dms"].append(
                    read_command_danmakus(reader.bytes_string())
                )
            elif type_ == 10:
                json_data["dm_setting"] = read_settings(reader.bytes_string())
            else:
                continue
        return json_data
