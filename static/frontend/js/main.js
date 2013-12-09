$(document).ready(function() {

	// Handle clicks on voting buttons on the index and story/xyz pages
	$('.upvote, .downvote').on('click', function() {

		var $this = $(this);

		// Check voting hasn't been 'disabled' on this entry
		if ($this.parent().data('voted') !== 'true') {

			var type = $this.data('type');
			var story_id = $this.parents('.frontend-story').data('story-id');
			var opposite = type === 'upvote' ? type : 'downvote';

			// Submit the ajax request to increment or decrement the vote count
			$.ajax({
				url: '/vote?type=' + type + '&story_id=' + story_id,
				cache: false
			}).done(function(result) {

				// Was there an error?
				if (result.error !== null) {

					alert('There was an error recording your vote, please try again');
					console.log(result);

				// If not we can update the vote count!
				} else {

					// Update the vote count
					$('#' + story_id + '-votes').text(result.data.total);

					// Change the colour of the other arrow
					$this.parent().find('> .' + opposite).css('color', '#aaa');

					// 'disable' further voting
					$this.parent().data('voted', 'true');

				}

			});

		}

	});

});