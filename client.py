from utils import *

# Create a socket and connect to the server
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(("192.168.56.1", 1234))  # Server IP and port

# Create or connect to the user database
user_db = sqlite3.connect("user_db.db")
user_cursor = user_db.cursor()

# Create a table to store user accounts if it doesn't exist
user_cursor.execute("""
   CREATE TABLE IF NOT EXISTS users (
       id INTEGER PRIMARY KEY,
       email TEXT UNIQUE,
       username TEXT UNIQUE,
       password TEXT
   )
""")

user_db.commit()

# Encryption key
key = b'aSSXEMHjtMGAWoNutRbB096AiK_irBJBgk7-2Lh92A4='
cipher_suite = Fernet(key)

# Create a PyQt5 window for the client
class ClientWindow(QMainWindow):
    messageReceived = pyqtSignal(str)  # Define the signal for message reception
    def __init__(self, client_socket):
        super().__init__()
        self.client_socket = client_socket
        self.init_ui()
        self.setStyleSheet("background: qlineargradient(x1:0, y1:0, x2:0, y2:1,"
                           "stop:0 #ADD8E6, stop:1 #FFFFFF);"
                           "color: black")
        self.light_mode = True  # Added variable to track the mode
        
    def init_ui(self):
        self.setWindowTitle("LockChat: Sassy Secure Chats")
        self.setGeometry(100, 100, 400, 400)
        self.layout = QVBoxLayout()
        self.pair_code = self.generate_pair_code()
        self.login_attempts = {}  # Store login attempts here
        self.message_buttons = {}
        self.is_chat_hidden = False  # Initially, chat is not hidden

        # Create a text browser for displaying messages
        self.text_browser = QTextBrowser(self)
        self.layout.addWidget(self.text_browser)

        # Create a layout for buttons (Hide Chat and Dark Mode)
        buttons_layout = QHBoxLayout()

        input_send_layout = QVBoxLayout()
        input_box_layout = QHBoxLayout()

        # Create an emoji button
        emoji_button = QPushButton("😀", self)  # You can set any emoji you like as the button text
        emoji_button.clicked.connect(self.open_emoji_picker)
        input_box_layout.addWidget(emoji_button)

        # Create an input box for typing messages
        self.input_box = QLineEdit(self)
        input_box_layout.addWidget(self.input_box)

        input_send_layout.addLayout(input_box_layout)

        # Create a send button
        send_button = QPushButton("Send", self)
        send_button.clicked.connect(self.send_message)
        input_send_layout.addWidget(send_button)

        # Create a save button
        save_button = QPushButton("Save", self)
        save_button.clicked.connect(self.save_chat)
        input_send_layout.addWidget(save_button)

        self.layout.addLayout(input_send_layout)
        
        # Create a button to hide/unhide chat
        self.hide_unhide_button = QPushButton("Hide Chat", self)
        self.hide_unhide_button.clicked.connect(self.toggle_chat_visibility)
        buttons_layout.addWidget(self.hide_unhide_button)

        # Create a dark mode button
        dark_mode_button = QPushButton("🌙", self)
        dark_mode_button.setToolTip("Toggle Dark Mode")
        dark_mode_button.clicked.connect(self.toggle_dark_mode)  # Connect to toggle_dark_mode
        buttons_layout.addWidget(dark_mode_button)

        self.layout.addLayout(buttons_layout)

        self.central_widget = QWidget()
        self.central_widget.setLayout(self.layout)
        self.setCentralWidget(self.central_widget)

        while True:  # Loop for creating an account or logging in
            option, ok = QInputDialog.getItem(self, "Account Options", "Select an option:", ["Create Account", "Login Account"],
                                             0, False)
            if not ok:
                sys.exit(0)  # User closed the dialog, exit the application

            email, password = None, None
            if option == "Create Account":
                email, ok1 = QInputDialog.getText(self, "Create Account", "Enter your email:")
                username, ok2 = QInputDialog.getText(self, "Create Account", "Enter your username:")
                password, ok3 = QInputDialog.getText(self, "Create Account", "Enter your password:")
                self.pair_code = self.generate_pair_code()  # Generate a new PIN code
                if ok1 and ok2 and ok3 and email and username and password:
                    if create_account(email, username, password):
                        QMessageBox.information(self, "Account Creation", "Account created successfully.")
                        self.username = username  # Store the username
                    else:
                        QMessageBox.warning(self, "Account Creation", "Email or username already exists. Please use different ones.")
                else:
                    QMessageBox.warning(self, "Account Creation", "Invalid input.")
            elif option == "Login Account":
                email, ok1 = QInputDialog.getText(self, "Login Account", "Enter your email:")
                password, ok2 = QInputDialog.getText(self, "Login Account", "Enter your password:")

            if option == "Login Account":
                if (email, password) not in login_attempts:
                    login_attempts[(email, password)] = 0

                user_data = login(email, password)
                if user_data:
                    self.username = user_data  # Store the username
                    QMessageBox.information(self, "Login", f"Code is: {self.pair_code}\nLogin successful.")
                    self.receive_messages_thread = threading.Thread(target=self.receive_messages)
                    self.receive_messages_thread.start()
                    break
                else:
                    login_attempts[(email, password)] += 1
                    if login_attempts[(email, password)] >= max_login_attempts:
                        QMessageBox.critical(self, "Login Error", f"Maximum login attempts reached for {email}.")
                        sys.exit(0)

                    QMessageBox.warning(self, "Login", "Invalid email or password.")

    def generate_pair_code(self):
        # Generate a random 4-digit pair code
        return str(random.randint(1000, 9999))
        
    def toggle_chat_visibility(self):
        if self.is_chat_hidden:
            pin, ok = QInputDialog.getText(self, "Enter PIN", "Enter the PIN to see the chat:")
            if ok and pin == self.pair_code:
                self.text_browser.show()
                self.hide_unhide_button.setText("Hide Chat")
                self.is_chat_hidden = False
                # Your existing code for hiding the buttons...
            else:
                QMessageBox.critical(self, "Invalid PIN", "Incorrect PIN. Chat cannot be revealed.")
        else:
            self.text_browser.hide()
            self.hide_unhide_button.setText("Unhide Chat")
            self.is_chat_hidden = True
            
    def receive_messages(self):
        while True:
            try:
                encrypted_message = client_socket.recv(1024)
                if not encrypted_message:
                    continue  # Skip empty messages
                decrypted_message = cipher_suite.decrypt(encrypted_message).decode()
                self.text_browser.append(f'{decrypted_message}')
                self.play_notification_sound()  # Play notification sound
            except Exception as e:
                print(e)
                break
                
    # Add this method to play the notification sound
    def play_notification_sound(self):
        notification_sound = "notif.mp3"  # Replace with the path to your notification sound file
        playsound(notification_sound)
        
    def toggle_dark_mode(self):
        if self.light_mode:
            self.setStyleSheet("background-color: #1E1E1E; color: white;")
        else:
            self.setStyleSheet("background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #ADD8E6, stop:1 #FFFFFF); color: black;")
        self.light_mode = not self.light_mode

    def send_message(self):
        message = self.input_box.text()
        if message:
            full_message = f'{self.username}: {message}'
            encrypted_message = cipher_suite.encrypt(full_message.encode())
            client_socket.send(encrypted_message)  # Send the message via the 'conn' socket
            self.text_browser.append(f'You: {message}')
            self.input_box.clear()
    
    def open_emoji_picker(self):
        emoji_picker = EmojiPicker()
        if emoji_picker.exec_() == QDialog.Accepted:
            selected_emoji = emoji_picker.selected_emoji
            self.input_box.insert(selected_emoji)

    def save_chat(self):
        file_name, _ = QFileDialog.getSaveFileName(self, "Save Chat Messages", "", "Text Files (*.txt);;All Files (*)")
        if file_name:
            with open(file_name, 'w') as file:
                chat_text = self.text_browser.toPlainText()
                file.write(chat_text)
            QMessageBox.information(self, "File Saved", f"Your file has been saved as: {file_name}")

class EmojiPicker(QDialog):
    def __init__(self):
        super().__init__()
        self.selected_emoji = ""
        self.init_ui()

class EmojiPicker(QDialog):
    def __init__(self):
        super().__init__()
        self.selected_emoji = None
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Emoji Picker")
        self.setGeometry(200, 200, 400, 400)
        layout = QVBoxLayout()

        emoji_buttons_layout = QHBoxLayout()

        emojis = ["😀", "😍", "😂", "😎", "👍", "❤️", "👋", "👏", "🔥", "🌟", "🎉", "🍕", "❄️"]

        for emoji_text in emojis:
            emoji_button = QPushButton(emoji.emojize(emoji_text))
            emoji_button.clicked.connect(self.select_emoji)
            emoji_buttons_layout.addWidget(emoji_button)

        layout.addLayout(emoji_buttons_layout)

        button_layout = QHBoxLayout()

        select_button = QPushButton("Select", self)
        select_button.clicked.connect(self.accept)
        cancel_button = QPushButton("Cancel", self)
        cancel_button.clicked.connect(self.reject)

        button_layout.addWidget(select_button)
        button_layout.addWidget(cancel_button)

        layout.addLayout(button_layout)

        self.setLayout(layout)

    def select_emoji(self):
        sender_button = self.sender()
        if sender_button:
            self.selected_emoji = sender_button.text()

def create_account(email, username, password):
    try:
        user_cursor.execute("INSERT INTO users (email, username, password) VALUES (?, ?, ?)", (email, username, password))
        user_db.commit()
        return True
    except sqlite3.IntegrityError:
        return False

# Create a dictionary to store login attempts for each user
login_attempts = {}
# Maximum allowed login attempts before rate limiting kicks in
max_login_attempts = 3
# Delay in seconds before allowing another login attempt after reaching the maximum login attempts
login_attempt_delay = 5

def login(email, password):
    if email in login_attempts:
        if login_attempts[email]["attempts"] >= max_login_attempts:
            current_time = time.time()
            if current_time - login_attempts[email]["timestamp"] < login_attempt_delay:
                return None  # Rate limit exceeded, deny login
            else:
                # Reset login attempts
                login_attempts[email] = {"attempts": 0, "timestamp": current_time}
    else:
        login_attempts[email] = {"attempts": 0, "timestamp": time.time()}

    user_cursor.execute("SELECT username FROM users WHERE email = ? AND password = ?", (email, password))
    result = user_cursor.fetchone()
    if result:
        # Successful login, reset login attempts
        login_attempts[email]["attempts"] = 0
        return result[0]  # Return the username
    else:
        # Increment login attempts
        login_attempts[email]["attempts"] += 1
        return None  # Return None if login fails

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ClientWindow(client_socket)
    window.show()
    sys.exit(app.exec_())
