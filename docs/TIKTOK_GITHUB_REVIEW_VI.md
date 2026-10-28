# Rà soát source GitHub buff view TikTok

Ngày kiểm tra: 2026-10-08. Đọc README, mã Python và metadata GitHub; không chạy mã
repo, không tải EXE và không gửi yêu cầu buff view trong lần rà soát này.

## Các repo đã đọc

### xtekky/TikTok-ViewBot

https://github.com/xtekky/TikTok-ViewBot

Commit được kiểm tra: `0073d8fa06c79306084acb123b19bf4776ed0988`.
Commit mới nhất ngày 2026-09-15 cập nhật README, không chứng minh mã bot được sửa.
Các issue gần đây trong mẫu kiểm tra phần lớn chỉ đăng link, không đủ để xác
nhận tool đang hoạt động.

File `v2.py` tự động thao tác dịch vụ Zefoy bằng Selenium, phụ thuộc thêm một
dịch vụ bên ngoài xử lý CAPTCHA. Bộ đếm `sent` đếm số lần gửi, không phải view
TikTok được công nhận. README nhắc `viewbot.py`, nhưng không có file này trong
danh sách gốc đã kiểm tra. `requirements.txt` thiếu Selenium và webdriver-manager
mà `v2.py` nhập, nên hướng dẫn cài đặt hiện tại không khớp file này.

https://github.com/xtekky/TikTok-ViewBot/blob/0073d8fa06c79306084acb123b19bf4776ed0988/v2.py

### xtekky/zefoy

https://github.com/xtekky/zefoy

Commit được kiểm tra: `68e333d2ff343a233e98acd4c3d8f367518de7bb`.
Commit mới nhất ngày 2026-09-15 chỉ sửa định dạng README. `main.py` dùng Selenium
và undetected_chromedriver, mở Zefoy, chờ người dùng nhập CAPTCHA, gửi link rồi
lặp thao tác theo cooldown. Không phải một triển khai độc lập của hệ thống
ghi nhận view TikTok. Vòng chờ phần tử không có hạn thời gian; bộ chọn XPath
phụ thuộc chặt vào cấu trúc HTML của Zefoy. Nhãn WORKS chỉ kiểm tra nút có được
enable hay không, không kiểm tra TikTok cộng view.

https://github.com/xtekky/zefoy/blob/68e333d2ff343a233e98acd4c3d8f367518de7bb/main.py

### Kenokey/Tiktok-Zefoy-Generator

https://github.com/Kenokey/Tiktok-Zefoy-Generator

Commit được kiểm tra: `0c028a002eeaa84440a4703b3fe91e18ff68d682`, ngày 2025-05-20.
`main.py` dùng Chrome Selenium để thao tác Zefoy; có kiểm tra timeout và bộ chọn
dành cho bố cục có quảng cáo. Phụ thuộc CAPTCHA, bố cục và trạng thái dịch vụ.
Trong file đã đọc không thấy thao tác tự đọc cookie tài khoản TikTok hoặc tải
EXE, nhưng đây không phải chứng nhận an toàn toàn bộ repo và phụ thuộc.

Issue #7 báo lỗi chờ phần tử khi tải trang tháng 4/2025; hiện đã đóng. Lỗi lịch
sử này không chứng minh phiên bản hiện tại hỏng hoặc đã hoạt động thành công.
Một lần lấy `requirements.txt` thất bại do kết nối bị đóng; chưa đánh giá được
đầy đủ phiên bản phụ thuộc trong file đó.

https://github.com/Kenokey/Tiktok-Zefoy-Generator/issues/7

### DikeMothDive/TiktokViewerBot

https://github.com/DikeMothDive/TiktokViewerBot

Commit được kiểm tra: `6d07133d718884a334d5b5f4d2347602f427412f`.
README hướng dẫn chạy EXE, cấp quyền Administrator và bỏ qua SmartScreen.
Nhưng `tktk.py` thực tế là mã nhận telemetry UDP của trò chơi Forza Motorsport,
không phải mã tăng view TikTok. Đây là sự không khớp rõ ràng giữa quảng cáo và
mã nguồn; không đủ cơ sở tin rằng EXE được phát hành xây từ source được công bố.
Không kết luận EXE chứa malware vì chưa phân tích binary.

https://github.com/DikeMothDive/TiktokViewerBot/blob/6d07133d718884a334d5b5f4d2347602f427412f/tktk.py

## Kiểm tra dịch vụ phụ thuộc

Mở `https://zefoy.com` bằng Edge Playwright thông thường, không sửa dấu hiệu
trình duyệt hoặc giải CAPTCHA. Trang trả HTTP 200, tiêu đề `Zefoy - Official`,
hiện yêu cầu nhập từ trong ảnh. Điều này xác nhận trang đầu truy cập được từ
máy hiện tại, không xác nhận chức năng Views khả dụng hoặc TikTok sẽ cộng view.

## Đánh giá

Ba repo đầu có source thao tác Zefoy thật và khác với script phát lặp đã viết.
Chúng phụ thuộc dịch vụ bên ngoài; không cho biết dịch vụ tạo view bằng cơ chế
nào, và số lần gửi thành công không đủ để chứng minh view được công nhận.
Chưa có repo nào trong bốn repo được xác minh tăng view trong lần rà soát này.
Kenokey là ứng viên có mã thao tác Selenium thông thường để nghiên cứu tiếp;
không nên coi đây là xác nhận có hiệu quả hoặc bảo đảm an toàn.

## Lần thử sau khi người dùng hoàn thành CAPTCHA

Đã cài phụ thuộc trong `.tools/kenokey-env`, dùng source Kenokey ở commit nêu
trên và wrapper giới hạn một lần gửi. Bước tải ChromeDriver bị timeout, nên
wrapper dùng Chrome qua Playwright, giữ luồng chọn dịch vụ và các selector của
repo. Đây là bản thử đã điều chỉnh, không phải chạy nguyên bản không thay đổi.

Người dùng đã hoàn thành CAPTCHA. Ảnh chụp trang sau đó cho thấy menu dịch vụ;
mục **Views** hiện nhãn đỏ **soon will be update**. Followers, Hearts và Shares
cũng mang nhãn này, còn Comments Hearts và Favorites mang nhãn khác.

Bản wrapper ban đầu tìm chữ Views bên trong nút, trong khi đó là tiêu đề nằm
ngoài nút. Điều kiện sai khiến nó chờ hết năm phút và đóng phiên, báo nhầm là
CAPTCHA chưa hoàn thành. Đã sửa điều kiện nhận diện menu và bổ sung kiểm tra nhãn
dịch vụ trước khi gửi. Không chạy lại hoặc yêu cầu người dùng nhập CAPTCHA lại
chỉ để lặp bước kiểm tra nhãn vừa quan sát được.

Kết quả thực tế: **chưa gửi yêu cầu Views, chưa xác nhận view tăng**. Nhãn trên
giao diện cho thấy chức năng Views đang chờ cập nhật; chưa có bằng chứng dịch vụ
này khả dụng trong lần kiểm tra. Đổi sang hai repo xtekky vẫn phụ thuộc cùng
dịch vụ Zefoy, nên chưa có cơ sở xem việc đổi wrapper là giải pháp.
