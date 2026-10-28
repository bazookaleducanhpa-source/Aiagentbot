# OmniVoice cục bộ

Đã cài ở `.tools/omnivoice-env` bằng Python 3.12.14, OmniVoice 0.2.1, Torch/Torchaudio 2.8.0+cpu và Transformers 5.20.2. Máy hiện tại chạy CPU, 8 luồng. Model nằm ở `.tools/omnivoice-model`; không tải lại mỗi lần đọc.

Nguồn chính thức: https://github.com/k2-fsa/OmniVoice

Model `k2-fsa/OmniVoice`, revision `c5fdb5ccb189668d56333f77ba2629f4cd7535f4`. Script `download_weights_http.py` kiểm tra SHA256 hai tệp trọng số sau khi tải. Dữ liệu và mã model tuân theo giấy phép đi kèm trong thư mục model.

Chạy từ thư mục workspace:

```powershell
rtk proxy .tools/omnivoice-env/Scripts/python.exe scripts/omnivoice_narrate.py --text "Vỏ tôm cứng như áo giáp. Vậy, ăn vỏ có bổ xương không?" --output output/omnivoice/preview.wav --steps 16 --speed 0.92
```

Thử nghiệm thực tế: tạo 13,72 giây âm thanh mất 64,3 giây xử lý, chưa tính 4,3 giây nạp model. CPU không tạo lời đọc theo thời gian thực.

`--instruct "male, young adult, moderate pitch"` dùng các thuộc tính mà engine hỗ trợ. Đoạn chỉ đạo cảm xúc tiếng Việt là hướng dẫn biên tập; không phải cú pháp điều khiển ngữ điệu được OmniVoice bảo đảm thực hiện. Để tạo nhịp kể: viết câu ngắn, đặt dấu câu, chia cụm thoại, thay đổi tốc độ nhẹ và chèn khoảng nghỉ khi dựng.

Đoạn tôm mới dùng `output/tom-mo-dau-omnivoice/produce.py`. Giọng tham chiếu được tạo từ chính OmniVoice; các cụm tiếp theo dùng lại để giữ người nói ổn định. Không dùng giọng của người dẫn video tham khảo. Bộ nhớ đệm WAV giúp chạy tiếp mà không phải tổng hợp lại các cụm đã xong.
