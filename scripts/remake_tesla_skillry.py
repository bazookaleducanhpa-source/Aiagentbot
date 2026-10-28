"""Create a separately editable second edition and an original Vietnamese script."""
from pathlib import Path
import json, shutil, subprocess

WORKSPACE = Path(__file__).resolve().parents[1]
OLD = WORKSPACE / 'output/tesla-cappy-vfacts'
ROOT = WORKSPACE / 'output/tesla-cappy-skillry-v3'
ROOT.mkdir(exist_ok=True)
(ROOT / 'public/voice').mkdir(parents=True, exist_ok=True)
(ROOT / 'research').mkdir(exist_ok=True)
(ROOT / 'qa').mkdir(exist_ok=True)
if not (ROOT / 'src').exists():
    shutil.copytree(OLD / 'src', ROOT / 'src')
for name in ['package.json', 'tsconfig.json', 'generate_voice.py', 'align_voice.py',
             'master_mix.py', 'edit-manifest.cjs', 'export_subtitles.py', 'CREDITS.txt', 'SOURCES.md']:
    if not (ROOT / name).exists():
        shutil.copy2(OLD / name, ROOT / name)
for relative, source in [('node_modules', OLD / 'node_modules'),
                         ('public/footage', OLD / 'public/footage'),
                         ('public/music', OLD / 'public/music'),
                         ('public/sfx', OLD / 'public/sfx')]:
    link = ROOT / relative
    if not link.exists():
        subprocess.run(['rtk', 'proxy', 'cmd', '/c', 'mklink', '/J', str(link), str(source.resolve())], check=True)

RAW = '''XE BAY HAY XE LÀM XIẾC?
Một chiếc ô tô leo lên vách, treo ngược, rồi lộn vòng: xem đến đây, Cappy cũng phải bỏ gói bánh xuống.
Chào bạn, mình là Cappy; hôm nay chúng ta bóc tách màn trình diễn Roadster để hiểu chiếc xe này thực sự đang làm gì.
Đi cùng mình đến cuối nhé, vì điều thú vị nhất nằm ở khoảng cách giữa một cú nhảy ngoạn mục và một chiếc xe có thể bay.

CHỮ BAY ĐANG ĐÁNH LỪA CHÚNG TA
Ném một chiếc dép lên trời, bạn cũng có một vật thể bay, nhưng chẳng ai vì thế mà cấp bằng phi công cho chiếc dép.
Rời mặt đất chỉ mô tả một khoảnh khắc; duy trì độ cao, đổi hướng và hạ cánh mới là cả một bài toán khác.
Muốn đánh giá Roadster công bằng, ta cần tách những chuyện đó ra, thay vì để một chữ bay làm hộ toàn bộ phần giải thích.

BA NHIỆM VỤ, BA CÂU HỎI
Trước khi xem chậm cú lộn vòng, hãy đặt ba chiếc thẻ lên bàn: bám vào bề mặt, tạo lực đẩy và điều khiển tư thế.
Mỗi chiếc thẻ trả lời một câu hỏi riêng: xe giữ tiếp xúc bằng gì, thay đổi chuyển động bằng gì, và giữ đúng hướng bằng gì.
Đọc được ba chiếc thẻ này, bạn sẽ xem màn trình diễn bằng con mắt của người hiểu chuyện, thay vì chỉ há miệng cùng Cappy.

VẬT LÝ KHÔNG CẦN PHÉP THUẬT
Hãy nhìn chiếc xe như một đội làm việc: bánh lo tiếp xúc, quạt tạo chênh lệch áp suất, vòi phụt tạo thêm lực.
Bộ điều khiển phải phối hợp cả đội, bởi một cú đẩy đúng độ mạnh nhưng sai thời điểm vẫn có thể làm hỏng động tác.
Vì thế, câu hỏi dẫn đường cho video hôm nay rất đơn giản: lực đến từ đâu, đi hướng nào, và được duy trì trong bao lâu?

KHỎE CHƯA ĐỦ, PHẢI BÁM ĐƯỢC
Bạn từng thấy bánh xe quay tít mà chiếc xe gần như đứng yên chưa: động cơ có sức, nhưng mặt đường không nhận được hết sức đó.
Khi tăng tốc, phanh hay vào cua, lốp cần truyền lực qua vùng tiếp xúc; khả năng truyền lực ấy có giới hạn.
Tạo thêm lực ép xuống là một cách khai thác độ bám, giống nhắc anh chàng cơ bắp rằng muốn đẩy mạnh thì trước hết phải đứng vững.

CHIẾC QUẠT CÓ MỘT NGHỀ KHÁC
Nhìn quạt dưới gầm, đừng vội tưởng chiếc xe đang bật điều hòa cho mặt đường; nhiệm vụ đáng chú ý hơn là quản lý luồng khí.
Khi quạt rút khí khỏi một vùng được làm kín tương đối, áp suất phía dưới có thể thấp hơn áp suất bên ngoài.
Chênh lệch đó tạo lực ép chiếc xe về phía bề mặt, và quạt có thể làm việc ngay cả khi xe chưa chạy thật nhanh.

AI ĐANG ÉP CHIẾC XE XUỐNG?
Nói xe bị hút xuống khá dễ hình dung, nhưng bức tranh đầy đủ còn có không khí bên ngoài cùng tham gia tạo lực.
Điều quyết định là chênh lệch áp suất trên vùng diện tích hữu ích, trong khi không khí lọt vào liên tục làm bài toán khó hơn.
Không có một khoảng chân không hoàn hảo ngoan ngoãn nằm dưới gầm; hệ thống phải liên tục duy trì điều kiện mà nó cần.

MỘT PHÉP NHÂN NHỎ, MỘT LỰC LỚN
Thử một ví dụ do chúng ta tự chọn: mười nghìn pascal chênh lệch áp suất trên hai mét vuông cho lực hai mươi nghìn niutơn.
Đó là phép nhân áp suất với diện tích, chưa tính rò khí và tổn thất, và hoàn toàn không phải thông số đo của Roadster.
Ví dụ cho thấy vì sao quạt có thể đáng gờm; nó chưa phải giấy phép để Cappy gắn máy hút bụi vào xe đạp rồi leo tường.

KẺ PHÁ ĐÁM NẰM Ở KHE HỞ
Trên sơ đồ, mặt đường phẳng đẹp, khe gầm đều tăm tắp, còn mũi tên không khí thì xếp hàng lịch sự như đi nhận quà.
Ngoài đời có khe nối, mặt đường thay đổi và những chuyển động khiến việc hạn chế rò khí trở thành nhiệm vụ thật sự.
Một chiếc quạt khỏe chỉ giải một phần; cơ cấu làm kín, khoảng sáng gầm và bộ điều khiển còn phải phối hợp đủ tốt với nhau.

TREO NGƯỢC KHÔNG LÀM TRỌNG LỰC NGHỈ VIỆC
Khi xe nằm ngược dưới một bề mặt, trọng lực vẫn kéo xuống; nó không xin nghỉ chỉ vì camera đang quay đẹp.
Muốn duy trì tiếp xúc ở tư thế ấy, lực hướng về bề mặt phải đủ lớn, với dự phòng phù hợp cho chuyển động thực tế.
Màn trình diễn giúp ta hình dung nguyên lý, nhưng chưa cho phép kết luận chiếc xe sẽ bám được mọi trần nhà hay mọi kiểu mặt đường.

Ý TƯỞNG NÀY ĐÃ CÓ HỌ HÀNG
McMurtry Spéirling là một ví dụ khác về xe dùng quạt tạo lực ép chủ động, kể cả ở trạng thái đứng yên.
Điều đó cho thấy xe quạt có nền tảng kỹ thuật rõ ràng; phần đáng xem nằm ở cách thiết kế và triển khai từng hệ thống.
Ta đang so nguyên lý, không lấy thông số của chiếc xe này dán lên chiếc xe kia chỉ vì cả hai cùng có tiếng quạt khá dữ dội.

RỜI MẶT ĐƯỜNG, ĐỔI HẲN BÀI TOÁN
Đến lúc bánh rời khỏi đường trình diễn, câu chuyện giữ xe bám bề mặt đã chuyển sang một chương khác: thay đổi chuyển động trên không.
Chiếc quạt dưới gầm không tự mang theo một mặt đường vô hình, nên đừng bắt nó giải thích mọi phần của cú nhảy.
Bây giờ hãy nhìn những vòi phụt: đây là lúc phần khí mang theo trên xe bắt đầu có vai trò trong câu chuyện lực đẩy.

TÊN LỬA MÀ KHÔNG CẦN NGỌN LỬA
Hệ đẩy khí lạnh giữ khí dưới áp suất, rồi giải phóng khí qua vòi phụt để tạo lực; nguyên lý ấy cũng được dùng trong hàng không vũ trụ.
Chữ lạnh ở đây giúp phân biệt nó với hệ tạo luồng khí bằng quá trình đốt trong buồng cháy, không phải lời hứa xe đang phun điều hòa.
Vì vậy, một luồng trắng trong video chưa đủ để kết luận chiếc xe đang đốt cùng loại nhiên liệu với tên lửa ngoài bệ phóng.

NEWTON CÓ MẶT TRONG QUẢ BÓNG
Bơm căng một quả bóng rồi thả miệng bóng: khí chạy một phía, còn quả bóng lao theo phía khác, đôi khi đập thẳng vào chủ nhân.
Đó là một cách hình dung phản lực; hệ kỹ thuật làm công việc tương tự bằng bình khí, van và vòi phụt được kiểm soát.
Chiếc xe không cần đạp vào bầu trời, nó nhận lực khi phóng khí theo một hướng; còn lực mạnh bao nhiêu lại cần dữ liệu cụ thể.

MŨI TÊN KHÍ VÀ MŨI TÊN LỰC
Nếu khí bị phóng theo một hướng, phản lực tác dụng lên xe có thành phần theo hướng đối lại; đổi hướng vòi phụt sẽ đổi bài toán.
Vị trí đặt lực cũng quan trọng, bởi đẩy qua gần tâm khối lượng khác với đẩy lệch sang một bên của thân xe.
Cappy nghiêng người trên ghế không giúp thay thế bộ điều khiển; muốn xe đi đúng ý, các mũi tên lực phải được sắp xếp bằng kỹ thuật.

CÙNG MỘT CÚ ĐẨY, SAO XE LẠI XOAY?
Hãy đẩy một hộp đồ chơi ở giữa, rồi thử đẩy gần một góc: bạn sẽ thấy vị trí tác dụng làm thay đổi xu hướng quay.
Với chiếc xe, lực có cánh tay đòn phù hợp có thể tạo mômen, còn nhiều cơ cấu phải được phối hợp để tạo động tác mong muốn.
Nhìn từ xa chỉ có một cú lộn vòng; nhìn bằng sơ đồ lực, bạn bắt đầu thấy một chuỗi nhiệm vụ được giải nối tiếp nhau.

XOAY ĐƯỢC MỚI LÀ NỬA CHUYỆN
Một cú nhào lộn đẹp không kết thúc ở việc bắt đầu quay; chiếc xe còn phải về đúng tư thế và tiếp đất trong điều kiện phù hợp.
Hướng thân xe, tốc độ quay và thời điểm tác động đều quan trọng, nên phần điều khiển đáng được chú ý ngang với các cơ cấu tạo lực.
Camera cho ta thấy kết quả trong vài giây, còn những điều chỉnh diễn ra bên trong cần dữ liệu kỹ thuật để biết chính xác hơn.

XEM CHẬM THÌ THẤY GÌ?
Tua chậm đoạn trình diễn giúp ta quan sát lúc tiếp cận, rời đường, xoay và trở lại bề mặt; đó là một bài học thị giác khá tốt.
Nhưng hình ảnh riêng lẻ chưa cho biết đầy đủ tải trên các kết cấu, lực của từng cơ cấu hay mọi điều kiện chuẩn bị trước đó.
Muốn đi từ thấy một động tác đến khẳng định một thông số, ta cần phép đo tương ứng; mắt tinh cũng chưa tự biến thành phòng thử nghiệm.

MẠNH TRONG CHỐC LÁT, LÂU ĐƯỢC BAO NHIÊU?
Một lực đẩy lớn trong thời gian ngắn có thể tạo động tác ấn tượng, nhưng duy trì lực đó là câu hỏi về nguồn lực và giới hạn vận hành.
Với khí mang theo, mỗi lần phụt đều dùng bớt lượng khí trong bình; tăng thời gian thường kéo theo yêu cầu lớn hơn với cả hệ thống.
Đây là chỗ màn biểu diễn gặp kế toán: kỹ thuật cũng có ngân sách, chỉ khác là bảng chi tiêu có thêm khối lượng, áp suất và thời gian.

THỬ CHO MỘT CHIẾC XE LƠ LỬNG
Ta chọn khối lượng giả định một nghìn năm trăm kilôgam, rồi nhân với gia tốc trọng trường xấp xỉ chín phẩy tám mét trên giây bình phương.
Kết quả là trọng lượng khoảng mười bốn nghìn bảy trăm niutơn; muốn lơ lửng trong mô hình đơn giản, lực hướng lên cần cân bằng trọng lượng đó.
Những con số này do chúng ta chọn để học cách tính, không phải số cân hay lực đẩy mà Tesla đã công bố cho Roadster.

CÁI GIÁ CỦA VIỆC PHỤT KHÍ
Thêm một giả định: vận tốc phụt hiệu dụng là năm trăm mét mỗi giây; mô hình đơn giản cho lưu lượng bằng lực chia cho vận tốc này.
Lấy mười bốn nghìn bảy trăm chia năm trăm, ta được khoảng hai mươi chín phẩy bốn kilôgam khí mỗi giây trong ví dụ đang xét.
Đây không phải mức tiêu hao của Roadster; nó chỉ giúp bạn thấy vì sao một tuyên bố về lực cực đại chưa trả lời được chuyện duy trì bao lâu.

THÊM BÌNH KHÍ CÓ XONG KHÔNG?
Nghe thiếu khí, Cappy đề nghị mang bình to hơn, giống hệt cách mình giải quyết vali chật trước một chuyến du lịch quá nhiều đồ.
Nhưng bình, khí và cơ cấu đi kèm đều có khối lượng; mang thêm lại làm thay đổi trọng lượng, bố trí và yêu cầu của hệ thống.
Bởi thế, thiết kế là tìm điểm cân bằng giữa nhiều ràng buộc; một nâng cấp tưởng rất thẳng thắn có thể làm cả bài toán phải tính lại.

TĂNG TỐC LÀ MỘT CUỘC THI KHÁC
Vòi phụt có thể bổ sung lực ngoài lực truyền qua lốp, nhưng từ nguyên lý ấy đến một thành tích tăng tốc cụ thể vẫn cần đo đạc.
Khi so hai con số, hãy đọc điều kiện mặt đường, loại cấu hình, cách bắt đầu tính giờ và cách xác định mốc vận tốc.
Nếu một bên tính khác bên kia, bảng xếp hạng có thể đang so hai bài thi; tiêu đề ngắn đến mấy cũng không sửa được chuyện đó.

NGƯỜI NGỒI TRONG XE CŨNG CÓ QUÁN TÍNH
Chiếc xe đổi chuyển động, người ngồi trong xe cũng phải chịu tác động tương ứng; cơ thể không được miễn vật lý nhờ đeo dây an toàn.
Hướng gia tốc, thời gian tác dụng, tư thế ngồi và hệ bảo vệ đều thuộc bài toán thiết kế, bên cạnh thành tích đẹp trên màn hình.
Cappy thích xem cú nhào lộn từ ghế khán giả hơn: ở đó vẫn phấn khích, mà gói bỏng ngô không phải tham gia chương trình huấn luyện phi hành gia.

MỘT CÚ PHỤT CÒN CÓ HÀNG XÓM
Luồng khí không dừng lịch sự tại đường viền thân xe; tác động đến môi trường xung quanh cũng cần được tính trong điều kiện vận hành.
Không gian trống, bề mặt phù hợp và khu vực kiểm soát giúp một màn trình diễn khác rất nhiều với một góc phố đông người.
Vì vậy, xem xe làm được động tác ở nơi thử nghiệm chưa đủ để suy ra ai cũng có thể lặp lại nó ở bãi đỗ cạnh nhà.

ĐỌC ĐÚNG TÊN CHIẾC XE
Một tên sản phẩm có thể đi kèm nhiều cấu hình; hình quảng bá của bản đặc biệt không tự trở thành danh sách trang bị của mọi chiếc xe.
Trang Roadster hiện có những chú thích gắn tính năng với cấu hình hoặc gói nâng cấp, nên phải đọc chúng cùng nội dung chính.
Đừng ghép mọi con số và mọi hình ảnh vào một chiếc xe tưởng tượng hoàn hảo; chiếc xe ấy chạy rất nhanh, nhưng chỉ chạy trong đầu chúng ta.

TRÌNH DIỄN VÀ ĐƯỜNG PHỐ
Khả năng kỹ thuật, điều kiện thử nghiệm và điều kiện sử dụng ngoài đường phố là các câu hỏi cần được kiểm tra theo đúng nơi và cấu hình.
Một màn diễn gây ấn tượng không tự thay thế tài liệu vận hành hay sự chấp thuận cần thiết cho một tính năng cụ thể.
Ý tưởng nhảy qua đoạn tắc đường thì nghe hấp dẫn thật, nhưng trước khi tưởng tượng cảnh ấy, hãy tìm tài liệu nói rõ chiếc xe được phép làm gì.

LUỒNG TRẮNG CÓ PHẢI KHÓI CHÁY?
Hình ảnh một luồng trắng khiến ta dễ liên tưởng đến khói, nhưng màu trắng tự nó chưa xác định được thành phần hay quá trình tạo ra luồng đó.
Khí giãn nở có thể lạnh đi, và trong điều kiện phù hợp hiện tượng ngưng tụ góp phần làm một luồng khí trở nên nhìn thấy được.
Đó là cách giải thích định tính, không phải kết quả phân tích luồng phụt Tesla; hãy nhớ hơi thở mùa lạnh cũng nhìn thấy dù miệng bạn chẳng có buồng đốt.

MỘT CON SỐ RẤT DỄ ĐỌC NHẦM
Sáu mươi dặm mỗi giờ tương đương khoảng chín mươi bảy kilômét mỗi giờ; nó gần một trăm, nhưng không phải cùng một mốc vận tốc.
Giả sử đạt sáu mươi dặm mỗi giờ trong một giây, gia tốc trung bình sẽ vào khoảng hai phẩy bảy lần gia tốc trọng trường trong phép tính đơn giản.
Đây vẫn là ví dụ giả định, không phải phép đo của chúng ta trên xe; còn gia tốc tức thời có thể khác giá trị trung bình vừa tính.

SAO KHÔNG DÙNG NÓ NHƯ TRỰC THĂNG?
Cánh quạt trao đổi động lượng với không khí xung quanh, trong khi hệ khí lạnh đang xét giải phóng phần khí đã được mang sẵn trong bình.
Hai cách cùng có thể tạo lực, nhưng cách cấp dòng khí, nguồn năng lượng và giới hạn thời gian hoạt động khác nhau đáng kể.
Cùng rời mặt đất chưa có nghĩa cùng làm được một công việc; giống có người biết nhảy cao chưa có nghĩa họ nhận giao hàng thay máy bay.

SAU TIẾNG VỖ TAY CÒN VIỆC GÌ?
Một thao tác dùng khí mang theo muốn lặp lại phải còn đủ nguồn khí và trạng thái phù hợp; chỉ nhìn phần trăm pin là chưa đủ.
Chuẩn bị, kiểm tra, quản lý nhiệt và bảo dưỡng là những câu hỏi thuộc vòng vận hành thực tế, dù chúng ít khi được lên hình như cú lộn vòng.
Muốn biết công nghệ hữu ích đến đâu, hãy hỏi cả chuyện trước và sau màn diễn; đó mới là lúc sản phẩm bước ra khỏi đoạn video đẹp.

ĐỘI LÀM VIỆC KHÔNG CHỈ CÓ VÒI PHỤT
Nhìn các góc cận cảnh, câu chuyện còn gồm hình dáng khí động, cơ cấu chuyển động và cách bố trí không gian; nhiều hệ thống cùng chia sẻ một thân xe.
Mỗi thay đổi có thể tác động đến thứ khác, nên ghép chúng thành một thiết kế hoạt động được thường khó hơn việc kể tên từng món.
Cappy gọi đây là bài làm nhóm mà không ai được trốn: quạt, vòi phụt, bánh và phần điều khiển đều phải xuất hiện đúng phần của mình.

ĐỪNG NHẦM MỘT CỘT MỐC VỚI ĐÍCH ĐẾN
Roadster mới đã được Tesla giới thiệu từ năm hai nghìn không trăm mười bảy; theo dõi một sản phẩm cũng là theo dõi cách nó thay đổi qua thời gian.
Một màn giới thiệu mới cho thêm thông tin, nhưng mốc giới thiệu, mốc sản xuất và trải nghiệm sử dụng thực tế vẫn cần được đọc riêng.
Người xem có thể vừa hào hứng với kỹ thuật vừa tiếp tục hỏi về sản phẩm; sự tò mò và thói quen kiểm chứng hoàn toàn có thể ngồi chung một chiếc xe.

GHÉP BA MẢNH LẠI VỚI NHAU
Giờ quay lại ba chiếc thẻ: bám liên quan đến tiếp xúc và lực ép, đẩy liên quan đến thay đổi chuyển động, điều khiển liên quan đến đúng tư thế.
Một màn biểu diễn có thể kết hợp cả ba, nên sẽ thiếu nếu chỉ tìm một chiếc quạt hay một vòi phụt rồi tuyên bố đã giải thích xong.
Nhìn được từng nhiệm vụ và cách chúng phối hợp, bạn đã có một cách xem công nghệ hữu ích hơn nhiều so với chỉ hỏi ngầu hay không ngầu.

VẬY LÀ CÔNG NGHỆ HAY BÁNH VẼ?
Những nguyên lý chúng ta vừa xem đều có cơ sở vật lý; phần táo bạo nằm ở cách ghép chúng vào một chiếc ô tô và kiểm soát cả hệ thống.
Nhưng một cú nhào lộn đẹp chưa trả lời hết chuyện thời gian hoạt động, điều kiện sử dụng hay trải nghiệm của một sản phẩm đến tay khách hàng.
Vì thế, hãy thưởng thức màn trình diễn và giữ lại ba câu hỏi: lực từ đâu, được bao lâu, trong điều kiện nào; hào hứng vẫn có thể đi cùng tỉnh táo.

CÒN BẠN, BẠN NGHĨ SAO?
Bạn thấy Roadster là bước tiến thú vị hay một màn biểu diễn còn nhiều câu hỏi: hãy bình luận lựa chọn của bạn và lý do ở bên dưới nhé.
Nếu cách giải thích này giúp bạn hiểu rõ hơn, cho Cappy một lượt thích và nhấn đăng ký kênh để cùng bóc tách những công nghệ tiếp theo.
Mình là Cappy, cảm ơn bạn đã xem đến đây; hẹn gặp lại trong video sau, còn bây giờ mình đi tìm chỗ gửi xe, chỗ gửi bầu trời tính sau.
'''
groups = [g.strip().splitlines() for g in RAW.strip().split('\n\n')]
assert len(groups) == 36 and all(len(g) == 4 for g in groups)
old = json.loads((OLD / 'src/script.json').read_text(encoding='utf-8'))
blocks = []
for i, lines in enumerate(groups):
    blocks.append(dict(id=f's{i:02}', index=i, title=f'{i+1:02} · {lines[0]}',
        visual=old['blocks'][i]['visual'], sentences=lines[1:], text=' '.join(lines[1:]),
        fromFrame=i*600, duration=600, audioTargetSeconds=18.4))
data = dict(fps=30, duration=21600, seconds=720,
    voice_reference='../voice-clone-CwiDlwRJdYs/voice/voice-prompt.pt', blocks=blocks)
(ROOT / 'src/script.json').write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
(ROOT / 'src/captions.json').write_text('{}', encoding='utf-8')
(ROOT / 'src/ready.json').write_text('[]', encoding='utf-8')
(ROOT / 'src/audio-ready.json').write_text('{"ready":false}', encoding='utf-8')
(ROOT / 'KICH-BAN.md').write_text('# Xe bay Tesla: ngầu thật, nhưng bay được đến đâu?\n\n' +
    '\n\n'.join(f"## {i*20//60:02}:{i*20%60:02} — {b['title']}\n\n" + '\n\n'.join(b['sentences']) for i,b in enumerate(blocks)), encoding='utf-8')
package = json.loads((ROOT / 'package.json').read_text())
package['name'] = 'tesla-cappy-skillry-v3'
package['scripts']['dev'] = 'remotion studio src/index.tsx --port=3145'
package['scripts']['render'] = 'remotion render src/index.tsx TeslaCappySkillry Tesla-Cappy-Skillry-1080p.mp4 --codec=h264 --crf=17 --x264-preset=medium --concurrency=3 --image-format=png'
(ROOT / 'package.json').write_text(json.dumps(package, indent=2), encoding='utf-8')
print(f'Created {ROOT}; {len(blocks)} sections; {sum(len(b["text"].split()) for b in blocks)} Vietnamese tokens')
