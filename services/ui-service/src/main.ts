import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import './style.css'
import './styles/glassmorphism.css'

// Import custom components
import LineItemsManager from './components/LineItemsManager.vue'

const app = createApp(App)

app.use(createPinia())
app.use(router)

// Register global components
app.component('LineItemsManager', LineItemsManager)

app.mount('#app')