# deck_counter.py
from collections import Counter
import random

class DeckCounter:
    def __init__(self, deck_list):
        """
        初始化牌组计数器。
        """

        self.initial_deck = Counter(deck_list)  # 保存初始牌组
        self.initial_deck_list = deck_list

        self.remaining_deck = self.initial_deck.copy()  # 剩余牌组计数器
        self.ramaining_deck_list = self.initial_deck_list

    def draw_random(self):
        """
        从剩余的牌堆中随机抽取一张牌。
        """
        draw_item = random.choice(self.ramaining_deck_list)
        self.remaining_deck[draw_item] -= 1
        self.ramaining_deck_list.remove(draw_item)
        print(f"Drew {draw_item}. Remaining: {self.remaining_deck[draw_item]}")

    def discard(self, tile):
        """
        弃掉一张牌（将其移出计数器）。输入要弃掉的牌名。
        """
        if self.remaining_deck[tile] > 0:
            self.remaining_deck[tile] -= 1
            self.ramaining_deck_list.remove(tile)
        else:
            print(f"Cannot discard {tile}, none left in the deck.")

    # def add_tile(self, tile):
    #     """
    #     将牌放回牌组。输入要放回的牌名。
    #     """
    #     if self.remaining_deck[tile] < self.initial_deck[tile]:
    #         self.remaining_deck[tile] += 1
    #         print(f"Added {tile} back to deck. Now: {self.remaining_deck[tile]}")
    #     else:
    #         print(f"Cannot add {tile}, already at maximum count.")

    def remaining(self):
        """
        获取当前剩余的牌组，返回牌名及其剩余数量。
        """
        print(self.ramaining_deck_list)
        return {tile: count for tile, count in self.remaining_deck.items() if count > 0}

    def reset(self):
        """
        重置牌组到初始状态。
        """
        self.remaining_deck = self.initial_deck.copy()
        self.ramaining_deck_list = self.initial_deck
        print("Deck has been reset.")


# 创建牌组计数器

def load_deck(filename):
    with open(filename, 'r') as file:
        return file.readline().strip().split(",")
    


# 测试操作
# for i in range(100):
#     deck.draw_random()       # 抽牌

# print(deck.remaining())  # 查看剩余牌

# deck.discard('B1')       # 弃牌
# print(deck.remaining())  # 再次查看剩余牌

# # deck.add_tile('Dot 5')   # 将牌放回
# print(deck.remaining())  # 检查放回后的状态

# deck.reset()             # 重置牌组
# print(deck.remaining())  # 重置后的状态
