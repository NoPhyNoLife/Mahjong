# main.py

from state_manager import StateManager
from rule_engine import RuleEngine
from decision_maker import DecisionMaker 

def main():
    # 初始化
    state_manager = StateManager()
    rule_engine = RuleEngine(state_manager)
    decision_maker = DecisionMaker(rule_engine)
    
    state_manager.start()

    while True:
        state_manager.update()

if __name__ == "__main__":
    main()