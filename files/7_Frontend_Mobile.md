# 📱 ТЗ: Frontend Mobile Developer (мобильное приложение)

## Что делаем как команда

Приложение, которое смотрит на фото со стройки и определяет: есть ли на рабочих каска и жилет. Если кого-то нет — показывает красную рамку и пишет "нарушение".

---

## Что ты делаешь простыми словами

Ты делаешь **мобильное приложение** для телефона. На нём можно:

1. Открыть камеру и сфотографировать рабочих
2. Отправить фото на сервер
3. Увидеть результат (рамки, количество нарушений)
4. Посмотреть историю проверок

**Важно:** ты не пишешь нативное приложение (как обычные iOS-приложения на Swift). Ты пишешь **на JavaScript через Expo**, и оно **работает на телефонах через приложение Expo Go** или собирается в обычное приложение позже.

Это значит: тебе **не нужен Mac для разработки под iOS**, не нужно ставить Xcode/Android Studio. Всё работает с обычного компьютера.

---

## 🛠 Инструменты

| Инструмент | Зачем |
|------------|-------|
| **Node.js** (v20+) | Среда для JavaScript | https://nodejs.org |
| **Expo** | Платформа для мобильной разработки на React |
| **Expo Go** | Приложение на телефоне для запуска твоего приложения |
| **React Native** | Сам фреймворк (под капотом Expo) |
| **TypeScript** | JavaScript с типами |
| **VS Code** | Редактор кода |

**Что нужно скачать на телефон:**
- iPhone: **Expo Go** в App Store
- Android: **Expo Go** в Google Play

---

## 📋 Конкретные задачи по неделям

### Неделя 1: Подними проект и запусти на телефоне

**Цель:** убедиться что цикл "пишу код → вижу на телефоне" работает.

1. Установи Node.js v20+: https://nodejs.org
2. Создай проект:
```bash
npx create-expo-app@latest mobile --template blank-typescript
cd mobile
```

3. Запусти:
```bash
npx expo start
```

В терминале появится QR-код.

4. На телефоне:
   - Установи приложение **Expo Go**
   - Подключись к **той же Wi-Fi сети**, что и компьютер
   - Открой Expo Go, нажми "Scan QR code", отсканируй QR-код из терминала
   - На телефоне должно открыться твоё приложение с надписью "Open up App.tsx to start working"

5. Проверь горячую перезагрузку: открой `App.tsx`, поменяй текст, сохрани → на телефоне сразу обновится

**Если не работает:**
- Проверь что компьютер и телефон в одной Wi-Fi сети
- Попробуй запустить с тоннелем: `npx expo start --tunnel`
- Если совсем плохо — используй **iOS Simulator** (только Mac) или **Android Emulator**

---

### Неделя 2: Главный экран с заглушкой

**Цель:** сделать экран с кнопкой "Сделать фото" — пока без камеры.

Замени содержимое `App.tsx`:

```tsx
import { StatusBar } from 'expo-status-bar'
import { StyleSheet, Text, View, TouchableOpacity, Image } from 'react-native'
import { useState } from 'react'

export default function App() {
  const [photoUri, setPhotoUri] = useState<string | null>(null)
  const [violations, setViolations] = useState(0)
  
  const handleTakePhoto = () => {
    // Заглушка — потом подключим камеру
    setPhotoUri('https://placehold.co/600x400/png?text=Фото+со+стройки')
    setViolations(2)
  }
  
  return (
    <View style={styles.container}>
      <Text style={styles.title}>Детектор СИЗ</Text>
      
      {photoUri && (
        <Image source={{ uri: photoUri }} style={styles.image} />
      )}
      
      {violations > 0 && (
        <View style={styles.resultBox}>
          <Text style={styles.resultText}>
            Нарушений: {violations}
          </Text>
        </View>
      )}
      
      <TouchableOpacity style={styles.button} onPress={handleTakePhoto}>
        <Text style={styles.buttonText}>📸 Сделать фото</Text>
      </TouchableOpacity>
      
      <StatusBar style="auto" />
    </View>
  )
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 20,
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    marginBottom: 30,
  },
  image: {
    width: 300,
    height: 200,
    marginBottom: 20,
    borderRadius: 8,
  },
  resultBox: {
    backgroundColor: '#fee',
    padding: 16,
    borderRadius: 8,
    marginBottom: 20,
  },
  resultText: {
    fontSize: 20,
    color: '#c00',
    fontWeight: 'bold',
  },
  button: {
    backgroundColor: '#0066cc',
    paddingHorizontal: 30,
    paddingVertical: 16,
    borderRadius: 8,
  },
  buttonText: {
    color: 'white',
    fontSize: 18,
    fontWeight: 'bold',
  },
})
```

Сохрани, проверь на телефоне — должна появиться кнопка, при нажатии — заглушка с фото.

---

### Неделя 3: Подключаем настоящую камеру

**Цель:** сделать так, чтобы кнопка реально открывала камеру.

Используем **expo-camera** или проще — **expo-image-picker** (он умеет и снять фото, и выбрать из галереи).

```bash
npx expo install expo-image-picker
```

Поправь `handleTakePhoto`:

```tsx
import * as ImagePicker from 'expo-image-picker'

const handleTakePhoto = async () => {
  // Запрашиваем разрешение на камеру
  const { status } = await ImagePicker.requestCameraPermissionsAsync()
  if (status !== 'granted') {
    alert('Нужно разрешение на камеру')
    return
  }
  
  // Открываем камеру
  const result = await ImagePicker.launchCameraAsync({
    mediaTypes: ImagePicker.MediaTypeOptions.Images,
    quality: 0.7,  // сжимаем чтобы быстрее отправлять
  })
  
  if (!result.canceled && result.assets[0]) {
    setPhotoUri(result.assets[0].uri)
  }
}
```

Также добавь кнопку **выбора из галереи** (удобно для тестов когда нет настоящей стройки рядом):

```tsx
const handlePickPhoto = async () => {
  const result = await ImagePicker.launchImageLibraryAsync({
    mediaTypes: ImagePicker.MediaTypeOptions.Images,
    quality: 0.7,
  })
  
  if (!result.canceled && result.assets[0]) {
    setPhotoUri(result.assets[0].uri)
  }
}
```

И в JSX добавь вторую кнопку:
```tsx
<TouchableOpacity style={styles.button} onPress={handlePickPhoto}>
  <Text style={styles.buttonText}>🖼 Выбрать из галереи</Text>
</TouchableOpacity>
```

---

### Неделя 4: Отправка на сервер

**Цель:** научить приложение отправлять фото на сервер бэкендера и получать результат.

Когда бэкендер скажет "сервер запущен на http://192.168.X.X:8000":

⚠️ **ВАЖНО:** на телефоне нельзя писать `localhost` — это адрес самого телефона. Нужен **IP-адрес компьютера** в локальной сети. Бэкендер скажет тебе свой IP (на Windows: `ipconfig`, на Mac/Linux: `ifconfig`).

Создай файл `api.ts`:

```tsx
const API_URL = 'http://192.168.X.X:8000'  // подставь IP бэкендера

export async function detectImage(imageUri: string) {
  const formData = new FormData()
  
  // На React Native файл передаётся вот так:
  formData.append('file', {
    uri: imageUri,
    type: 'image/jpeg',
    name: 'photo.jpg',
  } as any)
  
  const response = await fetch(`${API_URL}/detect`, {
    method: 'POST',
    body: formData,
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })
  
  if (!response.ok) {
    throw new Error('Ошибка сервера')
  }
  
  return response.json()
}

export async function getHistory() {
  const response = await fetch(`${API_URL}/history`)
  return response.json()
}
```

Используй в `App.tsx`:

```tsx
import { detectImage } from './api'

const [loading, setLoading] = useState(false)
const [detections, setDetections] = useState<any[]>([])

const handleAnalyze = async () => {
  if (!photoUri) return
  setLoading(true)
  
  try {
    const result = await detectImage(photoUri)
    setDetections(result.detections)
    setViolations(result.violations)
  } catch (error) {
    alert('Не удалось проанализировать. Проверьте подключение.')
    console.error(error)
  } finally {
    setLoading(false)
  }
}

// Добавь кнопку Анализировать после фото
{photoUri && (
  <TouchableOpacity 
    style={styles.button} 
    onPress={handleAnalyze}
    disabled={loading}
  >
    <Text style={styles.buttonText}>
      {loading ? 'Анализирую...' : '🔍 Анализировать'}
    </Text>
  </TouchableOpacity>
)}
```

---

### Неделя 5: Рисование рамок поверх фото

**Цель:** показать на телефоне рамки с детекциями.

В React Native нет HTML, поэтому используем `View` с абсолютным позиционированием:

```tsx
import { Image, View, Text, Dimensions } from 'react-native'

interface Detection {
  class: string
  confidence: number
  bbox: [number, number, number, number]
}

function DetectionView({ photoUri, detections }: { photoUri: string, detections: Detection[] }) {
  const [imageSize, setImageSize] = useState({ width: 1, height: 1 })
  const [displaySize, setDisplaySize] = useState({ width: 300, height: 200 })
  
  // Получаем оригинальные размеры картинки
  useEffect(() => {
    Image.getSize(photoUri, (w, h) => {
      setImageSize({ width: w, height: h })
      // Подгоняем размер на экране (макс 300px по ширине)
      const screenWidth = Dimensions.get('window').width - 40
      const ratio = h / w
      setDisplaySize({ 
        width: screenWidth, 
        height: screenWidth * ratio 
      })
    })
  }, [photoUri])
  
  const scaleX = displaySize.width / imageSize.width
  const scaleY = displaySize.height / imageSize.height
  
  return (
    <View style={{ width: displaySize.width, height: displaySize.height, position: 'relative' }}>
      <Image 
        source={{ uri: photoUri }} 
        style={{ width: displaySize.width, height: displaySize.height }}
      />
      
      {detections.map((d, i) => {
        const isViolation = d.class.startsWith('no_')
        return (
          <View
            key={i}
            style={{
              position: 'absolute',
              left: d.bbox[0] * scaleX,
              top: d.bbox[1] * scaleY,
              width: (d.bbox[2] - d.bbox[0]) * scaleX,
              height: (d.bbox[3] - d.bbox[1]) * scaleY,
              borderWidth: 3,
              borderColor: isViolation ? 'red' : 'green',
            }}
          >
            <View style={{ 
              position: 'absolute', 
              top: -22, 
              left: 0, 
              backgroundColor: isViolation ? 'red' : 'green', 
              paddingHorizontal: 6, 
              paddingVertical: 2 
            }}>
              <Text style={{ color: 'white', fontSize: 10 }}>
                {d.class}
              </Text>
            </View>
          </View>
        )
      })}
    </View>
  )
}
```

И используй компонент в основном экране вместо обычного `<Image>`.

---

### Неделя 6: Экран истории

**Цель:** список прошлых проверок.

Установи навигацию:
```bash
npx expo install @react-navigation/native @react-navigation/native-stack react-native-screens react-native-safe-area-context
```

В `App.tsx`:

```tsx
import { NavigationContainer } from '@react-navigation/native'
import { createNativeStackNavigator } from '@react-navigation/native-stack'
import { HomeScreen } from './screens/HomeScreen'
import { HistoryScreen } from './screens/HistoryScreen'

const Stack = createNativeStackNavigator()

export default function App() {
  return (
    <NavigationContainer>
      <Stack.Navigator>
        <Stack.Screen name="Home" component={HomeScreen} options={{ title: 'Детектор СИЗ' }} />
        <Stack.Screen name="History" component={HistoryScreen} options={{ title: 'История' }} />
      </Stack.Navigator>
    </NavigationContainer>
  )
}
```

`screens/HistoryScreen.tsx`:

```tsx
import { useEffect, useState } from 'react'
import { View, Text, FlatList, Image, TouchableOpacity, StyleSheet } from 'react-native'

const API_URL = 'http://192.168.X.X:8000'

interface HistoryItem {
  id: string
  timestamp: string
  violations_count: number
  total_objects: number
  image_url: string
}

export function HistoryScreen() {
  const [history, setHistory] = useState<HistoryItem[]>([])
  const [loading, setLoading] = useState(true)
  
  useEffect(() => {
    fetch(`${API_URL}/history`)
      .then(r => r.json())
      .then(data => {
        setHistory(data)
        setLoading(false)
      })
  }, [])
  
  if (loading) return <Text>Загрузка...</Text>
  
  return (
    <FlatList
      data={history}
      keyExtractor={item => item.id}
      renderItem={({ item }) => (
        <View style={styles.item}>
          <Image 
            source={{ uri: `${API_URL}${item.image_url}` }}
            style={styles.thumbnail}
          />
          <View style={{ flex: 1, marginLeft: 12 }}>
            <Text style={styles.date}>
              {new Date(item.timestamp).toLocaleString('ru-RU')}
            </Text>
            <Text style={styles.violations}>
              Нарушений: {item.violations_count}
            </Text>
          </View>
        </View>
      )}
    />
  )
}

const styles = StyleSheet.create({
  item: {
    flexDirection: 'row',
    padding: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#eee',
  },
  thumbnail: { width: 60, height: 60, borderRadius: 4 },
  date: { fontSize: 12, color: '#666' },
  violations: { fontSize: 16, color: '#c00', fontWeight: 'bold' },
})
```

Добавь кнопку "История" на главном экране:
```tsx
<TouchableOpacity onPress={() => navigation.navigate('History')}>
  <Text>📋 История</Text>
</TouchableOpacity>
```

---

### Неделя 7: Полировка

- [ ] Спиннер при загрузке (компонент `ActivityIndicator`)
- [ ] Обработка ошибок сети ("Сервер недоступен. Проверьте подключение")
- [ ] Иконка приложения (картинка 1024×1024 в `assets/icon.png`)
- [ ] Splash-экран при загрузке
- [ ] Адаптация под маленькие экраны

```tsx
import { ActivityIndicator } from 'react-native'

{loading && <ActivityIndicator size="large" color="#0066cc" />}
```

---

## 📊 Что должно быть готово в конце

- [ ] Приложение запускается через Expo Go на телефоне
- [ ] Можно сделать фото или выбрать из галереи
- [ ] Можно отправить на сервер и получить результат
- [ ] Видны рамки на фото с детекциями
- [ ] Работает экран истории
- [ ] Файл `package.json` корректный
- [ ] README в `mobile/`:
  ```markdown
  # Mobile App
  
  ## Установка
  npm install
  
  ## Запуск
  npx expo start
  
  Затем отсканируй QR-код через приложение Expo Go на телефоне.
  
  ВАЖНО: 
  - Бэкенд должен быть запущен
  - В файле api.ts укажи IP компьютера в локальной сети (не localhost!)
  - Телефон и компьютер должны быть в одной Wi-Fi
  ```

---

## 🎓 Советы по вайбкодингу

- **Главная сложность Expo** — на телефоне `localhost` не работает! Используй IP компьютера в локалке (типа `192.168.1.5:8000`)
- Когда что-то ломается на телефоне — встряси телефон → откроется меню разработчика → "Reload"
- Логи `console.log` видны в терминале где запущен `expo start`
- React Native не = HTML. Нет тегов `<div>`, `<p>` — только `<View>` и `<Text>`
- Для стилей нет CSS — есть `StyleSheet.create({...})` с похожими свойствами
- **Документация по компонентам:** https://reactnative.dev/docs/components-and-apis

---

## 🤝 С кем ты работаешь

- **Backend** — он даёт тебе IP-адрес сервера. Спрашивай его про формат ответа
- **Frontend Web** — он делает то же самое для сайта. Можете шарить логику API-запросов (но не обязательно)
- **QA/DevOps** — будет тестировать на разных телефонах
- **PM** — следит за прогрессом

---

## 🎯 Ключевые понятия

- **React Native** — это React, но компоненты рендерятся в нативные элементы iOS/Android, а не в HTML
- **Expo** — обёртка над React Native, которая берёт на себя сложности сборки и нативного кода
- **Expo Go** — приложение, которое позволяет запускать твой код без сборки в `.apk`/`.ipa`
- **Permissions** — на мобильных надо явно запрашивать разрешения на камеру, галерею и т.д.
- **FormData** — формат отправки файлов через сеть (с MIME-типом)
- **Native** vs **Cross-platform** — нативное приложение пишется отдельно для iOS и Android, кроссплатформа (как у тебя) — один код для обеих платформ

Удачи! 📱
