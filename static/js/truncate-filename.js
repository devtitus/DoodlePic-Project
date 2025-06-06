// Function to truncate filenames to show beginning and end with ellipsis
function truncateFileName(filename, prefixLength = 10) {
  // If filename is short enough, don't truncate
  if (filename.length <= prefixLength + 8) { // +8 for ellipsis and extension
    const fileNameElement = document.getElementById('file-name');
    if (fileNameElement) {
      fileNameElement.textContent = filename;
      fileNameElement.setAttribute('title', filename);
    }
    return filename;
  }

  // Find the last dot to preserve the extension
  const lastDotIndex = filename.lastIndexOf('.');
  let nameWithoutExt = filename;
  let extension = '';

  if (lastDotIndex > 0) {
    nameWithoutExt = filename.substring(0, lastDotIndex);
    extension = filename.substring(lastDotIndex);
  }

  // Get the prefix (beginning of filename without extension)
  const prefix = nameWithoutExt.substring(0, Math.min(prefixLength, nameWithoutExt.length));

  // Create truncated display text
  const truncatedText = `${prefix}...${extension}`;

  // Apply truncation to the DOM element
  const fileNameElement = document.getElementById('file-name');

  if (fileNameElement) {
    fileNameElement.textContent = truncatedText; // Set the truncated text
    fileNameElement.setAttribute('title', filename); // Show full filename on hover
    fileNameElement.setAttribute('data-full-name', filename); // Store full name
  }

  return truncatedText;
}

// Example usage (to be called when a file is selected):
/*
document.getElementById('file-input').addEventListener('change', function(e) {
  if (this.files && this.files[0]) {
    const filename = this.files[0].name;
    const fileNameElement = document.getElementById('file-name');
    
    if (fileNameElement) {
      // Initially set the full filename
      fileNameElement.textContent = filename;
      
      // Then truncate it
      truncateFileName(filename);
    }
  }
});
*/ 