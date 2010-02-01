/**
 * Copyright (C) 2010, Tay Ray Chuan
 */
jQuery(function($) {
	StopwatchControls = function() {
		var m_state;

		var btn_flow = $('<div class="stopwatch-button"></div>');
		var btn_reset = $('<div class="stopwatch-button">Reset</div>');
		var controls = $('<div></div>')
			.append(btn_flow)
			.append(btn_reset);

		/* first handler to run; set states */
		controls.bind('pause', function() {
			m_state.running = false;
			m_state.use_value = true;
			m_state.reset = false;
		});

		controls.bind('continue', function() {
			m_state.running = true;
			m_state.use_value = false;
			m_state.reset = false;
		});

		controls.bind('reset', function() {
			m_state.running = false;
			m_state.use_value = false;
			m_state.reset = true;
		});

		/* make buttons trigger events */
		btn_flow.click(function() {
			if (m_state.running)
				controls.trigger('pause');
			else
				controls.trigger('continue');
		});

		btn_reset.click(function() {
			if (m_state.running) return;

			controls.trigger('reset');
		});

		/* make button states react to events */
		controls.bind('pause', function() {
			btn_flow.text('Continue');
			btn_reset.show();
		});

		controls.bind('continue', function() {
			btn_flow.text('Pause');
			btn_reset.hide();
		});

		controls.bind('reset', function() {
			btn_flow.text('Start');
			btn_reset.hide();
		});

		return {
			controls: controls,

			init: function(state) {
				m_state = state;
			}
		};
	}();
});
