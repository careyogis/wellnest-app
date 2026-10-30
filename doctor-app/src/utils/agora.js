import AgoraRTC from 'agora-rtc-sdk-ng';

// ---------------------------------------------------------------------------
// Module-level singleton — persists across Vue component mounts/unmounts so
// the doctor can navigate away (to review patient docs) and come back without
// dropping their RTC connection.  Only destroyed on an explicit End Call.
// ---------------------------------------------------------------------------
let _sharedInstance = null;

export function getAgoraService() {
  if (!_sharedInstance) {
    _sharedInstance = new AgoraService();
  }
  return _sharedInstance;
}

export function destroyAgoraService() {
  _sharedInstance = null;
}

export const AGORA_APP_ID = 'ecf9c8b7c88243f6bb988fafdf3dda44';

export class AgoraService {
  constructor() {
    this.client = AgoraRTC.createClient({ mode: 'rtc', codec: 'vp8' });
    this.localAudioTrack = null;
    this.localVideoTrack = null;
    this.screenTrack = null;
    this.isScreenSharing = false;
    this.isJoined = false;
    this.currentChannel = null;
    this.callStartedAt = null; // wall-clock ms when the patient first connected
    this.backgroundTimeoutId = null; // auto-leave timer while doctor is away
  }

  clearBackgroundTimeout() {
    if (this.backgroundTimeoutId) {
      clearTimeout(this.backgroundTimeoutId);
      this.backgroundTimeoutId = null;
    }
  }

  scheduleBackgroundTimeout(fn, ms = 5 * 60 * 1000) {
    this.clearBackgroundTimeout();
    this.backgroundTimeoutId = setTimeout(async () => {
      this.backgroundTimeoutId = null;
      await fn();
    }, ms);
  }

  _cleanupListeners() {
    if (this.client) {
      this.client.removeAllListeners('user-published');
      this.client.removeAllListeners('user-unpublished');
      this.client.removeAllListeners('user-left');
    }
  }

  async join({ appId, channelName, token = null, uid = 2001, onUserPublished, onUserUnpublished, onUserLeft }) {
    if (this.isJoined) {
      if (this.currentChannel && this.currentChannel !== channelName) {
        // Different channel! Teardown previous consultation before joining new one.
        await this.leave();
      } else {
        // Resuming the same consultation channel.
        // Clean up old listeners to prevent leak/accumulation
        this._cleanupListeners();
        this.client.on('user-published', onUserPublished);
        this.client.on('user-unpublished', onUserUnpublished);
        if (onUserLeft) this.client.on('user-left', onUserLeft);

        return {
          localAudioTrack: this.localAudioTrack,
          localVideoTrack: this.localVideoTrack,
        };
      }
    }

    // Fresh join: clear old listeners and set new ones
    this._cleanupListeners();
    this.client.on('user-published', onUserPublished);
    this.client.on('user-unpublished', onUserUnpublished);
    if (onUserLeft) this.client.on('user-left', onUserLeft);

    try {
      // Join the channel
      const actualAppId = appId || AGORA_APP_ID;
      await this.client.join(actualAppId, channelName, token, uid);
      this.currentChannel = channelName;

      // Create local audio and video tracks
      const [audioTrack, videoTrack] = await AgoraRTC.createMicrophoneAndCameraTracks(
        {},
        { encoderConfig: '720p_1' }
      );
      this.localAudioTrack = audioTrack;
      this.localVideoTrack = videoTrack;

      // Publish local tracks
      await this.client.publish([this.localAudioTrack, this.localVideoTrack]);

      this.isJoined = true;

      return {
        localAudioTrack: this.localAudioTrack,
        localVideoTrack: this.localVideoTrack,
      };
    } catch (error) {
      await this.leave();
      throw error;
    }
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
    if (this.isScreenSharing) return this.screenTrack;
    try {
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
    } catch (error) {
      if (this.screenTrack) {
        this.screenTrack.stop();
        this.screenTrack.close();
        this.screenTrack = null;
      }
      if (this.localVideoTrack && this.isJoined) {
        try {
          await this.client.publish(this.localVideoTrack);
        } catch (_) {}
      }
      this.isScreenSharing = false;
      throw error;
    }
  }

  async stopScreenShare() {
    if (!this.isScreenSharing && !this.screenTrack) return;
    if (this.screenTrack) {
      try {
        this.screenTrack.removeAllListeners();
        await this.client.unpublish(this.screenTrack);
      } catch (e) {
        console.warn('Error unpublishing screen track:', e);
      }
      this.screenTrack.stop();
      this.screenTrack.close();
      this.screenTrack = null;
    }
    this.isScreenSharing = false;
    if (this.localVideoTrack && this.isJoined) {
      try {
        await this.client.publish(this.localVideoTrack);
      } catch (e) {
        console.warn('Error republishing local video track:', e);
      }
    }
  }

  async leave() {
    this.clearBackgroundTimeout();

    if (this.screenTrack) {
      try {
        this.screenTrack.removeAllListeners();
        await this.client.unpublish(this.screenTrack);
      } catch (e) {
        console.warn('Error unpublishing screen track on leave:', e);
      }
      this.screenTrack.stop();
      this.screenTrack.close();
      this.screenTrack = null;
    }
    this.isScreenSharing = false;

    if (this.localAudioTrack) {
      try {
        await this.client.unpublish(this.localAudioTrack);
      } catch (e) {
        console.warn('Error unpublishing audio track on leave:', e);
      }
      this.localAudioTrack.stop();
      this.localAudioTrack.close();
      this.localAudioTrack = null;
    }

    if (this.localVideoTrack) {
      try {
        await this.client.unpublish(this.localVideoTrack);
      } catch (e) {
        console.warn('Error unpublishing video track on leave:', e);
      }
      this.localVideoTrack.stop();
      this.localVideoTrack.close();
      this.localVideoTrack = null;
    }

    this._cleanupListeners();
    try {
      this.client.removeAllListeners();
      await this.client.leave();
    } catch (e) {
      console.warn('Error leaving Agora client:', e);
    }

    this.isJoined = false;
    this.currentChannel = null;
    this.callStartedAt = null;
    destroyAgoraService();
  }
}
