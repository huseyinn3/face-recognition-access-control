# 📷 Yüz Tanıma ile Akıllı Erişim Kontrol Sistemi

ESP32-CAM ve OpenCV kullanarak geliştirilen yüz tanıma tabanlı akıllı erişim kontrol sistemi. Flask web sunucusu üzerinden çalışan sistem, tanınan yüzlere otomatik erişim izni vermektedir.

## 🎯 Proje Hakkında

Bu proje, Bitlis Eren Üniversitesi Bilgisayar Mühendisliği bölümünde ders projesi olarak geliştirilmiştir. ESP32-CAM modülünden alınan görüntü, Flask sunucusu üzerinde OpenCV ile işlenerek yüz tanıma gerçekleştirilmektedir.

## 🛠️ Kullanılan Teknolojiler

- **Donanım:** ESP32-CAM
- **Backend:** Python, Flask
- **Görüntü İşleme:** OpenCV
- **Veri Saklama:** JSON

## 📁 Proje Yapısı

├── server.py                  # Flask sunucusu ve yüz tanıma işlemleri
├── known_faces.json           # Sisteme kayıtlı yüz verileri
├── person_stats.json          # Kişi bazlı erişim istatistikleri
├── recognition_history.json   # Tanıma geçmişi logları
└── README.md

## 📋 Özellikler

- ESP32-CAM üzerinden canlı görüntü akışı alma
- OpenCV ile yüz algılama ve tanıma
- Tanınan yüzlere otomatik erişim izni verme
- Tanınmayan yüzlerde erişim reddi ve loglama
- Kişi bazlı erişim istatistikleri tutma
- Tanıma geçmişi kaydı

## 🚀 Nasıl Çalıştırılır

### Gereksinimler
```bash
pip install flask opencv-python numpy
```

### Çalıştırma
```bash
python server.py
```

## ⚙️ Sistem Mimarisi

ESP32-CAM → Görüntü Akışı → Flask Sunucusu → OpenCV Yüz Tanıma → Erişim Kararı
↓
JSON Veri Kaydı

## 📝 Lisans

Bu proje eğitim amaçlı geliştirilmiştir.
