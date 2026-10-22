<template>
  <div class="flex h-[calc(100vh-112px)] min-h-[560px] flex-col overflow-hidden rounded-2xl border border-gray-200 bg-white">
    <!-- Page header -->
    <header class="flex items-center justify-between gap-4 border-b border-gray-200 px-5 py-4">
      <div class="min-w-0">
        <h1 class="text-xl font-bold text-gray-900">Messages</h1>
        <p class="mt-1 text-sm text-gray-500">Conversations with your patients</p>
      </div>

      <button
        type="button"
        class="inline-flex h-10 items-center gap-2 rounded-lg border border-gray-200 px-3 text-sm font-medium text-gray-700 hover:bg-gray-50"
        :disabled="listLoading"
        @click="loadConversations"
      >
        <FeatherIcon name="refresh-cw" class="h-4 w-4" :class="{ 'animate-spin': listLoading }" />
        Refresh
      </button>
    </header>

    <!-- Main workspace -->
    <div class="grid min-h-0 flex-1 grid-cols-1 md:grid-cols-[320px_minmax(0,1fr)]">
      <!-- Conversation list -->
      <aside class="flex min-h-0 flex-col border-b border-gray-200 md:border-b-0 md:border-r">
        <div class="border-b border-gray-100 p-4">
          <label class="relative block">
            <FeatherIcon name="search" class="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
            <input
              v-model="searchQuery"
              type="search"
              placeholder="Search patients..."
              class="h-10 w-full rounded-lg border border-gray-200 bg-gray-50 pl-9 pr-3 text-sm outline-none focus:border-teal-500 focus:bg-white focus:ring-1 focus:ring-teal-500"
            />
          </label>

          <div class="mt-3 flex items-center justify-between">
            <span class="text-xs font-semibold uppercase tracking-wide text-gray-500"> Conversations </span>
            <span class="rounded-full bg-gray-100 px-2 py-0.5 text-xs font-medium text-gray-600">
              {{ filteredConversations.length }}
            </span>
          </div>
        </div>

        <div class="min-h-0 flex-1 overflow-y-auto">
          <div v-if="listLoading && conversations.length === 0" class="p-6 text-center text-sm text-gray-500">Loading conversations...</div>

          <div v-else-if="listError" class="p-4 text-sm text-red-600">
            {{ listError }}
            <button type="button" class="mt-2 block font-semibold underline" @click="loadConversations">Try again</button>
          </div>

          <div v-else-if="filteredConversations.length === 0" class="px-5 py-12 text-center">
            <div class="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-gray-100">
              <FeatherIcon name="message-circle" class="h-5 w-5 text-gray-400" />
            </div>
            <p class="mt-3 text-sm font-medium text-gray-800">
              {{ searchQuery ? 'No matching patients' : 'No conversations yet' }}
            </p>
            <p class="mt-1 text-xs text-gray-500">
              {{ searchQuery ? 'Try another name.' : 'Patient conversations will appear here.' }}
            </p>
          </div>

          <button
            v-for="conversation in filteredConversations"
            :key="conversation.appointment"
            type="button"
            class="flex w-full items-start gap-3 border-b border-gray-100 px-4 py-4 text-left transition hover:bg-gray-50"
            :class="{
              'bg-teal-50 hover:bg-teal-50 border-l-4 border-l-teal-600': selectedAppointmentId === conversation.appointment,
            }"
            @click="selectConversation(conversation)"
          >
            <div class="flex h-11 w-11 shrink-0 items-center justify-center rounded-full bg-teal-100 text-sm font-bold text-teal-800">
              {{ initials(conversation.patient_name) }}
            </div>

            <div class="min-w-0 flex-1">
              <div class="flex items-start justify-between gap-2">
                <p class="truncate text-sm font-semibold text-gray-900">
                  {{ conversation.patient_name || conversation.patient }}
                </p>
                <span class="shrink-0 text-[11px] text-gray-400">
                  {{ formatListTime(conversation.latest_message_at || conversation.scheduled_time) }}
                </span>
              </div>

              <p class="mt-1 truncate text-xs text-gray-500">
                {{ conversation.latest_message || 'No messages yet' }}
              </p>

              <div class="mt-2 flex flex-wrap items-center gap-2">
                <span
                  v-if="Number(conversation.unread_count) > 0"
                  class="ml-auto inline-flex h-6 min-w-5 items-center justify-center rounded-md bg-red-500 px-1.5 py-0.5 text-[10px] font-bold text-white"
                >
                  {{ conversation.unread_count }}
                </span>
              </div>
            </div>
          </button>
        </div>
      </aside>

      <!-- Selected conversation -->
      <section class="flex min-h-0 min-w-0 flex-col">
        <template v-if="selectedConversation">
          <!-- Conversation header -->
          <header class="flex items-center justify-between gap-3 border-b border-gray-200 px-5 py-4">
            <div class="flex min-w-0 items-center gap-3">
              <div class="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-teal-100 text-sm font-bold text-teal-800">
                {{ initials(selectedConversation.patient_name) }}
              </div>

              <div class="min-w-0">
                <h2 class="truncate text-sm font-bold text-gray-900">
                  {{ selectedConversation.patient_name || selectedConversation.patient }}
                </h2>
                <p class="mt-0.5 truncate text-xs text-gray-500">Consultation {{ selectedConversation.appointment }}</p>
              </div>
            </div>

            <div class="flex shrink-0 items-center gap-2">
              <!-- <button
                type="button"
                class="hidden items-center gap-1.5 rounded-lg border border-gray-200 px-3 py-2 text-xs font-medium text-gray-700 hover:bg-gray-50 sm:inline-flex"
                @click="openConsultation"
              >
                Open record
                <FeatherIcon name="external-link" class="h-3.5 w-3.5" />
              </button> -->
            </div>
          </header>

          <!-- Messaging information -->
          <div class="flex items-start gap-2 border-b border-gray-100 bg-gray-50 px-5 py-3">
            <FeatherIcon name="info" class="mt-0.5 h-4 w-4 shrink-0 text-gray-400" />
            <p class="text-xs leading-5 text-gray-600">You can view previous messages and continue communicating with this patient.</p>
          </div>

          <!-- Messages -->
          <div ref="messagesContainer" class="min-h-0 flex-1 overflow-y-auto bg-[#f8fafc] px-4 py-5 sm:px-6">
            <div v-if="messagesLoading" class="flex h-full min-h-40 items-center justify-center text-sm text-gray-500">Loading messages...</div>

            <div v-else-if="messagesError" class="flex h-full min-h-40 flex-col items-center justify-center gap-3 text-center">
              <p class="max-w-md text-sm text-red-600">{{ messagesError }}</p>
              <button type="button" class="rounded-lg border border-gray-200 bg-white px-3 py-2 text-sm font-medium text-gray-700" @click="loadMessages">Try again</button>
            </div>

            <div v-else-if="messages.length === 0" class="flex h-full min-h-40 flex-col items-center justify-center text-center">
              <div class="flex h-12 w-12 items-center justify-center rounded-full bg-white shadow-sm">
                <FeatherIcon name="message-circle" class="h-5 w-5 text-gray-400" />
              </div>
              <p class="mt-3 text-sm font-medium text-gray-700">No messages yet</p>
              <p class="mt-1 text-xs text-gray-500">Messages exchanged with this patient will appear here.</p>
            </div>

            <div v-else class="space-y-5">
              <div v-for="item in messages" :key="item.name" class="flex" :class="item.sender_type === 'Doctor' ? 'justify-end' : 'justify-start'">
                <div class="max-w-[85%] sm:max-w-[72%]">
                  <div
                    class="rounded-2xl px-4 py-3 shadow-sm"
                    :class="item.sender_type === 'Doctor' ? 'rounded-br-md border border-amber-500 bg-amber-500 text-white' : 'rounded-bl-md border border-gray-200 bg-white'"
                  >
                    <p v-if="item.message" class="whitespace-pre-wrap break-words text-sm leading-6" :class="item.sender_type === 'Doctor' ? 'text-white' : 'text-gray-800'">
                      {{ item.message }}
                    </p>

                    <a v-if="item.attachment" :href="getFileUrl(item.attachment)" target="_blank" rel="noopener noreferrer" class="mt-2 flex items-center gap-2 text-sm text-teal-700 hover:underline">
                      <FeatherIcon name="paperclip" class="h-4 w-4 shrink-0" />
                      <span class="break-all">{{ getAttachmentName(item.attachment) }}</span>
                    </a>
                  </div>

                  <p class="mt-1 text-[11px] text-gray-400" :class="item.sender_type === 'Doctor' ? 'text-right' : 'text-left'">
                    {{ item.sender_type === 'Doctor' ? 'You' : 'Patient' }}
                    <span v-if="item.sent_at"> · {{ formatMessageTime(item.sent_at) }}</span>
                  </p>
                </div>
              </div>
            </div>
          </div>

          <!-- Composer -->
          <div class="border-t border-gray-200 bg-white p-4">
            <div v-if="sendError" class="mb-3 rounded-lg border border-red-100 bg-red-50 px-3 py-2 text-sm text-red-700">
              {{ sendError }}
            </div>

            <div v-if="selectedFile" class="mb-3 flex items-center justify-between gap-3 rounded-lg border border-gray-200 bg-gray-50 px-3 py-2">
              <div class="flex min-w-0 items-center gap-2 text-xs text-gray-600">
                <FeatherIcon name="paperclip" class="h-4 w-4 shrink-0" />
                <span class="truncate">{{ selectedFile.name }}</span>
              </div>
              <button type="button" class="text-xs font-medium text-red-600 hover:text-red-700" :disabled="sending" @click="removeSelectedFile">Remove</button>
            </div>

            <form class="flex items-end gap-2" @submit.prevent="sendMessage">
              <input ref="fileInput" type="file" class="hidden" @change="handleFileChange" />

              <button
                type="button"
                title="Attach file"
                aria-label="Attach file"
                class="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl border border-gray-200 text-gray-500 hover:bg-gray-50 disabled:opacity-50"
                :disabled="sending"
                @click="fileInput?.click()"
              >
                <FeatherIcon name="paperclip" class="h-5 w-5" />
              </button>

              <textarea
                v-model="newMessage"
                rows="1"
                placeholder="Write a message..."
                class="max-h-32 min-h-11 min-w-0 flex-1 resize-y rounded-xl border border-gray-200 px-4 py-3 text-sm text-gray-900 outline-none focus:border-teal-500 focus:ring-1 focus:ring-teal-500 disabled:bg-gray-50"
                :disabled="sending"
                @keydown.enter.exact.prevent="sendMessage"
              />

              <button
                type="submit"
                class="flex h-11 shrink-0 items-center justify-center gap-2 rounded-xl bg-amber-500 px-4 text-sm font-semibold text-white hover:bg-amber-600 disabled:cursor-not-allowed disabled:opacity-50"
                :disabled="sending || (!newMessage.trim() && !selectedFile)"
              >
                <FeatherIcon v-if="!sending" name="send" class="h-4 w-4" />
                <span v-else class="h-4 w-4 animate-spin rounded-full border-2 border-white/40 border-t-white" />
                <span class="hidden sm:inline">{{ sending ? 'Sending' : 'Send' }}</span>
              </button>
            </form>
          </div>
        </template>

        <!-- No selection -->
        <div v-else class="flex min-h-0 flex-1 flex-col items-center justify-center px-6 text-center">
          <div class="flex h-16 w-16 items-center justify-center rounded-2xl bg-teal-50">
            <FeatherIcon name="message-circle" class="h-7 w-7 text-teal-600" />
          </div>
          <h2 class="mt-4 text-base font-semibold text-gray-900">Select a conversation</h2>
          <p class="mt-2 max-w-xs text-sm leading-6 text-gray-500">Choose a patient from the list to view the conversation and message history.</p>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { computed, nextTick, onMounted, ref, watch } from 'vue';
import { createResource, FeatherIcon } from 'frappe-ui';
import { useRoute, useRouter } from 'vue-router';

const router = useRouter();
const route = useRoute();

const conversations = ref([]);
const selectedConversation = ref(null);
const selectedAppointmentId = ref('');
const messages = ref([]);

const searchQuery = ref('');
const listLoading = ref(false);
const messagesLoading = ref(false);
const sending = ref(false);

const listError = ref('');
const messagesError = ref('');
const sendError = ref('');

const newMessage = ref('');
const selectedFile = ref(null);

const fileInput = ref(null);
const messagesContainer = ref(null);

const conversationsResource = createResource({
  url: 'wellnest.api.patient_chat.get_doctor_patient_chats',
});

const chatResource = createResource({
  url: 'wellnest.api.patient_chat.get_patient_chat',
});

const markReadResource = createResource({
  url: 'wellnest.api.patient_chat.mark_patient_chat_read',
});

const sendMessageResource = createResource({
  url: 'wellnest.api.patient_chat.send_patient_chat_message',
});

const filteredConversations = computed(() => {
  const query = searchQuery.value.trim().toLowerCase();

  if (!query) return conversations.value;

  return conversations.value.filter((conversation) => {
    const name = String(conversation.patient_name || conversation.patient || '').toLowerCase();

    return name.includes(query);
  });
});

async function loadConversations() {
  listLoading.value = true;
  listError.value = '';

  try {
    const response = await conversationsResource.submit({});
    const result = response?.message || response || {};

    conversations.value = Array.isArray(result.conversations) ? result.conversations : [];

    if (selectedAppointmentId.value) {
      const updated = conversations.value.find((item) => item.appointment === selectedAppointmentId.value);

      if (updated) {
        selectedConversation.value = updated;
      } else {
        selectedConversation.value = null;
        selectedAppointmentId.value = '';
        messages.value = [];
      }
    }

    const appointmentId = route.query.appointment;
    const patientId = route.query.patient;

    if (appointmentId || patientId) {
      const matchingConversation = conversations.value.find((item) => (appointmentId ? item.appointment === appointmentId : item.patient === patientId));

      if (matchingConversation) {
        await selectConversation(matchingConversation);
      } else {
        selectedConversation.value = null;
        selectedAppointmentId.value = '';
        messages.value = [];
        listError.value = 'The requested patient conversation could not be found.';
        return;
      }
    }

    if (!selectedConversation.value && conversations.value.length) {
      await selectConversation(conversations.value[0]);
    }
  } catch (error) {
    console.error('Failed to load doctor conversations:', error);
    listError.value = error?.message || 'Failed to load conversations.';
  } finally {
    listLoading.value = false;
  }
}

async function selectConversation(conversation) {
  if (!conversation?.appointment) return;

  selectedConversation.value = conversation;
  selectedAppointmentId.value = conversation.appointment;

  messages.value = [];
  messagesError.value = '';
  sendError.value = '';
  newMessage.value = '';
  removeSelectedFile();

  await loadMessages();
}

async function loadMessages() {
  const appointmentId = selectedAppointmentId.value;

  if (!appointmentId) {
    messages.value = [];
    return;
  }

  messagesLoading.value = true;
  messagesError.value = '';

  try {
    const response = await chatResource.submit({
      patient_appointment: appointmentId,
    });

    if (selectedAppointmentId.value !== appointmentId) return;

    const result = response?.message || response || {};

    messages.value = Array.isArray(result.messages) ? result.messages : [];

    await markReadResource.submit({
      patient_appointment: appointmentId,
    });

    window.dispatchEvent(new Event('doctor-chat-read'));

    await scrollToBottom();

    const conversation = conversations.value.find((item) => item.appointment === appointmentId);

    if (conversation) {
      conversation.unread_count = 0;
    }
  } catch (error) {
    console.error('Failed to load patient conversation:', error);
    messagesError.value = error?.message || 'Failed to load messages.';
  } finally {
    messagesLoading.value = false;
  }
}

async function sendMessage() {
  const appointmentId = selectedAppointmentId.value;
  const conversation = selectedConversation.value;

  if (!appointmentId || sending.value || !conversation) return;

  const message = newMessage.value.trim();
  const file = selectedFile.value;

  if (!message && !file) return;

  sending.value = true;
  sendError.value = '';

  try {
    let attachmentUrl = null;

    if (file) {
      attachmentUrl = await uploadFile(file);
    }

    const response = await sendMessageResource.submit({
      patient_appointment: appointmentId,
      message,
      attachment: attachmentUrl,
    });

    if (selectedAppointmentId.value !== appointmentId) return;

    const result = response?.message?.message || response?.message || response?.data?.message || response?.data || response;

    if (result?.name) {
      messages.value.push(result);
    } else {
      await loadMessages();
    }

    newMessage.value = '';
    removeSelectedFile();

    await scrollToBottom();

    // Refresh the preview and unread information without changing selection.
    await refreshConversationPreview(appointmentId);
  } catch (error) {
    console.error('Failed to send patient chat message:', error);
    sendError.value = error?.message || 'Failed to send message.';
  } finally {
    sending.value = false;
  }
}

async function refreshConversationPreview(appointmentId) {
  try {
    const response = await conversationsResource.submit({});
    const result = response?.message || response || {};

    if (Array.isArray(result.conversations)) {
      conversations.value = result.conversations;

      const updated = conversations.value.find((item) => item.appointment === appointmentId);

      if (updated) {
        selectedConversation.value = updated;
      }
    }
  } catch (error) {
    console.warn('Failed to refresh conversation preview:', error);
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
    throw new Error('The uploaded file URL was not returned.');
  }

  return fileUrl;
}

function handleFileChange(event) {
  const file = event.target.files?.[0];

  if (file) selectedFile.value = file;
}

function removeSelectedFile() {
  selectedFile.value = null;

  if (fileInput.value) {
    fileInput.value.value = '';
  }
}

function openConsultation() {
  if (!selectedConversation.value?.appointment) return;

  router.push({
    name: 'ConsultationDetails',
    params: {
      bookingId: selectedConversation.value.appointment,
    },
  });
}

function initials(name) {
  const parts = String(name || 'Patient')
    .trim()
    .split(/\s+/)
    .filter(Boolean);

  return parts
    .slice(0, 2)
    .map((part) => part[0].toUpperCase())
    .join('');
}

function formatListTime(value) {
  if (!value) return '';

  const date = parseDate(value);
  if (!date) return '';

  const today = new Date();
  const sameDay = date.toDateString() === today.toDateString();

  return sameDay ? date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : date.toLocaleDateString([], { day: '2-digit', month: 'short' });
}

function formatMessageTime(value) {
  if (!value) return '';

  const date = parseDate(value);
  if (!date) return '';

  return date.toLocaleString([], {
    day: '2-digit',
    month: 'short',
    hour: '2-digit',
    minute: '2-digit',
  });
}

function parseDate(value) {
  if (!value) return null;

  const normalized = String(value).replace(' ', 'T');
  const date = new Date(normalized);

  return Number.isNaN(date.getTime()) ? null : date;
}

function getFileUrl(fileUrl) {
  return fileUrl || '#';
}

function getAttachmentName(fileUrl) {
  if (!fileUrl) return 'Attachment';

  const cleanUrl = String(fileUrl).split('?')[0];
  return cleanUrl.split('/').pop() || 'Attachment';
}

async function scrollToBottom() {
  await nextTick();

  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight;
  }
}

watch(selectedAppointmentId, () => {
  sendError.value = '';
});

onMounted(loadConversations);
</script>
