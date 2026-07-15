import { createRouter, createWebHistory } from "vue-router";

import HomeView from "@/views/HomeView.vue";
import SettingsView from "@/views/SettingsView.vue";
import PracticeExamView from "@/views/PracticeExamView.vue";
import LoginView from "@/views/LoginView.vue";
import { useAuth } from "@/stores/auth";

export const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: "/login",
      name: "login",
      component: LoginView,
    },
    {
      path: "/",
      name: "home",
      component: HomeView,
    },
    {
      path: "/settings",
      name: "settings",
      component: SettingsView,
      meta: { requiresAuth: true },
    },
    {
      path: "/exam/pdpa",
      name: "practice-exam-pdpa",
      component: PracticeExamView,
      meta: { requiresAuth: true },
    },
  ],
});

router.beforeEach(async (to) => {
  const auth = useAuth();
  if (!auth.initialized.value) await auth.loadUser();
  if (to.meta.requiresAuth && !auth.isAuthenticated.value) return { name: "login", query: { redirect: to.fullPath } };
  if (to.name === "login" && auth.isAuthenticated.value) return { name: "home" };
  return true;
});
