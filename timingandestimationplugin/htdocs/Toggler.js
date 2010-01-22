/**
 * Copyright (C) 2010, Tay Ray Chuan
 */

/* toggles the stopwatch (and controls) with a simple slide */
jQuery(function($) {
	Toggler = function() {
		var m_state;

		var should_show = true;
		var toggler = $('<div class="stopwatch-button">Show stopwatch</div>');
		toggler.click(function() {
			if (should_show = !should_show) {
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
		var btn_flow_click = function() {
			if (m_state.running) {
				toggler.hide("fast");
			} else {
				toggler[0].firstChild.nodeValue = 'Use stopwatch value';
				toggler.show("fast");
			}
		};
		var btn_reset_click = function() {
			if (m_state.reset && !m_state.running)
				toggler[0].firstChild.nodeValue = 'Hide stopwatch';
		};

		return {
			toggler: toggler,
			btn_flow_click: btn_flow_click,
			btn_reset_click: btn_reset_click,

			init: function(state) {
				m_state = state;
			}
		};
	}();
});
