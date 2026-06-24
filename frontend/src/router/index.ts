import { createRouter, createWebHistory } from 'vue-router'

import ChatView from '../views/ChatView.vue'

export const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'home',
      component: ChatView,
    },
    {
      path: '/chat/:conversationId',
      name: 'chat',
      component: ChatView,
      props: true,
    },
  ],
})
