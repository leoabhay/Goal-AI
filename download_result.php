<?php
$output_video_path = __DIR__ . "/output_videos/output_video.mp4";

if (file_exists($output_video_path)) {
    header("Content-Type: video/mp4");
    header("Content-Disposition: attachment; filename=\"analyzed_video.mp4\"");
    header("Content-Length: " . filesize($output_video_path));
    readfile($output_video_path);
    exit;
} else {
    echo "<h1>Analysis result not found.</h1>";
    echo "<p>Please ensure the analysis completed successfully.</p>";
    echo "<a href='analysis.php'>Go back</a>";
}
?>