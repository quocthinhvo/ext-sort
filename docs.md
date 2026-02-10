# Hướng dẫn sử dụng chương trình Minh họa Sắp xếp Ngoại

Ứng dụng này minh họa trực quan quá trình sắp xếp ngoại (External Merge Sort) sử dụng Python và PyQt6.

## 1. Yêu cầu hệ thống

Đảm bảo bạn đã cài đặt Python. Cài đặt các thư viện cần thiết bằng lệnh:

```bash
pip install -r requirements.txt
```

## 2. Chạy chương trình

Mở terminal tại thư mục chứa mã nguồn và chạy lệnh:

```bash
python main.py
```

## 3. Hướng dẫn sử dụng

### Bước 1: Tạo dữ liệu mẫu
- Nhấn vào nút **Generate Random Data**.
- Nhập số lượng phần tử cần tạo (mặc định 100).
- Chọn vị trí lưu file (ví dụ: `data.bin`) và nhấn **Save**.
- Chương trình sẽ tạo ra một file nhị phân chứa các số thực ngẫu nhiên.

### Bước 2: Chọn tập tin dữ liệu
- Nếu bạn đã có file dữ liệu, nhấn **Select Input File** để chọn file `.bin` cần sắp xếp.
- Tên file sẽ hiển thị bên cạnh nút chọn.

### Bước 3: Cấu hình tham số
- **Chunk Size**: Điều chỉnh kích thước bộ nhớ giả lập. Số lượng phần tử được đọc vào bộ nhớ mỗi lần (Run). Giá trị càng nhỏ thì số lượng file tạm (Run) càng nhiều.
- **Delay (s)**: Thời gian trễ giữa các bước gộp (merge). Tăng giá trị này để quan sát quá trình gộp chậm hơn (ví dụ: 0.1s - 0.5s).

### Bước 4: Bắt đầu sắp xếp
- Nhấn nút **Start Sort** để bắt đầu quá trình.
- Các nút điều khiển sẽ được kích hoạt:
    - **Pause**: Tạm dừng quá trình sắp xếp.
    - **Resume**: Tiếp tục sắp xếp tự động.
    - **Next Step**: Khi đang tạm dừng, nhấn nút này để thực hiện từng bước gộp một.

## 4. Giải thích giao diện

- **Original File (First 100)**: Hiển thị 100 số đầu tiên của file gốc chưa sắp xếp.
- **Sorted Runs (in Memory/Temp)**: 
    - Hiển thị các block dữ liệu (Run) đã được sắp xếp nội bộ.
    - Mỗi cột tương ứng với một Run.
    - Ô được tô màu **xanh lá cây** là giá trị đang được lấy ra để đưa vào file kết quả.
- **Merged Output**: Hiển thị file kết quả đang dần được hình thành từ việc gộp các Run.
