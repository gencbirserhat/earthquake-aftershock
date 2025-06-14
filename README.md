
# 🌍 Deprem ve Artçı Şok Tahmin Sistemi

Bu proje, **gerçek zamanlı deprem verilerini** işleyerek, belirli bir büyüklüğün üzerindeki depremler için potansiyel **artçı şokların büyüklüğünü ve zamanını tahmin eden** bütünleşik bir sistemdir.

🔧 Sistem; Flask tabanlı bir arka uç servis, makine öğrenmesi modelleri ve React Native mobil uygulamasından oluşur.

---

## 🚀 Özellikler

- **📡 Gerçek Zamanlı Veri Akışı**  
  Kandilli Rasathanesi verilerini takip eder ve yeni depremleri saniyeler içinde işler.

- **🤖 Yapay Zeka Destekli Tahmin**  
  5.5 ve üzeri büyüklükteki depremler için LightGBM ile artçı şok tahmini yapar.

- **🔌 WebSocket İletişimi**  
  Flask-SocketIO ile istemcilere anlık veri iletimi sağlar.

- **📡 RESTful API + Swagger**  
  Model tahminleri ve sistem durumu için belgelenmiş API'ler sunar.

- **📱 Platform Bağımsız Mobil Uygulama**  
  iOS ve Android destekli, React Native ile geliştirilmiş mobil arayüz.

- **🔔 Anlık Bildirimler (FCM)**  
  Kritik bilgiler Firebase Cloud Messaging ile kullanıcılara iletilir.

---

## 🏗️ Mimaride Kullanılan Teknolojiler

### 🔙 Backend (Flask)

- Flask
- Flask-SocketIO
- Firebase Admin SDK
- Requests
- Flasgger

### 📊 Veri Bilimi & ML

- Pandas
- NumPy
- Scikit-learn
- LightGBM
- Joblib
- Matplotlib

### 📱 Frontend (Mobil)

- React Native
- Socket.IO Client
- AsyncStorage
- React Native Firebase

---

## 🏛️ Sistem Mimarisi

```mermaid
graph TD
  A[Kandilli API] --> B[Data Fetcher (Thread)]
  B --> C[Flask App (app.py)]
  C --> D[WebSocket Server]
  C --> E[Prediction Logic (main.py)]
  E --> F[ML Models (.pkl)]
  E --> G[Firebase Admin SDK]
  D --> H[React Native Mobil Uygulama]
  G --> I[Firebase Cloud Messaging]
  I --> J[FCM Listener]
  H --> K[WebSocket Client]
  H --> L[API Client]
  H --> M[Local Storage (AsyncStorage)]
```

---

## ⚙️ Kurulum

### 📋 Gereksinimler

- Python 3.8+
- Node.js 16+ & npm
- React Native geliştirme ortamı
- Firebase projesi & `serviceAccountKey.json`

---

## 1️⃣ Arka Uç (Backend) Kurulumu

```bash
git clone https://github.com/gencbirserhat/earthquake-aftershock.git
cd earthquake-aftershock/backend
pip install -r requirements.txt
```

### 🔐 Firebase Ayarları

- Firebase servis hesabını indir.
- Adını: `earthquake-aftershock-firebase-adminsdk.json` olarak değiştir.
- `app.py` ile aynı dizine koy.

### 📦 Model Dosyaları

- `models/` klasöründe şu dosyalar olmalı:
  - `lgbm_mag_pipeline.pkl`
  - `lgbm_time_pipeline.pkl`

> Model yoksa `veri-analizi/lgbm_first_aftershock-predict.ipynb` dosyasını çalıştırarak oluştur.

### 🚀 Sunucuyu Başlat

```bash
python app.py
# Sunucu http://0.0.0.0:5000 üzerinde çalışacaktır.
```

---

## 2️⃣ Mobil Uygulama Kurulumu

```bash
cd ../mobil-uygulama
npm install
```

### 🔐 Firebase

- Android: `google-services.json`
- iOS: `GoogleService-Info.plist`

> [React Native Firebase Kurulumu](https://rnfirebase.io/) kılavuzuna bak.

### 🌐 IP Güncellemesi

`App.tsx` ve servis dosyalarında:

```ts
const FLASK_API_URL = "http://<local-ip>:5000";
```

### ▶️ Uygulamayı Çalıştır

#### Android:

```bash
npx react-native run-android
```

#### iOS:

```bash
cd ios && pod install && cd ..
npx react-native run-ios
```

---

## 📂 Proje Yapısı

```
.
├── backend/
│   ├── app.py
│   ├── main.py
│   ├── requirements.txt
│   ├── models/
│   │   ├── lgbm_mag_pipeline.pkl
│   │   └── lgbm_time_pipeline.pkl
│   └── earthquake-aftershock-firebase-adminsdk.json
│
├── mobil-uygulama/
│   ├── src/
│   │   ├── components/
│   │   └── services/
│   ├── App.tsx
│   └── ...
│
├── veri-analizi/
│   ├── lgbm_first_aftershock-predict.ipynb
│   └── main copy.ipynb
│
└── README.md
```

---

## 🎯 Gelecek Geliştirmeler

- 🌐 Harita üzerinde canlı deprem gösterimi
- 📊 Tahmin sonuçlarının geçmişe dönük analizi
- 🔒 Kullanıcı kimlik doğrulama ve kayıt sistemi
- 🌍 Global deprem kaynaklarının desteklenmesi

---

## 🤝 Katkı Sağla

Projeye katkıda bulunmak istersen:

1. Fork'la 🍴  
2. Branch oluştur (`feature/yenilik`) 🌿  
3. Değişikliklerini yap ✏️  
4. Pull request gönder 🚀  

---

## 📜 Lisans

Bu proje MIT lisansı ile lisanslanmıştır.

---

> Hazırlayan: **Serhat Genç**  
> GitHub: [gencbirserhat](https://github.com/gencbirserhat)
