import { useState, useEffect } from 'react';
import { Shield, AlertTriangle, CheckCircle, Clock, TrendingUp, Send } from 'lucide-react';
import { browser } from 'wxt/browser';

interface ScanResult {
  scan_id: string;
  url: string;
  is_phishing: boolean;
  phishing_score: number;
  confidence: number;
  explanation?: string;
  risk_factors?: RiskFactor[];
  recommendation?: string;
  scan_duration_ms: number;
}

interface RiskFactor {
  category: string;
  risk: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  description: string;
}

export default function App() {
  const [currentUrl, setCurrentUrl] = useState<string>('');
  const [scanResult, setScanResult] = useState<ScanResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<'scan' | 'history'>('scan');

  useEffect(() => {
    // Get current tab URL
    browser.tabs.query({ active: true, currentWindow: true }).then(tabs => {
      if (tabs[0]?.url) {
        setCurrentUrl(tabs[0].url);
        checkExistingScan(tabs[0].url);
      }
    });
  }, []);

  const checkExistingScan = async (url: string) => {
    const result = await browser.runtime.sendMessage({
      type: 'GET_SCAN_RESULT',
      url
    });
    if (result) {
      setScanResult(result);
    }
  };

  const handleScan = async () => {
    setLoading(true);
    try {
      const tabs = await browser.tabs.query({ active: true, currentWindow: true });
      const result = await browser.runtime.sendMessage({
        type: 'SCAN_URL',
        url: currentUrl,
        tabId: tabs[0]?.id
      });
      setScanResult(result);
    } catch (error) {
      console.error('Scan error:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleFeedback = async (isCorrect: boolean) => {
    if (!scanResult) return;

    const success = await browser.runtime.sendMessage({
      type: 'SUBMIT_FEEDBACK',
      data: {
        scan_id: scanResult.scan_id,
        is_correct: isCorrect,
        actual_label: isCorrect 
          ? (scanResult.is_phishing ? 'phishing' : 'safe')
          : (scanResult.is_phishing ? 'safe' : 'phishing')
      }
    });

    if (success) {
      alert('Thank you for your feedback!');
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'text-red-600 bg-red-50';
      case 'high': return 'text-orange-600 bg-orange-50';
      case 'medium': return 'text-yellow-600 bg-yellow-50';
      case 'low': return 'text-blue-600 bg-blue-50';
      default: return 'text-gray-600 bg-gray-50';
    }
  };

  return (
    <div className="w-[400px] h-[600px] bg-gradient-to-br from-slate-50 to-slate-100">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-blue-700 text-white p-4 shadow-lg">
        <div className="flex items-center gap-3">
          <Shield className="w-8 h-8" />
          <div>
            <h1 className="text-xl font-bold">PhishGuard</h1>
            <p className="text-xs text-blue-100">Real-time Phishing Detection</p>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-gray-200 bg-white">
        <button
          onClick={() => setActiveTab('scan')}
          className={`flex-1 py-3 text-sm font-medium transition-colors ${
            activeTab === 'scan'
              ? 'text-blue-600 border-b-2 border-blue-600'
              : 'text-gray-500 hover:text-gray-700'
          }`}
        >
          Current Page
        </button>
        <button
          onClick={() => setActiveTab('history')}
          className={`flex-1 py-3 text-sm font-medium transition-colors ${
            activeTab === 'history'
              ? 'text-blue-600 border-b-2 border-blue-600'
              : 'text-gray-500 hover:text-gray-700'
          }`}
        >
          History
        </button>
      </div>

      {/* Content */}
      <div className="p-4 overflow-y-auto h-[calc(600px-140px)]">
        {activeTab === 'scan' && (
          <div className="space-y-4">
            {/* URL Display */}
            <div className="bg-white rounded-lg p-3 shadow-sm border border-gray-200">
              <p className="text-xs text-gray-500 mb-1">Current URL</p>
              <p className="text-sm text-gray-800 truncate font-mono">{currentUrl}</p>
            </div>

            {/* Scan Button */}
            {!scanResult && (
              <button
                onClick={handleScan}
                disabled={loading}
                className="w-full bg-blue-600 hover:bg-blue-700 text-white py-3 rounded-lg font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
              >
                {loading ? (
                  <>
                    <div className="animate-spin rounded-full h-5 w-5 border-2 border-white border-t-transparent" />
                    Scanning...
                  </>
                ) : (
                  <>
                    <Shield className="w-5 h-5" />
                    Scan This Page
                  </>
                )}
              </button>
            )}

            {/* Scan Result */}
            {scanResult && (
              <div className="space-y-4">
                {/* Status Card */}
                <div className={`rounded-lg p-4 shadow-md ${
                  scanResult.is_phishing
                    ? 'bg-gradient-to-br from-red-50 to-red-100 border-2 border-red-300'
                    : 'bg-gradient-to-br from-green-50 to-green-100 border-2 border-green-300'
                }`}>
                  <div className="flex items-start gap-3">
                    {scanResult.is_phishing ? (
                      <AlertTriangle className="w-8 h-8 text-red-600 flex-shrink-0" />
                    ) : (
                      <CheckCircle className="w-8 h-8 text-green-600 flex-shrink-0" />
                    )}
                    <div className="flex-1">
                      <h3 className={`font-bold text-lg mb-1 ${
                        scanResult.is_phishing ? 'text-red-800' : 'text-green-800'
                      }`}>
                        {scanResult.is_phishing ? '⚠️ Phishing Detected' : '✅ Safe Website'}
                      </h3>
                      <p className={`text-sm ${
                        scanResult.is_phishing ? 'text-red-700' : 'text-green-700'
                      }`}>
                        {scanResult.recommendation}
                      </p>
                    </div>
                  </div>

                  {/* Scores */}
                  <div className="grid grid-cols-2 gap-3 mt-4">
                    <div className="bg-white/60 rounded-lg p-3">
                      <p className="text-xs text-gray-600 mb-1">Risk Score</p>
                      <p className="text-2xl font-bold text-gray-800">
                        {(scanResult.phishing_score * 100).toFixed(0)}%
                      </p>
                    </div>
                    <div className="bg-white/60 rounded-lg p-3">
                      <p className="text-xs text-gray-600 mb-1">Confidence</p>
                      <p className="text-2xl font-bold text-gray-800">
                        {(scanResult.confidence * 100).toFixed(0)}%
                      </p>
                    </div>
                  </div>
                </div>

                {/* Explanation */}
                {scanResult.explanation && (
                  <div className="bg-white rounded-lg p-4 shadow-sm border border-gray-200">
                    <h4 className="font-semibold text-gray-800 mb-2 flex items-center gap-2">
                      <TrendingUp className="w-4 h-4" />
                      Analysis
                    </h4>
                    <p className="text-sm text-gray-700 leading-relaxed">
                      {scanResult.explanation}
                    </p>
                  </div>
                )}

                {/* Risk Factors */}
                {scanResult.risk_factors && scanResult.risk_factors.length > 0 && (
                  <div className="bg-white rounded-lg p-4 shadow-sm border border-gray-200">
                    <h4 className="font-semibold text-gray-800 mb-3">Risk Factors</h4>
                    <div className="space-y-2">
                      {scanResult.risk_factors.map((factor, idx) => (
                        <div
                          key={idx}
                          className={`p-3 rounded-lg ${getSeverityColor(factor.severity)}`}
                        >
                          <div className="flex items-start justify-between mb-1">
                            <p className="font-medium text-sm">{factor.risk}</p>
                            <span className="text-xs uppercase font-bold">
                              {factor.severity}
                            </span>
                          </div>
                          <p className="text-xs opacity-90">{factor.description}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Scan Info */}
                <div className="bg-white rounded-lg p-3 shadow-sm border border-gray-200">
                  <div className="flex items-center justify-between text-xs text-gray-600">
                    <span className="flex items-center gap-1">
                      <Clock className="w-3 h-3" />
                      Scan time: {scanResult.scan_duration_ms}ms
                    </span>
                    <span className="text-gray-400">ID: {scanResult.scan_id.slice(0, 8)}</span>
                  </div>
                </div>

                {/* Feedback */}
                <div className="bg-white rounded-lg p-4 shadow-sm border border-gray-200">
                  <p className="text-sm text-gray-700 mb-3">Was this result accurate?</p>
                  <div className="flex gap-2">
                    <button
                      onClick={() => handleFeedback(true)}
                      className="flex-1 bg-green-100 hover:bg-green-200 text-green-700 py-2 rounded-lg text-sm font-medium transition-colors"
                    >
                      ✓ Yes
                    </button>
                    <button
                      onClick={() => handleFeedback(false)}
                      className="flex-1 bg-red-100 hover:bg-red-200 text-red-700 py-2 rounded-lg text-sm font-medium transition-colors"
                    >
                      ✗ No
                    </button>
                  </div>
                </div>

                {/* Rescan Button */}
                <button
                  onClick={handleScan}
                  disabled={loading}
                  className="w-full bg-gray-100 hover:bg-gray-200 text-gray-700 py-2 rounded-lg text-sm font-medium transition-colors"
                >
                  Scan Again
                </button>
              </div>
            )}
          </div>
        )}

        {activeTab === 'history' && (
          <div className="text-center py-12">
            <Clock className="w-12 h-12 text-gray-400 mx-auto mb-3" />
            <p className="text-gray-600">Scan history coming soon</p>
            <p className="text-sm text-gray-500 mt-2">
              Your recent scans will appear here
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
