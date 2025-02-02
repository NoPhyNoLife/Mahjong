class DecisionMaker:
    def __init__(self, rule_engine):
        """
        rule_engine: 一个封装了 can_hu, can_peng, can_chi, can_gang, 
                     calculate_shanten, calculate_hand_score 等方法的对象
        """
        self.rule_engine = rule_engine

    def decide_action(self, state, new_tile=None):
        """
        核心决策接口：
        - state: StateManager中存储的局面信息(我的手牌, 各家舍牌, 剩余牌张, 风圈等)
        - new_tile: 对手打出的牌或我方自摸的牌
        - current_player: 当前玩家ID, 0表示自己

        返回值: (action_type, tile, [可能的附加信息]) 
        例如: ("HU", tile)、("PENG", tile)、("CHI", tile, [组合])、("DISCARD", tile)
        """

        # 1. 根据规则，先收集所有可行动作
        candidate_actions = self.get_candidate_actions(state, new_tile)

        # 如果没有任何动作(极少见，但也可能在特殊情况下出现)，就只好打牌
        if not candidate_actions:
            best_discard = self.select_best_discard(state.hand)
            return ("DISCARD", best_discard)

        # 2. 如果只有一个动作，直接返回
        if len(candidate_actions) == 1:
            return candidate_actions[0]

        # 3. 如果有多个动作，需要我们做评估再选
        best_action = self.select_best_action(state, candidate_actions)
        return best_action

    def get_candidate_actions(self, state, new_tile):
        """
        检查所有可行操作，把它们放到列表里返回。
        """
        hand = state.hand[:]  # 拷贝一份手牌
        actions = []

        # -- 先判断胡 --
        if new_tile is not None and self.rule_engine.can_hu(hand, new_tile):
            actions.append(("HU", new_tile))

        # -- 判断杠 --
        # 包括碰后加杠、明杠(对手打出)等多种情况
        if new_tile is not None and self.rule_engine.can_gang(hand, new_tile)[0]:
            actions.append(("GANG", new_tile))
        # 如果是暗杠(自摸并且手里有4张某张牌)
        possible_dark_gangs = self.rule_engine.check_dark_gang(hand)
        for tile in possible_dark_gangs:
            actions.append(("AN GANG", tile))

        # -- 判断碰 --
        if new_tile is not None and self.rule_engine.can_peng(hand, new_tile):
            actions.append(("PENG", new_tile))

        # -- 判断吃 (只在上家出牌时有效) --
        if new_tile is not None and self.rule_engine.can_chi(hand, new_tile) != []:
            # 可能一个牌可以吃出多种组合(如3,4,5和4,5,6)
            for combo in self.rule_engine.can_chi(hand, new_tile):
                actions.append(("CHI", new_tile, combo))

        # 注意：此时我们还没把“打牌”加到 actions 中，因为“打牌”本身往往是在
        # “不吃、不碰、不杠、不胡”之后才做。但是有些人也会把"DISCARD"看作一种
        # 候选动作，放进来一起比较，这也行。

        # 如果在轮到自己出牌(没有新_tile 或者选择不吃碰杠)，那就一定要打牌
        # 这里仅示例说明：
        if new_tile is None or self.rule_engine.must_discard_if_none_action(): 
            # 说明这是自己摸牌后的回合，需要打牌
            for tile in set(hand):
                actions.append(("DISCARD", tile))

        return actions

    def select_best_action(self, state, candidate_actions):
        """
        在多个可行动作中，通过“模拟+评估”选出最优动作。
        """
        best_score = -999999
        best_act = None

        for action in candidate_actions:
            # 1. 模拟执行该动作
            simulated_state = self.simulate_action(state, action)
            
            # 2. 对模拟后的状态打分
            score = self.evaluate_state(simulated_state)
            
            # 3. 记录最高分的动作
            if score > best_score:
                best_score = score
                best_act = action

        return best_act

    def simulate_action(self, state, action):
        """
        基于当前 state，模拟执行给定动作(吃/碰/杠/胡/打牌)，返回“新”状态。
        该新状态只用于评估，不会真正改动传进来的原state。
        """
        import copy
        new_state = copy.deepcopy(state)

        act_type = action[0]
        tile = action[1]

        if act_type == "HU":
            # 标记new_state某个字段为“胡了”，或直接给new_state加上某些胜利标记
            new_state.has_won = True
            # 评估时可以直接给一个超级高分
            return new_state

        elif act_type == "GANG":
            # 从手牌移除3张或4张 tile，或从meld变成杠
            self.handle_gang(new_state, tile)
            # 通常还会“补牌”，这里可以简单忽略或做随机处理
            return new_state

        elif act_type == "PENG":
            # 从手牌移除2张 tile，加到meld中
            self.handle_peng(new_state, tile)
            # 然后还需要打牌(碰之后要出一张牌)
            # 在这里可以考虑“自动选一张最好的牌打”或在评估时再深一层模拟
            # 这里演示简单做法：自动打出最差的那张
            discard_tile = self.select_best_discard(new_state.hand)
            new_state.hand.remove(discard_tile)
            new_state.discards[0].append(discard_tile)
            return new_state

        elif act_type == "CHI":
            # action形如 ("CHI", tile, comb)
            comb = action[2]
            self.handle_chi(new_state, tile, comb)
            # 吃完也要打牌
            discard_tile = self.select_best_discard(new_state.hand)
            new_state.hand.remove(discard_tile)
            new_state.discards[0].append(discard_tile)
            return new_state

        elif act_type == "DISCARD":
            # 打牌动作
            if tile in new_state.hand:
                new_state.hand.remove(tile)
                new_state.discards[0].append(tile)
            return new_state

        # 如果还有别的动作类型，在这里补充
        return new_state

    def evaluate_state(self, state):
        """
        对当前局面进行打分:
        1. 如果已经胡了(如 simulate_action 中标记了 has_won)，给高分
        2. 否则，根据向听数、听牌张数等进行估分
        """
        if getattr(state, "has_won", False) is True:
            return 1000000  # 一个非常大的分数

        # 计算向听数(离胡牌差几步)
        shanten = self.rule_engine.calculate_shanten(state.hand)
        # 可以简单地把分数设为负的向听数(向听数越小分数越高)
        score = -shanten * 100

        # 如果已经听牌(向听数=0)，可以再加一些额外的评价，如听张数多少
        if shanten == 0:
            ting_tiles_count = self.rule_engine.calculate_ting_tiles_count(state.hand)
            score += ting_tiles_count * 5

        # 你也可以加入更多因素，比如副露数量、防守安全度等等
        return score

    def select_best_discard(self, hand):
        """
        在没有其他操作时，决定打哪张牌。
        这里以“使向听数最优”为例——遍历手牌，每打出去一张，就算一下新的向听数，选向听数最低的。
        """
        best_tile = None
        best_shanten = 99

        for tile in set(hand):
            temp_hand = hand[:]
            temp_hand.remove(tile)
            shanten = self.rule_engine.calculate_shanten(temp_hand)
            if shanten < best_shanten:
                best_shanten = shanten
                best_tile = tile

        return best_tile

    # ===== 以下几个 handle_xxx 函数是模拟动作的具体逻辑 =====

    def handle_gang(self, state, tile):
        """
        模拟杠: 具体要从手牌删除4张(或从碰面子中再加1张变杠)等等。
        """
        # 简化示例：假设是手里4张暗杠
        for _ in range(4):
            state.hand.remove(tile)
        # melds[0]表示自己副露
        state.melds[0].append(("GANG", tile))

        # 一般还需要从牌山摸一张补牌，这里可忽略或随机抽
        # state.hand.append( ... )

    def handle_peng(self, state, tile):
        """
        模拟碰：从手牌删除2张tile，加到meld里
        """
        count_removed = 0
        new_hand = []
        for t in state.hand:
            if t == tile and count_removed < 2:
                count_removed += 1
            else:
                new_hand.append(t)
        state.hand = new_hand
        state.melds[0].append(("PENG", tile))

    def handle_chi(self, state, tile, comb):
        """
        模拟吃：从手牌中删除 comb(例: [3筒, 4筒])，加上 tile(例: 5筒)
        comb 是已经包含tile的完整顺子，也可以不包含，需要你自己定。
        """
        for c in comb:
            state.hand.remove(c)
        state.melds[0].append(("CHI", comb))