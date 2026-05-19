# 🌐 ТЗ: Frontend Web Developer (сайт)

## Что делаем как команда

Приложение, которое смотрит на фото со стройки и определяет: есть ли на рабочих каска и жилет. Если кого-то нет — показывает красную рамку и пишет "нарушение".

---

## Что ты делаешь простыми словами

Ты делаешь **сайт**, который открывается в браузере. На сайте можно:

1. Загрузить фото со стройки
2. Увидеть его с красными рамками вокруг нарушителей и зелёными вокруг ОК-рабочих
3. Увидеть надпись "Найдено нарушений: 3"
4. Открыть историю всех проверок
5. Посмотреть детали любой проверки

Ты не работаешь с моделью напрямую — ты делаешь HTTP-запросы к серверу бэкендера, и он возвращает тебе готовый JSON с результатами.

---

## 🛠 Инструменты

| Инструмент | Зачем |
|------------|-------|
| **Node.js** (v20+) | Среда для запуска JavaScript | https://nodejs.org |
| **Vite** | Быстрый сборщик React-приложений |
| **React + TypeScript** | Сам фреймворк |
| **shadcn/ui** | Готовые красивые компоненты | https://ui.shadcn.com |
| **Tailwind CSS** | CSS-фреймворк (идёт со shadcn) |
| **TanStack Query** | Удобная работа с API-запросами |
| **VS Code** | Редактор кода |

---

## 📋 Конкретные задачи по неделям

### Неделя 1: Поднять проект

**Цель:** запустить пустую заготовку React-приложения.

1. Установи Node.js v20+: https://nodejs.org
2. Проверь установку:
```bash
node --version  # должно быть v20+
npm --version
```

3. В корне репозитория создай проект:
```bash
npm create vite@latest frontend-web -- --template react-ts
cd frontend-web
npm install
npm run dev
```

4. Открой http://localhost:5173 — должна быть стандартная заглушка с логотипом Vite

5. Установи Tailwind CSS:
```bash
npm install -D tailwindcss@3 postcss autoprefixer
npx tailwindcss init -p
```

В `tailwind.config.js`:
```javascript
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: { extend: {} },
  plugins: [],
}
```

В `src/index.css` (замени всё содержимое):
```css
@tailwind base;
@tailwind components;
@tailwind utilities;
```

6. Установи shadcn/ui (по инструкции с https://ui.shadcn.com/docs/installation/vite):
```bash
npx shadcn@latest init
```

При вопросах выбирай дефолтные настройки.

7. Поставь несколько компонентов:
```bash
npx shadcn@latest add button card input
```

---

### Неделя 2: Главная страница на заглушках

**Цель:** сделать страницу загрузки фото — пока без сервера.

Создай `src/App.tsx`:

```tsx
import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'

interface Detection {
  class: string
  confidence: number
  bbox: [number, number, number, number]
}

function App() {
  const [imageUrl, setImageUrl] = useState<string | null>(null)
  const [detections, setDetections] = useState<Detection[]>([])
  const [violations, setViolations] = useState(0)
  const [loading, setLoading] = useState(false)
  
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return
    
    const url = URL.createObjectURL(file)
    setImageUrl(url)
    setDetections([])
  }
  
  const handleAnalyze = async () => {
    setLoading(true)
    
    // ЗАГЛУШКА: пока генерим случайные рамки
    setTimeout(() => {
      setDetections([
        { class: 'no_helmet', confidence: 0.87, bbox: [100, 80, 250, 220] },
        { class: 'helmet', confidence: 0.95, bbox: [400, 100, 520, 240] },
      ])
      setViolations(1)
      setLoading(false)
    }, 1000)
  }
  
  return (
    <div className="container mx-auto p-8 max-w-4xl">
      <h1 className="text-3xl font-bold mb-6">Детектор СИЗ</h1>
      
      <Card className="p-6 mb-6">
        <input 
          type="file" 
          accept="image/*"
          onChange={handleFileChange}
          className="mb-4"
        />
        
        {imageUrl && (
          <Button 
            onClick={handleAnalyze} 
            disabled={loading}
            className="mb-4"
          >
            {loading ? 'Анализируем...' : 'Анализировать'}
          </Button>
        )}
        
        {imageUrl && (
          <div className="relative inline-block">
            <img src={imageUrl} alt="upload" className="max-w-full" />
            
            {detections.map((d, i) => (
              <div
                key={i}
                style={{
                  position: 'absolute',
                  left: d.bbox[0],
                  top: d.bbox[1],
                  width: d.bbox[2] - d.bbox[0],
                  height: d.bbox[3] - d.bbox[1],
                  border: `3px solid ${d.class.startsWith('no_') ? 'red' : 'green'}`,
                }}
              >
                <span 
                  style={{
                    position: 'absolute',
                    top: -25,
                    left: 0,
                    background: d.class.startsWith('no_') ? 'red' : 'green',
                    color: 'white',
                    padding: '2px 6px',
                    fontSize: 12,
                  }}
                >
                  {d.class} {Math.round(d.confidence * 100)}%
                </span>
              </div>
            ))}
          </div>
        )}
        
        {detections.length > 0 && (
          <div className="mt-4 p-4 bg-gray-100 rounded">
            <p className="text-lg">
              Найдено нарушений: <strong className="text-red-600">{violations}</strong>
            </p>
            <p>Всего объектов: {detections.length}</p>
          </div>
        )}
      </Card>
    </div>
  )
}

export default App
```

Запусти `npm run dev` и проверь — должна работать загрузка фото с заглушечными рамками.

---

### Неделя 3: Подключение к настоящему API

**Цель:** заменить заглушку на реальные запросы к серверу.

Когда бэкендер скажет "сервер запущен на http://localhost:8000":

1. Установи библиотеку для запросов:
```bash
npm install @tanstack/react-query
```

2. Замени заглушку в `handleAnalyze`:

```tsx
const handleAnalyze = async () => {
  if (!imageUrl) return
  setLoading(true)
  
  try {
    // Получаем сам файл
    const blob = await fetch(imageUrl).then(r => r.blob())
    
    const formData = new FormData()
    formData.append('file', blob, 'photo.jpg')
    
    const response = await fetch('http://localhost:8000/detect', {
      method: 'POST',
      body: formData
    })
    
    if (!response.ok) {
      throw new Error('Ошибка сервера')
    }
    
    const data = await response.json()
    setDetections(data.detections)
    setViolations(data.violations)
  } catch (error) {
    console.error(error)
    alert('Что-то пошло не так')
  } finally {
    setLoading(false)
  }
}
```

3. **Тонкость с координатами:** бэк возвращает координаты в пикселях оригинальной картинки, но картинка на странице может быть отмасштабирована. Решение — рисовать рамки в пропорциях:

```tsx
// Сохраняем оригинальные размеры картинки
const [imageDimensions, setImageDimensions] = useState({ w: 0, h: 0 })

const handleImageLoad = (e: React.SyntheticEvent<HTMLImageElement>) => {
  setImageDimensions({
    w: e.currentTarget.naturalWidth,
    h: e.currentTarget.naturalHeight,
  })
}

// При рендере рамок используй проценты:
<div
  style={{
    position: 'absolute',
    left: `${(d.bbox[0] / imageDimensions.w) * 100}%`,
    top: `${(d.bbox[1] / imageDimensions.h) * 100}%`,
    width: `${((d.bbox[2] - d.bbox[0]) / imageDimensions.w) * 100}%`,
    height: `${((d.bbox[3] - d.bbox[1]) / imageDimensions.h) * 100}%`,
    border: `3px solid ${d.class.startsWith('no_') ? 'red' : 'green'}`,
  }}
>
```

И добавь `onLoad={handleImageLoad}` к тегу `<img>`.

---

### Неделя 4: Страница истории

**Цель:** сделать страницу со списком всех проверок.

Установи роутер:
```bash
npm install react-router-dom
```

Сделай 2 страницы: `/` (главная с загрузкой) и `/history` (список проверок).

`src/pages/HistoryPage.tsx`:
```tsx
import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { Card } from '@/components/ui/card'

interface HistoryItem {
  id: string
  timestamp: string
  violations_count: number
  total_objects: number
  image_url: string
}

export function HistoryPage() {
  const [history, setHistory] = useState<HistoryItem[]>([])
  const [loading, setLoading] = useState(true)
  
  useEffect(() => {
    fetch('http://localhost:8000/history')
      .then(r => r.json())
      .then(data => {
        setHistory(data)
        setLoading(false)
      })
  }, [])
  
  if (loading) return <div>Загрузка...</div>
  
  return (
    <div className="container mx-auto p-8">
      <h1 className="text-3xl font-bold mb-6">История проверок</h1>
      
      <div className="grid gap-4">
        {history.map(item => (
          <Link to={`/violations/${item.id}`} key={item.id}>
            <Card className="p-4 hover:bg-gray-50 cursor-pointer">
              <div className="flex justify-between items-center">
                <div>
                  <p className="text-sm text-gray-500">
                    {new Date(item.timestamp).toLocaleString('ru-RU')}
                  </p>
                  <p className="text-lg">
                    Объектов: {item.total_objects}, 
                    нарушений: <span className="text-red-600 font-bold">
                      {item.violations_count}
                    </span>
                  </p>
                </div>
                <img 
                  src={`http://localhost:8000${item.image_url}`}
                  className="w-20 h-20 object-cover rounded"
                  alt=""
                />
              </div>
            </Card>
          </Link>
        ))}
      </div>
    </div>
  )
}
```

В `App.tsx` добавь роутер:
```tsx
import { BrowserRouter, Routes, Route, Link } from 'react-router-dom'

function App() {
  return (
    <BrowserRouter>
      <nav className="p-4 border-b">
        <Link to="/" className="mr-4">Главная</Link>
        <Link to="/history">История</Link>
      </nav>
      <Routes>
        <Route path="/" element={<UploadPage />} />
        <Route path="/history" element={<HistoryPage />} />
        <Route path="/violations/:id" element={<DetailsPage />} />
      </Routes>
    </BrowserRouter>
  )
}
```

---

### Неделя 5: Детальная страница

**Цель:** показывать ту же картинку с рамками, что и при загрузке, но из истории.

`src/pages/DetailsPage.tsx`:
```tsx
import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'

interface Details {
  id: string
  timestamp: string
  detections: Detection[]
  violations_count: number
  total_objects: number
  image_url: string
}

export function DetailsPage() {
  const { id } = useParams<{ id: string }>()
  const [data, setData] = useState<Details | null>(null)
  
  useEffect(() => {
    fetch(`http://localhost:8000/violations/${id}`)
      .then(r => r.json())
      .then(setData)
  }, [id])
  
  if (!data) return <div>Загрузка...</div>
  
  return (
    <div className="container mx-auto p-8">
      <h1 className="text-2xl font-bold mb-4">Проверка от {new Date(data.timestamp).toLocaleString('ru-RU')}</h1>
      <p className="mb-4">
        Нарушений: <strong className="text-red-600">{data.violations_count}</strong>
      </p>
      
      {/* Тут используй тот же компонент рамок, что и на главной */}
      {/* image_url приходит относительный, добавляй http://localhost:8000 */}
    </div>
  )
}
```

---

### Неделя 6: Дашборд со статистикой

**Цель:** красивый блок с цифрами на главной.

```tsx
const [stats, setStats] = useState({ total_checks: 0, total_violations: 0 })

useEffect(() => {
  fetch('http://localhost:8000/stats')
    .then(r => r.json())
    .then(setStats)
}, [])

// В JSX:
<div className="grid grid-cols-3 gap-4 mb-6">
  <Card className="p-4">
    <p className="text-sm text-gray-500">Всего проверок</p>
    <p className="text-3xl font-bold">{stats.total_checks}</p>
  </Card>
  <Card className="p-4">
    <p className="text-sm text-gray-500">Всего нарушений</p>
    <p className="text-3xl font-bold text-red-600">{stats.total_violations}</p>
  </Card>
  <Card className="p-4">
    <p className="text-sm text-gray-500">Среднее на проверку</p>
    <p className="text-3xl font-bold">{stats.average_violations_per_check}</p>
  </Card>
</div>
```

---

### Неделя 7: Полировка

- [ ] Спиннер загрузки (вместо "Анализируем..." сделай красивую крутилку)
- [ ] Обработка ошибок ("сервер недоступен" — большое красное сообщение)
- [ ] Drag & drop для загрузки (не только через кнопку)
- [ ] Адаптив для мобильного (Tailwind: `md:` префиксы)
- [ ] Базовая иконка favicon
- [ ] Title страницы

Drag & drop:
```tsx
const handleDrop = (e: React.DragEvent) => {
  e.preventDefault()
  const file = e.dataTransfer.files[0]
  if (file && file.type.startsWith('image/')) {
    const url = URL.createObjectURL(file)
    setImageUrl(url)
  }
}

<div
  onDrop={handleDrop}
  onDragOver={(e) => e.preventDefault()}
  className="border-4 border-dashed border-gray-300 p-12 text-center"
>
  Перетащите фото сюда или
  <input type="file" ... />
</div>
```

---

## 📊 Что должно быть готово в конце

- [ ] Сайт работает локально по `npm run dev`
- [ ] Можно загрузить фото и увидеть рамки
- [ ] Работает страница истории
- [ ] Работает детальная страница
- [ ] Файл `package.json` корректный
- [ ] README в `frontend-web/`:
  ```markdown
  # Frontend Web
  
  ## Установка
  npm install
  
  ## Запуск
  npm run dev
  
  Сайт на http://localhost:5173
  
  ВАЖНО: бэкенд должен быть запущен на http://localhost:8000
  ```

---

## 🎓 Советы по вайбкодингу

- **v0.dev** (https://v0.dev) — пишешь "загрузка фото с превью и кнопкой анализа" — он генерит готовый компонент с shadcn/ui. Копируй и вставляй.
- Когда что-то не работает — скриншот ошибки в консоли браузера (F12 → Console) и кидай в Claude
- Не парься с TypeScript-ошибками жёстко, ставь `any` где он бесит — это учебный проект
- Если CORS-ошибка — это к бэкендеру, не твоя проблема. Скажи ему добавить `allow_origins=["*"]`
- **Не пиши свою библиотеку компонентов** — используй shadcn/ui, там всё готовое

---

## 🤝 С кем ты работаешь

- **Backend** — он даёт тебе адрес сервера. На 2-й неделе обсудите формат API
- **Frontend Mobile** — он делает то же на мобильном. Можете переиспользовать общую логику запросов (но не обязательно)
- **QA/DevOps** — будет тестировать твой сайт глазами, найдёт баги
- **PM** — следит за прогрессом

---

## 🎯 Ключевые понятия

- **React** — библиотека для построения интерфейсов из переиспользуемых компонентов
- **TypeScript** — JavaScript с типами. Помогает ловить ошибки на этапе написания
- **Vite** — собирает все твои файлы в один и запускает локальный сервер для разработки
- **State** — это переменные компонента, при изменении которых обновляется интерфейс (`useState`)
- **Props** — параметры, которые компонент принимает
- **Component** — переиспользуемый кусок UI (кнопка, карточка, форма)
- **Tailwind** — CSS-фреймворк, где стили задаются классами в HTML: `className="p-4 bg-red-500"`

Удачи! 🎨
