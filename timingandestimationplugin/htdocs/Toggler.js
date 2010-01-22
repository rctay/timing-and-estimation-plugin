/**
 * Copyright (C) 2010, Tay Ray Chuan
 */

/* toggles the stopwatch (and controls) with a simple slide */
jQuery(function($) {
	Toggler = function() {
		var m_state;

		var should_show = true;
		var toggler = $('<div class="stopwatch-button">Show stopwatch</div>');

		toggler.bind("show", function() { should_show = true; });
		toggler.bind("hide", function() { should_show = false; });

		toggler.click(function() {
			if (!should_show) {
				$(this).trigger("show");
			} else
				$(this).trigger("hide");
		});

		toggler.bind("hide",
			function() {
				this.firstChild.nodeValue = 'Show stopwatch';
			}
		);
		toggler.bind("show",
			function() {
				if (m_state.reset)
					this.firstChild.nodeValue = 'Hide stopwatch';
				else
					this.firstChild.nodeValue = 'Use stopwatch value';
			}
		);
		var continue_handler = function() {
			toggler.hide("fast");
		};
		var pause_handler = function() {
			toggler[0].firstChild.nodeValue = 'Use stopwatch value';
			toggler.show("fast");
		};
		var reset_handler = function() {
			toggler[0].firstChild.nodeValue = 'Hide stopwatch';
		};

		return {
			toggler: toggler,

			continue_handler: continue_handler,
			pause_handler: pause_handler,
			reset_handler: reset_handler,

			init: function(state) {
				m_state = state;
			}
		};
	}();
});
