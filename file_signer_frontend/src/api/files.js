import apiClient from "./client"


//Axios automatically sets the correct headers when you pass FormData
export async function signFile(file, password) {
  try {
    const formData = new FormData()
    // 'uploaded_file' must match the variable name in your FastAPI route!
    formData.append('uploaded_file', file)
    formData.append('password', password)
    const response = await apiClient.post(
      '/files/sign',
      formData,
      {
        responseType: 'blob'
      }

    )
    return response
  } catch (error) {
    // 1. Check if the error is a Blob (FastAPI error sent as binary)
    if (error.response?.data instanceof Blob) {
  
      let errorJson
      try {
        // 2. AWAIT the text conversion of the blob(text() is async)
         const errorText = await error.response.data.text();
         // Try to parse as JSON to get the 'detail' field
         errorJson = JSON.parse(errorText);
      } catch (parseError) {
         // If the server sent HTML or plain text instead of JSON
        throw new Error('Technical error during signing');
      }
      // this actual detail from the backend!
      throw new Error(errorJson.detail || 'Signing failed');
    }

    // Handle Network errors or standard JSON errors
    throw new Error(error.response?.data?.detail || 'Server Connection Failed')
  }
}

export async function verifyFile(fileId, file) {
  const formData = new FormData()
  formData.append('uploaded_file', file)
  try {
    const response = await apiClient.post(`/files/verify/${fileId}`, formData)
    return response.data
  } catch (error) {
    throw new Error(error.response?.data?.detail || "'File verification failed")
  }
}

export async function listFiles() {
  try {
    const response = await apiClient.get('/files/')
    return response.data
  } catch (error) {
    throw new Error(error.response?.data?.detail || 'Failed to load files')
  }
}

export async function getSignatureInspection(fileId) {
  try {
    const response = await apiClient.get(`/files/${fileId}/signature-inspection`)
    return response.data
  } catch (error) {
    throw new Error(error.response?.data?.detail || 'Failed to fetch inspection details')
  }
}

export async function verifySigIndependent(orginalFile, signatureFile, publicKeyStr) {
  try {
    // These keys MUST match your FastAPI arguments: uploaded_file, signature_file, public_key
    const formData = new FormData()
    formData.append('uploaded_file', orginalFile)
    formData.append('signature_file', signatureFile)
    formData.append('public_key', publicKeyStr)
    const response = await apiClient.post(`files/verify-independent`, formData)
    return response.data
  } catch (error) {
    throw new Error(error.response?.data?.detail || 'Verification Failed, Try again')
  }
}