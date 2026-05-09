import { browser } from 'wxt/browser';

const API_BASE_URL = 'http://localhost:8000/api/v1';
const API_KEY = import.meta.env.VITE_EXTENSION_API_KEY || 'dev-api-key';

interface ScanResult {
  scan_id: string;
  url: string;
  is_phishing: boolean;
  phishing_score: number;
  confidence: number;
  explanation?: string;
  risk_factors?: any[];
  recommendation?: string;
  scan_duration_ms: number;
  threat_intel_summary: any;
  visual_similarity_summary: any;
}

interface ScanCache {
  [url: string]: {
    result: ScanResult;
    timestamp: number;
  };
}

const scanCache: ScanCache = {};
const CACHE_DURATION = 5 * 60 * 1000; // 5 minutes

export default defineBackground(() => {
  console.log('PhishGuard background script loaded');

  // Listen for tab updates (navigation)
  browser.tabs.onUpdated.addListener(async (tabId, changeInfo, tab) => {
    if (changeInfo.status === 'complete' && tab.url) {
      // Skip chrome:// and extension:// URLs
      if (tab.url.startsWith('chrome://') || tab.url.startsWith('chrome-extension://')) {
        return;
      }

      // Check if URL should be scanned
      if (shouldScanUrl(tab.url)) {
        await scanUrl(tab.url, tabId);
      }
    }
  });

  // Listen for messages from popup/content scripts
  browser.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.type === 'SCAN_URL') {
      scanUrl(message.url, message.tabId).then(sendResponse);
      return true; // Keep channel open for async response
    }

    if (message.type === 'GET_SCAN_RESULT') {
      const cached = getCachedScan(message.url);
      sendResponse(cached);
      return false;
    }

    if (message.type === 'SUBMIT_FEEDBACK') {
      submitFeedback(message.data).then(sendResponse);
      return true;
    }
  });
});

function shouldScanUrl(url: string): boolean {
  try {
    const urlObj = new URL(url);
    
    // Skip local/internal URLs
    if (urlObj.hostname === 'localhost' || urlObj.hostname === '127.0.0.1') {
      return false;
    }

    // Only scan http/https
    if (!['http:', 'https:'].includes(urlObj.protocol)) {
      return false;
    }

    return true;
  } catch {
    return false;
  }
}

async function scanUrl(url: string, tabId?: number): Promise<ScanResult | null> {
  try {
    // Check cache first
    const cached = getCachedScan(url);
    if (cached) {
      console.log('Using cached scan result for:', url);
      if (tabId !== undefined) {
        await updateBadge(tabId, cached);
        await injectWarning(tabId, cached);
      }
      return cached;
    }

    console.log('Scanning URL:', url);

    // Call API
    const response = await fetch(`${API_BASE_URL}/scan`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-API-Key': API_KEY
      },
      body: JSON.stringify({
        url: url,
        user_agent: navigator.userAgent
      })
    });

    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }

    const result: ScanResult = await response.json();

    // Cache result
    scanCache[url] = {
      result,
      timestamp: Date.now()
    };

    // Update badge and inject warning if needed
    if (tabId !== undefined) {
      await updateBadge(tabId, result);
      await injectWarning(tabId, result);
    }

    // Show notification for high-risk phishing
    if (result.is_phishing && result.phishing_score > 0.8) {
      browser.notifications.create({
        type: 'basic',
        iconUrl: '/icon/128.png',
        title: '🚨 PhishGuard Alert',
        message: `Warning: This site is likely a phishing attempt!\n\nScore: ${(result.phishing_score * 100).toFixed(0)}%`,
        priority: 2
      });
    }

    return result;
  } catch (error) {
    console.error('Error scanning URL:', error);
    return null;
  }
}

function getCachedScan(url: string): ScanResult | null {
  const cached = scanCache[url];
  if (cached && Date.now() - cached.timestamp < CACHE_DURATION) {
    return cached.result;
  }
  return null;
}

async function updateBadge(tabId: number, result: ScanResult) {
  try {
    if (result.is_phishing) {
      await browser.action.setBadgeText({ text: '⚠️', tabId });
      await browser.action.setBadgeBackgroundColor({ color: '#ef4444', tabId });
    } else {
      await browser.action.setBadgeText({ text: '✓', tabId });
      await browser.action.setBadgeBackgroundColor({ color: '#22c55e', tabId });
    }
  } catch (error) {
    console.error('Error updating badge:', error);
  }
}

async function injectWarning(tabId: number, result: ScanResult) {
  if (!result.is_phishing) return;

  try {
    await browser.scripting.executeScript({
      target: { tabId },
      func: (data) => {
        // Check if warning already exists
        if (document.getElementById('phishguard-warning')) return;

        // Create warning overlay
        const overlay = document.createElement('div');
        overlay.id = 'phishguard-warning';
        overlay.style.cssText = `
          position: fixed;
          top: 0;
          left: 0;
          right: 0;
          background: linear-gradient(135deg, #dc2626 0%, #991b1b 100%);
          color: white;
          padding: 16px;
          z-index: 999999;
          box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
          animation: slideDown 0.3s ease-out;
        `;

        overlay.innerHTML = `
          <style>
            @keyframes slideDown {
              from { transform: translateY(-100%); }
              to { transform: translateY(0); }
            }
          </style>
          <div style="max-width: 1200px; margin: 0 auto; display: flex; align-items: center; justify-content: space-between;">
            <div style="flex: 1;">
              <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 8px;">
                <span style="font-size: 24px;">🛡️</span>
                <h3 style="margin: 0; font-size: 18px; font-weight: 600;">PhishGuard Warning</h3>
              </div>
              <p style="margin: 0; font-size: 14px; opacity: 0.95;">
                ${data.explanation || 'This website has been identified as a potential phishing attempt.'}
              </p>
              <p style="margin: 8px 0 0 0; font-size: 13px; opacity: 0.9;">
                <strong>Risk Score:</strong> ${(data.phishing_score * 100).toFixed(0)}% | 
                <strong>Confidence:</strong> ${(data.confidence * 100).toFixed(0)}%
              </p>
            </div>
            <button id="phishguard-close" style="
              background: rgba(255, 255, 255, 0.2);
              border: 1px solid rgba(255, 255, 255, 0.3);
              color: white;
              padding: 8px 16px;
              border-radius: 6px;
              cursor: pointer;
              font-size: 14px;
              font-weight: 500;
              transition: background 0.2s;
            " onmouseover="this.style.background='rgba(255,255,255,0.3)'" 
               onmouseout="this.style.background='rgba(255,255,255,0.2)'">
              Dismiss
            </button>
          </div>
        `;

        document.body.insertBefore(overlay, document.body.firstChild);

        // Add close button handler
        document.getElementById('phishguard-close')?.addEventListener('click', () => {
          overlay.style.animation = 'slideDown 0.3s ease-out reverse';
          setTimeout(() => overlay.remove(), 300);
        });
      },
      args: [result]
    });
  } catch (error) {
    console.error('Error injecting warning:', error);
  }
}

async function submitFeedback(data: any): Promise<boolean> {
  try {
    const response = await fetch(`${API_BASE_URL}/feedback`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-API-Key': API_KEY
      },
      body: JSON.stringify(data)
    });

    return response.ok;
  } catch (error) {
    console.error('Error submitting feedback:', error);
    return false;
  }
}
