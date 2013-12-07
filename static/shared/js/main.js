$(document).ready(function() {

	// TinyMCE Setup and Configuration
	tinymce.init({
		selector: 'textarea',
		menubar: false, // Hide the menu bar
		statusbar: false, // Hide the status bar
		plugins: ['link'],
		height: 750,
		verify_html: false,
		toolbar: 'undo redo | styleselect | bold italic underline | alignleft aligncenter alignright alignjustify | bullist numlist outdent indent | link | selectmedia',
		extended_valid_elements: '*[*]',
		relative_urls :false, // Stop TinyMCE messing up our urls!
		setup: function(editor) {
			editor.addButton('selectmedia', {
				text: 'Select Media',
				icon: false,
				onclick: function() {
					editor.windowManager.open({
						title: 'Media Search',
						file: '/cms/media/search/tinymce?title=' + $('#id_title').val(),
						width: 320,
						height: 240
					});
				}
			});
		}
	});
	// End TinyMCE

	// Init the select2 jQuery plugin
	$('select').select2({width: 'resolve'});

	// Function used to handle which (if any) of the optional media fields should be shown
	function handleMediaOptionalFields(value) {

		// If audio, video or image was selected then show the file field and hide the content field
		if (value === 'audio' || value === 'video' || value === 'image') {

			$('.form-file').show();
			$('.form-content').hide();

		// If text was selected then show the content field and hide the file field
		} else if (value === 'text') {

			$('.form-file').hide();
			$('.form-content').show();

		// If neither were selected then make sure both are hidden
		} else {

			$('.form-file, .form-content').hide();

		}

	}

	// Handle changing of the value of the type select box on the media forms
	$id_type = $('form #id_type');
	$id_type.on('change', function(e) {

		handleMediaOptionalFields($(this).val());

	});

	// A bit of a hacky way unfortunately of handling when Django returns validation errors
	// and the need to display either the content or file field
	if ($id_type.length > 0) {

		handleMediaOptionalFields($id_type.val());

	}

});