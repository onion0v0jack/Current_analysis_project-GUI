import pywt 
import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
import time
import os
from PySide2.QtCore import *
from PySide2.QtWidgets import *
from PySide2.QtGui import *

import clr
# import C# dll
cwd = os.getcwd()
dllPath = os.path.join(cwd, 'bin', 'SMB.iot.current.dll')
clr.AddReference(dllPath)
from SMB.iot.current import *

class WorkThread_generate_data(QThread):
    signal_detail_list = Signal(list)   # 送出的Signal定義，內部使用直接用self.test_output_message
    signal_train_ready = Signal(str)
    signal_th1_to_table_2 = Signal(pd.DataFrame)
    signal_filename_list_th1_to_GUI = Signal(list)  #傳送filename list到GUI

    def __init__(self, config):#, iot_switch):
        super().__init__()
        self.config = config

        self.id = config['id']
        self.ip = config['ip']
        self.input_path = config['Input data path']
        self.folder_name = config['Folder name']
        self.freq = config['Freq']
        self.Ntrain = config['Ntrain']
        self.cut_length = config['cut_length']

        # self.iot_switch = None #iot_switch  # (模擬iot點位觸發訊號)

        self.pause = False
        self.stopped = False

        self.isStart, self.isEnd = False, False
        self.file_number = 1
        self.start_point, self.end_point, self.start_time, self.end_time = 0, 0, 0, 0
        self.show_data_detail = []
        self.filename_list = [[], []]
        self.table2_from_th1 = pd.DataFrame(columns = ['id', 'Result'])

        self.th2_work = None
        self.train_data_enough = False

        self.adam = self.connectAdam()
    
    def run(self):
        self.output_data_path = f'{self.folder_name}/data'
        if not os.path.isdir(self.folder_name): os.mkdir(self.folder_name)
        if not os.path.isdir(self.output_data_path): os.mkdir(self.output_data_path)

        while True:
            # 當按下中斷時，強制結束，並回復初始(TODO)
            if self.stopped == True:
                print('Thread1 stopped2.')
                self.stopped = False
                return
            # 當按下暫停/繼續時，外部切換self.pause決定是否進入無限暫停迴圈
            # 按下暫停之後按下中斷，達到全部中斷的效果
            while self.pause:
                if self.stopped == True:
                    print('Thread1 stopped1.')
                    return
                time.sleep(0)

            # 程式內容執行於此
            self.iot_switch = self.adam.shot_di
            print(self.iot_switch)
            if self.iot_switch == '1': # (測試模擬射出開始)
                if self.isStart == False:
                    self.start_point = sum(1 for line in open(self.input_path))
                    self.start_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                    self.isStart, self.isEnd = True, False
            elif (self.iot_switch == '0' and (self.start_point > 0)): # (測試模擬射出結束)
                if self.isEnd == False:
                    self.end_point = sum(1 for line in open(self.input_path))
                    self.end_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                    print('區段資料筆數: {}    開始時間: {}   結束時間: {}'.format(self.end_point - self.start_point, self.start_time, self.end_time))
                    self.isStart, self.isEnd = False, True

                    # 載入部分資料
                    Data = pd.read_table(self.input_path, sep = ',')
                    Data = Data[['TimeStamp', ' Current']]

                    # 擷取部分資料並下載
                    SubData = Data.loc[self.start_point:(self.end_point - 1), :]
                    SubData.reset_index(drop = True, inplace = True)
                    SubData.loc[:, 'Time'] = range(SubData.shape[0])
                    SubData.loc[:, 'Time'] = SubData.loc[:, 'Time']/self.freq
                    SubData = SubData[['Time', ' Current']].rename(columns = {"Time": "CatchTime", " Current":"Current"})
                    SubData.to_csv(f'{self.output_data_path}/{str(self.file_number).zfill(4)}.txt', index = False)

                    self.show_data_detail = [str(self.file_number).zfill(4), self.start_time, self.end_time, self.end_point - self.start_point]
                    self.signal_detail_list.emit(self.show_data_detail)   # 發送信號，需要同物件定義(在此為list)
                    if (self.file_number <= self.Ntrain) and (self.train_data_enough == False):
                        self.filename_list[0].append(str(self.file_number).zfill(4))
                        self.signal_filename_list_th1_to_GUI.emit([self.filename_list] + [])
                        if len(SubData) < self.cut_length:
                            self.signal_train_ready.emit(f'擷取資料過短，建議停止運作')
                        if self.file_number == self.Ntrain:
                            self.signal_train_ready.emit(f'已收取{self.Ntrain}組訓練資料')
                            self.th2_work = WorkThread_anomaly_detection(self.config) # 建立執行緒th2
                            self.th2_work.signal_fileID_and_result.connect(self.slot_show_result)
                            self.th2_work.set_begin_training(self.filename_list)
                            self.th2_work.start()
                            self.train_data_enough = True

                    elif (self.file_number > self.Ntrain) and (self.train_data_enough == True):
                        self.filename_list[1].append(str(self.file_number).zfill(4))
                        self.th2_work.set_begin_training(self.filename_list)
                    self.file_number += 1
            else:
                pass
        
    def slot_show_result(self, message):
        print(f'輸出temp {message[0]}')
        print(f'輸出self.test_result {message[1]}')
        if len(message[1]) > 0:  # 測試時期
            self.table2_from_th1.loc[-1] = message[1]
            self.table2_from_th1.index = self.table2_from_th1.index + 1
            self.table2_from_th1 = self.table2_from_th1.sort_index()
            self.signal_th1_to_table_2.emit(self.table2_from_th1)
        else: pass

        self.signal_train_ready.emit(f'收取測試資料並判斷異常')
        self.signal_filename_list_th1_to_GUI.emit(message)

    def connectAdam(self):
        adam = clsCurrent()
        adam.Adam_id = self.id
        adam.Adam_speed = 500
        adam.Adam_ip = self.ip
        adam.run_getdi()
        adam.isActive = True
        return adam

class WorkThread_anomaly_detection(QThread):
    signal_fileID_and_result = Signal(list)  # 送出信號範例 
    def __init__(self, config):
        super().__init__()
        
        self.id = config['id']
        self.ip = config['ip']
        self.input_path = config['Input data path']
        self.folder_name = config['Folder name']
        self.freq = config['Freq']
        self.Ntrain = config['Ntrain']
        self.trun = config['trun']
        self.cut_length = config['cut_length']
        self.BCEV = config['BCEV']

        self.output_data_path = f'{self.folder_name}/data'
        self.cshow, self.ctime = 'Current', 'CatchTime'
        self.filename_list = None
        self.waited = False
        self.pca_model_list, self.MSE_thres_List = [], []
        self.test_draw_n = 4
        self.test_result = []   # 輸出

        self.pause, self.stopped = False, False
    
    def run(self): 
        
        bind_data_list, ylabel_list = [], []
        while True:
            # 按下中斷
            if self.stopped == True:
                print('Thread2 stopped2.')
                self.stopped = False
                return
            # 按下暫停/繼續
            while self.pause:
                if self.stopped == True:
                    print('Thread2 stopped1.')
                    return
                time.sleep(0)
        
            # 程式內容寫在這裡
            if self.waited == False:
                if len(self.filename_list[1]) == 0:  # 剛收完訓練資料時，要開始建立模型
                    temp = [self.filename_list[0]] + [self.filename_list[1]]
                    print("th2已經收到最後一筆訓練資料")
                    if 2>1:
                        try:
                            D1_bind, D2_bind, D3_bind, D4_bind, A4_bind = None, None, None, None, None
                            for count, idname in enumerate(self.filename_list[0]):
                                Data = pd.read_table('{}/{}.txt'.format(self.output_data_path, idname), sep = ',')
                                Data = Data[[self.ctime, self.cshow]]
                                Data = self.truncate(Data, self.cshow, self.ctime)

                                X = Data.loc[:, self.cshow].values
                                X_mean, X_std = X.mean(), X.std()
                                Data.loc[:, 'Normalized_Current'] = (X - X_mean)/X_std

                                cD1, cD2, cD3, cD4, cA4 = self.dwt_split(Data, column = 'Normalized_Current', waveletname = 'db1')
                                if count == 0: 
                                    D1_bind, D2_bind, D3_bind, D4_bind, A4_bind = cD1, cD2, cD3, cD4, cA4
                                else: 
                                    D1_bind = np.column_stack((D1_bind, cD1))
                                    D2_bind = np.column_stack((D2_bind, cD2))
                                    D3_bind = np.column_stack((D3_bind, cD3))
                                    D4_bind = np.column_stack((D4_bind, cD4))
                                    A4_bind = np.column_stack((A4_bind, cA4))
                                
                            model_rerun_counter, n_pc = 0, 4
                            while model_rerun_counter < 2:                
                                #對各分解小波訓練各自的PCA模型，注意餵進去的資料是訓練集
                                pca_D1, pca_D2, pca_D3, pca_D4, pca_A4 = PCA(n_components = n_pc), PCA(n_components = n_pc), PCA(n_components = n_pc), PCA(n_components = n_pc), PCA(n_components = n_pc)
                                pca_D1.fit(D1_bind)
                                pca_D2.fit(D2_bind)
                                pca_D3.fit(D3_bind)
                                pca_D4.fit(D4_bind)
                                pca_A4.fit(A4_bind)

                                if model_rerun_counter == 1: print('各通道PCA模型完成。\n')

                                bind_data_list, self.pca_model_list = [D1_bind, D2_bind, D3_bind, D4_bind, A4_bind], [pca_D1, pca_D2, pca_D3, pca_D4, pca_A4]
                                ylabel_list, pca_cum_explain_var_list = ['D1', 'D2', 'D3', 'D4', 'A4'], []

                                if model_rerun_counter == 1: print('各主成分解釋變量累積比例:')
                                for point in range(len(self.pca_model_list)):
                                    pca_cum_explain_var_list.append(self.pca_model_list[point].explained_variance_ratio_.cumsum())
                                    if model_rerun_counter == 1: 
                                        print('pca_{}: {}'.format(ylabel_list[point], self.pca_model_list[point].explained_variance_ratio_.cumsum()))
                                if model_rerun_counter == 1: print('*'*50)

                                for pc in range(1, n_pc + 1):
                                    if np.sum(np.array([channel[pc - 1] for channel in pca_cum_explain_var_list]) >= self.BCEV) == 5:
                                        n_pc = pc
                                        break

                                if model_rerun_counter == 1:
                                    cum_val_pass = sum([pca_model.explained_variance_ratio_.cumsum()[-1] > self.BCEV for pca_model in self.pca_model_list])
                                    if cum_val_pass < 5: print(f'目前主成分個數 {n_pc}，尚有通道的累積解釋變異不足{int(self.BCEV*100)}%，建議增加主成分個數。\n')
                                    else: print(f'目前主成分個數: {n_pc}，各通道的累積解釋變異超過{int(self.BCEV*100)}%，可做後續分析。\n')
                                
                                model_rerun_counter += 1
                        except Exception as e:
                            print('建立模型發生錯誤，錯誤訊息：')
                            print(e)
                        else:
                            self.MSE_thres_List = self.train_MSE_plot(bdl = bind_data_list, tfl = self.filename_list[0], pcal = self.pca_model_list, ylabell = ylabel_list)
                            print(f'MSE各通道閥值{self.MSE_thres_List}')
                            print('模型建立完成')    #self.pca_model_list
                else:                                # 建立完模型之後收測試資料
                    # 在測試時期，temp輸出要畫的train/test file id，其中測試資料限制個數為self.test_draw_n
                    if len(self.filename_list[1]) > self.test_draw_n: # 維持test file id的數量
                        temp = [self.filename_list[0]] + [self.filename_list[1][-self.test_draw_n:]]
                    else:
                        temp = [self.filename_list[0]] + [self.filename_list[1]]
                    
                    # 進入測試模式
                    print("th2收到測試資料")
                    Test_Data = pd.read_table('{}/{}.txt'.format(self.output_data_path, temp[1][-1]), sep = ',')
                    Test_Data, channel_MSE_list = Test_Data[[self.ctime, self.cshow]], np.zeros(5)

                    try:
                        Test_Data = self.truncate(Test_Data, self.cshow, self.ctime)
                    except:
                        self.test_result = [temp[1][-1], 'Error']     #【】
                        print(f'{temp[1][-1]}     資料無法被截斷，此資料無法被測試')
                    else:
                        if Test_Data.shape[0] != self.cut_length:
                            self.test_result = [temp[1][-1], 'Error']     #【】
                            print(f'{temp[1][-1]}     截斷後資料長度過短，此資料無法被測試')
                        else:
                            X = Test_Data.loc[:, self.cshow].values
                            X_mean, X_std = X.mean(), X.std()
                            Test_Data.loc[:, 'Normalized_Current'] = (X - X_mean)/X_std

                            cD1, cD2, cD3, cD4, cA4 = self.dwt_split(Test_Data, column = 'Normalized_Current', waveletname = 'db1')
                            new_data_list = [cD1, cD2, cD3, cD4, cA4]
                            model_test_rerun_counter = 0   #在有限時間內，偵測測試資料是否真的出現運算錯誤。若有，就跑兩次。若還是有就算了。
                            while model_test_rerun_counter < 2:
                                try:
                                    #丟入PCA模型並預測，計算MSE
                                    for point in range(len(bind_data_list)):
                                        Real = bind_data_list[point].copy()
                                        Real[:, -1] = new_data_list[point] #訓練資料的最後一欄位改成測試資料即可預測
                                        Pred = self.pca_model_list[point].inverse_transform(self.pca_model_list[point].fit_transform(Real))
                                        channel_MSE_list[point] = np.mean((Real[:, -1] - Pred[:, -1])**2, axis = 0)
                                except:
                                    self.test_result = [temp[1][-1], 'Error']     #【】
                                    print(f'{temp[1][-1]}     此資料在模型中運算出現錯誤，故無法偵測。')
                                    model_test_rerun_counter += 1
                                else:
                                    #計算嚴重程度，顯示出來並加入測試記錄檔
                                    anomaly_rank = sum(channel_MSE_list > self.MSE_thres_List)
                                    if anomaly_rank >= 2: 
                                        self.test_result = [temp[1][-1], f'Anomaly_{anomaly_rank}']     #【】
                                        print(f'{temp[1][-1]}     超出閥值通道數為{anomaly_rank}，超出標準，故判斷為異常資料')
                                    else: 
                                        self.test_result = [temp[1][-1], 'Normal']     #【】
                                        print(f'{temp[1][-1]}     判斷為正常資料')
                                    model_test_rerun_counter = 2
                # print(temp)        #【輸出】
                # print(self.test_result)      #【輸出】
                self.signal_fileID_and_result.emit([temp] + [self.test_result])
                self.waited = True
            else: pass
            time.sleep(1)


    def truncate(self, data, cshow, ctime):
        scan_data, trun1 = data.loc[:, cshow].values, 0
        for index, value in enumerate(scan_data):
            if (index > 0) and (value > self.trun) and (value - scan_data[index - 1] > 0) and (scan_data[index + 1] - value > 0):
                trun1 = index
                break
        Input_data = data.loc[trun1 : (trun1 + self.cut_length - 1), :]
        Input_data.reset_index(drop = True, inplace = True)
        Input_data.loc[:, ctime] = Input_data.loc[:, ctime] - Input_data.loc[:, ctime].min()
        return Input_data

    def dwt_split(self, data, column, waveletname):
        data = data.loc[:, column].values
        (cA1, cD1) = pywt.dwt(data, waveletname)
        (cA2, cD2) = pywt.dwt(cA1, waveletname)
        (cA3, cD3) = pywt.dwt(cA2, waveletname)
        (cA4, cD4) = pywt.dwt(cA3, waveletname)
        return cD1, cD2, cD3, cD4, cA4

    def train_MSE_plot(self, bdl, tfl, pcal, ylabell): 
        new_MESthres = []
        for point in range(len(bdl)):
            MSE_series = np.zeros(len(tfl))
            Real = bdl[point][:, 0:len(tfl)] 
            Pred = pcal[point].inverse_transform(pcal[point].fit_transform(Real))
            for iterate in range(len(tfl)):
                MSE_series[iterate] = np.mean((Real[:, iterate] - Pred[:, iterate])**2, axis = 0)
            new_MESthres.append(np.mean(MSE_series) + np.std(MSE_series))
        return new_MESthres
    
    def set_begin_training(self, filename_list):
        # filename_list = [['0001', '0002', '0003', '0004', '0005'], ['0006', '0007', '0008']]
        self.filename_list = filename_list.copy()
        self.waited = False