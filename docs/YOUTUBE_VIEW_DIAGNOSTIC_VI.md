# Kiểm tra cơ chế ghi nhận lượt xem YouTube

Ngày kiểm tra: 2026-10-08. Video: https://www.youtube.com/shorts/4jixNydSmBA

## Kết quả đo trực tiếp

Hai phép thử dùng Edge trên máy hiện tại, phiên mới chưa đăng nhập, không sửa
yêu cầu theo dõi, không đổi mạng hoặc giả danh nhiều người xem:

| Phép thử | Phát trực tiếp phần tử video như tool | Bấm trình phát YouTube |
| --- | --- | --- |
| ID video thực tế | 4jixNydSmBA | 4jixNydSmBA |
| Thời gian phát đo được | 30,10 giây | 29,65 giây, sau 2 giây chờ khởi động |
| `/api/stats/playback` | 1 phản hồi HTTP 204 | 1 phản hồi HTTP 204 |
| `/api/stats/watchtime` | 4 phản hồi HTTP 204 | 4 phản hồi HTTP 204 |
| Số view được xác nhận | Chưa đo được | Chưa đo được |

Lần thử qua nút phát cho thấy video dài 12,861 giây, bật lặp. Yêu cầu watchtime
chứa đúng ID video và các khoảng thời gian xem; khi hết video, khoảng thời gian
quay về đầu video. Tổng 30 giây không phải một lượt xem liên tục của video dài
30 giây. Script phát lặp trước đó không đại diện cho 10 người xem độc lập.

Có một số sự kiện `qoe`/`ptracking` báo `net::ERR_ABORTED` dù cũng quan sát được
phản hồi HTTP 204. Chưa xác định được ý nghĩa của các sự kiện này; không đủ căn
cứ để coi chúng là lý do view không tăng. Các sự kiện playback/watchtime được
theo dõi ở hai lần thử đều nhận phản hồi 204.

HTTP 204 chứng minh đã nhận phản hồi từ đầu nhận dữ liệu, không phải xác nhận
YouTube chấp nhận lượt phát thành view. Không có quyền truy cập Analytics của
chủ kênh và không có số đếm công khai trước/sau đáng tin cậy trong phép thử này.

## Điều tài liệu xác nhận

- Người xem chưa đăng nhập vẫn được đưa vào dữ liệu ước tính người xem. Thiếu
  đăng nhập không đủ để giải thích mọi lượt xem không được cộng.
  https://support.google.com/youtube/answer/7577916?hl=en
- YouTube xác minh tương tác bằng thuật toán, có thể trì hoãn hoặc điều chỉnh
  số đếm và loại lượt phát chất lượng thấp. Realtime chỉ là ước tính.
  https://support.google.com/youtube/answer/2991785?hl=en
- Views và Engaged views là các chỉ số khác nhau. Không có quy tắc được tài liệu
  này công bố rằng một lần phát Shorts đủ 30 giây tự động trở thành view hợp lệ.
  https://developers.google.com/youtube/analytics/metrics
- Lưu lượng bị nhận diện là nhân tạo không được tính.
  https://support.google.com/youtube/answer/3399767?hl=en
- Nghiên cứu năm 2024 trên dữ liệu 2021–2022 quan sát việc điều chỉnh số đếm theo
  đợt và có độ trễ. Đây không phải lịch xử lý hoặc công thức vượt lọc hiện tại.
  https://www.nature.com/articles/s41598-024-63649-w

## Kết luận và cách kiểm chứng tiếp

Không phát hiện khác biệt rõ ràng ở bước gửi playback/watchtime giữa cách tool
phát và bấm trình phát. Chưa tìm được thay đổi kỹ thuật nào đã được chứng minh
làm tăng view được công nhận. Giả thuyết cần phân biệt là xử lý số liệu chậm và
lượt phát bị loại ở phía máy chủ; các phản hồi HTTP hiện tại không phân biệt được.

Nếu là chủ kênh, ghi lại Views, Engaged views và thời gian cập nhật trong Studio
cho đúng video. Đối chiếu một lần xem tự nhiên với dữ liệu đã xử lý, thay vì tăng
số lần phát tự động. Không thể quy toàn bộ phần tăng cho phép thử nếu có người
xem khác trong cùng khoảng thời gian. YouTube không cung cấp lý do chấp nhận
hoặc loại riêng cho mỗi lượt xem qua các dữ liệu đã kiểm tra.

Nếu mục tiêu là đưa video tới người xem thật bằng quảng cáo, YouTube Promote là
công cụ chính thức. YouTube xác nhận view từ Promote là hợp lệ; thời gian xem và
người đăng ký từ quảng cáo không tính vào ngưỡng tham gia YPP. Không bảo đảm số
view cố định hoặc khả năng đề xuất tự nhiên:
https://support.google.com/youtube/answer/12199105?hl=en
