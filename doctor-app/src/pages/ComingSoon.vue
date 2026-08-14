<template>
  <div class="flex items-center justify-center min-h-[70vh] p-6">
    <div class="text-center max-w-md">
      <div class="w-16 h-16 rounded-full bg-amber-50 flex items-center justify-center text-amber-500 mx-auto mb-4">
        <FeatherIcon name="clock" class="w-7 h-7" />
      </div>
      <h3 class="text-xl font-bold text-gray-900 mb-2">{{ title }} — Coming soon</h3>
      <p class="text-gray-500 text-sm">We're still building this section. Check back soon.</p>
    </div>
  </div>
</template>

<script setup>
import { FeatherIcon } from 'frappe-ui';

defineProps({
  title: {
    type: String,
    default: 'This page',
  },
});
</script>