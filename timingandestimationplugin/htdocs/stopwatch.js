/**
 * Copyright (C) 2010, Tay Ray Chuan
 */

$(document).ready(function() {
	var state = {
		running: false,
		reset: false,
		use_value: false
	};
	var stopwatch;

	stopwatch = $('<div></div>');
	StopwatchDisplay.init(stopwatch);

	StopwatchControls.init(state, stopwatch);

	Toggler.init(state, stopwatch,
		StopwatchControls.btn_flow, StopwatchControls.btn_reset);

	/* put toggler and stopwatch in a div, then put it below the hours <input>
	 * field. */
	$("input#field-hours").after(
		$('<div></div>')
		.append(Toggler.toggler)
		.append(stopwatch));

	/* initialize */
	StopwatchControls.btn_reset.click();
	Toggler.toggler.click();
})
