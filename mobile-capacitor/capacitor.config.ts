import type { CapacitorConfig } from '@capacitor/cli';

const config: CapacitorConfig = {
  appId: 'com.local.tradingresearch.mobile',
  appName: 'Trading Research Mobile',
  webDir: 'www',
  server: {
    androidScheme: 'https',
  },
};

export default config;
