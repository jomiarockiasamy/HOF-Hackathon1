<?php
$name = $_POST['name'];
$email = $_POST['email'];
$phonenumber = $_POST['phone'];
$cash = $_POST['cashapp'];
$zipcode = $_POST['zipcode'];
$username = $_POST['username'];
$password = $_POST['password'];


if(empty($name) || empty($email) || empty($phonenumber) || empty($cash) || empty($zipcode) || empty($username) || empty($password)) {
    echo "All fields are required.";
    die();
}
else {
    $host = 'localhost';
    $dbusername = 'users';
    $dbname = 'user_info';
}
$conn = new mysqli($host, $dbusername, '', $dbname);
if($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
} else {
    $SELECT = "SELECT username FROM user_profiles WHERE username = ? LIMIT 1";
    $INSERT = "INSERT INTO user_profiles (name, email, phone, cashapp, zipcode, username, password) VALUES (?, ?, ?, ?, ?, ?, ?)";

    $stmt = $conn->prepare($SELECT);
    $stmt->bind_param("s", $username);
    $stmt->execute();
    $stmt->bind_result($username);
    $stmt->store_result();
    $rnum = $stmt->num_rows;
    
    if($rnum==0) {
        $stmt->close();
        $stmt = $conn->prepare($INSERT);
        $stmt->bind_param("ssssiss", $name, $email, $phonenumber, $cash, $zipcode, $username, $password);
        if($stmt->execute()) {
            echo "New record inserted successfully";
        } else {
            echo "Error: " . $stmt->error;
        }
    } else {
        echo "Someone already registered using this username.";
    }
    $stmt->close();
    $conn->close();
}
?>