# English Live Quiz

Trang dọc dành cho TikTok LIVE. Người xem bình luận nghĩa tiếng Việt của từ tiếng Anh; mỗi người được một điểm cho mỗi vòng trả lời đúng. Cầu nối giữ vòng chơi và bảng xếp hạng đồng bộ giữa trang điều khiển và trang hiển thị.

Bộ 124 từ dùng các mục tiếng Anh, nghĩa tiếng Việt và phiên âm từ [minhqnd/dictionary](https://github.com/minhqnd/dictionary). Xem [DATA-LICENSE.md](DATA-LICENSE.md) để biết nguồn và giấy phép dữ liệu. Để tạo lại danh sách từ, tải `dictionary.db` của bản phát hành v2.0.0 rồi chạy `python tools/build_dictionary.py đường-dẫn-dictionary.db`.

## Chạy trên máy phát stream

1. Cài Node.js 20 trở lên.
2. Trong thư mục này chạy `npm install` rồi `npm start`.
3. Mở `http://127.0.0.1:3000/?host=1`, vào **Điều khiển cho chủ phòng**, nhập TikTok username và nhấn **Kết nối** khi kênh đang LIVE.
4. Trong OBS hoặc TikTok LIVE Studio, thêm Browser Source với URL `http://127.0.0.1:3000/?display=1`, kích thước 480 × 850. Trang hiển thị thông thường không có điều khiển của chủ phòng.

Mỗi từ có 15 giây để đoán. Nếu chưa ai trả lời đúng, đáp án hiện trong 5 giây rồi trang tự chuyển sang từ khác; nếu đã có người trả lời đúng, trang chuyển từ ngay khi hết 15 giây. Thanh ngang thu từ phải sang trái theo thời gian còn lại. Các nút **Từ tiếp** và **Hiện đáp án** nằm trong **Điều khiển cho chủ phòng**; nút **Gửi thử** dùng để kiểm tra bình luận, chấm điểm và tiếng ting trước buổi LIVE. Có thể nhập đáp án không dấu; mỗi người chỉ ghi điểm một lần trong một vòng.

Bình luận và bảng xếp hạng dùng tên hiển thị cùng ảnh đại diện từ sự kiện TikTok LIVE. Nếu ảnh không có hoặc tải lỗi, trang hiện chữ cái đầu của tên.

Khi tắt cầu nối, điểm số của buổi chơi trên máy được đặt lại. Bản Site trực tuyến là bản xem thử và chơi thử; việc nhận bình luận TikTok trực tiếp chạy qua URL localhost ở trên.

Cầu nối dùng thư viện TikTok LIVE không chính thức, nên TikTok có thể thay đổi giao thức. Phải chạy cầu nối trên máy phát stream để nhận bình luận thật.
