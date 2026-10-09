<template>
  <section ref="chatSection" class="w-full overflow-hidden rounded-lg border border-gray-200 bg-white">
    <!-- HEADER -->
    <button type="button" class="w-full flex items-center justify-between gap-3 px-4 py-3 border-b border-gray-200 text-left" @click="chatStatus === 'Active' && (chatExpanded = !chatExpanded)">
      <div class="flex items-center gap-3 min-w-0">
        <!-- Chat icon -->
        <div class="w-10 h-10 shrink-0 rounded-xl bg-teal-50 flex items-center justify-center">
          <FeatherIcon name="message-circle" class="w-5 h-5 text-teal-600" />
        </div>

        <!-- Title + subtitle -->
        <div class="min-w-0">
          <h2 class="text-sm font-bold text-gray-900">Patient chat</h2>
        </div>
      </div>

      <div class="flex items-center gap-3 shrink-0">
        <!-- Active badge -->

        <span
          class="inline-flex items-center rounded-md px-2.5 py-1 text-xs font-semibold"
          :style="chatStatus === 'Active' ? { backgroundColor: '#d1fae5', color: '#047857' } : { backgroundColor: '#f3f4f6', color: '#4b5563' }"
        >
          {{ chatStatus }}
        </span>

        <!-- Chevron -->
        <FeatherIcon name="chevron-up" class="w-5 h-5 text-gray-400 transition-transform duration-200" :class="{ 'rotate-180': !chatExpanded }" />
      </div>
    </button>

    <!-- === CHAT BODY ==== -->
    <div v-if="chatExpanded && chatStatus === 'Active'">
      <!-- Messages -->
      <div ref="messagesContainer" class="bg-[#f8fafc] px-3 py-3 min-h-[200px] max-h-[300px] overflow-y-auto">
        <!-- Loading -->
        <div v-if="loading" class="h-[180px] flex items-center justify-center text-sm text-gray-400">Loading messages...</div>

        <!-- Error -->
        <div v-else-if="errorMessage" class="h-[180px] flex items-center justify-center px-4 text-center">
          <div class="text-sm text-red-600">
            {{ errorMessage }}
          </div>
        </div>

        <!-- Empty -->
        <div v-else-if="messages.length === 0" class="h-[180px] flex items-center justify-center text-sm text-gray-400">No messages yet.</div>

        <!-- Message list -->
        <div v-else class="space-y-2">
          <template v-for="item in messages" :key="item.name">
            <!-- Patient message -->
            <div v-if="item.sender_type === 'Patient'" class="flex justify-start">
              <div class="max-w-[72%]">
                <div class="rounded-lg border border-gray-200 bg-white px-3 py-2">
                  <p v-if="item.message" class="text-sm text-gray-800 leading-5 whitespace-pre-wrap break-words">
                    {{ item.message }}
                  </p>

                  <!-- Attachment -->
                  <a
                    v-if="item.attachment"
                    :href="getFileUrl(item.attachment)"
                    target="_blank"
                    rel="noopener noreferrer"
                    class="flex items-center gap-2 mt-1 text-sm text-gray-700 hover:text-amber-600"
                  >
                    <FeatherIcon name="paperclip" class="w-3.5 h-3.5 shrink-0" />

                    <span class="truncate">
                      {{ getAttachmentName(item.attachment) }}
                    </span>
                  </a>
                </div>

                <div class="text-[10px] text-gray-400 text-right mt-0.5 pr-1">
                  {{ formatTime(item.sent_at) }}
                </div>
              </div>
            </div>

            <!-- Doctor message -->
            <div v-else class="flex justify-end">
              <div class="max-w-[72%]">
                <div class="rounded-lg border border-teal-200 bg-[#eaf8f7] px-3 py-2">
                  <p v-if="item.message" class="text-sm text-gray-800 leading-5 whitespace-pre-wrap break-words">
                    {{ item.message }}
                  </p>

                  <!-- Attachment -->
                  <a
                    v-if="item.attachment"
                    :href="getFileUrl(item.attachment)"
                    target="_blank"
                    rel="noopener noreferrer"
                    class="flex items-center gap-2 mt-1 text-sm text-gray-700 hover:text-amber-600"
                  >
                    <FeatherIcon name="paperclip" class="w-3.5 h-3.5 shrink-0" />

                    <span class="truncate">
                      {{ getAttachmentName(item.attachment) }}
                    </span>
                  </a>
                </div>

                <div class="text-[10px] text-gray-400 mt-0.5 pl-1">
                  {{ formatTime(item.sent_at) }}
                </div>
              </div>
            </div>
          </template>
        </div>
      </div>

      <div class="px-2 py-2 border-t border-gray-200 bg-white">
        <div class="flex items-center gap-2">
          <!-- Attachment button -->
          <button
            type="button"
            class="w-10 h-10 shrink-0 rounded-lg border border-gray-200 bg-white flex items-center justify-center text-gray-500 hover:bg-gray-50 hover:text-gray-700 disabled:opacity-50"
            :disabled="sending"
            title="Attach file"
            @click="openFilePicker"
          >
            <FeatherIcon name="paperclip" class="w-4 h-4" />
          </button>

          <input ref="fileInput" type="file" class="hidden" @change="handleFileChange" />

          <!-- Message input -->
          <input
            v-model="newMessage"
            type="text"
            placeholder="Message or reply..."
            class="flex-1 min-w-0 h-10 rounded-lg border border-gray-200 px-3 text-sm text-gray-900 placeholder:text-gray-400 focus:outline-none focus:ring-1 focus:ring-amber-300 focus:border-amber-300 disabled:bg-gray-50"
            :disabled="sending"
            @keydown.enter.prevent="sendMessage"
          />

          <!-- Send button -->
          <button
            type="button"
            class="w-10 h-10 shrink-0 rounded-lg bg-amber-500 hover:bg-amber-400 text-white flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed"
            :disabled="sending || (!newMessage.trim() && !selectedFile)"
            title="Send message"
            @click="sendMessage"
          >
            <FeatherIcon v-if="!sending" name="send" class="w-4 h-4" />

            <span v-else class="w-4 h-4 border-2 border-white/40 border-t-white rounded-full animate-spin"></span>
          </button>
        </div>

        <!-- Selected attachment -->
        <div v-if="selectedFile" class="flex items-center justify-between gap-2 px-1 pt-2">
          <div class="flex items-center gap-1.5 min-w-0 text-xs text-gray-500">
            <FeatherIcon name="paperclip" class="w-3.5 h-3.5 shrink-0" />

            <span class="truncate">
              {{ selectedFile.name }}
            </span>
          </div>

          <button type="button" class="text-xs text-red-500 hover:text-red-600 shrink-0" @click="removeSelectedFile">Remove</button>
        </div>
      </div>

      <div class="px-4 py-2 border-t border-gray-100 bg-white text-xs text-gray-500">
        {{ followUpText }}
      </div>
    </div>
  </section>
</template>

<script setup>
import { nextTick, onUnmounted, ref, watch } from 'vue';
import { FeatherIcon, createResource } from 'frappe-ui';

const props = defineProps({
  appointmentId: {
    type: String,
    default: null,
  },

  chatStatus: {
    type: String,
    default: 'Active',
  },

  followUpText: {
    type: String,
    default: '...',
  },
});

const messages = ref([]);
const loading = ref(false);
const sending = ref(false);
const errorMessage = ref('');

const newMessage = ref('');
const selectedFile = ref(null);

const chatExpanded = ref(false);

const fileInput = ref(null);
const messagesContainer = ref(null);

const chatResource = createResource({
  url: 'wellnest.api.patient_chat.get_patient_chat',
});

const markReadResource = createResource({
  url: 'wellnest.api.patient_chat.mark_patient_chat_read',
});

const sendMessageResource = createResource({
  url: 'wellnest.api.patient_chat.send_patient_chat_message',
});

const chatSection = ref(null);

async function openChat() {
  if (props.chatStatus !== 'Active') return;

  chatExpanded.value = true;
  await nextTick();

  chatSection.value?.scrollIntoView({
    behavior: 'smooth',
    block: 'center',
  });
}

defineExpose({ openChat });

async function loadMessages() {
  if (!props.appointmentId) {
    messages.value = [];
    return;
  }

  loading.value = true;
  errorMessage.value = '';

  try {
    const response = await chatResource.submit({
      patient_appointment: props.appointmentId,
    });

    const result = response?.message || response || {};

    messages.value = Array.isArray(result.messages) ? result.messages : [];

    await markMessagesAsRead();
    await scrollToBottom();
  } catch (error) {
    console.error('Failed to load patient chat:', error);

    errorMessage.value = error?.message || 'Failed to load patient chat.';
  } finally {
    loading.value = false;
  }
}

async function markMessagesAsRead() {
  if (!props.appointmentId) {
    return;
  }

  try {
    await markReadResource.submit({
      patient_appointment: props.appointmentId,
    });
  } catch (error) {
    console.error('Failed to mark patient chat as read:', error);
  }
}

function openFilePicker() {
  fileInput.value?.click();
}

function handleFileChange(event) {
  const file = event.target.files?.[0];

  if (!file) {
    return;
  }

  selectedFile.value = file;
}

function removeSelectedFile() {
  selectedFile.value = null;

  if (fileInput.value) {
    fileInput.value.value = '';
  }
}

async function uploadFile(file) {
  const formData = new FormData();

  formData.append('file', file);
  formData.append('is_private', '1');

  const response = await fetch('/api/method/upload_file', {
    method: 'POST',
    headers: {
      'X-Frappe-CSRF-Token': window.csrf_token,
    },
    body: formData,
  });

  if (!response.ok) {
    throw new Error(`File upload failed (${response.status})`);
  }

  const result = await response.json();

  const fileUrl = result?.message?.file_url;

  if (!fileUrl) {
    throw new Error('File upload failed.');
  }

  return fileUrl;
}

async function sendMessage() {
  if (!props.appointmentId || sending.value) {
    return;
  }

  const message = newMessage.value.trim();
  const file = selectedFile.value;

  if (!message && !file) {
    return;
  }

  sending.value = true;
  errorMessage.value = '';

  try {
    let attachmentUrl = null;

    if (file) {
      attachmentUrl = await uploadFile(file);
    }

    const response = await sendMessageResource.submit({
      patient_appointment: props.appointmentId,

      message,

      attachment: attachmentUrl,
    });

    const sentMessage = response?.message?.message || response?.message || response?.data?.message || response?.data || response;

    if (sentMessage?.name) {
      messages.value.push(sentMessage);
    } else {
      await loadMessages();
    }

    newMessage.value = '';
    removeSelectedFile();

    await scrollToBottom();
  } catch (error) {
    console.error('Failed to send patient chat message:', error);

    errorMessage.value = error?.message || 'Failed to send message.';
  } finally {
    sending.value = false;
  }
}

function getFileUrl(fileUrl) {
  if (!fileUrl) {
    return '#';
  }

  if (fileUrl.startsWith('http://') || fileUrl.startsWith('https://')) {
    return fileUrl;
  }

  return fileUrl;
}

function getAttachmentName(fileUrl) {
  if (!fileUrl) {
    return 'Attachment';
  }

  try {
    const cleanUrl = fileUrl.split('?')[0];

    const parts = cleanUrl.split('/');

    const name = parts[parts.length - 1];

    return name || 'Attachment';
  } catch {
    return 'Attachment';
  }
}

function formatTime(value) {
  if (!value) {
    return '';
  }

  try {
    const date = new Date(value);

    if (Number.isNaN(date.getTime())) {
      return '';
    }

    return date.toLocaleTimeString([], {
      hour: '2-digit',
      minute: '2-digit',
    });
  } catch {
    return '';
  }
}

async function scrollToBottom() {
  await nextTick();

  if (!messagesContainer.value) {
    return;
  }

  messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight;
}

watch(
  () => props.appointmentId,
  async (newAppointment, oldAppointment) => {
    if (newAppointment === oldAppointment) {
      return;
    }

    messages.value = [];
    newMessage.value = '';

    removeSelectedFile();

    await loadMessages();
  },
  {
    immediate: true,
  }
);

/*== CLEANUP ==*/
onUnmounted(() => {
  messages.value = [];
});
</script>
