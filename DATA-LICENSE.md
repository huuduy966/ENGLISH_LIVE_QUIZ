# Nguồn dữ liệu từ điển

Danh sách câu đố trong `dist/words.js` được lọc và chuyển thể từ cơ sở dữ liệu [minhqnd/dictionary](https://github.com/minhqnd/dictionary), bản phát hành v2.0.0, tác giả [@minhqnd](https://dict.minhqnd.com).

Dữ liệu nguồn và danh sách chuyển thể được sử dụng theo giấy phép [Creative Commons Attribution-ShareAlike 4.0](https://creativecommons.org/licenses/by-sa/4.0/). Có thể chia sẻ và chỉnh sửa danh sách này theo cùng giấy phép, đồng thời ghi công tác giả và dẫn nguồn.

Tệp `tools/curated_words.json` giữ 149 nghĩa tiếng Việt đã được biên tập; `tools/meaning_overrides.json` lưu các nghĩa được sửa trong trang quản trị. `tools/build_dictionary.py` chỉ tạo `dist/words.js` từ danh sách này, không tự thêm mục từ từ cơ sở dữ liệu. Một số phiên âm thiếu trong nguồn được bổ sung thủ công.
