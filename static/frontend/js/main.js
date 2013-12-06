$(document).ready(function() {

	// Handle clicks on voting buttons on the index and story/xyz pages
	$('.upvote, .downvote').on('click', function() {

		var $this = $(this);
		var type = $this.data('type');
		var story_id = $this.parents('.frontend-story').data('story-id');

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

				$('#' + story_id + '-votes').text(result.data.total);

			}

		});

	});

});