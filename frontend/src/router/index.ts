import { createRouter, createWebHistory } from "vue-router";

import HomeView from "@/views/HomeView.vue";
import SettingsView from "@/views/SettingsView.vue";
import PracticeExamView from "@/views/PracticeExamView.vue";
import LoginView from "@/views/LoginView.vue";
import { useAuth } from "@/stores/auth";
import ReportsView from "@/views/ReportsView.vue";
import UserAdminView from "@/views/UserAdminView.vue";
import AuthoringView from "@/views/AuthoringView.vue";
import PaperBuilderView from "@/views/PaperBuilderView.vue";
import AuditView from "@/views/AuditView.vue";
import ExamLobbyView from "@/views/ExamLobbyView.vue";
import ExamSessionView from "@/views/ExamSessionView.vue";

export const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: "/audit",
      name: "audit",
      component: AuditView,
      meta: { requiresAuth: true, allowedRoles: ["super_admin", "viewer", "division_admin", "bureau_admin", "station_admin"] },
    },
    {
      path: "/admin/users",
      name: "user-admin",
      component: UserAdminView,
      meta: { requiresAuth: true, allowedRoles: ["super_admin"] },
    },
    {
      path: "/authoring",
      name: "authoring",
      component: AuthoringView,
      meta: { requiresAuth: true, allowedRoles: ["super_admin", "exam_author"] },
    },
    {
      path: "/papers",
      name: "paper-builder",
      component: PaperBuilderView,
      meta: { requiresAuth: true, allowedRoles: ["super_admin", "exam_author"] },
    },
    {
      path: "/reports",
      name: "reports",
      component: ReportsView,
      meta: { requiresAuth: true, allowedRoles: ["super_admin", "viewer", "division_admin", "bureau_admin", "station_admin"] },
    },
    {
      path: "/login",
      name: "login",
      component: LoginView,
    },
    {
      path: "/",
      name: "home",
      component: HomeView,
      meta: { requiresAuth: true },
    },
    {
      path: "/settings",
      name: "settings",
      component: SettingsView,
      meta: { requiresAuth: true, allowedRoles: ["super_admin"] },
    },
    {
      path: "/exam",
      name: "exam-lobby",
      component: ExamLobbyView,
      meta: { requiresAuth: true, allowedRoles: ["super_admin", "examinee"] },
    },
    {
      path: "/exam/window/:windowId",
      name: "exam-session",
      component: ExamSessionView,
      meta: { requiresAuth: true, allowedRoles: ["super_admin", "examinee"] },
    },
    {
      path: "/exam/pdpa",
      name: "practice-exam-pdpa",
      component: PracticeExamView,
      meta: { requiresAuth: true, allowedRoles: ["super_admin", "examinee"] },
    },
  ],
});

router.beforeEach(async (to) => {
  const auth = useAuth();
  if (!auth.initialized.value) await auth.loadUser();
  if (to.meta.requiresAuth && !auth.isAuthenticated.value) return { name: "login", query: { redirect: to.fullPath } };
  const allowedRoles = to.meta.allowedRoles as string[] | undefined;
  if (allowedRoles && auth.user.value && auth.user.value.role !== "super_admin" && !allowedRoles.includes(auth.user.value.role)) return { name: "home" };
  if (to.name === "login" && auth.isAuthenticated.value) return { name: "home" };
  return true;
});
