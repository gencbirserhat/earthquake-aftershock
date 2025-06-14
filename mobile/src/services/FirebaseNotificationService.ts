import messaging from '@react-native-firebase/messaging';
import { Alert, Platform } from 'react-native';
import DeviceInfo from 'react-native-device-info';

export const requestUserPermission = async () => {
    const authStatus = await messaging().requestPermission();
    const enabled =
        authStatus === messaging.AuthorizationStatus.AUTHORIZED ||
        authStatus === messaging.AuthorizationStatus.PROVISIONAL;

    if (enabled) {
        console.log('Notification permission enabled:', authStatus);
        getFcmToken();
    }
};

const getFcmToken = async () => {
    try {
        const token = await messaging().getToken();
        console.log('FCM Token:', token);

        // 🔽 Token'ı sunucuya gönderiyoruz
        await fetch('http://192.168.1.199:5000/register-token', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                token, // cihazın FCM token'ı
                deviceId: DeviceInfo.getUniqueId(), // opsiyonel: cihaz kimliği vs.
                platform: Platform.OS,
            }),
        });

        console.log('FCM token sunucuya gönderildi.');
    } catch (error) {
        console.error('FCM token alınırken ya da gönderilirken hata:', error);
    }
};

