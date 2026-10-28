# Motion Studio

Bộ công cụ đồ họa và âm thanh cho Aiagentbot, cài ngày 22/10/2026. Thư viện được khóa phiên bản trong hai package-lock.json. Dự án video cũ ở output/myth-2026 giữ nguyên.

## Mở công cụ

Từ thư mục này:

```powershell
npm run studio         # Remotion Studio
npm run motion-canvas  # Motion Canvas Editor, chỉ lắng nghe localhost
npm run check          # Kiểm tra TypeScript và các đường dẫn import
npm run render         # Xuất composition mẫu vào output/toolkit-demo.mp4
npm run svgo -- --help # Tối ưu SVG
```

Motion Canvas có plugin FFmpeg để xuất video. Cấu hình và cảnh mẫu ở motion-canvas/. Chạy `npm --prefix motion-canvas run build` để kiểm tra build.

## Đã cài

| Công cụ | Gói / vị trí |
| --- | --- |
| Motion AI Kit | Skill motion trong C:/Users/Tonny/.codex/skills; MCP motion tại https://mcp.motion.dev |
| GSAP Skills | 8 skill gsap-* cùng thư mục trên |
| GSAP và React hook | gsap, @gsap/react |
| Loading GSAP | Component src/GsapLoader.tsx, có cleanup và hỗ trợ reduced motion |
| SVGO, Satori | svgo, satori |
| Anime.js, Motion | animejs, motion |
| Rive | @rive-app/react-canvas — runtime React để phát file .riv |
| Remotion 2D/3D | remotion, @remotion/cli, @remotion/three, media, transitions, captions; 12 skill Remotion |
| Motion Canvas 2D | @motion-canvas/core, 2d, ui, vite-plugin, ffmpeg trong motion-canvas/ |
| Three.js / React Three Fiber | three, @react-three/fiber |
| Drei, Rapier | @react-three/drei, @react-three/rapier |
| PostProcessing | postprocessing, @react-three/postprocessing |
| Howler.js | howler |
| Mediabunny | mediabunny |
| FFmpeg | Bản portable 9.0.2 tại ../../.tools/ffmpeg/ffmpeg-9.0.2-full_build/bin/; winget đã thêm alias và PATH người dùng |

Các import tham khảo đã kiểm tra ở src/libraries.ts. GSAP, Anime.js và Motion phù hợp cho giao diện tương tác. Khi xuất Remotion, điều khiển hoạt ảnh theo useCurrentFrame hoặc seek timeline theo frame để bảo đảm kết quả ổn định.

Rive ở đây là runtime; không bao gồm việc đăng nhập hay cài ứng dụng Rive Editor. Có thể tải file .riv của bạn vào runtime. Motion AI Kit cài phần miễn phí; Motion+ chưa kích hoạt. Skill mới có hiệu lực từ lượt chat tiếp theo; có thể cần mở lại ứng dụng để nạp MCP. Mở terminal mới để dùng alias ffmpeg.

## Nguồn

- Motion AI Kit: https://github.com/motiondivision/ai-kit và https://motion.dev/docs/ai-kit-install
- GSAP Skills: https://github.com/greensock/gsap-skills
- Remotion Skills: https://github.com/remotion-dev/skills
- Motion Canvas: https://motioncanvas.io/docs/quickstart/
- FFmpeg distribution: https://www.gyan.dev/ffmpeg/builds/

## Ghi chú phụ thuộc

Motion Canvas 3.17.2 hiện yêu cầu Vite 4/5. Đã cập nhật xmldom và esbuild bằng overrides; npm audit vẫn báo các vấn đề upstream của Vite và braces chưa có bản sửa tương thích. Editor chỉ được cấu hình chạy tại 127.0.0.1. Satori còn phụ thuộc fflate có cảnh báo mức moderate. Không chạy audit fix --force để hạ phiên bản hoặc phá tương thích. Chi tiết trạng thái cài đặt và kiểm tra ở installation-report.json.
