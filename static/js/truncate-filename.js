// Function to truncate filenames to show beginning and end with ellipsis
function truncateFileName(filename, prefixLength = 10) {
    // If filename is short enough, don't truncate
    if (filename.length <= prefixLength + 4 + 3) { // +3 for ellipsis
        return filename;
    }

    // Get the prefix (beginning of filename)
    const prefix = filename.substring(0, prefixLength);

    // Get the suffix (last 4 characters)
    const suffix = filename.substring(filename.length - 4);

    // Apply truncation to the DOM element
    const fileNameElement = document.getElementById('file-name');

    if (fileNameElement) {
        fileNameElement.textContent = ''; // Clear the text content
        fileNameElement.setAttribute('data-truncated', 'true');
        fileNameElement.setAttribute('data-prefix', prefix);
        fileNameElement.setAttribute('data-suffix', suffix);
        fileNameElement.setAttribute('title', filename); // Show full filename on hover
    }
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