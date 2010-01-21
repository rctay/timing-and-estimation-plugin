/**
 * Copyright (C) 2010, Tay Ray Chuan
 */

StopwatchControls = function() {
	var m_state;
	var btn_flow = $('<div style="float: left"></div>');
	var btn_reset = $('<div style="float: left">Reset</div>');

	btn_flow.click(function() {
		if (m_state.running) {
			StopwatchDisplay.pause_stopwatch();

			btn_flow.text('Continue');
			btn_reset.show();
		} else {
			StopwatchDisplay.continue_stopwatch();

			btn_flow.text('Pause');
			btn_reset.hide();
		}
		m_state.running = !m_state.running;
		m_state.use_value = !m_state.running;
		m_state.reset = false;
	});

	btn_reset.click(function() {
		if (m_state.running) return;

		StopwatchDisplay.reset_stopwatch();
		btn_flow.text('Start');
		btn_reset.hide();
		m_state.running = false;
		m_state.reset = true;
	});

	return {
		btn_flow: btn_flow,
		btn_reset: btn_reset,

		init: function(state, p_stopwatch) {
			m_state = state;

			p_stopwatch.append($('<div></div>')
				.append(btn_flow)
				.append(btn_reset));
		}
	};
}();
