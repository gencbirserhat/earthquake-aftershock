Deprem ve Artçı Şok Tahmin Sistemi
Bu proje, gerçek zamanlı deprem verilerini işleyerek, belirli bir büyüklüğün üzerindeki ana şoklar için potansiyel artçı şokların büyüklüğünü ve zamanını tahmin eden bütünleşik bir sistemdir. Sistem, bir Flask arka uç servisinden, makine öğrenmesi modellerinden ve bir React Native mobil uygulamasından oluşur.

🚀 Projenin Özellikleri
Gerçek Zamanlı Veri Akışı: Kandilli Rasathanesi verilerini anlık olarak takip eder ve yeni depremleri saniyeler içinde işler.
Yapay Zeka Destekli Tahmin: LightGBM kullanılarak eğitilmiş makine öğrenmesi modelleri ile 5.5 ve üzeri büyüklükteki depremlerin potansiyel artçı şoklarını tahmin eder.
WebSocket İletişimi: Flask-SocketIO ile sunucu ve istemci arasında düşük gecikmeli, anlık veri akışı sağlar.
RESTful API: Model tahminlerini ve durumunu sunan, Flasgger ile belgelendirilmiş bir Flask API'si.
Platform Bağımsız Mobil Uygulama: React Native ile geliştirilmiş, hem iOS hem de Android'de çalışan, kullanıcı dostu bir mobil arayüz.
Anlık Bildirimler: Firebase Cloud Messaging (FCM) entegrasyonu ile kritik deprem ve tahmin bilgilerini mobil kullanıcılara anlık olarak iletir.
🛠️ Teknolojiler ve Mimarisi
Proje üç ana bileşenden oluşur:
Arka Uç (Backend) - app.py
Flask: Ana web framework.
Flask-SocketIO: Gerçek zamanlı WebSocket iletişimi için.
Firebase Admin SDK: Anlık mobil bildirimler göndermek için.
Requests: Üçüncü parti deprem API'lerinden veri çekmek için.
Flasgger: API dokümantasyonu oluşturmak için.
Veri Bilimi ve Makine Öğrenmesi - main.py, lgbm_first_aftershock-predict.ipynb
Pandas & NumPy: Veri işleme ve analizi.
Scikit-learn: Model eğitimi ve değerlendirmesi için.
LightGBM: Artçı şok büyüklüğü ve zamanını tahmin eden ana model.
Joblib: Eğitilmiş modelleri kaydetmek ve yüklemek için.
Matplotlib: Keşifçi veri analizi ve görselleştirme için.
Ön Uç (Frontend) - Mobil Uygulama
React Native: Platform bağımsız mobil uygulama geliştirme.
Socket.IO Client: Arka uç ile gerçek zamanlı bağlantı.
React Native Firebase: FCM bildirimlerini almak ve yönetmek için.
AsyncStorage: Verileri cihazda yerel olarak saklamak için.
🏛️ Sistem Mimarisi

Bir arka plan görevi (thread), periyodik olarak (örn. 15 saniyede bir) Kandilli API'sinden en son deprem verilerini çeker.
Yeni ve büyük (>5.5) bir deprem tespit edildiğinde, bu bilgi eğitilmiş LightGBM modeline gönderilir.
Model, artçı şok büyüklüğü ve zamanı için bir tahmin üretir.
Yeni deprem ve (varsa) tahmin sonucu, WebSocket üzerinden tüm bağlı mobil istemcilere anlık olarak gönderilir.
Aynı zamanda, Firebase Cloud Messaging (FCM) aracılığıyla kayıtlı tüm mobil cihazlara bir uyarı bildirimi gönderilir.
Mobil uygulama, bu verileri alır ve kullanıcı arayüzünü günceller.
🏁 Projeyi Yerel Makinede Çalıştırma
Projeyi kendi makinenizde çalıştırmak için aşağıdaki adımları izleyin.
📋 Ön Gereksinimler
Python 3.8+
Node.js 16+ ve npm
React Native geliştirme ortamı kurulumu (Resmi Kılavuz)
Bir Firebase projesi ve serviceAccountKey.json dosyası.
⚙️ 1. Arka Ucu Kurma ve Çalıştırma
Depoyu klonlayın:
git clone https://github.com/gencbirserhat/earthquake-aftershock.git
cd deprem-tahmin-projesi/backend # veya kök dizin
Use code with caution.
Bash
Gerekli Python paketlerini yükleyin:
pip install -r requirements.txt
Use code with caution.
Bash
Firebase Kurulumu:
Firebase projenizden oluşturduğunuz servis anahtarı dosyasını indirin.
Dosyanın adını earthquake-aftershock-firebase-adminsdk-fbsvc-703a825086.json olarak değiştirin ve app.py ile aynı dizine koyun.
Model Dosyaları:
models/ klasörünün içinde lgbm_mag_pipeline.pkl ve lgbm_time_pipeline.pkl dosyalarının bulunduğundan emin olun. Bu modelleri lgbm_first_aftershock-predict.ipynb not defterini çalıştırarak üretebilirsiniz.
Sunucuyu başlatın:
python app.py
Use code with caution.
Bash
Sunucu varsayılan olarak http://0.0.0.0:5000 adresinde çalışmaya başlayacaktır.
📱 2. Mobil Uygulamayı Kurma ve Çalıştırma
Mobil uygulama dizinine gidin:
cd ../mobil-uygulama # veya ilgili dizin
Use code with caution.
Bash
Gerekli npm paketlerini yükleyin:
npm install
Use code with caution.
Bash
Firebase Kurulumu:
React Native Firebase dokümantasyonunu takip ederek google-services.json (Android) ve GoogleService-Info.plist (iOS) dosyalarını projenize ekleyin.
IP Adresini Güncelleyin:
App.tsx ve diğer servis dosyalarındaki FLASK_API_URL değişkenini, arka uç sunucunuzun yerel ağdaki IP adresi ile güncelleyin. Örneğin: http://192.168.1.10:5000.
Uygulamayı başlatın (Android):
npx react-native run-android
Use code with caution.
Bash
Uygulamayı başlatın (iOS):
cd ios && pod install && cd ..
npx react-native run-ios
Use code with caution.
Bash
📂 Proje Dosya Yapısı
.
├── backend/                  # Arka uç ve model dosyaları
│   ├── app.py                # Flask sunucusu
│   ├── main.py               # Model tahmin fonksiyonları
│   ├── requirements.txt      # Python bağımlılıkları
│   ├── models/               # Eğitilmiş .pkl modelleri
│   │   ├── lgbm_mag_pipeline.pkl
│   │   └── lgbm_time_pipeline.pkl
│   └── earthquake-aftershock-firebase-adminsdk.json # Firebase anahtarı
│
├── mobil-uygulama/           # React Native mobil uygulaması
│   ├── src/
│   │   ├── components/       # React bileşenleri (Liste, Modal vb.)
│   │   └── services/         # Servisler (WebSocket, Firebase)
│   ├── App.tsx               # Ana uygulama bileşeni
│   └── ...
│
├── veri-analizi/             # Veri bilimi not defterleri
│   ├── lgbm_first_aftershock-predict.ipynb  # Model eğitim not defteri
│   └── main copy.ipynb       # Keşifçi veri analizi ve görselleştirme
│
└── README.md                 # Bu dosya
Use code with caution.
🎯 Gelecek Geliştirmeler ve Katkı
Bu proje sürekli geliştirilmeye açıktır. Gelecek için planlanan bazı adımlar:
Daha Gelişmiş Modeller: LSTM veya Transformer gibi derin öğrenme modellerini denemek.
Özellik Mühendisliği: Fay hatlarına uzaklık, zemin türü gibi daha fazla jeolojik özelliği modele dahil etmek.
İnteraktif Harita: Mobil uygulamaya depremleri ve tahminleri gösteren interaktif bir harita eklemek.
Bulut Dağıtımı: Projeyi Docker ve Kubernetes kullanarak bir bulut platformuna (AWS, GCP) taşımak.
Katkıda bulunmak isterseniz, lütfen bir "issue" açın veya bir "pull request" gönderin. Tüm katkılar memnuniyetle karşılanır!