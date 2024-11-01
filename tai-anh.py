import os
import requests
from bs4 import BeautifulSoup
from tkinter import Tk, Label, Entry, Button, filedialog, StringVar, messagebox, Text, Scrollbar, END, Checkbutton, BooleanVar
from urllib.parse import urljoin
from random import choices
import string
import threading
import time

# Hàm để tải ảnh từ URL
def download_images():
    url = url_entry.get()
    img_class_name = img_class_entry.get()
    img_id_name = img_id_entry.get()
    div_class_name = div_class_entry.get()
    div_id_name = div_id_entry.get()
    lazyload = lazyload_var.get()

    # Yêu cầu người dùng chọn thư mục lưu ảnh
    folder_selected = filedialog.askdirectory()
    if not folder_selected:
        messagebox.showwarning("Warning", "Bạn chưa chọn thư mục lưu ảnh!")
        return

    # Tạo tên thư mục ngẫu nhiên (chữ và số)
    folder_name = ''.join(choices(string.ascii_letters + string.digits, k=10))
    save_path = os.path.join(folder_selected, folder_name)
    os.makedirs(save_path, exist_ok=True)

    try:
        response = requests.get(url)
        if response.status_code != 200:
            messagebox.showerror("Error", f"Không thể truy cập trang web: {url}")
            return
        
        # Parse HTML
        soup = BeautifulSoup(response.text, 'html.parser')

        # Xóa nội dung trong text log trước khi bắt đầu tải
        log_text.delete(1.0, END)

        # Kiểm tra class hoặc id của thẻ img được nhập và tìm ảnh theo điều kiện
        images = []
        if img_class_name:
            images = soup.find_all('img', class_=img_class_name)
        elif img_id_name:
            img_tag = soup.find('img', id=img_id_name)
            if img_tag:
                images.append(img_tag)
            else:
                messagebox.showwarning("Warning", f"Không tìm thấy thẻ img với ID: {img_id_name}")
                return
        elif div_class_name or div_id_name:
            # Nếu không có class hoặc id của img, tìm thẻ div bọc ngoài
            divs = []
            if div_class_name:
                divs = soup.find_all('div', class_=div_class_name)
            elif div_id_name:
                div_tag = soup.find('div', id=div_id_name)
                if div_tag:
                    divs.append(div_tag)
                else:
                    messagebox.showwarning("Warning", f"Không tìm thấy thẻ div với ID: {div_id_name}")
                    return
            
            # Tìm thẻ img bên trong các thẻ div
            for div in divs:
                images += div.find_all('img')
        
        if not images:
            messagebox.showinfo("No images", "Không tìm thấy ảnh nào với class hoặc id đã chỉ định.")
            return

        # Nếu lazyload được bật, đợi các ảnh được tải xong
        if lazyload:
            log_text.insert(END, "Trang web sử dụng lazyload, đang đợi ảnh tải xong...\n")
            log_text.see(END)
            time.sleep(5)  # Tùy chỉnh thời gian đợi dựa trên độ dài trang hoặc logic khác

        # Tải ảnh
        count = 0
        for img in images:
            img_url = img.get('src')
            if not img_url.startswith('http'):
                img_url = urljoin(url, img_url)

            try:
                img_data = requests.get(img_url).content
                img_name = os.path.join(save_path, os.path.basename(img_url))
                with open(img_name, 'wb') as handler:
                    handler.write(img_data)
                
                count += 1
                # Cập nhật trạng thái vào khung log
                log_text.insert(END, f"Tải thành công: {img_url}\n")
                log_text.see(END)  # Cuộn xuống dòng cuối cùng
            except Exception as e:
                log_text.insert(END, f"Lỗi khi tải ảnh: {img_url}, lỗi: {e}\n")
                log_text.see(END)  # Cuộn xuống dòng cuối cùng
        
        messagebox.showinfo("Completed", f"Tải thành công {count} ảnh.")
    except Exception as e:
        messagebox.showerror("Error", f"Lỗi: {e}")

# Hàm để chạy quá trình tải ảnh trong một luồng khác
def start_download_thread():
    download_thread = threading.Thread(target=download_images)
    download_thread.start()

# Hàm để xóa sạch log trạng thái
def clear_log():
    log_text.delete(1.0, END)

# Tạo giao diện tkinter
root = Tk()
root.title("Tải ảnh hàng loạt")
root.geometry("500x500")  # Đặt kích thước cửa sổ

# Tùy chỉnh phong cách hiển thị
padding_options = {'padx': 10, 'pady': 5}

# Các widget nhập URL và class HTML
url_label = Label(root, text="Nhập URL:")
url_label.pack(**padding_options)
url_entry = Entry(root, width=50)
url_entry.pack(**padding_options)

# Thêm khung nhập class của thẻ img
img_class_label = Label(root, text="Nhập class của thẻ img (nếu có):")
img_class_label.pack(**padding_options)
img_class_entry = Entry(root, width=50)
img_class_entry.pack(**padding_options)

# Thêm khung nhập ID của thẻ img
img_id_label = Label(root, text="Nhập ID của thẻ img (nếu có):")
img_id_label.pack(**padding_options)
img_id_entry = Entry(root, width=50)
img_id_entry.pack(**padding_options)

# Thêm khung nhập class của thẻ div bao ngoài thẻ img
div_class_label = Label(root, text="Nhập class của thẻ div bao ngoài thẻ img (nếu không có class hoặc id của img):")
div_class_label.pack(**padding_options)
div_class_entry = Entry(root, width=50)
div_class_entry.pack(**padding_options)

# Thêm khung nhập ID của thẻ div bao ngoài thẻ img
div_id_label = Label(root, text="Nhập ID của thẻ div bao ngoài thẻ img (nếu không có class hoặc id của img):")
div_id_label.pack(**padding_options)
div_id_entry = Entry(root, width=50)
div_id_entry.pack(**padding_options)

# Tùy chọn lazyload
lazyload_var = BooleanVar()
lazyload_check = Checkbutton(root, text="Trang web sử dụng lazyload", variable=lazyload_var)
lazyload_check.pack(**padding_options)

download_button = Button(root, text="Tải ảnh", command=start_download_thread, bg="#4CAF50", fg="white", relief="raised")
download_button.pack(**padding_options)

# Thêm Text widget để hiển thị trạng thái tải ảnh
log_label = Label(root, text="Trạng thái tải ảnh:")
log_label.pack(**padding_options)

# Thêm Scrollbar vào khung Text để cuộn khi nội dung dài
scrollbar = Scrollbar(root)
scrollbar.pack(side="right", fill="y")

log_text = Text(root, height=10, width=60, yscrollcommand=scrollbar.set)
log_text.pack(**padding_options)

scrollbar.config(command=log_text.yview)

# Thêm nút Clear để xóa sạch log trạng thái
clear_button = Button(root, text="Clear", command=clear_log, bg="#f44336", fg="white", relief="raised")
clear_button.pack(**padding_options)

# Chạy giao diện
root.mainloop()
