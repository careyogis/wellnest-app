<template>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link
    rel="preconnect"
    href="https://fonts.gstatic.com"
    crossorigin="anonymous"
  />
  <link
    href="https://fonts.googleapis.com/css2?family=Quicksand:wght@300..700&display=swap"
    rel="stylesheet"
  />
  <div>
    <router-view />
    <InstallPrompt />
  </div>
</template>

<script setup>
import InstallPrompt from '@/components/InstallPrompt.vue'
</script>
<style>
body {
  font-family: 'Quicksand', sans-serif;
}

.bro button[role='tab'][aria-selected='true'] {
  color: #78abaf !important;
  font-weight: bold;
}

div.bottom-0 {
  background-color: #78abaf;
}
</style>
