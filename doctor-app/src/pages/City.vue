<template>
    <div class="space-y-4">
      <Avatar :shape="'circle'"
        image="https://avatars.githubusercontent.com/u/499550?s=60&v=4"
        label="RK" size="md" />
      <Tooltip text="This action cannot be undone" :hover-delay="1" :placement="'top'">
        <Button theme="red" @click="cities.next()">
          Next Page
        </Button>
      </Tooltip>
      <div
        class="flex items-center text-blue-800 border-2"
        v-for="city in cities.data"
        :key="city.name">
        <div>
          {{ city.city_name }}, {{ city.state }}
        </div>
        <Badge>{{ city.state }}</Badge>
      </div>
    </div>
  </template>

  <script setup>
  import { Badge, Avatar, Tooltip } from 'frappe-ui'

  import { createListResource } from 'frappe-ui'

  let cities = createListResource({
                doctype: 'City',
                fields: ['city_name', 'state'],
                orderBy: 'creation desc',
                start: 0,
                pageLength: 5,
              })

  cities.reload()
  </script>