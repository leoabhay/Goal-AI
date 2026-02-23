<?php
header('Content-Type: application/json');

$progress_file = __DIR__ . '/python/progress.txt';

if (!file_exists($progress_file)) {
    echo json_encode(['progress' => 0]);
    exit;
}

$progress = (int)file_get_contents($progress_file);
echo json_encode(['progress' => $progress]);
?>