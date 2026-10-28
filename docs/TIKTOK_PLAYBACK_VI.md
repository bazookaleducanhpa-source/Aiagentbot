# Tool phát lại video TikTok

Script riêng chạy trên Windows bằng Python và Playwright. Nhận link video đầy đủ,
mở trình duyệt có cửa sổ và phát lại theo số lần yêu cầu. Log đo thời gian video
thực sự chạy, không phải số view được TikTok ghi nhận. Chưa xác minh khả năng tăng
view trên TikTok; không có cam kết tăng view.

Chạy PowerShell tại thư mục dự án:

```powershell
python -m pip install -r requirements-playback.txt
python -m playwright install chromium
python scripts/tiktok_playback.py "https://www.tiktok.com/@tenkenh/video/123456789" --repeat 3 --seconds 30 --ready
```

Thay link ví dụ bằng link video của bạn. Link rút gọn `vt.tiktok.com` hoặc
`vm.tiktok.com` cần mở trong trình duyệt để lấy link đầy đủ trước.

`--ready` tạm dừng ở lần đầu để bạn đóng hộp thoại hoặc đăng nhập nếu cần.
Sau đó nhấn Enter trong PowerShell. Video được phát tắt tiếng. Mỗi lần kết thúc
khi video hết hoặc đủ thời gian `--seconds`, rồi tải lại trang cho lần kế tiếp.
Trình duyệt dùng phiên tạm thời; đăng nhập không được lưu sau khi đóng.

- `--repeat`: số lần phát, mặc định 3.
- `--seconds`: thời gian phát tối đa mỗi lần, mặc định 30 giây.
- `--timeout`: thời gian chờ tải hoặc đứng hình, mặc định 60 giây.
- `--channel msedge`: dùng Edge đã cài, không cần tải Chromium.
- `--channel chrome`: dùng Chrome đã cài.
- `Ctrl+C`: dừng chạy.

Tool dừng với thông báo lỗi nếu không phát được video hoặc video đứng hình.
Nếu có yêu cầu xác minh, xử lý trực tiếp trong trình duyệt; script không tự giải.
Không tự chạy lượt xem vào video thật trong quá trình kiểm tra mã nguồn.

Tài liệu Playwright: https://playwright.dev/python/docs/library

## Phát thử YouTube

Script `scripts/youtube_playback.py` dùng cùng trình phát, hỗ trợ link Shorts,
`youtube.com/watch?v=...` và `youtu.be/...`:

```powershell
python scripts/youtube_playback.py "https://www.youtube.com/shorts/4jixNydSmBA" --channel msedge --repeat 3 --seconds 30
```

Log vẫn chỉ là số lần phát, không xác nhận view YouTube tăng. Tool không đo
Analytics hoặc giờ xem đủ điều kiện kiếm tiền. Thời gian quảng cáo không được
cộng vào thời gian phát đo được. Trình duyệt sẽ đóng sau khi hoàn thành.
