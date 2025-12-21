# Đồ án 02: Hashiwokakero Solver
**Môn học:** CSC14003 - Nhập môn Trí tuệ nhân tạo (AI)
**Ngôn ngữ:** Python 3.7+

## 1. Giới thiệu
Dự án này tập trung vào việc giải quyết trò chơi logic **Hashiwokakero** (Bridges) bằng các phương pháp khác nhau. Mục tiêu là kết nối các đảo (island) bằng các cây cầu sao cho số lượng cầu tại mỗi đảo khớp với con số ghi trên đảo đó và tất cả các đảo tạo thành một thành phần liên thông duy nhất.

Dự án triển khai 4 thuật toán chính để so sánh:
*   **Bruteforce:** Tìm kiếm vét cạn kết hợp kiểm tra ràng buộc.
*   **Backtracking (DPLL):** Quay lui kết hợp Unit Propagation (Lan truyền đơn vị) dựa trên logic mệnh đề.
*   **A\* Search:** Tìm kiếm tối ưu với hàm heuristic dựa trên số lượng clause chưa thỏa mãn.
*   **PySAT:** Sử dụng thư viện SAT solver của python để giải quyết bài toán dưới dạng CNF.

---

## 2. Cấu trúc mã nguồn
```
.
├── main.py                 # File thực thi chính (CLI), chạy các solver
├── Hashiwokakero.py        # Định nghĩa bài toán, sinh ràng buộc CNF, kiểm tra liên thông
├── BaseSolver.py           # Lớp trừu tượng (Abstract Class) cho các thuật toán giải
├── AStarSolver.py          # Thuật toán A* cho SAT
├── Backtracking.py         # Thuật toán quay lui (DPLL + Unit Propagation)
├── Bruteforce.py           # Thuật toán tìm kiếm vét cạn
├── visualize.py            # Script vẽ biểu đồ so sánh Time/Memory (với Time, trục Y sử dụng Log Scale)
├── Inputs/                 # Thư mục chứa các file input mẫu (.txt) phân loại theo size
│   ├── 7x7/
│   ├── 9x9/
│   └── ...
└── Outputs/                # Thư mục chứa kết quả sau khi chạy
    ├── astar/              # Thư mục chứa output của thuật toán A*
    ├── backtracking/       # Thư mục chứa output của thuật toán backtracking
    ├── brute-force/        # Thư mục chứa output của thuật toán brute-force
    ├── pysat/              # Thư mục chứa output khi dùng thư viện pySAT
    ├── cnf/                # Các file ràng buộc logic định dạng DIMACS .cnf
    ├── Summary/            # Các file .csv lưu thống kê Time, Memory, Stats
    └── Visualization/      # Ảnh biểu đồ so sánh (.png)
```
**Note**: Ngoài ra còn 1 file **auto-run.py** tự động chạy tất cả các thuật toán
---

## 3. Cài đặt môi trường
Dự án yêu cầu các thư viện xử lý dữ liệu và logic mệnh đề. Bạn có thể cài đặt thông qua `pip`:

```bash
pip install numpy python-sat pandas matplotlib
```

---

## 4. Hướng dẫn chạy chương trình

### 4.1. Chạy Solver để giải bài toán
Sử dụng `main.py` với các tham số:
*   `-a`: Thuật toán (`bruteforce`, `backtracking`, `astar`, `pysat`)
*   `-f`: Đường dẫn tới file input.

**Ví dụ:**
```bash
# Giải map 11x11 bằng thuật toán A*
python main.py -a astar -f Inputs/11x11/input-01.txt

# Giải map 7x7 bằng quay lui
python main.py -a backtracking -f Inputs/7x7/input-02.txt
```

Hoặc chạy tất cả (bruteforce tốn thời gian rất lâu):
```
python auto-run.py
```

### 4.2. Vẽ biểu đồ so sánh
Sau khi đã chạy xong các thuật toán cho các map và có dữ liệu trong thư mục `Outputs/Summary/`, hãy chạy script sau để xuất biểu đồ:

```bash
python visualize.py
```
*   **Kết quả:** Ảnh so sánh sẽ được lưu tại `Outputs/Visualization/`.
*   **Lưu ý:** Biểu đồ thời gian sử dụng **Thang đo Log (Log Scale)** để thể hiện rõ sự chênh lệch giữa các thuật toán.

---

## 5. Các thuật toán triển khai

1.  **CNF Encoding:** Toàn bộ luật chơi của Hashi được chuyển đổi sang dạng logic mệnh đề (Conjunctive Normal Form). Bao gồm ràng buộc về số cầu, ràng buộc không cắt nhau và ràng buộc đảo cô lập.
2.  **A\* Search:** Sử dụng trạng thái gán biến SAT làm nút trong cây tìm kiếm. Heuristic $h(n)$ là số lượng mệnh đề (clauses) chưa được thỏa mãn.
3.  **Backtracking:** Cải tiến với kỹ thuật Unit Propagation để cắt tỉa không gian tìm kiếm sớm, đặc biệt hiệu quả khi số lượng biến lớn.
4.  **Connectivity Check:** Vì CNF chỉ đảm bảo các ràng buộc cục bộ, một bước kiểm tra hậu kỳ (Singly Connected Component) bằng Disjoint Set (DSU) được thực hiện để đảm bảo tính liên thông toàn cầu.

---

## 6. Kết quả thống kê
Mọi kết quả về:
*   **Thời gian thực thi (ms)**
*   **Bộ nhớ tiêu thụ (MB)**
*   **Số lượng Clause/Biến/Node mở rộng**
