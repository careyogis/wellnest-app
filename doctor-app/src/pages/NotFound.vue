<template>
  <div class="container-fluid min-vh-100 d-flex align-items-center justify-content-center" style="background: #f5f7fb">
    <div class="text-center p-5" style="max-width: 480px">
      <div class="mb-3" style="font-size: 64px">4️⃣0️⃣4️⃣</div>
      <h3 class="fw-bold mb-2">Page Not Found</h3>
      <p class="text-muted mb-4">The page you are looking for does not exist or has been moved.</p>
      <Button variant="solid" theme="blue" @click="goHome">Back to Profile</Button>
    </div>
  </div>
</template>

<script setup>
import { Button } from 'frappe-ui';
import router from '@/router';

function goHome() {
  router.push({ name: 'Profile' });
}
</script>
