# **LockChat: Sassy Secure Chats**

**LockChat** is a secure chat application built using Python, PyQt5, and cryptography. The app offers encrypted messaging, user authentication, and additional features like dark mode, emoji support, and chat visibility toggling. This project is ideal for those interested in learning about secure communications and GUI development in Python.

## **Features**

- **User Authentication:**
  - Account creation with email, username, and password.
  - Secure login with rate limiting to prevent brute force attacks.
  
- **Encryption:**
  - Messages are encrypted using Fernet symmetric encryption.
  - Ensures secure communication between the server and the client.

- **GUI with PyQt5:**
  - User-friendly interface with light/dark mode.
  - Emoji picker for easy emoji insertion in messages.
  - Save chat history to a text file.
  - Toggle chat visibility with PIN protection.

- **Notifications:**
  - Sound notifications for incoming messages.

## **Installation**

### **1. Clone the Repository**
```bash
git clone https://github.com/1cYinfinity/lockchat.git
cd lockchat
```
2. Install Dependencies
Ensure you have Python installed (version 3.7+). Install the required dependencies using pip:
```
pip install -r requirements.txt
```
3. Run the Application
Start the server:
```
python server.py
```
### **4. Set Up the Database (Optional)**

If not already set up, the application will automatically create a `user_db.db` SQLite database in the working directory.

## **Usage**

### **Starting the Server:**

- Run the server script using the command provided above.
- The server will bind to the specified IP and port (`192.168.56.1:1234` by default).

### **Creating an Account:**

- Launch the application and select "Create Account."
- Enter your email, username, and password.

### **Logging In:**

- Select "Login Account" and provide your credentials.
- On successful login, you'll receive a pair code for chat visibility toggling.

### **Sending Messages:**

- Type your message in the input box and click "Send."
- Messages will be encrypted before being sent to the server.

### **Using Emojis:**

- Click the emoji button to open the emoji picker and select your desired emoji.

### **Toggling Dark Mode:**

- Use the moon button (🌙) to switch between light and dark mode.

### **Hiding/Unhiding Chat:**

- Use the "Hide Chat" button to hide the chat window. You'll need the pair code to unhide it.

### **Saving Chat History:**

- Click "Save" to store the chat history in a text file.

## **Security Considerations**

- **Password Security:** Passwords are stored in plain text in the database. It's recommended to implement password hashing (e.g., using `bcrypt`) before using this application in a production environment.

- **Encryption Key Management:** Ensure the encryption key is stored securely. Avoid hardcoding it in the source code for production use.

## **Contributing**

Contributions are welcome! Feel free to submit a pull request or open an issue to discuss any changes or improvements.

## **License**

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

## **Acknowledgments**

- This project uses the [PyQt5](https://pypi.org/project/PyQt5/) library for the graphical user interface.
- Encryption is handled by the [cryptography](https://pypi.org/project/cryptography/) library.
