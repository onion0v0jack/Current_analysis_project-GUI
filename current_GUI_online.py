# 版本號： ver 1.0
import datetime
import shutil
import time
import itertools
import os
import random
import sys
import warnings
import pandas as pd
from matplotlib.font_manager import FontProperties
from mplWidget import MplWidget
from PySide2 import QtCore
from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
from treeWidget import TreeWidget
from pandasModel import pandasModel
from thread import *

warnings.filterwarnings("ignore") # 要求忽略warning
import matplotlib.pyplot as plt
plt.style.use('ggplot')   # 設定畫圖風格為ggplot
plt.rcParams['font.sans-serif'] = ['SimHei'] # 設定相容中文 
plt.rcParams['axes.unicode_minus'] = False
pd.options.mode.chained_assignment = None

QtCore.QCoreApplication.addLibraryPath(os.path.join(os.path.dirname(QtCore.__file__), "plugins"))  # 掃plugin套件(windows必備)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        #【設定GUI外觀】
        # 程式標題、小圖檔、視窗大小
        self.setWindowTitle('Current anomaly detection ver 1.0')
        self.setWindowIcon(QIcon("favicon.ico"))
        self.resize(QSize(1500, 950))

        # 設定UI中的元件
        ## 按鍵顯示
        self.btn_start = QPushButton('開始')
        self.btn_pause = QPushButton('暫停')
        self.btn_stop = QPushButton('重建')
        self.btn_download_log = QPushButton('下載記錄檔')
        # self.btn_demo_switch = QPushButton('1')     # (測試)
        ## 字元顯示
        self.label_main = QLabel('電流異常偵測程式')
        self.label_setting = QLabel('設定')
        self.label_update_time = QLabel('')
        self.label_message = QLabel('')
        ## 樹表格顯示
        self.tree_config = TreeWidget()
        ## 表格顯示
        self.table_1 = QTableView()
        self.table_2 = QTableView()
        ## 圖片顯示
        self.plot = MplWidget()
        
        ## 元件細節設定
        ### 按鍵字元設定
        self.btn_start.setStyleSheet("QPushButton{font-family: Microsoft JhengHei;}")
        self.btn_pause.setStyleSheet("QPushButton{font-family: Microsoft JhengHei;}")
        self.btn_stop.setStyleSheet("QPushButton{font-family: Microsoft JhengHei;}")
        self.btn_download_log.setStyleSheet("QPushButton{font-family: Microsoft JhengHei;}")
        ### 字型設定
        self.label_main.setStyleSheet("QLabel{font-family: Microsoft JhengHei; color: rgb(0, 0, 0); font-size: 15pt; font-weight: bold;}")
        self.label_setting.setStyleSheet("QLabel{font-family: Microsoft JhengHei; color: rgb(0, 0, 0); font-size: 12pt; font-weight: bold;}")
        self.label_message.setStyleSheet("QLabel{font-family: Microsoft JhengHei; color: rgb(0, 0, 0); font-size: 10pt; border: 1px solid black;}")
        self.label_message.setWordWrap(True) # 自動換行
        ### 樹表格設定
        self.tree_config.resizeColumnToContents(0) # 將第0欄完整顯示
        ### 表格大小設定
        self.table_1.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.table_1
        # self.table_1.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # self.table_1.resizeColumnToContents(3)  
        # self.table_input_data.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents) # 把顯示表格的寬調整到最小
        # self.table_output_data.setMinimumHeight(105) # 設定顯示的最小高度
        # self.table_output_data.setMaximumHeight(110) # 設定顯示的最大高度
        ### 圖片大小設定
        self.plot.setMinimumHeight(300)

        # 設定佈局(layout)
        ## main layout
        layout = QHBoxLayout() # 建立layout並指定layout為水平切分 # 建立layout之後要定義一個widget讓layout設定進去(註*1)
        
        ## left layout
        left_layout = QVBoxLayout()                  # 設定此layout為垂直切分
        left_layout.addWidget(self.label_main)  # 建立layout之後就可以塞元件了
        setting_title_layout = QHBoxLayout()  
        setting_title_layout.addWidget(self.label_setting)
        setting_title_layout.addWidget(self.label_update_time)
        setting_title_layout.setStretchFactor(self.label_setting, 1)       # 設定left_widget與right_widget的比例
        setting_title_layout.setStretchFactor(self.label_update_time, 4)
        setting_title_widget = QWidget()
        setting_title_widget.setLayout(setting_title_layout)
        left_layout.addWidget(setting_title_widget)
        left_layout.addWidget(self.tree_config)
        left_layout.addWidget(self.label_message) 
        left_layout.setStretchFactor(self.tree_config, 4)
        left_layout.setStretchFactor(self.label_message, 3)
        # left_layout.addWidget(self.btn_demo_switch)   # (測試)
        left_layout.addWidget(self.btn_download_log)
        run_btn_layout = QHBoxLayout()  
        run_btn_layout.addWidget(self.btn_start)
        run_btn_layout.addWidget(self.btn_pause)
        run_btn_layout.addWidget(self.btn_stop)
        run_btn_widget = QWidget()
        run_btn_widget.setLayout(run_btn_layout)
        left_layout.addWidget(run_btn_widget)
        left_widget = QWidget()
        left_widget.setLayout(left_layout)           # 建立left layout的widget(參考main layout的註*1)
        
        ## right layout
        right_layout = QVBoxLayout() 
        right_layout.addWidget(self.plot)
        result_layout = QHBoxLayout()  
        result_layout.addWidget(self.table_1)
        result_layout.addWidget(self.table_2)
        result_layout.setStretchFactor(self.table_1, 4)
        result_layout.setStretchFactor(self.table_2, 3)
        result_widget = QWidget()
        result_widget.setLayout(result_layout)
        right_layout.addWidget(result_widget)
        right_widget = QWidget()
        right_widget.setLayout(right_layout)           # 建立right layout的widget(參考main layout的註*1)

        ## 置入left_widget與right_widget於main_widget
        layout.addWidget(left_widget)                 # 設定好left與right layout的widget之後加入在main layout
        layout.addWidget(right_widget)
        layout.setStretchFactor(left_widget, 1)       # 設定left_widget與right_widget的比例
        layout.setStretchFactor(right_widget, 3) 
        main_widget = QWidget()                       # (註*1)每一次建layout後要用widget包
        main_widget.setLayout(layout)                 # (註*1)每一次建layout後要用widget包
        self.setCentralWidget(main_widget)            # 設定main_widget為中心視窗


        ## 設定button觸發的slot(function)
        self.btn_start.clicked.connect(self.slot_press_start)
        self.btn_pause.clicked.connect(self.slot_press_pause)
        self.btn_stop.clicked.connect(self.slot_press_stop)
        self.btn_download_log.clicked.connect(self.slot_download)
        # self.btn_demo_switch.clicked.connect(self.slot_switch) # (測試)

        ## 設定thread
        self.th1_work = None
        self.th1_build = False # th1是否已建立
        self.th1_stopped = True  #th1是否停止

        # 【設定內部使用的全域變數】
        self.config = {
            'id': self.tree_config.child01_01.text(1),
            'ip': self.tree_config.child01_02.text(1),
            'Input data path': self.tree_config.labelBtn.text(),
            'Folder name': self.tree_config.child02_02.text(1),
            'Freq': self.tree_config.child03_01.text(1),
            'Ntrain': self.tree_config.child03_02.text(1),
            'trun': self.tree_config.child03_03.text(1),
            'cut_length': self.tree_config.child03_04.text(1),
            'BCEV': self.tree_config.child03_05.text(1),
        }
        self.table1_show = pd.DataFrame(columns = ['id', 'Start time', 'End time', 'Data length'])
        self.table2_show = pd.DataFrame(columns = ['id', 'Result'])
        self.table_1.setModel(pandasModel(self.table1_show)) # 先建立空的欄位df再放在table_1
        self.table_2.setModel(pandasModel(self.table2_show))
        self.iot_switch = None        # (測試模擬iot)

    def slot_press_start(self):
        # Initail setting
        self.config = {
            'id': self.tree_config.child01_01.text(1),
            'ip': self.tree_config.child01_02.text(1),
            'Input data path': self.tree_config.labelBtn.text(),
            'Folder name': self.tree_config.child02_02.text(1),
            'Freq': self.tree_config.child03_01.text(1),
            'Ntrain': self.tree_config.child03_02.text(1),
            'trun': self.tree_config.child03_03.text(1),
            'cut_length': self.tree_config.child03_04.text(1),
            'BCEV': self.tree_config.child03_05.text(1),
        }

        try:
            self.config['Freq'] = int(self.config['Freq'])
            self.config['Ntrain'] = int(self.config['Ntrain'])
            self.config['trun'] = float(self.config['trun'])
            self.config['cut_length'] = int(self.config['cut_length'])
            self.config['BCEV'] = float(self.config['BCEV'])
            with open(self.config['Input data path'], 'r') as f:  # 輸入資料內容錯誤，刻意產生error
                if (f.readline() != 'TimeStamp, Current, \n'):
                    print(int('ffff'))
        except:
            self.label_message.setText('請確認設定或檔案內容')
        else:
            self.label_message.setText('程式進行中')
            self.th1_work = WorkThread_generate_data(self.config) # 建立執行緒th1
            # 接收th1內部發送的信號signal_detail_list到slot_output_signal這個function
            self.th1_work.signal_filename_list_th1_to_GUI.connect(self.slot_draw_plot)  

            self.th1_work.signal_detail_list.connect(self.slot_output_signal)  
            self.th1_work.signal_train_ready.connect(self.slot_train_ready)  
            self.th1_work.signal_th1_to_table_2.connect(self.slot_update_result)  
            self.th1_build, self.th1_stopped = True, False # 按下開始鍵後，代表程序建立且無停止

            self.run_process()
            self.btn_start.setEnabled(False)
    
    def slot_press_pause(self):
        # 程序未建立時，此鍵不應該有反應
        if self.th1_build == False:
            print('正常不反應')
            self.label_message.setText('')
        elif self.btn_pause.text() == '暫停':
            self.label_message.setText('程式暫停')
            self.btn_pause.setText('繼續')
            self.th1_work.pause = True
            self.th1_build, self.th1_stopped = True, True # 按下暫停鍵後，代表程序建立且停止
        else:
            self.btn_pause.setText('暫停')
            self.label_message.setText('程式進行中')
            self.th1_work.pause = False
            self.th1_build, self.th1_stopped = True, False # 按下繼續鍵後，與按下開始鍵相同

    def slot_press_stop(self):
        # 程序未建立時，此鍵不應該有反應
        if self.th1_build == False:
            print('正常不反應')
            self.label_message.setText('')
        else:
            self.th1_work.stopped = True 
            self.btn_pause.setText('暫停')
            self.label_message.setText('程式中斷')
            # 中斷後的df需要清空，待重啟之後再寫入
            # 中斷就也會把產生資料的整個資料夾刪除
            self.table1_show = pd.DataFrame(columns = ['id', 'Start time', 'End time', 'Data length'])
            self.table2_show = pd.DataFrame(columns = ['id', 'Result'])
            shutil.rmtree('{}'.format(self.config['Folder name'])) 
            
            self.btn_start.setEnabled(True)
            self.th1_build, self.th1_stopped = False, True # 按下中斷鍵後，代表程序刪除(未建立)且停止

    def slot_download(self):
        fileName, _ = QFileDialog.getSaveFileName(self, 'Save file', '', '*.csv')  # 建立儲存檔案的對話盒(dialog)
        if fileName:
            pd.merge(self.table1_show, self.table2_show, on = 'id').to_csv(fileName, index = None)

    """
    def slot_switch(self):   #   (測試)
        if self.th1_build == True:
            if self.iot_switch != 1:  # 初始時或0時切換到1，連帶影響th1
                self.iot_switch, self.th1_work.iot_switch = 1, 1
                self.btn_demo_switch.setText('0')
                print('0 --> 1 觸發')
            else:    # 1時切換到0，連帶影響th1
                self.iot_switch, self.th1_work.iot_switch = 0, 0
                self.btn_demo_switch.setText('1')
                print('1 --> 0 觸發')
        else: 
            if self.iot_switch != 1:  # 初始時或0時切換到1，連帶影響th1
                self.iot_switch = 1
                self.btn_demo_switch.setText('0')
                print('0 --> 1 觸發')
            else:    # 1時切換到0，連帶影響th1
                self.iot_switch = 0
                self.btn_demo_switch.setText('1')
                print('1 --> 0 觸發')
    """
    
    def run_process(self):
        self.th1_work.start()
        
    def slot_output_signal(self, output_list):
        # 負責接收執行緒的信號並運算
        # 將最新的list放在最上行
        self.table1_show.loc[-1] = output_list
        self.table1_show.index = self.table1_show.index + 1
        self.table1_show = self.table1_show.sort_index()
        # print(self.table1_show)
        # 完成表格之後更新於table_1
        self.table_1.setModel(pandasModel(self.table1_show))
        
    def slot_train_ready(self, message_str):
        self.label_message.setText(message_str)
    
    def slot_update_result(self, result_df):
        self.table_2.setModel(pandasModel(result_df))
        self.table2_show = result_df
        print(self.table2_show)    
    
    def slot_draw_plot(self, message_filename_list):
        print(f'GUI: {message_filename_list[0]}')
        print(f'result: {self.table2_show}')
        result_color_dict = {
            'Normal': 'green',
            'Anomaly_2': 'orangered',
            'Anomaly_3': 'red',
            'Anomaly_4': 'maroon',
            'Anomaly_5': 'purple',    
        }
        Data = pd.read_table(r'{}'.format(self.config['Input data path']), sep = ',')
        Data = Data[['TimeStamp', ' Current']]
        count_data = Data.groupby('TimeStamp').count()
        self.plot.setRows()
        self.plot.canvas.ax[0].plot(count_data.index[1:-1], count_data.values[1:-1], linewidth = 1, color = 'steelblue')
        self.plot.canvas.ax[0].set_ylabel('count')
        self.plot.canvas.ax[0].set_xlabel('timestamp(sec)')
        self.plot.canvas.ax[0].set_title('蒐取的輸入資料在每個timestamp的資料筆數(設定100Hz)', fontproperties = FontProperties(fname = "SimHei.ttf", size = 14))
        print(f'MFL: {message_filename_list[0]}')
        if len(message_filename_list[0][1]) == 0:
            for count, filename in enumerate(message_filename_list[0][0]):
                Data = pd.read_table('{}/data/{}.txt'.format(self.config['Folder name'], filename), sep = ',')
                Data = self.truncate(Data, 'Current', 'CatchTime')
                if count == len(message_filename_list[0][0]) - 1: Linewidth, Alpha = 1.5, 1
                else: Linewidth, Alpha = 1, 0.4
                self.plot.canvas.ax[1].plot(Data.loc[:, 'CatchTime'], Data.loc[:, 'Current'], linewidth = Linewidth, color = 'grey', alpha = Alpha)
        else:
            for count, filename in enumerate(message_filename_list[0][0]):
                Data = pd.read_table('{}/data/{}.txt'.format(self.config['Folder name'], filename), sep = ',')
                Data = self.truncate(Data, 'Current', 'CatchTime')
                self.plot.canvas.ax[1].plot(Data.loc[:, 'CatchTime'], Data.loc[:, 'Current'], linewidth = 1, color = 'dimgrey', alpha = 0.2)
            for count, filename in enumerate(message_filename_list[0][1]):
                level = self.table2_show[self.table2_show['id'] == filename].loc[:, 'Result'].values[0]
                if level == 'Error':
                    pass
                else:
                    Data = pd.read_table('{}/data/{}.txt'.format(self.config['Folder name'], filename), sep = ',')
                    Data = self.truncate(Data, 'Current', 'CatchTime')
                    if count == len(message_filename_list[0][1]) - 1: Linewidth, Alpha = 1.5, 1
                    else: Linewidth, Alpha = 1, 0.4
                    self.plot.canvas.ax[1].plot(Data.loc[:, 'CatchTime'], Data.loc[:, 'Current'], linewidth = Linewidth, color = result_color_dict[level], alpha = Alpha)
        self.plot.canvas.ax[1].set_ylabel('Current')
        self.plot.canvas.ax[1].set_xlabel('Time(sec)')
        self.plot.canvas.ax[1].set_title('截斷的訓練/測試資料', fontproperties = FontProperties(fname = "SimHei.ttf", size = 14))
        self.plot.canvas.figure.tight_layout()
        # self.plot.canvas.figure.subplots_adjust(top = 0.8, bottom = 0.3)#調整子圖間距
        self.plot.canvas.draw()


    def truncate(self, data, cshow, ctime):
        scan_data, trun1 = data.loc[:, cshow].values, 0
        for index, value in enumerate(scan_data):
            if (index > 0) and (value > self.config['trun']) and (value - scan_data[index - 1] > 0) and (scan_data[index + 1] - value > 0):
                trun1 = index
                break
        Input_data = data.loc[trun1 : (trun1 + self.config['cut_length'] - 1), :]
        Input_data.reset_index(drop = True, inplace = True)
        Input_data.loc[:, ctime] = Input_data.loc[:, ctime] - Input_data.loc[:, ctime].min()
        return Input_data    

def main():
    app = QApplication([])
    app.setStyle(QStyleFactory.create('fusion'))
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()