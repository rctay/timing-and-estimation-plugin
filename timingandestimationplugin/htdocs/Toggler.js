/**
 * Copyright (C) 2010, Tay Ray Chuan
 */

/* toggles the stopwatch (and controls) with a simple slide */
jQuery(function($) {
	Toggler = function() {
		var m_state;
		var m_field;

		var should_show = true;
		var toggler = $('<div>Show stopwatch</div>');
		toggler.click(function() {
			if (should_show = !should_show) {
				$(this).trigger("show");
			} else
				$(this).trigger("hide");
		});

		toggler.bind("show",
			function() {
				if (m_state.use_value) {
					m_field.value = StopwatchDisplay.get_hours();
				}
				this.firstChild.nodeValue = 'Show stopwatch';
			}
		);
		toggler.bind("hide",
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

			init: function(state, field) {
				m_state = state;
				m_field = field;
			}
		};
	}();
});
