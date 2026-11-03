# Nguồn dữ liệu từ điển

Danh sách câu đố trong `dist/words.js` được lọc và chuyển thể từ cơ sở dữ liệu [minhqnd/dictionary](https://github.com/minhqnd/dictionary), bản phát hành v2.0.0, tác giả [@minhqnd](https://dict.minhqnd.com).

Dữ liệu nguồn và danh sách chuyển thể được sử dụng theo giấy phép [Creative Commons Attribution-ShareAlike 4.0](https://creativecommons.org/licenses/by-sa/4.0/). Có thể chia sẻ và chỉnh sửa danh sách này theo cùng giấy phép, đồng thời ghi công tác giả và dẫn nguồn.

Tệp `tools/curated_words.json` giữ 124 nghĩa đã kiểm tra thủ công; `tools/meaning_overrides.json` sửa những nghĩa hiếm được dữ liệu gốc đặt lên trước; `tools/quiz_words.tsv` là danh sách tuyển chọn ban đầu. `tools/build_dictionary.py` lọc thêm các mục tiếng Anh có nghĩa tiếng Việt ngắn và phiên âm trước khi tạo `dist/words.js`, đồng thời dùng [wordfreq](https://github.com/rspeer/wordfreq/) (Apache-2.0) để loại từ có tần suất quá thấp hoặc viết sai. Tám phiên âm trong danh sách ban đầu bị thiếu hoặc cắt trong dữ liệu nguồn được kiểm tra và sửa theo [Cambridge Dictionary](https://dictionary.cambridge.org/pronunciation/english/careful).
