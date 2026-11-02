# English Live Quiz

Trang dọc dành cho TikTok LIVE. Người xem bình luận nghĩa tiếng Việt của từ tiếng Anh; mỗi người được một điểm cho mỗi vòng trả lời đúng. Cầu nối giữ vòng chơi và bảng xếp hạng đồng bộ giữa trang điều khiển và trang hiển thị.

Bộ 124 từ dùng các mục tiếng Anh, nghĩa tiếng Việt và phiên âm từ [minhqnd/dictionary](https://github.com/minhqnd/dictionary). Xem [DATA-LICENSE.md](DATA-LICENSE.md) để biết nguồn và giấy phép dữ liệu. Để tạo lại danh sách từ, tải `dictionary.db` của bản phát hành v2.0.0 rồi chạy `python tools/build_dictionary.py đường-dẫn-dictionary.db`.

## Chạy trên máy phát stream

1. Cài Node.js 20 trở lên.
2. Trong thư mục này chạy `npm install` rồi `npm start`.
3. Trên chính máy đang chạy `npm start`, mở website và bấm **LIVE** ở góc phải. Dán link livestream TikTok dạng `https://www.tiktok.com/@tenkenh/live` rồi nhấn **Xác nhận**. Trang sẽ gửi username tới cầu nối và tự chuyển sang phiên đồng bộ. Có thể dùng ô username trong `http://127.0.0.1:3000/?host=1` để kết nối thủ công.
4. Trong OBS hoặc TikTok LIVE Studio, thêm Browser Source với URL `http://127.0.0.1:3000/?display=1`, kích thước 480 × 850. Trang hiển thị thông thường không có điều khiển của chủ phòng.
5. Nhấn **Tạo link đồng bộ** trên trang chủ phòng. Sao chép link hiện ra và mở trên điện thoại hoặc máy khác. Các màn hình dùng cùng từ, đồng hồ, bình luận và bảng xếp hạng. Link này chỉ dùng được khi `npm start` và Cloudflare Tunnel còn chạy; sau khi khởi động lại cầu nối, hãy tạo link mới. Máy phát cần cài `cloudflared` để tạo link.

Mỗi từ có 15 giây để đoán. Nếu chưa ai trả lời đúng, đáp án hiện trong 5 giây rồi trang tự chuyển sang từ khác; nếu đã có người trả lời đúng, trang chuyển từ ngay khi hết 15 giây. Thanh ngang thu từ phải sang trái theo thời gian còn lại. Các nút **Từ tiếp** và **Hiện đáp án** nằm trong **Điều khiển cho chủ phòng**; nút **Gửi thử** dùng để kiểm tra bình luận, chấm điểm và tiếng ting trước buổi LIVE. Có thể nhập đáp án không dấu; mỗi người chỉ ghi điểm một lần trong một vòng.

Bình luận và bảng xếp hạng dùng tên hiển thị cùng ảnh đại diện từ sự kiện TikTok LIVE. Nếu ảnh không có hoặc tải lỗi, trang hiện chữ cái đầu của tên.

Khi tắt cầu nối, điểm số của buổi chơi trên máy được đặt lại. Link Site trực tuyến thông thường là bản xem thử và chơi thử cho đến khi kết nối LIVE. Nút LIVE cần được bấm trên máy chạy cầu nối; điện thoại hoặc máy khác dùng link đồng bộ để xem. Link được tạo ở bước 5 là trang xem chỉ đọc qua cầu nối trên máy phát. Link tạm có thể được mở bởi bất kỳ ai có link, nên chỉ chia sẻ với người cần xem. Site vẫn giữ quyền truy cập riêng hiện tại.

Cầu nối dùng thư viện TikTok LIVE không chính thức, nên TikTok có thể thay đổi giao thức. Phải chạy cầu nối trên máy phát stream để nhận bình luận thật.
