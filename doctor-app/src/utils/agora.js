import AgoraRTC from 'agora-rtc-sdk-ng';

export const AGORA_APP_ID = 'ecf9c8b7c88243f6bb988fafdf3dda44';

export class AgoraService {
  constructor() {
    this.client = AgoraRTC.createClient({ mode: 'rtc', codec: 'vp8' });
    this.localAudioTrack = null;
    this.localVideoTrack = null;
    this.screenTrack = null;
    this.isScreenSharing = false;
  }

  async join({ appId, channelName, token = null, uid = 2001, onUserPublished, onUserUnpublished }) {
    this.client.on('user-published', onUserPublished);
    this.client.on('user-unpublished', onUserUnpublished);

    // Join the channel
    const actualAppId = appId || AGORA_APP_ID;
    await this.client.join(actualAppId, channelName, token, uid);

    // Create local audio and video tracks
    const [audioTrack, videoTrack] = await AgoraRTC.createMicrophoneAndCameraTracks(
      {},
      { encoderConfig: '720p_1' }
    );
    this.localAudioTrack = audioTrack;
    this.localVideoTrack = videoTrack;

    // Publish local tracks
    await this.client.publish([this.localAudioTrack, this.localVideoTrack]);

    return {
      localAudioTrack: this.localAudioTrack,
      localVideoTrack: this.localVideoTrack,
    };
  }

  async toggleAudio(enabled) {
    if (this.localAudioTrack) {
      await this.localAudioTrack.setEnabled(enabled);
      return enabled;
    }
    return false;
  }

  async toggleVideo(enabled) {
    if (this.localVideoTrack) {
      await this.localVideoTrack.setEnabled(enabled);
      return enabled;
    }
    return false;
  }

  async startScreenShare() {
    if (this.isScreenSharing) return;
    this.screenTrack = await AgoraRTC.createScreenVideoTrack({}, 'disable');
    if (this.localVideoTrack) {
      await this.client.unpublish(this.localVideoTrack);
    }
    await this.client.publish(this.screenTrack);
    this.isScreenSharing = true;

    this.screenTrack.on('track-ended', async () => {
      await this.stopScreenShare();
    });

    return this.screenTrack;
  }

  async stopScreenShare() {
    if (!this.isScreenSharing) return;
    if (this.screenTrack) {
      await this.client.unpublish(this.screenTrack);
      this.screenTrack.close();
      this.screenTrack = null;
    }
    if (this.localVideoTrack) {
      await this.client.publish(this.localVideoTrack);
    }
    this.isScreenSharing = false;
  }

  async leave() {
    if (this.localAudioTrack) {
      this.localAudioTrack.stop();
      this.localAudioTrack.close();
      this.localAudioTrack = null;
    }
    if (this.localVideoTrack) {
      this.localVideoTrack.stop();
      this.localVideoTrack.close();
      this.localVideoTrack = null;
    }
    if (this.screenTrack) {
      this.screenTrack.stop();
      this.screenTrack.close();
      this.screenTrack = null;
    }
    await this.client.leave();
  }
}
