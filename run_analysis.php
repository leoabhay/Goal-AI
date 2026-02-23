<?php
set_time_limit(3600);

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $video_path = null;

    if (!empty($_POST['demo_video'])) {
        $demo_name = $_POST['demo_video'];
        $video_path = realpath(__DIR__ . "/demo_videos/" . $demo_name);
    } else if (isset($_FILES['file']) && $_FILES['file']['error'] === UPLOAD_ERR_OK) {
        $upload_dir = __DIR__ . "/uploads/";
        if (!file_exists($upload_dir)) mkdir($upload_dir, 0777, true);
        $target_file = $upload_dir . basename($_FILES['file']['name']);
        if (move_uploaded_file($_FILES['file']['tmp_name'], $target_file)) {
            $video_path = realpath($target_file);
        }
    }

    if (!$video_path || !file_exists($video_path)) {
        echo json_encode(['status' => 'error', 'message' => 'Invalid video path']);
        exit;
    }

    $script_path = realpath(__DIR__ . "/python/main.py");
    $python_cmd = "python";
    $command = $python_cmd . " " . escapeshellarg($script_path) . " " . escapeshellarg($video_path);
    
    // Reset progress
    file_put_contents(__DIR__ . "/python/progress.txt", "0");

    // Run in background on Windows
    // We use popen/pclose to start the process without waiting
    $log_file = __DIR__ . "/python/last_run.log";
    $cmd = "start /B " . $command . " > " . escapeshellarg($log_file) . " 2>&1";
    pclose(popen($cmd, "r"));

    echo json_encode(['status' => 'success', 'video' => $video_path]);
    exit;
}
?>