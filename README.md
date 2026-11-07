# English Practice — Tiếng Anh thương mại & Quản lý

> 🌐 **Link học trực tuyến chính thức:** **[https://nguyendang3103.github.io/english-practice/](https://nguyendang3103.github.io/english-practice/)**
>
> *(Hỗ trợ đầy đủ âm thanh, nhận diện giọng nói chấm phát âm và điền từ email. Mở bằng Safari / Chrome trên điện thoại rồi chọn **"Thêm vào màn hình chính"** để dùng như App).*

---

App học tiếng Anh chuyên biệt cho vai trò Manager và công việc thực tế (xuất nhập khẩu, logistics, supply chain, đàm phán, họp đối tác và viết email thương mại).

---

## Tính năng chính

- 📚 **32 chủ đề thương mại chuyên sâu:** 640 từ vựng và cụm từ thực tế, 192 câu quiz, 74 tình huống đối thoại, 154 câu Coach phản xạ nhanh, 32 email mẫu.
- 🔁 **Ôn tập ngắt quãng (SRS):** Tự động lên lịch ôn theo thuật toán Leitner (hộp 0 đến 6: 1, 1, 3, 7, 14, 30, 60 ngày).
- 🎙️ **Luyện nói & Chấm giọng:** Nhận diện giọng nói qua microphone, đối chiếu và chấm điểm phần trăm độ chính xác.
- ✉️ **Viết & Điền từ email:** 32 bức email thương mại thực tế với các vị trí khuyết từ quan trọng, kiểm tra đáp án và phân tích cấu trúc.
- ☁️ **Đồng bộ đám mây GitHub Gist:** Tự động lưu tiến độ lên Secret Gist trên tài khoản GitHub cá nhân, học liên tục giữa máy tính và điện thoại.

---

## Cấu trúc thư mục

| Đường dẫn | Mô tả |
| --- | --- |
| `index.html` | Ứng dụng web SPA độc lập (chạy trên trình duyệt máy tính, điện thoại, PWA). |
| `data/en.json` | Toàn bộ dữ liệu 32 chủ đề bài học tiếng Anh. |
| `audio/` | 37 gói âm thanh base64 chất lượng cao phục vụ phát âm từng từ và câu. |
| `notes/` | Tài liệu ghi chú và lộ trình học tập chi tiết trong Obsidian. |
| `tools/` | Công cụ build và đóng gói dữ liệu. |

---

## Cách chạy thử trên máy tính (Local)

Mở terminal trong thư mục này và chạy:

```bash
python -m http.server 8000
```

Sau đó mở trình duyệt tại: **http://localhost:8000**
