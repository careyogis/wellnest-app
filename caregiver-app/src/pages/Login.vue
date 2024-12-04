<template>
  <div class="m-3 flex flex-row items-center justify-center">
    <Card class="w-full max-w-md mt-4">
      <div class="flex flex-row justify-center">
        <img src="../../public/favicon.png" width="50" alt="">
      </div>
      <div class="flex flex-row justify-center mt-4">
        <span class="font-bold">Login to CareYogi App!</span>
      </div>
      <form class="flex flex-col space-y-2 w-full" @submit.prevent="submit">
        <Input
          required
          name="email"
          type="text"
          placeholder="johndoe@email.com"
          label="User ID"
        />
        <Input
          required
          name="password"
          type="password"
          placeholder="••••••"
          label="Password"
        />
        <Button :loading="session.login.loading" variant="solid"
          >Login</Button
        >
      </form>
    </Card>
  </div>
</template>

<script lang="ts" setup>
import { session } from '../data/session'

function submit(e) {
  let formData = new FormData(e.target)
  session.login.submit({
    email: formData.get('email'),
    password: formData.get('password'),
  })
}
</script>
