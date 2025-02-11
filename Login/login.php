<?php
include 'connection.php';
session_start(); // Start the session
error_reporting(E_ALL);
ini_set('display_errors', 1);

// Initialize message variables 
$_SESSION['error'] = '';

// Check if form is submitted
if ($_SERVER['REQUEST_METHOD'] == 'POST') {
    // Check if it's a registration or login
    if (isset($_POST['register'])) {
        // Registration
        $email = $_POST['email'];
        $password = $_POST['password'];

        // Prepare and bind for insertion
        $stmt = $conn->prepare("INSERT INTO accounts (email, password) VALUES (?, ?)");
        if (!$stmt) {
            die("Prepare failed: " . $conn->error);
        }
        $stmt->bind_param("ss", $email, $password);
        
        // Execute statement
        if ($stmt->execute()) {
            $_SESSION['success'] = "User registered successfully!";
        } else {
            $_SESSION['error'] = "Error: " . $stmt->error;
        }

        // Close the statement
        $stmt->close();
    } else {
        // Login
        $email = $_POST['email'];
        $password = $_POST['password'];
        
        // Prepare and bind
        $sql = "SELECT password FROM accounts WHERE email = ?";
        $stmt = $conn->prepare($sql);
        if (!$stmt) {
            die("Prepare failed: " . $conn->error);
        }
        $stmt->bind_param("s", $email);
        
        // Execute statement
        if (!$stmt->execute()) {
            die("Execute failed: " . $stmt->error);
        }
        $stmt->store_result();
        
        // Check if email exists
        if ($stmt->num_rows > 0) {
            // Bind result
            $stmt->bind_result($storedPassword);
            $stmt->fetch();
            
            // Check if the provided password matches the stored one
            if ($password === $storedPassword) {
                // Login successful
                $_SESSION['email'] = $email; // Store email in session
                header("Location: ../Home/index.html"); // Redirect to home page
                exit();
            } else {
                // Redirect to invalid.html on invalid password
                header("Location: ../Login/invalid.html");
                exit();
            }   
        } else {
            // Redirect to invalid.html if no user found
            header("Location: ../Login/invalid.html");
            exit();
        }
        
        // Close the statement
        $stmt->close();
    }
}

// Close the connection after all operations
$conn->close();
?>
