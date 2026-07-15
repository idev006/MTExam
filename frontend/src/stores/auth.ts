import { computed, ref } from "vue";
import { apiGet, apiRequest } from "@/api/client";
import type { CurrentUser } from "@/types/auth";

const user = ref<CurrentUser | null>(null);
const initialized = ref(false);
export function useAuth() {
  async function loadUser() { try { user.value = await apiGet<CurrentUser>("/auth/me"); } catch { user.value = null; } finally { initialized.value = true; } }
  async function login(username: string, password: string) { user.value = await apiRequest<CurrentUser>("/auth/login", "POST", { username, password }); }
  async function logout() { await apiRequest<{ status: string }>("/auth/logout", "POST"); user.value = null; }
  return { user: computed(() => user.value), initialized: computed(() => initialized.value), loadUser, login, logout, isAuthenticated: computed(() => user.value !== null) };
}
