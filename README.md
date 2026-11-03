# English Live Quiz

Trang dọc dành cho TikTok LIVE. Màn hình hiện nghĩa tiếng Việt; người xem bình luận từ tiếng Anh tương ứng. Mỗi người được một điểm cho mỗi vòng trả lời đúng. Cầu nối giữ vòng chơi và bảng xếp hạng đồng bộ giữa trang điều khiển và trang hiển thị.

Bộ 4.007 từ chơi được lấy từ các mục tiếng Anh phổ biến có nghĩa tiếng Việt ngắn và phiên âm trong [minhqnd/dictionary](https://github.com/minhqnd/dictionary). Bộ 124 từ đã kiểm tra thủ công vẫn được giữ nguyên. `tools/meaning_overrides.json` ưu tiên nghĩa thông dụng cho các từ mà mục từ gốc liệt kê nghĩa hiếm trước, ví dụ **list → danh sách**. Các từ ghép tự động, dạng chia động từ, đáp án quá dài và từ quá hiếm được loại khỏi trò chơi. Xem [DATA-LICENSE.md](DATA-LICENSE.md) để biết nguồn và giấy phép dữ liệu. Để tạo lại danh sách từ, tải `dictionary.db` của bản phát hành v2.0.0, chạy `python -m pip install -r tools/requirements.txt` rồi `python tools/build_dictionary.py đường-dẫn-dictionary.db`.

## Chạy trên máy phát stream

1. Cài Node.js 20 trở lên.
2. Trong thư mục này chạy `npm install` rồi `npm start`.
3. Mở `http://127.0.0.1:3000/`, nhấn biểu tượng ✳ để vào trang quản trị, nhập TikTok username hoặc link LIVE rồi nhấn **Kết nối** khi kênh đang LIVE. Từ Site online, biểu tượng ✳ cũng dẫn tới trang quản trị và có nút mở cầu nối trên máy livestream.
4. Trong OBS hoặc TikTok LIVE Studio, thêm Browser Source với URL `http://127.0.0.1:3000/?display=1`, kích thước 480 × 850. Trang hiển thị thông thường không có điều khiển của chủ phòng.
5. Nhấn **Tạo link đồng bộ** trên trang chủ phòng. Sao chép link hiện ra và mở trên điện thoại hoặc máy khác. Các màn hình dùng cùng từ, đồng hồ, bình luận và bảng xếp hạng. Link này chỉ dùng được khi `npm start` và Cloudflare Tunnel còn chạy; sau khi khởi động lại cầu nối, hãy tạo link mới. Máy phát cần cài `cloudflared` để tạo link.

Mỗi từ có 15 giây để đoán. Nếu chưa ai trả lời đúng, từ tiếng Anh và phiên âm hiện trong 5 giây rồi trang tự chuyển sang từ khác; nếu đã có người trả lời đúng, trang chuyển từ ngay khi hết 15 giây. Thanh ngang thu từ phải sang trái theo thời gian còn lại. Trang quản trị có các nút **Từ tiếp**, **Hiện đáp án**, **Bỏ từ khó**, **Lưu nghĩa** và **Ngắt kết nối**. Khi gặp nghĩa sai, sửa ô nghĩa tiếng Việt rồi nhấn **Lưu nghĩa**; sửa đổi được ghi vào `tools/meaning_overrides.json`, áp dụng ngay trên các màn hình đồng bộ và từ hiện tại được bỏ qua để bắt đầu vòng mới. Nút **Bỏ từ khó** loại từ hiện tại khỏi các vòng sau, lưu danh sách tại `excluded-words.json` trên máy livestream và chuyển ngay sang từ mới. **Ngắt kết nối** dừng nhận bình luận TikTok mà vẫn giữ vòng chơi và điểm hiện có. Bình luận tiếng Anh không phân biệt chữ hoa, chữ thường; mỗi người chỉ ghi điểm một lần trong một vòng.

Bình luận và bảng xếp hạng dùng tên hiển thị cùng ảnh đại diện từ sự kiện TikTok LIVE. Nếu ảnh không có hoặc tải lỗi, trang hiện chữ cái đầu của tên.

Khi tắt cầu nối, điểm số của buổi chơi trên máy được đặt lại. Link Site trực tuyến thông thường chỉ hiển thị từ và đồng hồ độc lập; điện thoại hoặc máy khác dùng link đồng bộ để xem phiên LIVE. Link được tạo ở bước 5 là trang xem chỉ đọc qua cầu nối trên máy phát. Link tạm có thể được mở bởi bất kỳ ai có link, nên chỉ chia sẻ với người cần xem. Site vẫn giữ quyền truy cập riêng hiện tại.

Tiếng ting tự bật khi có người trả lời đúng, tối đa một lần mỗi 2 giây. Một số trình duyệt chặn âm thanh tự phát cho đến khi người xem nhấp hoặc chạm vào trang lần đầu; với OBS Browser Source, cần cho phép âm thanh tự phát trong nguồn trình duyệt nếu nguồn không phát tiếng.

Cầu nối dùng thư viện TikTok LIVE không chính thức, nên TikTok có thể thay đổi giao thức. Phải chạy cầu nối trên máy phát stream để nhận bình luận thật.
