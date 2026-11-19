<template>
  <div class="flex h-[calc(100vh-112px)] min-h-[600px] flex-col overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">

    <!-- Page heading -->
    <header class="flex shrink-0 items-center justify-between gap-4 border-b border-slate-200 bg-white px-5 py-4 sm:px-7">
      <div class="min-w-0">
        <div class="flex items-center gap-2">
          <div class="flex h-9 w-9 items-center justify-center rounded-xl bg-teal-50">
            <FeatherIcon name="message-square" class="h-4 w-4 text-teal-700" />
          </div>
          <div>
            <h1 class="text-lg font-bold tracking-tight text-slate-900 sm:text-xl">Messages</h1>
            <p class="mt-0.5 text-xs text-slate-500 sm:text-sm">Patient communication centre</p>
          </div>
        </div>
      </div>

      <button
        type="button"
        class="inline-flex h-10 shrink-0 items-center gap-2 rounded-xl border border-slate-200 bg-white px-3 text-sm font-semibold text-slate-600 shadow-sm transition hover:border-teal-200 hover:bg-teal-50 hover:text-teal-700 disabled:cursor-not-allowed disabled:opacity-50"
        :disabled="listLoading"
        @click="loadConversations"
      >
        <FeatherIcon name="refresh-cw" class="h-4 w-4" :class="{ 'animate-spin': listLoading }" />
        <span class="hidden sm:inline">Refresh</span>
      </button>
    </header>

    <!-- Main workspace -->
    <div class="grid min-h-0 flex-1 grid-cols-1 grid-rows-[minmax(150px,32%)_minmax(0,1fr)] md:grid-cols-[310px_minmax(0,1fr)] md:grid-rows-1 lg:grid-cols-[340px_minmax(0,1fr)]">

      <!-- Conversation sidebar -->
      <aside class="flex min-h-0 flex-col border-b border-slate-200 bg-white md:border-b-0 md:border-r">

        <!-- Search and list heading -->
        <div class="shrink-0 border-b border-slate-100 p-4 sm:p-5">
          <div class="mb-3 flex items-center justify-between">
            <div>
              <h2 class="text-sm font-bold text-slate-800">Your conversations</h2>
              <p class="mt-0.5 text-xs text-slate-400">Stay connected with your patients</p>
            </div>

            <span class="inline-flex h-7 min-w-7 items-center justify-center rounded-lg bg-teal-50 px-2 text-xs font-bold text-teal-700">
              {{ filteredConversations.length }}
            </span>
          </div>

          <label class="relative block">
            <FeatherIcon name="search" class="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
            <input
              v-model="searchQuery"
              type="search"
              placeholder="Search patients..."
              aria-label="Search conversations"
              class="h-10 w-full rounded-xl border border-slate-200 bg-slate-50 pl-9 pr-3 text-sm text-slate-800 outline-none transition placeholder:text-slate-400 hover:border-slate-300 focus:border-teal-500 focus:bg-white focus:ring-2 focus:ring-teal-100"
            />
          </label>
        </div>

        <!-- Conversation list -->
        <div class="min-h-0 flex-1 overflow-y-auto">

          <div v-if="listLoading && conversations.length === 0" class="flex h-full min-h-32 flex-col items-center justify-center gap-3 p-6 text-center">
            <div class="flex h-9 w-9 items-center justify-center rounded-full bg-teal-50">
              <FeatherIcon name="loader" class="h-5 w-5 animate-spin text-teal-600" />
            </div>
            <p class="text-sm text-slate-500">Loading conversations...</p>
          </div>

          <div v-else-if="listError" class="m-4 rounded-xl border border-red-100 bg-red-50 p-4">
            <div class="flex items-center gap-2 text-sm font-semibold text-red-700">
              <FeatherIcon name="alert-circle" class="h-4 w-4" />
              Unable to load conversations
            </div>
            <p class="mt-1 text-xs leading-5 text-red-600">{{ listError }}</p>
            <button type="button" class="mt-3 text-xs font-bold text-red-700 underline underline-offset-2" @click="loadConversations">
              Try again
            </button>
          </div>

          <div v-else-if="filteredConversations.length === 0" class="flex h-full min-h-36 flex-col items-center justify-center px-5 py-8 text-center">
            <div class="flex h-12 w-12 items-center justify-center rounded-2xl bg-slate-100">
              <FeatherIcon name="message-circle" class="h-5 w-5 text-slate-400" />
            </div>
            <p class="mt-3 text-sm font-semibold text-slate-700">
              {{ searchQuery ? 'No matching patients' : 'No conversations yet' }}
            </p>
            <p class="mt-1 max-w-[220px] text-xs leading-5 text-slate-400">
              {{ searchQuery ? 'Try searching with another patient name.' : 'Patient conversations will appear here.' }}
            </p>
          </div>

          <button
            v-for="conversation in filteredConversations"
            :key="conversation.patient"
            type="button"
            class="group relative flex w-full items-start gap-3 border-b border-slate-100 px-4 py-4 text-left transition duration-150 hover:bg-slate-50 sm:px-5"
            :class="{
              'bg-teal-50/80 hover:bg-teal-50': selectedPatientId === conversation.patient,
            }"
            @click="selectConversation(conversation)"
          >
            <!-- Active conversation indicator -->
            <span
              v-if="selectedPatientId === conversation.patient"
              class="absolute bottom-3 left-0 top-3 w-[3px] rounded-r-full bg-teal-600"
            ></span>

            <!-- Patient avatar -->
            <div
              class="flex h-11 w-11 shrink-0 items-center justify-center rounded-2xl text-sm font-bold transition"
              :class="selectedPatientId === conversation.patient ? 'bg-teal-600 text-white shadow-sm' : 'bg-slate-100 text-slate-600 group-hover:bg-teal-100 group-hover:text-teal-800'"
            >
              {{ initials(conversation.patient_name) }}
            </div>

            <!-- Conversation preview -->
            <div class="min-w-0 flex-1">
              <div class="flex items-start justify-between gap-2">
                <p class="truncate text-sm font-semibold text-slate-800">
                  {{ conversation.patient_name || conversation.patient }}
                </p>
                <span class="shrink-0 pt-0.5 text-[10px] font-medium text-slate-400">
                  {{ formatListTime(conversation.latest_message_at || conversation.scheduled_time) }}
                </span>
              </div>

              <p class="mt-1 truncate text-xs leading-5 text-slate-500">
                {{ conversation.latest_message || 'No messages yet' }}
              </p>

              <div class="mt-2 flex items-center justify-between">
                <span class="text-[10px] font-medium text-slate-400">Patient conversation</span>

                <span
                  v-if="Number(conversation.unread_count) > 0"
                  class="inline-flex h-5 min-w-5 items-center justify-center rounded-full bg-teal-600 px-1.5 text-[10px] font-bold text-white shadow-sm"
                >
                  {{ conversation.unread_count }}
                </span>
              </div>
            </div>
          </button>
        </div>
      </aside>

      <!-- Conversation panel -->
      <section class="flex min-h-0 min-w-0 flex-col bg-slate-50/70">

        <template v-if="selectedConversation">

          <!-- Selected patient header -->
          <header class="z-10 flex shrink-0 items-center justify-between gap-3 border-b border-slate-200 bg-white px-4 py-3.5 sm:px-6 sm:py-4">
            <div class="flex min-w-0 items-center gap-3">
              <div class="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-teal-100 text-sm font-bold text-teal-800">
                {{ initials(selectedConversation.patient_name) }}
              </div>

              <div class="min-w-0">
                <h2 class="truncate text-sm font-bold text-slate-900 sm:text-base">
                  {{ selectedConversation.patient_name || selectedConversation.patient }}
                </h2>
                <p class="mt-0.5 truncate text-[11px] text-slate-500 sm:text-xs">
                  Consultation {{ selectedConversation.appointment }}
                </p>
              </div>
            </div>

            <div class="flex shrink-0 items-center gap-2">
              <span class="hidden items-center gap-1.5 rounded-full border border-emerald-100 bg-emerald-50 px-2.5 py-1 text-[10px] font-semibold text-emerald-700 sm:inline-flex">
                <span class="h-1.5 w-1.5 rounded-full bg-emerald-500"></span>
                Conversation
              </span>
            </div>
          </header>

          <!-- Information banner -->
          <div class="flex shrink-0 items-start gap-2.5 border-b border-teal-100 bg-teal-50/70 px-4 py-3 sm:px-6">
            <FeatherIcon name="info" class="mt-0.5 h-4 w-4 shrink-0 text-teal-700" />
            <p class="text-[11px] leading-5 text-teal-900 sm:text-xs">
              Messages exchanged with this patient are displayed below. You can continue the conversation here.
            </p>
          </div>

          <!-- Message history -->
          <div ref="messagesContainer" class="min-h-0 flex-1 overflow-y-auto bg-[#f5f7fa] px-3 py-5 sm:px-6 sm:py-6">

            <div v-if="messagesLoading" class="flex h-full min-h-40 flex-col items-center justify-center gap-3">
              <div class="flex h-10 w-10 items-center justify-center rounded-full bg-white shadow-sm">
                <FeatherIcon name="loader" class="h-5 w-5 animate-spin text-teal-600" />
              </div>
              <p class="text-xs font-medium text-slate-500">Loading message history...</p>
            </div>

            <div v-else-if="messagesError" class="flex h-full min-h-40 flex-col items-center justify-center gap-3 text-center">
              <div class="flex h-11 w-11 items-center justify-center rounded-xl bg-red-50">
                <FeatherIcon name="alert-circle" class="h-5 w-5 text-red-500" />
              </div>
              <p class="max-w-md text-sm text-red-600">{{ messagesError }}</p>
              <button
                type="button"
                class="rounded-lg border border-slate-200 bg-white px-4 py-2 text-xs font-semibold text-slate-700 shadow-sm transition hover:bg-slate-50"
                @click="loadMessages"
              >
                Try again
              </button>
            </div>

            <div v-else-if="messages.length === 0" class="flex h-full min-h-40 flex-col items-center justify-center text-center">
              <div class="flex h-14 w-14 items-center justify-center rounded-2xl bg-white shadow-sm ring-1 ring-slate-100">
                <FeatherIcon name="messages-square" class="h-6 w-6 text-slate-400" />
              </div>
              <p class="mt-4 text-sm font-semibold text-slate-700">Start a conversation</p>
              <p class="mt-1 max-w-xs text-xs leading-5 text-slate-400">
                There are no messages in this conversation yet. Send a message to get started.
              </p>
            </div>

            <div v-else class="mx-auto flex w-full max-w-4xl flex-col gap-5">

              <div
                v-for="item in messages"
                :key="item.name"
                class="flex w-full"
                :class="item.sender_type === 'Doctor' ? 'justify-end' : 'justify-start'"
              >
                <div class="flex max-w-[90%] items-end gap-2 sm:max-w-[75%]">

                  <div
                    v-if="item.sender_type !== 'Doctor'"
                    class="mb-5 hidden h-7 w-7 shrink-0 items-center justify-center rounded-lg bg-white text-[10px] font-bold text-slate-600 shadow-sm ring-1 ring-slate-100 sm:flex"
                  >
                    {{ initials(selectedConversation.patient_name) }}
                  </div>

                  <div class="min-w-0">
                    <!-- Message bubble -->
                    <div
                      class="rounded-2xl px-4 py-3 shadow-sm"
                      :class="item.sender_type === 'Doctor'
                        ? 'rounded-br-md border border-teal-700 bg-teal-700 text-white'
                        : 'rounded-bl-md border border-slate-200 bg-white text-slate-800'"
                    >
                      <p
                        v-if="item.message"
                        class="whitespace-pre-wrap break-words text-[13px] leading-6 sm:text-sm"
                        :class="item.sender_type === 'Doctor' ? 'text-white' : 'text-slate-700'"
                      >
                        {{ item.message }}
                      </p>

                      <!-- Attachment -->
                      <a
                        v-if="item.attachment"
                        :href="getFileUrl(item.attachment)"
                        target="_blank"
                        rel="noopener noreferrer"
                        class="mt-2 flex min-w-0 items-center gap-2 rounded-lg px-2.5 py-2 text-xs font-medium transition hover:opacity-80"
                        :class="item.sender_type === 'Doctor' ? 'bg-white/10 text-white' : 'bg-slate-50 text-teal-700'"
                      >
                        <FeatherIcon name="paperclip" class="h-4 w-4 shrink-0" />
                        <span class="break-all">{{ getAttachmentName(item.attachment) }}</span>
                        <FeatherIcon name="external-link" class="ml-auto h-3 w-3 shrink-0" />
                      </a>
                    </div>

                    <!-- Sender and timestamp -->
                    <div
                      class="mt-1.5 flex items-center gap-1.5 px-1 text-[10px] text-slate-400 sm:text-[11px]"
                      :class="item.sender_type === 'Doctor' ? 'justify-end' : 'justify-start'"
                    >
                      <span class="font-semibold" :class="item.sender_type === 'Doctor' ? 'text-teal-700' : 'text-slate-500'">
                        {{ item.sender_type === 'Doctor' ? 'You' : 'Patient' }}
                      </span>
                      <span v-if="item.sent_at">· {{ formatMessageTime(item.sent_at) }}</span>
                    </div>
                  </div>

                  <div
                    v-if="item.sender_type === 'Doctor'"
                    class="mb-5 hidden h-7 w-7 shrink-0 items-center justify-center rounded-lg bg-teal-100 text-[10px] font-bold text-teal-800 sm:flex"
                  >
                    You
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Message composer -->
          <div class="shrink-0 border-t border-slate-200 bg-white px-3 py-3 sm:px-6 sm:py-4">

            <!-- Send error -->
            <div v-if="sendError" class="mb-3 flex items-start gap-2 rounded-xl border border-red-100 bg-red-50 px-3 py-2.5 text-xs text-red-700">
              <FeatherIcon name="alert-circle" class="mt-0.5 h-4 w-4 shrink-0" />
              <span>{{ sendError }}</span>
            </div>

            <!-- Selected attachment -->
            <div v-if="selectedFile" class="mb-3 flex items-center justify-between gap-3 rounded-xl border border-teal-100 bg-teal-50/60 px-3 py-2.5">
              <div class="flex min-w-0 items-center gap-2.5">
                <div class="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-white text-teal-700">
                  <FeatherIcon name="file" class="h-4 w-4" />
                </div>
                <div class="min-w-0">
                  <p class="truncate text-xs font-semibold text-slate-700">{{ selectedFile.name }}</p>
                  <p class="text-[10px] text-slate-400">Attachment ready to send</p>
                </div>
              </div>

              <button
                type="button"
                class="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg text-slate-400 transition hover:bg-red-50 hover:text-red-600 disabled:opacity-50"
                title="Remove attachment"
                aria-label="Remove attachment"
                :disabled="sending"
                @click="removeSelectedFile"
              >
                <FeatherIcon name="x" class="h-4 w-4" />
              </button>
            </div>

            <form class="mx-auto flex w-full max-w-4xl items-end gap-2 sm:gap-3" @submit.prevent="sendMessage">

              <input
                ref="fileInput"
                type="file"
                class="hidden"
                @change="handleFileChange"
              />

              <!-- Attach file -->
              <button
                type="button"
                title="Attach file"
                aria-label="Attach file"
                class="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl border border-slate-200 bg-white text-slate-500 transition hover:border-teal-200 hover:bg-teal-50 hover:text-teal-700 disabled:cursor-not-allowed disabled:opacity-50"
                :disabled="sending"
                @click="fileInput?.click()"
              >
                <FeatherIcon name="paperclip" class="h-5 w-5" />
              </button>

              <!-- Message input -->
              <div class="min-w-0 flex-1">
                <textarea
                  v-model="newMessage"
                  rows="1"
                  placeholder="Write a message..."
                  aria-label="Write a message"
                  class="max-h-32 min-h-11 w-full resize-y rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-800 outline-none transition placeholder:text-slate-400 hover:border-slate-300 focus:border-teal-500 focus:bg-white focus:ring-2 focus:ring-teal-100 disabled:bg-slate-100"
                  :disabled="sending"
                  @keydown.enter.exact.prevent="sendMessage"
                ></textarea>
              </div>

              <!-- Send -->
              <button
                type="submit"
                class="flex h-11 shrink-0 items-center justify-center gap-2 rounded-xl bg-teal-700 px-3.5 text-sm font-semibold text-white shadow-sm transition hover:bg-teal-800 hover:shadow-md focus:outline-none focus:ring-2 focus:ring-teal-500 focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 sm:px-5"
                :disabled="sending || (!newMessage.trim() && !selectedFile)"
              >
                <FeatherIcon v-if="!sending" name="send" class="h-4 w-4" />
                <span v-else class="h-4 w-4 animate-spin rounded-full border-2 border-white/40 border-t-white"></span>
                <span class="hidden sm:inline">{{ sending ? 'Sending' : 'Send' }}</span>
              </button>
            </form>

            <p class="mx-auto mt-2 hidden max-w-4xl text-[10px] text-slate-400 sm:block">
              Press Enter to send · Attach files using the paperclip
            </p>
          </div>
        </template>

        <!-- No conversation selected -->
        <div v-else class="flex min-h-0 flex-1 flex-col items-center justify-center px-6 py-10 text-center">
          <div class="relative flex h-20 w-20 items-center justify-center rounded-3xl bg-teal-50 ring-1 ring-teal-100">
            <FeatherIcon name="messages-square" class="h-9 w-9 text-teal-700" />
            <span class="absolute -right-1 -top-1 flex h-6 w-6 items-center justify-center rounded-full border-2 border-white bg-emerald-500">
              <FeatherIcon name="check" class="h-3 w-3 text-white" />
            </span>
          </div>

          <h2 class="mt-6 text-lg font-bold tracking-tight text-slate-900">
            Your patient conversations
          </h2>

          <p class="mt-2 max-w-sm text-sm leading-6 text-slate-500">
            Select a patient from your conversation list to view previous messages and continue communicating.
          </p>

          <div class="mt-6 flex items-center gap-2 rounded-full border border-slate-200 bg-white px-4 py-2 text-xs font-medium text-slate-500 shadow-sm">
            <FeatherIcon name="shield-check" class="h-4 w-4 text-teal-600" />
            Patient communication workspace
          </div>
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
const selectedPatientId = ref('');
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

    conversations.value = Array.isArray(result.conversations)
      ? result.conversations
      : [];

    if (selectedPatientId.value) {
      const updated = conversations.value.find(
        (item) => item.patient === selectedPatientId.value,
      );

      if (updated) {
        selectedConversation.value = updated;
      } else {
        selectedConversation.value = null;
        selectedPatientId.value = '';
        messages.value = [];
      }
    }

    const patientId = route.query.patient;
    const appointmentId = route.query.appointment;

    if (patientId || appointmentId) {
      
      const matchingConversation = patientId
        ? conversations.value.find((item) => item.patient === patientId)
        : conversations.value.find(
            (item) => item.appointment === appointmentId,
          );

      if (matchingConversation) {
        await selectConversation(matchingConversation);
      } else {
        selectedConversation.value = null;
        selectedPatientId.value = '';
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
  selectedPatientId.value = conversation.patient;

  messages.value = [];
  messagesError.value = '';
  sendError.value = '';
  newMessage.value = '';
  removeSelectedFile();

  await loadMessages();
}

async function loadMessages() {
  const patientId = selectedPatientId.value;

  if (!patientId) {
    messages.value = [];
    return;
  }

  messagesLoading.value = true;
  messagesError.value = '';

  try {
    const response = await chatResource.submit({
      patient: patientId,
    });

    if (selectedPatientId.value !== patientId) return;

    const result = response?.message || response || {};

    messages.value = Array.isArray(result.messages) ? result.messages : [];

    await markReadResource.submit({
      patient: patientId,
    });

    window.dispatchEvent(new Event('doctor-chat-read'));

    await scrollToBottom();

    const conversation = conversations.value.find(
      (item) => item.patient === patientId,
    );

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
  const conversation = selectedConversation.value;
  const appointmentId = conversation?.appointment;
  const patientId = selectedPatientId.value;

  if (!appointmentId || !patientId || sending.value || !conversation) return;

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

    if (selectedPatientId.value !== patientId) return;

    const result =
      response?.message?.message ||
      response?.message ||
      response?.data?.message ||
      response?.data ||
      response;

    if (result?.name) {
      messages.value.push({
        ...result,
        appointment: appointmentId,
      });
    } else {
      await loadMessages();
    }

    newMessage.value = '';
    removeSelectedFile();

    await scrollToBottom();

    await refreshConversationPreview(patientId);
  } catch (error) {
    console.error('Failed to send patient chat message:', error);
    sendError.value = error?.message || 'Failed to send message.';
  } finally {
    sending.value = false;
  }
}

async function refreshConversationPreview(patientId) {
  try {
    const response = await conversationsResource.submit({});
    const result = response?.message || response || {};

    if (Array.isArray(result.conversations)) {
      conversations.value = result.conversations;

      const updated = conversations.value.find(
        (item) => item.patient === patientId,
      );

      if (updated && selectedPatientId.value === patientId) {
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

watch(selectedPatientId, () => {
  sendError.value = '';
});

onMounted(loadConversations);
</script>
