import { defineConfig } from 'wxt';

export default defineConfig({
  manifest: {
    name: 'PhishGuard',
    description: 'Real-time phishing detection powered by AI',
    version: '1.0.0',
    permissions: [
      'activeTab',
      'storage',
      'tabs',
      'webNavigation',
      'notifications'
    ],
    host_permissions: [
      '<all_urls>'
    ],
    action: {
      default_title: 'PhishGuard',
      default_icon: {
        '16': 'icon/16.png',
        '32': 'icon/32.png',
        '48': 'icon/48.png',
        '128': 'icon/128.png'
      }
    },
    icons: {
      '16': 'icon/16.png',
      '32': 'icon/32.png',
      '48': 'icon/48.png',
      '128': 'icon/128.png'
    },
    content_security_policy: {
      extension_pages: "script-src 'self'; object-src 'self'"
    }
  },
  runner: {
    disabled: false,
    chromiumArgs: ['--disable-extensions-except=.output/chrome-mv3', '--load-extension=.output/chrome-mv3']
  }
});
