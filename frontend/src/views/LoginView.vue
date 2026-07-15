<script setup lang="ts">
import { ref } from "vue";
import { useRouter } from "vue-router";
import AppAlert from "@/components/feedback/AppAlert.vue";
import PageContainer from "@/components/layout/PageContainer.vue";
import { useAuth } from "@/stores/auth";

const router = useRouter(); const { login } = useAuth(); const username = ref(""); const password = ref(""); const error = ref(""); const isLoading = ref(false);
async function submit() { error.value = ""; isLoading.value = true; try { await login(username.value, password.value); await router.push((router.currentRoute.value.query.redirect as string) || "/"); } catch { error.value = "ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง"; } finally { isLoading.value = false; } }
</script>
<template><PageContainer><div class="mx-auto max-w-md"><section class="card border border-base-300 bg-base-100 shadow-sm"><div class="card-body"><h1 class="card-title text-2xl">เข้าสู่ระบบ</h1><p class="text-sm text-base-content/60">เข้าสู่ระบบเพื่อทำข้อสอบและกู้คืน session ได้อย่างปลอดภัย</p><AppAlert v-if="error" type="error">{{ error }}</AppAlert><form class="space-y-4" @submit.prevent="submit"><label class="form-control"><span class="label-text">ชื่อผู้ใช้</span><input v-model="username" class="input input-bordered" autocomplete="username" required /></label><label class="form-control"><span class="label-text">รหัสผ่าน</span><input v-model="password" class="input input-bordered" type="password" autocomplete="current-password" required /></label><button class="btn btn-primary w-full" :disabled="isLoading" type="submit"><span v-if="isLoading" class="loading loading-spinner loading-sm"></span>เข้าสู่ระบบ</button></form><p class="text-xs text-base-content/50">บัญชีสาธิตสำหรับ Development: demo / demo1234</p></div></section></div></PageContainer></template>
