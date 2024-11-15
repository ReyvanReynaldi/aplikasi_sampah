<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>RETRASH</title>
    <link rel="icon" href="assets/img/logo-title.png">
    <link rel="stylesheet" href="assets/styles/style.css">
    <link href="https://fonts.googleapis.com/css2?family=Bree+Serif&family=Noto+Sans&family=Roboto:ital,wght@0,100;0,300;0,400;0,500;0,700;1,500&display=swap" rel="stylesheet">

</head> 
<body>
    <?php require 'header.php'; ?>
                <main>
                    <?php require 'beranda.php'; ?>
                    <?php require 'tentangkami.php'; ?>
                        <?php require 'deteksi.php'; ?>
                    <?php require 'artikel.php'; ?>

                    <?php require 'bankSampah.php'; ?>
                </main>
                <?php require 'footer.php'; ?>
           
                <script
                src="https://code.jquery.com/jquery-3.6.0.min.js"
                integrity="sha256-/xUj+3OJU5yExlq6GSYGSHk7tPXikynS7ogEvDej/m4="
                crossorigin="anonymous"
              ></script>
              <script src="https://cdn.jsdelivr.net/npm/@tensorflow/tfjs@2.0.0/dist/tf.min.js"></script>
              <script
                type="text/javascript"
                src="https://unpkg.com/webcam-easy/dist/webcam-easy.min.js"
              ></script>
              <script src="javascript.js"></script>
</body>
</html>