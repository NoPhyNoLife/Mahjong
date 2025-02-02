# rule_engine.py
import tile_loader

class RuleEngine:
    """
    Mahjong Rule Engine:
    - can_chi:  是否可以吃
    - can_peng: 是否可以碰
    - can_gang: 是否可以杠
    - can_hu:   是否可以胡牌
    - calculate_hand_value: 评估手牌价值，如向听数、搭子数、可能番数等

    注意：
    1. 这里假设手牌和牌面都用相同的标记方式（整型或特殊字符串），
       并且不考虑花牌、红中等特殊牌，亦不包含特殊牌型（七对、十三幺等）。
    2. can_chi 的前提是“只有上家打出来的牌才能吃”，此处用 player_id == 3 来代表“上家”。
    3. 评估手牌价值的方法只是示例，并不是真正的计算方式。
    4. 胡牌判断使用最常见的“4副面子 + 1对”的思路做简化，不考虑“七对/十三幺”等特殊番型。
    5. 如需更完整的逻辑，需要结合游戏流程（碰/杠后的手牌结构、各类特殊番型算法等）加以扩展。
    """

    def __init__(self, state_manager):
        self.state_manager = state_manager
        # 在此持有游戏状态，用来实现更复杂的can_gang规则判断

    def can_chi(self, hand, tile):
        """
        判断当前手牌是否可以吃这张刚打出的牌 (tile)。
        返回:可以吃的组合列表，如果为空表示无法吃
        """
        # 只有当上家打出的牌时才可以吃
        if self.state_manager.current_player != 3:
            return []

        # 如果这张牌超出常规序数牌范围，不考虑吃
        if tile_loader.mahjong.get_value(tile) == None:
            return []
        
        # 获取牌面的数字（不存在则为0）
        [tile_title, tile_number] = tile_loader.mahjong.get_value(tile)

        # 如果这张牌是非数字牌，不考虑吃
        if tile_number == 0:
            return []

        possible_chi = []
        # 三种常见顺子形态:
        # (tile-2, tile-1, tile)
        # (tile-1, tile, tile+1)
        # (tile, tile+1, tile+2)
        chi_offset_sets = [(-2, -1), (-1, 1), (1, 2)]
        for offsets in chi_offset_sets:
            needed_numbers = [tile_number + o for o in offsets]
            # 保证顺子在合法范围内 (1~9)
            if any(t < 1 or t > 9 for t in needed_numbers):
                continue
            # 检查手牌里是否都有这些牌
            needed_tiles = [tile_loader.mahjong.get_name((tile_title, n)) for n in needed_numbers]
            if all(hand.count(t) > 0 for t in needed_tiles):
                # 这里的返回格式仅作示例，把 tile 自己也包含在组合中
                combo = [tile] + needed_tiles
                possible_chi.append(sorted(combo))

        return possible_chi

    def can_peng(self, hand, tile):
        """
        判断是否可以碰这张牌。
        返回bool，能碰则 True，否则 False
        """
        return hand.count(tile) >= 2

    def can_gang(self, hand, tile):
        """
        在有新牌的情况下判断是否可以杠，分为明杠、暗杠、补杠等多种情况，这里仅作基础示例。
        返回[bool, type_number]，其中:
        bool能杠则 True，否则 False；
        type_number 0为直杠，1为暗杠，2为补杠。
        """
        if self.state_manager.current_player != 0:
            # 此时别人正在打牌
            
            # 情况0：直杠（手里就有 3 张，别人打出第 4 张）
            if hand.count(tile) == 3:
                return [True, 0]
            
        else:
            melds = self.state_manager.melds
            # 此时轮到本家摸牌
            
            # 情况1：暗杠（手里就有 3 张，再摸到一张相同的）
            if hand.count(tile) == 3:
                return [True, 1]
        
            # 情况2：补杠（已经碰了该牌，再摸到一张相同的）
            for m in melds[0]:
                if m["type"] == "PENG" and m["tile"] == tile:
                    return [True, 2]

        return [False, None]
    
    def check_dark_gang(self, hand):
        """
        用于检查当前手中的牌是否存在暗杠。
        返回一个列表，其中列出了可能的暗杠牌。
        """
        possible_dark_gangs = []
        for tile in {tuple(t) for t in hand}:
            tile = list(tile)
            if hand.count(tile) == 4:
                possible_dark_gangs.append(tile)
        return possible_dark_gangs

    def can_hu(self, hand, tile = None):
        """
        判断是否满足胡牌条件。
        简化思路：只考虑“4面子 + 1对”常规胡，不含七对、十三幺等特殊牌型。
        返回bool，能胡则 True，否则 False
        """
        # 创建新的牌数组，若 tile 不为 None，则把这张牌也放进来一起判断
        if tile is not None:
            hand.append(tile)

        hand_value = [tile_loader.mahjong.get_value(t) for t in hand]
        hand_value.sort()

        # 常规胡牌时，手牌总数应为 14（4副面子+1对 = 14 张）
        if len(hand_value) % 3 != 2:
            return False

        return self._is_standard_win(hand_value)

    def _is_standard_win(self, tiles):
        """
        判断一个完整（长度为14或满足 3n+2）的手牌是否能拆分为 (1雀头 + 4面子)。
        简化检查：只找一个对子，其余全部由刻子或顺子组成。
        """
        if not tiles:
            return False

        # 先尝试找“对”
        # 任意一种对子拆出后，再判断剩余的牌是否能全部拆成刻子/顺子
        unique_tiles = {tuple(t) for t in tiles}
        for t in unique_tiles:
            t = list(t)
            if tiles.count(t) >= 2:
                # 拆掉这个对子
                tmp = list(tiles)
                tmp.remove(t)
                tmp.remove(t)
                # 检查剩余的 12 张是否能完全拆成刻子/顺子
                if self._all_melds(tmp):
                    return True

        return False

    def _all_melds(self, tiles):
        """
        判断传入的牌（长度必为3的倍数）能否全部拆成刻子或顺子。
        这里的顺子仅考虑数牌的连续 (例如 [3,4,5])，不考虑风牌、字牌等。
        """
        # 递归结束条件：没有牌了，说明都能拆完
        if not tiles:
            return True

        tiles.sort()
        first = tiles[0]

        # 优先尝试刻子
        if tiles.count(first) >= 3:
            new_tiles = tiles[:]
            for _ in range(3):
                new_tiles.remove(first)
            if self._all_melds(new_tiles):
                return True

        # 再尝试顺子 (适用于简单数牌)
        # 首张若为 x，后面需要 (x+1), (x+2)
        if first[1] <= 7:  # 确保不会越界到 8,9 无法组成顺子
            if ([first[0], first[1] + 1] in tiles) and ([first[0], first[1] + 2] in tiles):
                new_tiles = tiles[:]
                new_tiles.remove(first)
                new_tiles.remove([first[0], first[1] + 1])
                new_tiles.remove([first[0], first[1] + 2])
                if self._all_melds(new_tiles):
                    return True
        return False

    # def calculate_hand_value(self, hand):
        """
        计算手牌价值。
        这里以“向听数 / 搭子数 / 可能番数”等概念做示例，并不是真正的算法。

        参数:
        - hand: list[int]，当前玩家的手牌
        
        返回:
        - dict，示例格式:
          {
            'shanten': x,  # 向听数
            'da_zi': y,    # 搭子数（示例里未实际计算，仅返回0）
            'fan': z       # 可能番数（此处仅示例）
          }
        """
        shanten = self._calculate_shanten(hand)
        da_zi = 0  # 示例中未真实计算
        # 可能番数仅做示例：向听越少，潜在番数越高（非常粗糙）
        possible_fan = max(0, 8 - shanten)

        return {
            "shanten": shanten,
            "da_zi": da_zi,
            "fan": possible_fan
        }

    # def _calculate_shanten(self, tiles):
        """
        计算向听数的简化示例。真正的向听算法要更复杂，这里仅做演示。
        """
        # 一种非常简单（且并不准确）的做法：
        # 向听数 = 8 -（当前能组成的刻子/顺子数 * 2） - 对子修正
        # 实际在完整算法中需要考虑多个拆分、搭子、复合形等多种情况。
        return 8
    

# rule_engine = RuleEngine()
hand = ["T1", "T2", "T3", "B4", "B4", "W6", "W6", "W6", "E", "E", "E", "B7", "B8", "B9"]
tile = "W8"
player_id = 1
melds = [[{"type": "PENG", "tile": "W8"}], [], [{"type": "GANG", "tile": "T4"}, {"type": "CHI", "tile": "B3"}], []]
# print(rule_engine.can_gang(hand, tile, melds = melds))