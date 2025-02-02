# state_manager.py

import deck_counter

class StateManager:

    def __init__(self, player_number = 4):
    
        self.hand = []
        self.remain = []
        self.discards = [[] for _ in range(player_number)]  # 建立每个玩家的弃牌堆
        self.melds = [[] for _ in range(player_number)]     # 副露，即吃碰杠信息

        self.deck_list = deck_counter.load_deck("recourse/deck")
        self.deck_counter = deck_counter.DeckCounter(self.deck_list)


    def start(self):
        # 输入坐庄玩家信息
        self.current_player = int(input("请输入坐庄的玩家位置: "))
        
        # 输入手牌
        my_hand = input("请输入你的初始手牌(如 W1 W2 W3,...): ").upper().split()
        self.initialize_hand(my_hand)

    def initialize_hand(self, new_hand):
        # 初始化手牌
        self.hand = new_hand
        for t in new_hand:
            self.deck_counter.discard(t)

    def update(self):
        """
        主程序函数
        """

        # if user_input.upper() == "QUIT":
            #     break
        
        if self.current_player != 0:
            # 第一种情况：非本家回合，在对手出牌后进行决策。

            self.opponent_discard()
            
        else:
            # 如果是自己打牌，就在第一阶段，看自己摸到了什么牌
            self.my_fetch()
            
            # 执行决策

            # 更新出牌状态
            self.my_discard()
        
        
        # 执行决策，第二阶段统一执行
        # action = decision_maker.decide_action(state_manager, new_tile=tile, current_player=0)
        # print(f"AI建议: {action}")
        # 根据AI建议来更新手牌或明刻信

        # 进行第二阶段出牌记录
        self.handle_second_phase()

    def my_fetch(self):
        # 第零阶段：玩家摸牌，随后进行决策
        user_input = input("请输入我方摸牌(如W2): ").upper()
        self.hand.append(user_input)
        self.deck_counter.discard(user_input)

    def add_discard(self, player_id, tile):
        # 第一阶段：玩家出牌
        self.discards[player_id].append(tile)
    
    def my_discard(self):
        # 用于我方出牌
        tile = input("请输入你的出牌: ").upper()
        self.add_discard(0, tile)
        self.hand.remove(tile)
        self.remain = [0, tile]
    
    def opponent_discard(self):
        # 用于对手出牌
        # 假设外部输入：“player_id tile”
        player_id, tile = input("请输入对手出牌(如 1 T5)").upper().split()
        player_id = int(player_id)
        self.remain = [player_id, tile]
            
        # 更新对方出牌信息
        self.add_discard(player_id, tile)
        self.deck_counter.discard(tile)

    def add_meld(self, player_id, meld):
        # 第二阶段：副露阶段，其他玩家进行反应
        self.melds[player_id].append(meld)
    
    def handle_second_phase(self):
        # 处理第二阶段的本方行动
        while True:
            event = input("输入发生的事件: ").upper()
            if event == "N":
                # 无事发生，回合正常结束
                break
            else:
                # 第二阶段还没结束
                event = event.split()
                if event[0] == 0:
                    # 轮到本家出牌
                    self.handle_my_action(event[1:])
                else:
                    # 其他人出牌
                    if event[1] == "PENG":
                        # 打出碰牌
                        current_player, tile = int(event[0]), self.remain[1]
                        self.handle_peng(current_player, tile)

                        # 剩余牌库减少两张牌
                        self.deck_counter.discard(tile)
                        self.deck_counter.discard(tile)

                    elif event[1] == "GANG":
                        # 打出杠牌
                        current_player, tile = int(event[0]), self.remain[1]
                        self.handle_gang(current_player, tile)

                        # 剩余牌库减少三张牌
                        self.deck_counter.discard(tile)
                        self.deck_counter.discard(tile)
                        self.deck_counter.discard(tile)

                    elif event[1] == "CHI":
                        # 吃上家牌
                        current_player, tile1, tile2, tile3 = int(event[0]), self.remain[1], event[2], event[3]
                        self.handle_chi(current_player, event[2:])

                        # 剩余牌库减少打出的吃牌
                        self.deck_counter.discard(tile2)
                        self.deck_counter.discard(tile3)

        # 出牌方流转
        self.player_changeto((self.current_player + 1) % 4)


    def handle_my_action(self, action, *tiles):
        # 用于处理本方出牌及后端

        tile = self.remain[1]
        if action == "PENG":
            self.handle_peng(0, tile)
            self.hand.remove(tile)
            self.hand.remove(tile)
        elif action == "GANG":
            self.handle_gang(0, tile)
            self.hand.remove(tile)
            self.hand.remove(tile)
            self.hand.remove(tile)
        elif action == "CHI":
            self.hand.remove(tiles)
            tiles = [tile].append(tiles)
            self.handle_chi(0, tiles)
    
    def handle_chi(self, player_id, tiles):
        if player_id == 0:
            # 我方吃牌，需要再出一张
            self.my_discard()
        else:
            # 对方吃牌，需要记录对方的出牌
            self.opponent_discard()
        self.add_meld(player_id, meld = {"type": "CHI", "tile": tiles})
        self.player_changeto(player_id)

    def handle_peng(self, player_id, tile):
        if player_id == 0:
            # 我方碰牌，需要再出一张
            self.my_discard()
        else:
            # 对方碰牌，需要记录对方的出牌
            self.opponent_discard()
            
        self.add_meld(player_id, meld = {"type": "PENG", "tile": [tile, tile, tile]})
        self.player_changeto(player_id)
    
    def handle_gang(self, player_id, tile):
        if player_id == 0:
            # 我方明杠，啥都不做
            pass
        self.add_meld(player_id, meld = {"type": "GANG", "tile": [tile, tile, tile, tile]})
        self.player_changeto(player_id)
    
    def player_changeto(self, next_player):
        # 结束阶段：回合结束，轮到某一方出牌
        self.current_player = next_player

    # ... 其他可能的状态更新方法