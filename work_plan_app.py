import sys
import os
import json
from datetime import datetime, timedelta
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QLineEdit, QTextEdit, QPushButton, QListWidget, QComboBox, QMessageBox, QDialog
from PyQt5.QtCore import Qt

class WorkPlanApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("工作计划/总结管理工具")
        self.setGeometry(100, 100, 800, 600)
        
        # 数据存储
        self.records = {}
        self.title_records = []
        self.member_records = []
        
        
        # 初始化当前记录
        self.dateNow = datetime.now()
        self.current_date = self.dateNow.strftime("%Y/%m/%d")
        self.current_date_title = self.dateNow.strftime("%Y-%m-%d")
        self.yesterday = self.dateNow - timedelta(days=1)
        self.current_record = {
            "title": "",
            "members": {},
            "date": self.current_date
        }
        
        self.current_member_index = None
        # 主界面布局
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        self.layout = QVBoxLayout()
        self.main_widget.setLayout(self.layout)
        
        # 标题部分
        self.title_layout = QHBoxLayout()
        # self.title_input = QLineEdit()
        # self.title_input.setPlaceholderText("输入标题，如'XX组工作计划'或'XX组工作总结'")
        # self.title_input.setMinimumWidth(300)
        self.title_layout.addWidget(QLabel(self.current_date))
        # self.title_layout.addWidget(self.title_input)
        
        # 标题历史选择
        # self.title_history_label = QLabel("历史标题:")
        self.title_combo = QComboBox()
        self.title_combo.setEditable(True)
        self.title_combo.setMinimumWidth(300)
        
        self.load_title()
        self.title_combo.currentTextChanged.connect(self.load_selected_record)
        # self.title_layout.addWidget(self.title_history_label)
        self.title_layout.addWidget(self.title_combo)
        

        
        #添加标题
        self.add_title_button = QPushButton("保存标题")
        self.add_title_button.clicked.connect(self.add_title)
        
        #删除标题
        self.delete_title_button = QPushButton("删除标题")
        self.delete_title_button.clicked.connect(self.delete_title)
        
        self.title_layout.addWidget(self.add_title_button)
        self.title_layout.addWidget(self.delete_title_button)
        
        self.layout.addLayout(self.title_layout)

        # 成员内容部分
        self.member_layout = QHBoxLayout()
        
        # 成员列表
        self.member_list = QListWidget()
        self.member_list.setFixedWidth(150)
        self.load_member_list()
        self.member_list.itemSelectionChanged.connect(self.show_member_content)
        self.member_layout.addWidget(self.member_list)
        
        # 成员内容编辑区
        self.content_layout = QVBoxLayout()
        
        self.member_name_input = QLineEdit()
        self.member_name_input.setPlaceholderText("成员姓名")
        self.content_layout.addWidget(self.member_name_input)
        
        self.content_edit = QTextEdit()
        self.content_edit.setPlaceholderText("输入工作内容...")
        self.content_layout.addWidget(self.content_edit)
        
        # 成员操作按钮
        self.member_button_layout = QHBoxLayout()
        self.add_member_button = QPushButton("添加成员")
        self.add_member_button.clicked.connect(self.add_member)
        self.update_member_button = QPushButton("更新内容")
        self.update_member_button.clicked.connect(self.update_member_content)
        self.remove_member_button = QPushButton("删除成员")
        self.remove_member_button.clicked.connect(self.delete_member)
        self.clear_button = QPushButton("清空所有内容")
        self.clear_button.clicked.connect(self.clear_records)
        self.member_button_layout.addWidget(self.add_member_button)
        self.member_button_layout.addWidget(self.update_member_button)
        self.member_button_layout.addWidget(self.remove_member_button)
        self.member_button_layout.addWidget(self.clear_button)
        
        self.content_layout.addLayout(self.member_button_layout)
        self.member_layout.addLayout(self.content_layout)
        self.layout.addLayout(self.member_layout)
        
        # 底部按钮
        self.button_layout = QHBoxLayout()
        
        self.generate_button = QPushButton("生成汇总内容")
        self.generate_button.clicked.connect(self.generate_summary)
        self.button_layout.addWidget(self.generate_button)
        
        self.save_button = QPushButton("保存记录")
        self.save_button.clicked.connect(self.save_record)
        self.save_button.setShortcut("Ctrl+S")
        self.button_layout.addWidget(self.save_button)
        
        self.import_button = QPushButton("导入前一日记录")
        self.import_button.clicked.connect(self.import_previous_day)
        self.button_layout.addWidget(self.import_button)
        
        self.layout.addLayout(self.button_layout)
        
        self.load_records()

    def load_records(self):
        """加载保存的记录"""
        # self.load_title()
        # self.load_member_list()
        
        title = self.title_combo.currentText().strip()
        summary = f"{self.current_date_title}_{title}"
        year = self.dateNow.year
        month = self.dateNow.month
        dir_path = os.path.join("records", str(year), str(month))
        file_path = os.path.join(dir_path, f"work_records_{summary}.json")
        if os.path.exists(file_path):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    self.current_record = json.load(f)
                if self.current_member_index != None:
                    self.get_current_content()
            except Exception as e:
                raise e
                # os.remove(file_path)
    
    def save_records(self):
        """保存所有记录到文件"""
        title = self.title_combo.currentText().strip()
        summary = f"{self.current_date_title}_{title}"
        year = self.dateNow.year
        month = self.dateNow.month
        dir_path = os.path.join("records", str(year), str(month))
        file_path = os.path.join(dir_path, f"work_records_{summary}.json")
        
        # 创建目录结构
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(self.current_record, f, ensure_ascii=False, indent=2)
    
    def load_title(self):
        """加载标题到下拉框"""
        if not os.path.exists("title.json"):
            self.title_records = ["XX组工作计划","XX组工作总结"]
            self.save_title()
            self.title_combo.addItems(self.title_records)
        else:
            self.update_title()

        if datetime.now().hour < 12 :
            self.title_combo.setCurrentIndex(0)
        else:
            self.title_combo.setCurrentIndex(1)

    def update_title(self):
        """更新标题"""
        currentTitle = self.title_combo.currentText()
        self.save_title()
        try:
            with open("title_records.json", "r", encoding="utf-8") as f:
                self.title_records = json.load(f)
        except:
            self.title_records = ["XX组工作计划","XX组工作总结"]
            os.remove("title_records.json")
        self.title_combo.clear()
        self.title_combo.addItems(self.title_records)
        if currentTitle in self.title_records:
            self.title_combo.setCurrentIndex(self.title_records.index(currentTitle))
        else:
            self.title_combo.setCurrentIndex(0)
    def save_title(self):
        """保存标题到文件"""
        with open("title_records.json", "w", encoding="utf-8") as f:
            json.dump(self.title_records, f, ensure_ascii=False, indent=2)
    def add_title(self):
        newTitle = self.title_combo.currentText().strip()
        if not newTitle:
            QMessageBox.warning(self, "警告", "标题不能为空")
            return
        if newTitle in self.title_records:
            QMessageBox.warning(self, "警告", "该标题已存在")
            return
        self.title_records.append(newTitle)
        self.update_title()
        QMessageBox.information(self, "成功", "标题已更新")
        return

    def delete_title(self):
        """删除当前标题"""
        currentTitle = self.title_combo.currentText().strip()
        if not currentTitle:
            QMessageBox.warning(self, "警告", "请选择要删除的标题")
            return
        if currentTitle in self.title_records:
            reply = QMessageBox.question(self, "确认", f"确定要删除标题 '{currentTitle}' 吗?",QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.title_records.remove(currentTitle)
                self.update_title()
                QMessageBox.information(self, "成功", "标题已删除")
        else:
            QMessageBox.warning(self, "警告", "当前标题不存在")

    def load_selected_record(self):
        """加载选中的历史记录"""
        title = self.title_combo.currentText()
        if not title:
            return
        summary = f"{self.current_date_title}_{title}"
        year = self.dateNow.year
        month = self.dateNow.month
        dir_path = os.path.join("records", str(year), str(month))
        file_path = os.path.join(dir_path, f"work_records_{summary}.json")
        if os.path.exists(file_path):
            reply = QMessageBox.question(self, "帮助", f"检测到已有数据，是否覆盖？（覆盖将导致现有数据丢失）",QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.load_records()

    
    def load_member_list(self):
        """加载成员列表"""
        if not os.path.exists("member_records.json"):
            self.member_records = []
        else:
            try:
                with open("member_records.json", "r", encoding="utf-8") as f:
                    self.member_records = json.load(f)
            except:
                self.member_records = []
                os.remove("member_records.json")
        self.member_list.addItems(self.member_records)
    
    def save_member_list(self):
        """保存成员列表到文件"""
        with open("member_records.json", "w", encoding="utf-8") as f:
            json.dump(self.member_records, f, ensure_ascii=False, indent=2)
    
    def update_member_records(self):
        """更新成员记录"""
        current_member = self.member_name_input.text().strip()
        self.save_member_list()
        self.member_list.clear()
        self.member_list.addItems(self.member_records)
        if current_member in self.member_records:
            index = self.member_records.index(current_member)
            self.member_list.setCurrentRow(index)
        else:
            self.member_list.setCurrentRow(0)

    def add_member(self):
        """添加新成员"""
        member_name = self.member_name_input.text().strip()
        if not member_name:
            QMessageBox.warning(self, "警告", "请输入成员姓名")
            return
        
        if member_name in self.member_records:
            QMessageBox.warning(self, "警告", "该成员已存在")
            return
        
        self.member_records.append(member_name)
        self.update_member_records()
        QMessageBox.information(self, "成功", "成员已添加")
        
        
        # 自动选择新添加的成员
        items = self.member_list.findItems(member_name, Qt.MatchExactly)
        if items:
            self.member_list.setCurrentItem(items[0])
    
    def delete_member(self):
        """删除当前选中的成员"""
        current_item = self.member_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "警告", "请选择要删除的成员")
            return
        
        member_name = current_item.text()
        reply = QMessageBox.question(self, "确认", f"确定要删除成员 {member_name} 吗?",
                                    QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.member_records.remove(member_name)
            self.update_member_records()
            self.content_edit.clear()
            QMessageBox.information(self, "成功", "成员已删除")
    def update_member_content(self):
        """更新当前成员的内容"""
        current_item = self.member_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "警告", "请选择要更新的成员")
            return
        
        member_name = current_item.text()
        content = self.content_edit.toPlainText().strip()
        self.current_record["members"][member_name] = content
        QMessageBox.information(self, "成功", "内容已更新")
    
    def remove_member(self):
        """删除当前选中的成员"""
        current_item = self.member_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "警告", "请选择要删除的成员")
            return
        
        member_name = current_item.text()
        reply = QMessageBox.question(self, "确认", f"确定要删除成员 {member_name} 吗?",
                                    QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            if member_name in self.current_record["members"]:
                del self.current_record["members"][member_name]
            self.member_list.takeItem(self.member_list.row(current_item))
            self.content_edit.clear()
            self.member_records.remove(member_name)
            self.update_member_records()
    
    def show_member_content(self):
        """显示选中成员的内容"""
        if self.current_member_index == None:
            self.current_member_index = self.member_list.currentRow()
        else:
            self.change_member_content()
            self.current_member_index = self.member_list.currentRow()
        
        current_member_name = self.member_list.currentItem()
        if current_member_name:
            current_member_name = current_member_name.text()
            content = self.current_record["members"].get(current_member_name, "")
            self.content_edit.setPlainText(content)
            self.member_name_input.setText(current_member_name)
        
    
    def change_member_content(self):
        """更改成员内容"""
        member_name = self.member_list.item(self.current_member_index).text()
        content = self.content_edit.toPlainText().strip()
        if member_name in self.current_record["members"]:
            if self.current_record["members"][member_name] and not content:
                reply = QMessageBox.question(
                    self, "确认", 
                    f"当前数据为空，是否覆盖？",
                    QMessageBox.Yes | QMessageBox.No
                )
                if reply == QMessageBox.Yes:
                    self.current_record["members"][member_name] = content
            else:
                self.current_record["members"][member_name] = content
        else:
            self.current_record["members"][member_name] = content

    def get_current_content(self):
        member_name = self.member_list.item(self.current_member_index).text()
        if member_name in self.current_record["members"]:
            content = self.current_record["members"][member_name]
        else:
            content = ""
        self.content_edit.setPlainText(content)
    def generate_summary(self):
        """生成汇总内容"""
        if self.current_member_index is not None:
            self.change_member_content()
        title = self.title_combo.currentText().strip()
        if not title:
            QMessageBox.warning(self, "警告", "请输入标题")
            return
        
        if not self.current_record["members"]:
            QMessageBox.warning(self, "警告", "请添加至少一个成员")
            return
        
        summary = f"{self.current_date} {title}:\n"
        for member, content in self.current_record["members"].items():
            if content.strip():
                summary += f"{member}:\n{content}\n"
        
        # 显示汇总内容对话框
        dialog = QDialog(self)
        dialog.setWindowTitle("汇总内容")
        layout = QVBoxLayout()
        
        text_edit = QTextEdit()
        text_edit.setPlainText(summary)
        text_edit.setReadOnly(False)  # 允许用户编辑后再复制
        layout.addWidget(text_edit)
        
        copy_button = QPushButton("复制内容")
        copy_button.clicked.connect(lambda: self.copy_to_clipboard(summary))
        layout.addWidget(copy_button)
        
        close_button = QPushButton("关闭")
        close_button.clicked.connect(dialog.close)
        layout.addWidget(close_button)
        
        dialog.setLayout(layout)
        dialog.exec_()
    
    def copy_to_clipboard(self, text):
        """复制文本到剪贴板"""
        clipboard = QApplication.clipboard()
        clipboard.setText(text)
        QMessageBox.information(self, "成功", "内容已复制到剪贴板")
    
    def save_record(self):
        """保存当前记录"""
        title = self.title_combo.currentText().strip()
        self.change_member_content()

        if not title:
            QMessageBox.warning(self, "警告", "请输入标题")
            return
        
        if not self.current_record["members"]:
            QMessageBox.warning(self, "警告", "当前记录为空")
            return
            
        self.current_record["title"] = title
        self.current_record["date"] = self.current_date
        
        # 保存到记录字典
        self.save_records()
        
        QMessageBox.information(self, "成功", "记录已保存")
    
    def clear_records(self):
        reply = QMessageBox.question(self, "确认", f"确定要清空数据吗",QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes :
            self.current_record["members"] = {}
            self.content_edit.clear()
    def import_previous_day(self):
        """导入前一天的记录"""
        previous_date = self.yesterday.strftime("%Y-%m-%d")
        title = self.title_combo.currentText().strip()
        summary = f"{previous_date}_{title}"
        year = self.yesterday.year
        month = self.yesterday.month
        dir_path = os.path.join("records", str(year), str(month))
        file_path = os.path.join(dir_path, f"work_records_{summary}.json")
        if os.path.exists(file_path):
            # 询问用户是否要导入
            reply = QMessageBox.question(
                self, "确认", 
                f"确定要导入 {previous_date} 的记录吗?\n当前内容将被覆盖。",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                with open(file_path, "r", encoding="utf-8") as f:
                    last_records = json.load(f)
                current_item = self.member_list.currentItem()
                if not current_item:
                    for i in self.member_records:
                        if i in last_records["members"]:
                            self.current_record["members"][i] = last_records["members"][i]
                else:
                    current_member_name = current_item.text()
                    if current_member_name in last_records["members"]:
                        self.current_record["members"][current_member_name] = last_records["members"][current_member_name]
                        self.content_edit.setPlainText(last_records["members"][current_member_name])
                    else:
                        QMessageBox.warning(self, "警告", f"没有找到 {current_member_name} 的记录")
        else:
            QMessageBox.information(self, "提示", f"没有找到 {previous_date} 的记录")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = WorkPlanApp()
    window.show()
    sys.exit(app.exec_())