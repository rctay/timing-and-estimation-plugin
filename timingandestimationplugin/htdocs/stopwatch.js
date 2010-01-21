/**
 * Copyright (C) 2010, Tay Ray Chuan
 */

$(document).ready(function() {
	var state = {
		running: false,
		reset: false,
		use_value: false
	};
	var field = $("input#field-hours");
	var stopwatch = $('<div></div>');

	StopwatchDisplay.init(stopwatch);

	StopwatchControls.init(state, stopwatch);

	Toggler.init(state, field[0], stopwatch,
		StopwatchControls.btn_flow, StopwatchControls.btn_reset);

	/* put toggler and stopwatch in a div, then put it below the hours <input>
	 * field. */
	field.after(
		$('<div></div>')
		.append(Toggler.toggler)
		.append(stopwatch));

	/* initialize */
	StopwatchControls.btn_reset.click();
	Toggler.toggler.click();
})
