$(document).ready(function() {

	// Handle the AJAX based search widget used by the TinyMCE editor
	function searchMedia(query) {

		var $results = $('#media-search-results');
		var results_html;

		// Ensure we actually have something to search for
		if (typeof query != 'undefined' && query.length > 0) {

			// Submit the AJAX requset, but not asynchornously to make this
			// a bit simpler. Also ensure the browser doesn't cache the response
			// by appending a random query string to the request
			$.ajax({
				url: '/api/search?doc_type=media&query=' + query,
				cache: false,
				async: false
			}).done(function(results) {

				var result;
				var glyph;
				var content;
				results_html = '';

				// Loop through our result set
				for (var id in results.data) {

					content = '';
					result = results.data[id];

					// Based on the content type append an appropriate icon and
					// the source of the media element
					if (result.type === 'image') {

						glyph = 'camera';
						content += '<img src="' + result.content + '"/>';

					} else if (result.type === 'audio') {

						glyph = 'volume-up';
						content += '<audio controls>';
						// As this is just a prototype only mp3 audio files are supported
						content += '<source src="' + result.content + '" type="audio/mpeg">';
						content += 'Your browser does not support HTML5 audio.</audio>';

					} else if (result.type === 'video') {

						glyph = 'film';
						content += '<video controls>';
						// As this is just a prototype only mp4 video files are supported
						content += '<source src="' + result.content + '" type="video/mp4">';
						content += 'Your browser does not support HTML5 video.</video>';

					} else if (result.type === 'text') {

						glyph = 'font';

					}

					// Append the HTML used to create the list to display to the user
					results_html += '<li><span class="glyphicon glyphicon-' + glyph + '"></span> ';
					results_html += '<a data-content="' + encodeURIComponent(content) + '" ';
					results_html += 'href="javascript:void(0)">' + result.title + '</a></li>';

				}

			});

			$results.html(results_html);

		} else {

			$results.html('');

		}

	}

	// Cache the media search ui selector for performance
	$media_search_ui = $('#media-search-ui');

	// Search media on keyup
	$media_search_ui.on('keyup', function(e) {

		searchMedia($(this).val());

	});

	// Run a search initially with the page title
	searchMedia($media_search_ui.val());

	// Handle the pop up box used by the TinyMCE editor
	$('#media-search-results').on('click', 'li a', function(e) {

		// URL Decode and insert the content into the active editor window
		window.top.tinymce.EditorManager.activeEditor.insertContent(decodeURIComponent($(this).data('content')));

		// Close our pop up
		window.top.tinymce.activeEditor.windowManager.close();

	});

});