import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api'

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 600000, // 10分钟超时
})

export const uploadVideo = async (file, model = 'base', useAI = false) => {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('model', model)
  formData.append('use_ai', useAI)

  try {
    const response = await api.post('/transcribe', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  } catch (error) {
    if (error.response) {
      throw new Error(error.response.data.error || '服务器错误')
    } else if (error.request) {
      throw new Error('网络错误，请检查连接')
    } else {
      throw new Error('请求失败')
    }
  }
}

export const getHistory = async () => {
  try {
    const response = await api.get('/history')
    return response.data
  } catch (error) {
    if (error.response) {
      throw new Error(error.response.data.error || '获取历史记录失败')
    }
    throw new Error('网络错误')
  }
}

export const getHistoryDetail = async (taskId) => {
  try {
    const response = await api.get(`/history/${taskId}`)
    return response.data
  } catch (error) {
    if (error.response) {
      throw new Error(error.response.data.error || '获取详情失败')
    }
    throw new Error('网络错误')
  }
}

export const deleteHistory = async (taskId) => {
  try {
    const response = await api.delete(`/history/${taskId}`)
    return response.data
  } catch (error) {
    if (error.response) {
      throw new Error(error.response.data.error || '删除失败')
    }
    throw new Error('网络错误')
  }
}

export default api
