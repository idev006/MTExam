<script setup lang="ts">
import { useHealth } from "@/composables/useHealth";

const { health, errorMessage, isLoading, loadHealth } = useHealth();
</script>

<template>
  <main class="mx-auto flex min-h-[calc(100vh-4rem)] max-w-5xl items-center px-4 py-12">
    <section class="card w-full border border-base-300 bg-base-100 shadow-xl">
      <div class="card-body gap-6">
        <div>
          <div class="badge badge-primary badge-outline mb-3">M0 Foundation</div>
          <h1 class="card-title text-4xl">MTExam</h1>
          <p class="mt-2 max-w-2xl text-base-content/70">
            ระบบสอบออนไลน์แบบเลือกตอบและจับเวลา โดยใช้ API เป็น System Core
          </p>
        </div>

        <div v-if="isLoading" class="alert" aria-live="polite">
          <span class="loading loading-spinner loading-sm"></span>
          <span>กำลังตรวจสอบ API...</span>
        </div>

        <div v-else-if="health" class="alert alert-success" aria-live="polite">
          <span class="status status-success"></span>
          <div>
            <p class="font-semibold">API พร้อมใช้งาน</p>
            <p class="text-sm">
              {{ health.app_name }} {{ health.version }} · Database: {{ health.database }}
            </p>
          </div>
        </div>

        <div v-else class="alert alert-error" role="alert">
          <div class="grow">
            <p class="font-semibold">ยังเชื่อมต่อ API ไม่ได้</p>
            <p class="text-sm">{{ errorMessage }}</p>
          </div>
          <button class="btn btn-sm" type="button" @click="loadHealth">ลองใหม่</button>
        </div>
      </div>
    </section>
  </main>
</template>
