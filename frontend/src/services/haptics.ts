/**
 * Haptic Feedback Service
 * Sprint 24: Provides native-like haptic feedback for mobile interactions
 */

export type HapticFeedbackType =
  | 'light'
  | 'medium'
  | 'heavy'
  | 'selection'
  | 'impact'
  | 'notification'
  | 'success'
  | 'warning'
  | 'error';

export interface HapticPattern {
  vibrate: number[];
  description: string;
}

class HapticsService {
  private isSupported: boolean;
  private patterns: Record<HapticFeedbackType, HapticPattern>;

  constructor() {
    this.isSupported = 'vibrate' in navigator;

    // Define haptic patterns for different feedback types
    this.patterns = {
      light: {
        vibrate: [50],
        description: 'Light tap feedback'
      },
      medium: {
        vibrate: [100],
        description: 'Medium intensity feedback'
      },
      heavy: {
        vibrate: [150],
        description: 'Heavy impact feedback'
      },
      selection: {
        vibrate: [25],
        description: 'Selection change feedback'
      },
      impact: {
        vibrate: [75, 50, 75],
        description: 'Impact feedback with rhythm'
      },
      notification: {
        vibrate: [200, 100, 200],
        description: 'Notification alert pattern'
      },
      success: {
        vibrate: [100, 50, 100, 50, 200],
        description: 'Success confirmation pattern'
      },
      warning: {
        vibrate: [150, 100, 150],
        description: 'Warning alert pattern'
      },
      error: {
        vibrate: [300, 100, 300],
        description: 'Error alert pattern'
      }
    };
  }

  /**
   * Check if haptic feedback is supported
   */
  isHapticsSupported(): boolean {
    return this.isSupported;
  }

  /**
   * Trigger haptic feedback
   */
  feedback(type: HapticFeedbackType): void {
    if (!this.isSupported) {
      return;
    }

    try {
      const pattern = this.patterns[type];
      if (pattern) {
        navigator.vibrate(pattern.vibrate);
      }
    } catch (error) {
      console.warn('Haptic feedback failed:', error);
    }
  }

  /**
   * Custom vibration pattern
   */
  customVibrate(pattern: number[]): void {
    if (!this.isSupported) {
      return;
    }

    try {
      navigator.vibrate(pattern);
    } catch (error) {
      console.warn('Custom vibration failed:', error);
    }
  }

  /**
   * Stop all vibrations
   */
  stop(): void {
    if (!this.isSupported) {
      return;
    }

    try {
      navigator.vibrate(0);
    } catch (error) {
      console.warn('Stop vibration failed:', error);
    }
  }

  /**
   * Button press feedback
   */
  buttonPress(): void {
    this.feedback('light');
  }

  /**
   * Toggle switch feedback
   */
  toggleSwitch(): void {
    this.feedback('medium');
  }

  /**
   * Slider/range input feedback
   */
  sliderChange(): void {
    this.feedback('selection');
  }

  /**
   * Swipe gesture feedback
   */
  swipeGesture(): void {
    this.feedback('light');
  }

  /**
   * Pull to refresh feedback
   */
  pullToRefresh(): void {
    this.customVibrate([100, 50, 50, 50, 100]);
  }

  /**
   * Long press feedback
   */
  longPress(): void {
    this.feedback('heavy');
  }

  /**
   * Navigation feedback
   */
  navigation(): void {
    this.feedback('selection');
  }

  /**
   * Card tap feedback
   */
  cardTap(): void {
    this.feedback('light');
  }

  /**
   * Form submission feedback
   */
  formSubmit(): void {
    this.feedback('success');
  }

  /**
   * Error/validation feedback
   */
  error(): void {
    this.feedback('error');
  }

  /**
   * Warning feedback
   */
  warning(): void {
    this.feedback('warning');
  }

  /**
   * Success feedback
   */
  success(): void {
    this.feedback('success');
  }

  /**
   * Notification feedback
   */
  notification(): void {
    this.feedback('notification');
  }

  /**
   * Photo capture feedback
   */
  photoCapture(): void {
    this.customVibrate([50, 30, 100]);
  }

  /**
   * Voice recording start feedback
   */
  voiceRecordStart(): void {
    this.customVibrate([100, 50, 100]);
  }

  /**
   * Voice recording stop feedback
   */
  voiceRecordStop(): void {
    this.customVibrate([150, 100, 150, 100, 200]);
  }

  /**
   * Deal stage change feedback
   */
  dealStageChange(): void {
    this.customVibrate([75, 50, 75, 50, 150]);
  }

  /**
   * Real-time message feedback
   */
  messageReceived(): void {
    this.customVibrate([50, 50, 100]);
  }

  /**
   * Typing indicator feedback
   */
  typing(): void {
    this.customVibrate([25]);
  }

  /**
   * Connection status feedback
   */
  connectionLost(): void {
    this.customVibrate([200, 100, 200, 100, 300]);
  }

  connectionRestored(): void {
    this.customVibrate([100, 50, 100, 50, 100, 50, 200]);
  }

  /**
   * Get available patterns
   */
  getAvailablePatterns(): Record<HapticFeedbackType, HapticPattern> {
    return { ...this.patterns };
  }

  /**
   * Test haptic pattern
   */
  testPattern(type: HapticFeedbackType): void {
    console.log(`Testing haptic pattern: ${type} - ${this.patterns[type].description}`);
    this.feedback(type);
  }
}

// Export singleton instance
export const hapticsService = new HapticsService();

// React hook for haptic feedback
export function useHaptics() {
  return {
    isSupported: hapticsService.isHapticsSupported.bind(hapticsService),
    feedback: hapticsService.feedback.bind(hapticsService),
    customVibrate: hapticsService.customVibrate.bind(hapticsService),
    stop: hapticsService.stop.bind(hapticsService),

    // Convenience methods
    buttonPress: hapticsService.buttonPress.bind(hapticsService),
    toggleSwitch: hapticsService.toggleSwitch.bind(hapticsService),
    sliderChange: hapticsService.sliderChange.bind(hapticsService),
    swipeGesture: hapticsService.swipeGesture.bind(hapticsService),
    pullToRefresh: hapticsService.pullToRefresh.bind(hapticsService),
    longPress: hapticsService.longPress.bind(hapticsService),
    navigation: hapticsService.navigation.bind(hapticsService),
    cardTap: hapticsService.cardTap.bind(hapticsService),
    formSubmit: hapticsService.formSubmit.bind(hapticsService),
    error: hapticsService.error.bind(hapticsService),
    warning: hapticsService.warning.bind(hapticsService),
    success: hapticsService.success.bind(hapticsService),
    notification: hapticsService.notification.bind(hapticsService),
    photoCapture: hapticsService.photoCapture.bind(hapticsService),
    voiceRecordStart: hapticsService.voiceRecordStart.bind(hapticsService),
    voiceRecordStop: hapticsService.voiceRecordStop.bind(hapticsService),
    dealStageChange: hapticsService.dealStageChange.bind(hapticsService),
    messageReceived: hapticsService.messageReceived.bind(hapticsService),
    typing: hapticsService.typing.bind(hapticsService),
    connectionLost: hapticsService.connectionLost.bind(hapticsService),
    connectionRestored: hapticsService.connectionRestored.bind(hapticsService),

    // Utility methods
    getAvailablePatterns: hapticsService.getAvailablePatterns.bind(hapticsService),
    testPattern: hapticsService.testPattern.bind(hapticsService),
  };
}

export default hapticsService;