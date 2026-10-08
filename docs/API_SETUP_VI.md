# Hướng dẫn API: tạo video tiếng Anh, research và đăng YouTube + TikTok

Dự án hỗ trợ YouTube qua Google API, TikTok qua Buffer. TikTok research dùng Apify hoặc nguồn bạn nhập. Buffer và Apify là dịch vụ bên thứ ba, không phải API key của TikTok.

## Bạn cần những tài khoản nào?

| Dịch vụ | Dùng làm gì | Cấu hình |
|---|---|---|
| OpenAI Platform | Viết kịch bản, tạo hình, giọng tiếng Anh | `OPENAI_API_KEY` |
| Google Cloud | Research và upload YouTube | API key + OAuth |
| Buffer | Đăng TikTok tự động | API key + channel ID |
| Cloudinary | Lưu MP4 ở URL công khai để Buffer tải | Cloud name + API key + secret |
| Apify, tùy chọn | Research TikTok tự động bằng từ khóa | API token |
| ElevenLabs, tùy chọn | Thay giọng OpenAI | API key + voice ID |

Gói Plus không trả phí API. Kiểm tra hạn mức và bảng giá trong từng tài khoản trước khi bật live. Không cần mua thêm ElevenLabs nếu dùng giọng OpenAI mặc định.

## 1. Chuẩn bị dự án

Mở PowerShell tại thư mục dự án. Nếu chưa có môi trường Python, chạy `./start.ps1` một lần để cài, rồi Ctrl+C để dừng server. Sau khi có `.venv`:

```powershell
.venv/Scripts/python.exe -m pip install -r requirements.txt
```

Nếu **chưa có** `.env`, tạo từ mẫu:

```powershell
Copy-Item .env.example .env
```

Nếu đã có `.env`, thêm các biến còn thiếu; không chép đè file đang chứa key. Mở `.env` bằng trình soạn thảo trên máy. Lưu key tại đây, không gửi vào chat và không commit lên Git.

## 2. OpenAI: một key cho kịch bản, hình và giọng

1. Đăng nhập [OpenAI Platform](https://platform.openai.com/).
2. Chọn/tạo project, vào API keys và tạo secret key. [Mở trang API keys](https://platform.openai.com/api-keys).
3. Kiểm tra Billing, phương thức thanh toán và credits/usage. Plus và API có thanh toán riêng.
4. Lưu key tại máy. Trong `.env`:

```dotenv
APP_MODE=live
OPENAI_API_KEY=replace_with_your_key
CONTENT_MODEL=gpt-6.1-sol
RESEARCH_MODEL=gpt-6-luna
IMAGE_MODEL=gpt-image-2.5-flare
TTS_PROVIDER=openai
TTS_MODEL=gpt-4o-mini-tts
TTS_VOICE=coral
```

Chỉ dùng model mà project của bạn có quyền truy cập; nếu trả HTTP 403/404, kiểm tra model access và organization verification. Các tên model đều có thể đổi trong `.env` nếu tài khoản chưa được cấp quyền. [OpenAI Docs: tạo key và gọi API](https://developers.openai.com/api/docs/quickstart).

## 3. Google Cloud: YouTube API key cho research

1. Mở [Google Cloud Console](https://console.cloud.google.com/), tạo project, ví dụ `Dreamforge Studio`.
2. APIs & Services → Library → tìm **YouTube Data API v3** → Enable.
3. APIs & Services → Credentials → Create credentials → API key.
4. Chỉnh API restrictions để key chỉ dùng YouTube Data API v3. Key được dùng phía Python nên không đặt HTTP referrer restriction như key chạy trong trình duyệt.
5. Điền:

```dotenv
YOUTUBE_API_KEY=replace_with_your_google_api_key
```

Key này dùng tìm video/đọc metadata. **Nó không cấp quyền đăng lên kênh của bạn.** Để upload cần OAuth ở bước tiếp theo. [YouTube Python Quickstart](https://developers.google.com/youtube/v3/quickstart/python).

## 4. YouTube OAuth: cho phép upload lên kênh

1. Trong Google Cloud project trên, mở Google Auth Platform hoặc mục OAuth consent screen.
2. Hoàn tất Branding/thông tin ứng dụng. Với tài khoản cá nhân thường chọn External; khi ở chế độ Testing, thêm email Google của bạn vào Test users.
3. Data Access: thêm scope `https://www.googleapis.com/auth/youtube.upload` khi cấu hình yêu cầu quyền.
4. Clients / Credentials → Create OAuth client ID → chọn **Desktop app**.
5. Download JSON và lưu tại `data/google-client.json` trong dự án. Thư mục `data` đã được Git bỏ qua.
6. Chạy helper:

```powershell
.venv/Scripts/python.exe scripts/connect_youtube.py
```

Trình duyệt sẽ mở trang Google. Đăng nhập tài khoản có kênh YouTube, chọn đúng kênh nếu Google cho lựa chọn, và cấp quyền upload. Helper lưu các biến sau vào `.env` mà không in token ra màn hình:

```dotenv
YOUTUBE_CLIENT_ID=filled_by_helper
YOUTUBE_CLIENT_SECRET=filled_by_helper
YOUTUBE_REFRESH_TOKEN=filled_by_helper
```

Nếu trình duyệt báo ứng dụng thử nghiệm chưa được xác minh, kiểm tra rằng đó đúng là OAuth client do bạn vừa tạo và email đã nằm trong Test users. Nếu refresh token hết hạn/bị thu hồi, chạy helper lại. Chế độ Testing có giới hạn token, chưa phù hợp để vận hành lâu dài.

OAuth consent verification và YouTube upload compliance audit là hai việc khác nhau. Có token không đảm bảo video có thể đăng công khai; một số dự án chưa được audit bị giới hạn upload private. Hãy thử một video Private trước. [Google OAuth](https://developers.google.com/youtube/v3/guides/auth/installed-apps), [YouTube upload restrictions](https://developers.google.com/youtube/v3/docs/videos/insert).

## 5. TikTok: kết nối Buffer để tự đăng

TikTok có Content Posting API, gồm `video.upload` gửi bản nháp và `video.publish` đăng trực tiếp. Đăng trực tiếp yêu cầu app/quyền/xét duyệt; hướng dẫn intended use không chấp nhận công cụ chỉ phục vụ tài khoản bạn/nhóm bạn quản lý. Dự án này dùng Buffer thay vì mặc định rằng app nội bộ sẽ được TikTok duyệt. [TikTok guidelines](https://developers.tiktok.com/docs/en/content-sharing-guidelines).

1. Tạo tài khoản [Buffer](https://buffer.com/), vào phần Channels và kết nối TikTok.
2. Đăng nhập đúng TikTok, cấp quyền cho Buffer. Kiểm tra kênh không disconnected, locked hoặc paused.
3. Thử tạo một video post trong Buffer và kiểm tra **Automatic**, không phải **Notify Me**. Một số nội dung/hiệu ứng chỉ hỗ trợ notification publishing. [Buffer TikTok](https://support.buffer.com/en-us/articles/using-tiktok-with-buffer-oGEroY9Of2).
4. Vào Settings → API (nếu tài khoản có quyền API), tạo personal API key. [Buffer API](https://buffer.com/api).
5. Điền:

```dotenv
BUFFER_API_KEY=replace_with_your_buffer_key
```

6. Lấy channel ID bằng helper chỉ đọc dữ liệu:

```powershell
.venv/Scripts/python.exe scripts/list_buffer_channels.py
```

Kết quả có service, tên kênh và `channel_id`. Chọn dòng `tiktok`; điền:

```dotenv
TIKTOK_PUBLISHER=buffer
BUFFER_TIKTOK_CHANNEL_ID=replace_with_tiktok_channel_id
```

Không chọn ID của YouTube hoặc nền tảng khác. Nếu không thấy menu API, kiểm tra quyền tài khoản/API với Buffer trước khi mua gói. Không có tích hợp này nào được bảo đảm hoạt động với tài khoản chưa cấp đủ quyền.

## 6. Cloudinary: để Buffer đọc được video

Buffer cần URL video công khai; đường dẫn `localhost` của bạn không dùng được. [Buffer media hosting](https://developers.buffer.com/guides/hosting-media.html).

1. Tạo tài khoản [Cloudinary](https://cloudinary.com/).
2. Trong Console, chọn product environment. Tìm Cloud name và trang API Keys của environment đó; tên menu có thể thay đổi theo giao diện.
3. Lấy API key và API secret. Điền:

```dotenv
CLOUDINARY_CLOUD_NAME=replace_with_cloud_name
CLOUDINARY_API_KEY=replace_with_api_key
CLOUDINARY_API_SECRET=replace_with_api_secret
```

Khi bạn chọn TikTok → Buffer → Public và đưa video đã duyệt vào hàng đợi, dự án upload **MP4 đã duyệt** lên Cloudinary bằng signed upload, lấy HTTPS URL, rồi gửi sang Buffer. File đó truy cập được với người có URL và còn trên Cloudinary cho tới khi bạn xóa. Không xóa trước khi Buffer tải và đăng xong. Không cần bật unsigned upload preset. [Cloudinary signed uploads](https://cloudinary.com/documentation/authentication_signatures).

`submitted` nghĩa là Buffer đã nhận bài, **chưa xác nhận TikTok đã đăng**. Nút **Check Buffer status** kiểm tra lại; trạng thái `sent` mới được đánh dấu `published`. Đổi/hủy bài đã gửi phải thao tác trong Buffer. Dự án không tự thử lại nếu upload có kết quả không rõ.

## 7. Apify: research TikTok tự động, tùy chọn

Đây là dịch vụ thu thập metadata bên thứ ba; không phải TikTok Research API chính thức.

1. Tạo tài khoản [Apify](https://apify.com/), vào Console → Settings → Integrations/API tokens để lấy token của bạn.
2. Mở [Clockworks TikTok Scraper](https://apify.com/clockworks/tiktok-scraper), kiểm tra quyền sử dụng và giá của actor.
3. Điền:

```dotenv
APIFY_API_TOKEN=replace_with_your_apify_token
APIFY_MAX_CHARGE_USD=0.5
```

Khi chạy live, research tìm tối đa 12 kết quả TikTok theo từ khóa trong tuần qua. Không tải lại video của tác giả; chỉ đọc caption, link, thời gian và views. Mỗi run truyền giới hạn chi phí 0.5 USD qua `maxTotalChargeUsd`; có thể sửa trong khoảng 0.01–5. Nếu actor yêu cầu mức tối thiểu cao hơn cấu hình, request có thể bị từ chối. Dữ liệu và khả năng thu thập phụ thuộc actor/TikTok. [Apify API và giới hạn chi phí](https://docs.apify.com/api/v2/actor-run-sync-get-dataset-items-post).

Để trống token nếu muốn nhập nguồn TikTok thủ công. Tổng views không chứng minh video đang tăng mạnh; cần các lần quan sát để so sánh growth/hour.

## 8. Bật và thử từng bước

1. Để `APP_MODE=demo` nếu chỉ kiểm tra luồng UI, không gọi API.
2. Cấu hình OpenAI, đổi live, tạo một video ngắn để thử hình/giọng.
3. Bật YouTube research và optional Apify research.
4. Duyệt video rồi upload YouTube ở chế độ Private để kiểm tra kênh.
5. Cấu hình Buffer + Cloudinary. Duyệt video rồi chọn TikTok, Buffer, Public để gửi bài thật.
6. Mở Buffer kiểm tra caption, AI disclosure và lịch; sau thời điểm đăng dùng Check Buffer status.

Khởi động lại sau khi sửa `.env`:

```powershell
./start.ps1
```

Hai nền tảng có hai publication entries riêng: có thể queue cùng một video cho YouTube và TikTok. Server phải chạy để tới giờ gửi bài từ hàng đợi cục bộ. Khi Buffer đã nhận, lịch của nó chạy phía Buffer. API keys được giữ phía server; màn hình Connections chỉ hiện đã cấu hình hay chưa, không hiện key và cũng chưa xác nhận key hoạt động.

Nếu bạn muốn tự dùng TikTok API thay vì Buffer: đăng ký app trên [TikTok for Developers](https://developers.tiktok.com/), thêm Login Kit/Content Posting API, cấu hình redirect URL, xin scope phù hợp và thực hiện OAuth. `client_key`/`client_secret` khác access token của người dùng. `video.upload` vẫn yêu cầu bạn hoàn tất đăng trong TikTok; `video.publish` chịu điều kiện audit. Adapter native này chưa được triển khai trong dự án, nên đừng điền TikTok client key vào ô Buffer API key.
