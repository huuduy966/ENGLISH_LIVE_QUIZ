# English Live Quiz

Trang dọc dành cho TikTok LIVE. Người xem bình luận nghĩa tiếng Việt của từ tiếng Anh; mỗi người được một điểm cho mỗi vòng trả lời đúng. Cầu nối giữ vòng chơi và bảng xếp hạng đồng bộ giữa trang điều khiển và trang hiển thị.

## Chạy trên máy phát stream

1. Cài Node.js 20 trở lên.
2. Trong thư mục này chạy `npm install` rồi `npm start`.
3. Mở `http://127.0.0.1:3000`, vào **Điều khiển cho chủ phòng**, nhập TikTok username và nhấn **Kết nối** khi kênh đang LIVE.
4. Trong OBS hoặc TikTok LIVE Studio, thêm Browser Source với URL `http://127.0.0.1:3000/?display=1`, kích thước 480 × 850. URL này ẩn điều khiển của chủ phòng.

Nút **Gửi thử** dùng để kiểm tra bình luận, chấm điểm và tiếng ting trước buổi LIVE. Bấm **Từ tiếp** để chuyển vòng, **Hiện đáp án** để mở đáp án. Có thể nhập đáp án không dấu; mỗi người chỉ ghi điểm một lần trong một vòng.

Khi tắt cầu nối, điểm số của buổi chơi trên máy được đặt lại. Bản Site trực tuyến là bản xem thử và chơi thử; việc nhận bình luận TikTok trực tiếp chạy qua URL localhost ở trên.

Cầu nối dùng thư viện TikTok LIVE không chính thức, nên TikTok có thể thay đổi giao thức. Phải chạy cầu nối trên máy phát stream để nhận bình luận thật.
