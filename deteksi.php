<section id="Deteksi">
                            <div class="layar-dalam">
                              <h3 style="text-align: center">Deteksi</h3>
                              <p class="ringkasan">
                                Tekan kamera atau masukan gambar dari galeri Anda untuk mendeteksi jenis sampah
                              </p>
                            </div>
                            <div class="canvas">
                                <div class="video">
                                    <div class="webcam">
                                    <video id="webcam" autoplay playsinline>
                                    </video>
                                </div>
                                  </div>
                            </div>
                            <div class="tombol-deteksi">
                              <label for="inputImage" class="tombol-kamera"> Galeri </label>
                              <input
                                style="display: none"
                                type="file"
                                id="inputImage"
                                accept="image/*" 
                                onchange="renderImage(this)"
                              />
                              <button class="tombol-kamera" value="On" id="webcam-control"onclick="getPicture()"  target="_blank">
                                Buka Kamera
                              </button>
                                                                                                                                                    
                            </div>
                            <div id="overlay">
                              <div id="prediksi">
                                <div class="tutup">
                                    <button class="tombol-tutup-prediksi" id="close-modal-btn" onclick="closeBtn()">&#10005;</button>
                                </div>
                                <div class="image-popup">
                                <img id="elemImage" class="d-none" src="" />
                                <canvas id="canvas" class="d-none"></canvas>
                                </div>
                                <div>
                                <p class="hasil-prediksi" id="elemPrediksi"></p>
                                </div>
                                <div class="konten" id="konten">
                            </div>
                            </div>
                          </div>
                    </section>