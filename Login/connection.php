<?php
// Database credentials
$host = 'localhost';
$dbUsername = 'root';
$dbPassword = '';
$dbName = 'pricely';

// Create a connection
$conn = new mysqli($host, $dbUsername, $dbPassword, $dbName);

// Check connection
if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}
echo "Connected successfully";

// Close the connection (optional)
?>
