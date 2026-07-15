<script setup lang="ts">
import AppAlert from "@/components/feedback/AppAlert.vue";
import PageContainer from "@/components/layout/PageContainer.vue";
import PageHeader from "@/components/layout/PageHeader.vue";
import { useHealth } from "@/composables/useHealth";

const { health, errorMessage, isLoading, loadHealth } = useHealth();
</script>

<template>
  <PageContainer>
    <PageHeader
      eyebrow="M0 Foundation"
      title="MTExam"
      description="ระบบสอบออนไลน์แบบเลือกตอบและจับเวลา โดยใช้ API เป็น System Core"
    />

    <section class="card border border-base-300 bg-base-100 shadow-xl">
      <div class="card-body gap-6">
        <AppAlert v-if="isLoading">
          <span class="loading loading-spinner loading-sm"></span>
          <span>กำลังตรวจสอบ API...</span>
        </AppAlert>

        <AppAlert v-else-if="health" type="success">
          <span class="status status-success"></span>
          <div>
            <p class="font-semibold">API พร้อมใช้งาน</p>
            <p class="text-sm">
              {{ health.app_name }} {{ health.version }} · Database: {{ health.database }}
            </p>
          </div>
        </AppAlert>

        <AppAlert v-else type="error">
          <div class="grow">
            <p class="font-semibold">ยังเชื่อมต่อ API ไม่ได้</p>
            <p class="text-sm">{{ errorMessage }}</p>
          </div>
          <button class="btn btn-sm" type="button" @click="loadHealth">ลองใหม่</button>
        </AppAlert>
      </div>
    </section>
  </PageContainer>
</template>
