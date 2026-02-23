<?php
set_time_limit(1000);
?>
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>GOAL AI | Smarter Football Analytics</title>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">
  <link rel="stylesheet" href="css/styles.css?v=5">
</head>
<body>

<!-- ── NAVBAR ──────────────────────────────────────────── -->
<div class="navbar-wrap">
  <a href="index.php" class="nav-logo"><i class="fas fa-futbol" style="font-size: 1.5rem; color: var(--accent); margin-right: 0.5rem;"></i>GOAL AI</a>
  <a href="index.php" class="btn-secondary nav-btn" style="margin-left: auto; display: inline-flex; align-items: center; gap: 0.4rem;"><i class="fas fa-arrow-left"></i> <span class="desktop-only">Go Back</span><span class="mobile-only">Back</span></a>
</div>

<div class="page-wrap">
  <!-- ── BANNER ─────────────────────────────────── -->
  <div class="page-banner">
    <h1>Football <span>AI Analysis</span></h1>
    <p>Upload a match video or choose a demo — our AI will track players, measure speed, and analyze possession.</p>
  </div>

  <!-- ── PREDICT/RESULTS LAYOUT ─────────────────────────── -->
  <div class="section">
    <?php if (isset($_GET['status']) && $_GET['status'] === 'complete'): ?>
      <!-- Results View -->
      <div class="result-container glass">
        <div class="result-header">
          <div class="status-badge"><i class="fas fa-check-circle"></i> Analysis Complete</div>
          <h2>Your <span>Analyzed Video</span> is Ready</h2>
          <p>We've processed your footage. You can now view the AI tracking and metrics below.</p>
        </div>
        
        <div class="result-video-wrapper">
          <video id="result-video" controls autoplay muted loop poster="assets/images/football2.jpg">
            <source src="output_videos/output_video.mp4" type="video/mp4">
            Your browser does not support the video tag.
          </video>
        </div>

        <div class="result-actions">
          <a href="download_result.php" class="btn-primary"><i class="fas fa-download"></i> Download Video</a>
          <a href="analysis.php" class="btn-secondary"><i class="fas fa-redo"></i> Analyze Another</a>
        </div>
      </div>
    <?php else: ?>
      <!-- Analysis Form View -->
      <div class="predict-layout">
        <!-- Info side -->
        <div class="predict-info">
          <h2>How It <span>Works</span></h2>
          <p>Our deep learning model detects and tracks every entity on the pitch — delivering professional-grade insights in minutes.</p>
          <div class="predict-feature"><i class="fas fa-user-friends"></i> Player & goalkeeper detection</div>
          <div class="predict-feature"><i class="fas fa-futbol"></i> Ball possession analysis</div>
          <div class="predict-feature"><i class="fas fa-tachometer-alt"></i> Real-time speed & distance metrics</div>
          <div class="predict-feature"><i class="fas fa-camera"></i> Camera movement estimation</div>
          <div class="predict-feature"><i class="fas fa-users"></i> Team-level control statistics</div>
          <div class="alert alert-info" style="margin-top:1rem;">
            <i class="fas fa-info-circle"></i>
            Processing may take 1–5 minutes depending on video length. Please don't close the page.
          </div>
        </div>

        <!-- Form side -->
        <div class="form-card">
          <h2>Analyze Video</h2>
          <p class="sub">Select a demo or upload your own match footage.</p>
          <form id="analysis-form" enctype="multipart/form-data">

            <!-- Demo selection -->
            <div class="form-group">
              <label>Demo Videos</label>
              <div class="demo-options">
                <div class="demo-option">
                  <video src="demo_videos/demo1.mp4" muted loop autoplay playsinline class="demo-vid"></video>
                  <div class="demo-radio-wrap">
                    <input type="radio" name="demo_video" id="d1" value="demo1.mp4">
                    <label for="d1">⚽ Demo 1</label>
                  </div>
                </div>
                <div class="demo-option">
                  <video src="demo_videos/demo2.mp4" muted loop autoplay playsinline class="demo-vid"></video>
                  <div class="demo-radio-wrap">
                    <input type="radio" name="demo_video" id="d2" value="demo2.mp4">
                    <label for="d2">⚽ Demo 2</label>
                  </div>
                </div>
                <div class="demo-option">
                  <video src="demo_videos/demo3.mp4" muted loop autoplay playsinline class="demo-vid"></video>
                  <div class="demo-radio-wrap">
                    <input type="radio" name="demo_video" id="d3" value="demo3.mp4">
                    <label for="d3">⚽ Demo 3</label>
                  </div>
                </div>
                <div class="demo-option">
                  <video src="demo_videos/demo4.mp4" muted loop autoplay playsinline class="demo-vid"></video>
                  <div class="demo-radio-wrap">
                    <input type="radio" name="demo_video" id="d4" value="demo4.mp4">
                    <label for="d4">⚽ Demo 4</label>
                  </div>
                </div>
              </div>
            </div>

            <!-- File upload -->
            <div class="form-group">
              <label>Or Upload Your Own Video</label>
              <div class="file-browse">
                <input type="text" id="file-name" class="input file-name" placeholder="No file selected" readonly style="background:rgba(255,255,255,0.05);border:1px solid var(--glass-border);border-radius:var(--radius-sm);padding:.75rem 1rem;color:var(--text-primary);">
                <input type="file" id="file-input" name="file" accept="video/*" style="display:none;">
                <button type="button" class="btn-secondary" onclick="document.getElementById('file-input').click();" style="white-space:nowrap;padding:.75rem 1.1rem;">Browse</button>
              </div>
            </div>

            <button type="submit" class="form-submit"><i class="fas fa-play"></i>&nbsp; Start Analysis</button>
          </form>
        </div>
      </div>
    <?php endif; ?>
  </div>

  <?php include 'includes/footer.php'; ?>
</div>

<!-- ── LOADER OVERLAY ─────────────────────────────────── -->
<div class="loader-overlay" id="loader">
  <div class="loader-content">
    <div class="spinner"></div>
    <div class="progress-container">
      <div class="progress-bar" id="progress-bar"></div>
    </div>
    <p id="loader-text">Analyzing video with AI — please wait...</p>
    <div class="percentage" id="percentage">0%</div>
    <button type="button" id="cancel-analysis" class="btn-secondary" style="margin-top: 2rem; border-color: var(--danger); color: var(--danger);"><i class="fas fa-times"></i> Cancel Analysis</button>
  </div>
</div>


<script src="js/script.js?v=5"></script>
</body>
</html>