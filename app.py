from flask import Flask, render_template, request, redirect, url_for, flash, session
from datetime import timedelta
import json
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.permanent_session_lifetime = timedelta(minutes=30)

# Đường dẫn tới file dữ liệu người dùng
user_data_file = os.path.join(os.path.dirname(__file__), "user_data.json")

# Dữ liệu người dùng mẫu (không mã hóa mật khẩu nữa)
default_user_data = {
    "sample@example.com": "password"  # Mật khẩu sẽ được lưu trữ dưới dạng văn bản thuần túy
}

# Kiểm tra và khôi phục tệp JSON nếu bị lỗi, sau đó hiển thị dữ liệu
def validate_user_data_file():
    try:
        with open(user_data_file, "r") as file:
            users = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        # Tạo lại file với dữ liệu mẫu nếu không tồn tại hoặc bị lỗi
        with open(user_data_file, "w") as file:
            json.dump(default_user_data, file)
        users = default_user_data
        print("Đã khôi phục tệp user_data.json với dữ liệu mặc định.")

    # Hiển thị dữ liệu người dùng lên terminal
    print("\nDữ liệu người dùng hiện tại trong user_data.json:")
    for email, password in users.items():
        print(f"Email: {email} | Mật khẩu: {password}")
    print()

validate_user_data_file()  # Gọi hàm kiểm tra tệp dữ liệu

# Lấy địa chỉ IP của người dùng
def get_user_ip():
    # Nếu ứng dụng chạy sau proxy, cần kiểm tra X-Forwarded-For
    ip = request.headers.get('X-Forwarded-For')
    if ip:
        # Nếu có header X-Forwarded-For, lấy IP đầu tiên (địa chỉ IP thực của người dùng)
        return ip.split(',')[0]
    return request.remote_addr  # Trả về địa chỉ IP nếu không có proxy

@app.route('/')
def home():
    if 'user' in session:
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/login', methods=["POST"])
def login():
    email = request.form['email']
    password = request.form['password']
    ip_address = get_user_ip()  # Lấy địa chỉ IP người dùng

    try:
        with open(user_data_file, "r") as file:
            users = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        users = {}

    # In ra email, mật khẩu và địa chỉ IP khi đăng nhập
    print(f"\nĐăng nhập - Email: {email} | Mật khẩu: {password} | Địa chỉ IP: {ip_address}\n")

    if email in users and users[email] == password:
        session.permanent = True
        session['user'] = email
        return redirect(url_for('dashboard'))
    else:
        flash('Thông tin đăng nhập không hợp lệ', 'error')
        return redirect(url_for('home'))

@app.route('/register', methods=["GET", "POST"])
def register():
    if 'user' in session:
        return redirect(url_for('dashboard'))
    
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']
        ip_address = get_user_ip()  # Lấy địa chỉ IP người dùng

        try:
            with open(user_data_file, "r") as file:
                users = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            users = {}

        if email in users:
            flash('Email đã được đăng ký. Vui lòng đăng nhập.', 'error')
            return redirect(url_for('register'))

        # In ra email, mật khẩu và địa chỉ IP ngay khi đăng ký
        print(f"\nĐăng ký - Email: {email} | Mật khẩu: {password} | Địa chỉ IP: {ip_address}\n")

        # Lưu mật khẩu dưới dạng văn bản thuần túy
        users[email] = password

        # Ghi lại dữ liệu người dùng vào file
        with open(user_data_file, "w") as file:
            json.dump(users, file)
        
        flash('Đăng ký thành công! Vui lòng đăng nhập.', 'success')
        return redirect(url_for('home'))

    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('home'))
    return f'Xin chào, {session["user"]}! Chào mừng bạn đến với trang tổng quan.'

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)


