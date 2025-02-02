import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, 
                             QPushButton, QLabel, QVBoxLayout, 
                             QHBoxLayout, QMessageBox)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt

class MahjongGUI(QMainWindow):
    def __init__(self, state_manager, decision_maker):
        super().__init__()

        self.state_manager = state_manager
        self.decision_maker = decision_maker

        self.initUI()

    def initUI(self):
        self.setWindowTitle("AI麻将助手")
        self.setGeometry(100, 100, 1200, 800)

        # 主容器Widget
        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        # 主布局
        main_layout = QVBoxLayout(main_widget)

        # 1. 顶部：其他玩家信息/出牌区
        self.top_info_label = QLabel("这里显示对手信息与出牌")
        main_layout.addWidget(self.top_info_label)

        # 2. 中部：牌局展示(弃牌、玩家副露等)
        self.board_area = QWidget()
        self.board_layout = QHBoxLayout(self.board_area)
        main_layout.addWidget(self.board_area)

        # 3. 底部：我的手牌区域 + 操作提示
        bottom_widget = QWidget()
        bottom_layout = QVBoxLayout(bottom_widget)
        main_layout.addWidget(bottom_widget)

        # 3.1 我的手牌展示
        self.my_hand_area = QHBoxLayout()
        bottom_layout.addLayout(self.my_hand_area)

        # 3.2 操作按钮或提示
        self.action_buttons_layout = QHBoxLayout()
        bottom_layout.addLayout(self.action_buttons_layout)

        self.btn_chi = QPushButton("吃")
        self.btn_peng = QPushButton("碰")
        self.btn_gang = QPushButton("杠")
        self.btn_hu = QPushButton("胡")

        self.btn_chi.clicked.connect(lambda: self.on_action_clicked("CHI"))
        self.btn_peng.clicked.connect(lambda: self.on_action_clicked("PENG"))
        self.btn_gang.clicked.connect(lambda: self.on_action_clicked("GANG"))
        self.btn_hu.clicked.connect(lambda: self.on_action_clicked("HU"))

        self.action_buttons_layout.addWidget(self.btn_chi)
        self.action_buttons_layout.addWidget(self.btn_peng)
        self.action_buttons_layout.addWidget(self.btn_gang)
        self.action_buttons_layout.addWidget(self.btn_hu)

        # 4. 绘制初始手牌
        self.update_hand_display()

    def update_hand_display(self):
        """
        根据 state_manager.hand 里的牌，更新底部手牌区域控件
        """
        # 先清除旧的
        for i in reversed(range(self.my_hand_area.count())):
            widget = self.my_hand_area.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        # 重新绘制我的手牌
        for tile in self.state_manager.hand:
            tile_label = QLabel()
            tile_label.setPixmap(QPixmap(self.get_tile_image_path(tile)).scaled(60, 80, Qt.KeepAspectRatio))
            # 这里添加事件: 用户点击此Label时 => 出牌/选牌
            tile_label.mousePressEvent = lambda e, t=tile: self.on_tile_clicked(t)
            self.my_hand_area.addWidget(tile_label)

    def on_tile_clicked(self, tile):
        """
        用户点击某个手牌：可视为想打出这张牌，或者想选择这张牌配合吃碰杠
        具体逻辑看你怎么设计
        """
        # 简化：直接弹出对话框问是否要打出这张
        reply = QMessageBox.question(self, "打牌", f"确定要打出 {tile} 吗？",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            # 更新手牌
            if tile in self.state_manager.hand:
                self.state_manager.hand.remove(tile)
            # 更新弃牌区
            self.state_manager.discards[0].append(tile)
            # 刷新UI
            self.update_hand_display()

            # 在这里也可以调用 AI的决策(如果需要)
            # ...

    def on_action_clicked(self, action_type):
        """
        用户点击了“吃/碰/杠/胡”按钮
        需要跟AI逻辑结合，或者让用户选择具体组合
        """
        QMessageBox.information(self, "信息", f"你点击了 {action_type} ，但还需要更多逻辑来处理哦。")

    def get_tile_image_path(self, tile):
        """
        返回对应牌面图片的路径。
        这里假设你有对应资源文件，如 images/W1.png, images/T9.png 等
        """
        # 简单写法举例
        return f"./images/{tile}.png"


def run_gui_app(state_manager, decision_maker):
    app = QApplication(sys.argv)
    gui = MahjongGUI(state_manager, decision_maker)
    gui.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    # 伪造 state_manager, decision_maker
    from collections import defaultdict

    class FakeStateManager:
        def __init__(self):
            self.hand = ["W1","W2","W3","W5","T3","T3","T4","T7","S6","S7","Z1","Z1","Z2"]
            self.discards = [[] for _ in range(4)]
            self.melds = [[] for _ in range(4)]

    class FakeDecisionMaker:
        pass

    sm = FakeStateManager()
    dm = FakeDecisionMaker()

    run_gui_app(sm, dm)