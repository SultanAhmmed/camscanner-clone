// State management
let selectedFiles = [];

// DOM Elements
const dropZone = document.getElementById('dropZone');
const fileInput = document.getElementById('fileInput');
const previewSection = document.getElementById('previewSection');
const previewGrid = document.getElementById('previewGrid');
const fileCount = document.getElementById('fileCount');
const clearBtn = document.getElementById('clearBtn');
const settingsSection = document.getElementById('settingsSection');
const processBtn = document.getElementById('processBtn');
const resultSection = document.getElementById('resultSection');
const downloadLink = document.getElementById('downloadLink');


// Drag and Drop Events
dropZone.addEventListener('click', () => fileInput.click());

dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.classList.add('drag-over');
});

dropZone.addEventListener('dragleave', () => {
    dropZone.classList.remove('drag-over');
});

dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.classList.remove('drag-over');
    handleFiles(e.dataTransfer.files);
});

fileInput.addEventListener('change', (e) => {
    handleFiles(e.target.files);
});

// Handle Files
function handleFiles(files) {
    const imageFiles = Array.from(files).filter(file => file.type.startsWith('image/'));
    selectedFiles = [...selectedFiles, ...imageFiles];
    updatePreview();
}

// Update Preview
function updatePreview() {
    if (selectedFiles.length === 0) {
        previewSection.style.display = 'none';
        settingsSection.style.display = 'none';
        return;
    }

    previewSection.style.display = 'block';
    settingsSection.style.display = 'block';
    fileCount.textContent = selectedFiles.length;

    previewGrid.innerHTML = '';
    selectedFiles.forEach((file, index) => {
        const reader = new FileReader();
        reader.onload = (e) => {
            const previewItem = document.createElement('div');
            previewItem.className = 'preview-item';
            previewItem.innerHTML = `
                <img src="${e.target.result}" alt="${file.name}">
                <button class="remove-btn" data-index="${index}">×</button>
            `;
            previewGrid.appendChild(previewItem);
        };
        reader.readAsDataURL(file);
    });

    // Add remove button listeners
    document.querySelectorAll('.remove-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const index = parseInt(e.target.dataset.index);
            selectedFiles.splice(index, 1);
            updatePreview();
        });
    });
}

// Clear All
clearBtn.addEventListener('click', () => {
    selectedFiles = [];
    fileInput.value = '';
    updatePreview();
    resultSection.style.display = 'none';
});

// Process Documents
processBtn.addEventListener('click', async () => {
    if (selectedFiles.length === 0) {
        alert('Please select at least one image');
        return;
    }

    const mode = document.querySelector('input[name="mode"]:checked').value;
    const formData = new FormData();

    selectedFiles.forEach(file => {
        formData.append('files', file);
    });

    // Show loading state
    processBtn.disabled = true;
    processBtn.querySelector('.btn-text').style.display = 'none';
    processBtn.querySelector('.btn-loader').style.display = 'inline';

    try {
        const response = await fetch(`/scan-to-pdf?mode=${mode}`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error('Failed to process documents');
        }

        const blob = await response.blob();
        const url = URL.createObjectURL(blob);

        downloadLink.href = url;
        resultSection.style.display = 'block';
        resultSection.scrollIntoView({ behavior: 'smooth' });

    } catch (error) {
        alert('Error processing documents: ' + error.message);
        console.error(error);
    } finally {
        processBtn.disabled = false;
        processBtn.querySelector('.btn-text').style.display = 'inline';
        processBtn.querySelector('.btn-loader').style.display = 'none';
    }
});


