# tile_loader.py
import json

class MahjongTiles:
    """从json文件中读取我自定义的麻将对应规则。"""
    
    def __init__(self, filepath="resources/tile_codes.json"):
        with open(filepath, "r", encoding="utf-8") as f:
            self.tiles = json.load(f)
        self.reverse_tiles = {(u, v): k for k, [u, v] in self.tiles.items()}  # 反向查找用

    def get_value(self, tile_name):
        """通过名称获取麻将牌编号"""
        return self.tiles.get(tile_name, None)

    def get_name(self, tile_tuple):
        """通过编号获取麻将牌名称"""
        return self.reverse_tiles.get(tile_tuple, None)

# 快捷调用
mahjong = MahjongTiles()