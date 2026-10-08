# Hướng dẫn làm và phát triển kênh video 3D thiếu nhi

Cập nhật: 08/10/2026. Dành cho dự án `E:\DucAnh_PA\Aigent`.

Hướng dẫn bằng tiếng Việt; nội dung, tiêu đề và bài hát trong video dùng tiếng Anh. Bao gồm thiết lập dự án, nghiên cứu, tạo video, ghép nhạc, đăng YouTube/TikTok và lấy những lượt xem đầu tiên.

## 1. Định dạng video đã chọn

| Thành phần | Thiết lập |
|---|---|
| Hình ảnh | Hoạt hình 3D, con vật dễ thương, màu sáng |
| Khung hình | Dọc 9:16, bản hiện tại 720 × 1280, 30 fps |
| Thời lượng | 30 giây, 6 cảnh |
| Chuyển cảnh | Khoảng 5 giây đổi con vật và bối cảnh |
| Âm thanh | Bài hát thiếu nhi tiếng Anh có sẵn |
| Giọng kể và chữ | Không có |
| Nền tảng | YouTube Shorts và TikTok |

Bản đã đăng: cá mập dưới biển → thỏ ở đồng hoa → chim cánh cụt trên băng → voi ở thảo nguyên → khỉ trong rừng → vịt ở ao. Nhạc: **Old MacDonald — The Green Orbs**.

- [Video YouTube](https://www.youtube.com/watch?v=0IVRyyEV4Io)
- [Video TikTok](https://tiktok.com/@dreamforgestories36/video/7694239727154744583)
- File hoàn chỉnh: `data/animal-dance/video.mp4`.
- Hình tổng hợp 6 cảnh: `data/animal-dance/contact-sheet.jpg`.

Điểm nên cải thiện ở video tiếp theo: lời Old MacDonald nói về động vật trang trại, trong khi hình hiện tại có cả cá mập và chim cánh cụt. Chọn con vật khớp lời hát sẽ làm nội dung liền mạch hơn.

## 2. Công cụ và tài khoản cần có

| Công cụ | Công việc | Cần cho cách làm hiện tại? |
|---|---|---|
| Trợ lý trong cuộc trò chuyện | Nghiên cứu, lên ý tưởng, viết prompt, hỗ trợ dựng/đăng | Có |
| Google Flow | Tạo các clip 3D có chuyển động | Có |
| Python + FFmpeg | Cắt clip, nối cảnh, ghép nhạc | Có |
| Google Cloud + OAuth YouTube | Cho phép dự án upload YouTube | Có |
| Buffer | Gửi video tự động sang TikTok | Có, nếu đăng tự động |
| Cloudinary | Cung cấp URL MP4 để Buffer tải | Có, nếu đăng qua Buffer |
| Apify | Lấy metadata/video tham khảo TikTok | Tùy lần nghiên cứu |
| Groq | Hỗ trợ kiểm tra lời bài hát trong script kiểm tra hiện tại | Tùy chọn |

Luồng này không cần tạo nhạc mới, ElevenLabs hay gọi API tạo hình/giọng OpenAI. Tuy nhiên, nút tạo video **live** trong ứng dụng web vẫn dùng pipeline API riêng của dự án; nó không tự điều khiển Google Flow.

## 3. Cài và mở dự án lần đầu

Mở PowerShell. Máy cần Python 3.11 trở lên.

```powershell
Set-Location -LiteralPath 'E:\DucAnh_PA\Aigent'
./start.ps1
```

Script tạo `.venv`, cài dependencies và mở server. Truy cập:

```text
http://127.0.0.1:8000
```

Giữ cửa sổ PowerShell này mở nếu dùng ứng dụng hoặc hàng đợi đăng bài cục bộ. Dùng cửa sổ PowerShell thứ hai cho các lệnh bên dưới. Ctrl+C để dừng server.

Nếu máy đã cài dependencies, có thể mở server trực tiếp:

```powershell
& .\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Chạy một tiến trình server, không thêm `--workers` hoặc `--reload` khi đang dựng/đăng. Nếu cần kiểm tra luồng giao diện mà chưa gọi dịch vụ thật, dùng `APP_MODE=demo`; demo không tạo video 3D bằng Flow và không đăng bài thật.

Các lệnh trong hướng dẫn là lệnh PowerShell thông thường. Quy tắc RTK dành cho trợ lý có thể thực hiện bằng cách bọc lệnh trong `rtk proxy powershell -NoProfile -Command "..."`.

## 4. Cấu hình `.env`

Máy hiện tại đã có `.env`; **không chép đè**. Nếu thiết lập trên máy mới và chưa có file:

```powershell
if (-not (Test-Path -LiteralPath '.env')) {
    Copy-Item -LiteralPath '.env.example' -Destination '.env'
}
```

Điền giá trị thật bằng trình soạn thảo trên máy:

```dotenv
APP_MODE=live
YOUTUBE_API_KEY=your_key_for_research
YOUTUBE_CLIENT_ID=filled_by_oauth_helper
YOUTUBE_CLIENT_SECRET=filled_by_oauth_helper
YOUTUBE_REFRESH_TOKEN=filled_by_oauth_helper
TIKTOK_PUBLISHER=buffer
BUFFER_API_KEY=your_buffer_key
BUFFER_TIKTOK_CHANNEL_ID=your_tiktok_channel_id
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_cloudinary_key
CLOUDINARY_API_SECRET=your_cloudinary_secret
APIFY_API_TOKEN=your_optional_apify_token
APIFY_MAX_CHARGE_USD=0.5
GROQ_API_KEY=your_optional_groq_key
```

Không gửi `.env`, OAuth JSON hoặc token lên chat công khai/Git. Khởi động lại server sau khi sửa `.env`.

`APIFY_MAX_CHARGE_USD=0.5` là mức trần được cấu hình cho mỗi run trong phần nghiên cứu, không phải mỗi lần luôn mất đúng 0,5 USD. Xem chi phí thực tế trong Apify Console; nhiều run vẫn có thể cộng dồn chi phí.

## 5. Kết nối YouTube

Nếu đã đăng thành công như máy hiện tại, không cần kết nối lại trừ khi token lỗi.

Trên máy mới:

1. Mở [Google Cloud Console](https://console.cloud.google.com/), tạo/chọn project.
2. Bật **YouTube Data API v3**.
3. Cấu hình OAuth consent; nếu ở Testing, thêm tài khoản của bạn vào Test users.
4. Tạo OAuth client loại **Desktop app**, tải JSON.
5. Lưu JSON tại `data/google-client.json` hoặc chỉ định đường dẫn thật khi chạy helper.
6. Chạy:

```powershell
& .\.venv\Scripts\python.exe scripts/connect_youtube.py --client-file 'data/google-client.json'
```

Với JSON hiện có trên máy của bạn:

```powershell
& .\.venv\Scripts\python.exe scripts/connect_youtube.py --client-file 'E:\DucAnh_PA\Aigent\data\client_secret_73092399946-3d8up4ohsthvi8grduvcp1ghli5o4qgc.apps.googleusercontent.com.json'
```

Đăng nhập đúng tài khoản/kênh và cấp quyền upload. Khi thấy **YouTube authorization received. You can close this browser tab.**, helper đã nhận phản hồi; chờ PowerShell báo lưu credentials rồi khởi động lại server.

API key dùng nghiên cứu; OAuth cấp quyền đăng. Hai loại này không thay thế nhau. [Tài liệu OAuth chính thức](https://developers.google.com/youtube/v3/guides/auth/installed-apps).

## 6. Kết nối TikTok qua Buffer

1. Trong [Buffer](https://buffer.com/), kết nối đúng tài khoản TikTok.
2. Kiểm tra kênh có thể đăng **Automatic**, không chỉ nhắc đăng bằng điện thoại.
3. Tạo/lấy API key nếu tài khoản có quyền API, lưu vào `BUFFER_API_KEY`.
4. Liệt kê các kênh:

```powershell
& .\.venv\Scripts\python.exe scripts/list_buffer_channels.py
```

5. Lấy `channel_id` ở dòng `tiktok`, lưu vào `BUFFER_TIKTOK_CHANNEL_ID`.
6. Tạo/chọn môi trường Cloudinary và lưu cloud name, API key, API secret vào `.env`.

Khi đăng, dự án upload MP4 lên Cloudinary, lấy URL HTTPS công khai rồi gửi Buffer. Không xóa file trên Cloudinary trước khi Buffer tải và đăng xong. Adapter đăng TikTok trực tiếp bằng TikTok Content Posting API chưa được triển khai trong dự án này. [Ví dụ đăng video của Buffer](https://developers.buffer.com/examples/create-video-post.html).

Chi tiết thiết lập tài khoản nằm trong [API_SETUP_VI.md](API_SETUP_VI.md). Tên menu và quyền truy cập có thể thay đổi theo dịch vụ/tài khoản.

## 7. Nghiên cứu trước khi làm video

Tìm các từ khóa tiếng Anh như `cute animal dance`, `3D nursery rhymes`, `kids animal song`, `Old MacDonald animation`.

Ghi lại khoảng 5–10 video phù hợp:

| Cần quan sát | Câu hỏi |
|---|---|
| Giây đầu | Có chuyển động và âm nhạc ngay không? |
| Nhịp dựng | Bao lâu đổi cảnh/con vật? |
| Hình ảnh | Con vật có rõ, dễ thương, nhất quán không? |
| Nhạc | Lời bài hát có khớp hành động không? |
| Kết thúc | Có nối tự nhiên về đầu không? |
| Số liệu | Ngày đăng, views, lượt thích, các lần đo tiếp theo |

Một video có hàng triệu lượt xem tích lũy không tự chứng minh nó đang nổi hôm nay. Quan sát thêm sau một khoảng thời gian để biết tốc độ tăng.

Nếu cần lấy một video tham khảo qua Apify:

```powershell
& .\.venv\Scripts\python.exe scripts/fetch_tiktok_reference.py 'https://www.tiktok.com/@creator/video/VIDEO_ID'
```

Thay URL bằng link thật. Helper này gọi Apify và tải bản tham khảo khi actor trả được file; nó lưu trong `data/references/<video-id>/`. Dùng để phân tích bố cục và nhịp dựng, rồi tạo cảnh mới của mình.

## 8. Chọn bài hát trước, lên cảnh sau

Chọn bài quen thuộc rồi nghe đoạn 30 giây định dùng. Ví dụ Old MacDonald, Wheels on the Bus, If You're Happy and You Know It, hoặc Baby Shark nếu có quyền sử dụng bản thu phù hợp.

Lập bảng thời gian trước khi tạo clip:

| Thời gian | Hình ảnh cần tạo | Hành động |
|---|---|---|
| 0–5 giây | Con vật/cảnh thứ nhất | Chuyển động nổi bật ngay |
| 5–10 giây | Con vật/cảnh thứ hai | Động tác theo nhạc |
| 10–15 giây | Con vật/cảnh thứ ba | Thay màu và môi trường |
| 15–20 giây | Con vật/cảnh thứ tư | Một động tác rõ |
| 20–25 giây | Con vật/cảnh thứ năm | Giữ năng lượng vui |
| 25–30 giây | Con vật/cảnh thứ sáu | Kết thúc hoặc nối về đầu |

Nếu một đoạn lời hát dài hơn 5 giây, có thể đổi góc/bối cảnh trong đoạn đó; tránh thay sang con vật khác khiến lời và hình không khớp. Không thêm intro logo, giọng kể hay chữ vào định dạng bạn đã chọn.

## 9. Tạo các clip 3D trong Google Flow

1. Mở [Google Flow](https://flow.google.com/), đăng nhập tài khoản có tín dụng.
2. Tạo project mới cho video mới để dễ quản lý.
3. Chọn video dọc **9:16**, một kết quả mỗi cảnh.
4. Dùng cùng mô tả phong cách cho tất cả cảnh; thay con vật và môi trường.
5. Kiểm tra model, số clip và chi phí được hiển thị trước khi tạo.
6. Tạo clip dài hơn phần cần dùng, chẳng hạn 8 giây để cắt lấy 5 giây đẹp nhất.
7. Xem từng clip, loại cảnh lỗi rồi tải MP4.

Prompt tiếng Anh mẫu cho một cảnh:

```text
Create ONE 8-second vertical 9:16 polished 3D cartoon video.
A cute round white baby bunny hops and wiggles its ears in a
bright flower meadow. Soft glossy toy-like materials, friendly
expressive eyes, colorful lighting, smooth articulated movement.
The animal is fully visible and starts moving immediately.
One continuous shot. No human characters, captions, letters,
logos, spoken dialogue or narration. I will add music locally.
Show the generation cost before creating the video.
```

Lần dựng hiện tại dùng 5 clip mới và 1 clip cá mập sẵn có. Flow báo **100 tín dụng cho 5 clip mới**; đây là chi phí đã quan sát của lần này, không phải cam kết giá cho mọi model/lần tạo.

Các helper `scripts/animal_dance_browser.cjs` và `scripts/inspect_flow.cjs` được viết cho những project đã thao tác trong phiên này; chúng chứa project ID, tên nút và một số tọa độ cụ thể. Không coi chúng là công cụ tự tạo mọi project mới. Nếu giao diện đổi, có thể thao tác trực tiếp trên web hoặc nhờ trợ lý cập nhật helper.

## 10. Lấy nhạc có sẵn

Mở [YouTube Audio Library](https://www.youtube.com/audiolibrary), tìm **Old MacDonald**, nghệ sĩ **The Green Orbs**. Phân biệt bản hát và bản `(Instrumental)`, nghe thử đúng dòng rồi tải MP3. Trong cột giấy phép, sao chép phần ghi nguồn nếu yêu cầu. [Hướng dẫn chính thức](https://support.google.com/youtube/answer/3376882).

Muốn ghép cùng một file nhạc vào cả YouTube và TikTok, kiểm tra giấy phép của **bản thu** cho phép dùng trên cả hai. Nhạc chọn từ thư viện trong ứng dụng của một nền tảng không tự cấp quyền mang bản thu sang nền tảng khác. Với Baby Shark hoặc bài thương mại, có thể tải bản hình không nhạc rồi chọn âm thanh được nền tảng cho phép ngay trong ứng dụng; cách này có thể cần hoàn tất đăng thủ công.

File nhạc hiện tại: `data/animal-dance/old-macdonald.mp3`. Thông tin ghi nguồn đã lưu trong `data/animal-dance/music-credit.txt` và mô tả bài đăng.

Không dùng helper `data/animal-dance/fetch_music.py` để tải lại: URL tải cũ trong helper đã trả 404. Helper browser đã dùng thành công cho bài hiện tại là `scripts/music_library.cjs get-song`, nhưng phụ thuộc Chrome và giao diện tiếng Việt; tải trực tiếp từ Audio Library dễ kiểm soát hơn.

## 11. Ghép và kiểm tra video

### Dựng lại đúng bản hiện tại

Các file phải có:

```text
data/animal-dance/
  bunny.mp4
  penguin.mp4
  elephant.mp4
  monkey.mp4
  duckling.mp4
  old-macdonald.mp3
```

Cảnh cá mập được lấy từ `data/references/7620858344969964820/flow-shot-03.mp4`.

```powershell
& .\.venv\Scripts\python.exe data/animal-dance/assemble.py --music data/animal-dance/old-macdonald.mp3
```

Kết quả: `preview-silent.mp4` không nhạc và `video.mp4` có nhạc. Assembler cắt 5 giây đầu mỗi clip, bỏ âm thanh clip gốc và không thêm chữ/giọng kể. Lệnh này ghi đè các file dựng trong thư mục hiện tại.

Kiểm tra hình và tạo bảng 6 cảnh:

```powershell
& .\.venv\Scripts\python.exe data/animal-dance/check.py
```

`check.py` kiểm tra bản không nhạc. Mở thêm `video.mp4` để nghe hết 30 giây, xác nhận đúng bài hát, âm lượng ổn và không có tiếng nói từ clip gốc. `finish_music.py` có thể dựng lại nhạc, giải mã file hoàn chỉnh và dùng Groq để kiểm tra lời; nó cần `GROQ_API_KEY` và được viết riêng cho bài Old MacDonald hiện tại.

### Làm một video mới

Tạo thư mục mới, ví dụ `data/animal-dance-02/`, lưu clip/nhạc riêng và sửa bản sao assembler theo danh sách cảnh mới. Mỗi clip chỉ dài 5 giây trên timeline; cắt đúng đoạn đẹp nhất thay vì luôn lấy đầu clip nếu clip có khởi động chậm.

Trước khi đăng, xem toàn bộ video và xác nhận:

- Đúng 30 giây; đủ 6 cảnh, khoảng 5 giây mỗi cảnh.
- Đổi con vật và môi trường rõ ràng.
- Không lỗi tay/chân/khuôn mặt, không nháy hình hay khung đen.
- Không chữ, logo lạ hoặc giọng kể.
- Đúng bài hát và hình khớp lời ở mức hợp lý.
- Nhạc không bị rè, cắt đột ngột hoặc im lặng ngoài ý muốn.

## 12. Chuẩn bị tiêu đề, mô tả và hashtag

Ví dụ tiêu đề tiếng Anh:

```text
Cute Animals Dance to Old MacDonald! | 3D Kids Song
```

Mô tả nên nói đúng nội dung, có thông tin nhạc và ghi nguồn theo giấy phép. Dùng 3–5 hashtag sát chủ đề cho TikTok, chẳng hạn:

```text
#KidsSongs #CuteAnimals #3DAnimation #OldMacDonald #AnimalDance
```

Hashtag giúp diễn đạt chủ đề; không có bộ hashtag bảo đảm lên đề xuất. Không hứa chắc hàng triệu lượt xem. Video dành cho trẻ em cần khai báo đúng đối tượng; bản hiện tại có `made_for_kids=True` trên YouTube. Bình luận và một số tính năng sẽ bị hạn chế. [Thiết lập đối tượng YouTube](https://support.google.com/youtube/answer/9527654).

## 13. Đăng và xác nhận kết quả

### Video hiện tại

Video hiện tại **đã đăng thành công lên cả hai nền tảng**. Job ID:

```text
0e2ae8e510b547eb969b6e01f40707af
```

Đăng ký bản dựng vào studio, nếu đang khôi phục luồng hiện tại:

```powershell
& .\.venv\Scripts\python.exe data/animal-dance/register.py
```

Helper giữ `job-id.txt` để trả lại job cũ. Nó không tự tạo job mới mỗi lần chạy. Không xóa file này để đăng lại cùng video.

Lệnh đăng có thật trong dự án:

```powershell
& .\.venv\Scripts\python.exe scripts/assisted_video.py publish --job 0e2ae8e510b547eb969b6e01f40707af
```

Job hiện tại đã published nên không cần chạy nữa. Với video mới, tạo job mới sau khi kiểm tra bản dựng và dùng ID mới. `assisted_video.py publish` duyệt video, gửi YouTube công khai và TikTok qua Buffer theo danh sách nền tảng của job. Không chạy khi vẫn đang chỉnh sửa video.

Kiểm tra trạng thái bản hiện tại:

```powershell
& .\.venv\Scripts\python.exe data/animal-dance/monitor_publication.py
```

Helper này cũng đọc `job-id.txt` của thư mục hiện tại. Với job khác phải dùng helper phù hợp hoặc nút kiểm tra trạng thái trong studio.

| Trạng thái | Ý nghĩa |
|---|---|
| `queued` | Đang chờ hàng đợi cục bộ |
| `submitted` | Buffer đã nhận, TikTok chưa được xác nhận đăng |
| `scheduled` / `sending` phía Buffer | Đang chờ hoặc chuyển sang nền tảng |
| `published` | Provider đã báo đăng thành công |
| `remote_error` / `failed` | Có lỗi cần xử lý |
| `unknown` / `upload_unknown` | Kết quả chưa rõ; kiểm tra nền tảng trước khi thử lại |

Mở link bài đăng để kiểm tra hình, nhạc và mô tả thực tế. Nếu YouTube thành công nhưng TikTok lỗi, chỉ xử lý TikTok; không đăng lại YouTube để sửa lỗi nền tảng khác.

## 14. Lấy những lượt xem đầu tiên

### Ngay sau khi đăng

1. Kiểm tra video công khai và phát được.
2. Gửi link cho một vài người có con nhỏ hoặc người thích nội dung hoạt hình, xin nhận xét thật.
3. Chia sẻ vào nhóm phù hợp nếu nội quy cho phép; nói rõ nội dung và tránh đăng lặp.
4. Không mua view hoặc tự mở lặp bằng nhiều tài khoản. Mục tiêu là tìm người muốn xem nội dung này.
5. Giữ bài đăng để quan sát, không xóa/đăng lại liên tục chỉ vì chưa có lượt xem ngay.

Shorts/For You và tìm kiếm có thể đem người xem mới đến kênh, nhưng không có mức view khởi đầu bảo đảm. YouTube đánh giá phản ứng khi video được giới thiệu và việc người xem có ở lại; TikTok cũng nhấn mạnh watch time trong hướng dẫn cho nhà sáng tạo. [YouTube](https://support.google.com/youtube/answer/11914225), [TikTok](https://newsroom.tiktok.com/5-tips-for-tiktok-creators?lang=en).

### Lịch thử nghiệm 7 ngày

Đây là kế hoạch đề xuất, không phải yêu cầu thuật toán. Chọn một video/ngày để kiểm soát chi phí; chỉ tăng lên hai khi vẫn giữ được chất lượng.

| Ngày | Công việc |
|---|---|
| 1 | Đăng bản thử, ghi link và thời điểm |
| 2 | Đọc số liệu bản đầu; làm bản mở đầu mạnh hơn |
| 3 | Thử bài hát khác hoặc nhóm con vật khác |
| 4 | Làm thêm một bản theo ý tưởng đang có kết quả tốt |
| 5 | Thử đoạn kết nối mượt về đầu |
| 6 | Thử một khung giờ khác, giữ định dạng gần giống |
| 7 | So sánh các bản ở cùng độ tuổi bài đăng; chọn cách làm tuần sau |

Không có một giờ đăng tốt nhất cho mọi kênh. Khi có đủ dữ liệu, dùng múi giờ và thời gian hoạt động của người xem thực tế. Nội dung tiếng Anh không bảo đảm sẽ được phân phối ngay sang Mỹ/Anh.

## 15. Đọc số liệu và cải thiện

Kiểm tra sơ bộ sau 24 giờ, thêm lần nữa sau 48–72 giờ. Các mốc này để tổ chức công việc, không phải thời hạn nền tảng bắt buộc phải phân phối video.

Trên YouTube Studio, mở video → Analytics: xem nguồn truy cập Shorts Feed, tỷ lệ người chọn xem so với vuốt qua, thời lượng xem trung bình, tỷ lệ xem và đoạn rơi người xem. [Hướng dẫn Analytics Shorts](https://support.google.com/youtube/answer/12942217).

Trên TikTok Studio, xem những chỉ số tài khoản có cung cấp: views, thời lượng xem trung bình, tỷ lệ xem hết, chia sẻ, lưu và follower mới. Đừng chỉ nhìn tổng view.

| Quan sát | Thay đổi nên thử |
|---|---|
| Người xem bỏ ngay đầu | Bắt đầu bằng động tác rõ nhất; nhạc vào ngay |
| Rơi nhiều ở một cảnh | Cắt phần đứng yên, thay cảnh ít hấp dẫn |
| Xem khá lâu nhưng ít theo dõi | Làm chuỗi video có phong cách và chủ đề nhất quán |
| Hình đẹp nhưng nhạc không khớp | Chọn đoạn hát trước rồi lập cảnh theo lời |
| Lượt xem ít, dữ liệu quá nhỏ | Làm thêm bản có chủ đích; chưa kết luận chắc nguyên nhân |

Với video 30 giây, thời lượng trung bình 24 giây tương đương 80% thời lượng. Đây là cách tính, không phải ngưỡng bảo đảm lên đề xuất. So sánh với các video khác của chính kênh ở cùng khoảng thời gian sau khi đăng.

Ghi vào bảng theo dõi hoặc mục Performance feedback của studio:

```text
Ngày đăng | Nền tảng | Link | Bài hát | Con vật mở đầu |
Views sau 24h | Views sau 72h | Thời lượng xem |
Tỷ lệ xem hết/chọn xem | Chia sẻ | Ghi chú | Thử gì tiếp theo
```

Dự án chưa tự đồng bộ toàn bộ Analytics từ hai nền tảng. Feedback hiện tại là thông tin đưa vào vòng viết nội dung sau, không phải huấn luyện lại model hoặc tự bảo đảm tăng view.

## 16. Lỗi thường gặp

| Lỗi | Cách xử lý |
|---|---|
| Không thấy server | Chạy `start.ps1`, mở đúng `127.0.0.1:8000` |
| OAuth JSON không tìm thấy | Dùng `--client-file` trỏ đúng file Desktop app |
| YouTube token bị thu hồi/hết hạn | Kết nối lại bằng `connect_youtube.py` |
| Flow không tạo được | Xem thông báo model/tín dụng; không tạo hàng loạt lại khi chưa biết nguyên nhân |
| Clip lỗi hoặc thiếu chuyển động | Sửa prompt cụ thể hơn và tạo lại riêng cảnh lỗi |
| Browser helper báo cổng 9223 không kết nối | Chrome dành riêng cho automation chưa mở; thao tác web thủ công hoặc nhờ trợ lý mở đúng profile |
| Nhạc tải nhầm | Nghe và kiểm tra đúng tên/nghệ sĩ/bản hát trước khi ghép |
| TikTok còn `submitted` | Chờ và kiểm tra Buffer; chưa coi là đã đăng |
| TikTok lỗi kênh | Kết nối lại đúng kênh trong Buffer, kiểm tra chế độ Automatic |
| Upload kết quả không rõ | Kiểm tra Studio/Buffer trước khi thử lại để tránh bài trùng |
| Đã đổi MP4 nhưng job vẫn là bản cũ | Job đã lưu bản sao trong `data/artifacts/<job-id>/`; video mới cần job mới |

## 17. Cách yêu cầu trợ lý làm video tiếp theo

Bạn có thể nhắn:

```text
Làm video thiếu nhi 3D mới dài 30 giây, dọc 9:16.
Mỗi khoảng 5 giây đổi con vật và bối cảnh, không chữ,
không giọng kể. Dùng bài hát tiếng Anh có sẵn phù hợp.
Research trước, cho động tác xuất hiện ngay giây đầu,
hình khớp lời hát. Tạo trong thư mục mới, kiểm tra xong
đăng YouTube và TikTok. Giới hạn tạo video: 100 tín dụng Flow.
```

Nếu chỉ muốn xem trước, thay câu cuối bằng “xuất file cho tôi xem, chưa đăng”. Nếu muốn một bài cụ thể, ghi tên và bản thu bạn chọn. Đăng nhập tài khoản và thực hiện bước xác nhận trực tiếp của dịch vụ khi cần; trợ lý không thay bạn nhập mật khẩu hay mã OTP.

Luồng hiện tại được trợ lý hỗ trợ trong phiên làm việc, chưa phải hệ thống tự chạy toàn bộ nền tảng không cần giám sát. Quy trình cần hoàn thành cho mỗi video là: chọn nhạc → nghiên cứu → lên 6 cảnh → tạo clip → cắt ghép → xem kiểm tra → tạo job mới → đăng → xác nhận link → ghi số liệu → cải thiện bản tiếp theo.
