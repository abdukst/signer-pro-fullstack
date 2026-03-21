/**
 * Professional Utility to trigger a browser download.
 * @param {string} content - The text/data to save
 * @param {string} filename - e.g., 'public_key.pem'
 * @param {string} mimeType - e.g., 'application/x-pem-file'
 */
export function triggerDownload(content, filname, mimeType = 'text/plain') {

  // 1. If it's already a Blob (binary), use it directly.
  // If it's a string (text), wrap it in a new binary Blob.
  const blob = content instanceof Blob ? content : new Blob([content], { type: mimeType })
  //const blob = new Blob([content], {type: mimeType})

  // 2. Create a temporary URL in the browser memory
  const url = window.URL.createObjectURL(blob)

  // 3. Create a hidden 'a' tag to "click"  
  const link = document.createElement('a')
  link.href = url
  link.setAttribute('download', filname)
  document.body.appendChild(link)
  link.click()

  // 4. CLEANUP memory
  link.remove()
  window.URL.revokeObjectURL(url)
}