# Nguồn dữ liệu từ điển

Danh sách câu đố trong `dist/words.js` được tuyển chọn và chuyển thể từ cơ sở dữ liệu [minhqnd/dictionary](https://github.com/minhqnd/dictionary), bản phát hành v2.0.0, tác giả [@minhqnd](https://dict.minhqnd.com).

Dữ liệu nguồn và danh sách chuyển thể được sử dụng theo giấy phép [Creative Commons Attribution-ShareAlike 4.0](https://creativecommons.org/licenses/by-sa/4.0/). Có thể chia sẻ và chỉnh sửa danh sách này theo cùng giấy phép, đồng thời ghi công tác giả và dẫn nguồn.

Tệp `tools/quiz_words.tsv` chứa cách chọn nghĩa phù hợp với trò chơi. `tools/build_dictionary.py` xác nhận từng nghĩa với mục từ tiếng Anh trong cơ sở dữ liệu và lấy cách phát âm trước khi tạo `dist/words.js`.
