'use client'

import { useAuth } from '@clerk/nextjs'
import { useQuery } from '@tanstack/react-query'
import { Shield, TrendingUp, AlertTriangle, CheckCircle, Clock, Activity } from 'lucide-react'
import { Line, Doughnut } from 'react-chartjs-2'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js'
import axios from 'axios'

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler
)

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'

export default function Dashboard() {
  const { getToken } = useAuth()

  const { data: stats, isLoading } = useQuery({
    queryKey: ['user-stats'],
    queryFn: async () => {
      const token = await getToken()
      const response = await axios.get(`${API_URL}/users/me/stats`, {
        headers: { Authorization: `Bearer ${token}` }
      })
      return response.data
    }
  })

  const { data: profile } = useQuery({
    queryKey: ['user-profile'],
    queryFn: async () => {
      const token = await getToken()
      const response = await axios.get(`${API_URL}/users/me`, {
        headers: { Authorization: `Bearer ${token}` }
      })
      return response.data
    }
  })

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-4 border-blue-600 border-t-transparent mx-auto mb-4" />
          <p className="text-gray-600">Loading dashboard...</p>
        </div>
      </div>
    )
  }

  const scanHistoryData = {
    labels: stats?.scan_history?.map((d: any) => new Date(d.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })) || [],
    datasets: [
      {
        label: 'Total Scans',
        data: stats?.scan_history?.map((d: any) => d.total_scans) || [],
        borderColor: 'rgb(59, 130, 246)',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        fill: true,
        tension: 0.4
      },
      {
        label: 'Phishing Detected',
        data: stats?.scan_history?.map((d: any) => d.phishing_detected) || [],
        borderColor: 'rgb(239, 68, 68)',
        backgroundColor: 'rgba(239, 68, 68, 0.1)',
        fill: true,
        tension: 0.4
      }
    ]
  }

  const threatDistributionData = {
    labels: ['Safe Sites', 'Phishing Detected'],
    datasets: [{
      data: [stats?.safe_sites || 0, stats?.phishing_detected || 0],
      backgroundColor: [
        'rgba(34, 197, 94, 0.8)',
        'rgba(239, 68, 68, 0.8)',
      ],
      borderColor: [
        'rgb(34, 197, 94)',
        'rgb(239, 68, 68)',
      ],
      borderWidth: 2
    }]
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 bg-gradient-to-br from-blue-600 to-blue-700 rounded-xl flex items-center justify-center shadow-lg">
                <Shield className="w-7 h-7 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">PhishGuard Dashboard</h1>
                <p className="text-sm text-gray-600">Welcome back, {profile?.full_name || profile?.email}</p>
              </div>
            </div>
            <div className="flex items-center gap-2 px-4 py-2 bg-green-50 border border-green-200 rounded-lg">
              <Activity className="w-4 h-4 text-green-600" />
              <span className="text-sm font-medium text-green-700">System Active</span>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow">
            <div className="flex items-center justify-between mb-4">
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                <Shield className="w-6 h-6 text-blue-600" />
              </div>
              <span className="text-xs font-medium text-gray-500 bg-gray-100 px-2 py-1 rounded">Total</span>
            </div>
            <div className="text-3xl font-bold text-gray-900 mb-1">{stats?.total_scans || 0}</div>
            <div className="text-sm text-gray-600">Total Scans</div>
          </div>

          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow">
            <div className="flex items-center justify-between mb-4">
              <div className="w-12 h-12 bg-red-100 rounded-lg flex items-center justify-center">
                <AlertTriangle className="w-6 h-6 text-red-600" />
              </div>
              <span className="text-xs font-medium text-red-600 bg-red-50 px-2 py-1 rounded">Threats</span>
            </div>
            <div className="text-3xl font-bold text-gray-900 mb-1">{stats?.phishing_detected || 0}</div>
            <div className="text-sm text-gray-600">Phishing Detected</div>
          </div>

          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow">
            <div className="flex items-center justify-between mb-4">
              <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
                <CheckCircle className="w-6 h-6 text-green-600" />
              </div>
              <span className="text-xs font-medium text-green-600 bg-green-50 px-2 py-1 rounded">Safe</span>
            </div>
            <div className="text-3xl font-bold text-gray-900 mb-1">{stats?.safe_sites || 0}</div>
            <div className="text-sm text-gray-600">Safe Sites</div>
          </div>

          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow">
            <div className="flex items-center justify-between mb-4">
              <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
                <Clock className="w-6 h-6 text-purple-600" />
              </div>
              <span className="text-xs font-medium text-purple-600 bg-purple-50 px-2 py-1 rounded">7 Days</span>
            </div>
            <div className="text-3xl font-bold text-gray-900 mb-1">{stats?.scans_last_7_days || 0}</div>
            <div className="text-sm text-gray-600">Recent Scans</div>
          </div>
        </div>

        {/* Charts */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          <div className="lg:col-span-2 bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-lg font-semibold text-gray-900">Scan Activity (Last 30 Days)</h2>
              <TrendingUp className="w-5 h-5 text-gray-400" />
            </div>
            <div className="h-64">
              <Line
                data={scanHistoryData}
                options={{
                  responsive: true,
                  maintainAspectRatio: false,
                  plugins: {
                    legend: {
                      position: 'bottom' as const,
                    },
                  },
                  scales: {
                    y: {
                      beginAtZero: true,
                      ticks: {
                        precision: 0
                      }
                    }
                  }
                }}
              />
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-6">Threat Distribution</h2>
            <div className="h-64 flex items-center justify-center">
              <Doughnut
                data={threatDistributionData}
                options={{
                  responsive: true,
                  maintainAspectRatio: false,
                  plugins: {
                    legend: {
                      position: 'bottom' as const,
                    },
                  },
                }}
              />
            </div>
          </div>
        </div>

        {/* Top Domains */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Top Scanned Domains</h2>
          <div className="space-y-3">
            {stats?.top_domains?.slice(0, 5).map((domain: any, idx: number) => (
              <div key={idx} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center">
                    <span className="text-sm font-bold text-blue-600">#{idx + 1}</span>
                  </div>
                  <span className="font-medium text-gray-900">{domain.domain}</span>
                </div>
                <span className="text-sm font-semibold text-gray-600">{domain.count} scans</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
