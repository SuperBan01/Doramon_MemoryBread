# 硬件总结

## 记忆面包录音卡片

### BOM

1. XIAO ESP32S3开发板，此开发板集成了microSD/TF 卡扩展，集成了麦克风录音，集成了摄像头（并未使用），SEEED 官方文档: https://wiki.seeedstudio.com/cn/xiao_esp32s3_getting_started/
2. microSD 卡，8G 容量
3. 3.7V 500mah 软包电池
4. 按键
5. LED
6. 面包板+杜邦线

### CODE 说明

1. `ESP32_recording`: 普通 ESP32 开发板录音example code
2. `ESP32_WIFI_connection`:   普通 ESP32 开发板WIFI 传输 example code
3. `XIAO_ESP32_button`: 使用 XIAO_ESP32S3 进行按键测试
4. `XIAO_ESP32_mic_rec_eg`: 使用 XIAO_ESP32S3 进行录音测试example code
5. `XIAO_REC`: 使用 XIAO_ESP32S3 进行录音
6. `XIAO_WIFI_connection`: 使用 XIAO_ESP32S3 进行 WIFI 传输（AP 模式）