// TinyMCE Setup and Configuration
tinymce.init({
	selector: 'textarea',
	menubar: false, // Hide the menu bar
	statusbar: false, // Hide the status bar
	plugins: ['link'],
	verify_html: false,
	toolbar: 'undo redo | styleselect | bold italic underline | alignleft aligncenter alignright alignjustify | bullist numlist outdent indent | link | addmedia',
	extended_valid_elements: '*[*]',
	setup: function(editor) {
		editor.addButton('addmedia', {
			text: 'Add Media',
			icon: false,
			onclick: function() {
				editor.windowManager.open({
					title: 'Media Search',
					file: '/cms/media/search/tinymce',
					width: 320,
					height: 240
				});
			}
		});
	}
});
// End TinyMCE

// Code reliant on jQuery and the DOM being ready
$(document).ready(function() {

	$('#media-search-ui').on('keyup', function(e) {

		var $this = $(this);
		var query = $this.val();
		var $results = $('#media-search-results');
		var results_html;

		if (query.length > 0) {

			$.ajax({
				url: '/cms/media/search/ajax/' + query,
				cache: false,
				async: false
			}).done(function(results) {

				var result;
				var glyph;
				var content;
				results_html = '';
				
				for (var id in results) {

					content = '';
					result = results[id].fields;

					// Convert the type to appropriate icon
					if (result.type === 'image') {

						glyph = 'camera';
						content += '<img src="' + result.content + '"/>';

					} else if (result.type === 'audio') {

						glyph = 'volume-up';
						content += '<audio controls>';
						content += '<source src="' + result.content + '" type="audio/mpeg">';
						content += 'Your browser does not support HTML5 audio.';
						content += '</audio>';

					} else if (result.type === 'video') {

						glyph = 'film';
						content += '<video controls>';
						content += '<source src="' + result.content + '" type="video/mp4">';
						content += 'Your browser does not support HTML5 video.</video>';

					} else if (result.type === 'text') {

						glyph = 'font';

					}

					results_html += '<li><span class="glyphicon glyphicon-' + glyph + '"></span> ';
					results_html += '<a data-content="' + encodeURIComponent(content) + '" ';
					results_html += 'href="javascript:void(0)">' + result.title + '</a></li>';

				}

			});

			$results.html(results_html);

		} else {

			$results.html('');

		}

		

	});

	$('#media-search-results').on('click', 'li a', function(e) {

		var $this = $(this);

		window.top.tinymce.EditorManager.activeEditor.insertContent(decodeURIComponent($this.data('content')));
		window.top.tinymce.activeEditor.windowManager.close();

	});

});
// End jQuery reliant code