/**
 * Copyright (C) 2010, Tay Ray Chuan
 */
jQuery(function($) {
	StopwatchControls = function() {
		var m_state;

		var btn_flow = $('<div class="stopwatch-button" style="float: left"></div>');
		var btn_reset = $('<div class="stopwatch-button" style="float: left">Reset</div>');
		var controls = $('<div></div>')
			.append(btn_flow)
			.append(btn_reset);

		btn_flow.click(function() {
			if (m_state.running) {
				controls.trigger('pause');

				btn_flow.text('Continue');
				btn_reset.show();
			} else {
				controls.trigger('continue');

				btn_flow.text('Pause');
				btn_reset.hide();
			}
			m_state.running = !m_state.running;
			m_state.use_value = !m_state.running;
			m_state.reset = false;
		});

		btn_reset.click(function() {
			if (m_state.running) return;

			controls.trigger('reset');

			btn_flow.text('Start');
			btn_reset.hide();
			m_state.running = false;
			m_state.reset = true;
		});

		return {
			btn_flow: btn_flow,
			btn_reset: btn_reset,
			controls: controls,

			init: function(state) {
				m_state = state;
			}
		};
	}();
});
