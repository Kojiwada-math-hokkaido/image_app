// static/js/drag_and_drop.js
document.addEventListener('DOMContentLoaded', (event) => {
	const dropArea = document.getElementById('dropArea');
	const imageInput = document.getElementById('imageInput');
	const previewImage = document.getElementById('previewImage');

	// Prevent default drag behaviors
	['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
			dropArea.addEventListener(eventName, preventDefaults, false)
			document.body.addEventListener(eventName, preventDefaults, false)
	});

	// Highlight drop area when item is dragged over it
	['dragenter', 'dragover'].forEach(eventName => {
			dropArea.addEventListener(eventName, () => dropArea.classList.add('highlight'), false)
	});

	['dragleave', 'drop'].forEach(eventName => {
			dropArea.addEventListener(eventName, () => dropArea.classList.remove('highlight'), false)
	});

	// Handle dropped files
	dropArea.addEventListener('drop', handleDrop, false);

	function preventDefaults(e) {
			e.preventDefault();
			e.stopPropagation();
	}

	function handleDrop(e) {
			const dt = e.dataTransfer;
			const files = dt.files;

			handleFiles(files);
	}

	function handleFiles(files) {
			if (files.length > 0) {
					const file = files[0];
					imageInput.files = files; // Set files to input element
					previewImageFile(file); // Call your previewImage function
			}
	}

	function previewImageFile(file) {
			const reader = new FileReader();
			reader.readAsDataURL(file);
			reader.onloadend = function() {
					previewImage.src = reader.result;
					previewImage.removeAttribute('hidden'); // Remove hidden attribute
			}
	}

	// Preview image when selected from the input
	imageInput.addEventListener('change', (event) => {
			const file = event.target.files[0];
			if (file) {
					previewImageFile(file);
			}
	});
});
