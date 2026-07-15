<script setup lang="ts">
import { RouterView } from "vue-router";
</script>

<template>
  <div class="min-h-screen">
    <header class="navbar border-b border-base-300 bg-base-100 px-4">
      <div class="mx-auto w-full max-w-5xl">
        <span class="text-xl font-bold">MTExam</span>
      </div>
    </header>
    <RouterView />
  </div>
</template>
