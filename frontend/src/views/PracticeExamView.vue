<script setup lang="ts">
import { onMounted } from "vue";

import AppAlert from "@/components/feedback/AppAlert.vue";
import PageContainer from "@/components/layout/PageContainer.vue";
import PageHeader from "@/components/layout/PageHeader.vue";
import { usePracticeExam } from "@/composables/usePracticeExam";

const { bank, currentIndex, currentQuestion, selectedIndex, submittedIndex, score, isLoading, errorMessage, isSubmitted, progress, load, submitAnswer, nextQuestion } = usePracticeExam();
onMounted(load);
</script>

<template>
  <PageContainer>
    <PageHeader eyebrow="โหมดฝึกทำข้อสอบ" :title="bank?.title ?? 'ข้อสอบ PDPA'" description="ตอบคำถามแล้วดูเหตุผลประกอบ เพื่อเรียนรู้หลักการ ไม่ใช่ดูเฉพาะคะแนน">
      <template #actions><RouterLink class="btn btn-ghost" to="/">กลับหน้าภาพรวม</RouterLink></template>
    </PageHeader>

    <AppAlert v-if="isLoading"><span class="loading loading-spinner loading-sm"></span> กำลังโหลดข้อสอบ...</AppAlert>
    <AppAlert v-else-if="errorMessage" type="error">{{ errorMessage }}</AppAlert>
    <section v-else-if="currentQuestion" class="card border border-base-300 bg-base-100 shadow-sm">
      <div class="card-body gap-6">
        <div class="flex flex-wrap items-center justify-between gap-3"><div><span class="badge badge-primary">{{ currentQuestion.topic }}</span><span class="ml-2 text-sm text-base-content/60">ข้อ {{ currentIndex + 1 }} / {{ bank?.questions.length }}</span></div><span class="font-semibold text-primary">คะแนน {{ score }}</span></div>
        <progress class="progress progress-primary w-full" :value="progress" max="100"></progress>
        <h2 class="text-xl font-semibold leading-relaxed">{{ currentQuestion.content }}</h2>
        <div class="space-y-3"><label v-for="(choice, index) in currentQuestion.choices" :key="choice" class="flex cursor-pointer items-start gap-3 rounded-xl border border-base-300 p-4 transition hover:border-primary has-[:checked]:border-primary has-[:checked]:bg-primary/5"><input v-model="selectedIndex" class="radio radio-primary mt-1" type="radio" :value="index" :disabled="isSubmitted" /><span><span class="font-semibold">{{ String.fromCharCode(65 + index) }}.</span> {{ choice }}</span></label></div>
        <AppAlert v-if="isSubmitted" :type="submittedIndex === currentQuestion.correct_index ? 'success' : 'warning'"><div><p class="font-semibold">{{ submittedIndex === currentQuestion.correct_index ? 'ตอบถูกต้อง' : `คำตอบที่ถูกคือ ${String.fromCharCode(65 + currentQuestion.correct_index)}` }}</p><p class="mt-1 text-sm">{{ currentQuestion.explanation }}</p></div></AppAlert>
        <div class="card-actions justify-end"><button v-if="!isSubmitted" class="btn btn-primary" type="button" :disabled="selectedIndex === null" @click="submitAnswer">ตรวจคำตอบ</button><button v-else class="btn btn-primary" type="button" :disabled="currentIndex >= (bank?.questions.length ?? 1) - 1" @click="nextQuestion">ข้อต่อไป</button></div>
      </div>
    </section>
  </PageContainer>
</template>
