# Nghiên cứu bổ sung: view và tim TikTok

Kiểm tra ngày 2026-10-08. Đây là đánh giá khả thi, chưa phải tool tăng tương tác đã hoạt động.

## Nguồn độc lập với Zefoy

- `pingwin010/tiktok-views-bot`, commit `1ff76ea35e52c750757c63736c55bfe0982ff9f1`:
  `ast.parse` báo `IndentationError: unexpected indent` tại dòng 121 của `demo.py`.
  Repo chỉ có README.md và demo.py; thiếu thư mục signer mà mã nhập. Không chạy mã này.
  Nguồn: https://github.com/pingwin010/tiktok-views-bot/tree/1ff76ea35e52c750757c63736c55bfe0982ff9f1
- `HkerVit/TikTok-Private-API`, commit `b2c1524184fabd3d5323494b25fc1f85edf00522`
  (2023-02-24): có hàm like dùng phiên đăng nhập và API riêng. File qua kiểm tra cú pháp,
  nhưng một số hàm gọi biến không được định nghĩa hoặc sai số đối số, gồm unlike_video.
  Các lỗi này không tự chứng minh like_video thất bại; chưa thử đăng nhập hoặc gửi like.
  Không có bằng chứng tương thích TikTok hiện tại hay số tim được ghi nhận.
  Nguồn: https://github.com/HkerVit/TikTok-Private-API/blob/b2c1524184fabd3d5323494b25fc1f85edf00522/api.py

Nghi vấn gán chuỗi vào requests.Session.cookies đã được kiểm tra riêng bằng dữ liệu giả:
prepare_request không báo lỗi trong môi trường hiện tại. Vì vậy không kết luận đây là lỗi
chặn chạy. Phép kiểm tra không gửi mạng và không xác nhận cookie đăng nhập hoạt động.

## API công khai

Danh sách scope công khai đã kiểm tra có quyền đọc video/thống kê và đăng video;
không có quyền được tài liệu hóa để cộng view hoặc thả tim. Điều này chỉ mô tả API
công khai được kiểm tra, không chứng minh mọi giao diện nội bộ đều không tồn tại.

https://developers.tiktok.com/docs/en/tiktok-api-scopes

## Kết luận và tiêu chí xác minh

Chưa tìm được triển khai đủ cơ sở để gọi là tool buff view và tim hoạt động.
Nhóm Zefoy phụ thuộc dịch vụ đã hiện nhãn chờ cập nhật trong lần thử trước;
hai nguồn độc lập ở trên chưa cung cấp bằng chứng thay thế khả dụng.

HTTP 200, số request gửi hoặc phát video thành công không chứng minh được cộng view.
Một thử nghiệm có ý nghĩa cần ghi nhận số liệu trước/sau và kiểm tra lại sau đó;
với tim cần kiểm tra trạng thái thích có tồn tại sau tải lại. Số đếm tăng đồng thời
vẫn có thể đến từ người xem tự nhiên, nên không đủ tự nó chứng minh tác dụng của tool.

Bằng chứng kiểm tra tĩnh được lưu ở `.tools/tiktok_feasibility/report.json`.
Không gửi yêu cầu tăng view/tim trong lần nghiên cứu bổ sung này.

## Kiểm tra bổ sung Zefame

Ngày 2026-10-08, đọc source hiện tại của AdamBankz/tiktok-viewbot:
https://github.com/AdamBankz/tiktok-viewbot/blob/main/main.py

Source gọi tên miền zefame-free.com để lấy cấu hình và gửi đơn; nhãn WORKING lấy
từ cờ available, SUCCESS lấy từ trường success của dịch vụ. Không có bước đọc lại
thống kê TikTok để xác minh đơn tạo ra tương tác. Đây là wrapper dịch vụ bên ngoài,
không phải mã nguồn cơ chế ghi nhận tương tác của TikTok.

Kiểm tra chỉ đọc trên máy:
- curl endpoint cấu hình thất bại: Could not resolve host.
- nslookup zefame-free.com qua DNS 1.1.1.1 trả Non-existent domain.
- curl https://www.tiktok.com/ cùng thời điểm trả HTTP 200.

Như vậy endpoint trong source không truy cập được từ môi trường kiểm tra; có thêm
bằng chứng DNS độc lập với resolver mặc định. Không kết luận dịch vụ không bao giờ
hoạt động trở lại hoặc mọi tên miền khác của nhà cung cấp đều ngừng hoạt động.
Không gửi đơn, không mua dịch vụ, không thử nhiều tài khoản.

## Lịch sử cập nhật, bản sửa và hai repo bổ sung

Kiểm tra tiếp ngày 2026-10-08:

- AdamBankz/tiktok-viewbot: HEAD `afba2882942d0493c1c86f5351b6f3d0090af26a`,
  2026-01-03, chỉ thêm ảnh vào README. Source tại HEAD vẫn gọi tên miền cũ.
  Issue #42 ngày 2026-01-25 hỏi endpoint order có còn khả dụng không; đây là
  phản ánh của người dùng, không tự nó là phép đo trạng thái hiện tại.
  https://github.com/AdamBankz/tiktok-viewbot/issues/42
- PR #45 sửa main.py: đọc diff cho thấy thêm timeout, bắt lỗi JSON và chỉnh thời
  gian chờ, nhưng không đổi tên miền backend và không thêm xác minh thống kê TikTok.
  PR đóng vì xóa repo nhánh nguồn ngày 2026-04-21, không được merge.
  https://github.com/AdamBankz/tiktok-viewbot/pull/45
- gavaita/Tiktok-View-Bot: HEAD `15da7bca296eedd3a5779e6c187cfda1aa6d7807`,
  2025-12-30. File tiktok-bot.py qua kiểm tra cú pháp, nhưng vẫn gọi cùng endpoint
  Zefame; không có bước đọc lại view_count/like_count. Không phải backend thay thế.
  README có nói view đôi khi bị gỡ, nhưng không có phép thử có thể tái lập để chứng
  minh tác dụng hiện tại. Không coi cam kết không bị ban trong README là bảo đảm.
  https://github.com/gavaita/Tiktok-View-Bot/tree/15da7bca296eedd3a5779e6c187cfda1aa6d7807
- hiddenexee/TikTok-Live-Like: HEAD `053b529015206886c4418780527596bb7c80c1bd`,
  2026-08-02. Tree chỉ có README.md, .gitignore và .gitattributes; không có mã bot
  công khai. README nhắc LIVE, nên cũng không chứng minh thả tim video thường.
  https://github.com/hiddenexee/TikTok-Live-Like/tree/053b529015206886c4418780527596bb7c80c1bd

Metadata và source được lưu ở `.tools/tiktok_followups/`. Chỉ tải văn bản và phân
tích cú pháp, không nhập hoặc chạy code repo. Trong các nguồn bổ sung này chưa tìm
được endpoint thay thế hoặc bằng chứng tương tác được TikTok ghi nhận hiện tại.
