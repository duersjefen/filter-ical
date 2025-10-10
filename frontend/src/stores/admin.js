import { defineStore } from 'pinia'
import { ref } from 'vue'
import { API_BASE_URL } from '../constants/api'

export const useAdminStore = defineStore('admin', () => {
  const adminToken = ref(localStorage.getItem('admin_token') || null)

  function setAdminToken(token) {
    adminToken.value = token
    if (token) {
      localStorage.setItem('admin_token', token)
    } else {
      localStorage.removeItem('admin_token')
    }
  }

  function getAuthHeaders() {
    const headers = {
      'Content-Type': 'application/json'
    }

    if (adminToken.value) {
      headers['Authorization'] = `Bearer ${adminToken.value}`
    }

    return headers
  }

  async function login(password) {
    const response = await fetch(`${API_BASE_URL}/admin/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ password })
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Login failed')
    }

    const data = await response.json()
    setAdminToken(data.token)
    return data
  }

  function logout() {
    setAdminToken(null)
  }

  // Domain YAML Configuration Management

  async function listDomainConfigs() {
    const response = await fetch(`${API_BASE_URL}/admin/domain-configs`, {
      headers: getAuthHeaders()
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Failed to list configurations')
    }

    return await response.json()
  }

  async function getDomainConfig(domainKey, format = 'yaml') {
    const response = await fetch(
      `${API_BASE_URL}/admin/domain-configs/${domainKey}?format=${format}`,
      {
        headers: getAuthHeaders()
      }
    )

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Failed to get configuration')
    }

    if (format === 'json') {
      return await response.json()
    } else {
      return await response.text()
    }
  }

  async function downloadDomainConfig(domainKey) {
    const response = await fetch(
      `${API_BASE_URL}/admin/domain-configs/${domainKey}`,
      {
        headers: getAuthHeaders()
      }
    )

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Failed to download configuration')
    }

    // Trigger download
    const blob = await response.blob()
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${domainKey}.yaml`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    window.URL.revokeObjectURL(url)
  }

  async function uploadDomainConfig(domainKey, file) {
    const formData = new FormData()
    formData.append('file', file)

    const headers = {}
    if (adminToken.value) {
      headers['Authorization'] = `Bearer ${adminToken.value}`
    }

    const response = await fetch(
      `${API_BASE_URL}/admin/domain-configs/${domainKey}`,
      {
        method: 'POST',
        headers,
        body: formData
      }
    )

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Failed to upload configuration')
    }

    return await response.json()
  }

  async function seedDomainFromConfig(domainKey, forceReseed = false) {
    const response = await fetch(
      `${API_BASE_URL}/admin/domain-configs/${domainKey}/seed`,
      {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify({ force_reseed: forceReseed })
      }
    )

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Failed to seed domain')
    }

    return await response.json()
  }

  async function deleteDomainConfig(domainKey) {
    const response = await fetch(
      `${API_BASE_URL}/admin/domain-configs/${domainKey}`,
      {
        method: 'DELETE',
        headers: getAuthHeaders()
      }
    )

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Failed to delete configuration')
    }

    return await response.json()
  }

  // Admin Password Reset

  async function requestPasswordReset() {
    const response = await fetch(`${API_BASE_URL}/admin/request-password-reset`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      }
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Failed to request password reset')
    }

    return await response.json()
  }

  async function resetPassword(token, newPassword) {
    const response = await fetch(`${API_BASE_URL}/admin/reset-password`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        token,
        new_password: newPassword
      })
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Failed to reset password')
    }

    return await response.json()
  }

  return {
    adminToken,
    login,
    logout,
    listDomainConfigs,
    getDomainConfig,
    downloadDomainConfig,
    uploadDomainConfig,
    seedDomainFromConfig,
    deleteDomainConfig,
    requestPasswordReset,
    resetPassword
  }
})
