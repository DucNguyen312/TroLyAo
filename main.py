import sys

from PyQt5.QtCore import QSize, pyqtSignal
from PyQt5.QtGui import QPixmap , QIcon

from database import *
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QListWidgetItem, QWidget, QHBoxLayout, QPushButton, QCompleter
from dangnhap import Ui_DangNhap
from trangchu import Ui_MainWindow
from PyQt5 import QtWidgets, QtCore
from train import training_bot
from chatbot import *

class MainWindow(QMainWindow):
    signal = pyqtSignal(object)
    def __init__(self):
        super().__init__()
        self.a = None
        self.taiKhoan = None

        self.uic = Ui_DangNhap()
        self.uic.setupUi(self)

        self.uic.btnDangNhap.clicked.connect(self.show_trangchu)
        self.uic.btnDangKy.clicked.connect(self.show_dangky)
        self.uic.btnDangNhap_2.clicked.connect(self.show_dangnhap)
        self.uic.btnDangKy_2.clicked.connect(self.dangky)
        self.uic.txttk.setText("admin")
        self.uic.txtmk.setText("123")
        self.uic.txtmk.returnPressed.connect(self.show_trangchu)


    def show_trangchu(self):
        tk = self.uic.txttk.text()
        mk = self.uic.txtmk.text()
        if tk != "" and mk != "":
            query = "SELECT * FROM TaiKhoan where taiKhoan = %s and matKhau = %s"
            params = (tk, mk)
            results = run_query(query, params)
            if results:
                self.taiKhoan = tk.lower()
                QMessageBox.information(self, "Thông báo", "Đăng nhập thành công")
                self.hide()
                self.trangchu_home = QMainWindow()
                self.uic1 = Ui_MainWindow()
                self.uic1.setupUi(self.trangchu_home)
                self.trangchu_home.show()
                if self.taiKhoan != "admin":
                    self.uic1.btn_Train.setDisabled(True)
                self.uic1.btnDangXuat.clicked.connect(self.dangxuat)
                self.uic1.btnClear.clicked.connect(self.clear_chat)
                self.uic1.btnGui.clicked.connect(self.chat)
                self.uic1.btnMic.clicked.connect(self.chat_mic)
                self.uic1.btnMic_vh.clicked.connect(self.chat_mic_vohan)
                self.signal.connect(self.update_gui)
                self.uic1.txtchat.returnPressed.connect(self.enter_chat)
                self.uic1.btnChatBot.clicked.connect(self.show_chatbot)
                self.uic1.btn_Train.clicked.connect(self.show_train)
                self.uic1.btnLoadDL.clicked.connect(self.loadDL)
                self.tim_kiem()
                self.uic1.btnCapNhat.clicked.connect(self.capNhatDL)
                self.Save_chat()
            else:
                QMessageBox.warning(self, "Thông báo", "Đăng nhập thất bại, vui lòng nhập lại tài khoản và mật khẩu")
        else:
            QMessageBox.warning(self, "Thông báo", "Bạn vui lòng nhập đầy đủ thông tin !")

    def show_train(self):
        self.uic1.form_main.setCurrentWidget(self.uic1.page_train)

    def show_chatbot(self):
        self.uic1.form_main.setCurrentWidget(self.uic1.page)

    def show_dangky(self):
        self.uic.stackedWidget.setCurrentWidget(self.uic.page_2)

    def show_dangnhap(self):
        self.uic.stackedWidget.setCurrentWidget(self.uic.page)

    def dangky(self):
        tk = self.uic.txttk_2.text().lower()
        mk = self.uic.txtmk_2.text().lower()
        mkm = self.uic.txtmk_3.text().lower()
        if tk == "" or mk == "" or mkm == "":
            QMessageBox.information(self,"Thông báo" ,"Bạn chưa nhập đầy đủ thông tin")
        else:
            query = "SELECT * FROM TaiKhoan where taiKhoan = %s"
            params = (tk,)
            results = run_query(query, params)
            if len(results) == 1:
                QMessageBox.information(self, "Thông Báo" , "Tài khoản đã tồn tại")
            else:
                if mk == mkm:
                    add_tai_khoan(tk, mk)
                    QMessageBox.information(self,"Thông Báo", "Đăng Ký thành công!")
                else:
                    QMessageBox.information(self, "Thông Báo", "Mật khẩu không khớp")

    def dangxuat(self):
        self.uic.txttk.setText("")
        self.uic.txtmk.setText("")
        self.trangchu_home.close()
        self.show()

    def Save_chat(self):
        query = "SELECT cauHoi , dapAn FROM DuLieu where taiKhoan = %s"
        param = (self.taiKhoan,)
        s = run_query(query, param)
        s = sum(s, ())
        for i in range(len(s)):
            if i % 2 == 0:
                user_widget = self.create_user_widget(s[i])
                item = QListWidgetItem()
                item.setSizeHint(QSize(0, 100))
                self.uic1.lvchatbot.addItem(item)
                self.uic1.lvchatbot.setItemWidget(item, user_widget)
            else:
                bot_widget = self.create_bot_widget(s[i])
                item = QListWidgetItem()
                item.setSizeHint(QSize(0, 100))
                self.uic1.lvchatbot.addItem(item)
                self.uic1.lvchatbot.setItemWidget(item, bot_widget)

            self.uic1.lvchatbot.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
            self.uic1.lvchatbot.setFocusPolicy(QtCore.Qt.NoFocus)
            self.uic1.lvchatbot.scrollToItem(item)

    def chat(self):
        try:
            content = self.uic1.txtchat.text()
            if content != "":
                # Thêm item user_widget
                user_widget = self.create_user_widget(content)
                item = QListWidgetItem()
                item.setSizeHint(QSize(0, 100))
                self.uic1.lvchatbot.addItem(item)
                self.uic1.lvchatbot.setItemWidget(item, user_widget)

                self.uic1.txtchat.setText("")

                result = chatbot(content)
                bot_widget = self.create_bot_widget(result)
                item = QListWidgetItem()
                item.setSizeHint(QSize(0, 100))
                self.uic1.lvchatbot.addItem(item)
                self.uic1.lvchatbot.setItemWidget(item, bot_widget)

                self.uic1.lvchatbot.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
                self.uic1.lvchatbot.setFocusPolicy(QtCore.Qt.NoFocus)
                self.uic1.lvchatbot.scrollToItem(item)

                add_du_lieu(content , result , self.taiKhoan)

                speak(result)
        except Exception as e:
            print(e)

    def chat_mic(self):
        r = sr.Recognizer()
        mic = sr.Microphone()
        with mic as source:
            r.adjust_for_ambient_noise(source)  # điều chỉnh nhiễu
            audio = r.listen(source, timeout=10, phrase_time_limit=10)
        try:
            content = r.recognize_google(audio, language='vi-VN').lower()

            user_widget = self.create_user_widget(content)
            item = QListWidgetItem()
            item.setSizeHint(QSize(0, 100))
            self.uic1.lvchatbot.addItem(item)
            self.uic1.lvchatbot.setItemWidget(item, user_widget)

            result = chatbot(content)
            bot_widget = self.create_bot_widget(result)
            item = QListWidgetItem()
            item.setSizeHint(QSize(0, 100))
            self.uic1.lvchatbot.addItem(item)
            self.uic1.lvchatbot.setItemWidget(item, bot_widget)
            self.uic1.lvchatbot.scrollToItem(item)
            self.uic1.lvchatbot.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
            self.uic1.lvchatbot.setFocusPolicy(QtCore.Qt.NoFocus)
            speak(result)
            add_du_lieu(content, result, self.taiKhoan)
        except sr.UnknownValueError:
            robot_rain = "Không thể xác định giọng nói! Bạn vui lòng thử lại !"
            speak(robot_rain)
            bot_widget = self.create_bot_widget(robot_rain)
            item = QListWidgetItem()
            item.setSizeHint(QSize(0, 100))
            self.uic1.lvchatbot.addItem(item)
            self.uic1.lvchatbot.setItemWidget(item, bot_widget)
        except sr.RequestError as e:
            print("Lỗi trong quá trình kết nối tới Google Speech Recognition; {0}".format(e))

    def chat_mic_vohan(self):
        t = threading.Thread(target=self.mic)
        t.start()

    def mic(self):
        r = sr.Recognizer()
        mic = sr.Microphone()

        # Set up microphone
        with mic as source:
            r.adjust_for_ambient_noise(source)
        while True:
            try:
                with mic as source:
                    audio = r.listen(source, timeout=5, phrase_time_limit=5)
                text = r.recognize_google(audio, language='vi-VN').lower()
                self.a = text
                self.signal.emit(self.a)
                time.sleep(5)

                if any(word in text for word in ["tạm biệt", "thoát", "quit", "đóng"]):
                    break
            except sr.UnknownValueError:
                robot_brain = "Xin lỗi, tôi không thể nhận dạng giọng nói của bạn! Bạn vui lòng thử lại !"
                speak(robot_brain)
                break
            except sr.RequestError:
                robot_brain = "Xin lỗi, tôi không thể kết nối tới Google Speech Recognition service!"
                speak(robot_brain)
                break

    def update_gui(self):
        user_widget = self.create_user_widget(self.a)
        item = QListWidgetItem()
        item.setSizeHint(QSize(0, 100))
        self.uic1.lvchatbot.addItem(item)
        self.uic1.lvchatbot.setItemWidget(item, user_widget)

        result = chatbot(self.a)
        bot_widget = self.create_bot_widget(result)
        item = QListWidgetItem()
        item.setSizeHint(QSize(0, 100))
        self.uic1.lvchatbot.addItem(item)
        self.uic1.lvchatbot.setItemWidget(item, bot_widget)

        speak(result)
        add_du_lieu(self.a,result , self.taiKhoan)
        self.uic1.lvchatbot.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        self.uic1.lvchatbot.setFocusPolicy(QtCore.Qt.NoFocus)
        self.uic1.lvchatbot.scrollToItem(item)

    def create_bot_widget(self , chat):
        user_widget = QWidget()
        avatar = QtWidgets.QLabel(user_widget)

        avatar.setObjectName("label")
        pixmap = QPixmap('bot.png')
        avatar.setPixmap(pixmap)
        avatar.setAlignment(QtCore.Qt.AlignLeft)

        bot_chat = QtWidgets.QLabel(user_widget)

        bot_chat.setObjectName("user_chat")
        bot_chat.setText(chat)
        bot_chat.adjustSize()
        if len(bot_chat.text().split()) <= 40:
            bot_chat.setMaximumHeight(40)
        elif len(bot_chat.text().split()) <= 80:
            bot_chat.setMaximumHeight(60)
        else:
            bot_chat.setMaximumHeight(100)
        bot_chat.setStyleSheet("border: 1px solid black; border-radius: 10px;background-color: rgb(58, 59, 60); color: white;")
        bot_chat.setAlignment(QtCore.Qt.AlignCenter)
        bot_chat.setWordWrap(True)

        h_layout = QHBoxLayout()
        h_layout.addWidget(avatar)
        h_layout.addWidget(bot_chat)
        bot_chat.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        h_layout.setContentsMargins(10, 10, 960 - bot_chat.width(), 50)
        # Set layout cho user_widget
        user_widget.setLayout(h_layout)
        return user_widget

    def create_user_widget(self ,chat):
        user_widget = QWidget()
        avatar = QtWidgets.QLabel(user_widget)

        avatar.setObjectName("label")
        pixmap = QPixmap('User.png')
        avatar.setPixmap(pixmap)
        avatar.setAlignment(QtCore.Qt.AlignRight)

        user_chat = QtWidgets.QLabel(user_widget)

        user_chat.setObjectName("user_chat")
        user_chat.setText(chat)
        user_chat.adjustSize()
        if len(user_chat.text().split()) <= 30:
            user_chat.setMaximumHeight(40)
        else:
            user_chat.setMaximumHeight(60)
        user_chat.setStyleSheet("border: 1px solid white; border-radius: 10px;background-color: rgb(25, 132, 247);color: white;")
        user_chat.setAlignment(QtCore.Qt.AlignCenter)
        user_chat.setWordWrap(True)

        h_layout = QHBoxLayout()
        h_layout.addWidget(user_chat)
        h_layout.addWidget(avatar)
        user_chat.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        h_layout.setContentsMargins(950 - (user_chat.width() - 10), 10, 0, 0)

        # Set layout cho user_widget
        user_widget.setLayout(h_layout)
        return user_widget

    def clear_chat(self):
        ans = QMessageBox.question(self,"Thông Báo" , "Bạn muốn xóa lịch sử trò chuyện ?" , QMessageBox.Yes | QMessageBox.No)
        if ans == QMessageBox.Yes:
            delete_data_by_tai_khoan(self.taiKhoan)
            QMessageBox.information(self,"Thông Báo", "Xóa lịch sử thành công !")
            self.uic1.lvchatbot.clear()
        else:
            pass

    def enter_chat(self):
        self.chat()

    def tim_kiem(self):
        self.name_tag = tag()
        self.tag_list = []
        for i in self.name_tag:
            self.tag_list.append(i.lower())
        self.completer = QCompleter(self.tag_list)
        self.uic1.txtTag.editingFinished.connect(self.result_tk_Q)
        self.uic1.txtTag.textChanged.connect(self.result_tk)

    def result_tk(self):
        self.uic1.txtTag.setCompleter(self.completer)

    def result_tk_Q(self):
        try:
            text = self.uic1.txtTag.text()
            pa = [result_pa(text)]
            p = str(pa).strip('[]').replace(",", ", \n-").replace("'", "\"")
            self.uic1.txt_hoi.setText(p)

            rep = [reslt_res(text)]
            r = str(rep).strip('[]').replace(",", ", \n-").replace("'", "\"")
            self.uic1.txt_dap.setText(r)

        except Exception as e:
            print(e)

    def loadDL(self):
        training_bot()
        QMessageBox.information(self, "Thông báo", "Huấn luyện dữ liệu thành công !")


    def capNhatDL(self):
        p = [self.uic1.txt_hoi.toPlainText().replace("\n", "").replace("\"","").replace(",","")]
        p= p[0].split('-')
        p = [s.strip() for s in p]
        countp = 0
        for i in p:
            if i == "":
                countp += 1

        r = [self.uic1.txt_dap.toPlainText().replace("\n", "").replace("\"","").replace(",","")]
        r = r[0].split('-')
        r = [s.strip() for s in r]
        countr = 0
        for j in r:
            if j == "":
                countr += 1

        tag = self.uic1.txtTag.text()

        if countp >= 1 or countr >= 1 or tag == "":
            QMessageBox.information(self, "Thông báo", "Bạn vui lòng nhập đầy đủ thông tin cập nhật")
        else:
            train_bot(tag,p,r)
            QMessageBox.information(self, "Thông báo", "Cập nhật dữ liệu thành công !")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_win = MainWindow()
    main_win.show()
    sys.exit(app.exec())