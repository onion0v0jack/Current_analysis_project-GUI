# 電流異常偵測GUI
# 銷售模型GUI設計
主要執行檔案：current_GUI_online.py
===
### ver 1.0
1. GUI 佈局：樹表格選單設定、表格顯示、圖片顯示、按鍵設定、檔案字動寫入與手動下載
2. 從Adam點位訊號及來自電流鉤表PPB蒐取的電流訊號，擷取電流資料。從訓練資料訓練模型之後，輸入測試資料並對其偵測異常程度。
3. 批次對輸入資料(全部)建立模型，遍歷全部參數組合並以RMSE為選擇模型參數的準則。建立模型之後預測。
4. 每一循環執行2. 3.等步驟。
