<script setup lang="ts">
import { onMounted, ref } from "vue";

import AppAlert from "@/components/feedback/AppAlert.vue";
import ConfirmModal from "@/components/feedback/ConfirmModal.vue";
import PageContainer from "@/components/layout/PageContainer.vue";
import PageHeader from "@/components/layout/PageHeader.vue";
import { usePracticeExam } from "@/composables/usePracticeExam";

const { bank, currentIndex, currentQuestion, selectedIndex, answers, score, isLoading, errorMessage, isFinalSubmitted, progress, load, nextQuestion, finishExam } = usePracticeExam();
const showSubmitModal = ref(false);
onMounted(load);

function openSubmitModal() {
  if (selectedIndex.value !== null) showSubmitModal.value = true;
}

function confirmSubmit() {
  showSubmitModal.value = false;
  finishExam();
}
</script>

<template>
  <PageContainer>
    <PageHeader eyebrow="โหมดฝึกทำข้อสอบ" :title="bank?.title ?? 'ข้อสอบ PDPA'" description="ระบบจะเปิดเผยคะแนนและเฉลยหลังจากกดส่งข้อสอบเท่านั้น">
      <template #actions><RouterLink class="btn btn-ghost" to="/">กลับหน้าภาพรวม</RouterLink></template>
    </PageHeader>

    <AppAlert v-if="isLoading"><span class="loading loading-spinner loading-sm"></span> กำลังโหลดข้อสอบ...</AppAlert>
    <AppAlert v-else-if="errorMessage" type="error">{{ errorMessage }}</AppAlert>

    <section v-else-if="isFinalSubmitted && bank" class="space-y-6">
      <div class="card border border-success/30 bg-base-100 shadow-sm"><div class="card-body items-center text-center"><p class="text-sm text-base-content/60">ส่งข้อสอบเรียบร้อยแล้ว</p><p class="text-6xl font-bold text-success">{{ score }}<span class="text-2xl text-base-content/50"> / {{ bank.questions.length }}</span></p><p class="text-base-content/70">ด้านล่างคือเฉลยและเหตุผลประกอบทุกข้อ</p></div></div>
      <section class="card border border-base-300 bg-base-100 shadow-sm"><div class="card-body"><h2 class="card-title">เฉลยและเหตุผลประกอบ</h2><div class="space-y-2"><details v-for="(question, index) in bank.questions" :key="question.id" class="collapse collapse-arrow border border-base-300 bg-base-100"><summary class="collapse-title font-medium"><span class="badge mr-2" :class="answers[index] === question.correct_index ? 'badge-success' : 'badge-error'">{{ answers[index] === question.correct_index ? 'ถูก' : 'ผิด' }}</span>ข้อ {{ index + 1 }} {{ question.content }}</summary><div class="collapse-content text-sm"><p><strong>คำตอบ:</strong> {{ question.choices[question.correct_index] }}</p><p class="mt-2"><strong>เหตุผล:</strong> {{ question.explanation }}</p></div></details></div></div></section>
    </section>

    <section v-else-if="currentQuestion && bank" class="card border border-base-300 bg-base-100 shadow-sm"><div class="card-body gap-6"><div class="flex flex-wrap items-center justify-between gap-3"><div><span class="badge badge-primary">{{ currentQuestion.topic }}</span><span class="ml-2 text-sm text-base-content/60">ข้อ {{ currentIndex + 1 }} / {{ bank.questions.length }}</span></div><span class="text-sm text-base-content/60">คะแนนจะแสดงหลังส่งข้อสอบ</span></div><progress class="progress progress-primary w-full" :value="progress" max="100"></progress><h2 class="text-xl font-semibold leading-relaxed">{{ currentQuestion.content }}</h2><div class="space-y-3"><label v-for="(choice, index) in currentQuestion.choices" :key="choice" class="flex cursor-pointer items-start gap-3 rounded-xl border border-base-300 p-4 transition hover:border-primary has-[:checked]:border-primary has-[:checked]:bg-primary/5"><input v-model="selectedIndex" class="radio radio-primary mt-1" type="radio" :value="index" /><span><span class="font-semibold">{{ String.fromCharCode(65 + index) }}.</span> {{ choice }}</span></label></div><div class="card-actions justify-end"><button v-if="currentIndex < bank.questions.length - 1" class="btn btn-primary" type="button" :disabled="selectedIndex === null" @click="nextQuestion">บันทึกและข้อต่อไป</button><button v-else class="btn btn-primary" type="button" :disabled="selectedIndex === null" @click="openSubmitModal">ส่งข้อสอบ</button></div></div></section>
    <ConfirmModal :open="showSubmitModal" title="ยืนยันการส่งข้อสอบ" message="หลังจากส่งแล้ว ระบบจะแสดงคะแนนและเฉลย ไม่สามารถกลับมาแก้คำตอบในรอบนี้ได้" confirm-label="ยืนยันส่งข้อสอบ" cancel-label="กลับไปตรวจคำตอบ" @confirm="confirmSubmit" @cancel="showSubmitModal = false" />
  </PageContainer>
</template>
