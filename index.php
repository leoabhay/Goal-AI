<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="description" content="GOAL AI – AI-powered football analytics platform in Nepal.">
  <title>GOAL AI | Smarter Football Analytics</title>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">
  <link rel="stylesheet" href="css/styles.css?v=5">
</head>
<body>

<!-- ── NAVBAR ──────────────────────────────────────────── -->
<div class="navbar-wrap">
  <a href="index.php" class="nav-logo">
    <i class="fas fa-futbol" style="font-size: 1.5rem; color: var(--accent); margin-right: 0.5rem;"></i>
    GOAL AI
  </a>
  <nav id="main-nav">
    <a href="#home">Home</a>
    <a href="#about">About</a>
    <a href="#services">Services</a>
    <a href="analysis.php" class="btn-primary nav-btn">Start Analysis</a>
  </nav>
  <i class="fas fa-bars hamburger" id="hamburger"></i>
</div>

<!-- ── HERO ─────────────────────────────────────────────── -->
<section class="hero" id="home">
  <div class="hero-content">
    <span class="badge"><i class="fas fa-bolt"></i> AI-Powered Analytics</span>
    <h1>Elevate Your <span class="highlight">Football</span> Game Today</h1>
    <p>Experience smarter football analytics powered by AI. Track players, analyze ball possession, calculate speeds seamlessly.</p>
    <div class="hero-buttons">
      <a href="analysis.php" class="btn-primary">Get Started &nbsp;<i class="fas fa-arrow-right"></i></a>
      <a href="#about" class="btn-secondary">Learn More</a>
    </div>
  </div>
  <div class="hero-image">
    <img src="assets/images/football.jpg" alt="Football analytics illustration">
  </div>
</section>

<!-- ── ABOUT ─────────────────────────────────────────────── -->
<section class="section" id="about">
  <div class="about-grid">
    <div class="about-img">
      <img src="assets/images/football1.jpg" alt="About GOAL AI">
    </div>
    <div class="about-text">
      <h2>What is <span>GOAL AI?</span></h2>
      <p>GOAL AI is your ultimate football analytics assistant. Using advanced AI and computer vision, it tracks players, goalkeepers, referees, and the ball in real time — identifying possession, camera movement, and speed metrics for both teams.</p>
      <p>Experience football like never before — analyze and improve your gameplay!</p>
      <div class="stat-row">
        <div class="stat"><div class="num">AI</div><div class="label">Powered</div></div>
        <div class="stat"><div class="num">Real-time</div><div class="label">Tracking</div></div>
        <div class="stat"><div class="num">In-depth</div><div class="label">Analytics</div></div>
      </div>
    </div>
  </div>
</section>

<!-- ── SERVICES ───────────────────────────────────────────── -->
<section class="section" id="services">
  <div class="section-title">
    <h2>What We <span>Provide</span></h2>
    <p>From cutting-edge AI analytics to seamless user experience — we cover everything.</p>
  </div>
  <div class="services-grid">
    <div class="service-card">
      <div class="icon"><i class="fas fa-chart-line"></i></div>
      <h3>Football Analytics</h3>
      <p>Upload match footage and let our AI analyze player tracking, ball possession, speed, and team performance metrics.</p>
    </div>
    <div class="service-card">
      <div class="icon"><i class="fas fa-headset"></i></div>
      <h3>Customer Support</h3>
      <p>Have questions? Our dedicated team is always ready to help you get the most out of GOAL AI's features.</p>
    </div>
  </div>
</section>

<!-- ── FOOTER ─────────────────────────────────────────────── -->
<?php include 'includes/footer.php'; ?>

<script src="js/script.js?v=5"></script>
</body>
</html>